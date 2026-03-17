#---------------------------------------------------------
# Exercice 1 : Représentations graphiques simples avec ggplot2
#---------------------------------------------------------
library(ggplot2)

# (1) Tracer l'histogramme de la variable mpg
ggplot(data = mtcars, aes(x = mpg)) +
  geom_histogram() +
  labs(title = "Histogramme")

# (2) Tracer le diagramme en barres de la variable cyl
ggplot(data = mtcars, aes(x = factor(cyl))) +
  geom_bar()

# (3) Représenter le nuage de points (disp,mpg) en fonction de cyl
ggplot(data = mtcars, aes(x = disp, y = mpg)) +
  geom_point() +
  facet_wrap(~ cyl)


#---------------------------------------------------------
# Exercice 2 : Représentation d'une courbe avec ggplot2
#---------------------------------------------------------

# (a) Créer un dataframe df d'une seule colonne X
df <- data.frame(
  X = rep(c("red", "blue", "green", "black"), times = c(30, 20, 40, 10))
)

# (b) Utiliser aes(...) et geom_bar()
# (c) Rajouter les labels et le titre
ggplot(data = df, aes(x = X, y = (..count..) / sum(..count..))) +
  geom_bar() +
  labs(x = "X", 
       y = "Probabilité", 
       title = "Distribution de la variable X")


#---------------------------------------------------------
# Exercice 3 : Représentation graphique avec ggplot2
#---------------------------------------------------------

df_trigo <- data.frame(x = seq(-2 * pi, 2 * pi, length.out = 500))

# (1) Tracer la fonction sinus()
ggplot(data = df_trigo, aes(x = x)) +
  geom_line(aes(y = sin(x)))

# (2) Ajouter en bleu épais les droites y = -1 et y = 1
ggplot(data = df_trigo, aes(x = x)) +
  geom_line(aes(y = sin(x))) +
  geom_hline(yintercept = c(-1, 1), color = "blue", size = 2)

# (3) Ajouter la fonction cosinus()
ggplot(data = df_trigo, aes(x = x)) +
  geom_line(aes(y = sin(x))) +
  geom_line(aes(y = cos(x))) +
  geom_hline(yintercept = c(-1, 1), color = "blue", size = 2)

# (4) Faire le même graphe avec une légende
ggplot(data = df_trigo, aes(x = x)) +
  geom_line(aes(y = sin(x), color = "Sinus")) +
  geom_line(aes(y = cos(x), color = "Cosinus")) +
  geom_hline(yintercept = c(-1, 1), color = "blue", size = 2) +
  labs(color = "Fonctions")

# (5) Représenter cosinus() et sinus() sur deux graphes séparés
df_long <- data.frame(
  x = rep(df_trigo$x, 2),
  y = c(sin(df_trigo$x), cos(df_trigo$x)),
  fonction = rep(c("Sinus", "Cosinus"), each = nrow(df_trigo))
)

ggplot(data = df_long, aes(x = x, y = y)) +
  geom_line() +
  geom_hline(yintercept = c(-1, 1), color = "blue", size = 2) +
  facet_wrap(~ fonction)


#---------------------------------------------------------
# Exercice 4 : Simulation et représentation graphique 
#---------------------------------------------------------

set.seed(1234)
Xi <- runif(100, min = 0, max = 1)

epsilon_i <- rnorm(100, mean = 0, sd = sqrt(0.04))

Yi <- 3 + Xi + epsilon_i
df_sim <- data.frame(X = Xi, Y = Yi)

# (2) Nuage de points et droite des moindres carrés
modele <- lm(Y ~ X, data = df_sim)
ggplot(data = df_sim, aes(x = X, y = Y)) +
  geom_point() +
  geom_abline(intercept = coef(modele)[1], slope = coef(modele)[2])

ggplot(data = df_sim, aes(x = X, y = Y)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE)

# (3) Représenter les résidus
df_sim$Y_pred <- predict(modele)

ggplot(data = df_sim, aes(x = X, y = Y)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE) +
  geom_segment(aes(x = X, y = Y, xend = X, yend = Y_pred))

