<div align="center">

<img src="assets/logo_wordmark.png" alt="MyBestSim" width="220">

<h1>MyBestSim — dashboard eSIM</h1>

<p><strong>Consolide 18 catalogues fournisseurs, valide la donnée et compare 5 056 offres eSIM.</strong></p>

<p>
  <a href="https://mybestsim-dashboard.streamlit.app"><img src="https://img.shields.io/badge/D%C3%A9mo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Démo Streamlit"></a>
  <a href="https://github.com/Lamizana/MyBestSim"><img src="https://img.shields.io/badge/Code-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="Code source"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12"></a>
  <a href="https://github.com/Lamizana/MyBestSim/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Lamizana/MyBestSim/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI" alt="CI"></a>
  <a href="https://mybestsim.com"><img src="https://img.shields.io/badge/Contexte-Test%20de%20recrutement-8A2BE2?style=for-the-badge" alt="Test de recrutement"></a>
</p>

<p>Créé le 26/10/2026 · Dernière mise à jour : 27/10/2026</p>

</div>

---

## Sommaire

<details>
<summary>Afficher le sommaire</summary>

- [Sommaire](#sommaire)
- [À propos](#à-propos)
- [Stack technique](#stack-technique)
- [KPI](#kpi)
- [Comment ça marche](#comment-ça-marche)
- [Installation](#installation)
  - [Prérequis](#prérequis)
  - [Étapes](#étapes)
- [Bibliothèques](#bibliothèques)
- [Utilisation](#utilisation)
- [Écran](#écran)
- [Contrat de données](#contrat-de-données)
- [Décisions](#décisions)
- [Tests](#tests)
- [Limites connues](#limites-connues)
- [Publications](#publications)
- [Structure du projet](#structure-du-projet)
- [Documentation](#documentation)
- [Contribuer](#contribuer)
- [Auteur](#auteur)
- [Remerciements](#remerciements)

</details>

---

## À propos

Ce dashboard consolide les 18 fichiers CSV fournisseurs du catalogue eSIM MyBestSim, contrôle la qualité de la donnée et calcule les indicateurs de prix, de volume et de couverture. Il a été réalisé dans le cadre du test de recrutement MyBestSim (partie 1 : data & automatisation) et déployé sur Streamlit Community Cloud.

| Ressource | Lien |
| --- | --- |
| Application en ligne | [mybestsim-dashboard.streamlit.app](https://mybestsim-dashboard.streamlit.app) |
| Code source | [github.com/Lamizana/MyBestSim](https://github.com/Lamizana/MyBestSim) |
| Article (partie 2) | [Internet en croisière : quelle eSIM choisir ?](article/internet-croisiere-esim.md) |
| Sujet du test | [docs/enonce-test.pdf](docs/enonce-test.pdf) |

---

## Stack technique

| Catégorie | Technologie | Badge |
| --- | --- | --- |
| **Langage** | Python 3.12 | [![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) |
| **Interface** | Streamlit 1.66 | [![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) |
| **Données** | pandas 3.1 | [![pandas](https://img.shields.io/badge/pandas-3.1-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/) |
| **Graphiques** | Altair 6.3 | [![Altair](https://img.shields.io/badge/Altair-6.3-1F77B4?style=flat-square&logo=vega&logoColor=white)](https://altair-viz.github.io/) |
| **Qualité** | pytest, Ruff | [![Ruff](https://img.shields.io/badge/Ruff-0.6-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/) |
| **CI/CD** | GitHub Actions | [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions) |
| **Hébergement** | Streamlit Community Cloud | [![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/cloud) |

---

## KPI

Les six indicateurs demandés par le sujet, calculés sur les 5 056 offres :

| KPI | Valeur |
|---|---|
| Nombre total de cartes | 5 056 |
| Produits > 100 € | 56 |
| Fourchette de prix | 5,36 € – 154,63 € |
| Moyenne de data | 14,49 Go (4 403 offres finies) |
| Prix moyen | 29,30 € (médiane 20,70 €) |
| Répartition par fournisseur | 18 fournisseurs, Airalo 722 → 4S eSIM 92 |

S'y ajoutent deux séries : **1 113 combinaisons** destination × volume × durée (54 destinations, 7 volumes, 3 durées) pour les meilleures offres par destination, et `prix_go_volume`, la médiane du prix au Go par forfait avec ses quartiles. Toutes offres finies confondues, la médiane est de **2,55 €/Go** ; les 653 offres illimitées sont exclues et traitées à part (prix médian 51,28 €).

---

## Comment ça marche

L'application recalcule tout en mémoire, au démarrage, depuis `data/raw/` : `load_raw` → `clean_data` → `compute_metrics`. Aucun artefact intermédiaire, aucune étape de build.

```console
data/raw/*.csv
   │  load_raw      lecture, contrôle des en-têtes, dédoublonnage par SKU
   ▼
DataFrame brut (12 colonnes texte)
   │  clean_data    validation bloquante + colonnes dérivées
   ▼
DataFrame propre (14 colonnes typées)
   │  compute_metrics
   ▼
dict { meta, kpi, series }
   │
   └── app.py        affichage Streamlit
```

> [!NOTE]
> Le cache Streamlit est versionné par une empreinte de `etl.py` et `metrics.py` : toute modification du calcul force le recalcul, sans redémarrage manuel.

---

## Installation

### Prérequis

- Python 3.11 ou plus récent (3.12 recommandé)
- `make` pour les raccourcis
- `uv` uniquement pour régénérer `requirements.txt`

### Étapes

```bash
git clone https://github.com/Lamizana/MyBestSim.git
cd MyBestSim
make install
```

Ou manuellement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

> [!NOTE]
> Trois dépendances runtime directes : `altair`, `pandas` et `streamlit`. `requirements.txt` est épinglé pour Streamlit Cloud, `pyproject.toml` fait foi en local.

---

## Bibliothèques

| Bibliothèque | Rôle |
| --- | --- |
| [`pandas`](https://pandas.pydata.org/) | lecture, validation et agrégation des CSV |
| [`streamlit`](https://streamlit.io/) | interface web et cache de calcul |
| [`altair`](https://altair-viz.github.io/) | graphiques Vega-Lite |
| [`pytest`](https://docs.pytest.org/) | 53 tests |
| [`ruff`](https://docs.astral.sh/ruff/) | lint et style |
| [`uv`](https://docs.astral.sh/uv/) | génération des dépendances épinglées |

---

## Utilisation

| Commande | Effet |
| --- | --- |
| `make run` | lance l'application sur `localhost:8501` |
| `make test` | exécute les 53 tests |
| `make check` | valide `data/raw/` sans lancer Streamlit |
| `make lint` | vérifie le style avec Ruff |
| `make reqs` | régénère `requirements.txt` depuis `pyproject.toml` |
| `make reqs-check` | vérifie que le lock est synchrone |
| `make clean` | supprime les caches |

Ou directement, sans `make` :

```bash
python -m streamlit run app.py
```

Le point d'entrée de l'application est `app.py`.

> [!TIP]
> Avant `make run`, lancez `make check` : il détecte un fichier dupliqué, une valeur vide ou un conflit de SKU avec le fichier et la ligne fautive.

---

## Écran

1. **Chiffres clés** — six cartes, chacune avec une ligne de contexte.
2. **Répartition par fournisseur** — barres horizontales triées.
3. **Distribution des prix** — histogramme par tranche de 10 €, tranches à partir de 100 € en rouge.
4. **Prix au Go** — médiane par forfait et écart interquartile p25–p75, avec une carte de synthèse : 2,55 €/Go de médiane globale, de 6,71 € (1 Go) à 1,18 € (50 Go).
5. **Meilleures offres par destination** — sélection du volume et de la durée, podium des trois destinations les moins chères, onglets Pays / Régions, recherche, tableau triable.

---

## Contrat de données

Douze colonnes source, identiques dans les 18 fichiers : `sku`, `provider`, `product_name`, `country_code`, `country_name`, `data_gb`, `data_display`, `validity_days`, `price`, `currency`, `network`, `top_up`.

Deux colonnes dérivées :

| Colonne | Type | Définition |
| --- | --- | --- |
| `is_unlimited` | bool | vrai si `data_display` vaut « Illimité » (653 lignes) |
| `is_region` | bool | vrai si l'offre couvre une zone multi-pays (778 lignes) |

Règles de validation, toutes bloquantes (aucune correction silencieuse) :

| Règle | Vérifié par |
| --- | --- |
| aucune colonne obligatoire vide (`data_gb` excepté si illimité) | `clean_data` |
| `sku` unique : doublons exacts dédupliqués, conflits refusés | `load_raw` puis `clean_data` |
| fichier identique à un autre | `load_raw` (ignoré, avertissement) |
| `currency` = `EUR` | `clean_data` |
| `network` ∈ {`4G`, `5G`} | `clean_data` |
| `top_up` ∈ {`oui`, `non`} | `clean_data` |
| `price` numérique et strictement positif | `clean_data` |
| `validity_days` entier strictement positif | `clean_data` |
| `data_gb` vide **si et seulement si** `is_unlimited` | `clean_data` |
| en-têtes égaux aux 12 colonnes attendues | `load_raw` |

Chaque échec indique les SKU ou le fichier fautif, et le programme s'arrête avec un code de sortie non nul.

---

## Décisions

- **Illimité ≠ 0 Go.** La moyenne de data porte sur les 4 403 offres à volume fini ; les 653 offres illimitées sont exclues et signalées à part.
- **Seuil de 100 €** appliqué strictement (`price > 100`).
- **Pays vs régions.** 50 pays et 4 zones (Europe, Asie, Amérique du Nord, Monde). Les zones ont leur propre onglet et ne sont jamais mélangées aux pays.
- **Codes de zone préfixés** (`ZONE_EU`, `ZONE_AS`, `ZONE_NA`, `ZONE_WW`) : `NA` serait interprété comme une valeur manquante par pandas à la relecture.
- **Devise unique.** Tout est en euros ; une autre devise fait échouer le pipeline.

---

## Tests

```bash
make test
```

53 tests couvrent les invariants des données réelles (5 056 lignes, 653 illimitées, 778 zones, moyenne de 14,49 Go), les six KPI, le prix au Go (médiane, quartiles, offres illimitées), la série des meilleures offres (1 113 combinaisons, minimum et départage), la structure des graphiques, le rendu de l'application, la clé de cache et le rejet des cas invalides.

La CI (`.github/workflows/ci.yml`) exécute `make reqs-check`, `ruff` et `pytest` sur Python 3.12 à chaque push vers `main` et à chaque pull request.

---

## Limites connues

- Jeu de données synthétique fourni pour le test : les relations observées décrivent ce catalogue, pas le marché réel.
- **Pas de fusion des variantes commerciales** : les 731 doublons apparents `(provider, product_name)` sont de vraies variantes de prix, de réseau ou de recharge. Seuls les doublons exacts de SKU sont dédupliqués à l'ingestion.
- Aucune suppression de valeur extrême : le produit à 154,63 € est réel.
- **Prix au Go et offres illimitées** : sans volume en Go, elles n'ont pas de prix au Go ; elles sont exclues des séries et traitées à part (653 offres, prix médian 51,28 €).
- **Histogramme borné à 160 €** : le prix maximal observé est 154,63 €, donc aucune offre n'est écartée aujourd'hui.

---

## Publications

- [Internet en croisière : quelle eSIM choisir ?](article/internet-croisiere-esim.md) — choisir une eSIM utile en mer et à quai, selon l'itinéraire.

---

## Structure du projet

```console
MyBestSim/
├── .github/workflows/     # CI (reqs-check, ruff, pytest)
├── .streamlit/            # thème MyBestSim
├── app.py                 # application Streamlit (affichage seul)
├── article/               # article SEO (partie 2)
├── assets/                # logo et wordmark
├── data/raw/              # 18 CSV fournisseurs, jamais modifiés
├── mybestsim/
│   ├── config.py          # chemins, contrat de données, constantes
│   ├── etl.py             # lecture, validation, typage, dédoublonnage
│   ├── metrics.py         # KPI et séries
│   ├── graphiques.py      # spécifications Altair
│   └── check.py           # validation sans Streamlit
├── tests/                 # 53 tests
├── docs/                  # FONCTIONS.md, sujet, archives
├── Makefile               # install / reqs / reqs-check / run / test / check / lint / clean
├── pyproject.toml         # dépendances, Ruff, pytest
├── requirements.txt       # lock généré par make reqs
└── README.md
```

---

## Documentation

| Fichier | Descriptif |
| --- | --- |
| [`docs/FONCTIONS.md`](docs/FONCTIONS.md) | rôles et signatures des fonctions |
| [`docs/enonce-test.pdf`](docs/enonce-test.pdf) | sujet du test de recrutement |
| [`docs/archive/`](docs/archive/) | plans de travail successifs |

---

## Contribuer

Projet personnel réalisé dans le cadre d'un test de recrutement : les corrections et les remarques sont bienvenues via une **issue** ou une **pull request**.

Les messages de commit suivent [Conventional Commits](https://www.conventionalcommits.org/fr/) :

```text
<type>(<scope>): <description>
```

| Type | Usage |
| --- | --- |
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation seule |
| `refactor` | Réécriture sans changement de comportement |
| `chore` | Maintenance (configuration, fichiers annexes) |

**Scopes** : `etl`, `metrics`, `ui`, `article`, `ci`, `readme`.

---

## Auteur

**Alex Lamizana**, étudiant à 42 Angoulême, spécialisation Data & IA

- [Site](https://lamizana.github.io/ZehdBox/)
- [GitHub](https://github.com/Lamizana)
- [Contact](https://lamizana.github.io/ZehdBox/contact/)

---

## Remerciements

- **MyBestSim** (Etienne Tillier) : sujet du test et jeu de données fournisseur.
- **42 Angoulême** : formation et cadre méthodologique.
