import tempfile
import unittest
from pathlib import Path

from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_clean, load_raw, write_csv


class LoadDataTest(unittest.TestCase):
    def test_lit_les_18_fichiers(self):
        raw = load_raw(DATA_DIR)
        self.assertEqual(raw.shape, (5056, 12))
        self.assertEqual(raw["provider"].nunique(), 18)

    def test_refuse_dossier_vide(self):
        with tempfile.TemporaryDirectory() as dossier:
            with self.assertRaises(ValueError):
                load_raw(Path(dossier))

    def test_refuse_colonnes_differentes(self):
        with tempfile.TemporaryDirectory() as dossier:
            fichier = Path(dossier) / "faux.csv"
            fichier.write_text("sku,provider\nx,y\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_raw(Path(dossier))

    def test_round_trip_table_propre(self):
        clean = clean_data(load_raw(DATA_DIR))

        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "clean.csv"
            write_csv(clean, chemin)
            relu = load_clean(chemin)

        self.assertEqual(relu.shape, clean.shape)
        self.assertEqual(list(relu.columns), list(clean.columns))
        self.assertEqual(int(relu["country_code"].isna().sum()), 0)
        self.assertEqual(int(relu["is_unlimited"].sum()), 653)
        self.assertEqual(relu["validity_days"].dtype.kind, "i")
        self.assertAlmostEqual(relu["price"].mean(), clean["price"].mean())


if __name__ == "__main__":
    unittest.main()
