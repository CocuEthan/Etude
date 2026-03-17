import random
import matplotlib.pyplot as plt
from Exercice_1 import calculer_L1_multi, calculer_L2_multi

# ==========================================
# 1. TIRAGE ALÉATOIRE PONDÉRÉ
# ==========================================
def tirage_aleatoire_pondere(liste_points, poids):
    """
    Fonction générique qui effectue un tirage aléatoire à partir d'une distribution de probabilités.
    Plus le poids d'un point est grand, plus il a de chances d'être tiré.
    """
    somme_poids = 0
    for p in poids:
        somme_poids += p
        
    # On tire un nombre aléatoire entre 0 et la somme totale des poids
    valeur_cible = random.uniform(0, somme_poids)
    
    cumul = 0
    for i in range(len(liste_points)):
        cumul += poids[i]
        # Dès que le cumul dépasse la valeur cible, on choisit ce point
        if valeur_cible <= cumul:
            return liste_points[i]
            
    # Sécurité (ne devrait jamais arriver avec des maths parfaites)
    return liste_points[-1]

# ==========================================
# 2. INITIALISATION K-MEANS++
# ==========================================
def choisir_premier_centre(liste_points):
    """
    Choisit aléatoirement un premier centre parmi l'ensemble des points.
    """
    index_aleatoire = random.randint(0, len(liste_points) - 1)
    return liste_points[index_aleatoire]

def choisir_deuxieme_centre(liste_points, premier_centre, type_dist="L2"):
    """
    Choisit le deuxième centre avec une probabilité proportionnelle 
    au carré de sa distance au premier centre.
    """
    poids = []
    for p in liste_points:
        if type_dist == "L1":
            distance = calculer_L1_multi(p, premier_centre)
        else:
            distance = calculer_L2_multi(p, premier_centre)
            
        # Probabilité proportionnelle au carré de la distance
        poids.append(distance ** 2)
        
    nouveau_centre = tirage_aleatoire_pondere(liste_points, poids)
    return nouveau_centre

def choisir_centres_suivants(liste_points, centres_deja_choisis, k, type_dist="L2"):
    """
    Sélectionne les centres du troisième au k-ième, avec une probabilité 
    proportionnelle au carré de la distance au centre le plus proche déjà choisi.
    """
    centres = []
    for c in centres_deja_choisis:
        centres.append(c)
        
    while len(centres) < k:
        poids = []
        for p in liste_points:
            # 1. Trouver la distance au centre le PLUS PROCHE
            distance_min = float('inf')
            for c in centres:
                if type_dist == "L1":
                    distance = calculer_L1_multi(p, c)
                else:
                    distance = calculer_L2_multi(p, c)
                    
                if distance < distance_min:
                    distance_min = distance
                    
            # 2. Le poids est le carré de cette distance minimale
            poids.append(distance_min ** 2)
            
        # 3. Tirer le nouveau centre
        nouveau_centre = tirage_aleatoire_pondere(liste_points, poids)
        centres.append(nouveau_centre)
        
    return centres

# Fonction "chapeau" pour appeler toute la procédure facilement
def initialiser_kmeans_plus_plus(liste_points, k, type_dist="L2"):
    """Exécute toute la séquence d'initialisation K-means++"""
    if k == 1:
        return [choisir_premier_centre(liste_points)]
        
    c1 = choisir_premier_centre(liste_points)
    c2 = choisir_deuxieme_centre(liste_points, c1, type_dist)
    
    if k == 2:
        return [c1, c2]
        
    tous_les_centres = choisir_centres_suivants(liste_points, [c1, c2], k, type_dist)
    return tous_les_centres

# ==========================================
# 3. FONCTION DE TEST VISUEL
# ==========================================
def afficher_test_initialisation(liste_points, centres, titre):
    dim = len(liste_points[0])
    fig = plt.figure(figsize=(8, 6))
    
    if dim == 3:
        ax = fig.add_subplot(111, projection='3d')
    else:
        ax = fig.add_subplot(111)
        
    # Séparer les points normaux des centres pour l'affichage
    liste_centres_listes = []
    for c in centres:
        liste_centres_listes.append(list(c))
        
    for p in liste_points:
        est_centre = list(p) in liste_centres_listes
        
        if est_centre:
            couleur = 'red'
            marqueur = 'X'
            taille = 150
            z_ordre = 3
        else:
            couleur = 'blue'
            marqueur = 'o'
            taille = 30
            z_ordre = 2
            
        if dim == 1:
            ax.scatter(p[0], 0, c=couleur, marker=marqueur, s=taille, zorder=z_ordre)
            ax.set_yticks([])
        elif dim == 2:
            ax.scatter(p[0], p[1], c=couleur, marker=marqueur, s=taille, zorder=z_ordre)
        elif dim == 3:
            ax.scatter(p[0], p[1], p[2], c=couleur, marker=marqueur, s=taille, zorder=z_ordre)
            
    plt.title(titre)
    plt.show()


###############################
# Main - Test K-Means++
###############################
if __name__ == "__main__":
    
    points_1d = [[1], [3], [7], [9], [15], [17], [19], [21]]
    points_2d = [[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]
    points_3d = [[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]]
    
    k = 3
    distance_testee = "L2"
    
    ##############
    #   D1
    #############
    print("\n[K-MEANS++] Test de l'initialisation sur le jeu de données 1D...")
    centres_1d = initialiser_kmeans_plus_plus(points_1d, k, distance_testee)
    afficher_test_initialisation(points_1d, centres_1d, "K-Means++ : Centres initiaux en 1D")

    ##############
    #   D2
    #############
    print("\n[K-MEANS++] Test de l'initialisation sur le jeu de données 2D...")
    centres_2d = initialiser_kmeans_plus_plus(points_2d, k, distance_testee)
    afficher_test_initialisation(points_2d, centres_2d, "K-Means++ : Centres initiaux en 2D")

    ##############
    #   D3
    #############
    print("\n[K-MEANS++] Test de l'initialisation sur le jeu de données 3D...")
    centres_3d = initialiser_kmeans_plus_plus(points_3d, k, distance_testee)
    afficher_test_initialisation(points_3d, centres_3d, "K-Means++ : Centres initiaux en 3D")