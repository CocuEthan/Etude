# Importer les librairies nécessaires numpy et matplotlib 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np            
# Fixer la reproductibilité 
np.random.seed(42)   
# Générer les points du premier groupe centrés autour de (0,0) (50 points) 
G0 = np.random.randn(50, 2) + np.array([0,0]) 
# Générer les points du deuxième groupe centrés autour de (2,2) (50 points)  
G1 =  np.random.randn(50, 2) + np.array([2,2]) 
# Combiner les points des deux groupes dans un seul tableau « dataset » 
X = X = np.concatenate((G0, G1), axis=0)                     
# Visualiser les groupes dans un plan 2D 
# Chaque groupe doit avoir un symbole et une couleur différents 
plt.scatter(X[:50,0], X[:50,1], color = "blue", marker = "o",  label = 'Groupe 0')    
plt.scatter(X[50:,0], X[50:,1], color = "red", marker = "x",  label = 'Groupe 1')  
plt.xlabel("x1") 
plt.ylabel("x2") 
plt.title("Dataset 2D linéairement séparable") 
plt.legend() 
#plt.show() 

# 2 qui se sépare légérement: linéairement séparable
# Générer les points du deuxième groupe centrés autour de (4,4) (50 points)  
G3 =  np.random.randn(50, 2) + np.array([4,4]) 
# Combiner les points des deux groupes dans un seul tableau « dataset » 
X = X = np.concatenate((G0, G3), axis=0)                     
# Visualiser les groupes dans un plan 2D 
# Chaque groupe doit avoir un symbole et une couleur différents 
plt.scatter(X[:50,0], X[:50,1], color = "blue", marker = "o",  label = 'Groupe 0')    
plt.scatter(X[50:,0], X[50:,1], color = "red", marker = "x",  label = 'Groupe 1')  
plt.xlabel("x1") 
plt.ylabel("x2") 
plt.title("Dataset 2D linéairement séparable") 
plt.legend() 
#plt.show() 

#2 qui se rapproche
# Générer les points du deuxième groupe centrés autour de (1,1) (50 points)  
G4 =  np.random.randn(50, 2) + np.array([1,1]) 
# Combiner les points des deux groupes dans un seul tableau « dataset » 
X = X = np.concatenate((G0, G4), axis=0)                     
# Visualiser les groupes dans un plan 2D 
# Chaque groupe doit avoir un symbole et une couleur différents 
plt.scatter(X[:50,0], X[:50,1], color = "blue", marker = "o",  label = 'Groupe 0')    
plt.scatter(X[50:,0], X[50:,1], color = "red", marker = "x",  label = 'Groupe 1')  
plt.xlabel("x1") 
plt.ylabel("x2") 
plt.title("Dataset 2D linéairement séparable") 
plt.legend() 
#plt.show() 

#2 quasiment fusionner
G0 = np.random.randn(50, 2) + np.array([0,0]) 
# Générer les points du deuxième groupe centrés autour de (2,2) (50 points)  
G5 =  np.random.randn(50, 2) + np.array([0,0]) 
# Combiner les points des deux groupes dans un seul tableau « dataset » 
X = X = np.concatenate((G0, G5), axis=0)                     
# Visualiser les groupes dans un plan 2D 
# Chaque groupe doit avoir un symbole et une couleur différents 
plt.scatter(X[:50,0], X[:50,1], color = "blue", marker = "o",  label = 'Groupe 0')    
plt.scatter(X[50:,0], X[50:,1], color = "red", marker = "x",  label = 'Groupe 1')  
plt.xlabel("x1") 
plt.ylabel("x2") 
plt.title("Dataset 2D linéairement séparable") 
plt.legend() 
#plt.show() 


G0 = np.random.randn(50, 2) + np.array([0,0]) 
G1 = np.random.randn(50, 2) + np.array([2,2]) 
X = np.concatenate((G0, G1), axis=0)
# Affichage des point de test (les points de la grille) 
def create_test_grid(X_train, resolution=0.2): 
    """ 
    Crée une grille de points couvrant l'espace du dataset d'entraînement. 
    X_train : données d'apprentissage (n_samples, 2) 
    resolution : distance entre deux points de la grille 
    Retourne : 
    xx, yy : matrices meshgrid 
    grid_points : tableau (n_points, 2) 
        """ 
    # Définir les bornes 
    x_min, x_max = X_train[:, 0].min() - 1, X_train[:, 0].max() + 1 
    y_min, y_max = X_train[:, 1].min() - 1, X_train[:, 1].max() + 1 
    # Créer la grille 
    xx, yy = np.meshgrid( 
    np.arange(x_min, x_max, resolution), 
    np.arange(y_min, y_max, resolution) 
        ) 
    # Transformer en liste de points 
    grid_points = np.c_[xx.ravel(), yy.ravel()] 
    return xx, yy, grid_points

