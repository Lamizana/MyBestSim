# Fonctions du pipeline

Ce document décrit les modules, leurs responsabilités et les signatures
publiques. Il suit le flux de données : lire, valider, calculer, afficher.

## Vue d'ensemble

```text
data/raw/*.csv
   │  load_raw
   ▼
DataFrame brut (12 colonnes texte)
   │  clean_data  (validation bloquante + colonnes dérivées)
   ▼
DataFrame propre (14 colonnes typées)
   │  compute_metrics
   ▼
dict { meta, kpi, series }
   │
   └── app.py            → application Streamlit
```

Aucun fichier intermédiaire : l'application lit `data/raw/` et recalcule tout
en mémoire.

## `mybestsim/config.py`

Chemins du projet et contrat d'entrée.

| Nom | Rôle |
|---|---|
| `PROJECT_ROOT` | racine du dépôt |
| `DATA_DIR` | `data/raw/` |
| `ASSETS_DIR`, `LOGO`, `LOGO_MARQUE` | dossier `assets/` et logos |
| `EXPECTED_COLUMNS` | les 12 colonnes attendues, dans l'ordre |
| `REGION_CODES` | `EU`, `AS`, `NA`, `WW` |
| `ZONE_PREFIX` | `ZONE_` |
| `SEUIL_PRIX` | seuil du KPI « prix supérieur à 100 € » et de l'histogramme |
| `DEVISE` | devise acceptée (`EUR`) |
| `RESEAUX` | réseaux acceptés (`4G`, `5G`) |
| `VALEURS_TOP_UP` | correspondance `oui`/`non` → booléen |
| `LIBELLE_ILLIMITE` | libellé du volume illimité |
| `VOLUMES`, `VOLUME_DEFAUT` | volumes du filtre et sélection par défaut |
| `DUREES`, `DUREE_DEFAUT` | durées du filtre et sélection par défaut |

## `mybestsim/etl.py`

### `load_raw(data_dir: Path) -> pd.DataFrame`

Lit tous les CSV du dossier, vérifie que les en-têtes sont identiques à
`EXPECTED_COLUMNS`, puis empile les tables. Échoue si le dossier est vide ou
si un fichier a un schéma différent.

Un fichier dont l'empreinte SHA-256 est déjà vue est ignoré avec un
avertissement. Les lignes portant le même `sku` sont ensuite dédoublonnées si
elles sont identiques ; si leurs valeurs divergent, la lecture échoue en
nommant le SKU, les fichiers et les colonnes en cause.

### `clean_data(raw: pd.DataFrame) -> pd.DataFrame`

Type, valide et enrichit. Ne modifie pas `raw`. Les contrôles sont bloquants :
valeur obligatoire vide, SKU dupliqué, devise autre que EUR, réseau inconnu,
durée non entière ou non positive, prix illisible ou non positif, `data_gb`
vide sans « Illimité » (et inversement). Ajoute `is_unlimited` et `is_region`,
préfixe les codes de zone en `ZONE_*`.

## `mybestsim/metrics.py`

### KPI

| Fonction | Retour |
|---|---|
| `total_cards(df)` | nombre de lignes |
| `cards_above_price(df, seuil=SEUIL_PRIX)` | offres dont le prix dépasse strictement le seuil |
| `price_range(df)` | `{"min", "max"}` |
| `mean_data_gb(df)` | `{"valeur", "nb_offres"}`, illimitées exclues |
| `mean_price(df)` | `{"moyenne", "mediane"}` |
| `provider_distribution(df)` | liste `{provider, cartes, part_pct}` triée |

### Séries

**`price_histogram(df, largeur=10, maximum=160) -> list`** — 16 tranches de
10 €, y compris les vides, somme = 5 056.

**`prix_go_median(df) -> float`** — médiane du prix au Go sur les offres finies.

**`illimitees_prix(df) -> dict`** — nombre et prix médian des offres illimitées,
exclues du prix au Go.

**`prix_go_par_volume(df) -> list`** — par volume (1, 3, 5, 10, 20, 50 Go),
médiane du prix au Go et quartiles p25/p75, avec le nombre d'offres. Les offres
illimitées sont exclues : pas de dénominateur en Go.

**`meilleures_offres(df) -> list`** — pour chaque destination, volume et durée,
l'offre la moins chère. Une entrée contient `code`, `destination`, `zone`,
`volume`, `data_gb`, `validity_days`, `provider`, `prix`, `provider_max`,
`prix_max`, `offres`.
Départage déterministe : prix, puis nom du fournisseur. Les zones sont
conservées et signalées par `zone=True`. 1 113 combinaisons réelles.

**`compute_metrics(clean) -> dict`** — assemble `meta`, `kpi` (six indicateurs
avec `definition` et `perimetre`) et `series` (`histogramme_prix`,
`meilleures_offres`).

## `mybestsim/graphiques.py`

Spécifications Altair, sans Streamlit ni HTML. `_finaliser` applique la charte
commune : fond transparent, police Poppins, axes discrets.

| Fonction | Rendu |
|---|---|
| `fournisseurs(metrics)` | barres horizontales triées, valeur en bout de barre |
| `prix(metrics)` | histogramme par tranche, tranches ≥ 100 € en rouge, valeurs annotées |
| `prix_go_volume(metrics)` | barres de la médiane €/Go, écart interquartile p25–p75 |

## `app.py`

Application Streamlit, sans calcul : elle appelle `compute_metrics` et affiche.

| Fonction | Rôle |
|---|---|
| `charger_metriques()` | `load_raw` → `clean_data` → `compute_metrics`, mise en cache |
| `afficher_entete(metrics)` | titre, contexte, carte de périmètre |
| `afficher_kpi(metrics)` | six cartes, chacune avec une ligne de contexte |
| `afficher_fournisseurs(metrics)` | carte + barres |
| `afficher_prix(metrics)` | carte + histogramme |
| `_podium(offres)` | trois destinations les moins chères |
| `_tableau_offres(offres)` | tableau triable ; message si la sélection est vide |
| `afficher_offres(metrics)` | volume, durée, onglets Pays/Régions, recherche |
| `afficher_methodologie(metrics)` | définitions et limites |
| `format_fr(valeur, decimales)` | nombres à la française : `5 056`, `14,49` |
| `main()` | assemble la page |

## Conventions

| Sujet | Choix |
|---|---|
| Noms de fonctions et de modules | anglais |
| Variables locales et docstrings | français |
| Types de retour | Python natifs, sérialisables |
| Arrondi | à la sortie seulement |
| Illimité | `is_unlimited` + `data_gb` manquant, jamais `0` |
| Déterminisme | pas d'horodatage, tris stables |
| Streamlit | aucun calcul dans `app.py` |

## Tests

53 tests, cinq fichiers :

- `tests/test_ingest.py` — lecture des 18 fichiers, refus d'un dossier vide ou
  d'un en-tête différent, fichiers identiques, doublons exacts et conflits ;
- `tests/test_clean.py` — invariants du nettoyage et cas de rejet ;
- `tests/test_metrics.py` — six KPI, histogramme, meilleures offres, structure
  de `compute_metrics` ;
- `tests/test_graphiques.py` — structure des quatre graphiques Altair ;
- `tests/test_app.py` — rendu, six métriques, méthodologie, recherche vide.

La CI exécute `ruff` et `pytest` sur Python 3.12 à chaque push.
