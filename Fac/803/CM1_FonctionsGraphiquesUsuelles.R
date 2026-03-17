#### Les fonctions graphiques usuelles ####

# Références :
# 1. Chapitre 3 du livre : R pour la statistique et la science des données
#    voir le site web du livre : https://r-stat-sc-donnees.github.io
# 2. D'autres sites web : http://www.thibault.laurent.free.fr/cours/R_intro/chapitre_4.html
#                         http://www.r-graph-gallery.com
#                         https://lrouviere.github.io/VISU/

# On peut obtenir des exemples de représentations graphiques 
# à l'aide de la fonction "demo()":
demo(graphics)

# Nous allons donner des exemples de représentation 
# pour des variables quantitatives/qualitatives.
# Nous utilisons le fichier de données ``ozone.txt''

# Importer le fichier de données ``ozone.txt'':
ozone <- read.table(file.choose(), header=TRUE, stringsAsFactors=TRUE)
str(ozone)

# on extrait quelques variables:
ozone <- ozone[, c("T12","maxO3","vent","pluie","Vx12")] 
str(ozone)

# La base est constituée de variables climatiques, et d'une variable de pollution à l'ozone,
# mesurées quotidiennement durant l'été 2001 à Rennes (Juin-Septembre, 4 mois), 
# 112 observations, de 5 variables.
# Les variables considérées sont:
# T12 : température à midi (variable numérique)
# vent : direction du vent, qualitative à 4 modalités (Est, Nord, Ouest, Sud)
# pluie : qualitative à deux modalités (Pluie, Sec)
# maxO3 : maximum d'ozone journalier (variable numérique)
# Vx12 : projection du vecteur vitesse du vent sur l'axe Est-Ouest (variable numérique)

# Les noms des lignes correspondent aux dates de prise des mesures: 
rownames(ozone)

View(ozone)

summary(ozone)

#### 1. La fonction plot() ####

# Commençons par représenter deux variables numériques:
plot(maxO3~T12, data=ozone, main="Nuage de points (T12, maxO3)")

# Pour représenter une variable quantitative (maxO3) 
# en fonction d'une variable qualitative (vent),
# nous écrivons de la même façon:
plot(maxO3~vent, data=ozone, main="Boxplots",
     xlab="Direction du vent", 
     ylab="Concentration en ozone") # la fonction plot() dans ce cas retourne une boîte
                                    # à moustaches par modalité de la variable (vent).
# on représente la moyenne de la variable (maxO3) par une ligne horizontale:
abline(h=mean(ozone$maxO3), lty=3) 

# On peut obtenir le même graphique avec la fonction boxplot():
boxplot(maxO3~vent, data=ozone, main="Boxplots",
        xlab="Direction du vent", 
        ylab="Concentration en ozone")
# on représente la moyenne de la variable (maxO3) par une ligne horizontale:
abline(h = mean(ozone$maxO3), lty=3) 

# Ceci affiche le boxplot de la variable (maxO3): 
boxplot(ozone$maxO3, main="Boxplot", ylab="Concentration en ozone")
# on représente la moyenne de la variable (maxO3) par une ligne horizontale:
abline(h=mean(ozone$maxO3), lty=3) 

# On représente deux variables qualitatives par un diagramme en bandes:
plot(pluie~vent, data=ozone, main="Diagramme en bandes")

# On représente une variable qualitative en fonction d'une variable numérique:
plot(x=ozone[,"T12"], y=ozone[,"vent"], pch=3, yaxt="n", xlab="T12", ylab="vent") 
# L'argument yaxt="n" supprime les libellés des graduations de l'axe y 
# qui prennent ici par défaut les modalités de la variable qualitative (vent) 
# transformées en numériques (1,2,3,4).
# La fonction axis() permet alors de renommer les libellés des graduations:
axis(side=2, at=1:4, labels=levels(ozone[,"vent"]))

# On représente la variable numérique maxO3 en fonction de l'indice (temporel):
plot(ozone[,"maxO3"], xlab="indice temporel", ylab="maxO3", cex=0.5, pch=16,
     main="Nuage de points")