def plot_test_grid(grid_points): 
    """ 
    Affiche uniquement les points de test (grille). 
    """ 
    plt.figure() 
    plt.scatter(grid_points[:, 0], grid_points[:, 1], s=10) 
    plt.xlabel("x1") 
    plt.ylabel("x2") 
    plt.title("Points de test (grille)") 
    plt.gca().set_aspect('equal', adjustable='box') 
    plt.show() 


def count_grid_points(grid_points):
    """
    Affiche et retourne le nombre total de points dans la grille.
    """
    # grid_points est une matrice de forme (Nombre_de_points, 2)
    # shape[0] donne le nombre de lignes (donc le nombre de points)
    n_points = grid_points.shape[0]
    
    print(f"Nombre total de points de test : {n_points}")
    return n_points


X_train_dummy = np.array([[1, 2], [5, 6], [3, 8]])

# 2. Liste des résolutions à tester (du plus grossier au plus fin)
resolutions_to_test = [1.0, 0.5, 0.2, 0.1]

print("--- Comparaison de l'impact de la résolution ---")

for res in resolutions_to_test:
    print(f"\nTest avec résolution = {res}")
    
    # Création de la grille
    _, _, points = create_test_grid(X_train_dummy, resolution=res)
    
    # Comptage
    count_grid_points(points)

#3 resolution une tres dense, une moyennement dens, une peu dense

# ==============================================================================
# PARTIE A AJOUTER A LA FIN DE TON FICHIER
# Visualisation 3x3 : 3 Types de données vs 3 Résolutions de grille
# ==============================================================================

# 1. Préparation des 3 Datasets (Lignes du tableau)
# On recrée les cas que tu as définis plus haut pour les avoir dans une liste
np.random.seed(42) # Pour garder les mêmes points
G0 = np.random.randn(50, 2) + np.array([0,0])

# Cas 1 : Bien séparé (G3 était à 4,4)
X_separe = np.concatenate((G0, np.random.randn(50, 2) + np.array([4,4])), axis=0)

# Cas 2 : Rapproché (G1 était à 2,2)
X_rapproche = np.concatenate((G0, np.random.randn(50, 2) + np.array([2,2])), axis=0)

# Cas 3 : Fusionné / Chevauchement (G5 était à 0,0)
X_fusion = np.concatenate((G0, np.random.randn(50, 2) + np.array([0,0])), axis=0)

liste_datasets = [
    ("Bien Séparé", X_separe),
    ("Rapproché", X_rapproche),
    ("Chevauchement", X_fusion)
]

# 2. Préparation des 3 Résolutions (Colonnes du tableau)
# On choisit : Peu dense (1.0), Moyenne (0.5), Très dense (0.2)
liste_resolutions = [1.0, 0.5, 0.2]
noms_resolutions = ["Peu dense (Res=1.0)", "Moyenne (Res=0.5)", "Très dense (Res=0.2)"]

# 3. Création de la figure (Matrice 3x3)
fig, axes = plt.subplots(3, 3, figsize=(15, 12))

# Boucle sur les Lignes (Datasets)
for i, (nom_ds, X_actuel) in enumerate(liste_datasets):
    
    # Boucle sur les Colonnes (Résolutions)
    for j, res in enumerate(liste_resolutions):
        ax = axes[i, j] # On sélectionne le bon carré
        
        # --- Etape A : Créer la grille avec TA fonction ---
        # Note : on récupère juste 'grid' (le 3ème retour), on ignore xx et yy pour l'instant
        _, _, grid = create_test_grid(X_actuel, resolution=res)
        
        # --- Etape B : Afficher la grille (Points gris en fond) ---
        # On met s=1 (taille) pour ne pas surcharger le dessin quand c'est très dense
        ax.scatter(grid[:, 0], grid[:, 1], s=5, color='lightgray', label='Grille')
        
        # --- Etape C : Afficher les vraies données par dessus ---
        # Les 50 premiers points sont le Groupe 0 (Bleu)
        ax.scatter(X_actuel[:50, 0], X_actuel[:50, 1], color="blue", marker="o")
        # Les 50 suivants sont le Groupe 1 (Rouge)
        ax.scatter(X_actuel[50:, 0], X_actuel[50:, 1], color="red", marker="x")
        
        # Mise en page (Titres et Labels)
        if i == 0: # Titre seulement sur la première ligne
            ax.set_title(noms_resolutions[j], fontweight='bold')
        if j == 0: # Nom du dataset seulement sur la première colonne
            ax.set_ylabel(nom_ds, fontweight='bold', fontsize=12)
            
        # On enlève les chiffres des axes pour faire plus propre
        ax.set_xticks([])
        ax.set_yticks([])

