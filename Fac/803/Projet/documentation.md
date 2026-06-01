# Documentation du projet – Analyse du CAC40 (2010-2020)
**Cocu Ethan — INFO0803 Visualisation des données**

---

## 1. Présentation générale

Le script `analyse_cac40.R` analyse les données boursières de 38 entreprises du CAC40
sur la période 2010-2020. Il produit **13 figures** organisées en deux grandes parties :

- **(1) à (4)** : chargement et préparation des données
- **(Fig. 1 à 13)** : visualisations

Toutes les visualisations utilisent `ggplot2`, en suivant la grammaire des graphiques
vue en **CM2** et pratiquée en **TP3, TP4, TP5**.

---

## 2. Préparation des données (sections 1 à 4)

### (1) Chargement — `read.csv()`, `as.Date()`, `trimws()`

Le fichier `data/preprocessed_CAC40.csv` contient les cours journaliers (ouverture,
clôture, haut, bas, volume) de 38 entreprises du CAC40 de 2010 à avril 2020.

```r
donnees_brutes <- read.csv("data/preprocessed_CAC40.csv", stringsAsFactors = FALSE)
donnees_brutes$Date <- as.Date(donnees_brutes$Date)
```

`read.csv()` et `as.Date()` ont été utilisés dans **CM1** (fichier `ozone.txt`) et
dans **TP2** (fichier `taches_solaires_date.csv`) pour importer et formater des données
avec des colonnes de dates.

---

### (2) Nettoyage des noms — boucle `for`, indexation logique

Les noms d'entreprises dans le fichier brut sont trop longs (ex. `"LVMH Moet Hennessy
Louis Vuitton"`). On les remplace par des noms courts via un vecteur nommé et une boucle.

```r
noms_courts <- c("LVMH Moet Hennessy Louis Vuitton" = "LVMH", ...)
for (ancien in names(noms_courts)) {
  donnees_brutes$Entreprise[donnees_brutes$Entreprise == ancien] <- noms_courts[ancien]
}
```

L'indexation logique sur un `data.frame` (`df$col[condition] <- valeur`) est un
fondamental de R vu dès **CM1** et **TP1/TP2**.

---

### (3) Classification sectorielle — `data.frame()`, `left_join()`, `rep()`

On crée manuellement un tableau de correspondance entreprise → secteur, puis on le
joint aux données avec `left_join()` de **dplyr**.

```r
secteurs <- data.frame(Entreprise = c(...), Secteur = c(rep("Finance", 4), ...))
cac40 <- left_join(cac40, secteurs, by = "Entreprise")
```

`rep()` est utilisé en **TP1** (construction de vecteurs). `left_join()` fait partie
du **tidyverse** introduit en **TP4/TP5** avec `dplyr`.

---

### (4) Rendements journaliers — `group_by()`, `mutate()`, `lag()`

Le rendement journalier est la variation relative du cours de clôture entre deux séances
consécutives, exprimée en pourcentage :

```
Rendement(t) = (Cloture(t) / Cloture(t-1) - 1) × 100
```

```r
cac40 <- cac40 %>%
  arrange(Entreprise, Date) %>%
  group_by(Entreprise) %>%
  mutate(Rendement = (Cloture / lag(Cloture) - 1) * 100) %>%
  ungroup()
```

Le pipeline `%>%` et les verbes `arrange`, `group_by`, `mutate` font partie de **dplyr**,
vu en **TP4 et TP5**. `lag()` permet d'accéder à la valeur précédente dans un groupe.

---

## 3. Visualisations

---

### Figure 1 — Évolution des cours normalisés (base 100)

**Technique de normalisation : Base 100**

Chaque cours est divisé par sa première valeur et multiplié par 100. Cela permet de
comparer des actions dont les prix absolus sont très différents (Renault à ~10€ vs
LVMH à ~150€ en 2010) sur une même échelle.

