"""Dashboard Streamlit du catalogue eSIM MyBestSim.

L'application ne calcule rien : elle appelle ``compute_metrics`` et affiche.
Tout l'affichage passe par des composants Streamlit natifs, sans CSS ni HTML.
"""

from pathlib import Path

import streamlit as st

from mybestsim import graphiques
from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw
from mybestsim.format import format_fr
from mybestsim.metrics import compute_metrics

LOGO = Path(__file__).resolve().parent / "assets" / "logo.png"


@st.cache_data(show_spinner="Lecture des 18 fichiers fournisseurs…")
def charger_metriques() -> dict:
    """Lit les CSV bruts, nettoie et calcule les six KPI, une fois par processus."""
    return compute_metrics(clean_data(load_raw(DATA_DIR)))


def afficher_entete(metrics: dict) -> None:
    meta = metrics["meta"]
    st.caption("Dashboard du catalogue eSIM — test de recrutement")
    st.title(
        f"{format_fr(meta['lignes'])} offres comparées, "
        f"{meta['fournisseurs']} fournisseurs"
    )
    st.markdown(
        "Consolidation des 18 fichiers fournisseurs, nettoyage, contrôle et calcul des indicateurs de prix. Tous les chiffres proviennent du même calcul, mis en cache au démarrage."
    )
    with st.container(horizontal=True):
        st.badge(f"{format_fr(meta['lignes'])} offres", color="blue")
        st.badge(f"{meta['fournisseurs']} fournisseurs", color="gray")
        st.badge(f"Devise : {meta['devise']}", color="gray")


def afficher_kpi(metrics: dict) -> None:
    kpi = metrics["kpi"]
    fourchette = kpi["fourchette_prix"]["valeur"]
    data = kpi["data_gb_moyenne"]
    prix = kpi["prix_moyen"]["valeur"]

    st.subheader("Les chiffres clés")

    premiere = st.columns(3)
    premiere[0].metric(
        "Nombre total de cartes",
        format_fr(kpi["total_cartes"]["valeur"]),
        help=kpi["total_cartes"]["definition"],
        border=True,
    )
    premiere[1].metric(
        "Cartes au-delà de 100 €",
        format_fr(kpi["prix_superieur_100"]["valeur"]),
        help=kpi["prix_superieur_100"]["definition"],
        border=True,
    )
    premiere[2].metric(
        "Fourchette de prix",
        f"{format_fr(fourchette['min'], 2)} – {format_fr(fourchette['max'], 2)} €",
        help=kpi["fourchette_prix"]["definition"],
        border=True,
    )

    seconde = st.columns(3)
    seconde[0].metric(
        "Moyenne de data",
        f"{format_fr(data['valeur'], 2)} Go",
        help=f"{data['definition']} — {data['perimetre']}",
        border=True,
    )
    seconde[1].metric(
        "Prix moyen",
        f"{format_fr(prix['moyenne'], 2)} €",
        help=(
            f"{kpi['prix_moyen']['definition']} — "
            f"médiane {format_fr(prix['mediane'], 2)} €"
        ),
        border=True,
    )
    seconde[2].metric(
        "Fournisseurs",
        format_fr(metrics["meta"]["fournisseurs"]),
        help=kpi["fournisseurs"]["definition"],
        border=True,
    )


def afficher_fournisseurs(metrics: dict) -> None:
    st.subheader("Répartition par fournisseur")
    st.caption("Nombre d'offres par fournisseur, trié décroissant.")
    st.altair_chart(graphiques.fournisseurs(metrics), width="stretch", theme=None)


def afficher_prix(metrics: dict) -> None:
    st.subheader("Distribution des prix")
    st.caption(
        "Tranches de 10 €. Trait rouge : seuil des 100 € · " "pointillés : prix médian."
    )
    st.altair_chart(graphiques.prix(metrics), width="stretch", theme=None)


def afficher_methodologie(metrics: dict) -> None:
    data = metrics["kpi"]["data_gb_moyenne"]
    with st.expander("Méthodologie et définitions", expanded=True):
        st.markdown(
            f"- {format_fr(metrics['meta']['lignes'])} offres lues dans les 18 "
            "fichiers fournisseurs, aucune ligne rejetée.\n"
            f"- Moyenne de data calculée sur les {format_fr(data['nb_offres'])} "
            "offres à volume fini ; les offres illimitées sont exclues et ne "
            "valent jamais 0 Go.\n"
            "- Seuil des 100 € appliqué strictement : prix supérieur à 100,00 €.\n"
            "- Jeu de données synthétique fourni pour le test : les relations "
            "observées décrivent ce catalogue, pas le marché réel."
        )


def main() -> None:
    st.set_page_config(
        page_title="Dashboard eSIM — MyBestSim",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    if LOGO.exists():
        st.logo(str(LOGO), size="large")

    try:
        metrics = charger_metriques()
    except (OSError, ValueError) as erreur:
        st.error(f"Impossible de calculer les KPI : {erreur}")
        st.stop()

    afficher_entete(metrics)
    st.divider()
    afficher_kpi(metrics)
    st.divider()
    afficher_fournisseurs(metrics)
    st.divider()
    afficher_prix(metrics)
    st.divider()
    afficher_methodologie(metrics)
    st.caption(
        "Réalisé dans le cadre du test de recrutement MyBestSim — "
        "[code source](https://github.com/Lamizana/MyBestSim)."
    )


main()
