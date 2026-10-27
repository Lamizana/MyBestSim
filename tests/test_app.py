import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


class AppTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = AppTest.from_file(str(APP), default_timeout=30).run()

    def test_aucune_exception(self):
        self.assertFalse(self.page.exception)

    def test_titre(self):
        titre = self.page.title[0].value
        self.assertIn("5 056", titre)
        self.assertIn("offres comparées", titre)

    def test_six_metriques(self):
        self.assertEqual(len(self.page.metric), 6)

    def test_valeurs_kpi(self):
        valeurs = [metrique.value for metrique in self.page.metric]
        self.assertEqual(valeurs[0], "5 056")
        self.assertEqual(valeurs[1], "56")
        self.assertIn("5,36", valeurs[2])
        self.assertIn("154,63", valeurs[2])
        self.assertEqual(valeurs[3], "14,49 Go")
        self.assertEqual(valeurs[4], "29,30 €")
        self.assertEqual(valeurs[5], "18")

    def test_prix_au_go(self):
        texte = "\n".join(element.value for element in self.page.subheader)
        self.assertIn("Prix au Go selon le volume", texte)

    def test_colonnes_tableau_offres(self):
        colonnes = list(self.page.dataframe[0].value.columns)
        self.assertEqual(
            colonnes,
            [
                "Destination",
                "Fournisseur min",
                "Prix min",
                "Fournisseur max",
                "Prix max",
                "Offres",
                "Écart",
            ],
        )

    def test_methodologie(self):
        texte = "\n".join(element.value for element in self.page.markdown)
        self.assertIn("illimitées sont exclues", texte)

    def test_recherche_sans_resultat(self):
        page = AppTest.from_file(str(APP), default_timeout=30).run()
        page.text_input[0].set_value("zzz")
        page.run()
        self.assertFalse(page.exception)


if __name__ == "__main__":
    unittest.main()