# L'argument cex permet de gérer la taille (par défaut cex=1).
# L'argument pch permet de préciser la forme des points, 
# il peut prendre les valeurs entières de 0 à 25, 
# ou l'un des caractères "+", "x", ".", "#". 

# Il est possible de modifier le type de tracé via l'argument type: 
# type="p" pour tracer des points (option par défaut), 
# type="l" (line) pour relier les points, et type="b" ou type="o" 
# pour faire les deux: 
plot(ozone[,"maxO3"], xlab="indice temporel", 
     ylab="maxO3", type="l", 
     main="Evolution de la concentration en ozone")

plot(ozone[,"maxO3"], xlab="indice temporel", ylab="maxO3", type="o",
     main="Evolution de la concentration en ozone")

plot(ozone[,"maxO3"], xlab="indice temporel", ylab="maxO3", type="b",
     main="Evolution de la concentration en ozone")

#### 2. Représentation de la distribution (la densité de probabilité) d'une variable quantitative continue ####
hist(ozone[,"maxO3"], main="Histogramme", 
      prob=TRUE, xlab="Ozone", col="lightblue") # trace l'histogramme si on spécifie 
                                                # l'argument ``prob=TRUE''.

plot(density(ozone[,"maxO3"]), 
     main="Estimateur à noyau", 
     xlab="Ozone") # trace l'estimateur à noyau de la densité de probabilité 
                   # de la variable (maxO3).

# les deux représentations sur le même graphique:
val_hist <- hist(ozone[,"maxO3"], prob="TRUE", plot=FALSE)
y_lim <- range(density(ozone[,"maxO3"])$y, val_hist$density)
x_lim <- range(density(ozone[,"maxO3"])$x, val_hist$breaks)
hist(ozone[,"maxO3"], main="Histogramme et Densité", 
     prob=TRUE, xlab="Ozone", ylim=y_lim, xlim=x_lim, col="lightblue")
lines(density(ozone[,"maxO3"]))

## Calcul explicite de l'estimateur à noyau de la densité de la variable (maxO3)
n <- length(ozone$maxO3) # donne le nombre d'observations. 

# Le noyau (une densité de proba symétrique, le noyau gaussien):
k <- function(t){(1/sqrt(2*pi))*exp(-t^2/2)}

Ecart_Iq <- summary(ozone$maxO3)["3rd Qu."]-summary(ozone$maxO3)["1st Qu."]
# La largeur de la fenêtre de lissage:
h <- 0.9*min(sqrt((n-1)/n)*sd(ozone$maxO3), Ecart_Iq/1.349)*n^(-1/5) 

# On utilise lapply() pour éviter la boucle ``for'', de plus x peut être un vecteur: 
estim_densite <- function(x) lapply(X=x, FUN=function(x){(1/h)*mean(k((x-ozone$maxO3)/h))})

# On trace l'histogramme et l'estimateur à noyau sur le même graphique:
hist(ozone[,"maxO3"], main="Histogramme et Densité", 
     prob=TRUE, xlab="Ozone", col="lightblue", 
     xlim=x_lim, ylim=y_lim) # Trace l'histogramme si on spécifie 
                             # l'argument ``prob=TRUE''.

# L'argument ``add=TRUE'' permet de tracer sur le graphique précédent:
curve(estim_densite(x), add=TRUE) 

#### Représentation de la distribution d'une variable qualitative #### 
# On utilise un diagramme en barres
plot(ozone[,"vent"], main="Diagrammes en barres")

# Le même graphique peut être obtenu via la fonction barplot() appliquée 
# à un vecteur donnant les effectifs de chaque modalités:
barplot(table(ozone[,"vent"])/n, main="Diagrammes en barres")
# table(ozone[,"vent"]): calcule les effectifs des modalités de la variable qualitative (vent)

#### 3. Ajouts aux graphiques ####
# Une fois le graphique tracé, il est possible de le compléter par d'autres informations : 
# ajouts de textes, lignes, points, ...

