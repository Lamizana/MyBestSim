# Passage à Streamlit — plan d'exécution

> **Contexte.** 26 octobre 2026, échéance vendredi 30. Le pipeline est terminé
> (37 tests verts, six KPI, page statique générée). Décision : remplacer la
> couche d'affichage statique par une application Streamlit pour sécuriser le
> lien public et libérer du temps pour l'article.
> **Périmètre :** six KPI uniquement. Aucun bonus, aucune statistique
> complémentaire.

---

## 1. Ce qui change, ce qui ne change pas

| Élément | Avant | Après |
|---|---|---|
| Ingestion, nettoyage, contrat | `mybestsim/etl.py` | **inchangé** |
| Calcul des KPI | `mybestsim/metrics.py` | **inchangé** |
| Tests | 37 tests | **37 + 2** |
| Affichage | `site.py` + `templates/index.html.j2` | `app.py` Streamlit |
| Publication | GitHub Pages | Streamlit Community Cloud |
| Déploiement | GitHub Actions | redéploiement automatique sur push |

Le pipeline ne bouge pas : seule la dernière couche est remplacée. C'est ce qui
rend la migration sûre à trois jours de l'échéance.

---

## 2. Principe : application mince, logique testée

`app.py` ne contient **aucun calcul**. Il appelle `compute_metrics()` et
affiche. Toute la logique reste dans `mybestsim/`, où elle est déjà couverte
par les tests.

Conséquence : on peut tester l'app sans navigateur, et un bug d'affichage ne
peut pas fausser un chiffre.

---

## 3. Arborescence cible

```text
.
├── app.py                      # point d'entrée Streamlit (affichage seul)
├── .streamlit/
│   └── config.toml             # thème MyBestSim
├── mybestsim/                  # inchangé
├── data/raw/                   # 18 CSV, commités
├── data/processed/             # ignoré par git, calculé au démarrage
├── requirements.txt            # dépendances lues par Streamlit Cloud
├── tests/
│   └── test_app.py             # nouveau : fumée + six KPI
├── site/                       # conservé en secours jusqu'au 29/10
└── templates/                  # idem
```

---

## 4. Contrat de l'application

| Fonction | Rôle | Signature |
|---|---|---|
| `charger_metriques()` | lit les 18 CSV, nettoie, calcule, retourne le dict de KPI | `() -> dict` |
| `afficher_entete(metrics)` | titre, sous-titre, contexte | `(dict) -> None` |
| `afficher_kpi(metrics)` | six `st.metric` avec la définition en aide | `(dict) -> None` |
| `afficher_fournisseurs(metrics)` | barres horizontales triées | `(dict) -> None` |
| `afficher_prix(metrics)` | histogramme des tranches de 10 € | `(dict) -> None` |
| `afficher_methodologie(metrics)` | `st.expander` : définitions, dénominateur, limites | `(dict) -> None` |
| `main()` | assemble la page | `() -> None` |

`charger_metriques` est décorée par `@st.cache_data` : elle s'exécute une fois
par processus, pas à chaque interaction.

### Détails qui comptent

- **Pas de fichier intermédiaire.** `data/processed/` n'est pas commité et le
  disque de Streamlit Cloud est éphémère. L'app calcule en mémoire au démarrage
  (~0,2 s sur 5 056 lignes) au lieu de lire `metrics.json`.
- **Six métriques, pas onze.** Le retrait des bonus est déjà fait côté
  `metrics.py` : l'app n'a rien à filtrer.
- **Définitions visibles.** `st.metric(..., help=definition)` affiche la règle
  au survol. C'est le seul endroit où le jury voit la décision « illimité ».
- **Mise en page.** `layout="wide"`, trois colonnes de métriques, graphiques en
  pleine largeur, `st.expander` pour la méthodologie.
- **Thème.** `.streamlit/config.toml` : `primaryColor = "#007bff"`,
  `backgroundColor = "#ffffff"`, `secondaryBackgroundColor = "#f5f7fa"`,
  `textColor = "#1d2939"`. Poppins n'est pas supporté nativement : on garde la
  police système plutôt que d'injecter du CSS fragile.

---

## 5. Étapes

### T1 — Dépendance et fichier de déploiement
- Ajouter `streamlit` aux dépendances de `pyproject.toml`.
- Créer `requirements.txt` avec les mêmes contraintes (Streamlit Cloud lit ce
  fichier en priorité).
- Vérifier `streamlit run app.py` avec une page vide.

**Fini quand :** l'app démarre localement, `ruff` et les 37 tests passent
toujours.

### T2 — Couche données cachée
- `charger_metriques()` : `load_raw` → `clean_data` → `compute_metrics`.
- `@st.cache_data`, aucun accès disque en écriture.

**Fini quand :** `python -c` importe la fonction et renvoie les six KPI attendus.

### T3 — Les six cartes
- `afficher_kpi` avec `st.columns(3)` et deux rangées.
- Format français (espace insécable, virgule décimale) : réutiliser `format_fr`
  de `mybestsim/site.py`, ou le déplacer dans un module partagé.

**Fini quand :** les six valeurs affichées sont 5 056 / 56 / 5,36–154,63 /
14,49 / 29,30 / 18.

