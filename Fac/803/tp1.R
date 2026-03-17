#Cocu Ethan
#TP1
#Exercice 1
#1. Tracer la fonction sinus entre 0 et 2pi (utiliser pi)
# Ajouter au graphique le titre suivant: Graphique de la fonction sinus (utiliser la commande title())

#  Visualisation d'une fonction trigonométrique continue sur un cycle complet.
x <- seq(0, 2 * pi, length.out = 100)
y = sin(x)
plot(x, y, 
     type = "l",
     col = "blue",          
     lwd = 2,
     xlab = "x (radians)", 
     ylab = "sin(x)")     

title(main = "Graphique de la fonction sinus")
abline(h = 0, lty = 2, col = "black")

#exercice 2:
#1)tracer la courbe de la densité de loi normale centré réduite entre -4 et 4 (utiliser la fonction dnorm)

# Comparaison de la loi Normale (Gauss) avec la loi de Student.
# Illustre comment la loi de Student converge vers la Normale quand les degrés de liberté augmentent.
x <- seq(-4, 4, length.out = 200)
y_auto <- dnorm(x)
plot(x, y_auto, 
     type = "l", 
     lwd = 2, 
     col = "blue",
     main = "Densité de la Loi Normale (Paramètres par défaut)",
     xlab = "x", 
     ylab = "Densité")

#2) reprendre la question précédente en définnissaant explicitement la densité demandé

y_explicite <- dnorm(x, mean = 0, sd = 1)

plot(x, y_explicite, 
     type = "l", 
     lwd = 2, 
     col = "black",
     main = "Densité de la Loi Normale (Définition Explicite)",
     xlab = "x", 
     ylab = "f(x)")

#3)Ajouter au graphique la droite d'équation x=0 et la dorite d'équation y = 0

abline(v = 0, col = "gray", lty = 2)
abline(h = 0, col = "gray", lty = 2)

#4) tracer sur le même graphique les densité des lois de student à 5 et 30 degrès de liberté (utiliser la fonction curve (), la fonction dt(), une couleur différente pour chaque courbe)

curve(dt(x, df = 5), add = TRUE, col = "red", lwd = 2)
curve(dt(x, df = 30), add = TRUE, col = "blue", lwd = 2, lty = 4)

#5) ajouter une légende en haut à gauche pour préciser chaque distribution

legend("topleft", 
       legend = c("Normale (0,1)", "Student (df=5)", "Student (df=30)"),
       col = c("black", "red", "blue"), 
       lty = c(1, 1, 4), 
       lwd = 2)



#Exercice 3

set.seed(1234) 
#1) générer un échantillon (X1, ...., X10000) de taille 10000 selon une loi de Bernoulli de paramètre p = 0.6(utiliser la fonction rbinom()

# Illustration de la Loi des Grands Nombres (LGN).
# Démontre que la moyenne empirique se stabilise vers l'espérance théorique (0.6) avec n grand.
p <- 0.6
taille <- 10000
X <- rbinom(n = taille, size = 1, prob = p)

#2) calculer les moyennes successives Mn := Sn/n, n = 1,...,10000 où Sn := somme des Xi  pour i =1 
Sn <- cumsum(X)
nr <- 1:taille
Mn <- Sn / nr

#3) Tracer Mn pour n = 30,31,32,.....10000
n_zoom <- 30:taille
Mn_zoom <- Mn[n_zoom]

plot(n_zoom, Mn_zoom, 
     type = "l", 
     col = "blue",
     main = "Loi des Grands Nombres (Bernoulli p=0.6)",
     xlab = "n (Taille de l'échantillon)",
     ylab = "Moyenne empirique (Mn)",
     ylim = c(0.4, 0.8))

#ajouter la droite d'équation y = 0.6
abline(h = 0.6, col = "red", lwd = 2, lty = 2)



#Exercice 4
#1)Soient x1,...,xn des variables aléatoires i.i.d suivant une loi de bernoulli de paramètre p. Rappeler la loi suivie par S := x1,...xn,. Donner son espérance et son écart-type

# Illustration du Théorème Central Limite (TCL).
# Montre que la somme centrée réduite de variables discrètes tend vers une loi Normale continue.

# La somme S de n variables de Bernoulli i.i.d. de paramètre p suit une loi Binomiale B(n, p).
# L'espérance est : E(S) = n * p
# L'écart-type est : sigma(S) = racine_carrée(n * p * (1 - p))

#2)On fixe N=10 et p = 0.5. Générer, grâce a la fonction rbinom(), n = 1000 réalisation i.i.d.S1,S2,...S1000 de S. Ranger dans un vecteur U10 les quantité (si-np)/ racine(np(1-p)), i = 1....1000. Faire de même avec N =30 et N = 1000 pour obtenir deux nouveaux vecteurs U30 et U1000;

p <- 0.5
n_simu <- 1000

# Pour N = 10
N10 <- 10
S10 <- rbinom(n = n_simu, size = N10, prob = p)
U10 <- (S10 - N10 * p) / sqrt(N10 * p * (1 - p))

# Pour N = 30
N30 <- 30
S30 <- rbinom(n = n_simu, size = N30, prob = p)
U30 <- (S30 - N30 * p) / sqrt(N30 * p * (1 - p))

# Pour N = 1000
N1000 <- 1000
S1000 <- rbinom(n = n_simu, size = N1000, prob = p)
U1000 <- (S1000 - N1000 * p) / sqrt(N1000 * p * (1 - p))


#3) Représenter sur un même fenetre (utiliser par(mfrow =)), les histogrammes de U10, U30et U1000 en superposant à chaque fois la densité de la loi normale centrée réduite(dnorm()), entre -4 et 4

par(mfrow = c(1, 3))

# Préparation de la courbe normale pour la superposition
x_axe <- seq(-4, 4, length.out = 100)
y_norm <- dnorm(x_axe, mean = 0, sd = 1)

# Histogramme pour N = 10
hist(U10, probability = TRUE, main = "N = 10", xlab = "U10", col = "blue", xlim = c(-4,4), ylim = c(0, 0.5))
lines(x_axe, y_norm, col = "red", lwd = 2)

# Histogramme pour N = 30
hist(U30, probability = TRUE, main = "N = 30", xlab = "U30", col = "green", xlim = c(-4,4), ylim = c(0, 0.5))
lines(x_axe, y_norm, col = "red", lwd = 2)

# Histogramme pour N = 1000
hist(U1000, probability = TRUE, main = "N = 1000", xlab = "U1000", col = "black", xlim = c(-4,4), ylim = c(0, 0.5))
lines




