#Cocu Ethan
#TP5
library(questionr)
library(tidyverse)
library(sf)

data(rp2012)

#---------------------------------------------------------
# (1) Extraction des données de France métropolitaine
#---------------------------------------------------------

rp <- rp2012 %>%
  filter(!region %in% c("Guadeloupe", "Martinique", "Guyane", "La Réunion"))

#---------------------------------------------------------
# (2) Nuage de points : sans diplôme vs ouvriers
#---------------------------------------------------------

ggplot(data = rp, aes(x = dipl_aucun, y = ouvr)) +
  geom_point() +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Sans diplôme vs ouvriers (France métropolitaine)")

#---------------------------------------------------------
# (3) Boxplots : répartition de proprio selon pop_cl
#---------------------------------------------------------

ggplot(data = rp, aes(x = pop_cl, y = proprio)) +
  geom_boxplot() +
  labs(x = "Taille de la commune",
       y = "% propriétaires",
       title = "Répartition des propriétaires selon la taille de la commune")

#---------------------------------------------------------
# (4) Diagramme en bâtons : nombre de communes selon pop_cl
#---------------------------------------------------------

ggplot(data = rp, aes(x = pop_cl)) +
  geom_bar() +
  labs(x = "Taille de la commune",
       y = "Nombre de communes",
       title = "Nombre de communes selon la taille")

#---------------------------------------------------------
# (5) Extraction du Grand Est (Alsace, Lorraine, Champagne-Ardenne)
#---------------------------------------------------------

rp_GE <- rp %>%
  filter(region %in% c("Alsace", "Lorraine", "Champagne-Ardenne"))

#---------------------------------------------------------
# (6) Nuage de points : sans diplôme vs ouvriers, couleur par région
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = dipl_aucun, y = ouvr, color = region)) +
  geom_point() +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Sans diplôme vs ouvriers dans le Grand Est",
       color = "Région")

#---------------------------------------------------------
# (7) Ajustement par droite (lm) puis courbe loess
#---------------------------------------------------------

# Ajustement par droite des moindres carrés
ggplot(data = rp_GE, aes(x = dipl_aucun, y = ouvr)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Ajustement linéaire (Grand Est)")

# Ajustement par courbe loess
ggplot(data = rp_GE, aes(x = dipl_aucun, y = ouvr)) +
  geom_point() +
  geom_smooth(method = "loess", se = FALSE) +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Ajustement loess (Grand Est)")

#---------------------------------------------------------
# (8) Ajustement par groupes de région, comparaison des courbes
#---------------------------------------------------------

# Droites par région
ggplot(data = rp_GE, aes(x = dipl_aucun, y = ouvr, color = region)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Ajustement linéaire par région (Grand Est)",
       color = "Région")

# Courbes loess par région
ggplot(data = rp_GE, aes(x = dipl_aucun, y = ouvr, color = region)) +
  geom_point() +
  geom_smooth(method = "loess", se = FALSE) +
  labs(x = "% sans diplôme",
       y = "% ouvriers",
       title = "Ajustement loess par région (Grand Est)",
       color = "Région")

# Commentaire : la Lorraine présente une association plus forte entre le manque de diplôme
# et la proportion d'ouvriers. La Champagne-Ardenne suit un profil similaire.
# L'Alsace montre une pente plus faible, avec un marché de l'emploi plus diversifié.

#---------------------------------------------------------
# (9) Boxplots : proprio selon pop_cl, fill par région
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = pop_cl, y = proprio, fill = region)) +
  geom_boxplot() +
  labs(x = "Taille de la commune",
       y = "% propriétaires",
       title = "Propriétaires selon taille de commune et région (Grand Est)",
       fill = "Région")

# Commentaire : dans les petites communes, la proportion de propriétaires est
# globalement plus élevée dans les trois régions. La Lorraine et la Champagne-Ardenne
# ont des taux de propriété plus élevés que l'Alsace pour les communes de grande taille.

#---------------------------------------------------------
# (10) Diagramme en bâtons empilés : communes par pop_cl, couleur par région
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = pop_cl, fill = region)) +
  geom_bar(position = "stack") +
  labs(x = "Taille de la commune",
       y = "Nombre de communes",
       title = "Nombre de communes par taille et région (Grand Est)",
       fill = "Région")

#---------------------------------------------------------
# (11) Barres côte à côte (position = "dodge")
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = pop_cl, fill = region)) +
  geom_bar(position = "dodge") +
  labs(x = "Taille de la commune",
       y = "Nombre de communes",
       title = "Communes par taille et région – côte à côte (Grand Est)",
       fill = "Région")