plt.suptitle("Impact de la densité de la grille de test", fontsize=16)
plt.tight_layout()
plt.show()
######################################
#       6
######################################

# Fonction pour initialiser les poids et le biais 
def initialize_weights(n_inputs) : 
    #Créer un vecteur de poids w de taille n_inputs avec de petites valeurs aléatoires 
    w = np.random.randn(n_inputs) * 0.2
    # Créer un biais b avec une petite valeur aléatoire 
    b = np.random.randn() * 0.2
    return w, b

w_init, b_init = initialize_weights(n_inputs=2)

#print(f"Poids w initialisés : {w_init}")
#print(f"Biais b initialisé : {b_init}")

# Fonction pour calculer la sortie linéaire du neurone 
def forward(x, w, b): 
    # Calculer z = w·x + b ;  la variable b correspond au biais w0 ; w et x sont des   
    # vecteurs de même dimension, b est un scalaire ; z = produit scalaire de w et x + b 
    z = np.dot(x, w) + b
    return z

# Fonction d'activation générique 
def activation(z, activation_function) : 
    # Appliquer la fonction d'activation fournie en paramètre  
    return activation_function(z)


def carre(x):
    return x * x

z_test = 5
# On passe 'z_test' et la fonction 'carre' à notre fonction générique
#resultat = activation(z_test, carre)
#print(f"Si z={z_test} et la fonction est 'carré', le résultat est : {resultat}")


##############################################
###     4
##############################################

def update_weights(w, b, delta_w, delta_b, learning_rate): 
    """ 
    Met à jour les poids et le biais selon la règle de la descente de gradient.
    w, b : poids et biais actuels 
    delta_w, delta_b : corrections calculées (gradient) pour le modèle spécifique 
    learning_rate : taux d'apprentissage (eta)
     
    Retourne les poids et biais mis à jour 
    """
    # Mise à jour des poids : w = w - learning_rate * delta_w
    w = w - learning_rate * delta_w
    # Mise à jour du biais : b = b - learning_rate * delta_b
    b = b - learning_rate * delta_b
    
    return w, b

def predict(X, w, b, activation_function): 
    """ 
    Prédit la classe pour un ensemble de points.
    X : tableau de points (exemples) 
    w, b : poids et biais du neurone 
    activation_function : fonction d'activation spécifique à chaque modèle 
    """ 
    y_hats = [] 
    
    for x in X: 
        # 1. Calculer z avec la propagation (forward)
        z = forward(x, w, b)
        
        # 2. Appliquer la fonction d'activation
        y_hat = activation(z, activation_function)
        
        y_hats.append(y_hat) 
    
    return np.array(y_hats)


def compute_error(y_true, y_hat, model_type): 
    """ 
    Calcule l'erreur selon le type de modèle.
    y_true : labels réels (ce qu'on attend)
    y_hat : prédictions du neurone (ce qu'on a obtenu)
    model_type : 'perceptron', 'adaline', 'logistic' 
 
    Retourne une valeur unique représentant l'erreur 
    """ 
    
    if model_type == 'perceptron': 
        # Perceptron : On compte simplement le nombre d'erreurs
        # (y_true != y_hat) crée une liste de Vrai/Faux. sum() compte les Vrai.
        error = np.sum(y_true != y_hat)
        
    elif model_type == 'adaline': 
        # ADALINE : Erreur Quadratique Moyenne (MSE)
        # On fait la moyenne des écarts au carré
        error = np.mean((y_true - y_hat)**2)
        
    elif model_type == 'logistic': 
        # Logistique : Cross-entropy (Entropie croisée)
        epsilon = 1e-15
        y_hat = np.clip(y_hat, epsilon, 1 - epsilon)
        
        # Formule de la Cross-Entropy
        error = -np.mean(y_true * np.log(y_hat) + (1 - y_true) * np.log(1 - y_hat))
        
    return error