### T4 — Les deux graphiques
- Fournisseurs : barres horizontales triées (`st.bar_chart` ou Altair, déjà
  fourni avec Streamlit).
- Prix : histogramme des 16 tranches.
- Pas de camembert, pas de sélecteur, pas de tableau de destinations.

**Fini quand :** les deux graphiques s'affichent sur 360 px de large sans
défilement horizontal.

### T5 — Méthodologie et thème
- `st.expander` : 5 056 offres, 18 fichiers, aucun rejet ; moyenne sur 4 403
  offres finies ; illimitées exclues et jamais comptées 0 Go ; jeu de données
  synthétique.
- Lien vers le dépôt GitHub.
- Thème dans `.streamlit/config.toml`.

**Fini quand :** la page tient sur un écran de téléphone, lisible sans zoom.

### T6 — Test de fumée
- `tests/test_app.py` : `AppTest.from_file("app.py").run()`, aucune exception,
  exactement six `st.metric`.

**Fini quand :** `pytest` passe à 39 tests.

### T7 — Déploiement
- Dépôt public (voir section 6), branche `main`, fichier `app.py`.
- share.streamlit.io → New app → Python 3.12.
- Ouvrir l'URL sur un téléphone en 4G, vérifier le réveil après inactivité.

**Fini quand :** le lien public affiche les six KPI sans authentification.

### T8 — Bascule
- Remplacer le lien dans le README et dans l'e-mail.
- Garder `site.py` et le gabarit jusqu'au jeudi 29 comme secours.
- Commit séparé pour la suppression de la page statique, seulement après
  validation du lien.

---

## 6. Point bloquant : le dépôt doit être public

Streamlit Community Cloud déploie depuis un dépôt GitHub **public** (l'offre
gratuite). Or l'historique Git contient encore les documents de candidature
(commit `a9f5bca`), retirés de l'arbre mais toujours présents dans les commits.

Publier tel quel exposerait ton CV, ton téléphone et ton adresse.

Deux options, dans l'ordre de préférence :

1. **Nouveau dépôt, historique neuf.** Créer un dépôt public
   `mybestsim-dashboard`, y pousser un commit unique de l'état actuel
   (branche orpheline). Simple, rapide, aucune trace des documents.
2. **Réécrire l'historique** du dépôt existant pour supprimer `papiers_stage/`
   de tous les commits (`git filter-repo`), puis le rendre public.

L'option 1 est recommandée : elle prend cinq minutes et ne touche pas à
l'historique local.

---

## 7. Risques et parades

| Risque | Réalité | Parade |
|---|---|---|
| Lien qui s'endort | L'app se met en veille après inactivité ; réveil en 10–30 s | Ouvrir le lien avant d'envoyer l'e-mail ; l'indiquer dans le README |
| Dépôt public | CV dans l'historique | Section 6, option 1 |
| Design moins contrôlé | Streamlit impose sa mise en page | Thème + largeur + `st.metric` ; on accepte |
| Calcul au démarrage | Recalcul à chaque redémarrage du conteneur | `@st.cache_data`, 0,2 s mesuré |
| Dépendances | Streamlit Cloud installe `requirements.txt` | Versions épinglées, test local identique |
| Régression silencieuse | L'app pourrait afficher un chiffre faux | Tests `metrics.py` inchangés + test de fumée |

---

## 8. Calendrier (4 jours)

| Jour | Travail | Sortie |
|---|---|---|
| **Lun 26** | T1 à T4 | App locale avec KPI et graphiques |
| **Mar 27** | T5 à T7 | **Lien Streamlit public validé sur mobile** |
| **Mer 28** | Article SEO (journée entière) | Article publié |
| **Jeu 29** | T8, vérification des chiffres, README, journal IA | E-mail envoyé |
| **Ven 30** | Marge | — |

Le passage à Streamlit coûte une journée et demie, mais il en économise deux
sur l'interface statique. Le solde est positif pour l'article.

---

## 9. Critères d'acceptation

- [ ] URL publique, sans authentification, ouverte depuis un téléphone
- [ ] Six KPI exacts : 5 056 / 56 / 5,36–154,63 / 14,49 / 29,30 / 18
- [ ] Deux graphiques lisibles à 360 px
- [ ] Méthodologie présente, y compris la règle « illimité ≠ 0 Go »
- [ ] Aucun bonus affiché
- [ ] 39 tests verts, `ruff` propre
- [ ] README à jour avec le nouveau lien

---

## 10. Retour arrière

`make site` reste fonctionnel jusqu'au 29. Si Streamlit Cloud bloque
(dépôt public impossible, build en échec), on redéploie la page statique sur
GitHub Pages et on garde les six KPI. Le pipeline et les tests étant communs,
le retour coûte une heure, pas une journée.

---

## 11. Ce qu'on ne fait pas

- Pas de sélecteur de destination, pas de comparateur : c'était le bonus, il est
  retiré.
- Pas de filtre par fournisseur, pas de recherche.
- Pas de base de données ni de fichier DuckDB.
- Pas de CSS injecté pour forcer Poppins.
- Pas de page multi-onglets.
