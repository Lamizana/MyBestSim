import pandas as pd

from mybestsim.config import REGION_CODES, ZONE_PREFIX


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Type les colonnes et ajoute les colonnes dérivées.

    Les codes de zone (EU, AS, NA, WW) deviennent ZONE_EU, ZONE_AS, ZONE_NA,
    ZONE_WW. Ne modifie pas `raw`. Échoue si une valeur contredit le contrat.
    """
    df = raw.copy()

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
        raise ValueError("Incohérence illimité : " + ", ".join(df.loc[incoherents, "sku"]))

    # Les codes de zone (EU, AS, NA, WW) sont préfixés dans la table nettoyée.
    # "NA" est interprété comme une valeur manquante par pandas à la relecture,
    # ce qui ferait disparaître 192 lignes de tout groupby. Voir README.md.
    df["is_region"] = df["country_code"].isin(REGION_CODES)
    df.loc[df["is_region"], "country_code"] = ZONE_PREFIX + df.loc[df["is_region"], "country_code"]

    df["price_per_gb"] = df["price"] / df["data_gb"]

    return df
