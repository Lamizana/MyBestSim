import hashlib
import io
import warnings
from pathlib import Path

import pandas as pd

from mybestsim.config import EXPECTED_COLUMNS, REGION_CODES, ZONE_PREFIX


def _resoudre_doublons(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons exacts, refuse les SKU aux valeurs divergentes.

    Un SKU présent plusieurs fois avec les mêmes valeurs est un doublon
    d'ingestion : on n'en garde qu'un. S'il porte des valeurs différentes,
    c'est un conflit : on échoue plutôt que de choisir silencieusement.
    """
    doublons = df[df["sku"].duplicated(keep=False)]
    if doublons.empty:
        return df

    for sku, groupe in doublons.groupby("sku", sort=False):
        uniques = groupe[EXPECTED_COLUMNS].drop_duplicates()
        if len(uniques) > 1:
            divergentes = [
                colonne
                for colonne in EXPECTED_COLUMNS
                if uniques[colonne].nunique(dropna=False) > 1
            ]
            sources = ", ".join(sorted(groupe["_source"].unique()))
            raise ValueError(
                f"SKU {sku} en conflit dans {sources} : "
                f"colonnes divergentes {', '.join(divergentes)}"
            )

    dedoublonne = df.drop_duplicates(subset=["sku"], keep="first")
    supprimes = len(df) - len(dedoublonne)
    if supprimes:
        warnings.warn(
            f"{supprimes} doublons exacts ignorés (même SKU, mêmes valeurs)",
            stacklevel=2,
        )
    return dedoublonne.reset_index(drop=True)


def load_raw(data_dir: Path) -> pd.DataFrame:
    """Lit les CSV du dossier, contrôle les en-têtes et empile les tables.

    Un fichier strictement identique à un autre est ignoré. Les lignes portant
    le même SKU sont dédoublonnées si elles sont identiques ; si elles
    divergent, la lecture échoue en nommant le SKU, les fichiers et les
    colonnes en cause.
    """
    fichiers = sorted(data_dir.glob("*.csv"))
    if not fichiers:
        raise ValueError(f"Aucun CSV trouvé dans {data_dir}")

    tableaux = []
    empreintes = {}

    for fichier in fichiers:
        contenu = fichier.read_bytes()
        empreinte = hashlib.sha256(contenu).hexdigest()
        if empreinte in empreintes:
            warnings.warn(
                f"Fichier identique ignoré : {fichier.name} "
                f"(copie de {empreintes[empreinte]})",
                stacklevel=2,
            )
            continue
        empreintes[empreinte] = fichier.name

        df = pd.read_csv(
            io.BytesIO(contenu),
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )

        if list(df.columns) != EXPECTED_COLUMNS:
            raise ValueError(
                f"Colonnes différentes dans {fichier.name}\n"
                f"  attendu : {EXPECTED_COLUMNS}\n"
                f"  trouvé  : {list(df.columns)}"
            )

        df["_source"] = fichier.name
        tableaux.append(df)

    if not tableaux:
        raise ValueError(f"Aucun CSV exploitable dans {data_dir}")

    empile = pd.concat(tableaux, ignore_index=True)
    propre = _resoudre_doublons(empile)
    return propre.drop(columns="_source")


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Type les colonnes et ajoute les colonnes dérivées.

    Les codes de zone (EU, AS, NA, WW) deviennent ZONE_EU, ZONE_AS, ZONE_NA,
    ZONE_WW. Ne modifie pas `raw`. Échoue si une valeur contredit le contrat.
    """
    df = raw.copy()

    obligatoires = [colonne for colonne in EXPECTED_COLUMNS if colonne != "data_gb"]
    vides = {colonne: int(df[colonne].eq("").sum()) for colonne in obligatoires}
    vides = {colonne: nombre for colonne, nombre in vides.items() if nombre}
    if vides:
        details = ", ".join(
            f"{colonne} ({nombre})" for colonne, nombre in vides.items()
        )
        raise ValueError(f"Valeurs vides dans : {details}")

    doublons = df.loc[df["sku"].duplicated(), "sku"]
    if not doublons.empty:
        exemples = ", ".join(doublons.head(5))
        reste = len(doublons) - 5
        suffixe = f" (+{reste} autres)" if reste > 0 else ""
        raise ValueError(f"SKU dupliqué : {exemples}{suffixe}")

    if not df["currency"].eq("EUR").all():
        raise ValueError(f"Devise inattendue : {sorted(df['currency'].unique())}")

    if not df["network"].isin({"4G", "5G"}).all():
        raise ValueError(f"Réseau inattendu : {sorted(df['network'].unique())}")

    durees = pd.to_numeric(df["validity_days"], errors="coerce")
    if durees.isna().any():
        raise ValueError("Durée illisible : " + ", ".join(df.loc[durees.isna(), "sku"]))
    if (durees <= 0).any():
        raise ValueError(
            "Durée non positive : " + ", ".join(df.loc[durees <= 0, "sku"])
        )
    df["validity_days"] = durees.astype(int)

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["data_gb"] = pd.to_numeric(df["data_gb"], errors="coerce")

    if df["price"].isna().any():
        raise ValueError(
            "Prix illisible : " + ", ".join(df.loc[df["price"].isna(), "sku"])
        )

    if (df["price"] <= 0).any():
        raise ValueError(
            "Prix non positif : " + ", ".join(df.loc[df["price"] <= 0, "sku"])
        )

    top_up = df["top_up"].map({"oui": True, "non": False})
    if top_up.isna().any():
        valeurs = sorted(df.loc[top_up.isna(), "top_up"].unique())
        raise ValueError(f"Valeur top_up inattendue : {valeurs}")

    df["top_up"] = top_up.astype(bool)
    df["is_unlimited"] = df["data_display"].eq("Illimité")

    # data_gb vide et "Illimité" doivent aller ensemble : sinon une offre
    # finie sans volume sortirait silencieusement de la moyenne de Go.
    incoherents = df["data_gb"].isna() != df["is_unlimited"]
    if incoherents.any():
        raise ValueError(
            "Incohérence illimité : " + ", ".join(df.loc[incoherents, "sku"])
        )

    # Les codes de zone (EU, AS, NA, WW) sont préfixés dans la table nettoyée.
    # "NA" est interprété comme une valeur manquante par pandas à la relecture,
    # ce qui ferait disparaître 192 lignes de tout groupby. Voir README.md.
    df["is_region"] = df["country_code"].isin(REGION_CODES)
    df.loc[df["is_region"], "country_code"] = (
        ZONE_PREFIX + df.loc[df["is_region"], "country_code"]
    )

    return df
