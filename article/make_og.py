"""Génère la carte Open Graph 1200×630 de l'article."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SORTIE = Path(__file__).resolve().parent / "og.png"
BLEU = "#007bff"
ROUGE = "#de1414"
TEXTE = "#1d2939"
MUTED = "#667085"

GRAS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NORMAL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TITRE = "Internet en croisière : quelle eSIM choisir ?"


def couper(texte: str, police: ImageFont.FreeTypeFont, largeur: int) -> list[str]:
    lignes, courante = [], ""
    for mot in texte.split():
        essai = f"{courante} {mot}".strip()
        if police.getlength(essai) <= largeur:
            courante = essai
        else:
            lignes.append(courante)
            courante = mot
    if courante:
        lignes.append(courante)
    return lignes


image = Image.new("RGB", (1200, 630), "white")
dessin = ImageDraw.Draw(image)

dessin.rectangle((0, 0, 1200, 10), fill=BLEU)

marque = ImageFont.truetype(GRAS, 58)
dessin.text((80, 64), "MyBest", font=marque, fill=BLEU)
largeur = dessin.textlength("MyBest", font=marque)
dessin.text((80 + largeur, 64), "Sim", font=marque, fill=ROUGE)

sous_marque = ImageFont.truetype(NORMAL, 22)
dessin.text((82, 140), "Comparateur eSIM indépendant", font=sous_marque, fill=MUTED)

titre = ImageFont.truetype(GRAS, 54)
y = 220
for ligne in couper(TITRE, titre, 1040):
    dessin.text((80, y), ligne, font=titre, fill=TEXTE)
    y += 70

chapo = ImageFont.truetype(NORMAL, 27)
dessin.text(
    (80, y + 18),
    "Mer ou port, Méditerranée ou Caraïbes : la méthode pour bien choisir.",
    font=chapo,
    fill=MUTED,
)

dessin.rectangle((0, 550, 1200, 630), fill=BLEU)
pied = ImageFont.truetype(GRAS, 26)
dessin.text((80, 578), "mybestsim.com", font=pied, fill="white")
guide = ImageFont.truetype(NORMAL, 22)
dessin.text((880, 582), "Guide croisière", font=guide, fill="white")

image.save(SORTIE, "PNG")
print(f"Image générée : {SORTIE} ({image.width}×{image.height})")