# Ajout de textes : nous reprenons la représentation du couple de variables numériques (T12, maxO3).
# Pour faire apparaître la date, il est nécessaire d'ajouter du texte au nuage de points obtenu 
# par la fonction plot(). On écrit uniquement le mois et le jour, i.e. caractères 5 à 8 des noms des lignes,
# avec une taille de fonte diminuée (``cex=0.75''). Le texte est ajouté au-dessus (``pos=3'') 
# avec un décalage de 0.3 (``offset=0.3'') :
plot(maxO3~T12, data=ozone, pch=20, main="Nuage de points")
text(x=ozone[,"T12"], y=ozone[,"maxO3"], labels=substr(rownames(ozone), start=5, stop=8), 
     cex=.75, pos=3, offset=0.3)

# On peut ajouter une ligne verticale avec ``abline(v= )'' :
abline(v=27, lty=2)
# ou une ligne horizontale avec ``abline(h= )'', ou encore une droite en précisant l'ordonnée 
# à l'origine et la pente avec la fonction ``abline(c(ordonnee, pente))''.
# Le paramètre ``lty'' (line type) permet de déterminer le type de ligne :
# 1: trait plein, 2 : tirets, 3 : pointillés, ...

# Si on veut représenter deux courbes sur le même graphiques,
# on peut utiliser la fonction ``lines()'' :
# On compare ici l'évolution de l'ozone sur deux semaines différentes
plot(ozone[1:7,"maxO3"], type="l", ylab="ozone") # la semaine de 1:7
lines(ozone[8:14,"maxO3"], col="red") # ajout de la 2ème semaine (8:14)
# Le graphique n'affiche pas les sixième et septième observations de cette deuxième semaine.
# On doit donc ajuster les échelles. Pour cela, la connaissance du min et max est nécessaire.
# (min, max) peut être obtenu avec la fonction range(). On fait la mise à l'échelle alors comme suit
ecart_y <- range(ozone[1:7,"maxO3"], ozone[8:14,"maxO3"])
ecart_y
plot(ozone[1:7,"maxO3"], type="l", ylim=ecart_y, lty=1, ylab="ozone")
lines(ozone[8:14,"maxO3"], col="red", lty=1)

#### 4. Graphiques 3D ####
# Les fonctions classiques de représentations 3D sont les fonctions ``persp()'' (3D avec perspective)
# ``contour()'' (lignes de niveau), et ``filled.contour()'' 
# ou ``image()'' (lignes de niveau avec effet de couleur).

# A titre d'exemple, nous allons représenter la fonction classique "chapeau mexicain":
# (x,y) -> z := f(x,y) = 10 sin(sqrt(x^2+y^2))/sqrt(x^2+y^2).
# On choisit une grille régulière carrée comprenant 30 valeurs différentes, comprises entre -10 et 10,
# sur x et sur y :
f <- function(x,y){10*sin(sqrt(x^2+y^2))/sqrt(x^2+y^2)}
x <- seq(from=-10, to=10, length=30)
y <- seq(from=-10, to=10, length=30)
# On évalue ensuite la fonction f en chaque point de la grille :
# pour chaque couple ``(x[i], y[j])'', nous calculons ``f(x[i], y[j])''. 
# Afin d'éviter une (double) boucle, nous utilisons la fonction ``outer()''
z <- outer(x, y, f)
str(z)

# Nous pouvons maintenant tracer la fonction en 3D
persp(x=x, y=y, z=z, theta=30, phi=30, expand=0.4)

# Si on veut colorer chaque facette (il y en a 29x29), 
# on calcule la moyenne des quatre extrémités de la facette et on découpe 
# cette moyenne en facteur de 100 niveaux, un niveau pour chaque couleur. 
# Le vecteur des 100 couleurs possibles est obtenu avec la fonction ``heat.colors()'' :
zfacette <- (z[-1,-1]+z[-1,-30]+z[-30,-1]+z[-30,-30])/4
niveaucouleur <- cut(zfacette, 100)
couleurs <- heat.colors(100)[niveaucouleur]
persp(x=x, y=y, z=z, theta=30, phi=30, expand=0.4, col=couleurs)

