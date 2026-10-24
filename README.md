# MyBestSim — dashboard eSIM

Consolide les 18 CSV fournisseurs en une table unique, la nettoie et calcule les
KPI du catalogue eSIM.

Projet réalisé dans le cadre du test de recrutement MyBestSim (partie 1 :
data & automatisation).

## Arborescence

```text
.
├── pyproject.toml          # dépendances, ruff, pytest
├── Makefile                # install / data / test / lint / clean
├── main.py                 # raccourci vers python -m mybestsim
├── mybestsim/
│   ├── config.py           # chemins et constantes du contrat
│   ├── ingest.py           # lecture des CSV
│   ├── clean.py            # typage, validation, colonnes dérivées
│   ├── metrics.py          # KPI
│   ├── export.py           # écriture CSV
│   └── __main__.py         # orchestration
├── data/
│   ├── raw/                # les 18 CSV fournisseurs, jamais modifiés
│   └── processed/          # sorties régénérées (ignorées par git)
├── tests/                  # ingestion, nettoyage, KPI
├── docs/                   # fonctions, plan, énoncé du test
├── site/                   # page générée (ignorée par git)
└── .github/workflows/ci.yml
```

## Prérequis

Python ≥ 3.11. Une seule dépendance d'exécution : pandas.

## Installation

```bash
make install
```

ou manuellement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Commandes

| Commande | Équivalent | Effet |
|---|---|---|
| `make install` | `python3 -m venv .venv` puis `pip install -e ".[dev]"` | crée l'environnement et installe le paquet |
| `make data` | `python -m mybestsim` | lit `data/raw/`, écrit `data/processed/`, affiche les KPI |
| `make test` | `python -m pytest` | exécute les 23 tests |
| `make lint` | `ruff check .` | vérifie le style et les erreurs |
| `make clean` | `rm -rf data/processed site …` | supprime les sorties générées |

`python main.py` fonctionne aussi : c'est un raccourci de quatre lignes vers
`python -m mybestsim`.

## Pipeline

| Étape | Module | Rôle |
|---|---|---|
| 1 | `mybestsim.ingest.load_data` | lit les 18 CSV, contrôle les en-têtes, empile |
| 2 | `mybestsim.clean.clean_data` | type les colonnes, valide le contrat, ajoute les colonnes dérivées |
| 3 | `mybestsim.export.write_csv` | écrit les sorties |

## Fichiers produits

| Fichier | Contenu |
|---|---|
| `data/processed/all_products.csv` | fusion brute : 5 056 lignes, 12 colonnes, valeurs texte inchangées |
| `data/processed/clean_products.csv` | fusion typée : 5 056 lignes, 15 colonnes |

`data/raw/` est la matière première et n'est jamais modifiée : toute règle de
nettoyage peut être rejouée sans retélécharger les fichiers.

## Contrat de données

Douze colonnes source, identiques dans les 18 fichiers :
`sku`, `provider`, `product_name`, `country_code`, `country_name`, `data_gb`,
`data_display`, `validity_days`, `price`, `currency`, `network`, `top_up`.

Trois colonnes dérivées :

| Colonne | Type | Définition |
|---|---|---|
| `is_unlimited` | bool | vrai si `data_display` vaut « Illimité » (653 lignes) |
| `is_region` | bool | vrai si l'offre couvre une zone multi-pays (778 lignes) |
| `price_per_gb` | float | `price / data_gb`, vide si illimité |

Règles de validation, toutes bloquantes (aucune correction silencieuse) :

| Règle | Vérifié par |
|---|---|
| `sku` unique | `clean_data` |
| `currency` = `EUR` | `clean_data` |
| `network` ∈ {`4G`, `5G`} | `clean_data` |
| `top_up` ∈ {`oui`, `non`} | `clean_data` |
| `price` numérique et strictement positif | `clean_data` |
| `validity_days` entier strictement positif | `clean_data` |
| `data_gb` vide **si et seulement si** `is_unlimited` | `clean_data` |
| en-têtes égaux aux 12 colonnes attendues (`EXPECTED_COLUMNS`) | `load_data` |

Chaque échec indique les SKU ou le fichier fautif, et le programme s'arrête avec
un code de sortie non nul.

## Décision : codes de zone préfixés

Les 18 CSV utilisent quatre pseudo-codes pour les offres régionales : `EU`
(Europe), `AS` (Asie), `NA` (Amérique du Nord), `WW` (Monde). Trois d'entre eux
sont aussi des codes ISO 3166-1 valides (UE, Samoa américaines, Namibie), et
surtout **`NA` est une valeur manquante reconnue par pandas**.

Concrètement, relire le fichier propre avec `pd.read_csv(...)` par défaut
transformait les 192 lignes « Amérique du Nord » en `NaN`, et elles
disparaissaient de tout `groupby` sans aucune erreur.

Dans `clean_products.csv`, ces quatre codes sont donc préfixés :

| Source | Table nettoyée |
|---|---|
| `EU` | `ZONE_EU` |
| `AS` | `ZONE_AS` |
| `NA` | `ZONE_NA` |
| `WW` | `ZONE_WW` |

Les 50 codes pays restent inchangés. `all_products.csv` conserve les codes
d'origine, pour la traçabilité avec les fichiers fournisseurs.

## Règles de lecture

Pour consommer les fichiers sans perdre de données :

```python
pd.read_csv(path, dtype=str, keep_default_na=False)          # tout en texte
pd.read_csv(path, dtype={"country_code": str}, keep_default_na=False)
```

Ces options évitent les conversions implicites de pandas (`NA` → `NaN`,
`data_gb` vide → `NaN`, prix en flottant).

## Tests

```bash
make test          # ou : python -m pytest
```

23 tests couvrent les invariants des données réelles (5 056 lignes, 653
illimitées, 778 zones, moyenne de 14,49 Go, durées entières), les six KPI et le
rejet des cas invalides (SKU dupliqué, prix non positif, illimité incohérent,
durée illisible ou non positive, colonnes différentes, dossier vide).

La CI (`.github/workflows/ci.yml`) exécute `ruff` et `pytest` à chaque push.

## Documentation

- [`docs/FONCTIONS.md`](docs/FONCTIONS.md) — détail de chaque fonction :
  signature, rôle, exemple, valeur attendue et pièges.
- [`docs/PLAN.md`](docs/PLAN.md) — plan d'exécution du test et décisions.
- [`docs/enonce-test.pdf`](docs/enonce-test.pdf) — énoncé du test.

## Limites connues

- Aucune déduplication : les 620 doublons apparents `(provider, product_name)`
  sont de vraies variantes de prix, de réseau ou de recharge.
- Aucune suppression de valeur extrême : le produit à 154,63 € est réel.
- La moyenne de Go porte sur les 4 403 offres à data finie (14,49 Go) ; les
  653 offres illimitées sont un indicateur distinct et ne valent pas 0 Go.
