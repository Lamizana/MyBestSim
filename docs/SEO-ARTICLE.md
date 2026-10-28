# Référencement de l'article croisière

Ce document décrit la stratégie SEO de la page
`https://lamizana.github.io/MyBestSim/` : ce qui a été mis en place, pourquoi,
et comment le maintenir.

Il couvre le SEO technique et éditorial. Il ne garantit ni une position dans
Google, ni l'affichage des rich results : ce sont des signaux, pas des
promesses.

## Pourquoi le référencement

La page doit pouvoir être trouvée sur des requêtes comme « eSIM croisière »,
« internet en croisière » ou « eSIM Méditerranée ». Le référencement sert
quatre objectifs :

1. **Être indexable** : une URL canonique, un `robots.txt` ouvert et un
   sitemap valide.
2. **Être comprise** : un titre, une description, une hiérarchie de titres et
   des données structurées qui décrivent l'article.
3. **Être crédible** : des sources, un auteur identifiable, des dates et une
   divulgation d'affiliation.
4. **Être agréable à ouvrir** : des images légères, pas de JavaScript, un
   affichage mobile correct.

Le SEO ne se limite donc pas aux balises `<meta>`. Le contenu, la vitesse et
la cohérence entre le visible et le balisé comptent autant.

## Ce que j'ai fait

| Fichier | Rôle |
|---|---|
| `article/internet-croisiere-esim.md` | titre, description, dates, FAQ, images responsive |
| `article/template.html` | `lang`, canonical, Open Graph, préchargement, hero |
| `article/build.py` | JSON-LD, `scope`, sitemap, dates, FAQ |
| `article/style.css` | mise en page, responsive, composants |
| `article/images/` | variantes 760/900, avatar, favicon, logo éditeur |

### Métadonnées

- `<title>` de **53 caractères** :
  « Internet en croisière : quelle eSIM choisir en 2026 ? »
- Meta description de **151 caractères**, avec le mot-clé et le bénéfice.
- `lang="fr-FR"`, `canonical` auto-référente, `robots: index, follow`.
- Open Graph : type, titre, description, URL, locale.
- `article:published_time` et `article:modified_time`.
- Pas d'`og:image` : choix assumé, voir plus bas.

### Structure et contenu

- Un seul `<h1>`, neuf `<h2>`, cinq `<h3>`.
- Sommaire généré depuis les titres, ancres vérifiées.
- 11 liens vers MyBestSim, tous en 200 au moment de l'audit.
- Sources externes : GSMA, Starlink Maritime, Carnival, Royal Caribbean,
  Apple et Google.
- 2 figures avec `figcaption`, 3 tableaux avec `<caption>`.
- Divulgation d'affiliation visible.
- Date de publication et date de mise à jour affichées.

### Données structurées

Trois blocs JSON-LD sont générés par `build.py` :

| Type | Contenu |
|---|---|
| `Article` | headline, description, dates, image 4:3 + 16:9, auteur, éditeur, logo |
| `FAQPage` | les 8 questions/réponses visibles |
| `BreadcrumbList` | Accueil › Blog › Croisière |

L'auteur et l'éditeur sont `Organization` (MyBestSim), avec `sameAs` vers
Instagram, Facebook et YouTube. Le logo éditeur est un PNG **600 × 60**.

### Images

- Hero : `mbs_intro_02`, variantes **760** et **1400** px, `srcset`,
  `sizes`, `fetchpriority="high"`.
- Schémas : `esim-croisiere-mer-port` et `esim-croisiere-itineraire`,
  variantes **900** et **1400** px, `loading="lazy"`, `decoding="async"`,
  légende visible.
- Toutes les images ont un `alt` descriptif, une largeur et une hauteur.
- Avatar : 200 × 200, affiché 100 × 100, `loading="lazy"`.
- Favicon : 48 × 48.
- Le logo éditeur est distinct du favicon et de l'avatar.

### Technique

- CSS externe, **9 266 octets** (≈ 9,0 Kio), une seule requête.
- Aucun JavaScript.
- `preload` du hero avec `imagesrcset` pour le LCP.
- `scope="col"` sur les 10 en-têtes de tableau.
- Sitemap avec `lastmod`, `robots.txt` ouvert.
- Page servie par GitHub Pages, cache de 10 minutes.

## Pourquoi ces choix

### Titre et description

Le titre place le sujet et l'année dès le début. Il reste sous la limite
d'affichage (~60 caractères). La description tient en 151 caractères, ajoute
« 2026 » et conserve les trois angles : itinéraire, roaming, prix.

Le title et le H1 sont volontairement alignés. Le H1 reste le titre
éditorial ; le title peut évoluer pour le CTR sans casser la page.

### Une seule page, une seule URL

Le site ne contient qu'un article. La racine `/MyBestSim/` est donc l'URL
canonique, et le sitemap ne déclare qu'une URL. C'est cohérent, mais l'URL ne
contient pas le mot-clé. Un chemin `/internet-cruisiere-esim/` serait
meilleur ; il impliquerait une redirection et un nouveau canonical, donc il
est laissé pour plus tard.

**Décision retenue : canonical auto-référente.** Cette page est une version
de démonstration autonome, pas une copie publiée sur `mybestsim.com`. Elle ne
cherche donc pas à consolider ses signaux vers le site officiel. Si l'article
est un jour publié sur `mybestsim.com`, il faudra pointer `canonical`,
`og:url`, `mainEntityOfPage` et le dernier item du `BreadcrumbList` vers
l'URL officielle, puis retirer ou canonicaliser cette version GitHub.

### Pourquoi pas d'OG image

