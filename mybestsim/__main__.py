import sys

from mybestsim import metrics
from mybestsim.clean import clean_data
from mybestsim.config import CLEAN_OUTPUT, DATA_DIR, RAW_OUTPUT
from mybestsim.export import write_csv
from mybestsim.ingest import load_data


def main() -> int:
    try:
        raw = load_data(DATA_DIR)
        clean = clean_data(raw)
    except UnicodeDecodeError as erreur:
        print(f"Encodage invalide : {erreur}")
        return 1
    except OSError as erreur:
        print(f"Erreur d'accès aux fichiers : {erreur}")
        return 1
    except ValueError as erreur:
        print(f"Échec : {erreur}")
        return 1

    write_csv(raw, RAW_OUTPUT)
    write_csv(clean, CLEAN_OUTPUT)

    prix = metrics.price_range(clean)
    data = metrics.mean_data_gb(clean)
    prix_stats = metrics.mean_price(clean)

    print(f"{len(clean)} lignes, {len(clean.columns)} colonnes")
    print(f"Écrit dans {RAW_OUTPUT} et {CLEAN_OUTPUT}")
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
