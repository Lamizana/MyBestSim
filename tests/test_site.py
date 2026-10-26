import unittest

from mybestsim import site


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = site.load_metrics()
        cls.html = site.render(cls.metrics)

    def test_chiffres_presents(self):
        for attendu in ["5 056", "56", "5,36", "154,63", "14,49", "29,30", "Airalo"]:
            self.assertIn(attendu, self.html)

    def test_six_cartes_kpi(self):
        self.assertEqual(self.html.count('class="carte-kpi"'), 6)

    def test_un_graphique_svg(self):
        self.assertEqual(self.html.count("<svg "), 1)

    def test_page_autonome(self):
        self.assertNotIn("<script src=", self.html)
        self.assertNotIn('<link rel="stylesheet"', self.html)
        self.assertNotIn("@import", self.html)

    def test_rendu_deterministe(self):
        self.assertEqual(site.render(self.metrics), self.html)

    def test_format_fr(self):
        self.assertEqual(site.format_fr(5056), "5 056")
        self.assertEqual(site.format_fr(14.49, 2), "14,49")


if __name__ == "__main__":
    unittest.main()
