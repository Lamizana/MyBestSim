# Test de recrutement MyBestSim — plan d'exécution

**Objectif :** livrer un dashboard de statistiques eSIM en ligne et un article SEO publié, avant le **vendredi 30 octobre 2026**.
**Contrainte :** aucune ligne de code dans ce plan, seulement l'architecture et les décisions.
**Nature du test :** 18 CSV fournisseurs, 1 dashboard public, 1 article SEO public, 1 note sur l'usage de l'IA.

---

## 1. Contexte vérifié

- Offre : stage 6 mois, 100 % remote, « Stagiaire Développeur IA & Automatisation », rattachement direct au fondateur.
- Évaluation annoncée : **résultat**, **autonomie**, **méthodologie**. L'IA est encouragée et fait partie de ce qui est observé.
- Le mail de retour précise que l'article doit **aussi être mis en ligne** (l'énoncé accepte un simple Markdown : c'est un piège, il faut une URL).
- Deadline : vendredi 30 octobre. Point de départ : jeudi 22 octobre. **8 jours.**

### Audit des données (fait le 22/10)

| Constat | Valeur | Conséquence |
|---|---|---|
| Fichiers / lignes | 18 / 5 056 | Un seul schéma, 12 colonnes identiques |
| Encodage / séparateur | UTF-8 (BOM possible) / virgule | Lecture défensive obligatoire |
| Devise | 100 % EUR | Aucune conversion ; refuser autre chose |
| `data_gb` vide | 653 lignes = « Illimité » | Point de définition central |
| Prix | 5,36 € → 154,63 € ; moyenne 29,30 ; médiane 20,70 | 56 produits > 100 € |
| `data_gb` | {1, 3, 5, 10, 20, 50} | Valeurs discrètes |
| `validity_days` | {7, 15, 30} | Entier, conservé dans la table nettoyée |
| `network` | 4G 3 302 / 5G 1 754 | 34,7 % de 5G |
| `top_up` | oui 2 738 / non 2 318 | 54,2 % rechargeables |
| SKU dupliqués | 0 | Dédup = garde-fou, pas un travail |
| Pays | 54 codes dont 4 régions (Europe, Asie, Amérique du Nord, Monde) | 50 pays + 4 zones |
| Bundles identiques chez ≥ 2 fournisseurs | 1 033 | Écart de prix médian 13,4 % |
| Prix au Go | médiane 2,55 € ; min 0,91 (Yesim) ; max 11,86 (Yatelo) | Bonus pertinent |

---

## 2. Principe directeur

**Un pipeline, deux livrables.** Les chiffres calculés pour le dashboard alimentent aussi l'article. Le jury doit voir un candidat qui comprend que MBS est un comparateur, pas deux exercices séparés.

---

## 3. Décisions figées

