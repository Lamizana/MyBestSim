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
IMAGE_ARTICLE = SITE_URL + "images/mbs_intro_02.jpeg"
LOGO_PUBLISHER = SITE_URL + "images/logo_publisher.png"
SOCIALS = [
    "https://www.instagram.com/mybestsim/",
    "https://www.facebook.com/people/Mybestsim/61568955372340/",
    "https://www.youtube.com/@MyBestSim",
]

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


def construire_faq(contenu: str) -> dict | None:
    """Construit le balisage FAQPage à partir des accordéons générés."""
    questions = re.findall(
        r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>',
        contenu,
        flags=re.S,
    )
    if not questions:
        return None

    def texte(fragment: str) -> str:
        return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": texte(question),
                "acceptedAnswer": {"@type": "Answer", "text": texte(reponse)},
            }
            for question, reponse in questions
        ],
    }


def construire_breadcrumb() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Accueil",
                "item": "https://mybestsim.com/fr/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Blog",
                "item": "https://mybestsim.com/fr/articles/",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": "Croisière",
                "item": SITE_URL,
            },
        ],
    }


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

    brief = re.search(r'<div class="brief">.*?</div>', contenu, flags=re.S)
    brief_html = brief.group(0) if brief else ""
    if brief:
        contenu = contenu.replace(brief_html, "", 1)

    contenu = contenu.replace("<table>", '<div class="table-wrap"><table>')
    contenu = contenu.replace("</table>", "</table></div>")
    contenu = contenu.replace("<th>", '<th scope="col">')

    faq = construire_faq(contenu)
    faq_jsonld = (
        f'<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>'
        if faq
        else ""
    )
    breadcrumb_jsonld = (
        '<script type="application/ld+json">'
        f"{json.dumps(construire_breadcrumb(), ensure_ascii=False)}"
        "</script>"
    )

    mots = re.findall(r"\w+", re.sub(r"<[^>]+>", " ", contenu))
    minutes = max(1, round(len(mots) / 200))

    donnees = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta.get("title", ""),
        "description": meta.get("description", ""),
        "datePublished": meta.get("date", ""),
        "dateModified": meta.get("updated", meta.get("date", "")),
        "inLanguage": "fr-FR",
        "image": [IMAGE_ARTICLE],
        "author": {
            "@type": "Organization",
            "name": "MyBestSim",
            "url": "https://mybestsim.com/fr/",
            "sameAs": SOCIALS,
        },
        "publisher": {
            "@type": "Organization",
            "name": "MyBestSim",
            "url": "https://mybestsim.com/fr/",
            "logo": {
                "@type": "ImageObject",
                "url": LOGO_PUBLISHER,
                "width": 600,
                "height": 60,
            },
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE_URL},
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
        "{{DATE_FR}}": date_francaise(meta["date"]),
        "{{DATE_ISO}}": meta.get("date", ""),
        "{{READING_TIME}}": str(minutes),
        "{{H1}}": titre_html,
        "{{BRIEF}}": brief_html,
        "{{TOC}}": construire_sommaire(md.toc_tokens),
        "{{JSONLD}}": json.dumps(donnees, ensure_ascii=False),
        "{{FAQ_JSONLD}}": faq_jsonld,
        "{{BREADCRUMB_JSONLD}}": breadcrumb_jsonld,
        "{{CONTENT}}": contenu,
    }
    for cle, valeur in remplacements.items():
        page = page.replace(cle, valeur)

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / "index.html").write_text(page, encoding="utf-8")

    shutil.copytree(ARTICLE / "images", SITE / "images")
    shutil.copy2(RACINE / "assets" / "logo_wordmark.png", SITE / "logo_wordmark.png")
    shutil.copy2(ARTICLE / "style.css", SITE / "style.css")

    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}</loc>"
        f"<lastmod>{meta.get('updated', meta['date'])}</lastmod></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )

    print(f"Page générée : {SITE / 'index.html'}")
    print(f"{len(mots)} mots · {minutes} min de lecture")


if __name__ == "__main__":
    rendre()
