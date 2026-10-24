import json
import tempfile
import unittest
from pathlib import Path

from mybestsim import metrics
from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw, write_json


class MetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = clean_data(load_raw(DATA_DIR))

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

    def test_compute_metrics_structure(self):
        rapport = metrics.compute_metrics(self.clean)
        self.assertEqual(set(rapport), {"meta", "kpi"})
        self.assertEqual(
            set(rapport["kpi"]),
            {
                "total_cartes",
                "prix_superieur_100",
                "fourchette_prix",
                "data_gb_moyenne",
                "prix_moyen",
                "fournisseurs",
            },
        )
        self.assertEqual(
            rapport["meta"],
            {"lignes": 5056, "fournisseurs": 18, "devise": "EUR"},
        )

    def test_compute_metrics_valeurs(self):
        kpi = metrics.compute_metrics(self.clean)["kpi"]
        self.assertEqual(kpi["total_cartes"]["valeur"], 5056)
        self.assertEqual(kpi["prix_superieur_100"]["valeur"], 56)
        self.assertEqual(
            kpi["fourchette_prix"]["valeur"],
            {"min": 5.36, "max": 154.63},
        )
        self.assertEqual(kpi["data_gb_moyenne"]["valeur"], 14.49)
        self.assertEqual(
            kpi["prix_moyen"]["valeur"],
            {"moyenne": 29.3, "mediane": 20.7},
        )
        self.assertEqual(
            sum(ligne["cartes"] for ligne in kpi["fournisseurs"]["valeur"]),
            5056,
        )

    def test_write_json_round_trip(self):
        rapport = metrics.compute_metrics(self.clean)

        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "metrics.json"
            write_json(rapport, chemin)
            premier = chemin.read_bytes()
            write_json(rapport, chemin)
            second = chemin.read_bytes()

        self.assertEqual(premier, second)
        self.assertEqual(json.loads(premier), rapport)

    def test_write_json_refuse_nan(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "metrics.json"
            with self.assertRaises(ValueError):
                write_json({"valeur": float("nan")}, chemin)


if __name__ == "__main__":
    unittest.main()