###########################################
###
###             V.Perceptron
#######
############################################


def perceptron_activation(z): 
    """
    Retourne +1 si z >= 0, sinon -1.
    Utilise np.where pour gérer aussi bien les nombres seuls que les tableaux numpy.
    """
    return np.where(z >= 0, 1, -1)


# 2. Calcul de delta_w et delta_b pour le perceptron 
def perceptron_delta(X, y_true, y_hat): 
    """ 
    Calcule le gradient (la correction) uniquement sur les erreurs.
    X : vecteurs d'entrée 
    y_true : labels réels (+1/-1) 
    y_hat : prédictions actuelles 
    """ 
    n_samples = X.shape[0] 
    delta_w_total = np.zeros(X.shape[1]) 
    delta_b_total = 0 
    count_misclassified = 0 
 
    for i in range(n_samples): 
        if y_hat[i] != y_true[i]: 
            delta_w_total += -y_true[i] * X[i] 
            
            delta_b_total += -y_true[i] 
            
            count_misclassified += 1 
 
    if count_misclassified > 0: 
         delta_w = delta_w_total / count_misclassified
         delta_b = delta_b_total / count_misclassified
    else: 
         delta_w = np.zeros_like(delta_w_total) 
         delta_b = 0     
         
    return delta_w, delta_b


# Création des labels (-1 pour G0, +1 pour G1) 
y_true = np.array([-1]*len(G0) + [1]*len(G1)) 
# Initialisation 
w, b = initialize_weights(n_inputs=2) 
learning_rate = 0.01 
n_epochs = 50 

# Boucle d'apprentissage 
for epoch in range(n_epochs): 
    # prédiction sur tout le dataset 
    y_hat = predict(X, w, b, perceptron_activation) 
     
    # calcul des deltas moyens 
    delta_w, delta_b = perceptron_delta(X, y_true, y_hat) 
     
    # mise à jour des poids et du biais 
    w, b = update_weights(w, b, delta_w, delta_b, learning_rate) 
     
    # optionnel : calcul du coût pour suivi 
    loss = compute_error(y_true, y_hat, model_type='perceptron') 
    print(f"Epoch {epoch+1} - coût : {loss}") 

# Générer la grille 
xx, yy, grid_points = create_test_grid(X, resolution=0.5) 
 
# Prédire la classe de chaque point 
grid_predictions = predict(grid_points, w, b, perceptron_activation)
 
# Séparer selon la classe 
grid_class_neg = grid_points[grid_predictions == -1] 
grid_class_pos = grid_points[grid_predictions == 1] 
 
# Affichage 
plt.figure(figsize=(8,6)) 
 
# Affichage, en bleu clair, des points de test dont la classe prédite est -1  
plt.scatter(grid_class_neg[:, 0], grid_class_neg[:, 1], color='lightblue', s=15, label='Grille (Prédit -1)') 
 
# Affichage, en rose, des points de test dont la classe prédite est +1 
plt.scatter(grid_class_pos[:, 0], grid_class_pos[:, 1], color='pink', s=15, label='Grille (Prédit +1)') 
 
# Affichage, en bleu, des données d’apprentissage labélisées en -1 
plt.scatter(X[y_true == -1, 0], X[y_true == -1, 1], color='blue', marker='o', edgecolors='k', s=50, label='Train -1') 
 
# Affichage, en rouge, des données d’apprentissage labélisées en +1 
plt.scatter(X[y_true == 1, 0], X[y_true == 1, 1], color='red', marker='x', s=50, label='Train +1') 

plt.xlabel("x1") 
plt.ylabel("x2") 
plt.title("Prédiction des points de test") 
plt.legend() 
plt.show()

