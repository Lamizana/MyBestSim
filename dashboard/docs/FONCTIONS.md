# Fonctions du pipeline

Documentation des fonctions présentes dans `dashboard/`. Les valeurs indiquées
sont celles obtenues sur les 18 fichiers fournisseurs (5 056 offres).

Répartition : `mybestsim/config.py` (constantes), `mybestsim/ingest.py`
(lecture), `mybestsim/clean.py` (nettoyage), `mybestsim/export.py` (écriture),
`mybestsim/metrics.py` (KPI), `mybestsim/__main__.py` (orchestration).

Voir aussi le [`README.md`](../README.md) pour l'installation, l'exécution et
le contrat de données.

## Vue d'ensemble

```text
18 CSV ──load_data()──> brut (5 056 × 12) ──clean_data()──> propre (5 056 × 15) ──metrics.*──> KPI
```

Règle commune : les fonctions de `metrics.py` ne lisent aucun fichier et
n'écrivent rien. Elles reçoivent la table nettoyée et renvoient une valeur.
C'est ce qui permet de les tester une par une, et de vérifier un chiffre isolé
quand un total paraît faux.

## Récapitulatif

| Module | Fonction | Retour | Valeur attendue |
|---|---|---|---|
| `mybestsim/export.py` | `write_csv(df, path)` | — | écrit le CSV en UTF-8 |
| `mybestsim/ingest.py` | `load_data(data_dir)` | `DataFrame` | 5 056 × 12 |
| `mybestsim/clean.py` | `clean_data(raw)` | `DataFrame` | 5 056 × 15 |
| `mybestsim/__main__.py` | `main()` | `int` | 0 (succès) / 1 (échec) |
| `mybestsim/metrics.py` | `total_cards(df)` | `int` | 5 056 |
| `mybestsim/metrics.py` | `cards_above_price(df, seuil=100.0)` | `int` | 56 |
| `mybestsim/metrics.py` | `price_range(df)` | `dict` | 5,36 – 154,63 |
| `mybestsim/metrics.py` | `mean_data_gb(df)` | `dict` | 14,49 sur 4 403 offres |
| `mybestsim/metrics.py` | `mean_price(df)` | `dict` | 29,30 moyen / 20,70 médian |
| `mybestsim/metrics.py` | `provider_distribution(df)` | `list` | 18 fournisseurs, somme 5 056 |

## `mybestsim/config.py`

Chemins et constantes du contrat, sans aucune logique :

| Constante | Contenu |
|---|---|
| `DASHBOARD` | dossier `dashboard/`, calculé depuis `__file__` |
| `DATA_DIR` | les 18 CSV fournisseurs |
| `RAW_OUTPUT` | `data/all_products.csv` |
| `CLEAN_OUTPUT` | `data/clean_products.csv` |
| `EXPECTED_COLUMNS` | les 12 colonnes attendues, dans l'ordre |
| `REGION_CODES` | `{EU, AS, NA, WW}` |
| `ZONE_PREFIX` | `"ZONE_"` |

Aucun module n'importe `main` : la dépendance va toujours de `main` vers
`pipeline`, `metrics` et `config`.

## `mybestsim/export.py`

### `write_csv(df: pd.DataFrame, path: Path) -> None`

Écrit un DataFrame en CSV : UTF-8, en-tête inclus, sans colonne d'index.

```python
write_csv(clean, CLEAN_OUTPUT)
```

- Crée le dossier parent si nécessaire (`mkdir(parents=True, exist_ok=True)`).
- `index=False` est indispensable : sans lui, pandas ajoute une colonne d'index
  sans nom et le fichier passe de 15 à 16 colonnes.

## `mybestsim/ingest.py`

### `load_data(data_dir: Path) -> pd.DataFrame`

Lit les 18 CSV du dossier, contrôle les en-têtes, empile les tables.

```python
raw = load_data(DATA_DIR)  # (5056, 12)
```

- Fichiers triés par nom : l'ordre de sortie est reproductible.
- Lecture en texte brut (`dtype=str`, `keep_default_na=False`) : `NA`
  (Amérique du Nord) reste `"NA"` et `data_gb` vide reste `""`. Sans ces
  options, pandas transforme le code `NA` en `NaN` et perd 192 lignes.
- `encoding="utf-8-sig"` tolère un éventuel BOM.
- Contrôle : chaque en-tête doit être **égal** à `EXPECTED_COLUMNS`, pas
  seulement identique aux autres fichiers.
- Erreurs : `ValueError` si le dossier est vide ou si un fichier a un autre
  schéma ; `OSError` si un fichier est inaccessible.

## `mybestsim/clean.py`

### `clean_data(raw: pd.DataFrame) -> pd.DataFrame`

Type les colonnes, valide le contrat, ajoute les colonnes dérivées. Ne modifie
pas `raw` (travail sur une copie).

```python
clean = clean_data(raw)  # (5056, 15)
```

Ordre des opérations :

1. `sku` unique ;
2. `currency` = `EUR` ;
3. `network` ∈ {`4G`, `5G`} ;
4. `validity_days` converti en entier strictement positif ;
5. `price` numérique et strictement positif ;
6. `top_up` ∈ {`oui`, `non`}, converti en booléen ;
7. `is_unlimited` = `data_display == "Illimité"` ;
8. cohérence : `data_gb` vide **si et seulement si** `is_unlimited` ;
9. `is_region` = code dans {`EU`, `AS`, `NA`, `WW`} ;
10. préfixage des codes de zone en `ZONE_EU`, `ZONE_AS`, `ZONE_NA`, `ZONE_WW` ;
11. `price_per_gb` = `price / data_gb` (vide si illimité).

