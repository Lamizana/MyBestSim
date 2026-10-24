# Fonctions du pipeline

Documentation des fonctions présentes dans `mybestsim/`. Les valeurs indiquées
sont celles obtenues sur les 18 fichiers fournisseurs (5 056 offres).

Répartition : `config.py` (constantes), `etl.py` (lecture, nettoyage, écriture),
`merge.py` (production des tables), `report.py` (KPI), `metrics.py` (calculs),
`__main__.py` (enchaînement).

Voir aussi le [`README.md`](../README.md) pour l'installation, l'exécution et
le contrat de données.

## Vue d'ensemble

```text
merge    : 18 CSV ──load_raw()──> brut (5 056 × 12) ──clean_data()──> propre (5 056 × 15)
                                                                          │ write_csv()
                                                                          ▼
report   :                        data/processed/clean_products.csv ──load_clean()──> metrics.* ──> KPI
```

Règle commune : les fonctions de `metrics.py` ne lisent aucun fichier et
n'écrivent rien. Elles reçoivent la table nettoyée et renvoient une valeur.
C'est ce qui permet de les tester une par une, et de vérifier un chiffre isolé
quand un total paraît faux.

## Récapitulatif

| Module | Fonction | Retour | Valeur attendue |
|---|---|---|---|
| `etl.py` | `load_raw(data_dir)` | `DataFrame` | 5 056 × 12 |
| `etl.py` | `load_clean(path)` | `DataFrame` | 5 056 × 15 |
| `etl.py` | `clean_data(raw)` | `DataFrame` | 5 056 × 15 |
| `etl.py` | `write_csv(df, path)` | — | écrit le CSV en UTF-8 |
| `merge.py` | `run()` | `DataFrame` | écrit les deux tables |
| `merge.py` | `main()` | `int` | 0 (succès) / 1 (échec) |
| `report.py` | `run(clean)` | — | affiche les KPI |
| `report.py` | `main()` | `int` | 0 (succès) / 1 (échec) |
| `__main__.py` | `main()` | `int` | enchaîne merge puis report |
| `metrics.py` | `total_cards(df)` | `int` | 5 056 |
| `metrics.py` | `cards_above_price(df, seuil=100.0)` | `int` | 56 |
| `metrics.py` | `price_range(df)` | `dict` | 5,36 – 154,63 |
| `metrics.py` | `mean_data_gb(df)` | `dict` | 14,49 sur 4 403 offres |
| `metrics.py` | `mean_price(df)` | `dict` | 29,30 moyen / 20,70 médian |
| `metrics.py` | `provider_distribution(df)` | `list` | 18 fournisseurs, somme 5 056 |

## `mybestsim/config.py`

Chemins et constantes du contrat, sans aucune logique :

| Constante | Contenu |
|---|---|
| `PROJECT_ROOT` | racine du dépôt, calculée depuis `__file__` |
| `DATA_DIR` | `data/raw/`, les 18 CSV fournisseurs |
| `PROCESSED_DIR` | `data/processed/` |
| `RAW_OUTPUT` | `data/processed/all_products.csv` |
| `CLEAN_OUTPUT` | `data/processed/clean_products.csv` |
| `EXPECTED_COLUMNS` | les 12 colonnes attendues, dans l'ordre |
| `REGION_CODES` | `{EU, AS, NA, WW}` |
| `ZONE_PREFIX` | `"ZONE_"` |

## `mybestsim/etl.py`

### `load_raw(data_dir: Path) -> pd.DataFrame`

Lit les 18 CSV du dossier, contrôle les en-têtes, empile les tables.