def plot_decision_boundary(X, y_true, w, b, activation_function, model_type, resolution=0.02): 
      """ 
      Trace la frontière de décision d'un neurone simple sur un dataset 2D. 
    
      X : tableau de points d’entraînement (n_samples, 2) 
      y_true : labels réels (0/1 ou -1/+1 selon le modèle) 
      w, b : poids et biais du neurone 
      activation_function : fonction d'activation spécifique au modèle 
      resolution : pas de la grille pour la visualisation 
 
      Cette fonction réutilise les fonctions create_test_grid et predict pour générer    
      la grille et prédire sur tous les points. 
 
      """ 
      # Créer la grille de points sur tout l'espace 
      xx, yy, grid_points = create_test_grid(X, resolution)
     
      # Prédire la sortie pour chaque point de la grille 
      Z = predict(grid_points, w, b, activation_function)
       
      # Pour classification binaire, convertir en 0/1 si nécessaire 
      if model_type == 'logistic': 
                 Z = np.where(Z >= 0.5, 1, 0) 
      else: 
                 Z = np.where(Z >= 0, 1, -1) 
 
      # Reshaper les prédictions pour correspondre à la grille 
      Z = Z.reshape(xx.shape)    
      
      # Tracer la frontière de décision 
      plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.coolwarm)    
      
      # Tracer les points réels 
      plt.scatter(X[:, 0], X[:, 1], c=y_true, cmap=plt.cm.coolwarm, edgecolors='k', s=50) 
 
      plt.xlabel('x1') 
      plt.ylabel('x2') 
      plt.title('Frontière de décision du neurone') 
      plt.show()

plot_decision_boundary(X, y_true, w, b, perceptron_activation, model_type='perceptron')


# Une liste pour sauvegarder les poids w (w1 et w2) 
w_history = []  
# Une liste pour sauvegarder les biais b (w0) 
b_history = []  

for epoch in range(n_epochs): 
    y_hat = predict(X, w, b, perceptron_activation) 
    delta_w, delta_b = perceptron_delta(X, y_true, y_hat) 
    w, b = update_weights(w, b, delta_w, delta_b, learning_rate) 
    # Sauvegarde des paramètres pour l’animation 
    w_history.append(w.copy()) 
    b_history.append(b) 
    
    error = compute_error(y_true, y_hat, model_type='perceptron') 
    print(f"Epoch {epoch+1} - coût : {error}")

# Création de la figure 
fig, ax = plt.subplots(figsize=(8,6)) 
ax.set_xlim(X[:,0].min()-1, X[:,0].max()+1) 
ax.set_ylim(X[:,1].min()-1, X[:,1].max()+1) 
# Affichage des points d’apprentissage 
ax.scatter(X[y_true==-1,0], X[y_true==-1,1], color='blue', label='Classe –1',   
                 edgecolor='k', marker = 'o') 
ax.scatter(X[y_true==1,0], X[y_true==1,1], color='red', label='Classe +1',  
                 edgecolor='k', marker = 'D') 
ax.set_xlabel("x1") 
ax.set_ylabel("x2") 
ax.legend() 
#plt.show()  Si vous souhaitez l’afficher avant l’ajout de la droite 

x_vals = np.array([X[:,0].min(),X[:,0].max()])
y_vals = -(w_history[epoch][0]/w_history[epoch][1])* x_vals-(b_history[epoch]/w_history[epoch][1])

 
line, =ax.plot([], [], 'k--', lw=2, label='Frontière apprentissage') 
# Initialise le contenu de cet objet   
def init(): 
    line.set_data([], []) 
    return line, 
# Met à jour le contenu de cet objet à chaque frame   
def update(epoch): 
    x_vals = np.array([X[:,0].min(), X[:,0].max()]) 
    y_vals = - (w_history[epoch][0]/w_history[epoch][1]) * x_vals- (b_history[epoch]/w_history[epoch][1]) 
    line.set_data(x_vals, y_vals) 
    return line, 
# Création de la l’animation image par image (frame par frame) 
ani = animation.FuncAnimation(fig, update, frames=len(w_history),init_func=init, blit=True, interval=500) 
#Affichage de l’animation 
plt.show()

# Affichage dans le notebook 
#from IPython.display import HTML 
#HTML(ani.to_jshtml())

# Sauvegarde dans une image gif 
ani.save('perceptron_evolution.gif', writer='pillow')



##############################################################################
# Adaline

def adaline_activation(z): 
    return z

def adaline_delta(X, y_true, y_hat): 
    """ 
    X : le dataset d’apprentissage 
    Y_true: label réel (0/1 ou -1/+1) 
    y_hat : sortie linéaire du neurone 
    Calcule les deltas moyens sur le batch complet. 
    Retourne delta_w et delta_b 
    """ 
    errors = y_hat - y_true 
    delta_w = np.dot(errors, X) / X.shape[0] 
    delta_b = np.mean(errors) 
    return delta_w, delta_b


