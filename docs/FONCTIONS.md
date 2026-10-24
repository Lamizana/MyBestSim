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
report   :                        data/processed/clean_products.csv ──load_clean()──> metrics.* ──> metrics.json
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
| `etl.py` | `write_json(data, path)` | — | écrit le JSON (refuse `NaN`) |
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
| `metrics.py` | `unlimited_share(df)` | `dict` | 12,9 % (653 / 5 056) |
| `metrics.py` | `price_per_gb_stats(df)` | `dict` | médiane 2,55 sur 4 403 offres |
| `metrics.py` | `bundle_spread(df)` | `dict` | 1 033 bundles, écart médian 13,4 % |
| `metrics.py` | `provider_stats(df)` | `list` | 18 fournisseurs enrichis |
| `metrics.py` | `cheapest_by_destination(df)` | `list` | 50 pays × 6 paliers |
| `metrics.py` | `compute_metrics(clean)` | `dict` | `meta` + les 11 KPI |

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

### `write_json(data: dict, path: Path) -> None`

Écrit un dictionnaire en JSON lisible et **strict**.

```python
write_json(compute_metrics(clean), METRICS_OUTPUT)
```

- `indent=2` et `ensure_ascii=False` : fichier diff-able, accents lisibles.
- `allow_nan=False` : `json.dumps` accepterait `NaN` par défaut, ce qui produit
  un JSON invalide pour les parseurs stricts. Ici, une valeur manquante lève
  une erreur au lieu de corrompre le fichier.
- Pas d'horodatage : deux exécutions produisent le même octet pour octet.

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
Écrit ensuite `data/processed/metrics.json`.

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

### `unlimited_share(df) -> dict`

Part des offres dont le volume est illimité.

```python
unlimited_share(clean)  # {'part_pct': 12.9, 'nb': 653, 'total': 5056}
```

### `price_per_gb_stats(df) -> dict`

Distribution du prix au Go sur les offres à volume fini.

```python
price_per_gb_stats(clean)
# {'mediane': 2.55, 'q1': 1.67, 'q3': 3.82, 'min': 0.91, 'max': 11.86, 'nb_offres': 4403}
```

- `dropna()` écarte les 653 illimitées : sans volume, pas de prix au Go.
- L'écart va de 0,91 € (Yesim, Philippines 50 Go) à 11,86 € (Yatelo, Europe
  1 Go 30 jours), soit un facteur 13.

### `bundle_spread(df, min_fournisseurs=2) -> dict`

Écart de prix entre fournisseurs pour un même bundle (destination, volume,
durée).

```python
bundle_spread(clean)
# {'nb_bundles': 1033, 'ecart_median_pct': 13.4, 'ecart_max_pct': 64.3,
#  'part_superieur_20_pct': 5.7, 'exemples': [...]}
```

- Les offres zonales sont incluses : comparer « Europe 10 Go 15 jours » entre
  fournisseurs est légitime. C'est différent de `cheapest_by_destination`, qui
  exclut les zones parce qu'on y compare des pays.
- Un bundle n'est retenu que s'il est proposé par au moins 2 fournisseurs.
- `exemples` donne les trois plus gros écarts, triés de façon déterministe.
- Interprétation : la moitié des bundles comparables varient de plus de 13,4 %
  selon le fournisseur, et 5,7 % dépassent 20 %.

### `provider_stats(df) -> list`

Statistiques par fournisseur, triées par nombre d'offres.

```python
provider_stats(clean)[0]
# {'provider': 'Airalo', 'cartes': 722, 'part_pct': 14.3, 'prix_moyen': 27.05,
#  'prix_go_median': 2.76, 'part_5g_pct': 30.2, 'part_illimite_pct': 12.6,
#  'pays': 50}
```

- `pays` compte les destinations nationales couvertes (zones exclues).
- `prix_go_median` exclut les illimitées par construction (`NaN` ignoré).

### `cheapest_by_destination(df, validity_days=15) -> list`

Offre la moins chère par pays et par palier de volume, à durée fixe.

```python
cheapest_by_destination(clean)[0]
# {'country_code': 'AE', 'country_name': 'Émirats arabes unis',
#  'offres': [{'data_display': '1 Go', 'data_gb': 1.0, 'provider': 'GigSky',
#              'price': 5.52, 'prix_max': 9.9, 'nb_offres': 18}, ...]}
```

- Zones exclues : comparer « Europe » à « Espagne » n'a pas de sens.
- Durée fixe (15 jours par défaut) : on ne compare pas un 7 jours à un 30 jours.
- Départage à prix égal : prix au Go, puis nom du fournisseur.
- `prix_max` donne la borne haute du même palier, donc l'écart réel.

### `compute_metrics(clean) -> dict`

Assemble les KPI et leurs définitions dans un dictionnaire sérialisable.

```python
compute_metrics(clean)["kpi"]["total_cartes"]["valeur"]  # 5056
```

Structure :

```json
{
  "meta": { "lignes": 5056, "fournisseurs": 18, "devise": "EUR" },
  "kpi": {
    "total_cartes": { "valeur": 5056, "definition": "...", "perimetre": "..." },
    "prix_superieur_100": { "valeur": 56, "...": "..." },
    "fourchette_prix": { "valeur": { "min": 5.36, "max": 154.63 }, "...": "..." },
    "data_gb_moyenne": { "valeur": 14.49, "...": "..." },
    "prix_moyen": { "valeur": { "moyenne": 29.3, "mediane": 20.7 }, "...": "..." },
    "fournisseurs": { "valeur": [ { "provider": "Airalo", "cartes": 722, "part_pct": 14.3 } ], "...": "..." },
    "part_illimite": { "valeur": { "part_pct": 12.9, "nb": 653, "total": 5056 }, "...": "..." },
    "prix_au_go": { "valeur": { "mediane": 2.55, "q1": 1.67, "q3": 3.82, "min": 0.91, "max": 11.86, "nb_offres": 4403 }, "...": "..." },
    "ecart_bundles": { "valeur": { "nb_bundles": 1033, "ecart_median_pct": 13.4 }, "...": "..." },
    "fournisseurs_detail": { "valeur": [ { "provider": "Airalo", "prix_go_median": 2.76 } ], "...": "..." },
    "meilleure_offre_par_destination": { "valeur": [ { "country_code": "ES", "offres": [] } ], "...": "..." }
  }
}
```

- Chaque KPI porte `definition` et `perimetre` : la page n'a pas à réinventer le
  dénominateur, et le lecteur voit la règle à côté du chiffre.
- Les valeurs composées (fourchette, moyenne + médiane, répartition) gardent
  leur forme de dictionnaire ou de liste.
- Aucune valeur numpy : tout est converti en types Python pour `json.dumps`.

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

- `site.py` — rend la page HTML depuis `metrics.json`.

## Tests

```bash
make test        # ou : python -m pytest
```

38 tests, répartis en trois fichiers :

- `tests/test_ingest.py` — lecture des 18 fichiers, refus d'un dossier vide ou
  d'un en-tête différent, round-trip de la table propre ;
- `tests/test_clean.py` — invariants du nettoyage, valeurs vides et cas de rejet ;
- `tests/test_metrics.py` — les 11 KPI, les invariants de la répartition
  (somme des cartes = 5 056, parts ≈ 100 %, tri décroissant), la structure de
  `metrics.json` et le refus de `NaN`.
