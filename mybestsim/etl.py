import json
from pathlib import Path

import pandas as pd

from mybestsim.config import EXPECTED_COLUMNS, REGION_CODES, ZONE_PREFIX


def load_raw(data_dir: Path) -> pd.DataFrame:
    """Lit les CSV du dossier, contrôle les en-têtes et empile les tables."""
    fichiers = sorted(data_dir.glob("*.csv"))
    if not fichiers:
        raise ValueError(f"Aucun CSV trouvé dans {data_dir}")

    tableaux = []

    for fichier in fichiers:
        df = pd.read_csv(fichier, dtype=str, keep_default_na=False, encoding="utf-8-sig")

        if list(df.columns) != EXPECTED_COLUMNS:
            raise ValueError(
                f"Colonnes différentes dans {fichier.name}\n"
                f"  attendu : {EXPECTED_COLUMNS}\n"
                f"  trouvé  : {list(df.columns)}"
            )

        tableaux.append(df)

    return pd.concat(tableaux, ignore_index=True)


def load_clean(path: Path) -> pd.DataFrame:
    """Relit la table nettoyée en préservant les types et les valeurs vides."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")

    df["validity_days"] = df["validity_days"].astype(int)
    for colonne in ("price", "data_gb"):
        df[colonne] = pd.to_numeric(df[colonne], errors="coerce")
    for colonne in ("top_up", "is_unlimited", "is_region"):
        df[colonne] = df[colonne].map({"True": True, "False": False})

    return df


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
        details = ", ".join(f"{colonne} ({nombre})" for colonne, nombre in vides.items())
        raise ValueError(f"Valeurs vides dans : {details}")

    doublons = df.loc[df["sku"].duplicated(), "sku"]
    if not doublons.empty:
        raise ValueError("SKU dupliqué : " + ", ".join(doublons))

    if not df["currency"].eq("EUR").all():
        raise ValueError(f"Devise inattendue : {sorted(df['currency'].unique())}")

    if not df["network"].isin({"4G", "5G"}).all():
        raise ValueError(f"Réseau inattendu : {sorted(df['network'].unique())}")

    durees = pd.to_numeric(df["validity_days"], errors="coerce")
    if durees.isna().any():
        raise ValueError("Durée illisible : " + ", ".join(df.loc[durees.isna(), "sku"]))
    if (durees <= 0).any():
        raise ValueError("Durée non positive : " + ", ".join(df.loc[durees <= 0, "sku"]))
    df["validity_days"] = durees.astype(int)

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["data_gb"] = pd.to_numeric(df["data_gb"], errors="coerce")

    if df["price"].isna().any():
        raise ValueError("Prix illisible : " + ", ".join(df.loc[df["price"].isna(), "sku"]))

    if (df["price"] <= 0).any():
        raise ValueError("Prix non positif : " + ", ".join(df.loc[df["price"] <= 0, "sku"]))

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


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def write_json(data: dict, path: Path) -> None:
    """Écrit un dictionnaire en JSON lisible et strict (refuse NaN)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
