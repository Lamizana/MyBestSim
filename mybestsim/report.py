import sys

from mybestsim import metrics
from mybestsim.config import CLEAN_OUTPUT, METRICS_OUTPUT
from mybestsim.etl import load_clean, write_json


def run(clean) -> None:
    """Affiche les KPI calculés sur la table nettoyée."""
    prix = metrics.price_range(clean)
    data = metrics.mean_data_gb(clean)
    prix_stats = metrics.mean_price(clean)

    print(f"- Nombre total de cartes : {metrics.total_cards(clean)}")
    print(f"- Nombre de cartes au-delà de 100 € : {metrics.cards_above_price(clean, 100.0)}")
    print(f"- Plage de prix : {prix['min']} € à {prix['max']} €")
    print(
        f"- Moyenne des données (offres à volume fini) : "
        f"{data['valeur']} Go ({data['nb_offres']} offres)"
    )
    print(f"- Prix moyen et médian : {prix_stats['moyenne']} € et {prix_stats['mediane']} €")
    print("- Distribution par fournisseur :")
    for ligne in metrics.provider_distribution(clean):
        print(f"  - {ligne['provider']} : {ligne['cartes']} cartes")

    write_json(metrics.compute_metrics(clean), METRICS_OUTPUT)
    print(f"KPI écrits dans {METRICS_OUTPUT}")


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