```
Prix_norm(t) = Cloture(t) / Cloture(t_0) × 100
```

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_line()` | Tracé des séries temporelles |
| `geom_hline()` | Ligne de référence à 100 |
| `geom_vline()` | Marqueur de l'événement COVID |
| `annotate("text")` | Annotation textuelle sur le graphique |
| `geom_text_repel()` | Labels non chevauchants en bout de courbe (package `ggrepel`) |
| `scale_x_date()` | Formatage de l'axe temporel |

**Références cours :**
- `geom_line()` → **CM2** (tracé de courbes), **TP3** (exercice 3 sinus/cosinus)
- `geom_hline()` / `geom_vline()` → **TP3** (exercice 3, ajout de droites horizontales)
- `annotate()` → **CM2** (ajout de texte sur un graphique)
- `scale_x_date()` → **TP2** (gestion des axes de date pour les taches solaires)

---

### Figure 2 — Heatmap des rendements annuels

**Type de graphique : Heatmap (carte de chaleur)**

Pour chaque couple (entreprise, année), on calcule le rendement annuel :

```
Rend_annuel = (dernier cours / premier cours de l'année - 1) × 100
```

La couleur encode la valeur : rouge = perte, blanc = neutre, vert = gain.

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_tile()` | Grille de rectangles colorés |
| `scale_fill_gradient2()` | Palette divergente centrée sur 0 |
| `geom_text()` + `sprintf()` | Valeurs numériques dans chaque case |
| `theme_minimal()` | Thème épuré pour la lisibilité |

**Références cours :**
- `geom_tile()` → **CM2** (liste des `geom_*` disponibles)
- `scale_fill_gradient2()` → **CM2** (section *Scales*, contrôle des couleurs)
- `summarise()` avec `first()` / `last()` → **TP4/TP5** (agrégations avec `dplyr`)
- `factor()` pour ordonner l'axe Y → **TP4** (variable `mois` ordonnée)

---

### Figure 3 — Distribution des rendements par secteur (violin + boxplot)

**Type de graphique : Violin plot superposé à un boxplot**

Le violin plot montre la forme complète de la distribution (densité de probabilité).
Le boxplot interne donne la médiane, les quartiles et les valeurs atypiques.
Les secteurs sont ordonnés par volatilité croissante (écart-type des rendements).

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_violin()` | Distribution en forme de violon |
| `geom_boxplot()` | Boîte à moustaches |
| `coord_flip()` | Rotation horizontale du graphique |
| `scale_fill_manual()` | Palette de couleurs personnalisée |

**Références cours :**
- `geom_boxplot()` → **CM1** (`boxplot()` en base R), **TP4** (boxplots de l'ozone par mois)
- `coord_flip()` → **CM2** (orientation des graphiques)
- `scale_fill_manual()` → **CM2**, **TP4** (couleurs par modalité)
- Violin plot → **CM2** (liste des `geom_*` mentionnés)

---

### Figure 4 — Profil Risque / Rendement

**Concept : Volatilité annualisée**

La volatilité d'une action est mesurée par l'écart-type de ses rendements journaliers.
Pour l'annualiser, on la multiplie par √252 (nombre de séances de bourse par an) :

```
Volatilite_annualisee = sigma_journalier × sqrt(252)
```

Chaque point représente une entreprise. La position dans le plan (risque, rendement)
révèle son profil : idéalement on cherche un point en haut à gauche (fort rendement,
faible risque).

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_point()` | Un point par entreprise |
| `geom_text_repel()` | Labels sans chevauchement |
| `geom_hline()` | Ligne y = 0 (frontière gain/perte) |
| `scale_color_manual()` | Couleur par secteur |

**Références cours :**
- `geom_point()` → **CM2**, **TP3** (nuages de points), **TP4** (nuage avec couleur par région)
- `sd()` / `sqrt()` → **TP1** (calculs statistiques de base)
- Notion d'écart-type → **TP1** (exercices sur les distributions et la variance)

---

### Figure 5 — Matrice de corrélation

**Concept : Corrélation de Pearson**

Le coefficient de corrélation r ∈ [-1, 1] mesure la linéarité de la relation entre
les rendements de deux actions. On calcule la matrice 38×38 avec `cor()`.

Les actions sont triées par secteur pour faire apparaître les blocs de corrélation
intra-sectorielle (les actions du même secteur tendent à évoluer ensemble).

**Fonctions ggplot2 / R utilisées :**

| Fonction | Rôle |
|----------|------|
| `pivot_wider()` | Passage du format long au format large |
| `cor()` | Calcul de la matrice de corrélation |
| `as.table()` + `as.data.frame()` | Passage en format long pour ggplot |
| `geom_tile()` | Heatmap de la matrice |
| `scale_fill_gradient2()` | Palette divergente [-1, 1] |

**Références cours :**
- `cor()` → notion de corrélation abordée en **TP3** (régression) et **TP4** (covariables)
- `pivot_wider()` / `pivot_longer()` → **TP5** (manipulation de données avec tidyr)
- `geom_tile()` → **CM2** (catalogue des `geom_*`)

---

### Figure 6 — Impact de la crise COVID-19

**Même normalisation base 100 que la Figure 1**, appliquée uniquement sur l'année 2020.
On calcule ensuite la **moyenne de l'indice normalisé par secteur** pour chaque jour :
cela lisse les fluctuations individuelles et montre la tendance sectorielle.

La ligne verticale du 17 mars 2020 (début du confinement en France) est annotée.

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_line()` | Courbe temporelle par secteur |
| `geom_vline()` + `annotate()` | Événement daté |
| `scale_x_date()` | Axe des dates bimensuel |
| `group_by(Date, Secteur)` + `summarise()` | Moyenne par secteur par jour |

**Références cours :**
- Séries temporelles avec dates → **TP2** (taches solaires, `as.Date()`, `plot()`)
- `geom_vline()` + `annotate()` → **TP3** (ajout de repères sur un graphique)
- `group_by()` + `summarise()` → **TP4/TP5**

---

### Figure 7 — Performance totale 2010-2020

**Type de graphique : Diagramme en barres horizontal (`geom_col` + `coord_flip`)**

La performance totale est le rendement de la première à la dernière séance disponible.
Les barres sont colorées par secteur et les entreprises sont triées du moins bon au
meilleur performeur.

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_col()` | Barres proportionnelles aux valeurs |
| `geom_text()` + `sprintf()` | Étiquettes de pourcentage |
| `coord_flip()` | Barres horizontales |
| `scale_y_continuous(labels = label_percent())` | Axe en % |

**Références cours :**
- `geom_bar()` / `geom_col()` → **CM2**, **TP3** (exercices 1 et 2)
- `coord_flip()` → **CM2**
- `factor()` pour ordonner les barres → **TP4** (variable `mois` ordonnée)

---

### Figure 8 — Évolution de la volatilité annualisée

**Type de graphique : Lignes + points par secteur**

On calcule l'écart-type annualisé des rendements journaliers pour chaque secteur
et chaque année. Le pic spectaculaire de 2020 illustre le choc de volatilité dû
au COVID-19.

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_line()` | Évolution temporelle |
| `geom_point()` | Points sur chaque année |
| `scale_x_continuous(breaks = 2010:2020)` | Axe discret des années |

**Références cours :**
- `geom_line()` + `geom_point()` → **CM2**, **TP3**
- `sd()` → **TP1** (statistiques descriptives)
- `group_by()` + `summarise()` → **TP4/TP5**

---

### Figure 9 — Camembert de la composition sectorielle

**Type de graphique : Diagramme circulaire (camembert)**

En ggplot2, un camembert s'obtient avec `geom_bar(stat = "identity")` suivi de
`coord_polar("y")` qui transforme le repère cartésien en repère polaire :

```r
geom_bar(stat = "identity", width = 1) +
coord_polar("y", start = 0)
```

**Fonctions ggplot2 utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_bar(stat = "identity")` | Barres de hauteur = valeur |
| `coord_polar("y")` | Transformation en repère polaire → camembert |
| `position_stack(vjust = 0.5)` | Labels au centre de chaque part |
| `theme_void()` | Suppression des axes et du fond |

**Références cours :**
- `geom_bar()` → **CM2**, **TP3** (exercice 2, fréquences relatives)
- `coord_polar()` → **CM2** (transformations de coordonnées)
- `theme_void()` → **CM2** (personnalisation des thèmes)

---

### Figure 10 — Histogrammes + loi normale théorique

**Connexion directe avec TP1 et TP4**

On superpose à l'histogramme empirique des rendements la densité de la loi normale
N(μ, σ²) ajustée sur les paramètres empiriques de chaque action. L'écart visible entre
l'histogramme et la courbe rouge révèle les **queues épaisses** (leptokurtose) : les
rendements extrêmes sont plus fréquents que ne le prédit la loi normale.

La densité théorique est générée avec `dnorm()` pour 300 points entre -15% et +15%.

```r
densite_normale <- rend_histo %>%
  group_by(Entreprise) %>%
  summarise(mu = mean(Rendement), sigma = sd(Rendement)) %>%
  rowwise() %>%
  mutate(x = list(seq(-15, 15, length.out = 300)),
         y = list(dnorm(seq(-15, 15, length.out = 300), mu, sigma))) %>%
  unnest(cols = c(x, y))
```

**Fonctions utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_histogram(aes(y = after_stat(density)))` | Histogramme en densité |
| `geom_line()` sur `densite_normale` | Courbe N(μ,σ²) |
| `facet_wrap(~ Entreprise)` | Un panel par entreprise |
| `dnorm(x, mean, sd)` | Densité de la loi normale |

**Références cours :**
- `hist()` avec superposition de `dnorm()` → **TP1** (exercice 4, illustration du TCL)
- `dnorm()` → **TP1** (exercice 2), **TP2** (exercice 2, tracé de densité)
- `geom_histogram()` → **CM2**, **TP3** (exercice 1)
- `facet_wrap()` → **TP3** (exercice 1), **TP4** (exercice 1 et 2)

---

### Figure 11 — Comparaison de trois méthodes de normalisation

**Trois formules sur la même série (cours de clôture de LVMH) :**

| Méthode | Formule | Interprétation |
|---------|---------|----------------|
| **Base 100** | x / x₀ × 100 | Évolution en % depuis le début |
| **Z-score** | (x − μ) / σ | Nombre d'écarts-types par rapport à la moyenne |
| **Min-Max** | (x − min) / (max − min) | Valeur dans l'intervalle [0, 1] |

`pivot_longer()` transforme les trois colonnes en un format long pour `facet_wrap`.

```r
lvmh_norm %>%
  pivot_longer(cols = c(Base100, Zscore, MinMax),
               names_to = "Methode", values_to = "Valeur")
```

**Fonctions utilisées :**

| Fonction | Rôle |
|----------|------|
| `mutate()` | Calcul des trois normalisations |
| `pivot_longer()` | Format large → long |
| `facet_wrap(~ Methode, scales = "free_y")` | Un panel par méthode |
| `labeller = labeller()` | Labels lisibles dans les facettes |

**Références cours :**
- Base 100 → **TP2** (normalisation des séries temporelles)
- Z-score → **TP1** (exercice 4, variable centrée réduite `U = (S - np) / sqrt(np(1-p))`)
- `pivot_longer()` → **TP3/TP5** (passage format long/large)
- `facet_wrap()` → **TP3**, **TP4**

---

### Figure 12 — Régression linéaire entre LVMH et Kering

**Modèle : régression simple par les moindres carrés ordinaires (MCO)**

On modélise le rendement de LVMH en fonction du rendement de Kering :

```
LVMH = a + b × Kering + ε
```

Le coefficient R² mesure la part de variance de LVMH expliquée par Kering.
Un R² = 0.276 signifie que 27.6% des fluctuations de LVMH s'expliquent
par celles de Kering.

```r
modele_lk <- lm(LVMH ~ Kering, data = rend_lk)
r2 <- summary(modele_lk)$r.squared
```

**Fonctions utilisées :**

| Fonction | Rôle |
|----------|------|
| `pivot_wider()` | Une colonne par action |
| `lm(Y ~ X)` | Ajustement du modèle linéaire |
| `summary()$r.squared` | Extraction du R² |
| `geom_smooth(method = "lm", se = TRUE)` | Droite de régression + IC 95% |
| `annotate()` | Affichage du R² sur le graphique |

**Références cours :**
- `lm()` + `geom_smooth(method = "lm")` → **TP3** (exercice 4, régression sur données simulées)
- `se = TRUE` (bande de confiance) → **TP4** (exercice 1, droite avec bande de confiance)
- `annotate()` → **CM2**, **TP3**

---

### Figure 13 — Illustration du Théorème Central Limite (TCL)

**Connexion directe avec TP1, exercice 4**

Le TCL affirme que la moyenne de n variables aléatoires indépendantes de même loi
converge en distribution vers une loi normale quand n → ∞.

**Application aux rendements boursiers :** Le portefeuille équipondéré (moyenne des
rendements de 38 actions) a une distribution :
- **Plus étroite** (variance réduite d'un facteur ~38)
- **Plus proche de la normale** que les actions individuelles

Ce résultat justifie la diversification en finance.

```r
rend_portefeuille <- cac40 %>%
  group_by(Date) %>%
  summarise(Rendement = mean(Rendement, na.rm = TRUE))
```

**Fonctions utilisées :**

| Fonction | Rôle |
|----------|------|
| `geom_density()` | Courbe de densité empirique lissée |
| `group_by(Date)` + `summarise(mean(...))` | Rendement moyen = portefeuille |
| `bind_rows()` | Fusion de plusieurs data.frames |
| `scale_x_continuous(oob = squish)` | Troncature de l'axe |

**Références cours :**
- TCL → **TP1** (exercice 4 : histogrammes de U10, U30, U1000 avec N(0,1) superposée)
- `dnorm()` + `hist()` → **TP1** (superposition densité normale et histogramme)
- `geom_density()` → **CM2** (`geom_density()` listé parmi les `geom_*`)
- `bind_rows()` → **TP4/TP5** (combinaison de tableaux avec dplyr)

---

## 4. Récapitulatif des références par cours

| Technique | Figure(s) | TP/CM |
|-----------|-----------|-------|
| `read.csv()`, `as.Date()` | Prép. (1) | CM1, TP2 |
| Indexation logique, boucle `for` | Prép. (2) | CM1, TP1 |
| `data.frame()`, `left_join()`, `rep()` | Prép. (3) | TP4, TP5 |
| `group_by()`, `mutate()`, `lag()` | Prép. (4) | TP4, TP5 |
| `geom_line()` | 1, 6, 8, 11 | CM2, TP3 |
| `geom_hline()`, `geom_vline()` | 1, 4, 6 | TP3 |
| `annotate()` | 1, 6, 12 | CM2, TP3 |
| `geom_text_repel()` | 1, 4 | ggrepel (complément CM2) |
| `scale_x_date()` | 1, 6, 11 | TP2 |
| `geom_tile()` + `scale_fill_gradient2()` | 2, 5 | CM2 |
| `geom_violin()` | 3 | CM2 |
| `geom_boxplot()` | 3 | CM1, TP4 |
| `coord_flip()` | 3, 7 | CM2 |
| `geom_point()` | 4, 12 | CM2, TP3, TP4 |
| `cor()` — corrélation de Pearson | 5 | TP3, TP4 |
| `pivot_wider()`, `pivot_longer()` | 5, 11, 12 | TP5 |
| `geom_col()` + barres horizontales | 7, 9 | CM2, TP3 |
| `sd()` × √252 — volatilité annualisée | 4, 8 | TP1 |
| `coord_polar()` — camembert | 9 | CM2 |
| `geom_histogram()` + `dnorm()` | 10 | TP1, TP3 |
| `facet_wrap()` | 10, 11 | TP3, TP4 |
| Normalisation Base 100 | 1, 6 | TP2 |
| Normalisation Z-score | 11 | TP1 (exo 4) |
| Normalisation Min-Max | 11 | Cours CM |
| `lm()` + `geom_smooth(method="lm")` | 12 | TP3 (exo 4), TP4 |
| Théorème Central Limite (TCL) | 13 | TP1 (exo 4) |
| `geom_density()` | 13 | CM2 |
| Loi Normale `dnorm()` | 10, 13 | TP1 (exo 2), TP2 (exo 2) |

---

## 5. Packages utilisés

| Package | Rôle | Introduit |
|---------|------|-----------|
| `ggplot2` | Toutes les visualisations | CM2, TP3 |
| `dplyr` | Manipulation des données (`filter`, `group_by`, `summarise`, `mutate`) | TP4, TP5 |
| `tidyr` | Pivot long/large (`pivot_wider`, `pivot_longer`, `unnest`) | TP5 |
| `scales` | Formatage des axes (`label_percent`, `label_number`, `squish`) | CM2, TP3 |
| `ggrepel` | Labels sans chevauchement (`geom_text_repel`) | Complément ggplot2 |
