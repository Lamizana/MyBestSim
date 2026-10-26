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


# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
def halteres(offres: list) -> alt.Chart:
    """Graphique en haltères : prix le moins cher et le plus cher par pays.

    La longueur du segment représente l'économie possible en choisissant le
    bon fournisseur ; la position donne le niveau de prix.
    """
    donnees = pd.DataFrame(offres)
    donnees["economie"] = donnees["prix_max"] - donnees["prix"]
    donnees = donnees.sort_values("economie", ascending=False, kind="stable")
    donnees["gain"] = [
        f"+{valeur:.2f} €".replace(".", ",") for valeur in donnees["economie"]
    ]
    maximum = float(donnees["prix_max"].max()) * 1.18

    base = alt.Chart(donnees).encode(
        y=alt.Y(
            "destination:N",
            sort=None,
            title=None,
            axis=alt.Axis(
                labelFontSize=12, labelColor=TEXTE, ticks=False, domain=False
            ),
        ),
        x=alt.X(
            "prix:Q",
            title="Prix (€)",
            scale=alt.Scale(domain=[0, maximum]),
            axis=alt.Axis(tickCount=5, gridColor="#eef0f3"),
        ),
    )
    segments = base.mark_rule(color=BORD, strokeWidth=3).encode(x2="prix_max:Q")
    minimum = base.mark_circle(size=90, color=BLEU).encode(
        tooltip=[
            alt.Tooltip("destination:N", title="Destination"),
            alt.Tooltip("provider:N", title="Fournisseur le moins cher"),
            alt.Tooltip("prix:Q", title="Prix min", format=".2f"),
            alt.Tooltip("prix_max:Q", title="Prix max", format=".2f"),
            alt.Tooltip("offres:Q", title="Offres comparées"),
        ]
    )
    maximum_prix = base.mark_circle(size=70, color=ROUGE).encode(x="prix_max:Q")
    gains = base.mark_text(align="left", dx=8, color=MUTED, fontSize=11).encode(
        x="prix_max:Q", text="gain:N"
    )
    hauteur = max(200, 38 * len(donnees))
    return _finaliser(
        (segments + minimum + maximum_prix + gains).properties(height=hauteur)
    )


def prix(metrics: dict) -> alt.Chart:
    """Histogramme des prix par tranche de 10 €, avec seuil à 100 €."""
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
        text=alt.condition(
            (alt.datum.offres > 50) | (alt.datum.min >= SEUIL_PRIX),
            alt.Text("offres:Q"),
            alt.value(""),
        ),
    )

    return _finaliser((barres + valeurs).properties(height=420))