# Les graphiques avec les courbes de niveaux peuvent être obtenues avec 
# les commandes ``contour(x,y,z)'', ``filled.contour(x,y,z)'' ou ``image(x,y,z)''
contour(x=x, y=y, z=z, xlab="x", ylab="y", main="Courbes de niveaux")

filled.contour(x=x, y=y, z=z, xlab="x", ylab="y", main="Courbes de niveaux")

image(x=x, y=y, z=z, xlab="x", ylab="y", main="Courbes de niveaux")

# On peut aussi utiliser le package "rgl" pour construire la surface de réponse du graphique précédent
library(rgl)
rgl.open()
rgl.surface(x,y,z)
# Ce package est conseillé pour tous les problèmes de visualisation 3D; 
# il permet d'opérer des rotations des graphiques avec la souris. 
# Voici l'exemple donné dans l'aide de R pour la commande ``rgl.surface()'' :
data(volcano)
str(volcano)
z <- 2 * volcano        # Exaggerate the relief
x <- 10 * (1:nrow(z))   # 10 meter spacing (S to N)
y <- 10 * (1:ncol(z))   # 10 meter spacing (E to W)
zlim <- range(z)
zlim
zlen <- zlim[2] - zlim[1] + 1
zlen

colorlut <- terrain.colors(zlen) # height color lookup table

col <- colorlut[ z - zlim[1] + 1 ] # assign colors to heights for each point
rgl.open()
rgl.surface(x, y, z, color = col, back = "lines")

# Si on veut tracer le nuage de points représentant ``n'' individus décrits par 
# l'observation de trois variables quantitatives, il n'est pas possible d'utiliser
# les fonctions usuelles. Il faut alors utiliser un package comme "rgl" ou "lattice".

# Ici on utilise le package "lattice" pour représenter les observations avec
# les trois variables numériques (maxO3, T12, Vx12) de la bd "ozone"
library(lattice)
cloud(maxO3~T12+Vx12, data=ozone, type=c("p","h"), col="blue")

# Avec le package "rgl", on peut utiliser la fonction "plot3d()" :
rgl.open()
plot3d(x=ozone[,"T12"], y=ozone[,"Vx12"], z=ozone[,"maxO3"], radius=1.2,
       xlab="T12", ylab="Vx12", zlab="maxO3", type="s", col="red")
# l'argument type="s", spécifique à "rgl", permet de représenter les points par des sphères 
# dont le rayon est fixé à radius=1.2. 

# On peut rajouter des segments horizontaux au graphique précédent comme suit 
plot3d(x=ozone[,"T12"], y=ozone[,"Vx12"], z=ozone[,"maxO3"], radius=1.2,
       xlab="T12", ylab="Vx12", zlab="maxO3", type="h", col="blue", add=TRUE)

#### 5. Plusieurs graphiques ####
# Si l'on souhaite figurer plusieurs graphiques dans la même fenêtre,
# on peut utiliser la fonction "par()" : la commande "par(mfrow=c(n,p))" organise
# n*p graphiques en n lignes et p colonnes. Voici un exemple :
par(mfrow=c(1,2))
plot(x=1:10, y=10:1, pch=0)
plot(x=rep(1,4), type="l")

# Pour revenir à un graphique par fenêtre, 
# on utilise la commande "par(mfrow=c(1,1))".

# Parfois, il est nécessaire d'avoir des graphiques de tailles différentes. 
# On utilise alors la fonction "layout()". Voici un exemple :
mat <- matrix(c(1,1,2,3), nrow=2, ncol=2, byrow=TRUE)
layout(mat)
plot(x=1:10, y=10:1, pch=0)
plot(x=rep(1,4), type="l")
plot(x=c(2,3,-1,0), type="b")

# On peut avoir besoin d'ouvrir plusieurs fenêtres graphiques. Pour créer une fenêtre graphique,
# il suffit d'ouvrir le "device" qui correspond au système d'exploitation : X11() sous Unix/Linux ou Windows, 
# et quartz() sous macOS. Ainsi si on veut réaliser deux graphiques dans deux fenêtres séparées, 
# on procède comme suit :
par(mfrow=c(1,1))
quartz()
plot(x=1:10, y=10:1, pch=0)
quartz()
plot(x=rep(1,4), type="l")

