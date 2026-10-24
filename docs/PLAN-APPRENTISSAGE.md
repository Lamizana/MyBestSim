# MyBestSim — Plan d'apprentissage

> **Projet :** test de recrutement MyBestSim — dashboard eSIM + article SEO
> **Stack choisie :** Python / DuckDB / page statique / GitHub Pages / MkDocs (ZehdBox)
> **Niveau de départ :** à l'aise en Python, SQL, Git, Django ; débutant en qualité de données, dataviz et SEO
> **Rythme visé :** 8 jours de travail, 5 à 7 h par jour
> **Mode :** solo, avec agent IA (encouragé par l'employeur)
> **Échéance :** vendredi 30 octobre 2026

---

## Comment utiliser ce document

Chaque **jalon** suit la même structure :

1. **Objectifs** : ce que tu dois savoir faire à la fin.
2. **Théorie** : les concepts à maîtriser, avec les chapitres précis à lire.
3. **Sources** : les références à consulter (aucune ne fournit de code à copier).
4. **Exercices / auto-vérifications** : des tâches concrètes pour valider le jalon sans dépendre de l'IA.
5. **Critère de sortie** : le signal clair que tu peux passer au jalon suivant.

> [!INFO] **Règle d'or**
> Ce plan ne contient volontairement **aucun code**. Le but est que tu puisses écrire et **défendre chaque chiffre** toi-même. Le test évalue la méthodologie ; un dashboard juste dont tu ne sais pas expliquer les définitions vaut moins qu'un dashboard simple que tu maîtrises.

> [!WARNING] **Principe de réalité**
> Contrairement à un projet d'école, la date est fixe. L'apprentissage est ici **instrumental** : chaque jalon produit une brique livrable. Si un jalon déborde, on coupe dans le bonus, jamais dans les tests ni dans les définitions.

---

## Point de départ

| Déjà acquis | À acquérir pendant le test |
|---|---|
| Python, structures de données, fichiers | Conception d'un contrat de données et d'un rapport qualité |
| SQL, PostgreSQL, agrégations | DuckDB, modèle analytique minimal, sémantique des NULL |
| Git, branches, commits | CI qui bloque un déploiement sur écart de KPI |
| Django, HTML/CSS | Génération statique, déploiement Pages, Lighthouse |
| Rigueur de migration ERP | Définitions d'indicateurs, dénominateurs, quartiles |
| — | Analyse de SERP, structure SEO, données structurées |

Le vrai gouffre n'est pas technique : c'est **l'écart entre « ça calcule » et « c'est défendable »**. Tout ce plan vise cet écart.

---

## Planning des 8 jours

| Jour | Jalons | Thème | Sortie attendue |
| ------ | -------- | ------- |----------------- |
| **J1 — jeu 22** | 0 + 1 | *Cadrage et ingestion défensive* | Contrat écrit, 5 056 lignes chargées, rapport qualité |
| **J2 — ven 23** | 2 + 3 | *SQL analytique et rigueur statistique* | Les 6 KPI justes sur le jeu doré et sur le réel |
| **J3 — sam 24** | 4 | *Visualisation et hiérarchie* | Maquette validée, page générée depuis les métriques |
| **J4 — dim 25** | 5 | *Génération statique et déploiement* | **Lien public affichant les 6 KPI** |
| **J5 — lun 26** | 6 | *Tests, invariants, reproductibilité* | Clone propre → mêmes chiffres, CI rouge si dérive |
| **J6 — mar 27** | 7 | *SEO : comprendre avant d'écrire* | Brief d'une page, plan H2/H3, longueur argumentée |
| **J7 — mer 28** | 8 | *Rédaction et publication* | **Article en ligne, indexation demandée** |
| **J8 — jeu 29** | 9 | *Rendu et défense* | E-mail envoyé, dossier relu à froid |
| **J9 — ven 30** | — | *Marge* | Réponse aux questions d'Étienne |

---

## Jalon 0 — Cadrage, contrat de données et décisions

### Objectifs
- Transformer un énoncé flou en **contrat vérifiable** : 12 champs, types, domaines autorisés.
- Distinguer **brut / normalisé / calculé**, et savoir pourquoi le brut ne se modifie jamais.
- Écrire une définition de KPI **non ambiguë** : population, exclusions, numérateur, dénominateur, unité, arrondi.
- Identifier les six arbitrages du test et assumer chacun.

### Théorie
- Les dimensions de la qualité : complétude, validité, unicité, cohérence, exactitude, actualité.
- Différence entre **contrat de données** (ce que le fichier doit être) et validation applicative (ce que le code fait ensuite).
- Anatomie d'un indicateur : à quoi sert-il, sur quelle population, avec quelle exclusion.
- Traçabilité : copie immuable, manifeste, empreinte SHA-256, horodatage.
- Pourquoi « corriger en silence » est la pire des options dans un pipeline.

### Sources
- **DAMA-DMBOK** (chapitre *Data Quality*) — référence sur les dimensions de la qualité.
- **Great Expectations :** [concepts et attentes](https://greatexpectations.io) — vocabulaire des contrôles.
- **dbt :** [tests et documentation](https://docs.getdbt.com/docs/build/tests) — tests de données en pratique.
- **RFC 4180 :** [format CSV](https://www.rfc-editor.org/rfc/rfc4180).
- **Unicode :** [FAQ sur le BOM](https://unicode.org/faq/utf_bom.html).

### Exercices / auto-vérifications
- Lister les 12 champs et leur domaine **sur papier**, sans regarder les fichiers. Repérer les trois champs à risque.
- Écrire la définition de « moyenne de data par carte » en une phrase qui ne peut pas être mal interprétée.
- Calculer les 6 KPI à la main sur un échantillon de 10 lignes, avant d'écrire quoi que ce soit.
- Rédiger les six décisions : illimité, seuil de 100 €, fourchette, pays vs régions, devise, périmètre du comptage — avec l'alternative écartée à chaque fois.

### Critère de sortie
`DECISIONS.md` v1 existe, le contrat tient sur une page, et chaque KPI a une définition qui pourrait être testée par quelqu'un d'autre.

---

## Jalon 1 — Ingestion défensive

### Objectifs
- Lire 18 CSV **sans supposer** l'encodage, le séparateur ni les valeurs.
- Gérer BOM UTF-8, guillemets, espaces parasites, champs vides, décimales.
- Typer explicitement et **rejeter avec un motif**, jamais corriger en silence.
- Produire un rapport qualité lisible par un humain.

### Théorie
- Encodages et BOM : pourquoi un en-tête peut commencer par des octets invisibles.
- CSV : séparateur, guillemets, échappement, sauts de ligne dans les champs.
- Typage : entier, décimal, booléen, nul — et le piège du zéro qui remplace un vide.
- Idempotence : relancer l'ingestion doit produire exactement le même résultat.
- Principe *fail loud* : une anomalie non gérée est un bug, pas une tolérance.

### Sources
- **RFC 4180** — grammaire CSV.
- **Unicode FAQ BOM** — pourquoi `\ufeff` apparaît en tête de fichier.
- **Python :** [module `csv`](https://docs.python.org/3/library/csv.html).
- **DuckDB :** [lecture CSV](https://duckdb.org/docs/data/csv/overview) — options de typage et d'échappement.
- **12 Factor App :** [principe *build, release, run*](https://12factor.net/build-release-run).

### Exercices / auto-vérifications
- Compter les lignes de chaque fichier et comparer au manifeste.
- Localiser les 653 lignes « Illimité » et vérifier que `data_gb` est vide **et** `data_display` renseigné.
- Fabriquer cinq fichiers cassés (BOM, champ vide, prix négatif, devise inconnue, doublon de SKU) et vérifier que chacun est rejeté avec un motif lisible.
- Relancer l'ingestion deux fois et comparer les rapports.

### Critère de sortie
5 056 lignes chargées, zéro rejet non expliqué, `quality.json` généré, ingestion idempotente.

---

## Jalon 2 — Modélisation analytique et SQL

### Objectifs
- Concevoir un **modèle en étoile minimal** : une table de faits, des dimensions.
- Comprendre pourquoi un moteur **colonnaire** est adapté aux agrégats.
- Maîtriser `GROUP BY`, `COUNT`, `COUNT(colonne)`, `AVG`, `MIN/MAX`, `HAVING`.
- Comprendre la **sémantique des NULL** dans les agrégats.

### Théorie
- OLTP vs OLAP : lignes vs colonnes, écriture unitaire vs balayage massif.
- Pourquoi `COUNT(*)` et `COUNT(data_gb)` ne répondent pas à la même question.
- `AVG` ignore les NULL — c'est la clé du traitement de l'illimité.
- Table de faits / dimensions : le vocabulaire que MBS attend d'un profil data.
- `WHERE` filtre les lignes, `HAVING` filtre les groupes.

### Sources
- **DuckDB :** [pourquoi DuckDB](https://duckdb.org/why_duckdb), [introduction au SQL](https://duckdb.org/docs/sql/introduction), [fonctions d'agrégation](https://duckdb.org/docs/sql/aggregates).
- **PostgreSQL :** [fonctions d'agrégation et NULL](https://www.postgresql.org/docs/current/functions-aggregate.html).
- **Mode SQL Tutorial :** [agrégations](https://mode.com/sql-tutorial/sql-aggregate-functions/).
- **Designing Data-Intensive Applications** (Kleppmann), chapitre 3 — stockage colonnaire.

### Exercices / auto-vérifications
- Écrire les six requêtes à la main, puis les faire tourner sur le jeu doré de 10 lignes.
- Comparer chaque résultat aux valeurs calculées au crayon au jalon 0.
- Écrire une requête qui prouve que `data_gb` est nul exactement quand `data_display = Illimité`.
- Vérifier que la somme des cartes par fournisseur égale le total.

### Critère de sortie
Les six KPI sortent juste sur le jeu doré **et** sur les données réelles, et tu peux expliquer chaque clause.

---

## Jalon 3 — Rigueur statistique

### Objectifs
- Distinguer moyenne, médiane, quartiles, et savoir **quand chacun ment**.
- Choisir explicitement un **dénominateur** et l'afficher.
- Comprendre l'effet d'un outlier sur une moyenne.
- Mesurer un écart **relatif** entre deux offres comparables.

### Théorie
- Moyenne vs médiane : asymétrie de la distribution des prix.
- Quartiles et lecture d'une dispersion sans se faire piéger par les extrêmes.
- Biais de composition : une moyenne globale peut contredire toutes les moyennes par groupe.
- Pourcentage de quoi : 12,9 % de 5 056, pas 12,9 % « des cartes vendues ».
- Arrondis : où arrondir, et pourquoi ne jamais arrondir avant l'agrégat.

### Sources
- **Think Stats** (Allen Downey, gratuit) — [greenteapress.com](https://greenteapress.com/wp/think-stats-2e/).
- **OpenIntro Statistics** — [openintro.org](https://www.openintro.org/book/os/).
- **Khan Academy :** moyenne, médiane, quartiles.
- **FT Visual Vocabulary** — [github.com/Financial-Times/chart-doctor](https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary) (prépare le jalon 4).

### Exercices / auto-vérifications
- Calculer la moyenne de data avec et sans les illimitées. Expliquer en une phrase pourquoi 12,62 Go est faux.
- Calculer à la main les quartiles de dix prix, puis vérifier avec le moteur.
- Vérifier l'écart médian de prix entre fournisseurs sur cinq bundles identiques.
- Formuler chaque KPI en une phrase du type « sur [population], [calcul], en [unité] ».

### Critère de sortie
Tu peux défendre chaque chiffre du dashboard en 30 secondes, sans notes, y compris le choix du dénominateur.

---

## Jalon 4 — Visualisation et hiérarchie

### Objectifs
- Choisir un graphique **par question**, pas par esthétique.
- Construire une hiérarchie visuelle : les 6 KPI d'abord, le détail ensuite.
- Rendre la page lisible sur un téléphone de 360 px.
- Respecter contraste et daltonisme.

### Théorie
- Encodages perceptifs : position > longueur > angle > aire > couleur.
- Pourquoi un camembert à 18 parts est illisible ; quand une barre horizontale triée gagne.
- Hiérarchie : taille, graisse, espace, ordre de lecture.
- Contraste WCAG, palettes adaptées au daltonisme, rôle du gris.
- Densité utile : enlever tout ce qui ne porte pas d'information.

### Sources
- **FT Visual Vocabulary** — choix du graphique par intention.
- **Data Viz Catalogue** — [datavizcatalogue.com](https://datavizcatalogue.com).
- **Storytelling with Data** (Cole Nussbaumer Knaflic) — hiérarchie et annotation.
- **WCAG 2.2 :** [quick reference](https://www.w3.org/WAI/WCAG22/quickref/) — contraste et alternatives.
- **ColorBrewer :** [colorbrewer2.org](https://colorbrewer2.org) — palettes sûres.
- **The Truthful Art** (Alberto Cairo) — ne pas mentir avec un axe.

### Exercices / auto-vérifications
- Associer chaque KPI à un type de graphique et **écrire la justification** en une ligne.
- Dessiner trois maquettes papier, choisir, jeter les deux autres.
- Afficher la maquette à 360 px de large et vérifier que rien ne déborde.
- Faire lire la page à quelqu'un qui ne connaît pas le sujet : comprend-il le chiffre principal en 5 secondes ?

### Critère de sortie
Une maquette validée, chaque graphique justifié par écrit, lisible sur mobile.

---

## Jalon 5 — Génération statique et déploiement

### Objectifs
- Séparer **données** (`metrics.json`) et **présentation** (gabarit).
- Générer une page à partir des métriques, sans chiffre saisi à la main.
- Publier par CI, avec un lien stable et sans serveur.
- Comprendre ce qui se passe quand le build échoue.

### Théorie
- Génération statique : le HTML est un **artefact de build**, pas un document édité.
- CI/CD : déclencheur, étapes, artefact, permissions, environnement.
- Hébergement statique : cache, HTTPS, URL stable, absence de cold start.
- Pourquoi un lien qui s'endort est un risque le jour du rendu.

### Sources
- **GitHub Pages :** [documentation](https://docs.github.com/en/pages).
- **GitHub Actions :** [workflow, artefacts, déploiement](https://docs.github.com/en/actions).
- **Jamstack :** [jamstack.org](https://jamstack.org) — principes.
- **12 Factor App :** [build, release, run](https://12factor.net/build-release-run).
- **web.dev :** [Core Web Vitals](https://web.dev/vitals/).

### Exercices / auto-vérifications
- Déployer une page blanche, l'ouvrir depuis un téléphone en 4G.
- Casser volontairement le build et vérifier que le déploiement est bloqué.
- Modifier une valeur de `metrics.json` et vérifier que la page change sans toucher au HTML.
- Mesurer le temps de chargement et le poids de la page.

### Critère de sortie
Un lien public s'ouvre sur mobile en moins de deux secondes, et un push rebuild automatiquement.

---

## Jalon 6 — Tests, invariants et reproductibilité

### Objectifs
- Tester une chaîne de données, pas seulement des fonctions.
- Construire un **jeu doré** dont chaque valeur est calculée à la main.
- Écrire des **invariants** qui doivent toujours être vrais.
- Faire échouer la CI quand un KPI dérive.

### Théorie
- Pyramide des tests appliquée à la data : unitaire, intégration, acceptation.
- Test de propriété / invariant vs test d'exemple.
- Golden master : comparer une sortie complète, relire le diff.
- Test ≠ monitoring : le test protège le build, le monitoring protège la production.
- Reproductibilité : même entrée + même version = même sortie.

### Sources
- **pytest :** [documentation](https://docs.pytest.org).
- **Great Expectations :** tests de données et rapports.
- **dbt tests :** unicité, non-nullité, relations.
- **Approval Tests :** [approvaltests.com](https://approvaltests.com) — golden master.
- **Data Pipelines Pocket Guide** (Densmore) — industrialisation.

### Exercices / auto-vérifications
- Écrire dix lignes dorées et vérifier que les six KPI tombent exactement dessus.
- Casser un prix dans les données et vérifier qu'un test échoue **et** que la CI bloque.
- Reconstruire depuis un clone propre et comparer les `metrics.json` octet par octet.
- Chronométrer un build complet : doit rester sous une minute.

### Critère de sortie
Clone propre + une commande = mêmes chiffres. Un écart de KPI rend la CI rouge.

---

## Jalon 7 — SEO : comprendre avant d'écrire

### Objectifs
- Lire une SERP et en déduire une **intention** et un **format**.
- Analyser cinq concurrents et repérer le vide à combler.
- Décider d'une longueur **argumentée**, pas arbitraire.
- Connaître les fondamentaux techniques : title, meta, H1, maillage, données structurées.

### Théorie
- Intention de recherche : informationnelle, commerciale, transactionnelle.
- Fonctionnalités de SERP : extrait enrichi, People Also Ask, pack local, AI Overviews.
- E-E-A-T : expérience, expertise, autorité, fiabilité — et pourquoi les tarifs doivent être sourcés et datés.
- Couverture sémantique : entités et questions à traiter, pas répétition de mots-clés.
- JSON-LD `Article` et `FAQPage` : ce que Google en fait réellement (les résultats enrichis FAQ sont restreints depuis 2023 — le balisage sert la compréhension, pas la décoration).

### Sources
- **Google Search Essentials :** [developers.google.com/search/docs/essentials](https://developers.google.com/search/docs/essentials).
- **Contenu utile :** [creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- **Guide SEO de démarrage :** [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).
- **Quality Rater Guidelines :** [guidelines.raterhub.com](https://guidelines.raterhub.com).
- **Données structurées :** [Article](https://developers.google.com/search/docs/appearance/structured-data/article), [FAQPage](https://developers.google.com/search/docs/appearance/structured-data/faqpage).
- **Search Console :** [search.google.com/search-console](https://search.google.com/search-console/about) ; **PageSpeed :** [pagespeed.web.dev](https://pagespeed.web.dev).

### Exercices / auto-vérifications
- Relever pour cinq concurrents : longueur, plan H2, présence de tableaux, FAQ, angle, date de mise à jour.
- Lister dix questions issues de « People Also Ask » et des suggestions Google.
- Écrire le brief : intention, promesse, plan, longueur **justifiée par la SERP**, sources à citer.
- Vérifier trois affirmations tarifaires sur des pages officielles de compagnies de croisière, avec date.

### Critère de sortie
Un brief d'une page, un plan H2/H3 complet, une décision de longueur défendable.

---

## Jalon 8 — Rédaction et publication

### Objectifs
- Écrire pour un humain pressé **et** pour Google.
- Répondre dès les 50 premiers mots, puis développer.
- Construire un tableau comparatif honnête et des visuels utiles.
- Publier, baliser, soumettre à l'indexation.

### Théorie
- Pyramide inversée, scannabilité, phrases courtes, sous-titres porteurs d'information.
- Réponse directe sous le H1 : le passage que Google peut extraire.
- Tableau comparatif : critères en lignes, options en colonnes, pas de note inventée.
- Maillage interne : lier vers des pages existantes et pertinentes, pas vers tout.
- Publication MkDocs : front matter, slug, canonical, Open Graph, build.

### Sources
- **Google Search Central** — guides contenu et structuré.
- **They Ask, You Answer** (Marcus Sheridan) — répondre aux vraies questions.
- **Ahrefs / Backlinko** — guides pratiques sur la structure d'article.
- **MkDocs Material :** [documentation](https://squidfunk.github.io/mkdocs-material/) — front matter, méta, navigation.
- **Rich Results Test :** [search.google.com/test/rich-results](https://search.google.com/test/rich-results).

### Exercices / auto-vérifications
- Écrire l'introduction en 50 mots, la relire à voix haute.
- Rédiger le tableau comparatif eSIM / WiFi bord / roaming avec des sources datées.
- Faire valider les données structurées par le Rich Results Test.
- Passer Lighthouse mobile : performance, accessibilité, SEO.
- Demander l'indexation dans Search Console et noter la date.

### Critère de sortie
Article en ligne, mobile propre, données structurées valides, indexation demandée.

---

## Jalon 9 — Rendu et défense

### Objectifs
- Raconter le travail : décisions, preuves, reproductibilité.
- Écrire un README qu'un inconnu peut suivre.
- Rédiger la note d'usage de l'IA avec honnêteté.
- Tenir un oral de deux minutes sur chaque choix.

### Théorie
- Narration technique : problème, contrainte, décision, preuve.
- Ce qu'un relecteur cherche : le lien, les chiffres, la méthode, la limite.
- Divulgation de l'IA : ce qui a été délégué, ce qui a été vérifié, ce qui a été refusé.
- Défense : anticiper les trois questions les plus dures (illimité, dénominateur, lien).

### Sources
- **Make a README :** [makeareadme.com](https://www.makeareadme.com).
- **Google :** [documentation des bonnes pratiques de README](https://google.github.io/styleguide/) (section documentation de projet).
- **Staff Engineer** (Will Larson) — écrire pour convaincre, pas pour impressionner.

### Exercices / auto-vérifications
- Faire reconstruire le dashboard par quelqu'un d'autre à partir du README seul, en moins de dix minutes.
- Expliquer l'illimité en 30 secondes à une personne non technique.
- Relire l'e-mail à voix haute : cinq blocs, pas de roman.
- Se poser les trois questions dures et répondre sans notes.

### Critère de sortie
E-mail envoyé le jeudi 29, dossier relu à froid le lendemain matin.

---

## Annexe — Bonus

> Les bonus ne comptent que si **tout le socle est parfait**. Ils sont hors planning principal.

### B1 — Comparateur par destination *(le plus fort)*
- Sélecteur de destination → offre la moins chère par fournisseur.
- Écart de prix pour un bundle équivalent : 1 033 bundles, écart médian 13,4 %.
- C'est le KPI qui prouve la compréhension du métier de MBS.

### B2 — Visuels maison
- Hero, schéma « mer vs escale », carte des zones.
- L'auteur est illustrateur : avantage différenciant qu'aucun autre candidat n'aura.
- Sources : documentation MkDocs Material pour l'intégration, WCAG pour les alternatives textuelles.

### B3 — Qualité de page
- Lighthouse ≥ 95 partout, contraste AA, navigation clavier.
- Sources : web.dev, WCAG 2.2.

---

## Sources incontournables

### Données et qualité
- [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180) — format CSV.
- [Unicode FAQ BOM](https://unicode.org/faq/utf_bom.html).
- [Great Expectations](https://greatexpectations.io) — contrôles de qualité.
- [dbt tests](https://docs.getdbt.com/docs/build/tests).
- *DAMA-DMBOK* — dimensions de la qualité.

### SQL et stockage analytique
- [DuckDB](https://duckdb.org/docs/) — documentation complète.
- [PostgreSQL — agrégats](https://www.postgresql.org/docs/current/functions-aggregate.html).
- [Mode SQL Tutorial](https://mode.com/sql-tutorial/).
- *Designing Data-Intensive Applications* — chapitre stockage.

### Statistiques
- [Think Stats](https://greenteapress.com/wp/think-stats-2e/) — gratuit.
- [OpenIntro Statistics](https://www.openintro.org/book/os/).
- Khan Academy — moyenne, médiane, quartiles.

### Visualisation
- [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary).
- [Data Viz Catalogue](https://datavizcatalogue.com).
- [WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/), [ColorBrewer](https://colorbrewer2.org).
- *Storytelling with Data*, *The Truthful Art*.

### Ingénierie et déploiement
- [GitHub Pages](https://docs.github.com/en/pages), [GitHub Actions](https://docs.github.com/en/actions).
- [12 Factor App](https://12factor.net).
- [pytest](https://docs.pytest.org), [Approval Tests](https://approvaltests.com).
- [web.dev — Core Web Vitals](https://web.dev/vitals/).

### SEO
- [Google Search Essentials](https://developers.google.com/search/docs/essentials).
- [Contenu utile](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- [Quality Rater Guidelines](https://guidelines.raterhub.com).
- [Données structurées Article](https://developers.google.com/search/docs/appearance/structured-data/article) et [FAQPage](https://developers.google.com/search/docs/appearance/structured-data/faqpage).
- [Search Console](https://search.google.com/search-console/about), [PageSpeed Insights](https://pagespeed.web.dev), [Rich Results Test](https://search.google.com/test/rich-results).
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

---

## Notes pour le README du projet

Le README est un livrable évalué, pas une formalité. Il devra contenir :

- le **lien** du dashboard et celui du repo ;
- les **six chiffres clés** avec leur définition ;
- les **six décisions** (renvoi vers `DECISIONS.md`) ;
- la **commande unique** qui reconstruit tout depuis les CSV bruts ;
- la **note d'usage de l'IA** : ce qui a été délégué, ce qui a été vérifié, **où l'IA s'est trompée** ;
- une section **limites connues** : ce que le dashboard ne dit pas.

> **Rappel :** tu restes entièrement responsable des chiffres publiés. En entretien, tu dois pouvoir expliquer pourquoi 14,49 Go et pas 12,62, et pourquoi le seuil est strict.
