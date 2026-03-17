
#### Fonctions graphiques avec ggplot 2 ####

# Références :
# 1. Chapitre 3 du livre : R pour les statistiques et la science des données
#    voir le site web du livre : https://r-stat-sc-donnees.github.io
# 2. D'autres sites web : http://www.thibault.laurent.free.fr/cours/R_intro/chapitre_4.html
#                         http://www.r-graph-gallery.com
#                         https://github.com/tidyverse/ggplot2
#                         http://ggplot2.tidyverse.org

# Le package ggplot2 est très utilisé en visualisation de données;
# il permet d'obtenir des représentations graphiques par sous-groupe d'individus
# avec très peu de lignes de code, et de façon simple. La disposition des graphes
# et la gestion des titres et légendes sont le plus souvent gérées de manière automatique.
# Voir la "Cheat Sheet : Data visualisation with ggplot2" disponible dans l'aide de RStudio.

#### 1. Premiers graphes avec ggplot 2 ####
# On considère le jeu de données "diamonds" qui contient le prix ainsi que certaines
# caractéristiques de 54000 diamants. Nous allons nous restreindre à un sous-échantillons
# de taille 5000.

library(ggplot2)
set.seed(1234)
diamonds2 <- diamonds[sample(x=nrow(diamonds), size=5000), ]
str(diamonds2)

# Pour obtenir un graphe, la méthode ggplot2 consiste à segmenter les instructions.
# Par exemple pour tracer le diagramme en barres de la variable "cut" (qualitative ordinale, 
# qui représente la qualité de la coupe du diamant), on procède comme suit
ggplot(diamonds2)+aes(x=cut)+geom_bar()
# Le jeu de données est renseigné par la fonction "ggplot()", la variable par "aes()",
# et le type de graphique est spécifié par "geom_bar()". Les trois instructions sont séparées 
# par "+". C'est le schéma classique de construction de graphes avec ce package.

# En suivant le même schéma, on obtient par exemple l'histogramme de la variable "price" comme suit :
ggplot(diamonds2)+aes(x=price)+geom_histogram()

# Le nuage de points du couple "(carat, price)" s'obtient avec les instructions :
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point() 

#### 2. La grammaire de ggplot ####
# Les principaux éléments pour faire une visualisation avec "ggplot2" sont :
# Data :"ggplot()", le jeu de données contenant les variables utilisées;
# Aesthetics : "aes()" : les variables à représenter. On peut inclure des couleurs ou tailles 
#                      si elles sont associées à des variables;
# Geometrics : "geom_...()", le type de représentation graphique souhaitée;
# Statistics : "stat_...()", les éventuelles transformations des données pour la représentation souhaitée; 
# Scales : "scale_...()", permet de contrôler le lien entre les données et les "aesthetics"
#                      (modification de couleurs, gestion des axes).

# Data et aesthetics : Ces deux éléments spécifient le jeu de données et les variables 
#                      que l'on souhaite représenter. Le jeu de données est un data-frame 
#                      (ou data-table ou tibble) que l'on renseigne dans la fonction "ggplot()".
#                      Les variables sont spécifiées dans la fonction "aes()". Cette fonction admet
#                      également des arguments tels que "color", "size", "fill". Ces arguments sont 
#                      à utiliser lorsque une couleur ou une taille est définie à partir d'une 
#                      variable du jeu de données. Par exemple, visualiser le prix d'un diamant 
#                      en fonction de son nombre de carats avec une couleur différente selon 
#                      les modalités de la variable "cut" :  
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point() #présentation sans couleur
ggplot(diamonds2)+aes(x=carat, y=price, color=cut)+geom_point() #présentation avec code couleur

# Geometrics : la commande 
ggplot(diamonds2)+aes(x=carat, y=price)
# ne renvoie pas de graphique. Elle spécifie uniquement les variables du jeu de données que 
# l'on souhaite utiliser. L'élément "geom_...()" précise le type de représentation souhaitée.
# Voici une liste de fonctions possibles : "geom_point()", "geom_line()", "geom_abline()", 
# "geom_path()", "geom_text()", "geom_rect()", "geom_polygon()", "geom_segment()", "geom_bar()", 
# "geom_histogram()", "geom_boxplot()", "geom_density()", "geom_contour()", "geom_smooth()" ...
# Chaque fonction "geom_...()" admet également des arguments particuliers permettant de modifier 
# le graphe (couleur, taille de points, épaisseur de traits...). Par exemple :
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point(color="red")
ggplot(diamonds2)+aes(x=cut)+geom_bar(fill="blue")

