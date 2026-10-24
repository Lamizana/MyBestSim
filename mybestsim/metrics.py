import pandas as pd


def total_cards(df: pd.DataFrame) -> int:
    """Nombre total d'offres (une ligne = un produit eSIM)."""
    return len(df)


def cards_above_price(df: pd.DataFrame, seuil: float = 100.0) -> int:
    """Nombre d'offres dont le prix dépasse strictement `seuil` euros."""
    return int((df["price"] > seuil).sum())


def price_range(df: pd.DataFrame) -> dict:
    """Prix minimum et maximum du catalogue, en euros."""
    return {
        "min": round(float(df["price"].min()), 2),
        "max": round(float(df["price"].max()), 2),
    }


def mean_data_gb(df: pd.DataFrame) -> dict:
    """Moyenne des data_gb des offres à volume fini (illimitées exclues)."""
    finies = df.loc[~df["is_unlimited"], "data_gb"]
    return {
        "valeur": round(float(finies.mean()), 2),
        "nb_offres": int(finies.count()),
    }


def mean_price(df: pd.DataFrame) -> dict:
    """Prix moyen et médian du catalogue, en euros."""
    return {
        "moyenne": round(float(df["price"].mean()), 2),
        "mediane": round(float(df["price"].median()), 2),
    }


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


def compute_metrics(clean: pd.DataFrame) -> dict:
    """Assemble les KPI et leurs définitions dans un dictionnaire sérialisable."""
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
                "definition": "offres valides après nettoyage",
                "perimetre": f"{total} lignes",
            },
            "prix_superieur_100": {
                "valeur": cards_above_price(clean),
                "definition": "offres dont le prix dépasse strictement 100 EUR",
                "perimetre": f"{total} offres",
            },
            "fourchette_prix": {
                "valeur": prix,
                "definition": "prix minimum et maximum du catalogue",
                "perimetre": f"{total} offres",
            },
            "data_gb_moyenne": {
                "valeur": data["valeur"],
                "definition": "moyenne des data_gb des offres à volume fini",
                "perimetre": f"{data['nb_offres']} offres finies, illimitées exclues",
            },
            "prix_moyen": {
                "valeur": prix_stats,
                "definition": "prix moyen et médian du catalogue",
                "perimetre": f"{total} offres",
            },
            "fournisseurs": {
                "valeur": fournisseurs,
                "definition": "nombre d'offres par fournisseur, trié décroissant",
                "perimetre": f"{len(fournisseurs)} fournisseurs",
            },
        },
    }
