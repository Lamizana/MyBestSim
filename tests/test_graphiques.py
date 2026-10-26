import unittest

from mybestsim import graphiques
from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw
from mybestsim.metrics import compute_metrics


class GraphiquesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = compute_metrics(clean_data(load_raw(DATA_DIR)))

    def test_barres_fournisseurs(self):
        spec = graphiques.fournisseurs(self.metrics).to_dict()
        self.assertEqual(len(spec["layer"]), 2)
        self.assertEqual(spec["height"], 440)

    def test_histogramme(self):
        spec = graphiques.prix(self.metrics).to_dict()
        self.assertEqual(len(spec["layer"]), 3)
        self.assertEqual(spec["height"], 280)

    def test_police_commune(self):
        spec = graphiques.prix(self.metrics).to_dict()
        self.assertEqual(spec["config"]["font"], "Poppins, sans-serif")


if __name__ == "__main__":
    unittest.main()
