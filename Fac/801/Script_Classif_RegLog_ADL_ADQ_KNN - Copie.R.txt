
rm(list = ls())

#### Classifieurs Régression logistique binaire, ADL, ADQ et k-NN ####

library(MASS)
library(class)
library(sampling)

#chargement des données heart.xlsx
library(xlsx)
heart <- read.xlsx(file.choose(), sheetIndex=1, 
                   header=TRUE, stringsAsFactors=TRUE)

str(heart)

#on transforme les variables explicatives qualitatives en variables numériques
XX <- model.matrix(coeur ~., data=heart)[, -1] #Cette fonction construit la matrice de design en remplaçant 
                                                #chacune des variables qualitatives par les variables indicatrices 
                                                #de ses modalités (la première modalité est supprimée par défaut);
                                                #On supprime la première colonne correspondant à l'intercept

heart.num.data <- cbind(as.data.frame(XX), coeur = as.factor(heart[,"coeur"])) 
#bd constituée que de variables explicatives numériques 
#et une variable réponse qualitative (binaire) 

str(heart.num.data)

#On compare les 4 classifieurs en terme d'erreur de classification, 
#estimée par validation croisée : train + test

#On découpe l'échantillon en deux parties : train + test, avec échantillonnage stratifié
index <- 1:nrow(heart.num.data)
l <- 3 #(l-1)/l d'observations pour l'apprentissage et 1/l d'observations pour le test
mod.coeur <- as.vector(unique(heart.num.data$coeur)) #les modalités de la variable réponse "coeur"
table(heart.num.data$coeur)[mod.coeur]
size <- as.vector(table(heart.num.data$coeur)[mod.coeur]/l) #on veut 1/l observations pour le test 
s <- strata(heart.num.data, stratanames="coeur", size=size, method="srswor")
test.set.index <- s$ID_unit
heart.test.set <- heart.num.data[test.set.index,]
heart.train.set <- heart.num.data[- test.set.index,]

#### erreur du classifieur RegLog ####
modele.RegLog <- glm(formula = coeur ~ ., data = heart.train.set, family = binomial)
pred.proba <- predict(object = modele.RegLog, newdata = heart.test.set, type = "response")
pred.moda <- factor(ifelse(pred.proba > 0.5,"presence","absence"))
err.classif.RegLog <- mean(!(pred.moda == heart.test.set$coeur))
err.classif.RegLog

#erreur du classifieur ADL :
modele.ADL <- lda(formula = coeur ~ ., data = heart.train.set)
ADL.pred <- predict(object = modele.ADL, newdata = heart.test.set)
err.classif.ADL <- mean(!(ADL.pred$class == heart.test.set$coeur))
print(err.classif.ADL)

#### erreur du classifieur ADQ : ####
modele.ADQ <- qda(formula = coeur ~ ., data = heart.train.set)
ADQ.pred <- predict(object = modele.ADQ, newdata = heart.test.set)
err.classif.ADQ <- mean(!(ADQ.pred$class == heart.test.set$coeur))
print(err.classif.ADQ)

#### erreur du classifieur k-NN : ####
#normalisation des variables explicatives
heart_X_n <- as.data.frame(scale(heart.num.data[,!(colnames(heart.num.data)=="coeur")]))

#bd heart avec variables explicatives normalisées
heart_n <- as.data.frame(cbind(heart_X_n,"coeur"=heart.num.data$coeur)) 

heart.test.set <- heart_n[test.set.index, ]
heart.train.set <- heart_n[- test.set.index, ]

train.X <- heart.train.set[, !(colnames(heart.train.set) == c("coeur"))]
test.X <- heart.test.set[, !(colnames(heart.test.set) == c("coeur"))]

train.coeur <- heart.train.set[, (colnames(heart.train.set) == c("coeur"))]

#recherche du nombre optimal k de voisins
err.classif.KNN <- NULL
for (k in seq(from = 1, to = 50, by = 1) )
{  
knn.pred <- knn(train = train.X, test = test.X,  cl = train.coeur, prob = TRUE, k = k)
err.classif.KNN[k] <- mean(!(knn.pred == heart.test.set$coeur))
}

