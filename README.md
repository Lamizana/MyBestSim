<div align="center">

<p>
  <a href="https://mybestsim-dashboard.streamlit.app"><img src="https://img.shields.io/badge/D%C3%A9mo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Démo Streamlit"></a>
  <a href="https://github.com/Lamizana/MyBestSim"><img src="https://img.shields.io/badge/Code-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="Code source"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12"></a>
  <a href="https://github.com/Lamizana/MyBestSim/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Lamizana/MyBestSim/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI" alt="CI"></a>
  <a href="https://mybestsim.com"><img src="https://img.shields.io/badge/Contexte-Test%20de%20recrutement-8A2BE2?style=for-the-badge" alt="Test de recrutement"></a>
</p>

<img src="assets/logo.png" alt="MyBestSim" width="220">

<h1>MyBestSim</h1>
<p><strong>Dashboard eSIM</strong></p>
<p><em>Consolide 18 catalogues fournisseurs, valide la donnée et compare 5 056 offres eSIM.</em></p>

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
- [Fonctionnalités \& Écrans du Dashboard](#fonctionnalités--écrans-du-dashboard)
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

Ce dashboard consolide les **18 fichiers CSV** fournisseurs du catalogue eSIM **MyBestSim**, contrôle la qualité de la donnée et calcule les indicateurs de prix, de volume et de couverture. Il a été réalisé dans le cadre du test de recrutement MyBestSim  et déployé sur Streamlit Community Cloud.

<div align="center">
  
| Ressource | Lien |
| --- | --- |
| Application en ligne | [mybestsim-dashboard.streamlit.app](https://mybestsim-dashboard.streamlit.app) |
| Article en ligne  | [Internet en croisière : quelle eSIM choisir ?](https://lamizana.github.io/MyBestSim/) |
| Source de l'article | [article/internet-croisiere-esim.md](article/internet-croisiere-esim.md) |
| Sujet du test | [docs/enonce-test.pdf](docs/enonce-test.pdf) |

</div>

---

## Stack technique

<div align="center">
  
| Catégorie | Technologie | Badge |
| --- | --- | --- |
| **Langage** | Python 3.12 | [![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) |
| **Interface** | Streamlit 1.66 | [![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) |
| **Données** | pandas 3.1 | [![pandas](https://img.shields.io/badge/pandas-3.1-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/) |
| **Graphiques** | Altair 6.3 | [![Altair](https://img.shields.io/badge/Altair-6.3-1F77B4?style=flat-square&logo=vega&logoColor=white)](https://altair-viz.github.io/) |
| **Qualité** | pytest, Ruff | [![Ruff](https://img.shields.io/badge/Ruff-0.6-D7FF64?style=flat-square&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/) |
| **CI/CD** | GitHub Actions | [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions) |
| **Hébergement** | Streamlit Community Cloud | [![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/cloud) |
| **Article** | GitHub Pages | [![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-en%20ligne-222222?style=flat-square&logo=githubpages&logoColor=white)](https://lamizana.github.io/MyBestSim/) |

</div>

---

## KPI

Les six indicateurs demandés par le sujet, calculés sur les 5 056 offres :

<div align="center">
  
| KPI | Valeur |
|---|---|
| Nombre total de cartes | 5 056 |
| Produits > 100 € | 56 |
| Fourchette de prix | 5,36 € – 154,63 € |
| Moyenne de data | 14,49 Go (4 403 offres finies) |
| Prix moyen | 29,30 € (médiane 20,70 €) |
| Répartition par fournisseur | 18 fournisseurs, Airalo 722 → 4S eSIM 92 |

</div>

S'y ajoutent deux séries :
- **1 113 combinaisons** destination × volume × durée (54 destinations, 7 volumes, 3 durées) pour les meilleures offres par destination.
- **Prix du Go par volume de donées** : la médiane du prix au Go par forfait avec ses quartiles.
  - Toutes offres finies confondues, la médiane est de **2,55 €/Go**.
  - les 653 offres illimitées sont exclues et traitées à part (prix médian 51,28 €).

---

## Comment ça marche

L'application recalcule tout en mémoire, au démarrage, depuis :
- **`data/raw/`** : `load_raw` → `clean_data` → `compute_metrics`.

> Aucun artefact intermédiaire, aucune étape de build.

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

- **Python 3.11** ou plus récent (3.12 recommandé)
- `make` pour les raccourcis
- `uv` pour construire la page de l'article

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
| [`pytest`](https://docs.pytest.org/) | 88 tests |
| [`ruff`](https://docs.astral.sh/ruff/) | lint et style |
| [`uv`](https://docs.astral.sh/uv/) | construction de la page article |

---

## Utilisation

| Commande | Effet |
| --- | --- |
| `make run` | lance l'application sur `localhost:8501` |
| `make test` | exécute les 88 tests |
| `make check` | valide `data/raw/` sans lancer Streamlit |
| `make lint` | vérifie le style avec Ruff |
| `make article` | construit la page HTML de l'article dans `article/_site/` |
| `make clean` | supprime les caches |

Ou directement, sans `make` :

```bash
python -m streamlit run app.py
```

Le point d'entrée de l'application est `app.py`.

> [!TIP]
> Avant `make run`, lancez `make check` : il détecte un fichier dupliqué, une valeur vide ou un conflit de SKU avec le fichier et la ligne fautive.

---

## Fonctionnalités & Écrans du Dashboard

| Section | Description | Rendu & Indicateurs visuels |
| :--- | :--- | :--- |
| **1. Chiffres clés** | Métriques globales du catalogue | 6 cartes `st.metric` avec infobulle de définition (`help`) |
| **2. Répartition par fournisseur** | Volume d'offres par opérateur | Graphique en barres horizontales trié par ordre décroissant |
| **3. Distribution des prix** | Dispersion des tarifs | Histogramme par tranche de 10 € *(tranches ≥ 100 € en rouge)* |
| **4. Prix au Go** | Coût au Gigaoctet selon le volume | Médiane et écart interquartile (p25–p75) + carte de synthèse (2,55 €/Go de médiane) |
| **5. Meilleures offres** | Comparatif détaillé par destination | Filtres par volume/durée, podium du Top 3, onglets Pays/Régions et tableau triable |
| **6. Export CSV** | Téléchargement du catalogue nettoyé | Bouton `st.download_button`, 5 056 lignes × 14 colonnes, UTF-8 avec BOM |

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

> [!NOTE]
> Chaque échec indique les SKU ou le fichier fautif, et le programme s'arrête avec un code de sortie non nul.

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

88 tests couvrent les invariants des données réelles (5 056 lignes, 653 illimitées, 778 zones, moyenne de 14,49 Go), les six KPI, le prix au Go, la série des meilleures offres, la structure des graphiques, le rendu de l'application, la clé de cache, l'export CSV et le rejet des cas invalides.

Une suite dédiée (`tests/test_etl_cas.py`) éprouve l'ETL sur des CSV générés : schéma, doublons, conflits, devises, réseaux, prix, durées, illimité, zones, BOM et lignes mal formées.

La CI (`.github/workflows/ci.yml`) exécute `ruff` et `pytest` sur Python 3.12 à chaque push vers `main` et à chaque pull request.

---

## Limites connues

- Jeu de données synthétique fourni pour le test : les relations observées décrivent ce catalogue, pas le marché réel.
- **Pas de fusion des variantes commerciales** : les 731 doublons apparents `(provider, product_name)` sont de vraies variantes de prix, de réseau ou de recharge. Seuls les doublons exacts de SKU sont dédupliqués à l'ingestion.
- Aucune suppression de valeur extrême : le produit à 154,63 € est réel.
- **Prix au Go et offres illimitées** : sans volume en Go, elles n'ont pas de prix au Go ; elles sont exclues des séries et traitées à part (653 offres, prix médian 51,28 €).
- **Histogramme borné à 160 €** : le prix maximal observé est 154,63 €, donc aucune offre n'est écartée aujourd'hui.

---

## Publications

- **En ligne** : [Internet en croisière : quelle eSIM choisir ?](https://lamizana.github.io/MyBestSim/) : page HTML brandée, déployée par GitHub Pages, avec métadonnées SEO et données structurées.
- **Source** :  [article/internet-croisiere-esim.md](article/internet-croisiere-esim.md) : Markdown de référence, la page est générée par `make article`.

---

## Structure du projet

```console
MyBestSim/
├── .github/workflows/     # CI (ruff, pytest)
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
├── tests/                 # 88 tests
├── docs/                  # FONCTIONS.md, SEO-ARTICLE.md, sujet
├── Makefile               # install / run / test / lint / check / article / clean
├── pyproject.toml         # dépendances, Ruff, pytest
├── requirements.txt       # dépendances épinglées pour Streamlit Cloud
└── README.md
```

---

## Documentation

| Fichier | Descriptif |
| --- | --- |
| [`docs/FONCTIONS.md`](docs/FONCTIONS.md) | rôles et signatures des fonctions |
| [`docs/SEO-ARTICLE.md`](docs/SEO-ARTICLE.md) | stratégie SEO de l'article et maintenance |
| [`docs/enonce-test.pdf`](docs/enonce-test.pdf) | sujet du test de recrutement |

---

## Utilisation de l'IA

Ce projet a été réalisé avec l'assistance d'un agent IA dans une démarche à la fois pragmatique et pédagogique.

- **Revue et audit** : Relecture complète du code, identification de points d'amélioration (cache Streamlit, synchronisation UI, robustesse ETL) et proposition de correctifs ciblés.
- **Débogage** : Aide au diagnostic de cas concrets (invalidation du cache, désynchronisation podium/tableau) avec validation systématique.
- **Qualité et tests** : Renforcement de la rigueur (protection contre valeurs invalides, histogramme dynamique) tout en gardant tous les tests existants au vert.
- **Documentation** : Clarification et mise à jour du README, de `docs/FONCTIONS.md` et des explications dans l'interface.

**Démarche** : chaque suggestion a été comprise, analysée et testée manuellement avant intégration. Les modifications ont été validées avec `ruff` et `pytest` (88 tests). L'IA a servi d'accélérateur et de sparring partner technique, sans se substituer à la réflexion : l'architecture, les choix et la validation finale restent sous mon contrôle.

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

- **MyBestSim** : sujet du test et jeu de données fournisseur.
- **42 Angoulême** : formation et cadre méthodologique.
