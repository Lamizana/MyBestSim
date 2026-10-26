"""Dashboard Streamlit du catalogue eSIM MyBestSim.

L'application ne calcule rien : elle appelle ``compute_metrics`` et affiche.
Toute la logique reste dans ``mybestsim/``, où elle est testée.
"""

import altair as alt
import pandas as pd
import streamlit as st

from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw
from mybestsim.format import format_fr
from mybestsim.metrics import compute_metrics

BLEU = "#007bff"


@st.cache_data(show_spinner="Lecture des 18 fichiers fournisseurs…")
def charger_metriques() -> dict:
    """Lit les CSV bruts, nettoie et calcule les six KPI, une fois par processus."""
    return compute_metrics(clean_data(load_raw(DATA_DIR)))


def afficher_entete(metrics: dict) -> None:
    meta = metrics["meta"]
    st.title("Catalogue eSIM — MyBestSim")
    st.caption(
        f"{format_fr(meta['lignes'])} offres comparées, "
        f"{meta['fournisseurs']} fournisseurs, devise {meta['devise']}."
    )


def afficher_kpi(metrics: dict) -> None:
    kpi = metrics["kpi"]
    fourchette = kpi["fourchette_prix"]["valeur"]
    data = kpi["data_gb_moyenne"]
    prix = kpi["prix_moyen"]["valeur"]

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
        help=f"{kpi['prix_moyen']['definition']} — médiane {format_fr(prix['mediane'], 2)} €",
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
    donnees = pd.DataFrame(metrics["kpi"]["fournisseurs"]["valeur"])
    graphique = (
        alt.Chart(donnees)
        .mark_bar(color=BLEU)
        .encode(
            x=alt.X("cartes:Q", title="Nombre d'offres"),
            y=alt.Y("provider:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("provider:N", title="Fournisseur"),
                alt.Tooltip("cartes:Q", title="Offres"),
                alt.Tooltip("part_pct:Q", title="Part (%)"),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(graphique, width="stretch")


def afficher_prix(metrics: dict) -> None:
    st.subheader("Distribution des prix")
    tranches = pd.DataFrame(metrics["series"]["histogramme_prix"])
    graphique = (
        alt.Chart(tranches)
        .mark_bar(color=BLEU)
        .encode(
            x=alt.X("min:Q", title="Prix (€)", scale=alt.Scale(domain=[0, 160])),
            x2="max:Q",
            y=alt.Y("offres:Q", title="Nombre d'offres"),
            tooltip=[
                alt.Tooltip("min:Q", title="De (€)"),
                alt.Tooltip("max:Q", title="À (€)"),
                alt.Tooltip("offres:Q", title="Offres"),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(graphique, width="stretch")


def afficher_methodologie(metrics: dict) -> None:
    data = metrics["kpi"]["data_gb_moyenne"]
    with st.expander("Méthodologie et définitions"):
        st.markdown(
            f"""
- {format_fr(metrics['meta']['lignes'])} offres lues dans les 18 fichiers
  fournisseurs, aucune ligne rejetée.
- Moyenne de data calculée sur les {format_fr(data['nb_offres'])} offres à
  volume fini ; les offres illimitées sont exclues et ne valent jamais 0 Go.
- Seuil des 100 € appliqué strictement : prix supérieur à 100,00 €.
- Jeu de données synthétique fourni pour le test : les relations observées
  décrivent ce catalogue, pas le marché réel.
"""
        )
        st.caption("Code source : github.com/Lamizana/MyBestSim")


def main() -> None:
    st.set_page_config(
        page_title="Dashboard eSIM — MyBestSim",
        page_icon="📊",
        layout="wide",
    )

    try:
        metrics = charger_metriques()
    except (OSError, ValueError) as erreur:
        st.error(f"Impossible de calculer les KPI : {erreur}")
        st.stop()

    afficher_entete(metrics)
    afficher_kpi(metrics)
    afficher_fournisseurs(metrics)
    afficher_prix(metrics)
    afficher_methodologie(metrics)


main()
