"""Tests de l'export CSV du catalogue nettoyé."""

import codecs
import io
import unittest

import pandas as pd

from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw, to_csv_bytes


class ExportCsvTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.offres = clean_data(load_raw(DATA_DIR))
        cls.csv = to_csv_bytes(cls.offres)
        cls.relu = pd.read_csv(io.BytesIO(cls.csv), encoding="utf-8-sig")

    def test_encodage_utf8_avec_bom(self):
        self.assertTrue(self.csv.startswith(codecs.BOM_UTF8))

    def test_dimensions_et_colonnes(self):
        self.assertEqual(self.relu.shape, self.offres.shape)
        self.assertEqual(list(self.relu.columns), list(self.offres.columns))

    def test_pas_de_colonne_d_index(self):
        self.assertNotIn("Unnamed: 0", self.relu.columns)

    def test_colonnes_derivees(self):
        self.assertTrue(self.relu["is_region"].any())
        self.assertTrue(self.relu["is_unlimited"].any())
        self.assertTrue(self.relu["country_code"].str.startswith("ZONE_").any())
        self.assertTrue(pd.api.types.is_numeric_dtype(self.relu["price"]))

    def test_accents_conserves(self):
        self.assertIn("Égypte", set(self.relu["country_name"]))


if __name__ == "__main__":
    unittest.main()
