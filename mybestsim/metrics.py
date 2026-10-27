import pandas as pd


# -----------------------------------------------------------------------------
def total_cards(df: pd.DataFrame) -> int:
    """Nombre total d'offres (une ligne = un produit eSIM)."""
    return len(df)


# -----------------------------------------------------------------------------
def cards_above_price(df: pd.DataFrame, seuil: float = 100.0) -> int:
    """Nombre d'offres dont le prix dépasse strictement `seuil` euros."""
    return int((df["price"] > seuil).sum())


# -----------------------------------------------------------------------------
def price_range(df: pd.DataFrame) -> dict:
    """Prix minimum et maximum du catalogue, en euros."""
    return {
        "min": round(float(df["price"].min()), 2),
        "max": round(float(df["price"].max()), 2),
    }


# -----------------------------------------------------------------------------
def mean_data_gb(df: pd.DataFrame) -> dict:
    """Moyenne des data_gb des offres à volume fini (illimitées exclues)."""
    finies = df.loc[~df["is_unlimited"], "data_gb"]
    return {
        "valeur": round(float(finies.mean()), 2),
        "nb_offres": int(finies.count()),
    }


# -----------------------------------------------------------------------------
def mean_price(df: pd.DataFrame) -> dict:
    """Prix moyen et médian du catalogue, en euros."""
    return {
        "moyenne": round(float(df["price"].mean()), 2),
        "mediane": round(float(df["price"].median()), 2),
    }


# -----------------------------------------------------------------------------
def provider_distribution(df: pd.DataFrame) -> list:
    """Nombre d'offres par fournisseur, trié décroissant, avec part en %."""
    comptes = df.groupby("provider").size().sort_values(ascending=False, kind="stable")
    total = int(comptes.sum())
    return [
        {
            "provider": provider,
            "cartes": int(nombre),
            "part_pct": round(int(nombre) * 100 / total, 1),
        }
        for provider, nombre in comptes.items()
    ]


# -----------------------------------------------------------------------------
def price_histogram(df: pd.DataFrame, largeur: int = 10, maximum: int = 160) -> list:
    """Répartition des prix par tranche, pour l'histogramme de la page."""
    bornes = list(range(0, maximum + largeur, largeur))
    tranches = pd.cut(df["price"], bins=bornes, right=False)
    comptes = tranches.value_counts(sort=False).sort_index()
    return [
        {
            "min": int(intervalle.left),
            "max": int(intervalle.right),
            "offres": int(nombre),
        }
        for intervalle, nombre in comptes.items()
    ]


# -----------------------------------------------------------------------------
def meilleures_offres(df: pd.DataFrame) -> list:
    """Offre la moins chère par destination, volume et durée.

    Les zones (Europe, Asie, Amérique du Nord, Monde) sont conservées et
    signalées par ``zone`` : elles ne doivent pas être mélangées aux pays dans
    une même comparaison.
    """
    cles = [
        "country_code",
        "country_name",
        "is_region",
        "data_display",
        "validity_days",
    ]
    trie = df.sort_values(cles + ["price", "provider"], kind="stable")
    meilleures = trie.groupby(cles, as_index=False, dropna=False).first()
    bornes = df.groupby(cles, as_index=False, dropna=False).agg(
        prix_max=("price", "max"),
        offres=("sku", "size"),
    )
    trie_max = df.sort_values(
        cles + ["price", "provider"],
        ascending=[True] * len(cles) + [False, True],
        kind="stable",
    )
    plus_chers = (
        trie_max.groupby(cles, as_index=False, dropna=False)
        .first()[cles + ["provider"]]
        .rename(columns={"provider": "provider_max"})
    )
    fusion = meilleures.merge(bornes, on=cles).merge(plus_chers, on=cles)
    fusion = fusion.sort_values(
        ["is_region", "country_name", "validity_days", "data_display"],
        kind="stable",
    )

    return [
        {
            "code": ligne.country_code,
            "destination": ligne.country_name,
            "zone": bool(ligne.is_region),
            "volume": ligne.data_display,
            "data_gb": None if pd.isna(ligne.data_gb) else float(ligne.data_gb),
            "validity_days": int(ligne.validity_days),
            "provider": ligne.provider,
            "prix": round(float(ligne.price), 2),
            "provider_max": ligne.provider_max,
            "prix_max": round(float(ligne.prix_max), 2),
            "offres": int(ligne.offres),
        }
        for ligne in fusion.itertuples()
    ]


# -----------------------------------------------------------------------------
def compute_metrics(clean: pd.DataFrame) -> dict:
    """Assemble les KPI demandés et leurs définitions dans un dictionnaire sérialisable."""
    total = total_cards(clean)
    data = mean_data_gb(clean)
    prix = price_range(clean)
    prix_stats = mean_price(clean)
    fournisseurs = provider_distribution(clean)

    return {
        "meta": {
            "lignes": int(len(clean)),
            "fournisseurs": int(clean["provider"].nunique()),
            "devise": "EUR",
        },
        "kpi": {
            "total_cartes": {
                "valeur": total,
                "definition": "Cartes valides après nettoyage",
                "perimetre": f"{total} lignes",
            },
            "prix_superieur_100": {
                "valeur": cards_above_price(clean),
                "definition": "Offres dont le prix dépasse strictement 100 EUR",
                "perimetre": f"{total} offres",
            },
            "fourchette_prix": {
                "valeur": prix,
                "definition": "Prix minimum et maximum du catalogue",
                "perimetre": f"{total} offres",
            },
            "data_gb_moyenne": {
                "valeur": data["valeur"],
                "nb_offres": data["nb_offres"],
                "definition": "Moyenne des données de volume en Go",
                "perimetre": f"{data['nb_offres']} offres finies, illimitées exclues",
            },
            "prix_moyen": {
                "valeur": prix_stats,
                "definition": "Prix moyen et médian du catalogue",
                "perimetre": f"{total} offres",
            },
            "fournisseurs": {
                "valeur": fournisseurs,
                "definition": "Nombre d'offres par fournisseur",
                "perimetre": f"{len(fournisseurs)} fournisseurs",
            },
        },
        "series": {
            "histogramme_prix": price_histogram(clean),
            "meilleures_offres": meilleures_offres(clean),
        },
    }