plot(err.classif.KNN, type="o")
k_opt <- which.min(err.classif.KNN)
k_opt

knn.pred.opt <- knn(train = train.X, test = test.X, cl = train.coeur, prob = TRUE, k = k_opt)
err.classif.KNN_opt <- mean(!(knn.pred.opt == heart.test.set$coeur))
err.classif.KNN_opt

##comparaison
err.classif.RegLog
err.classif.ADL
err.classif.ADQ
err.classif.KNN_opt

#### Ces estimations dépendent de la partition apprentissage/test, ####
## et elles sont imprécises si n est petit, une solution possible
## est de répéter la méthode pour plusieurs partitions différentes, 
## et prendre la moyennes des estimations, comme suit :
# Pour éviter la boucle, on définit la fonction donnant l'estimation de l'erreur de classification
# pour une partition donnée pour chacun des classifieurs RegLog, ADL et ADQ, et utiliser ensuite la
# fonction de R "replicate()" :
# Partition avec 1/3 pour le test et 2/3 pour l'apprentissage,
# en utilisant un échantillonnage stratifié, pour que la distribution de la 
# la variable cible "coeur" reste la même pour les trois bd : la base complète, la base d'apprentissage et la base de test;

#voici comment réaliser un échantillonnage stratifié (fortement recommandé pour estimer l'erreur de classification) :
library(sampling)
n <- nrow(heart.num.data)
mod.coeur<-as.vector(unique(heart.num.data$coeur))#les modalités de la variable réponse "coeur"
table(heart.num.data$coeur)[mod.coeur]
size <- as.vector(table(heart.num.data$coeur)[mod.coeur]/3) #on veut 1/3 d'observations pour le test 
s <- strata(heart.num.data, stratanames="coeur", size=size, method="srswor")
test.set.index <- s$ID_unit
heart.test.set <- heart.num.data[test.set.index, ]
heart.train.set <- heart.num.data[- test.set.index, ]

#vérification
table(heart.num.data$coeur)/nrow(heart.num.data)
table(heart.train.set$coeur)/nrow(heart.train.set)
table(heart.test.set$coeur)/nrow(heart.test.set)

#la fonction donnant l'erreur de classification pour une partition donnée
err_classif <- function(l=3){
  #échantillonnage stratifié
  mod.coeur <- as.vector(unique(heart.num.data$coeur))#les modalités de la variable "coeur"
  size <- as.vector(table(heart.num.data$coeur)[mod.coeur]/l) 
  s <- strata(heart.num.data, stratanames="coeur", size=size, method="srswor")
  test.set.index <- s$ID_unit
  heart.test.set <- heart.num.data[test.set.index, ]
  heart.train.set <- heart.num.data[- test.set.index, ]
  
  ## erreur du classifieur RegLog ##
  modele.RegLog <- glm(formula = coeur ~ ., data = heart.train.set, family = binomial)
  pred.proba <- predict(object = modele.RegLog, newdata = heart.test.set, type = "response")
  pred.moda <- factor(ifelse(pred.proba > 0.5,"presence","absence"))
  err.classif.RegLog <- mean(!(pred.moda == heart.test.set$coeur))
  
  #erreur du classifieur ADL :
  modele.ADL <- lda(formula = coeur ~ ., data = heart.train.set)
  ADL.pred <- predict(object = modele.ADL, newdata = heart.test.set)
  err.classif.ADL <- mean(!(ADL.pred$class == heart.test.set$coeur))
  
  #### erreur du classifieur ADQ : ####
  modele.ADQ <- qda(formula = coeur ~ ., data = heart.train.set)
  ADQ.pred <- predict(object = modele.ADQ, newdata = heart.test.set)
  err.classif.ADQ <- mean(!(ADQ.pred$class == heart.test.set$coeur))
  
  return(c(err.classif.RegLog,err.classif.ADL,err.classif.ADQ))
}

