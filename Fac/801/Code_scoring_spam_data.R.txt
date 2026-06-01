
rm(list = ls())

library(kernlab)
library(MASS) 
library(randomForest) 
library(rpart)
library (e1071)
library(class)
library(ROCR) 

data(spam)
spam.data <- spam
#57 variables explicatives numériques
#une variable réponse qui s'appelle "type" à deux modalités ("nonspam","spam")

dim(spam.data)

#On partage la base en deux parties : train.set et test.set (échantillonnage stratifié)
library(sampling)
set.seed(12)
mod.type <- as.vector(unique(spam.data$type))#les modalités de la variable réponse "type"
table(spam.data$type)[mod.type]
size <- as.vector(table(spam.data$type)[mod.type]/3) #on veut 1/3 d'observations pour le test 
s <- strata(spam.data, stratanames="type", size=size, method="srswor")
test.set.index <- s$ID_unit
spam.test.set <- spam.data[test.set.index, ] #ensemble de test
spam.train.set <- spam.data[- test.set.index, ] #ensemble d'apprentissage

#On compare les scores construits par RegLog, lda, qda, forêts aléatoires,
#arbres de décision et svm 
modele.logit <- glm(formula = 
                      ~ ., data = spam.train.set, family = binomial)
modele.lda <- lda(formula = type ~., data = spam.train.set)
modele.qda <- qda(formula = type ~., data = spam.train.set)
modele.RF <- randomForest(formula = type ~., data = spam.train.set)
modele.arbre <- rpart(formula = type ~., data = spam.train.set)
tune.out <- tune(svm, type ~ ., data = spam.train.set, kernel = "linear", scale = TRUE,
                 ranges = list(cost = c(2^(-2) ,2^(-1), 1, 2^2, 2^3, 2^4, 2^5)))
tune.out
modele.svm <- tune.out$best.model

#On calcule ensuite pour chaque modèle le score des individus de l'échantillon de test
Score.logit <- predict(modele.logit, newdata = spam.test.set, type = "response")
Score.lda <- predict(modele.lda, newdata = spam.test.set, type = "prob")$posterior[, 2]
Score.qda <- predict(modele.qda, newdata = spam.test.set, type = "prob")$posterior[, 2]
Score.RF <- predict(modele.RF, newdata = spam.test.set, type = "prob")[, 2]
Score.arbre <- predict(modele.arbre, newdata = spam.test.set, type = "prob")[, 2]
Score.svm <- attributes(predict(modele.svm, newdata = spam.test.set, scale = TRUE, 
                                  decision.values = TRUE))$decision.values

#On trace maintenant les 6 courbes ROC 
S1.pred <- prediction(Score.logit, spam.test.set$type)
S2.pred <- prediction(Score.lda, spam.test.set$type)
S3.pred <- prediction(Score.qda, spam.test.set$type)
S4.pred <- prediction(Score.RF, spam.test.set$type)
S5.pred <- prediction(Score.arbre, spam.test.set$type)
S6.pred <- prediction(Score.svm, spam.test.set$type)

roc1 <- performance(S1.pred, measure = "tpr", x.measure = "fpr")
roc2 <- performance(S2.pred, measure = "tpr", x.measure = "fpr")
roc3 <- performance(S3.pred, measure = "tpr", x.measure = "fpr")
roc4 <- performance(S4.pred, measure = "tpr", x.measure = "fpr")
roc5 <- performance(S5.pred, measure = "tpr", x.measure = "fpr")
roc6 <- performance(S6.pred, measure = "tpr", x.measure = "fpr")

par(mfrow = c(1,1))

#Tracer les courbes ROC des scores
plot(roc1, col = "black", lwd = 2, main = "Courbes ROC")
plot(roc2, add = TRUE, col = "red", lwd = 2)
plot(roc3, add = TRUE, col = "blue", lwd = 2)
plot(roc4, add = TRUE, col = "green", lwd = 2)
plot(roc5, add = TRUE, col = "yellow", lwd = 2)
plot(roc6, add = TRUE, col = "orange", lwd = 2)
bissect <- function(x) x
curve(bissect(x),  col = "black", lty = 2, lwd = 2, add = TRUE)
legend("bottomright", legend = c("logit", "lda", "qda", "RF", "arbre", "svm"),
         col = c("black", "red", "blue", "green", "yellow", "orange"), lty = 1, lwd = 2)

#Calcul de l'AUC  
AUC1 <- performance(S1.pred, "auc")@y.values[[1]]
AUC2 <- performance(S2.pred, "auc")@y.values[[1]]
AUC3 <- performance(S3.pred, "auc")@y.values[[1]]
AUC4 <- performance(S4.pred, "auc")@y.values[[1]]
AUC5 <- performance(S5.pred, "auc")@y.values[[1]]
AUC6 <- performance(S6.pred, "auc")@y.values[[1]]