| Sujet | Décision | Alternative écartée |
|---|---|---|
| Ingestion | Python + contrat de schéma explicite | Pandas sans contrat |
| Stockage / calcul | DuckDB, requêtes SQL en fichiers séparés | Postgres (serveur inutile), pandas seul |
| Artefact pivot | `metrics.json` (valeur + définition + périmètre) | Chiffres codés en dur dans la page |
| Interface | Page statique générée (HTML + SVG) | Streamlit (lien qui s'endort), Power BI (binaire opaque, Windows), Looker Studio (méthodologie invisible) |
| Déploiement | GitHub Actions → GitHub Pages | Hébergement manuel |
| Article | ZehdBox, chemin dédié, mention « réalisé dans le cadre du test » | Google Doc, page noyée dans le dashboard |
| Repos | Dashboard dans `MyBestSim/dashboard/` ; article dans ZehdBox | Tout dans un seul repo |
| Langue | Français | — |

### Les six décisions à documenter dans `DECISIONS.md`

1. **« Illimité » ≠ 0 Go.** Moyenne sur les 4 403 cartes à data finie = **14,49 Go** ; les 653 illimitées (12,9 %) sont un KPI distinct. Les compter à 0 donnerait 12,62 Go, chiffre faux.
2. **« Plus de 100 € » = strictement supérieur.** 56 produits. Aucun prix à 100,00 € → pas d'ambiguïté, mais règle écrite.
3. **Fourchette = min/max réels** (5,36 – 154,63 €), pas des percentiles : la question demande l'étendue.
4. **Pays vs régions.** 50 pays + 4 zones ; les zones ont leur propre classement, elles n'entrent pas dans le classement pays.
5. **Devise.** Tout EUR, aucune conversion ; un autre code devise fait échouer le pipeline.
6. **Périmètre du comptage.** Lignes valides après validation, avant tout filtre d'affichage.

---

## 4. Architecture

### 4.1 Les cinq couches

| Couche | Rôle | Sortie |
|---|---|---|
| L0 — Brut | CSV intacts, manifeste (nom, SHA-256, lignes) | `data/raw/2026-10-22/` |
| L1 — Ingestion & contrat | Lecture défensive, typage, normalisation, contrôles | Table canonique + `quality_report` |
| L2 — Analytique | KPI requis et bonus, un fichier SQL par famille | `metrics.json` |
| L3 — Présentation | Page générée depuis `metrics.json` | `site/index.html` |
| L4 — Publication | CI : rebuild + vérification + déploiement | URL publique |

### 4.2 Arborescence cible

> Structure effectivement implémentée : voir [`README.md`](../README.md).
> L'arborescence ci-dessous est la cible initiale du plan ; le paquet
> `mybestsim/` a remplacé `src/` pour rester lançable sans installation, et
> le projet est désormais à la racine du dépôt.

```text
MyBestSim/dashboard/
├── data/raw/2026-10-22/        # 18 CSV intacts
├── data/raw/manifest.json      # nom, sha256, lignes, encodage
├── src/contract.py             # schéma, types, valeurs autorisées
├── src/ingest.py               # lecture + validation + chargement DuckDB
├── src/quality.py              # contrôles qualité → reports/quality.json
├── src/sql/kpi_required.sql    # 6 KPI demandés
├── src/sql/kpi_bonus.sql       # 6 à 8 KPI bonus
├── src/build_metrics.py        # exécution SQL → reports/metrics.json
├── src/build_site.py           # metrics.json + gabarit → site/index.html
├── templates/                  # gabarit de page
├── tests/golden.csv            # 10 lignes calculées à la main
├── tests/                      # unitaires, valeurs dorées, invariants
├── reports/                    # metrics.json, quality.json, quality.md
├── docs/DECISIONS.md
├── docs/JOURNAL_IA.md
├── docs/SEO_BRIEF.md           # analyse SERP + décision de longueur
├── README.md                   # lien, chiffres, décisions, rebuild, IA
└── .github/workflows/deploy.yml
```

### 4.3 Contrat de schéma

12 champs : `sku`, `provider`, `product_name`, `country_code`, `country_name`, `data_gb`, `data_display`, `validity_days`, `price`, `currency`, `network`, `top_up`.

Règles : `sku` unique ; `price` > 0 ; `currency` = EUR ; `network` ∈ {4G, 5G} ; `top_up` ∈ {oui, non} ; `validity_days` entier > 0 ; `data_gb` nul **si et seulement si** `data_display` = « Illimité ». Toute violation est listée, jamais corrigée en silence.

### 4.4 Stratégie de test (3 niveaux)

1. **Jeu doré** — 10 lignes construites à la main, chaque KPI calculé au crayon. Le pipeline doit tomber exactement dessus.
2. **Invariants de réconciliation** sur les vraies données : Σ cartes/fournisseur = 5 056 ; finies + illimitées = 5 056 ; devise unique ; aucun prix nul ; SKU uniques.
3. **Cas limites** : BOM UTF-8, champ vide, espace parasite, prix décimal, fichier vide, doublon de fichier. Comportement attendu écrit pour chacun.

---

## 5. Contrat des KPI

### 5.1 Les six KPI demandés

| KPI | Valeur attendue |
|---|---|
| Nombre total de cartes | **5 056** |
| Produits > 100 € | **56** |
| Fourchette de prix | **5,36 € – 154,63 €** |
| Moyenne de data par carte | **14,49 Go** (4 403 cartes finies) |
| Prix moyen global | **29,30 €** (médiane 20,70) |
| Répartition par fournisseur | **18** fournisseurs, Airalo 722 → 4S eSIM 92 |

### 5.2 Les bonus retenus

| Bonus | Valeur |
|---|---|
| Part d'illimité | 653 cartes, 12,9 % |
| Prix au Go | médiane 2,55 € |
| Quartiles de prix | 11,76 / 20,70 / 39,29 € |
| **Écart inter-fournisseurs** | 1 033 bundles, écart médian 13,4 % |
| Prix moyen par fournisseur | 4S eSIM 24,26 € → Yesim 32,10 € |
| Top destinations hors zones | Indonésie 104, Arabie saoudite 102, Singapour 99, Égypte 98 |

### 5.3 Ce que doit contenir la page

1. Les 6 cartes KPI au-dessus de la ligne de flottaison.
2. Classement des fournisseurs (barres horizontales triées).
3. Histogramme des prix.
4. Bloc bonus : illimité, 5G, top-up, prix au Go, top destinations.
5. **Sélecteur de destination** → offre la moins chère par fournisseur + écart de prix.
6. Bloc « Méthodologie » : définitions, rapport qualité, deux dénominateurs de la moyenne, lien GitHub.
7. Lien croisé vers l'article.

Contraintes : français, mobile-first (le jury ouvrira depuis un téléphone), contraste accessible, Lighthouse ≥ 90, aucun backend.

---

## 6. Article SEO

### 6.1 Angle

Éviter le « top 5 eSIM croisière » générique et faux : **en pleine mer, une eSIM classique ne capte pas**. La réponse honnête et différenciante est hybride — eSIM pour les escales, WiFi du bord pour les jours en mer, avec le point de bascule selon la durée de la croisière. C'est ce qui crédibilise la marque et ce qui peut ranker.

### 6.2 Processus

1. **Brief SEO** : SERP FR sur « eSIM croisière », « internet en croisière », « forfait internet bateau de croisière » ; analyse de 5 concurrents (structure, longueur, tableaux, FAQ, angle) ; décision de longueur argumentée (~2 000 mots, arbitrée par la SERP).
2. **Plan** : H1, slug, title ≤ 60, meta ≤ 155, promesse par section, entités à couvrir (WiFi à bord et tarifs, couverture en mer vs escales, roaming maritime, installation avant départ, compatibilité, durée du voyage).
3. **Rédaction** au ton MBS : réponse directe de 40–60 mots sous le H1, encadré « L'essentiel en 30 secondes », tableau comparatif, FAQ 5–6 questions, CTA.
4. **SEO technique** : canonical, Open Graph, JSON-LD `Article` + `FAQPage`, images WebP avec alt, 3 liens internes, 2 sources externes datées.
5. **Publication** sur ZehdBox (MkDocs déjà en ligne, déjà dans Search Console) + demande d'indexation + Lighthouse mobile.

### 6.3 Plan détaillé

- H1 + réponse directe en 50 mots (featured snippet)
- L'essentiel en 30 secondes — encadré décisionnel
- Pourquoi le WiFi à bord coûte cher et pourquoi l'eSIM ne le remplace pas en mer
- Les trois profils : escales uniquement / jours en mer / longue croisière
- Tableau comparatif eSIM vs WiFi bord vs roaming
- Quelle eSIM selon la zone de croisière — **tableau alimenté par le catalogue** : Méditerranée, Caraïbes, Europe du Nord, Alaska
- Installation avant l'embarquement
- Pièges : compatibilité, activation, expiration des données
- FAQ 6 questions (People Also Ask)
- Conclusion + CTA

### 6.4 Visuels

Trois visuels maison (l'auteur est illustrateur, c'est un avantage différenciant) : un hero, un schéma « mer vs escale », une carte des zones. WebP, alt rédigés.

---

## 7. Calendrier

| Jour | Matin | Après-midi | Fini quand |
|---|---|---|---|
| **Jeu 22** | Repo, structure, CSV + manifeste | Contrat de schéma, `DECISIONS.md`, README | Repo présentable même vide |
| **Ven 23** | Ingestion + validation | Tests unitaires + rapport qualité | 5 056 lignes, 0 rejet, tests verts |
| **Sam 24** | 6 KPI en SQL | Bonus + `metrics.json` + tests | Les 6 valeurs attendues tombent juste |
| **Dim 25** | Génération de la page (cartes + 2 graphiques) | Déploiement Pages | **Lien public avec les 6 KPI** |
| **Lun 26** | Bonus, sélecteur destination, méthodologie | Mobile, Lighthouse, README final | Page complète, Lighthouse ≥ 90 |
| **Mar 27** | Brief SEO, plan | Rédaction complète + illustrations | Article relu |
| **Mer 28** | Publication, JSON-LD, maillage | Relecture à froid, Search Console | **Article en ligne et soumis** |
| **Jeu 29** | Re-vérification des chiffres, journal IA | E-mail de rendu **envoyé** | Dossier clos |
| **Ven 30** | Marge | — | — |

**Règle :** rien ne s'ajoute après mercredi 28. Les deux derniers jours servent à vérifier et à écrire.

---

## 8. Livrables et rendu

### 8.1 Checklist

- [ ] URL dashboard publique et stable
- [ ] URL du repo GitHub
- [ ] URL de l'article publié
- [ ] `DECISIONS.md` (6 arbitrages)
- [ ] Rapport qualité
- [ ] Journal d'usage de l'IA
- [ ] README avec commande de reconstruction

### 8.2 Structure de l'e-mail

1. Objet : « Test pratique — dashboard + article »
2. Lien dashboard + repo
3. Lien article
4. Trois phrases sur les décisions (illimité en premier)
5. Paragraphe IA : délégué / vérifié / **où l'IA s'est trompée**
6. Formule courte

### 8.3 Journal IA (gabarit)

- Ce que j'ai délégué (échafaudage, tests, plan SEO, reformulations).
- Ce que j'ai vérifié moi-même (tous les chiffres, par requête indépendante ; contrat ; tests).
- Où l'IA s'est trompée (elle compte l'illimité à 0 Go, elle invente des tarifs de WiFi à bord, elle propose des outils surdimensionnés).
- Comment je l'ai pilotée (contexte, contraintes, relecture, décisions conservées).

---

## 9. Risques

| Risque | Mitigation |
|---|---|
| Définition de la moyenne de data | Écrite, deux dénominateurs affichés, illimité en KPI séparé |
| Lien indisponible le jour J | Statique, hébergé, jamais de tunnel local ni de service dormant |
| Sur-ingénierie | Pas de serveur, pas d'auth, pas de multi-langue |
| Chiffres faux dans l'article | Tableaux générés depuis `metrics.json`, pas saisis à la main |
| Article sous marque MBS sur site perso | Mention explicite du cadre du test |
| Retard | v0 en ligne dimanche, envoi jeudi, jamais vendredi |

---

## 10. À faire à la reprise

1. Basculer sur l'agent build (le mode plan interdit l'écriture dans le repo).
2. Copier ce plan dans `MyBestSim/dashboard/docs/PLAN.md`.
3. Initialiser le repo, le manifeste et `DECISIONS.md`.