err_classif(3)

M <- 200
resultats <- replicate(M, err_classif(3))
EC_RegLog_ADL_ADQ <-rowMeans(resultats)
names(EC_RegLog_ADL_ADQ) <- c("ErC RegLog", "ErC ADL", "ErC ADQ")
#Estimations plus précise de l'erreur de classification de chacun des classifieurs :
EC_RegLog_ADL_ADQ

#comparaison des classifieurs kNN
#normalisation des variables explicatives
heart_X_n <- as.data.frame(scale(heart.num.data[,!(colnames(heart.num.data)=="coeur")]))

#bd heart avec variables explicatives normalisées
heart_n <- as.data.frame(cbind(heart_X_n,"coeur"=heart.num.data$coeur)) 

#fonction donnant l'erreur de classification d'un classifieur kNN, pour 
# un k donné, et pour une partition donnée
err_classif_KNN <- function(l=3,k){
  #Échantillonnage stratifié
  mod.coeur <- as.vector(unique(heart_n$coeur))#les modalités de la variable "coeur"
  size <- as.vector(table(heart_n$coeur)[mod.coeur]/l) 
  s <- strata(heart_n, stratanames="coeur", size=size, method="srswor")
  test.set.index <- s$ID_unit
  heart.test.set <- heart_n[test.set.index, ]
  heart.train.set <- heart_n[- test.set.index, ]
  
  train.X <- heart.train.set[,!(colnames(heart.train.set) == c("coeur"))]
  test.X <- heart.test.set[,!(colnames(heart.test.set) == c("coeur"))]
  train.coeur <- heart.train.set[,(colnames(heart.train.set) == c("coeur"))]
  
  knn.pred <- knn(train = train.X, test = test.X,  cl = train.coeur, prob = TRUE, k = k)
  errC <- mean(!(knn.pred == heart.test.set$coeur))
  
  return(errC)
}

err_classif_KNN(l=3,k=1)

M <- 500 #nombre de réplications de la méthode VC
mean(replicate(M, err_classif_KNN(3,1)))

err.classif.K <- NULL
v_k <- NULL #les valeurs de k considérées
i <- 0
for (k in seq(from=20, to=60, by=1))
{ i <- i+1
  v_k[i] <- k
  err.classif.K[i] <- mean(replicate(M, err_classif_KNN(l=3,k=k)))
}

plot(v_k, err.classif.K, type="o")
min(err.classif.K)
i_k_opt <- which.min(err.classif.K)
k_opt <- v_k[i_k_opt]
k_opt

#comparaison des 4 classifieurs
err_classifieurs <-c(EC_RegLog_ADL_ADQ, "ErC KNN" = min(err.classif.K))
err_classifieurs

#################################################################################
#### Classifieurs (multi-class) RegLogMultinom, ADL, ADQ et k-NN : iris data ####
str(iris) 
levels(iris$Species)

#on cherche à prédire les 3 modalités de la variable réponse ``Species'' en fonction
#de quatre variables explicatives numériques

#On compare les 4 classifieurs en terme de l'erreur de classification 
#estimée par validation croisée : train + test
#On découpe l'échantillon en deux parties : train + test,
#avec échantillonnage stratifié :

l<-3
mod.Species <- as.vector(unique(iris$Species))#les modalités de la variable "Species"
size <- as.vector(table(iris$Species)[mod.Species]/l) 
s <- strata(iris, stratanames="Species", size=size, method="srswor")
test.set.index <- s$ID_unit
iris.test.set <- iris[test.set.index, ]
iris.train.set <- iris[- test.set.index, ]

#vérifications
table(iris$Species)/nrow(iris)
table(iris.train.set$Species)/nrow(iris.train.set)
table(iris.test.set$Species)/nrow(iris.test.set)