```python
raw = load_raw(DATA_DIR)  # (5056, 12)
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

### `load_clean(path: Path) -> pd.DataFrame`

Relit la table nettoyée produite par `merge`, en restituant les types.

```python
clean = load_clean(CLEAN_OUTPUT)  # (5056, 15)
```

- Lecture en texte (`dtype=str`, `keep_default_na=False`) : `NA` reste `"NA"`
  et `data_gb` vide reste `""`.
- `validity_days` → entier ; `price`, `data_gb`, `price_per_gb` → flottants
  (`""` devient `NaN`) ; `top_up`, `is_unlimited`, `is_region` → booléens via
  `{"True": True, "False": False}`.
- C'est cette fonction qui permet à `report` de ne jamais relire les 18 CSV.
- Un test de round-trip (écrire, relire) vérifie colonnes, types, absence de
  `NaN` sur `country_code` et somme des illimitées.

### `clean_data(raw: pd.DataFrame) -> pd.DataFrame`

Type les colonnes, valide le contrat, ajoute les colonnes dérivées. Ne modifie
pas `raw` (travail sur une copie).

```python
clean = clean_data(raw)  # (5056, 15)
```

Ordre des opérations :

1. aucune valeur vide dans les colonnes obligatoires (`data_gb` excepté) ;
2. `sku` unique ;
3. `currency` = `EUR` ;
4. `network` ∈ {`4G`, `5G`} ;
5. `validity_days` converti en entier strictement positif ;
6. `price` numérique et strictement positif ;
7. `top_up` ∈ {`oui`, `non`}, converti en booléen ;
8. `is_unlimited` = `data_display == "Illimité"` ;
9. cohérence : `data_gb` vide **si et seulement si** `is_unlimited` ;
10. `is_region` = code dans {`EU`, `AS`, `NA`, `WW`} ;
11. préfixage des codes de zone en `ZONE_EU`, `ZONE_AS`, `ZONE_NA`, `ZONE_WW` ;
12. `price_per_gb` = `price / data_gb` (vide si illimité).

Toute violation lève un `ValueError` citant les SKU ou les valeurs fautives.
Aucune correction silencieuse.

### `write_csv(df: pd.DataFrame, path: Path) -> None`

Écrit un DataFrame en CSV : UTF-8, en-tête inclus, sans colonne d'index.

```python
write_csv(clean, CLEAN_OUTPUT)
```

- Crée le dossier parent si nécessaire (`mkdir(parents=True, exist_ok=True)`).
- `index=False` est indispensable : sans lui, pandas ajoute une colonne d'index
  sans nom et le fichier passe de 15 à 16 colonnes.

## `mybestsim/merge.py`

### `run() -> pd.DataFrame`

`load_raw` → `clean_data` → `write_csv` des deux tables. Renvoie la table
nettoyée.

```python
clean = merge.run()
```

### `main() -> int`

Point d'entrée de `python -m mybestsim.merge` : exécute `run()` et affiche le
nombre de lignes et les chemins écrits.

- `0` en cas de succès, `1` en cas d'échec.
- Les écritures n'ont lieu qu'après un nettoyage réussi : pas de fichier à
  moitié produit.
- `UnicodeDecodeError` est intercepté **avant** `ValueError` (il en hérite),
  puis `OSError`, puis `ValueError`, pour un message adapté à chaque cause.

## `mybestsim/report.py`

### `run(clean) -> None`

Affiche les KPI calculés sur la table nettoyée : total, produits > 100 €,
fourchette, moyenne de Go, prix moyen et médian, répartition par fournisseur.

```python
report.run(clean)
```

### `main() -> int`

Point d'entrée de `python -m mybestsim.report` : lit `data/processed/
clean_products.csv` via `load_clean`, puis appelle `run()`.

- Si le fichier est absent, message explicite : « lance d'abord
  `python -m mybestsim.merge` ».
- Ne relit jamais les 18 CSV sources.

## `mybestsim/__main__.py`

### `main() -> int`

Point d'entrée de `python -m mybestsim` : appelle `merge.main()`, puis
`report.main()` si le premier a réussi. S'arrête au premier échec.

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
| Noms de fonctions et de modules | anglais (`load_raw`, `clean_data`, `mean_data_gb`) |
| Variables locales et docstrings | français (`fichiers`, `colonnes`, `valeurs`) |
| Types de retour | Python natifs (`int`, `float`, `dict`) pour rester sérialisables |
| Arrondi | à la sortie seulement, jamais avant un seuil ou une comparaison |
| Illimité | booléen `is_unlimited` + `data_gb` manquant, jamais `0` |
| Déterminisme | pas d'horodatage, fichiers triés, sorties comparables par `md5sum` |
| Style de retour | calcul directement dans le `return` ; variable intermédiaire seulement si la valeur sert deux fois |

## À venir

- `compute_metrics(df)` — assemble les KPI dans le dictionnaire écrit en
  `data/metrics.json` ;
- `site.py` — rend la page HTML depuis `metrics.json`.

## Tests

```bash
make test        # ou : python -m pytest
```

27 tests, répartis en trois fichiers :

- `tests/test_ingest.py` — lecture des 18 fichiers, refus d'un dossier vide ou
  d'un en-tête différent, round-trip de la table propre ;
- `tests/test_clean.py` — invariants du nettoyage, valeurs vides et cas de rejet ;
- `tests/test_metrics.py` — les six KPI et les invariants de la répartition
  (somme des cartes = 5 056, parts ≈ 100 %, tri décroissant).
