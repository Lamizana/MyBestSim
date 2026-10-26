"""Graphiques Altair du dashboard.

Aucun HTML, aucun CSS : uniquement des spécifications Vega-Lite passées à
``st.altair_chart``.
"""

import altair as alt
import pandas as pd

BLEU = "#007bff"
ROUGE = "#de1414"
MUTED = "#667085"
TEXTE = "#1d2939"
BORD = "#e4e7ec"
SEUIL_PRIX = 100


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
    """Barres horizontales triées, valeur en bout de barre."""
    donnees = pd.DataFrame(metrics["kpi"]["fournisseurs"]["valeur"])
    donnees = donnees.sort_values("cartes", ascending=False, kind="stable")
    maximum = int(donnees["cartes"].max() * 1.14)

    base = alt.Chart(donnees).encode(
        x=alt.X("cartes:Q", title=None, axis=None, scale=alt.Scale(domain=[0, maximum])),
        y=alt.Y(
            "provider:N",
            sort=None,
            title=None,
            axis=alt.Axis(labelFontSize=12, labelColor=TEXTE, ticks=False, domain=False),
        ),
    )
    barres = base.mark_bar(color=BLEU, cornerRadiusEnd=3, size=16).encode(
        tooltip=[
            alt.Tooltip("provider:N", title="Fournisseur"),
            alt.Tooltip("cartes:Q", title="Offres"),
            alt.Tooltip("part_pct:Q", title="Part (%)"),
        ]
    )
    valeurs = base.mark_text(align="left", dx=6, color=MUTED, fontSize=11).encode(
        text="cartes:Q"
    )
    return _finaliser((barres + valeurs).properties(height=440))


def prix(metrics: dict) -> alt.Chart:
    """Histogramme par tranche de 10 €, avec médiane et seuil des 100 €."""
    donnees = pd.DataFrame(metrics["series"]["histogramme_prix"])
    donnees["libelle"] = [
        f"{int(ligne['min'])}–{int(ligne['max'])} €" for _, ligne in donnees.iterrows()
    ]
    mediane = metrics["kpi"]["prix_moyen"]["valeur"]["mediane"]

    base = alt.Chart(donnees).encode(
        x=alt.X(
            "min:Q",
            title="Prix (€)",
            scale=alt.Scale(domain=[0, 160]),
            axis=alt.Axis(values=list(range(0, 161, 20)), grid=False, tickSize=0),
        ),
        x2="max:Q",
        y=alt.Y(
            "offres:Q",
            title="Nombre d'offres",
            axis=alt.Axis(
                tickCount=4,
                labelExpr="replace(format(datum.value, ',d'), ',', ' ')",
            ),
        ),
    )
    barres = base.mark_bar(color=BLEU, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        tooltip=[
            alt.Tooltip("libelle:N", title="Tranche"),
            alt.Tooltip("offres:Q", title="Offres"),
        ]
    )
    repere_mediane = (
        alt.Chart()
        .mark_rule(color=MUTED, strokeDash=[4, 4], size=1)
        .encode(x=alt.datum(mediane))
    )
    repere_seuil = (
        alt.Chart().mark_rule(color=ROUGE, size=1).encode(x=alt.datum(SEUIL_PRIX))
    )
    return _finaliser(
        (barres + repere_mediane + repere_seuil).properties(height=280)
    )