#### erreur du classifieur RegLogMultinom ####
library(nnet)
modele.RegLogM <- multinom(formula = Species ~ ., data = iris.train.set, maxit = 3000) 
RegLogM.pred <- predict(object = modele.RegLogM, newdata = iris.test.set)
err.classif.RegLogM <- mean(!(RegLogM.pred == iris.test.set$Species))
print(err.classif.RegLogM)

#### erreur du classifieur ADL : ####
modele.ADL <- lda(formula = Species ~ ., data = iris.train.set)
ADL.pred <- predict(object = modele.ADL, newdata = iris.test.set)
err.classif.ADL <- mean(!(ADL.pred$class == iris.test.set$Species))
print(err.classif.ADL)

#### erreur du classifieur ADQ : ####
modele.ADQ <- qda(formula = Species ~ ., data = iris.train.set)
ADQ.pred <- predict(object = modele.ADQ, newdata = iris.test.set)
err.classif.ADQ <- mean(!(ADQ.pred$class == iris.test.set$Species))
print(err.classif.ADQ)

#### erreur du classifieur k-NN : ####
#normalisation des variables explicatives
iris_X_n <- as.data.frame(scale(iris[,!(colnames(iris)=="Species")]))
iris_n <- as.data.frame(cbind(iris_X_n,"Species"=iris$Species))
iris_n.test.set <- iris_n[test.set.index, ]
iris_n.train.set <- iris_n[test.set.index, ]

train.X <- iris_n.train.set[, !(colnames(iris_n.train.set) == c("Species"))]
test.X <- iris_n.test.set[, !(colnames(iris_n.test.set) == c("Species"))]
train.Species <- iris_n.train.set[, (colnames(iris_n.train.set) == c("Species"))]

#recherche du nombre k optimal de voisins
err.classif.KNN <- NULL
v_k <- NULL
i <- 0
for (k in seq(from = 1, to = 23, by = 1) )
{  i <- i+1
  v_k[i] <- k
  knn.pred <- knn(train = train.X, test = test.X,  cl = train.Species, k = k)
  err.classif.KNN[i] <- mean(!(knn.pred == iris_n.test.set$Species))
}

plot(x=v_k, y=err.classif.KNN, xlab="Le nombre de voisins", ylab="L'erreur de classification", type="o")

err.classif.KNN_opt <- min(err.classif.KNN)
i_k_opt <- which.min(err.classif.KNN)
k_opt <- v_k[i_k_opt]
k_opt

##comparaison
err.classif.RegLogM
err.classif.ADL
err.classif.ADQ
err.classif.KNN_opt

#### Ces estimations dépendent de la partition apprentissage/test, ####
## et elles sont imprécises si n est petit, une solution possible
## est de répéter la méthode pour plusieurs partitions différentes, 
## et prendre la moyennes des estimations, comme suit :
# Pour éviter la boucle, on définit la fonction donnant l'estimation de l'erreur de classification
# pour une partition donnée pour chacun des classifieurs RegLog, ADL et ADQ, et utiliser ensuite la
# fonction de R "replicate()" :
# Partition avec 1/3 pour le test et 2/3 pour l'apprentissage,
# en utilisant un échantillonnage stratifié, pour que la distribution de la 
# la variable cible "Species" reste la même pour les trois bd : la bd complète, la bd d'apprentissage et la bd de test.
#voici comment réaliser un échantillonnage stratifié
n <- nrow(iris) #nombre d'observations
mod.Species <- as.vector(unique(iris$Species))#les modalités de la variable "Species"
table(iris$Species)[mod.Species]
size <- as.vector(table(iris$Species)[mod.Species]/3) 
s <- strata(iris, stratanames="Species", size=size, method="srswor")
test.set.index <- s$ID_unit
iris.test.set <- iris[test.set.index, ]
iris.train.set <- iris[- test.set.index, ]

#vérification
table(iris$Species)/nrow(iris)
table(iris.train.set$Species)/nrow(iris.train.set)
table(iris.test.set$Species)/nrow(iris.test.set)

