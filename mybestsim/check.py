"""Valide les données de data/raw sans lancer Streamlit."""

import sys
import warnings

from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw


def main() -> int:
    """Affiche les avertissements, puis le résultat ou une erreur lisible."""
    with warnings.catch_warnings(record=True) as capture:
        warnings.simplefilter("always")
        try:
            propre = clean_data(load_raw(DATA_DIR))
        except (OSError, ValueError) as erreur:
            for avertissement in capture:
                print(f"Avertissement : {avertissement.message}", flush=True)
            print(f"Erreur de données : {erreur}", file=sys.stderr)
            return 1

    for avertissement in capture:
        print(f"Avertissement : {avertissement.message}")
    print(f"{len(propre)} offres valides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