# Statistics : De nombreux graphiques ne se déduisent pas directement des données,
# elle nécessitent de transformer des variables ou de calculer des indicateurs 
# à partir des variables. Lorsque la transformation est fonctionnelle, il suffit de spécifier 
# cette transformation dans "aes()". Voici un exemple :
D <- data.frame(X=seq(-2*pi, 2*pi, by=0.01))
ggplot(D)+aes(x=X, y=sin(X))+geom_line()
# Les valeurs du sinus ne sont pas dans le jeu de données D. On précise qu'on veut représenter
# en ordonnée la fonction sinus via "y=sin(X)" dans "aes()".

# De nombreuses représentations nécessitent des transformations plus complexes. C'est le cas 
# par exemple de l'histogramme. Les "statistics" permettent de faire ces transformations. Ils sont 
# renseignés dans l'argument "stat" des fonctions "geom_...()". Dans "geom_histogram()", la valeur 
# par défaut est "stat="bin"". Cet argument permet de calculer 4 indicateurs :
# - count : nombre d'observations dans chaque classe;
# - density : densité pour chaque classe;
# - ncount : équivalent à "count" modifié de manière à ce que la valeur maximale soit de 1
# - ndensity : équivalent de `density` modifié de manière à ce que la valeur maximale soit de 1.
# Par défaut, la fonction "geom_histogram()" représente en ordonnée le premier de ces quatre 
# indicateurs ("count"). Ainsi, la commande
ggplot(diamonds2)+aes(x=price)+geom_histogram(bins=40)
# renvoie l'histogramme où figure en ordonnée le nombre d'individus par intervalle 
# (et non la densité), il donne le même résultat que
ggplot(diamonds2)+aes(x=price, y=..count..)+geom_histogram(bins=40)

# Si on souhaite visualiser un autre indicateur sur l'axe des ordonnées, il faut préciser son nom 
# dans la fonction "aes()" en utilisant la format "..nom..". Pour représenter l'histogramme 
# de la densité, on utilise donc 
ggplot(diamonds2)+aes(x=price, y=..density..)+geom_histogram(bins=40)

# Le package "ggplot2" propose une alternative pour obtenir des représentations faisant intervenir
# des transformations des données, il s'agit des fonctions "stat_...()". On peut obtenir 
# les deux histogrammes précédents comme suit :
ggplot(diamonds2)+aes(x=price)+stat_bin(bins=40)
ggplot(diamonds2)+aes(x=price, y=..density..)+stat_bin(bins=40)

# Les fonctions "stat_...()" possèdent un argument "geom". En modifiant cet argument, on change 
# la représentation graphique. Par exemple, la fonction "stat_smooth()" admet par défaut l'argument 
# "geom="smooth"". Il permet de faire un lissage de points avec une bande de confiance. 
# Si on utilise l'argument "geom="line"", le lissage se fera sans la bande de confiance.
# Enfin, avec "geom="point"" le lissage est représenté en pointillé :
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point(size=0.5)+
  stat_smooth(method="loess", size=0.8)
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point(size=0.5)+
  stat_smooth(method="loess", geom="line", color="red", size=0.8)
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point(size=0.5)+
  stat_smooth(method="loess", geom="point", color="red", size=0.8)

# De nombreuses représentations peuvent être obtenues en utilisant différemment 
# les fonctions de type "geom_...()" ou "stat_...()". 
# On pourra par exemple obtenir les graphiques de lissage précédents avec la fonction 
# "geom_smooth()". Voici d'autres fonctions : "stat_identity()", "stat_bin()",
# "stat_density()", "stat_smooth()", "stat_boxplot()".

# Scales : Les "scales" contiennent tous les paramètres qui font le lien entre les données
# et les "aesthetics". Ils permettent généralement d'affiner le graphe en modifiant par exemple
# les palettes de couleurs ou en créant des dégradés de couleurs, ou encore en gérant 
# les axes du graphe. Les fonctions "scales" suivent le schéma suivant :
# - elles commencent par "scale_...()";
# - suivi du nom de l'aesthetics que l'on souhaite modifier (color_, fill_, x_...);
# - et se termine par le nom du scale : manual, identity ...
# On modifie par exemple la couleur des points du graphe précédent comme suit :
ggplot(diamonds2)+aes(x=carat, y=price, color=cut)+geom_point()+
  scale_color_manual(values=c("Fair"="black","Good"="yellow",
                              "Very Good"="blue","Premium"="red","Ideal"="green"))
# Voici d'autres exemples d'utilisation des "scales" :
# - Couleurs d'un diagramme en barre :
p1 <- ggplot(diamonds2)+aes(x=cut)+geom_bar(aes(fill=cut))
p1 #on utilise une couleur différente pour chaque barre
p1 + scale_fill_brewer(palette="Reds") # on change la couleur des barres avec la palette `Reds`

