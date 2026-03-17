#---------------------------------------------------------
# Exercice 1 : Tracé des taches solaires
#---------------------------------------------------------

# (1) Importation 
taches <- read.csv("taches_solaires_date.csv", sep = ";", 
                   colClasses = c("numeric", "character"))
colnames(taches) <- c("nombre_relatif", "date")

taches$date <- as.Date(taches$date, format = "%Y/%m/%d")
#vérifications
head(taches)
str(taches)

#---------------------------------------------------------
# (2) Création de la variable qualitative 'trenteans'
#---------------------------------------------------------

dates_breaks <- seq(from = min(taches$date), 
                    to = max(taches$date) + 365*30, 
                    by = "30 years")

trenteans <- cut(taches$date, breaks = dates_breaks)
levels(trenteans) <- 1:nlevels(trenteans)

#---------------------------------------------------------
# (3) Couleurs et (4) Graphique
#---------------------------------------------------------
couleur <- c("yellow", "magenta", "orange", "cyan", "grey", "red", "green", "blue")
palette(couleur)

# Tracé
plot(taches$nombre_relatif, type = "n", 
     xlab = "Temps", 
     ylab = "Nb de taches")

for (i in 1:nlevels(trenteans)) {
  indices <- which(trenteans == levels(trenteans)[i])
  lines(x = indices, y = taches$nombre_relatif[indices], col = i)
}


#---------------------------------------------------------
# Exercice 2 : Tracé d'une densité
#---------------------------------------------------------

# (1) Tracer la densité de la loi normale N(0,1)
x <- seq(-4, 4, length.out = 1000)

y <- dnorm(x, mean = 0, sd = 1)

plot(x, y, type = "l", 
     xlab = "x", 
     ylab = "Densité",
     ylim = c(0, 0.4)) 
# (2) Ajouter l'axe des abscisses (droite y = 0)
abline(h = 0)

# (3) Colorier en bleu l'aire correspondant à la probabilité de 5%
q <- qnorm(1 - 0.05)

# On crée une séquence de points x allant de q jusqu'à la fin du graphe (4)
x_poly <- seq(q, 4, length.out = 100)
y_poly <- dnorm(x_poly)

polygon(x = c(q, x_poly, 4), 
        y = c(0, y_poly, 0), 
        col = "blue")

# (4) Ajouter une flèche désignant l'aire coloriée
arrows(x0 = 2.5, y0 = 0.1, x1 = 1.9, y1 = 0.03, length = 0.1)

# (5) Ajouter l'annotation alpha = 5%
text(x = 2.5, y = 0.12, labels = expression(alpha == "5%"))



#---------------------------------------------------------
# Exercice 3 : Disposition avec la fonction layout()
#---------------------------------------------------------

# Nettoyage préalable pour éviter les erreurs d'affichage ("margins too large")
graphics.off() 
# On réduit légèrement les marges par défaut 
par(mar = c(4, 4, 2, 1))

# (1) Reproduire le graphique avec 3 panneaux
matrice_dispo <- matrix(c(1, 1, 
                          2, 3), 
                        nrow = 2, byrow = TRUE)

layout(matrice_dispo)

# Tracé du Graphique 1 
plot(1:10, 10:1, pch = 0, xlab = "", ylab = "")

# Tracé du Graphique 2 
plot(1:4, rep(1, 4), type = "l", ylim = c(0.6, 1.4), xlab = "", ylab = "")

# Tracé du Graphique 3 
plot(1:4, c(2, 3, -1, 0), type = "b", pch = 1, xlab = "", ylab = "")


# (2) Reproduire la même figure avec des largeurs relatives différentes
layout(matrice_dispo, widths = c(4, 1))

# Graphique 1
plot(1:10, 10:1, pch = 0, xlab = "", ylab = "")

# Graphique 2
plot(1:4, rep(1, 4), type = "l", ylim = c(0.6, 1.4), xlab = "", ylab = "")

# Graphique 3
plot(1:4, c(2, 3, -1, 0), type = "b", pch = 1, xlab = "", ylab = "")

#Réinitialiser la disposition normale à la fin

par(mfrow = c(1, 1))

