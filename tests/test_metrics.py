import unittest

from mybestsim import metrics
from mybestsim.clean import clean_data
from mybestsim.config import DATA_DIR
from mybestsim.ingest import load_data


class MetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = clean_data(load_data(DATA_DIR))

    def test_total_cards(self):
        self.assertEqual(metrics.total_cards(self.clean), 5056)

    def test_cards_above_price(self):
        self.assertEqual(metrics.cards_above_price(self.clean), 56)

    def test_price_range(self):
        self.assertEqual(metrics.price_range(self.clean), {"min": 5.36, "max": 154.63})

    def test_mean_data_gb(self):
        self.assertEqual(
            metrics.mean_data_gb(self.clean),
            {"valeur": 14.49, "nb_offres": 4403},
        )

    def test_mean_price(self):
        self.assertEqual(
            metrics.mean_price(self.clean),
            {"moyenne": 29.3, "mediane": 20.7},
        )

    def test_provider_distribution_ordre(self):
        repartition = metrics.provider_distribution(self.clean)
        self.assertEqual(len(repartition), 18)
        self.assertEqual(repartition[0], {"provider": "Airalo", "cartes": 722, "part_pct": 14.3})
        self.assertEqual(repartition[-1]["provider"], "4S eSIM")

    def test_provider_distribution_reconciliation(self):
        repartition = metrics.provider_distribution(self.clean)
        self.assertEqual(sum(ligne["cartes"] for ligne in repartition), 5056)
        self.assertAlmostEqual(sum(ligne["part_pct"] for ligne in repartition), 100.0, delta=0.2)

    def test_provider_distribution_tri_decroissant(self):
        cartes = [ligne["cartes"] for ligne in metrics.provider_distribution(self.clean)]
        self.assertEqual(cartes, sorted(cartes, reverse=True))


if __name__ == "__main__":
    unittest.main()