# - Dégradé de couleurs pour un nuage de points : on représente les points "(carat, price)" avec 
# une échelle de couleur définie par la variable numérique continue "depth" :
p2 <- ggplot(diamonds2)+aes(x=carat, y=price)+
       geom_point(aes(color=depth))
p2
# - On modifie le dégradé de couleurs proposé par défaut en définissant un nouveau dégradé 
# allant du jaune au rouge à l'aide de la fonction "scale_color_gradient()" :
p2 + scale_color_gradient(low="yellow", high="red")

# - Gestion des axes et de la légende : On peut modifier la graduation de l'axe des abscisses, 
# le nom de l'axe des ordonnées et celui de la variable de la légende du graphe `p2` avec
p2+scale_x_continuous(breaks=seq(0.5, 3, by=0.5))+
   scale_y_continuous(name="prix")+
   scale_color_gradient("Profondeur")

#### 3. Group et facets ####
# Le package "ggplot2" permet de faire des représentations pour des sous-groupes d'individus
# caractérisés par une ou plusieurs variables. 
# Il y a essentiellement deux manières de faire :
# 1 . On souhaite représenter les sous-groupes d'individus sur un même graphe : on utilise l'argument
#     "group=" dans la fonction `aes()`;
# 2. On souhaite représenter les sous-groupes dans des graphes différents: on utilise les fonctions
#    "facet_grid()" et "facet_wrap()".

# Considérons l'exemple d'un lissage du nuage de points "(carat,price)"
# avec la fonction "geom_smooth()":
ggplot(diamonds2)+aes(x=carat, y=price)+geom_smooth()
# Pour obtenir un lissage pour chaque valeur de la variable "cut", il suffit d'ajouter
# l'argument "group=..." dans "aes()" :
ggplot(diamonds2)+aes(x=carat, y=price, group=cut)+geom_smooth()

# Pour distinguer les groupes, on peut rajouter l'argument "couleur=..." dans "aes()":
ggplot(diamonds2)+aes(x=carat, y=price, group=cut, color=cut)+
  geom_smooth()

# Si l'on veut obtenir les lissages sur des graphes séparés, on utilise les fonctions 
# "facet_grid()" ou "facet_wrap()". Elles admettent comme argument une formule de la forme
#  "var1 ~ var2". Elles renvoient en sortie la représentation souhaitée calculée 
# sur les individus appartenant à chaque croisement des modalités de "var1" et "var2". 
# La principale différence entre ces deux fonctions se situe dans la disposition des graphiques :
# "facet_grid()" produit un tableau de graphes de dimension (nombre de modalités de var1 * nombre
# de modalités de var2). Chaque graphe correspond à la représentation des individus 
# possédant une modalité de var1 et une modalité de var2. 
# "facet_wrap" calcule tous les croisements et représente les graphes associés les uns à la suite
# des autres. Voici une illustration :
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point()+
                  geom_smooth(method="lm")+facet_grid(color~cut)
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point()+
                  geom_smooth(method="lm")+facet_wrap(color~cut)
# "facet_grid()" propose une représentation plus cohérente lorsqu'on est en 
# présence de deux variables avec peu de modalités. Lorsqu'on est en présence 
# d'une seule variable, ou lorsqu'une variable admet beaucoup de modalités, 
# il est préférable d'utiliser "facet_wrap()". Voici un exemple d'utilisation 
# de "facet_wrap()" selon une seule variable :
ggplot(diamonds2)+aes(x=carat, y=price, color=cut)+geom_smooth()+
  facet_wrap(~cut, nrow=2)

# Remarque : pour dessiner plusieurs graphiques de la même forme dans une même 
# fenêtre, il est toujours préférable de créer une variable "group" ou bien 
# d'utiliser les fonctions "facet_grid()" et "facet_wrap()". 
# Cependant, il est aussi possible de faire figurer des graphiques différents 
# dans une même fenêtre. Pour cela, on définit dans un premier temps 
# les graphiques puis on les organise avec la fonction "grid.arrange()" du
# package "gridExtra". Par exemple :
gr1 <- ggplot(diamonds2)+aes(x=cut)+geom_bar() # 1er graphe
gr1
gr2 <- ggplot(diamonds2)+aes(x=price)+geom_histogram() # 2e graphe
gr2
library(gridExtra)
grid.arrange(gr1, gr2, ncol=2, nrow=1) # organisation des graphes


