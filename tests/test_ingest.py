import tempfile
import unittest
import warnings
from pathlib import Path

import pandas as pd

from mybestsim.config import DATA_DIR, EXPECTED_COLUMNS
from mybestsim.etl import clean_data, load_raw

LIGNE = "sku-1,P,Test,FR,France,10,10 Go,30,20.00,EUR,4G,non"
AUTRE = "sku-2,P,Autre,FR,France,5,5 Go,15,10.00,EUR,4G,oui"


def ecrire_csv(dossier: str, nom: str, lignes: list[str]) -> Path:
    chemin = Path(dossier) / nom
    entete = ",".join(EXPECTED_COLUMNS)
    chemin.write_text(entete + "\n" + "\n".join(lignes) + "\n", encoding="utf-8")
    return chemin


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

    def test_ignore_fichier_identique(self):
        with tempfile.TemporaryDirectory() as dossier:
            ecrire_csv(dossier, "a.csv", [LIGNE])
            ecrire_csv(dossier, "b.csv", [LIGNE])

            with warnings.catch_warnings(record=True) as journal:
                warnings.simplefilter("always")
                raw = load_raw(Path(dossier))

        self.assertEqual(len(raw), 1)
        self.assertTrue(any("identique" in str(a.message) for a in journal))

    def test_garde_les_lignes_nouvelles(self):
        with tempfile.TemporaryDirectory() as dossier:
            ecrire_csv(dossier, "a.csv", [LIGNE])
            ecrire_csv(dossier, "b.csv", [LIGNE, AUTRE])
            raw = load_raw(Path(dossier))

        self.assertEqual(set(raw["sku"]), {"sku-1", "sku-2"})
        self.assertEqual(len(raw), 2)

    def test_refuse_sku_avec_valeurs_divergentes(self):
        with tempfile.TemporaryDirectory() as dossier:
            ecrire_csv(dossier, "a.csv", [LIGNE])
            ecrire_csv(dossier, "b.csv", [LIGNE.replace("20.00", "25.00")])
            with self.assertRaises(ValueError) as capture:
                load_raw(Path(dossier))

        message = str(capture.exception)
        self.assertIn("sku-1", message)
        self.assertIn("price", message)
        self.assertIn("a.csv", message)
        self.assertIn("b.csv", message)

    def test_message_doublons_tronque(self):
        raw = load_raw(DATA_DIR)
        duplique = pd.concat([raw.iloc[[0]]] * 7, ignore_index=True)
        with self.assertRaises(ValueError) as capture:
            clean_data(duplique)
        self.assertIn("(+1 autres)", str(capture.exception))


if __name__ == "__main__":
    unittest.main()
