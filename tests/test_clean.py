import unittest

from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw


class CleanDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_raw(DATA_DIR)
        cls.clean = clean_data(cls.raw)

    def test_shape(self):
        self.assertEqual(self.clean.shape, (5056, 15))

    def test_duree_entier(self):
        self.assertEqual(str(self.clean["validity_days"].dtype), "int64")
        self.assertEqual(sorted(self.clean["validity_days"].unique()), [7, 15, 30])

    def test_illimitees(self):
        self.assertEqual(int(self.clean["is_unlimited"].sum()), 653)

    def test_zones(self):
        self.assertEqual(int(self.clean["is_region"].sum()), 778)
        zones = self.clean.loc[self.clean["is_region"], "country_code"].unique()
        self.assertEqual(sorted(zones), ["ZONE_AS", "ZONE_EU", "ZONE_NA", "ZONE_WW"])

    def test_aucun_code_pays_manquant(self):
        self.assertEqual(int(self.clean["country_code"].isna().sum()), 0)

    def test_moyenne_data_gb(self):
        self.assertAlmostEqual(self.clean["data_gb"].mean(), 14.49, places=2)

    def test_prix_au_go_absent_seulement_si_illimite(self):
        self.assertEqual(
            int(self.clean["price_per_gb"].isna().sum()),
            int(self.clean["is_unlimited"].sum()),
        )

    def test_refuse_sku_duplique(self):
        bad = self.raw.copy()
        bad.loc[1, "sku"] = bad.loc[0, "sku"]
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_provider_vide(self):
        bad = self.raw.copy()
        bad.loc[0, "provider"] = ""
        with self.assertRaises(ValueError) as contexte:
            clean_data(bad)
        self.assertIn("provider", str(contexte.exception))

    def test_refuse_country_code_vide(self):
        bad = self.raw.copy()
        bad.loc[0, "country_code"] = ""
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_data_display_vide(self):
        bad = self.raw.copy()
        bad.loc[0, "data_display"] = ""
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_prix_non_positif(self):
        bad = self.raw.copy()
        bad.loc[0, "price"] = "0"
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_illimite_incoherent(self):
        bad = self.raw.copy()
        index = bad.index[bad["data_display"] == "Illimité"][0]
        bad.loc[index, "data_display"] = "5 Go"
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_duree_illisible(self):
        bad = self.raw.copy()
        bad.loc[0, "validity_days"] = "abc"
        with self.assertRaises(ValueError):
            clean_data(bad)

    def test_refuse_duree_non_positive(self):
        bad = self.raw.copy()
        bad.loc[0, "validity_days"] = "0"
        with self.assertRaises(ValueError):
            clean_data(bad)


if __name__ == "__main__":
    unittest.main()