#### 4. Compléments ####
# Nous avons présenté la structure "ggplot2" selon 
# "ggplot(...)" + "aes(...)" + "geom_...(...)" + ...
# La syntaxe est en réalité plus flexible. On peut par exemple spécifier les "aes"
# dans "ggplot()" ou dans les "geom_...()". Les trois instructions suivantes produiront 
# par exemple le même graphe :
ggplot(diamonds2)+aes(x=carat, y=price)+geom_point()

ggplot(diamonds2, aes(x=carat, y=price))+geom_point()

ggplot(diamonds2)+geom_point(aes(x=carat, y=price))

# Il est également possible de produire des représentations graphiques à partir de 
# plusieurs jeux de données. Voici un exemple :
X <- seq(-2*pi,2*pi,by=0.001)
Y1 <- cos(X)
Y2 <- sin(X)
donnees1 <- data.frame(X,Y1)
donnees2 <- data.frame(X,Y2)
# On représente les deux fonctions sur le même graphe en utilisant 
ggplot(donnees1)+geom_line(aes(x=X, y=Y1))+
    geom_line(data=donnees2, aes(x=X, y=Y2), color="red")

# Lorsqu'on souhaite utiliser une variable qui commence par un chiffre ou un caractère
# spécial dans la fonction `aes()`, il faut mettre cette variable entre 
# deux accents graves (backquotes). Par exemple, on obtient le nuage de points
# (100m,1500m) du jeu de données `decathlon` avec 
library(FactoMineR) #Pour obtenir le jeu de données
data("decathlon")
ggplot(decathlon)+aes(x=`100m`, y=`1500m`)+geom_point()

# Il existe un grand nombre d'autres fonctions proposées par `ggplot2`. On pourra
# citer notamment `ggtitle()` qui permet d'ajouter un titre au graphique. 
# L'environnement par défaut du graphe est défini par la fonction `theme_grey()`,
# mais il est facile de changer ce thème :
p <- ggplot(diamonds2)+aes(x=carat, y=price, color=cut)+geom_point()
p
p + theme_bw()
p + theme_classic()
p + theme_grey()
p + theme_minimal()
# D'autres thèmes sont disponible dans le package `ggthemes`.
# Enfin la fonction `qplot()` est l'analogue pour `ggplot2` de la fonction
# `plot()` pour les graphiques classiques. Elle est très simple à utiliser :
qplot(data=diamonds2, x=carat, y=price, geom=c("point", "smooth"), facets=color~cut)

#### Exportation d'un graphique ####
# Pour exporter un graphique `ggplot2`, on peut utiliser la fonction `ggsave()` :
monplot <- qplot(data=diamonds2, x=carat, y=price, geom=c("point", "smooth"), 
                 facets=color~cut)
ggsave("mon_graphique.pdf", plot = monplot, width = 11, height = 8)

#### 5. Les graphiques interactifs ####
# De nombreux packages permettent la construction de graphiques interactifs
# où le survol du graphe avec la souris affiche des informations complémentaires, où il 
# est possible de zoomer pour sélectionner une partie du graphique, etc.
# En effet, depuis l'arrivée du package `htmlwidgets`, de plus en plus de fonctionnalités
# de librairies `javascript` sont accessibles sous R. 
# La page `http://www.htmlwidgets.org/` liste la plupart des packages dans l'onglet
# `showcase` et présente des exemples de graphiques dans l'onglet `Gallery`.

# Présentons par exemple le package `rAmCharts` qui reprend les principales fonctions
# graphiques de base de R. Le nom de la fonction est `am` suivi du nom de 
# la fonction R avec la première lettre en majuscule (`amBarplot()`, amHist(), ...).
# Voici un exemple pour construire des boîtes à moustaches

library(rAmCharts)
# Importer la bd ``ozone.txt''
ozone <- read.table(file.choose(), header=TRUE, stringsAsFactors=TRUE)
amBoxplot(maxO3 ~ vent, data = ozone, export = TRUE)
# En survolant le graphique avec la souris, on obtiendra différentes informations,
# par exemple les points aberrants, les quantiles, ...

# Il est également possible de représenter des données temporelles, de modifier la plage
# de temps, et de voir quelles valeurs sont prises à une date donnée ...
data(data_stock_2)
str(data_stock_2)
amTimeSeries(data_stock_2, "date", c("ts1", "ts2"))

# Si on construit des graphiques avec `ggplot2`, on peut réaliser le même 
# type de représentation interactive avec le package `plotly`. L'utilisation 
# est très simple : une fois le graphe `ggplot` construit, il suffit 
# de lancer `ggplotly()` :
ggplot(ozone) + aes(x=T12,y=maxO3, color=vent) + geom_point()
library(plotly)
ggplotly()
# Il est également possible de construire des graphiques animés avec `plotly`
# ou encore le package `gganimate`, ... 