# Création des labels
y_true = np.array([-1]*len(G0) + [1]*len(G1)) 

# Initialisation 
w, b = initialize_weights(n_inputs=2) 
learning_rate = 0.01 
n_epochs = 50 
# Boucle d'apprentissage 
for epoch in range(n_epochs): 
    # prédiction sur tout le dataset
    y_hat = predict(X, w, b, adaline_activation) 
     
    # calcul des deltas moyens 
    delta_w, delta_b = adaline_delta(X, y_true, y_hat) 
     
    # mise à jour des poids et du biais
    w, b = update_weights(w, b, delta_w, delta_b, learning_rate) 
     
    # calcul du coût pour suivi
    loss = compute_error(y_true, y_hat, model_type='adaline') 
    
    print(f"Epoch {epoch+1} - coût (MSE) : {loss}")


X_adaline = np.concatenate((G0, G1), axis=0)
y_true_adaline = np.array([-1]*len(G0) + [1]*len(G1))
# initialisation
w_ada, b_ada = initialize_weights(n_inputs=2)

learning_rate_ada = 0.001 
n_epochs_ada = 50

loss_history_ada = []
for epoch in range(n_epochs_ada):
    # calcul de ŷ avec adaline_activation
    y_hat_ada = predict(X_adaline, w_ada, b_ada, adaline_activation)
    
    # calcul des deltas avec adaline_delta
    delta_w_ada, delta_b_ada = adaline_delta(X_adaline, y_true_adaline, y_hat_ada)
    
    # mise à jour des poids avec update_weights
    w_ada, b_ada = update_weights(w_ada, b_ada, delta_w_ada, delta_b_ada, learning_rate_ada)
    
    # calcul du coût avec compute_error
    loss_ada = compute_error(y_true_adaline, y_hat_ada, model_type='adaline')
    
    # Sauvegarde du coût
    loss_history_ada.append(loss_ada)
    
    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f"Epoch {epoch+1} - coût (MSE) : {loss_ada:.4f}")

plt.figure(figsize=(8, 5))
plt.plot(range(1, n_epochs_ada + 1), loss_history_ada, marker='o', color='green', markersize=4)
plt.xlabel('Époques')
plt.ylabel('Coût (MSE)')
plt.title("Évolution du coût pour ADALINE")
plt.grid(True)
plt.show()

print("Affichage de la frontière de décision ADALINE...")
plot_decision_boundary(X_adaline, y_true_adaline, w_ada, b_ada, adaline_activation, model_type='adaline')

##########################################################################################################
# neuronnes logistique

def logistic_activation(z): 
    return 1 / (1 + np.exp(-z))

def logistic_delta(X, y_true, y_hat): 
    """ 
    X : le dataset d’apprentissage 
    y_true : label réel (0/1) 
    y_hat : sortie du neurone (probabilité) 
    Retourne delta_w et delta_b 
    """  
    errors = y_hat - y_true 
    delta_w = np.dot(errors, X) / X.shape[0]
    delta_b = np.mean(errors)
    return delta_w, delta_b


X_log = np.concatenate((G0, G1), axis=0)
y_true_log = np.array([0]*len(G0) + [1]*len(G1))
w_log, b_log = initialize_weights(n_inputs=2)
learning_rate_log = 0.01 
n_epochs_log = 50
loss_history_log = []
for epoch in range(n_epochs_log):
    y_hat_log = predict(X_log, w_log, b_log, logistic_activation)
    delta_w_log, delta_b_log = logistic_delta(X_log, y_true_log, y_hat_log)
    w_log, b_log = update_weights(w_log, b_log, delta_w_log, delta_b_log, learning_rate_log)
    loss_log = compute_error(y_true_log, y_hat_log, model_type='logistic')
    loss_history_log.append(loss_log)
    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f"Epoch {epoch+1} - coût (Cross-Entropy) : {loss_log:.4f}")

plt.figure(figsize=(8, 5))
plt.plot(range(1, n_epochs_log + 1), loss_history_log, marker='o', color='orange', markersize=4)
plt.xlabel('Époques')
plt.ylabel('Coût (Cross-Entropy)')
plt.title("Évolution du coût pour la Régression Logistique")
plt.grid(True)
plt.show()

plot_decision_boundary(X_log, y_true_log, w_log, b_log, logistic_activation, model_type='logistic')