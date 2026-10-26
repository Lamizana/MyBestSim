# MyBestSim — dashboard eSIM

Consolide les 18 CSV fournisseurs du catalogue eSIM, valide la donnée et
calcule les indicateurs de prix, de volume et de couverture. Le tout est
affiché dans une application Streamlit.

Projet réalisé dans le cadre du test de recrutement MyBestSim (partie 1 :
data & automatisation).

- **Application** : à compléter après déploiement sur Streamlit Cloud
- **Code** : [github.com/Lamizana/MyBestSim](https://github.com/Lamizana/MyBestSim)

## Arborescence

```text
.
├── app.py                  # application Streamlit (affichage seul)
├── Makefile                # install / data / run / test / lint / clean
├── pyproject.toml          # dépendances, ruff, pytest
├── requirements.txt        # dépendances lues par Streamlit Cloud
├── .streamlit/config.toml  # thème MyBestSim (couleurs, police, arrondis)
├── assets/
│   ├── logo.png            # favicon
│   └── logo_wordmark.png   # logo + nom, affiché par st.logo
├── mybestsim/
│   ├── config.py           # chemins et colonnes attendues
│   ├── etl.py              # lecture, validation, typage
│   ├── metrics.py          # six KPI + série des meilleures offres
│   └── graphiques.py       # spécifications Altair
├── data/raw/               # 18 CSV fournisseurs, jamais modifiés
├── tests/                  # 44 tests
└── docs/
    ├── FONCTIONS.md        # détail des fonctions
    ├── enonce-test.pdf     # sujet du test
    └── archive/            # plans de travail successifs
```

## Prérequis

Python ≥ 3.11. L'application tourne sur Streamlit ; les données sont lues avec
pandas. Aucune base de données, aucun serveur.

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
| `make install` | `python3 -m venv .venv` puis `pip install -e ".[dev]"` | crée l'environnement |
| `make run` | `python -m streamlit run app.py` | lance l'application |
| `make test` | `python -m pytest` | exécute les 44 tests |
| `make lint` | `ruff check .` | vérifie le style |
| `make clean` | `rm -rf …` | supprime les caches |

## Un seul chemin

L'application recalcule tout en mémoire, au démarrage, depuis `data/raw/` :
`load_raw` → `clean_data` → `compute_metrics`. Aucun artefact intermédiaire,
aucune étape de build. Le résultat est mis en cache par `@st.cache_data`.

Conséquence : un clone du dépôt suffit à lancer l'application. Et toute
modification de `etl.py` nécessite un redémarrage du serveur, le cache ne
portant que sur le code de la fonction décorée.

## KPI

Les six indicateurs demandés :

| KPI | Valeur |
|---|---|
| Nombre total de cartes | 5 056 |
| Produits > 100 € | 56 |
| Fourchette de prix | 5,36 € – 154,63 € |
| Moyenne de data | 14,49 Go (4 403 offres finies) |
| Prix moyen | 29,30 € (médiane 20,70 €) |
| Répartition par fournisseur | 18 fournisseurs, Airalo 722 → 4S eSIM 92 |

S'y ajoute une série pour la section « Meilleures offres par destination » :
**1 113 combinaisons** destination × volume × durée (54 destinations, 7 volumes,
3 durées), avec pour chacune le fournisseur le moins cher, son prix, le prix
maximum et le nombre d'offres comparées.

## Écran

1. **Chiffres clés** — six cartes, chacune avec une ligne de contexte.
2. **Répartition par fournisseur** — barres horizontales triées.
3. **Distribution des prix** — histogramme par tranche de 10 €, tranches à
   partir de 100 € en rouge.
4. **Meilleures offres par destination** — sélection du volume et de la durée,
   podium des trois destinations les moins chères, onglets Pays / Régions,
   recherche, tableau triable.

## Contrat de données

Douze colonnes source, identiques dans les 18 fichiers :
`sku`, `provider`, `product_name`, `country_code`, `country_name`, `data_gb`,
`data_display`, `validity_days`, `price`, `currency`, `network`, `top_up`.

Deux colonnes dérivées :

| Colonne | Type | Définition |
|---|---|---|
| `is_unlimited` | bool | vrai si `data_display` vaut « Illimité » (653 lignes) |
| `is_region` | bool | vrai si l'offre couvre une zone multi-pays (778 lignes) |

Règles de validation, toutes bloquantes (aucune correction silencieuse) :

| Règle | Vérifié par |
|---|---|
| aucune colonne obligatoire vide (`data_gb` excepté si illimité) | `clean_data` |
| `sku` unique | `clean_data` |
| `currency` = `EUR` | `clean_data` |
| `network` ∈ {`4G`, `5G`} | `clean_data` |
| `top_up` ∈ {`oui`, `non`} | `clean_data` |
| `price` numérique et strictement positif | `clean_data` |
| `validity_days` entier strictement positif | `clean_data` |
| `data_gb` vide **si et seulement si** `is_unlimited` | `clean_data` |
| en-têtes égaux aux 12 colonnes attendues | `load_raw` |

Chaque échec indique les SKU ou le fichier fautif, et le programme s'arrête avec
un code de sortie non nul.

## Décisions

- **Illimité ≠ 0 Go.** La moyenne de data porte sur les 4 403 offres à volume
  fini ; les 653 offres illimitées sont exclues et signalées à part.
- **Seuil de 100 €** appliqué strictement (`price > 100`).
- **Pays vs régions.** 50 pays et 4 zones (Europe, Asie, Amérique du Nord,
  Monde). Les zones ont leur propre onglet et ne sont jamais mélangées aux pays.
- **Codes de zone préfixés** (`ZONE_EU`, `ZONE_AS`, `ZONE_NA`, `ZONE_WW`) :
  `NA` serait interprété comme une valeur manquante par pandas à la relecture.
- **Devise unique.** Tout est en euros ; une autre devise fait échouer le
  pipeline.

## Tests

```bash
make test
```

44 tests couvrent les invariants des données réelles (5 056 lignes, 653
illimitées, 778 zones, moyenne de 14,49 Go), les six KPI, la série des
meilleures offres (1 113 combinaisons, minimum et départage), la structure des
graphiques, le rendu de l'application et le rejet des cas invalides.

La CI (`.github/workflows/ci.yml`) exécute `ruff` et `pytest` sur Python 3.12 à
chaque push.

## Limites connues

- Jeu de données synthétique fourni pour le test : les relations observées
  décrivent ce catalogue, pas le marché réel.
- Aucune déduplication : les 620 doublons apparents `(provider, product_name)`
  sont de vraies variantes de prix, de réseau ou de recharge.
- Aucune suppression de valeur extrême : le produit à 154,63 € est réel.
- Le prix au Go n'est pas exposé : à volume constant il n'apporte rien, et il
  n'a pas de sens pour les offres illimitées.

## Documentation

- [`docs/FONCTIONS.md`](docs/FONCTIONS.md) — rôles et signatures des fonctions.
- [`docs/archive/`](docs/archive/) — plans de travail successifs (exécution,
  apprentissage, migration Streamlit).