print(c("La valeur de l'AUC de chacun des scores : ", "",
        paste("logit = ", as.character(AUC1)),
        paste("lda = ", as.character(AUC2)),
        paste("qda = ", as.character(AUC3)),
        paste("RF = ", as.character(AUC4)),
        paste("arbre = ", as.character(AUC5)),
        paste("svm = ", as.character(AUC6))
        )) 

#La courbe Lift de chacun des scores
lift1 <- performance(S1.pred, measure =  "tpr", x.measure =  "rpp")
lift2 <- performance(S2.pred, measure = "tpr", x.measure = "rpp")
lift3 <- performance(S3.pred, measure = "tpr", x.measure = "rpp")
lift4 <- performance(S4.pred, measure = "tpr", x.measure = "rpp")
lift5 <- performance(S5.pred, measure = "tpr", x.measure = "rpp")
lift6 <- performance(S6.pred, measure = "tpr", x.measure = "rpp")

plot(lift1, col = "black", lwd = 2, main = "Courbes Lift")
plot(lift2, add = TRUE, col = "red", lwd = 2)
plot(lift3, add = TRUE, col = "blue", lwd = 2)
plot(lift4, add = TRUE, col = "green", lwd = 2)
plot(lift5, add = TRUE, col = "yellow", lwd = 2)
plot(lift6, add = TRUE, col = "orange", lwd = 2)
bissect <- function(x) x
curve(bissect(x),  col = "black", lty = 2, lwd = 2, add = TRUE)
legend("bottomright", legend = c("logit", "lda", "qda", "RF", "arbre", "svm"),
       col = c("black", "red", "blue", "green", "yellow", "orange"), 
        lty = 1, lwd = 2)

#### Améliorer la précision d'estimation de l'AUC des différents scores ####

#la fonction donnant l'AUC
estimation_AUC <- function(l=3){
  #échantillonnage stratifié
  mod.type <- as.vector(unique(spam.data$type))#les modalités de la variable réponse "type"
  table(spam.data$type)[mod.type]
  size <- as.vector(table(spam.data$type)[mod.type]/l) #on veut 1/3 d'observations pour le test 
  s <- strata(spam.data, stratanames="type", size=size, method="srswor")
  test.set.index <- s$ID_unit
  spam.test.set <- spam.data[test.set.index, ] #ensemble de test
  spam.train.set <- spam.data[- test.set.index, ] #ensemble d'apprentissage
  
  modele.logit <- glm(formula = type ~ ., data = spam.train.set, family = binomial)
  modele.lda <- lda(formula = type ~., data = spam.train.set)
  modele.RF <- randomForest(formula = type ~., data = spam.train.set)
  modele.arbre <- rpart(formula = type ~., data = spam.train.set)  

  Score.logit <- predict(modele.logit, newdata = spam.test.set, type = "response")
  Score.lda <- predict(modele.lda, newdata = spam.test.set, type = "prob")$posterior[, 2]
  Score.RF <- predict(modele.RF, newdata = spam.test.set, type = "prob")[, 2]
  Score.arbre <- predict(modele.arbre, newdata = spam.test.set, type = "prob")[, 2]

  S1.pred <- prediction(Score.logit, spam.test.set$type)
  S2.pred <- prediction(Score.lda, spam.test.set$type)
  S3.pred <- prediction(Score.RF, spam.test.set$type)
  S4.pred <- prediction(Score.arbre, spam.test.set$type)
  
  AUC1 <- performance(S1.pred, "auc")@y.values[[1]]
  AUC2 <- performance(S2.pred, "auc")@y.values[[1]]
  AUC3 <- performance(S3.pred, "auc")@y.values[[1]]
  AUC4 <- performance(S4.pred, "auc")@y.values[[1]]
  
  return(c(AUC1,AUC2,AUC3,AUC4))
}

estimation_AUC(3)

M <- 10
resultats <- replicate(M, estimation_AUC(3))
AUCs <-rowMeans(resultats)
names(AUCs) <- c("AUC_score.logit","AUC_score.lda","AUC_score.RF","AUC_score.arbre")
AUCs

#### la meilleur fonction score est celle obtenue par RF ####
modele.RF <- randomForest(formula = type ~., data = spam.train.set)
Score.RF <- predict(modele.RF, newdata = spam.test.set, type = "prob")[, 2]

sort(Score.RF, decreasing=TRUE)
sort(Score.RF, decreasing=TRUE)[1:150]
