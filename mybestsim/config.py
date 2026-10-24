from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_OUTPUT = PROCESSED_DIR / "all_products.csv"
CLEAN_OUTPUT = PROCESSED_DIR / "clean_products.csv"

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
