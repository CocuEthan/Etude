
#### 1. Classification binaire en grande dimension par régression logistique binomial pénalisée ####

#vider la mémoire
rm(list = ls())

#installer et charger le package xlsx
library(xlsx)
#importation des données heart.xlsx
heart <- read.xlsx(file.choose(), sheetIndex = 1, header = T, stringsAsFactors = TRUE)
str(heart)

#variable réponse : ``coeur'' qualitative à deux modalités
#variables explicatives : 3 numériques et 4 qualitatives

#dans ce qui suit on transforme toutes les variables explicatives qualitatives en numériques :
XX <- model.matrix(coeur ~., data = heart)[,-1] #cette fonction construit la matrice de design en remplaçant 
#chacune des variables qualitatives pour les indicatrices 
#de ses modalités (la première modalité est supprimée)
#on supprime la première colonne correspondant à l'intercept
heart.num.data <- cbind(as.data.frame(XX), coeur = as.factor(heart[,"coeur"])) #bd constituée que de variables explicatives numériques 
str(heart.num.data)

#### Régression logistique binomial Ridge ####
library(glmnet)
reg.ridge <- glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]), 
                    y = heart.num.data[, "coeur"], family = "binomial", alpha = 0) 
                         #alpha = 0 correspond au Ridge
par(mfrow = c(1,1))
plot(reg.ridge, label = TRUE)
plot(reg.ridge, xvar = "lambda", label = TRUE, lwd = 2)
n <- nrow(heart.num.data)
reg.cvridge <- cv.glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]),
                         y = heart.num.data[, "coeur"], family = "binomial", 
                         type.measure = "class", nfolds = n, alpha = 0)
bestlam <- reg.cvridge$lambda.min
bestlam
plot(reg.cvridge)
min(reg.cvridge$cvm) #erreur de prévision du modèle ridge optimal 
coef(reg.cvridge)

#comparaison avec le modèle de RegLog complet
reg.cvridge <- cv.glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]),
                         y = heart.num.data[, "coeur"], family = "binomial", 
                         type.measure = "class", nfolds=n, alpha = 0)
erreur.classif.ridge.opt <- min(reg.cvridge$cvm) #erreur de prévision du modèle ridge optimal 
erreur.classif.ridge.opt
library(boot)
modele.RegLog.complet <- glm(formula = coeur ~., data = heart.num.data, family = binomial)
cout <- function(r, pi) mean(abs(r-pi) > 0.5) #la fonction de perte
erreur.classif.RegLog.complet <- cv.glm(data = heart.num.data, 
                                    glmfit =  modele.RegLog.complet, 
                                    cost = cout, K = n)$delta[1]

erreur.classif.ridge.opt
erreur.classif.RegLog.complet

#### Régression logistique binomial Lasso ####
reg.lasso <- glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]), 
                    y = heart.num.data[, "coeur"], family = "binomial", alpha = 1)
                  #alpha = 1 correspond au lasso
par(mfrow = c(1,1))
plot(reg.lasso, label = TRUE)
plot(reg.lasso, xvar = "lambda", label = TRUE, lwd = 2)
reg.cvlasso <- cv.glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]),
                         y = heart.num.data[, "coeur"], family = "binomial", 
                         type.measure = "class", nfolds=n, alpha = 1)
bestlam <- reg.cvlasso$lambda.min
bestlam
plot(reg.cvlasso)
min(reg.cvlasso$cvm) #erreur de prévision du modèle ridge optimal 
coef(reg.cvlasso)

#comparaison avec le modèle de RegLog complet
reg.cvlasso <- cv.glmnet(x = scale(heart.num.data[, !(colnames(heart.num.data) == "coeur")]),
                         y = heart.num.data[, "coeur"], family = "binomial", 
                         type.measure = "class", nfolds = n, alpha = 1)
erreur.classif.lasso.opt <- min(reg.cvlasso$cvm) #erreur de classification du modèle lasso optimal 
erreur.classif.lasso.opt
library(boot)
modele.RegLog.complet <- glm(formula = coeur ~., data = heart.num.data, family = binomial)
cout <- function(r, pi) mean(abs(r-pi) > 0.5)
erreur.classif.RegLog.complet <- cv.glm(data = heart.num.data, 
                                        glmfit =  modele.RegLog.complet, 
                                        cost = cout, K = n)$delta[1]

erreur.classif.lasso.opt
erreur.classif.RegLog.complet

###########################################################################################################

#### 2. Classification multi-groupe en grande dimension par régression logistique multinomial pénalisée ####
str(iris) 
View(iris)
levels(iris$Species)

#on cherche à expliquer/prédire les 3 modalités de la variable réponse ``Species'' en fonction
#de quatre variables explicatives numériques

#### Régression logistique multinomial Ridge ####
library(glmnet)
str(iris)
n <- nrow(iris)
reg.ridge <- glmnet(x = scale(iris[, !(colnames(iris) == "Species")]), 
                    y = iris[, "Species"], family = "multinomial", 
                    type.multinomial = "grouped", nfolds=n, alpha = 0)
