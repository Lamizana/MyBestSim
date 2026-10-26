import sys

from mybestsim import metrics
from mybestsim.config import CLEAN_OUTPUT
from mybestsim.etl import load_clean


def run(clean) -> None:
    """Affiche les KPI calculés sur la table nettoyée."""
    rapport = metrics.compute_metrics(clean)
    kpi = rapport["kpi"]

    prix = kpi["fourchette_prix"]["valeur"]
    data = kpi["data_gb_moyenne"]
    prix_stats = kpi["prix_moyen"]["valeur"]

    print(f"- Nombre total de cartes : {kpi['total_cartes']['valeur']}")
    print(f"- Nombre de cartes au-delà de 100 € : {kpi['prix_superieur_100']['valeur']}")
    print(f"- Plage de prix : {prix['min']} € à {prix['max']} €")
    print(
        f"- Moyenne des données (offres à volume fini) : "
        f"{data['valeur']} Go ({data['perimetre']})"
    )
    print(f"- Prix moyen et médian : {prix_stats['moyenne']} € et {prix_stats['mediane']} €")
    print("- Distribution par fournisseur :")
    for ligne in kpi["fournisseurs"]["valeur"]:
        print(f"  - {ligne['provider']} : {ligne['cartes']} cartes")


def main() -> int:
    try:
        clean = load_clean(CLEAN_OUTPUT)
    except FileNotFoundError:
        print(f"{CLEAN_OUTPUT} absent : lance d'abord python -m mybestsim.merge")
        return 1
    except (UnicodeDecodeError, OSError, ValueError) as erreur:
        print(f"Échec : {erreur}")
        return 1

    run(clean)
    return 0


if __name__ == "__main__":
    sys.exit(main())