err_classif <- function(l=3){
  #échantillonnage stratifié
  mod.Species <- as.vector(unique(iris$Species))#les modalités de la variable "Species"
  table(iris$Species)[mod.Species]
  size <- as.vector(table(iris$Species)[mod.Species]/l) 
  s <- strata(iris, stratanames="Species", size=size, method="srswor")
  test.set.index <- s$ID_unit
  iris.test.set <- iris[test.set.index, ]
  iris.train.set <- iris[- test.set.index, ]
  
  #erreur du classifieur RegLogM
  modele.RegLogM <- multinom(formula = Species ~ ., data = iris.train.set, maxit=3000) 
  RegLogM.pred <- predict(object = modele.RegLogM, newdata = iris.test.set)
  err.classif.RegLogM <- mean(!(RegLogM.pred == iris.test.set$Species))
  
  #### erreur du classifieur ADL : 
  modele.ADL <- lda(formula = Species ~ ., data = iris.train.set)
  ADL.pred <- predict(object = modele.ADL, newdata = iris.test.set)
  err.classif.ADL <- mean(!(ADL.pred$class == iris.test.set$Species))
  
  #### erreur du classifieur ADQ : 
  modele.ADQ <- qda(formula = Species ~ ., data = iris.train.set)
  ADQ.pred <- predict(object = modele.ADQ, newdata = iris.test.set)
  err.classif.ADQ <- mean(!(ADQ.pred$class == iris.test.set$Species))
  
  return(c(err.classif.RegLogM,err.classif.ADL,err.classif.ADQ))
}

err_classif(3)

M <- 1000
resultats <- replicate(M, err_classif(3))
EC_RegLogM_ADL_ADQ <-rowMeans(resultats)
names(EC_RegLogM_ADL_ADQ) <- c("ErC RegLogM", "ErC ADL", "ErC ADQ")
#Estimation plus précise de l'erreur de classification de chacun des classifieurs
EC_RegLogM_ADL_ADQ


#normalisation des variables explicatives :
iris_X_n <- as.data.frame(scale(iris[, !(colnames(iris)=="Species")]))
iris_n <- as.data.frame(cbind(iris_X_n, Species=iris$Species))

#comparaison des classifieurs kNN :
err_classif_KNN <- function(l=3,k){
  #échantillonnage stratifié
  mod.Species <- as.vector(unique(iris_n$Species))#les modalités de la variable "Species"
  table(iris_n$Species)[mod.Species]
  size <- as.vector(table(iris_n$Species)[mod.Species]/3) 
  s <- strata(iris_n, stratanames="Species", size=size, method="srswor")
  test.set.index <- s$ID_unit
  iris.test.set <- iris_n[test.set.index, ]
  iris.train.set <- iris_n[- test.set.index, ]
  train.X <- iris.train.set[,!(colnames(iris.train.set) == c("Species"))]
  test.X <- iris.test.set[,!(colnames(iris.test.set) == c("Species"))]
  train.Species <- iris.train.set[,(colnames(iris.train.set) == c("Species"))]
  knn.pred <- knn(train = train.X, test = test.X,  cl = train.Species, prob = TRUE, k = k)
  errC <- mean(!(knn.pred == iris.test.set$Species))
  return(errC)
}

err_classif_KNN(l=3,k=1)

M <- 1000
mean(replicate(M, err_classif_KNN(3,1)))

err.classif.K <- NULL
v_k <- NULL
i <- 0
for (k in seq(from = 3, to = 20, by = 1))
{ i <- i+1
  v_k[i] <- k #le nombre de voisins
  err.classif.K[i] <- mean(replicate(M, err_classif_KNN(l=3,k=k)))
 print(k)
}

plot(x=v_k, y=err.classif.K, xlab = "Le nombre de voisins k", ylab = "L'erreur de classification", type="o")
min(err.classif.K)
i_k_opt <- which.min(err.classif.K)
k_opt <- v_k[i_k_opt]
k_opt

#comparaison des 4 classifieurs
err_classifieurs <-c(EC_RegLogM_ADL_ADQ, "ErC KNN"=min(err.classif.K))
err_classifieurs

