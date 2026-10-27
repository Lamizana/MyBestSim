"""Construit la page HTML de l'article à partir du Markdown.

Usage : uv run --with "markdown>=3.6" python article/build.py
"""

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

import markdown

ARTICLE = Path(__file__).resolve().parent
SOURCE = ARTICLE / "internet-croisiere-esim.md"
TEMPLATE = ARTICLE / "template.html"
SITE = ARTICLE / "_site"
RACINE = ARTICLE.parent

SITE_URL = "https://lamizana.github.io/MyBestSim/"
OG_IMAGE = SITE_URL + "og.png"

MOIS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def lire_front_matter(texte: str) -> tuple[dict, str]:
    """Sépare le front matter YAML minimal du corps Markdown."""
    if not texte.startswith("---"):
        return {}, texte

    _, bloc, corps = texte.split("---", 2)
    meta = {}
    for ligne in bloc.strip().splitlines():
        cle, _, valeur = ligne.partition(":")
        if cle.strip():
            meta[cle.strip()] = valeur.strip().strip('"')
    return meta, corps.lstrip("\n")


def date_francaise(iso: str) -> str:
    jour = date.fromisoformat(iso)
    return f"{jour.day} {MOIS[jour.month - 1]} {jour.year}"


def construire_sommaire(tokens: list[dict]) -> str:
    """Construit le sommaire à partir des titres H2 et H3."""
    if not tokens:
        return ""

    racine = tokens[0]
    entrees = racine.get("children", [])
    if not entrees:
        return ""

    lignes = ["<nav class=\"toc\" aria-label=\"Sommaire\">", "<p>Sommaire</p>", "<ol>"]
    for entree in entrees:
        titre = html.escape(entree["name"])
        lignes.append(f'<li><a href="#{entree["id"]}">{titre}</a>')
        enfants = entree.get("children", [])
        if enfants:
            lignes.append("<ol>")
            for enfant in enfants:
                nom = html.escape(enfant["name"])
                lignes.append(f'<li><a href="#{enfant["id"]}">{nom}</a></li>')
            lignes.append("</ol>")
        lignes.append("</li>")
    lignes.extend(["</ol>", "</nav>"])
    return "\n".join(lignes)


def rendre() -> None:
    texte = SOURCE.read_text(encoding="utf-8")
    meta, corps = lire_front_matter(texte)

    # Les suggestions d'images ne doivent pas apparaître sur la page publiée.
    corps = re.sub(
        r"^> \*\*(?:Image|Capture) suggérée\*\*.*\n?", "", corps, flags=re.M
    )

    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"])
    contenu = md.convert(corps)

    h1 = re.search(r"<h1[^>]*>.*?</h1>", contenu, flags=re.S)
    titre_html = h1.group(0) if h1 else f"<h1>{html.escape(meta.get('title', ''))}</h1>"
    if h1:
        contenu = contenu.replace(h1.group(0), "", 1)

    contenu = contenu.replace("<table>", '<div class="table-wrap"><table>')
    contenu = contenu.replace("</table>", "</table></div>")

    mots = re.findall(r"\w+", re.sub(r"<[^>]+>", " ", contenu))
    minutes = max(1, round(len(mots) / 200))

    donnees = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta.get("title", ""),
        "description": meta.get("description", ""),
        "datePublished": meta.get("date", ""),
        "dateModified": meta.get("date", ""),
        "inLanguage": "fr-FR",
        "author": {
            "@type": "Organization",
            "name": "MyBestSim",
            "url": "https://mybestsim.com/fr/",
        },
        "publisher": {
            "@type": "Organization",
            "name": "MyBestSim",
            "url": "https://mybestsim.com/fr/",
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE_URL},
        "image": OG_IMAGE,
        "isPartOf": {
            "@type": "WebSite",
            "name": "MyBestSim",
            "url": "https://mybestsim.com/fr/",
        },
    }

    page = TEMPLATE.read_text(encoding="utf-8")
    remplacements = {
        "{{TITLE}}": html.escape(meta.get("title", ""), quote=True),
        "{{DESCRIPTION}}": html.escape(meta.get("description", ""), quote=True),
        "{{CANONICAL}}": SITE_URL,
        "{{OG_IMAGE}}": OG_IMAGE,
        "{{DATE_FR}}": date_francaise(meta["date"]),
        "{{READING_TIME}}": str(minutes),
        "{{H1}}": titre_html,
        "{{TOC}}": construire_sommaire(md.toc_tokens),
        "{{JSONLD}}": json.dumps(donnees, ensure_ascii=False),
        "{{CONTENT}}": contenu,
    }
    for cle, valeur in remplacements.items():
        page = page.replace(cle, valeur)

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / "index.html").write_text(page, encoding="utf-8")

    shutil.copy2(ARTICLE / "og.png", SITE / "og.png")
    shutil.copy2(RACINE / "assets" / "logo_wordmark.png", SITE / "logo_wordmark.png")
    shutil.copy2(RACINE / "assets" / "logo.png", SITE / "logo.png")

    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}</loc></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )

    print(f"Page générée : {SITE / 'index.html'}")
    print(f"{len(mots)} mots · {minutes} min de lecture")


if __name__ == "__main__":
    rendre()
