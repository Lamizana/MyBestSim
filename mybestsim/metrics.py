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


def unlimited_share(df: pd.DataFrame) -> dict:
    """Part des offres illimitées dans le catalogue."""
    total = int(len(df))
    nb = int(df["is_unlimited"].sum())
    return {"part_pct": round(nb * 100 / total, 1), "nb": nb, "total": total}


def price_per_gb_stats(df: pd.DataFrame) -> dict:
    """Distribution du prix au Go sur les offres à volume fini."""
    valeurs = df["price_per_gb"].dropna()
    return {
        "mediane": round(float(valeurs.median()), 2),
        "q1": round(float(valeurs.quantile(0.25)), 2),
        "q3": round(float(valeurs.quantile(0.75)), 2),
        "min": round(float(valeurs.min()), 2),
        "max": round(float(valeurs.max()), 2),
        "nb_offres": int(valeurs.count()),
    }


def bundle_spread(df: pd.DataFrame, min_fournisseurs: int = 2) -> dict:
    """Écart de prix entre fournisseurs pour un même bundle.

    Un bundle est identifié par (destination, volume, durée). Les offres
    zonales sont incluses : comparer « Europe 10 Go 15 jours » entre
    fournisseurs est légitime, contrairement à une comparaison pays/zone.
    """
    stats = (
        df.groupby(["country_code", "country_name", "data_display", "validity_days"])
        .agg(
            prix_min=("price", "min"),
            prix_max=("price", "max"),
            nb_fournisseurs=("provider", "nunique"),
        )
        .reset_index()
    )
    comparables = stats[stats["nb_fournisseurs"] >= min_fournisseurs].copy()
    comparables["ecart_pct"] = (
        (comparables["prix_max"] - comparables["prix_min"])
        / comparables["prix_min"]
        * 100
    )

    exemples = comparables.sort_values(
        ["ecart_pct", "country_name", "data_display", "validity_days"],
        ascending=[False, True, True, True],
        kind="stable",
    ).head(3)

    return {
        "nb_bundles": int(len(comparables)),
        "ecart_median_pct": round(float(comparables["ecart_pct"].median()), 1),
        "ecart_max_pct": round(float(comparables["ecart_pct"].max()), 1),
        "part_superieur_20_pct": round(
            float(comparables["ecart_pct"].gt(20).mean() * 100), 1
        ),
        "exemples": [
            {
                "destination": ligne.country_name,
                "data_display": ligne.data_display,
                "validity_days": int(ligne.validity_days),
                "prix_min": round(float(ligne.prix_min), 2),
                "prix_max": round(float(ligne.prix_max), 2),
                "ecart_pct": round(float(ligne.ecart_pct), 1),
            }
            for ligne in exemples.itertuples()
        ],
    }


def provider_stats(df: pd.DataFrame) -> list:
    """Statistiques par fournisseur, triées par nombre d'offres."""
    total = int(len(df))
    stats = df.groupby("provider").agg(
        cartes=("sku", "size"),
        prix_moyen=("price", "mean"),
        prix_go_median=("price_per_gb", "median"),
        part_5g_pct=("network", lambda serie: serie.eq("5G").mean() * 100),
        part_illimite_pct=("is_unlimited", lambda serie: serie.mean() * 100),
    )
    stats["part_pct"] = stats["cartes"] * 100 / total
    stats["pays"] = df.loc[~df["is_region"]].groupby("provider")["country_code"].nunique()
    stats = stats.sort_values("cartes", ascending=False, kind="stable")

    return [
        {
            "provider": provider,
            "cartes": int(ligne.cartes),
            "part_pct": round(float(ligne.part_pct), 1),
            "prix_moyen": round(float(ligne.prix_moyen), 2),
            "prix_go_median": round(float(ligne.prix_go_median), 2),
            "part_5g_pct": round(float(ligne.part_5g_pct), 1),
            "part_illimite_pct": round(float(ligne.part_illimite_pct), 1),
            "pays": int(ligne.pays),
        }
        for provider, ligne in stats.iterrows()
    ]


def cheapest_by_destination(df: pd.DataFrame, validity_days: int = 15) -> list:
    """Offre la moins chère par pays et par palier, à durée fixe.

    Les offres zonales sont exclues : comparer « Europe » à « Espagne » n'a
    pas de sens. À prix égal, le départage se fait par prix au Go puis par
    nom de fournisseur, pour un résultat reproductible.
    """
    pays = df.loc[~df["is_region"] & df["validity_days"].eq(validity_days)]

    trie = pays.sort_values(
        ["country_code", "data_gb", "price", "price_per_gb", "provider"],
        kind="stable",
    )
    meilleures = trie.groupby(
        ["country_code", "country_name", "data_gb"], as_index=False
    ).first()
    bornes = (
        pays.groupby(["country_code", "data_gb"])
        .agg(prix_max=("price", "max"), nb_offres=("sku", "size"))
        .reset_index()
    )
    meilleures = meilleures.merge(bornes, on=["country_code", "data_gb"])
    meilleures = meilleures.sort_values(["country_code", "data_gb"], kind="stable")

    return [
        {
            "country_code": code,
            "country_name": nom,
            "offres": [
                {
                    "data_display": ligne.data_display,
                    "data_gb": float(ligne.data_gb),
                    "provider": ligne.provider,
                    "price": round(float(ligne.price), 2),
                    "prix_max": round(float(ligne.prix_max), 2),
                    "nb_offres": int(ligne.nb_offres),
                }
                for ligne in groupe.itertuples()
            ],
        }
        for (code, nom), groupe in meilleures.groupby(
            ["country_code", "country_name"], sort=True
        )
    ]


def compute_metrics(clean: pd.DataFrame) -> dict:
    """Assemble les KPI et leurs définitions dans un dictionnaire sérialisable."""
    total = total_cards(clean)
    data = mean_data_gb(clean)
    prix = price_range(clean)
    prix_stats = mean_price(clean)
    fournisseurs = provider_distribution(clean)
    illimite = unlimited_share(clean)
    prix_go = price_per_gb_stats(clean)
    ecart = bundle_spread(clean)
    stats = provider_stats(clean)
    destinations = cheapest_by_destination(clean)

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
            "part_illimite": {
                "valeur": illimite,
                "definition": "part des offres dont le volume est illimité",
                "perimetre": f"{illimite['total']} offres",
            },
            "prix_au_go": {
                "valeur": prix_go,
                "definition": "distribution du prix au Go sur les offres à volume fini",
                "perimetre": f"{prix_go['nb_offres']} offres finies, illimitées exclues",
            },
            "ecart_bundles": {
                "valeur": ecart,
                "definition": "écart de prix entre fournisseurs pour un même bundle",
                "perimetre": f"{ecart['nb_bundles']} bundles proposés par au moins 2 fournisseurs",
            },
            "fournisseurs_detail": {
                "valeur": stats,
                "definition": "statistiques par fournisseur, triées par nombre d'offres",
                "perimetre": f"{len(stats)} fournisseurs",
            },
            "meilleure_offre_par_destination": {
                "valeur": destinations,
                "definition": "offre la moins chère par pays et par palier, à 15 jours",
                "perimetre": f"{len(destinations)} pays, zones exclues",
            },
        },
    }