L'OG image a été retirée pour ne pas diffuser une carte visuelle obsolète.
Conséquence : un partage LinkedIn ou WhatsApp affiche le titre et la
description, sans vignette. Cela ne pénalise pas le classement Google, mais
réduit le taux de clic social.

Le JSON-LD garde des images : le hero et son recadrage 16:9. Ce ne sont pas
des OG images, ce sont des données pour Google.

### Pourquoi deux formats d'image dans `Article`

Google recommande plusieurs ratios pour les articles. Le hero fournit un 4:3
naturel (1400 × 1045) et un 16:9 recadré (1400 × 788). Les deux dépassent
largement le minimum de 50 000 pixels.

### FAQPage malgré les restrictions

Google limite l'affichage des FAQ enrichies aux sites de santé et
d'administration. Le balisage reste utile pour décrire précisément le contenu
et les questions visibles. Il ne faut donc pas promettre un rich result FAQ.

### Auteur `Organization`

Le bloc visible présente MyBestSim, pas une personne. Le JSON-LD utilise donc
`Organization`, avec `sameAs`. Inventer un auteur `Person` aurait été plus
risqué qu'utile. Un auteur nommé, avec bio et lien LinkedIn, serait un vrai
gain d'E-E-A-T ; ce n'est pas fait ici.

### Images responsive

Le hero est affiché au maximum à 760 px. Servir 1400 px sur mobile gaspille
des octets. Les variantes 760/900 réduisent le poids et le `srcset` laisse le
navigateur choisir selon la densité de l'écran et la largeur.

Les originaux 1400 px restent pour les écrans haute densité et le JSON-LD.

### Légendes et sources

Les deux schémas ont une `figcaption` visible, et les trois tableaux une
`<caption>`. Cela donne un contexte textuel aux images et aux tableaux, utile
pour la recherche d'images, les lecteurs d'écran et les extraits enrichis.

Les politiques internet de Carnival et Royal Caribbean sont liées directement
dans les sources. Les guides d'installation Apple et Google sont également
cités pour la procédure eSIM. Une affirmation sur les compagnies de croisière
ou sur une manipulation technique sans lien officiel est plus faible qu'une
source vérifiable.

### Accessibilité et SEO

`scope="col"`, les `alt`, le lien d'évitement, le focus visible et les
contrastes ne sont pas que des cases SEO : ils rendent la page lisible par
les robots et par les lecteurs d'écran. Le référencement profite de cette
cohérence.

### Pas de JavaScript

La page est statique. Le navigateur ne télécharge que le HTML, le CSS, les
polices et les images. C'est le meilleur compromis pour une page de contenu
et cela évite les problèmes d'indexation des contenus injectés.

## Vérifications

Commandes utilisées :

```bash
make article
make test
make lint
```

Résultats attendus :

- 3 blocs JSON-LD valides ;
- 8 questions dans `FAQPage` ;
- 3 niveaux dans `BreadcrumbList` ;
- 10/10 `<th scope="col">` ;
- 3 `<caption>` et 2 `<figcaption>` ;
- 5 images, 0 sans `alt` ;
- 0 ancre cassée, 0 identifiant dupliqué ;
- 11 liens MyBestSim en 200 ;
- 88 tests, `ruff` propre.

L'audit compare aussi la page locale et la version en ligne : les deux
exposent le même title, la même description, le même canonical et les mêmes
données structurées.

## Limites connues

- URL racine sans mot-clé.
- Pas d'OG image : pas de vignette sociale.
- Auteur `Organization`, pas de personne nommée.
- FAQ enrichies non garanties.
- Search Console : le sitemap est prêt, mais son envoi et le suivi de
  couverture restent manuels.
- Le lien GSMA renvoie 403 aux requêtes automatisées (`curl`) ; il reste à
  vérifier manuellement dans un navigateur.
- Certains contrastes restent à renforcer pour viser 4,5:1 : survol des liens,
  bouton CTA, lien d'évitement et nom de l'auteur.
- GitHub Pages met le CSS en cache 10 minutes : après un déploiement, faire
  un rechargement forcé avant de conclure à un bug.

## Maintenance

### Changer le titre ou la description

1. Modifier le front matter de `article/internet-croisiere-esim.md`.
2. Modifier le H1 dans le même fichier pour rester cohérent.
3. Lancer `make article`.
4. Vérifier la longueur du title (≤ 60) et de la description (≤ 155).

Le title alimente aussi `og:title`, `twitter:title` et `headline` dans le
JSON-LD. Le H1 n'est pas généré depuis le front matter : il faut le changer
à la main.

### Changer une image

1. Déposer l'original dans `article/images/`.
2. Générer la variante affichée (760 ou 900 px).
3. Mettre à jour le `src`, le `srcset` et le `sizes`.
4. Mettre à jour `IMAGE_ARTICLE` dans `build.py` si c'est le hero.
5. Vérifier le JSON-LD et l'`alt`.

### Changer la date

`date` est la publication, `updated` la dernière modification. Les deux
alimentent le JSON-LD, le sitemap et la ligne « Mis à jour le ». Ne pas
modifier `_site/` à la main : il est régénéré.

### Après un déploiement

1. Attendre la fin du workflow Pages.
2. Recharger sans cache.
3. Vérifier le title, le canonical et les JSON-LD.
4. Soumettre le sitemap dans Search Console si l'URL a changé.

## Fichiers liés

- `article/internet-croisiere-esim.md` : source éditoriale.
- `article/template.html` : en-tête et structure HTML.
- `article/build.py` : génération et données structurées.
- `article/style.css` : styles de la page.
- `docs/FONCTIONS.md` : documentation du reste du projet.
