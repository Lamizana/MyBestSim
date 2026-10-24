import tempfile
import unittest
from pathlib import Path

from mybestsim.config import DATA_DIR
from mybestsim.ingest import load_data


class LoadDataTest(unittest.TestCase):
    def test_lit_les_18_fichiers(self):
        raw = load_data(DATA_DIR)
        self.assertEqual(raw.shape, (5056, 12))
        self.assertEqual(raw["provider"].nunique(), 18)

    def test_refuse_dossier_vide(self):
        with tempfile.TemporaryDirectory() as dossier:
            with self.assertRaises(ValueError):
                load_data(Path(dossier))

    def test_refuse_colonnes_differentes(self):
        with tempfile.TemporaryDirectory() as dossier:
            fichier = Path(dossier) / "faux.csv"
            fichier.write_text("sku,provider\nx,y\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_data(Path(dossier))


if __name__ == "__main__":
    unittest.main()
