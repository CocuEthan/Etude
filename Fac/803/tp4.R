#Cocu Ethan
#TP4
library(ggplot2)

#---------------------------------------------------------
# Exercice 1 : Habillage selon une variable qualitative avec ggplot2
#---------------------------------------------------------

# Construction du jeu de données states
data(state)
states <- data.frame(state.x77, state.name = rownames(state.x77),
                     state.region = state.region)

# (1) Créer la variable revenu1 (faible / moyen / fort selon les terciles d'Income)
terciles <- quantile(states$Income, probs = c(1/3, 2/3))

states$revenu1 <- cut(states$Income,
                      breaks = c(-Inf, terciles[1], terciles[2], Inf),
                      labels = c("faible", "moyen", "fort"))

#---------------------------------------------------------
# (2) Nuage de points (Population, Murder) pour chaque modalité de revenu1
#---------------------------------------------------------

ggplot(data = states, aes(x = Population, y = Murder)) +
  geom_point() +
  facet_wrap(~ revenu1) +
  labs(title = "Nuage de points (Population, Murder) par niveau de revenu")

#---------------------------------------------------------
# (3) Couleur selon state.region + droite des moindres carrés
#---------------------------------------------------------

# Avec bande de confiance
ggplot(data = states, aes(x = Population, y = Murder, color = state.region)) +
  geom_point() +
  geom_smooth(method = "lm", se = TRUE) +
  facet_wrap(~ revenu1) +
  labs(title = "Nuage de points par revenu (avec bande de confiance)",
       color = "Région")

# Sans bande de confiance
ggplot(data = states, aes(x = Population, y = Murder, color = state.region)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  facet_wrap(~ revenu1) +
  labs(title = "Nuage de points par revenu (sans bande de confiance)",
       color = "Région")


#---------------------------------------------------------
# Exercice 2 : Habillage selon une variable quantitative avec ggplot2
#---------------------------------------------------------

# (1) Chargement du jeu de données Ozone (package mlbench)
library(mlbench)
data(Ozone)
# ?Ozone  # consulter l'aide

#---------------------------------------------------------
# (2) Création de la variable date au format Date (1976-01-01)
#---------------------------------------------------------

# V1 = mois, V2 = jour, année = 1976
Ozone$date <- as.Date(paste("1976", Ozone$V1, Ozone$V2, sep = "-"),
                      format = "%Y-%m-%d")

#---------------------------------------------------------
# (3) Série de la concentration en ozone (V4) en fonction de la date
#---------------------------------------------------------

ggplot(data = Ozone, aes(x = date, y = V4)) +
  geom_line() +
  labs(x = "Date",
       y = "Concentration en O3",
       title = "Concentration en ozone au cours du temps")

#---------------------------------------------------------
# (4) Nuage de points : concentration en ozone contre la température
#---------------------------------------------------------

# V8 = température à Sandburg (°F)
ggplot(data = Ozone, aes(x = V8, y = V4)) +
  geom_point() +
  labs(x = "Température (°F)",
       y = "Concentration en O3",
       title = "Concentration en ozone en fonction de la température")

#---------------------------------------------------------
# (5) Création de la variable mois (jan, fev, ...)
#---------------------------------------------------------

mois_fr <- c("jan", "fev", "mar", "avr", "mai", "jun",
             "jul", "aou", "sep", "oct", "nov", "dec")

Ozone$mois <- mois_fr[Ozone$V1]

#---------------------------------------------------------
# (6) Boxplots de la concentration en ozone par mois (ordre temporel)
#---------------------------------------------------------

# On ordonne le facteur mois dans l'ordre chronologique
Ozone$mois <- factor(Ozone$mois, levels = mois_fr)

ggplot(data = Ozone, aes(x = mois, y = V4)) +
  geom_boxplot() +
  labs(x = "Mois",
       y = "Concentration en O3",
       title = "Boxplots de la concentration en ozone par mois")

#---------------------------------------------------------
# (7) Discrétisation de la variable vent (V6) en trois classes selon les terciles
#---------------------------------------------------------

terciles_vent <- quantile(Ozone$V6, probs = c(1/3, 2/3), na.rm = TRUE)

Ozone$force_vent <- cut(Ozone$V6,
                        breaks = c(-Inf, terciles_vent[1], terciles_vent[2], Inf),
                        labels = c("faible", "moyen", "fort"))

#---------------------------------------------------------
# (8) Nuage de points (température, ozone) par mois avec couleur selon la force du vent
#---------------------------------------------------------

ggplot(data = Ozone, aes(x = V8, y = V4, color = force_vent)) +
  geom_point() +
  facet_wrap(~ mois) +
  labs(x = "Température (°F)",
       y = "Concentration en O3",
       title = "Concentration en ozone vs température par mois",
       color = "Force du vent")
