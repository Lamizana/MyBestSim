import sys

import pandas as pd

from mybestsim.config import CLEAN_OUTPUT, DATA_DIR, RAW_OUTPUT
from mybestsim.etl import clean_data, load_raw, write_csv


def run() -> pd.DataFrame:
    """Lit les sources, nettoie et écrit les deux tables."""
    raw = load_raw(DATA_DIR)
    clean = clean_data(raw)
    write_csv(raw, RAW_OUTPUT)
    write_csv(clean, CLEAN_OUTPUT)
    return clean


def main() -> int:
    try:
        clean = run()
    except (UnicodeDecodeError, OSError, ValueError) as erreur:
        print(f"Échec : {erreur}")
        return 1

    print(f"{len(clean)} lignes, {len(clean.columns)} colonnes")
    print(f"Écrit dans {RAW_OUTPUT} et {CLEAN_OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
