def format_fr(valeur, decimales: int = 0) -> str:
    """Formate un nombre à la française : 5056 -> « 5 056 », 14.49 -> « 14,49 »."""
    texte = f"{valeur:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",")