#### 6. Amélioration et personnalisation des graphiques ####
# Afin d'améliorer le graphique, il est possible:

# 1. d'utiliser des couleurs ou des nuances de gris :
plot(x=ozone[,"maxO3"], y=ozone[,"T12"], type="p", pch="+", col="grey30")
# Ces couleurs (ou nuances de gris) peuvent être appelées avec un chiffre
# (1 : noir, 2 : rouge, 3 : vert, etc), avec un nom de couleur en anglais 
# (la liste est donnée par la fonction "colors()"), 
# ou un code RGB avec une transparence (voir "rgb()").

# 2. il est possible de changer les couleurs de fond et de tracé du plan grâce 
# à la fonction "par()", avec les arguments "fg : foreground", 
# et "bg : background" :
par(fg="blue", bg="grey70")
plot(x=ozone[,"maxO3"], y=ozone[,"T12"], type="p", pch="+")

# Pour revenir au cas standard :
par(fg="black", bg="white")

# 3. de mettre un titre :
plot(x=ozone[,"maxO3"], y=ozone[,"T12"], type="p", pch="+", 
      main="Représentation du couple (T12,maxO3)")

# 4. de contrôler l'aspect des axes en les éliminant (ainsi que leur légende) :
plot(x=c(10,11,12), y=c(12,11,12), type="b", axes=FALSE, xlab="", ylab="")
# pour les reconstruire à la main :
axis(side=1, at=c(10,11,12), labels=c("obs. 1","obs. 2", "obs. 3"))

# 5. de construire des axes orthonormés (argument "asp=1")
plot(x=c(10,11,12), y=c(12,11,12), type="b", asp=1)

# 6. d'ajouter une légende :
ecart_y <- range(ozone[1:7,"maxO3"], ozone[8:14,"maxO3"])
plot(ozone[1:7,"maxO3"], ylim=ecart_y, type="l", col="blue")
lines(ozone[8:14,"maxO3"],  col="red")
legend("topright",legend=c("semaine 1","semaine 2"),
       col=c("blue","red"),lty=1)

# 7. d'insérer des symboles ou des formules mathématiques (voir "help(plotmath)"), 
# par exemple pour une légende d'axe :
n<-seq(from=50, to=3000, by=50) #vecteur des tailles d'échantillons
moyennes<-lapply(X=n, FUN=function(n) mean(rnorm(n,mean=1,sd=1))) # moyennes des échantillons en fonction de n
plot(x=n, y=moyennes, xlab="n : taille de l'échantillon", type="o", 
     ylab=expression(bar(x)[n]==sum(frac(x[i],n), i==1,n)))
# On constate que la marge pour le "ylab" n'est pas suffisante. On peut modifier
# cette marge grâce à la fonction "par()" en changeant la valeur de son argument "mar".
# "mar=" est exprimé en nombre de lignes. Pour le modifier, on écrit 
# "mar=c(bottom, left, top, right)" où "c(bottom, left, top, right)" est un vecteur de taille 4, 
# où le premier élément indique la marge en-dessous (bottom en anglais) du cadre graphique, 
# le deuxième élément indique la marge à gauche du cadre graphique, le troisième élément la marge au-dessus 
# du cadre graphique et le 4ème élément la marge à droite du cadre graphique. 
# Par défaut, le paramétrage est égal à :
par("mar") # 5.1 4.1 4.1 2.1

# On modifie alors la marge à gauche comme suit:
par(mar=c(5.1, 6, 4.1, 2.1))
plot(x=n, y=moyennes, xlab="n : taille de l'échantillon", type="o", 
     ylab=expression(bar(x)[n]==frac(1,n) ~~ sum(x[i], i==1,n)))
abline(h=1, lty=2)

# On revient aux marges par défaut :
par(mar=c(5.1, 4.1, 4.1, 2.1))
plot(x=n, y=moyennes, xlab="n : taille de l'échantillon", type="o", 
     ylab=expression(bar(x)[n]==frac(1,n) ~~ sum(x[i], i==1,n)))
abline(h=1, lty=2)