Toute violation lève un `ValueError` citant les SKU ou les valeurs fautives.
Aucune correction silencieuse.

## `mybestsim/__main__.py`

### `main() -> int`

Orchestration : `load_data` → `clean_data` → écriture des deux CSV. Affiche le
nombre de lignes et les chemins écrits.

- `0` en cas de succès, `1` en cas d'échec.
- Les écritures n'ont lieu qu'après un nettoyage réussi : pas de fichier à
  moitié produit.
- `UnicodeDecodeError` est intercepté **avant** `ValueError` (il en hérite),
  puis `OSError`, puis `ValueError`, pour un message adapté à chaque cause.

## `mybestsim/metrics.py`

### `total_cards(df) -> int`

Nombre total d'offres. Une ligne = un produit eSIM.

```python
total_cards(clean)  # 5056
```

Sert de référence à tous les autres KPI : si ce nombre est faux, tout le reste
l'est.

### `cards_above_price(df, seuil=100.0) -> int`

Nombre d'offres dont le prix dépasse **strictement** `seuil`.

```python
cards_above_price(clean)  # 56
cards_above_price(clean, 50.0)  # même fonction avec un autre seuil
```

- `>` et non `>=` : aucun prix ne vaut exactement 100 € aujourd'hui, mais la
  règle est écrite plutôt que dépendante des données.
- `int(...)` autour de `sum()` : `sum()` renvoie un entier numpy, que
  `json.dump` ne sait pas sérialiser.
- Ne jamais arrondir les prix avant la comparaison : `100,49` arrondi à l'euro
  deviendrait `100` et sortirait des 56.

### `price_range(df) -> dict`

Bornes réelles des prix du catalogue.

```python
price_range(clean)  # {'min': 5.36, 'max': 154.63}
```

- Minimum et maximum réels, pas des percentiles : le KPI demandé est l'étendue.
- `float(...)` : même raison que `int(...)`, les types numpy ne passent pas en
  JSON.

### `mean_data_gb(df) -> dict`

Moyenne des `data_gb` sur les offres à volume fini, avec le dénominateur.

```python
mean_data_gb(clean)  # {'valeur': 14.49, 'nb_offres': 4403}
```

- `~df["is_unlimited"]` sélectionne les offres finies ; les 653 illimitées sont
  exclues, jamais comptées comme 0 Go (`fillna(0).mean()` donnerait 12,62 Go,
  chiffre faux).
- `float(...)` et `round(..., 2)` pour un JSON lisible ; l'arrondi n'existe
  qu'à la sortie.
- `count()` compte les valeurs non manquantes : c'est le dénominateur réel de
  la moyenne.

### `mean_price(df) -> dict`

Prix moyen et médian du catalogue, en euros.

```python
mean_price(clean)  # {'moyenne': 29.3, 'mediane': 20.7}
```

- Aucune exclusion : les 5 056 offres ont un prix valide, contrairement à la
  moyenne de Go qui porte sur 4 403 offres.
- Les deux indicateurs sont affichés ensemble : les prix vont de 5,36 à
  154,63 €, donc la moyenne est tirée vers le haut et la médiane (20,70 €)
  décrit mieux l'offre « du milieu ».

### `provider_distribution(df) -> list`

Nombre d'offres par fournisseur, trié décroissant, avec la part en pourcentage.

```python
provider_distribution(clean)[0]
# {'provider': 'Airalo', 'cartes': 722, 'part_pct': 14.3}
provider_distribution(clean)[-1]
# {'provider': '4S eSIM', 'cartes': 92, 'part_pct': 1.8}
```

- `groupby("provider").size()` compte par fournisseur, trié par nom ;
  `sort_values(ascending=False, kind="stable")` classe par nombre décroissant
  en conservant l'ordre alphabétique pour les ex æquo. Le résultat est donc
  reproductible, contrairement à l'ordre interne de `value_counts`.
- `part_pct` est calculé ici, une fois, pour que le gabarit ou le graphique
  n'ait pas à refaire la division.
- Le retour est une liste de dictionnaires, donc directement sérialisable en
  JSON : `metrics.py` ne dépend d'aucune bibliothèque de visualisation.
- Invariant de réconciliation : la somme des `cartes` doit valoir 5 056 et la
  somme des `part_pct` 100 % (à l'arrondi près).

## Conventions

| Sujet | Choix |
|---|---|
| Noms de fonctions et de modules | anglais (`load_data`, `clean_data`, `mean_data_gb`) |
| Variables locales et docstrings | français (`fichiers`, `colonnes`, `valeurs`) |
| Types de retour | Python natifs (`int`, `float`, `dict`) pour rester sérialisables |
| Arrondi | à la sortie seulement, jamais avant un seuil ou une comparaison |
| Illimité | booléen `is_unlimited` + `data_gb` manquant, jamais `0` |
| Déterminisme | pas d'horodatage, fichiers triés, sorties comparables par `md5sum` |
| Style de retour | calcul directement dans le `return` ; variable intermédiaire seulement si la valeur sert deux fois |

## À venir

Fonction prévue, non encore écrite :

- `compute_metrics(df)` — assemble les KPI dans le dictionnaire écrit en
  `data/metrics.json`.

## Tests

```bash
cd dashboard
make test        # ou : python -m pytest
```

23 tests, répartis en trois fichiers :

- `tests/test_ingest.py` — lecture des 18 fichiers, refus d'un dossier vide ou
  d'un en-tête différent ;
- `tests/test_clean.py` — invariants du nettoyage et cas de rejet ;
- `tests/test_metrics.py` — les six KPI et les invariants de la répartition
  (somme des cartes = 5 056, parts ≈ 100 %, tri décroissant).
