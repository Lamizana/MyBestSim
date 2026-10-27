"""Cas limites de l'ETL, sur des CSV générés à la volée.

Aucun fichier de ``data/raw/`` n'est lu ni modifié : chaque test construit son
propre dossier temporaire avec des valeurs fausses.
"""

import tempfile
import unittest
import warnings
from pathlib import Path

import pandas as pd

from mybestsim.config import EXPECTED_COLUMNS
from mybestsim.etl import clean_data, load_raw

DEFAUT = {
    "sku": "sku-1",
    "provider": "P",
    "product_name": "Test",
    "country_code": "FR",
    "country_name": "France",
    "data_gb": "10",
    "data_display": "10 Go",
    "validity_days": "30",
    "price": "20.00",
    "currency": "EUR",
    "network": "4G",
    "top_up": "non",
}


def ligne(**champs: str) -> str:
    valeurs = {**DEFAUT, **champs}
    return ",".join(valeurs[colonne] for colonne in EXPECTED_COLUMNS)


def ecrire_csv(
    dossier: Path, nom: str, lignes: list[str], encodage: str = "utf-8"
) -> Path:
    chemin = dossier / nom
    entete = ",".join(EXPECTED_COLUMNS)
    chemin.write_text(
        entete + "\n" + "\n".join(lignes) + "\n", encoding=encodage
    )
    return chemin


class EtlCasLimitesTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dossier = Path(self._tmp.name)

    # ------------------------------------------------------------------
    # Schéma et fichiers
    # ------------------------------------------------------------------
    def test_fusionne_deux_fichiers(self):
        ecrire_csv(self.dossier, "a.csv", [ligne()])
        ecrire_csv(self.dossier, "b.csv", [ligne(sku="sku-2")])

        propre = clean_data(load_raw(self.dossier))

        self.assertEqual(len(propre), 2)
        self.assertEqual(list(propre.columns), list(EXPECTED_COLUMNS) + [
            "is_unlimited", "is_region"
        ])
        self.assertEqual(propre["validity_days"].dtype.kind, "i")
        self.assertEqual(propre["price"].dtype.kind, "f")
        self.assertEqual(propre["top_up"].dtype.kind, "b")
        self.assertFalse(bool(propre["is_region"].any()))

    def test_colonne_manquante(self):
        colonnes = [c for c in EXPECTED_COLUMNS if c != "top_up"]
        (self.dossier / "a.csv").write_text(
            ",".join(colonnes) + "\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)
        self.assertIn("Colonnes différentes dans a.csv", str(capture.exception))

    def test_colonne_en_trop(self):
        (self.dossier / "a.csv").write_text(
            ",".join(EXPECTED_COLUMNS) + ",extra\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)
        self.assertIn("a.csv", str(capture.exception))

    def test_ordre_des_colonnes_strict(self):
        colonnes = list(EXPECTED_COLUMNS)
        colonnes[0], colonnes[1] = colonnes[1], colonnes[0]
        (self.dossier / "a.csv").write_text(
            ",".join(colonnes) + "\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            load_raw(self.dossier)

    def test_dossier_vide(self):
        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)
        self.assertIn("Aucun CSV", str(capture.exception))

    def test_fichier_non_csv_ignore(self):
        ecrire_csv(self.dossier, "a.csv", [ligne()])
        (self.dossier / "notes.txt").write_text("hors périmètre", encoding="utf-8")
        self.assertEqual(len(load_raw(self.dossier)), 1)

    def test_fichier_identique_ignore(self):
        ecrire_csv(self.dossier, "a.csv", [ligne()])
        ecrire_csv(self.dossier, "b.csv", [ligne()])

        with warnings.catch_warnings(record=True) as journal:
            warnings.simplefilter("always")
            brut = load_raw(self.dossier)

        self.assertEqual(len(brut), 1)
        self.assertTrue(any("identique" in str(a.message) for a in journal))

    def test_doublon_exact_entre_fichiers(self):
        ecrire_csv(self.dossier, "a.csv", [ligne()])
        ecrire_csv(self.dossier, "b.csv", [ligne(), ligne(sku="sku-2")])

        with warnings.catch_warnings(record=True) as journal:
            warnings.simplefilter("always")
            brut = load_raw(self.dossier)

        self.assertEqual(set(brut["sku"]), {"sku-1", "sku-2"})
        self.assertTrue(
            any("a.csv" in str(a.message) and "b.csv" in str(a.message)
                for a in journal)
        )

    def test_conflit_de_prix(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(price="20.00")])
        ecrire_csv(self.dossier, "b.csv", [ligne(price="25.00")])

        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)

        message = str(capture.exception)
        self.assertIn("sku-1", message)
        self.assertIn("price", message)
        self.assertIn("a.csv", message)
        self.assertIn("b.csv", message)

    def test_doublon_interne_au_fichier(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(), ligne()])
        with warnings.catch_warnings(record=True) as journal:
            warnings.simplefilter("always")
            brut = load_raw(self.dossier)
        self.assertEqual(len(brut), 1)
        self.assertTrue(any("doublons exacts" in str(a.message) for a in journal))

    def test_valeurs_vides_localisees(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(provider="")])
        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)

        message = str(capture.exception)
        self.assertIn("Valeurs vides", message)
        self.assertIn("provider", message)
        self.assertIn("a.csv", message)
        self.assertIn("ligne 2", message)
        self.assertIn("sku-1", message)

    # ------------------------------------------------------------------
    # Contrat de valeurs
    # ------------------------------------------------------------------
    def test_devise_inconnue(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(currency="USD")])
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("Devise inattendue", str(capture.exception))

    def test_devise_minuscule(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(currency="eur")])
        with self.assertRaises(ValueError):
            clean_data(load_raw(self.dossier))

    def test_reseau_inconnu(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(network="3G")])
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("Réseau inattendu", str(capture.exception))

    def test_top_up_invalide(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(top_up="yes")])
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("top_up", str(capture.exception))

    def test_prix_illisible(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(price="abc")])
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("Prix illisible", str(capture.exception))
        self.assertIn("sku-1", str(capture.exception))

    def test_prix_zero_et_negatif(self):
        for prix in ("0", "-5"):
            with self.subTest(prix=prix):
                ecrire_csv(self.dossier, "a.csv", [ligne(price=prix)])
                with self.assertRaises(ValueError) as capture:
                    clean_data(load_raw(self.dossier))
                self.assertIn("Prix non positif", str(capture.exception))

    def test_prix_virgule_refuse(self):
        morceaux = ligne().split(",")
        morceaux[8] = '"12,50"'
        ecrire_csv(self.dossier, "a.csv", [",".join(morceaux)])
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("Prix illisible", str(capture.exception))

    def test_ligne_mal_formee(self):
        ecrire_csv(self.dossier, "a.csv", [ligne() + ",extra"])
        with self.assertRaises(ValueError) as capture:
            load_raw(self.dossier)
        message = str(capture.exception)
        self.assertIn("Ligne mal formée", message)
        self.assertIn("a.csv", message)

    def test_duree_illisible_et_non_positive(self):
        for duree in ("abc", "0", "-5"):
            with self.subTest(duree=duree):
                ecrire_csv(self.dossier, "a.csv", [ligne(validity_days=duree)])
                with self.assertRaises(ValueError):
                    clean_data(load_raw(self.dossier))

    # ------------------------------------------------------------------
    # Illimité et zones
    # ------------------------------------------------------------------
    def test_illimite_avec_volume_refuse(self):
        ecrire_csv(
            self.dossier,
            "a.csv",
            [ligne(data_gb="5", data_display="Illimité")],
        )
        with self.assertRaises(ValueError) as capture:
            clean_data(load_raw(self.dossier))
        self.assertIn("Incohérence illimité", str(capture.exception))
        self.assertIn("sku-1", str(capture.exception))

    def test_volume_sans_illimite_refuse(self):
        ecrire_csv(
            self.dossier,
            "a.csv",
            [ligne(data_gb="", data_display="10 Go")],
        )
        with self.assertRaises(ValueError):
            clean_data(load_raw(self.dossier))

    def test_illimite_valide(self):
        ecrire_csv(
            self.dossier,
            "a.csv",
            [ligne(data_gb="", data_display="Illimité")],
        )
        propre = clean_data(load_raw(self.dossier))
        self.assertTrue(bool(propre.loc[0, "is_unlimited"]))
        self.assertTrue(pd.isna(propre.loc[0, "data_gb"]))

    def test_data_gb_illisible(self):
        ecrire_csv(
            self.dossier,
            "a.csv",
            [ligne(data_gb="abc", data_display="10 Go")],
        )
        with self.assertRaises(ValueError):
            clean_data(load_raw(self.dossier))

    def test_zones_prefixees_et_na_conserve(self):
        lignes = [
            ligne(sku="eu", country_code="EU", country_name="Europe"),
            ligne(sku="na", country_code="NA", country_name="Amérique du Nord"),
            ligne(sku="fr"),
        ]
        ecrire_csv(self.dossier, "a.csv", lignes)
        propre = clean_data(load_raw(self.dossier)).set_index("sku")

        self.assertEqual(propre.loc["eu", "country_code"], "ZONE_EU")
        self.assertEqual(propre.loc["na", "country_code"], "ZONE_NA")
        self.assertTrue(bool(propre.loc["na", "is_region"]))
        self.assertEqual(propre.loc["fr", "country_code"], "FR")
        self.assertFalse(bool(propre.loc["fr", "is_region"]))

    def test_code_pays_inconnu_accepte_comme_pays(self):
        ecrire_csv(self.dossier, "a.csv", [ligne(country_code="XX")])
        propre = clean_data(load_raw(self.dossier))
        self.assertEqual(propre.loc[0, "country_code"], "XX")
        self.assertFalse(bool(propre.loc[0, "is_region"]))

    # ------------------------------------------------------------------
    # Encodage et cas limites
    # ------------------------------------------------------------------
    def test_bom_utf8_et_accents(self):
        ecrire_csv(
            self.dossier,
            "a.csv",
            [ligne(product_name="eSIM Privilège", country_name="Åland")],
            encodage="utf-8-sig",
        )
        propre = clean_data(load_raw(self.dossier))
        self.assertEqual(propre.loc[0, "product_name"], "eSIM Privilège")
        self.assertEqual(propre.loc[0, "country_name"], "Åland")

    def test_fichier_entete_seul(self):
        ecrire_csv(self.dossier, "vide.csv", [])
        ecrire_csv(self.dossier, "a.csv", [ligne()])
        propre = clean_data(load_raw(self.dossier))
        self.assertEqual(len(propre), 1)


if __name__ == "__main__":
    unittest.main()