par(mfrow = c(1,1))
plot(reg.ridge, label = TRUE)
plot(reg.ridge, xvar = "lambda", label = TRUE, lwd = 2)
reg.cvridge <- cv.glmnet(x = scale(iris[, !(colnames(iris) == "Species")]),
                         y = iris[, "Species"], family = "multinomial", 
                         type.measure = "class", 
                         type.multinomial = "grouped", nfolds=n, alpha = 0)
bestlam <- reg.cvridge$lambda.min
bestlam
plot(reg.cvridge)
min(reg.cvridge$cvm) #erreur de classification du modèle ridge optimal 
coef(reg.cvridge)

#### Régression logistique multinomial Lasso ####
reg.lasso <- glmnet(x = scale(iris[, !(colnames(iris) == "Species")]), 
                    y = iris[, "Species"], family = "multinomial", 
                    type.multinomial = "grouped", nfolds=n, alpha = 1)
par(mfrow = c(1,1))
plot(reg.lasso, label = TRUE)
plot(reg.lasso, xvar = "lambda", label = TRUE, lwd = 2)
reg.cvlasso <- cv.glmnet(x = scale(iris[, !(colnames(iris) == "Species")]), 
                         y = iris[, "Species"], family = "multinomial",
                         type.measure = "class", nfolds = n,
                         type.multinomial = "grouped", alpha = 1)
bestlam <- reg.cvlasso$lambda.min
bestlam
plot(reg.cvlasso)
min(reg.cvlasso$cvm) #erreur de classification du modèle lasso optimal 
coef(reg.cvlasso)

indices <- !(coef(reg.cvlasso)$setosa == 0)
indices.var.select <- indices[2:length(indices)]

#les variables explicatives sélectionnées par le lasso
colnames(iris[, !(colnames(iris) == "Species")])[indices.var.select]


# Application to Gene Expression Data (des données de grande dimension : 2308 variables explicatives numériques, 
# pour expliquer/prédire une variable réponse à 4 modalités)
library(ISLR)
names(Khan)
dim(Khan$xtrain)
dim(Khan$xtest)
length(Khan$ytrain)
length(Khan$ytest)
table(Khan$ytrain)
table(Khan$ytest) # la variable réponse est à quatre modalités

Khan.train.data <- data.frame(x = Khan$xtrain, y = as.factor(Khan$ytrain))
Khan.test.data <- data.frame(x = Khan$xtest, y = as.factor(Khan$ytest))

Khan.data <- rbind(Khan.train.data, Khan.test.data)
dim(Khan.data)
str(Khan.data)

#### Régression logistique multinomial Lasso ####
n <- nrow(Khan.data)
reg.lasso <- glmnet(x = scale(Khan.data[, !(colnames(Khan.data) == "y")]), 
                    y = Khan.data[, "y"], family = "multinomial", 
                    type.multinomial = "grouped", nfolds=n, alpha = 1)

par(mfrow = c(1,1))
plot(reg.lasso, label = TRUE)
plot(reg.lasso, xvar = "lambda", label = TRUE, lwd = 2)
reg.cvlasso <- cv.glmnet(x = scale(Khan.data[, !(colnames(Khan.data) == "y")]), 
                         y = Khan.data[, "y"], family = "multinomial",
                         type.measure = "class", 
                         type.multinomial = "grouped", 
                         nfolds = n, alpha = 1)

bestlam <- reg.cvlasso$lambda.min
bestlam
plot(reg.cvlasso)
min(reg.cvlasso$cvm) #erreur de classification du modèle lasso optimal 

coef(reg.cvlasso)

indices <- !(coef(reg.cvlasso)$"2" == 0)
indices.var.select <- indices[2:length(indices)]
#les variables explicatives sélectionnées par le lasso
noms.var.lasso <- colnames(Khan.data[, !(colnames(Khan.data) == "y")])[indices.var.select]

Khan.data2 <- Khan.data[, noms.var.lasso]
Khan.data2 <- as.data.frame(cbind(Khan.data2, y = Khan.data$y))
str(Khan.data2)

#### Régression logistique multinomial Ridge ####
reg.ridge <- glmnet(x = scale(Khan.data[, !(colnames(Khan.data) == "y")]), 
                    y = Khan.data[, "y"], family = "multinomial", 
                    type.multinomial = "grouped", nfolds=n, alpha = 0)

par(mfrow = c(1,1))
plot(reg.ridge, label = TRUE)
plot(reg.ridge, xvar = "lambda", label = TRUE, lwd = 2)
reg.cvridge <- cv.glmnet(x = scale(Khan.data[, !(colnames(Khan.data) == "y")]), 
                         y = Khan.data[, "y"], family = "multinomial",
                         type.measure = "class", 
                         type.multinomial = "grouped", 
                         nfolds = 10, alpha = 0)

bestlam <- reg.cvridge$lambda.min
bestlam
plot(reg.cvridge)
min(reg.cvridge$cvm) #erreur de classification du modèle ridge optimal 
coef(reg.cvridge)


