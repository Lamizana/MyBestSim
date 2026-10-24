from pathlib import Path

import pandas as pd

from mybestsim.config import EXPECTED_COLUMNS


def load_data(data_dir: Path) -> pd.DataFrame:
    """Lit les CSV du dossier, contrôle les en-têtes et empile les tables."""
    fichiers = sorted(data_dir.glob("*.csv"))
    if not fichiers:
        raise ValueError(f"Aucun CSV trouvé dans {data_dir}")

    tableaux = []

    for fichier in fichiers:
        df = pd.read_csv(fichier, dtype=str, keep_default_na=False, encoding="utf-8-sig")

        if list(df.columns) != EXPECTED_COLUMNS:
            raise ValueError(
                f"Colonnes différentes dans {fichier.name}\n"
                f"  attendu : {EXPECTED_COLUMNS}\n"
                f"  trouvé  : {list(df.columns)}"
            )

        tableaux.append(df)

    return pd.concat(tableaux, ignore_index=True)
