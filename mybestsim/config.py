"""Constantes partagées : chemins, schéma d'entrée et vocabulaire du contrat."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
ASSETS_DIR = PROJECT_ROOT / "assets"
LOGO = ASSETS_DIR / "logo.png"
LOGO_MARQUE = ASSETS_DIR / "logo_wordmark.png"

EXPECTED_COLUMNS = [
    "sku",
    "provider",
    "product_name",
    "country_code",
    "country_name",
    "data_gb",
    "data_display",
    "validity_days",
    "price",
    "currency",
    "network",
    "top_up",
]

REGION_CODES = {"EU", "AS", "NA", "WW"}
ZONE_PREFIX = "ZONE_"

SEUIL_PRIX = 100
DEVISE = "EUR"
RESEAUX = {"4G", "5G"}
VALEURS_TOP_UP = {"oui": True, "non": False}
LIBELLE_ILLIMITE = "Illimité"

VOLUMES = ["1 Go", "3 Go", "5 Go", "10 Go", "20 Go", "50 Go", LIBELLE_ILLIMITE]
VOLUME_DEFAUT = "10 Go"
DUREES = [7, 15, 30]
DUREE_DEFAUT = 15
