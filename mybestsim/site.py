import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mybestsim.config import METRICS_OUTPUT, PROJECT_ROOT

TEMPLATES_DIR = PROJECT_ROOT / "templates"
SITE_DIR = PROJECT_ROOT / "site"
SITE_OUTPUT = SITE_DIR / "index.html"


def format_fr(valeur, decimales: int = 0) -> str:
    """Formate un nombre à la française : 5056 -> 5 056, 14.49 -> 14,49."""
    texte = f"{valeur:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",")


def load_metrics(path: Path = METRICS_OUTPUT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_histogram_svg(tranches: list) -> str:
    largeur, hauteur = 680, 240
    gauche, bas, haut = 44, 30, 14
    largeur_plot = largeur - gauche - 10
    hauteur_plot = hauteur - bas - haut
    maximum = max(tranche["offres"] for tranche in tranches) or 1
    largeur_barre = largeur_plot / len(tranches)

    elements = [
        f'<svg viewBox="0 0 {largeur} {hauteur}" role="img" '
        'aria-label="Histogramme des prix par tranche de 10 euros">'
    ]

    for index, tranche in enumerate(tranches):
        hauteur_barre = tranche["offres"] / maximum * hauteur_plot
        x = gauche + index * largeur_barre
        y = haut + hauteur_plot - hauteur_barre
        elements.append(
            f'<rect x="{x + 1:.1f}" y="{y:.1f}" width="{largeur_barre - 2:.1f}" '
            f'height="{hauteur_barre:.1f}" fill="#007bff">'
            f'<title>{tranche["min"]}–{tranche["max"]} € : {tranche["offres"]} offres</title>'
            "</rect>"
        )

    elements.append(
        f'<line x1="{gauche}" y1="{haut + hauteur_plot}" '
        f'x2="{gauche + largeur_plot}" y2="{haut + hauteur_plot}" stroke="#e4e7ec"/>'
    )

    for index, tranche in enumerate(tranches):
        if tranche["min"] % 20 == 0:
            x = gauche + index * largeur_barre + largeur_barre / 2
            elements.append(
                f'<text x="{x:.1f}" y="{hauteur - 8}" text-anchor="middle" '
                f'font-size="11" fill="#667085">{tranche["min"]}</text>'
            )

    for valeur in (0, maximum // 2, maximum):
        y = haut + hauteur_plot - valeur / maximum * hauteur_plot
        elements.append(
            f'<text x="{gauche - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#667085">{format_fr(valeur)}</text>'
        )

    elements.append(
        f'<text x="{gauche + largeur_plot:.1f}" y="{hauteur - 8}" text-anchor="middle" '
        f'font-size="11" fill="#667085">{format_fr(tranches[-1]["max"])}</text>'
    )

    elements.append("</svg>")
    return "".join(elements)




def render(metrics: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["fr"] = format_fr
    template = env.get_template("index.html.j2")

    fournisseurs = metrics["kpi"]["fournisseurs"]["valeur"]

    return template.render(
        meta=metrics["meta"],
        kpi=metrics["kpi"],
        series=metrics["series"],
        fournisseurs=fournisseurs,
        max_cartes=max(ligne["cartes"] for ligne in fournisseurs),
        histogramme=build_histogram_svg(metrics["series"]["histogramme_prix"]),
    )


def main() -> int:
    try:
        metrics = load_metrics()
        html = render(metrics)
    except FileNotFoundError:
        print(f"{METRICS_OUTPUT} absent : lance d'abord python -m mybestsim.report")
        return 1
    except (OSError, ValueError) as erreur:
        print(f"Échec : {erreur}")
        return 1

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    SITE_OUTPUT.write_text(html, encoding="utf-8")
    print(f"Page écrite dans {SITE_OUTPUT} ({len(html)} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
