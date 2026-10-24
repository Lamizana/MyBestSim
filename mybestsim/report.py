import sys

from mybestsim import metrics
from mybestsim.config import CLEAN_OUTPUT, METRICS_OUTPUT
from mybestsim.etl import load_clean, write_json


def run(clean) -> None:
    """Affiche les KPI calculés sur la table nettoyée et écrit metrics.json."""
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

    illimite = kpi["part_illimite"]["valeur"]
    go = kpi["prix_au_go"]["valeur"]
    ecart = kpi["ecart_bundles"]["valeur"]
    detail = kpi["fournisseurs_detail"]["valeur"]
    destinations = kpi["meilleure_offre_par_destination"]["valeur"]

    moins_cher = min(detail, key=lambda ligne: ligne["prix_moyen"])
    plus_cher = max(detail, key=lambda ligne: ligne["prix_moyen"])

    print("- KPI bonus :")
    print(
        f"  - Part d'illimité : {illimite['part_pct']} % "
        f"({illimite['nb']} / {illimite['total']})"
    )
    print(
        f"  - Prix au Go : médiane {go['mediane']} € "
        f"(q1 {go['q1']}, q3 {go['q3']}), de {go['min']} à {go['max']} € "
        f"({go['nb_offres']} offres)"
    )
    print(
        f"  - Écart sur un même bundle : {ecart['nb_bundles']} bundles, "
        f"médiane {ecart['ecart_median_pct']} %, max {ecart['ecart_max_pct']} %"
    )
    for exemple in ecart["exemples"]:
        print(
            f"    - {exemple['destination']}, {exemple['data_display']} "
            f"{exemple['validity_days']} j : {exemple['prix_min']} € → "
            f"{exemple['prix_max']} € (+{exemple['ecart_pct']} %)"
        )
    print(
        f"  - Prix moyen par fournisseur : {moins_cher['prix_moyen']} € "
        f"({moins_cher['provider']}) → {plus_cher['prix_moyen']} € "
        f"({plus_cher['provider']})"
    )
    print(f"  - Meilleure offre par destination (15 j) : {len(destinations)} pays")
    for destination in destinations[:3]:
        offre = destination["offres"][0]
        print(
            f"    - {destination['country_name']} : {offre['provider']} "
            f"{offre['data_display']} — {offre['price']} €"
        )

    write_json(rapport, METRICS_OUTPUT)
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
