"""Graphiques Altair du dashboard.

Aucun HTML, aucun CSS : uniquement des spécifications Vega-Lite passées à
``st.altair_chart``.
"""

import altair as alt
import pandas as pd

from mybestsim.config import SEUIL_PRIX

BLEU = "#007bff"
ROUGE = "#de1414"
MUTED = "#667085"
TEXTE = "#1d2939"
BORD = "#e4e7ec"


def _finaliser(graphique: alt.Chart) -> alt.Chart:
    """Applique la charte commune : fond transparent, police, axes discrets."""
    return (
        graphique.properties(usermeta={"embedOptions": {"actions": False}})
        .configure(background="transparent", font="Poppins, sans-serif", padding=0)
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=MUTED,
            titleColor=MUTED,
            labelFontSize=11,
            titleFontSize=11,
            domainColor=BORD,
            tickColor=BORD,
            gridColor="#eef0f3",
        )
    )


def fournisseurs(metrics: dict) -> alt.Chart:
    """Barres horizontales triées, noms alignés à gauche et coins arrondis."""
    donnees = pd.DataFrame(metrics["kpi"]["fournisseurs"]["valeur"])
    donnees = donnees.sort_values("cartes", ascending=False, kind="stable")
    maximum = int(donnees["cartes"].max() * 1.14)

    # Base du graphique : axes et échelles :
    base = alt.Chart(donnees).encode(
        x=alt.X(
            "cartes:Q", title=None, axis=None, scale=alt.Scale(domain=[0, maximum])
        ),
        y=alt.Y(
            "provider:N",
            sort=None,
            title=None,
            axis=alt.Axis(
                labelFontSize=12,
                labelFontWeight="bold",
                labelColor=TEXTE,
                labelAlign="left",
                labelPadding=120,
                ticks=False,
                domain=False,
            ),
        ),
    )

    # Visuel des barres :
    barres = base.mark_bar(color=BLEU, cornerRadius=6, size=16).encode(
        tooltip=[
            alt.Tooltip("provider:N", title="Fournisseur"),
            alt.Tooltip("cartes:Q", title="Cartes"),
            alt.Tooltip("part_pct:Q", title="Part (%)"),
        ]
    )

    # Visuel des valeurs à droite des barres :
    valeurs = base.mark_text(
        align="left",
        dx=6,
        color=MUTED,
        fontSize=11,
        fontWeight="bold",  # Mettre en gras
    ).encode(text="cartes:Q")

    return _finaliser((barres + valeurs).properties(height=420))


def prix(metrics: dict) -> alt.Chart:
    """Histogramme des prix par tranche de 10 €, seuil `SEUIL_PRIX` en rouge."""
    donnees = pd.DataFrame(metrics["series"]["histogramme_prix"])
    donnees["plage"] = [
        f"{int(ligne['min'])}–{int(ligne['max'])} €" for _, ligne in donnees.iterrows()
    ]
    donnees["libelle"] = [
        f"{int(ligne['min'])}–{int(ligne['max'])}" for _, ligne in donnees.iterrows()
    ]

    base = alt.Chart(donnees).encode(
        x=alt.X(
            "libelle:N",
            sort=None,
            title="Tranches de prix (€)",
            scale=alt.Scale(paddingInner=0.04),  # ~2 px entre les barres
            axis=alt.Axis(
                labelAngle=-45,
                labelFontSize=11,
                labelColor=TEXTE,
                titleColor=TEXTE,
                grid=False,
                tickSize=0,
                labelOverlap="greedy",
            ),
        )
    )

    barres = base.mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3,
    ).encode(
        y=alt.Y(
            "offres:Q",
            title="Nombre d'offres",
            axis=alt.Axis(
                tickCount=4,
                labelExpr="replace(format(datum.value, ',d'), ',', ' ')",
                labelColor=TEXTE,
                titleColor=TEXTE,
                grid=True,
                gridColor="#E4E7EC",
            ),
        ),
        color=alt.condition(
            alt.datum.min >= SEUIL_PRIX,
            alt.value(ROUGE),
            alt.value(BLEU),
        ),
        tooltip=[
            alt.Tooltip("plage:N", title="Tranche"),
            alt.Tooltip("offres:Q", title="Nombre d'offres"),
        ],
    )

    valeurs = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-4,
        fontSize=10,
        fontWeight="bold",
        color=TEXTE,
    ).encode(
        y=alt.Y("offres:Q"),
        text=alt.Text("offres:Q"),
    )

    return _finaliser((barres + valeurs).properties(height=420))


def prix_go_volume(metrics: dict) -> alt.Chart:
    """Prix médian au Go par volume, avec écart interquartile."""
    donnees = pd.DataFrame(metrics["series"]["prix_go_volume"])
    maximum = float(donnees["p75"].max()) * 1.2

    base = alt.Chart(donnees).encode(
        x=alt.X(
            "libelle:N",
            sort=None,
            title="Volume",
            axis=alt.Axis(
                labelAngle=0,
                labelFontSize=11,
                labelColor=TEXTE,
                titleColor=TEXTE,
                grid=False,
                tickSize=0,
            ),
        ),
        y=alt.Y(
            "prix_go:Q",
            title="Prix médian au Go (€)",
            scale=alt.Scale(domain=[0, maximum]),
            axis=alt.Axis(
                tickCount=5,
                labelColor=TEXTE,
                titleColor=TEXTE,
                grid=True,
                gridColor="#E4E7EC",
            ),
        ),
    )
    barres = base.mark_bar(
        color=BLEU, cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=32
    ).encode(
        tooltip=[
            alt.Tooltip("libelle:N", title="Volume"),
            alt.Tooltip("prix_go:Q", title="Médiane €/Go", format=".2f"),
            alt.Tooltip("p25:Q", title="1er quartile", format=".2f"),
            alt.Tooltip("p75:Q", title="3e quartile", format=".2f"),
            alt.Tooltip("offres:Q", title="Offres"),
        ]
    )
    ecarts = base.mark_rule(color=TEXTE, strokeWidth=2).encode(
        y="p25:Q", y2="p75:Q"
    )
    valeurs = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-6,
        fontSize=11,
        fontWeight="bold",
        color=TEXTE,
    ).encode(y="p75:Q", text=alt.Text("prix_go:Q", format=".2f"))

    return _finaliser((barres + ecarts + valeurs).properties(height=300))
