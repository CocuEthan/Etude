
#### Solutions des exercices du TP1 ####

#### Exercice 1 : ####
# (1) Tracer la fonction sinus entre $0$ et $2\pi$ (Utiliser `pi`);
plot(sin, from=0, to=2*pi, type = "l")

# (2) Ajouter au graphique le titre suivant : Graphe de la fonction sinus (Utiliser la commande `title()`).
title("Graphe de la fonction sinus")

#### Exercice 2 : ####
# (1) Tracer la courbe de la densité de loi normale centrée réduite entre $-4$ et $4$
# (Utiliser la fonction `dnorm()`);
plot(dnorm, from=-4, to=4)

# (2) Reprendre la question précédente, en définissant explicitement la densité demandée;
d_normale <- function(x) {(1/sqrt(2*pi))*exp(-x^2/2)} #densité de la loi normale centrée réduite
plot(d_normale, from=-4, to=4)

# (3) Ajouter au graphique la droite d'équation $x=0$ et la droite d'équation $y=0$; 
abline(v=0, lty=2)
abline(h=0, lty=2)

# (4) Tracer sur le même graphique les densités des lois de Student  à $5$ et $30$ degrés de liberté 
# (Utiliser la fonction `curve()`, la fonction `dt()` et une couleur différente pour chaque courbe);
curve(dt(x, df=5), add=TRUE, col="red")
curve(dt(x, df=30), add=TRUE, col="blue")

# (5) Ajouter une légende en haut à gauche pour préciser chaque distribution. 
legend("topleft", legend=c("Normale","Student(5)","Student(30)"),
       col=c("black","red","blue"), lty=1)

#### Exercice 3 : La loi des grands nombres ####
# On fixe la graine du générateur à $1234$. 
set.seed(1234)

# (1) Générer un échantillon $(X_1,\ldots,X_{10000})$ de taille $10000$
#  selon une loi de Bernoulli de paramètre $p=0.6$ (Utiliser la fonction `rbinom()`);
n <- 10000
X <- rbinom(n=n, size=1, prob=0.6)

# (2) Calculer les moyennes successives $M_n := S_n/n$, $n=1,\ldots,10000,$ où 
# $S_n:=\sum_{i=1}^n X_i$.
Sn <- cumsum(X) # la fonction donne le vecteur des sommes cumulées
Mn <- Sn/(1:n)  # donne la suite des moyennes 

# (3) Tracer $M_n$ pour $n=30,31, 32, \ldots,10000$.
plot(x=30:n, y=Mn[30:n], xlab='n', ylab='Mn', type="l")

# (4) Ajouter la droite d'équation $y=0.6$.
abline(h=0.6, col="red", lty=2)

### Exercice 4 : (Théorème central limite)
# On fixe la graine du générateur à $1234$. 
set.seed(1234)
# (1) Soient $X_1,\ldots,X_N$ des variables aléatoires i.i.d. suivant une loi 
# de Bernoulli de paramètre $p$. 
# Rappeler la loi suivie par 
# $S := X_1+\cdots+X_N$. Donner son espérance et son écart-type;
# S suit une loi binomiale de paramètres N et p.
# E(S) = N p et Var(S) = N p (1-p). 
# (2) On fixe $N=10$ et $p=0.5$. Générer, grâce à la fonction `rbinom()`,
# $n=1000$ réalisations i.i.d. $S_1, S_2,\ldots,S_{1000}$ de $S$. 
# Ranger dans un vecteur $U10$ les quantités 
# $\frac{S_i-N p}{\sqrt{N p (1-p)}}$, $i=1,\ldots,1000$. 
p <- 0.5
N <- 10
U10 <- (rbinom(1000, size = N, prob=p) - N*p) /sqrt(N*p*(1-p))

# Faire de même avec $N=30$ et $N=1000$ pour obtenir 
# deux nouveaux vecteurs $U30$ et $U1000$.
set.seed(1234)
N <- 30
U30 <- (rbinom(1000, size = N, prob=p) - N*p) /sqrt(N*p*(1-p))

set.seed(1234)
N <- 1000
U1000 <- (rbinom(1000, size = N, prob=p) - N*p)/sqrt(N*p*(1-p))

# (3) Représenter sur une même fenêtre (`par(mfrow = )`), 
# les histogrammes de $U10$, $U30$ et $U1000$, en superposant à chaque fois 
# la densité de la loi normale centrée réduite (`dnorm()`).  
par(mfrow=c(1,3))
hist(U10, xlim=c(-4,4), ylim=c(0,0.6), prob=TRUE)
curve(dnorm(x), col="red", add=TRUE)
hist(U30, xlim=c(-4,4), ylim=c(0,0.6), prob=TRUE)
curve(dnorm(x), add=TRUE, col="red")
hist(U1000, xlim=c(-4,4), ylim=c(0,0.6), prob=TRUE)
curve(dnorm(x), add=TRUE, col="red")
dev.off()
graphics.off(

  