#---------------------------------------------------------
# (12) Nuage de points : cadres vs dipl_sup avec facet_grid par région
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = cadres, y = dipl_sup)) +
  geom_point() +
  facet_grid(. ~ region) +
  labs(x = "% cadres",
       y = "% diplômés du supérieur",
       title = "Cadres vs diplômés du supérieur par région (Grand Est)")

#---------------------------------------------------------
# (13) Même graphique : taille des points selon pop_tot, transparence
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = cadres, y = dipl_sup, size = pop_tot)) +
  geom_point(alpha = 0.4) + # alpha pour la transparence
  facet_grid(. ~ region) +
  labs(x = "% cadres",
       y = "% diplômés du supérieur",
       title = "Cadres vs diplômés du supérieur (taille = population totale)",
       size = "Population")

#---------------------------------------------------------
# (14) Nuage de points : chom vs dipl_aucun
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = dipl_aucun, y = chom)) +
  geom_point() +
  labs(x = "% sans diplôme",
       y = "% chômeurs",
       title = "Chômage vs sans diplôme (Grand Est)")

#---------------------------------------------------------
# (15) Même graphique par région avec droites d'ajustement
#---------------------------------------------------------

ggplot(data = rp_GE, aes(x = dipl_aucun, y = chom, color = region)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  facet_grid(. ~ region) +
  labs(x = "% sans diplôme",
       y = "% chômeurs",
       title = "Chômage vs sans diplôme par région (Grand Est)",
       color = "Région")

#---------------------------------------------------------
# Préparation de la carte des départements (questions 16-18)
#---------------------------------------------------------

# Importer le shapefile des départements (répertoire dpt)
# Modifier le chemin selon votre arborescence locale
lien_dpt <- "dpt" # chemin vers le répertoire contenant le shapefile
dpt <- read_sf(lien_dpt)

# Calcul des indicateurs agrégés par département
# On utilise la moyenne pondérée par pop_tot
vars_carte <- c("chom", "femmes", "agric", "cadres", "empl",
                "ouvr", "etud", "dipl_sup", "hlm", "maison", "appart")

rp_dept <- rp %>%
  group_by(dept) %>%
  summarise(across(all_of(vars_carte),
                   ~ weighted.mean(.x, pop_tot, na.rm = TRUE))) %>%
  rename(CODE_DEPT = dept)

# Jointure avec le fond de carte
dpt_stats <- inner_join(dpt, rp_dept, by = "CODE_DEPT")

#---------------------------------------------------------
# (16) Carte du taux de chômage par département (France métropolitaine)
#---------------------------------------------------------

ggplot(dpt_stats) +
  geom_sf(aes(fill = chom)) +
  scale_fill_gradient(low = "yellow", high = "red") +
  labs(title = "Taux de chômage par département (France métropolitaine)",
       fill = "% chômeurs") +
  theme_void()

#---------------------------------------------------------
# (17) Cartes pour les autres variables
#---------------------------------------------------------

titres_vars <- c(
  femmes  = "% de femmes",
  agric   = "% d'agriculteurs",
  cadres  = "% de cadres",
  empl    = "% d'employés",
  ouvr    = "% d'ouvriers",
  etud    = "% d'étudiants",
  dipl_sup = "% de diplômés du supérieur",
  hlm     = "% en HLM",
  maison  = "% en maison",
  appart  = "% en appartement"
)

for (var in names(titres_vars)) {
  p <- ggplot(dpt_stats) +
    geom_sf(aes(fill = .data[[var]])) +
    scale_fill_gradient(low = "yellow", high = "red") +
    labs(title = paste(titres_vars[var], "par département"),
         fill = titres_vars[var]) +
    theme_void()
  print(p)
}

#---------------------------------------------------------
# (18) Questions 16 et 17 restreintes aux départements du Grand Est
#---------------------------------------------------------

# Codes des départements du Grand Est
# Alsace : 67, 68 | Lorraine : 54, 55, 57, 88 | Champagne-Ardenne : 08, 10, 51, 52
dept_GE <- c("08", "10", "51", "52", "54", "55", "57", "67", "68", "88")

dpt_GE <- dpt_stats %>%
  filter(CODE_DEPT %in% dept_GE)

# Carte du taux de chômage – Grand Est
ggplot(dpt_GE) +
  geom_sf(aes(fill = chom)) +
  scale_fill_gradient(low = "yellow", high = "red") +
  labs(title = "Taux de chômage par département (Grand Est)",
       fill = "% chômeurs") +
  theme_void()

# Cartes des autres variables – Grand Est
for (var in names(titres_vars)) {
  p <- ggplot(dpt_GE) +
    geom_sf(aes(fill = .data[[var]])) +
    scale_fill_gradient(low = "yellow", high = "red") +
    labs(title = paste(titres_vars[var], "par département (Grand Est)"),
         fill = titres_vars[var]) +
    theme_void()
  print(p)
}
