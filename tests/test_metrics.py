import unittest

from mybestsim import metrics
from mybestsim.config import DATA_DIR
from mybestsim.etl import clean_data, load_raw


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

    def test_prix_go_median(self):
        self.assertEqual(metrics.prix_go_median(self.clean), 2.55)

    def test_illimitees_prix(self):
        self.assertEqual(
            metrics.illimitees_prix(self.clean),
            {"offres": 653, "prix_median": 51.28},
        )

    def test_prix_go_par_volume(self):
        serie = metrics.prix_go_par_volume(self.clean)
        self.assertEqual(len(serie), 6)
        self.assertEqual(serie[0]["libelle"], "1 Go")
        self.assertEqual(serie[0]["prix_go"], 6.71)
        self.assertEqual(serie[-1]["prix_go"], 1.18)
        self.assertEqual(sum(ligne["offres"] for ligne in serie), 4403)
        for ligne in serie:
            self.assertLess(ligne["p25"], ligne["prix_go"])
            self.assertLess(ligne["prix_go"], ligne["p75"])

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
        self.assertEqual(set(rapport), {"meta", "kpi", "series"})
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
            {
                "lignes": 5056,
                "fournisseurs": 18,
                "devise": "EUR",
                "illimitees": {"offres": 653, "prix_median": 51.28},
            },
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
        self.assertEqual(kpi["data_gb_moyenne"]["nb_offres"], 4403)
        self.assertEqual(
            kpi["prix_moyen"]["valeur"],
            {"moyenne": 29.3, "mediane": 20.7},
        )
        self.assertEqual(
            sum(ligne["cartes"] for ligne in kpi["fournisseurs"]["valeur"]),
            5056,
        )

    def test_price_histogram(self):
        histogramme = metrics.price_histogram(self.clean)
        self.assertEqual(len(histogramme), 16)
        self.assertEqual(sum(tranche["offres"] for tranche in histogramme), 5056)
        self.assertEqual(histogramme[0], {"min": 0, "max": 10, "offres": 887})
        self.assertEqual(histogramme[-1], {"min": 150, "max": 160, "offres": 3})


class MeilleuresOffresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = clean_data(load_raw(DATA_DIR))
        cls.offres = metrics.meilleures_offres(cls.clean)

    def test_nombre_de_combinaisons(self):
        self.assertEqual(len(self.offres), 1113)

    def test_pays_et_zones(self):
        self.assertEqual(len({o["code"] for o in self.offres if not o["zone"]}), 50)
        self.assertEqual(len({o["code"] for o in self.offres if o["zone"]}), 4)

    def test_volumes_et_durees(self):
        self.assertEqual(
            {o["volume"] for o in self.offres},
            {"1 Go", "3 Go", "5 Go", "10 Go", "20 Go", "50 Go", "Illimité"},
        )
        self.assertEqual({o["validity_days"] for o in self.offres}, {7, 15, 30})

    def test_prix_coherents(self):
        for offre in self.offres:
            self.assertLessEqual(offre["prix"], offre["prix_max"])
            self.assertIn("provider_max", offre)
            self.assertTrue(offre["provider_max"])
            self.assertGreaterEqual(offre["offres"], 1)

    def test_espagne_dix_go_quinze_jours(self):
        offre = next(
            o
            for o in self.offres
            if o["code"] == "ES" and o["volume"] == "10 Go" and o["validity_days"] == 15
        )
        self.assertEqual(offre["provider"], "Ubigi")
        self.assertEqual(offre["prix"], 18.52)
        self.assertEqual(offre["offres"], 4)

    def test_deterministe(self):
        self.assertEqual(metrics.meilleures_offres(self.clean), self.offres)


if __name__ == "__main__":
    unittest.main()
