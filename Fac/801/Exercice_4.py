import random
import matplotlib.pyplot as plt

from Exercice_1 import (
    rattach_point_cluster, 
    calculer_L1_multi, 
    calculer_score_config_multi
)

##################################
# 1. Calcul
##################################
def calculer_mediane_liste(valeurs):
    """
    Calcule la médiane d'une liste de nombres de manière explicite.
    """
    valeurs_triees = sorted(valeurs)
    n = len(valeurs_triees)
    
    if n % 2 == 1:
        return valeurs_triees[n // 2]
    else:
        milieu1 = valeurs_triees[(n // 2) - 1]
        milieu2 = valeurs_triees[n // 2]
        return (milieu1 + milieu2) / 2.0

def calculer_nouveaux_centres_medians(liste_points, affectations, k, centres_precedents):
    """
    Calcule le nouveau centre d'un cluster comme la médiane des points affectés,
    coordonnée par coordonnée.
    """
    dim = len(liste_points[0])
    nouveaux_centres = []
    
    for i in range(k):
        points_cluster = []
        for j in range(len(liste_points)):
            if affectations[j] == i:
                points_cluster.append(liste_points[j])
        
        if len(points_cluster) == 0:
            nouveaux_centres.append(centres_precedents[i])
        else:
            centre_median = []
            for d in range(dim):
                valeurs_dim = []
                for p in points_cluster:
                    valeurs_dim.append(p[d])
                    
                mediane_dim = calculer_mediane_liste(valeurs_dim)
                centre_median.append(mediane_dim)
                
            nouveaux_centres.append(centre_median)
            
    return nouveaux_centres

##################################
# 2. BOUCLE K-MEDIANS
##################################
def affecter_tous_les_points_L1(liste_points, centres):
    """Force l'utilisation de la distance L1 pour l'affectation."""
    affectations = []
    for p in liste_points:
        affectations.append(rattach_point_cluster(p, centres, "L1"))
    return affectations

def verifier_convergence_L1(anciens_centres, nouveaux_centres, epsilon=1e-5):
    """Vérifie la convergence en utilisant la distance L1."""
    for i in range(len(anciens_centres)):
        if calculer_L1_multi(anciens_centres[i], nouveaux_centres[i]) > epsilon:
            return False
    return True

def executer_kmedians(liste_points, centres_initiaux, max_iter=100, epsilon=1e-5):
    """
    Exécute l'algorithme K-medians jusqu'à convergence.
    Toutes les étapes utilisent la distance L1 et la médiane.
    """
    centres = []
    for c in centres_initiaux:
        centres.append(list(c))
        
    for iteration in range(max_iter):
        affectations = affecter_tous_les_points_L1(liste_points, centres)
        nouveaux_centres = calculer_nouveaux_centres_medians(liste_points, affectations, len(centres), centres)
        
        if verifier_convergence_L1(centres, nouveaux_centres, epsilon):
            centres = nouveaux_centres
            break
            
        centres = nouveaux_centres
        
    cout_final = calculer_score_config_multi(liste_points, centres, "L1")
    return centres, affectations, cout_final, iteration + 1

##################################
# 3. Affichage
##################################
def afficher_resultat_kmedians(liste_points, centres, affectations, titre):
    dim = len(liste_points[0])
    fig = plt.figure(figsize=(8, 6))
    
    if dim == 3:
        ax = fig.add_subplot(111, projection='3d')
    else:
        ax = fig.add_subplot(111)
        
    for i in range(len(liste_points)):
        p = liste_points[i]
        couleur = affectations[i]
        
        if dim == 1:
            ax.scatter(p[0], 0, c=couleur, marker='o', s=30, cmap='tab10', zorder=2)
            ax.set_yticks([])
        elif dim == 2:
            ax.scatter(p[0], p[1], c=couleur, marker='o', s=30, cmap='tab10', zorder=2)
        elif dim == 3:
            ax.scatter(p[0], p[1], p[2], c=couleur, marker='o', s=30, cmap='tab10', zorder=2)
            
    # Affichage des centres finaux
    for c in centres:
        if dim == 1:
            ax.scatter(c[0], 0, c='red', marker='X', s=150, edgecolors='black', zorder=3)
        elif dim == 2:
            ax.scatter(c[0], c[1], c='red', marker='X', s=150, edgecolors='black', zorder=3)
        elif dim == 3:
            ax.scatter(c[0], c[1], c[2], c='red', marker='X', s=150, edgecolors='black', zorder=3)
            
    plt.title(titre)
    plt.show()

###############################
# Main 
###############################
if __name__ == "__main__":
    
    points_1d = [[1], [3], [7], [9], [15], [17], [19], [21]]
    points_2d = [[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]
    points_3d = [[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]]
    
    k = 3
    
    ##############
    #   D1
    #############
    print("\n[K-MEDIANS] Exécution sur le jeu de données 1D...")
    # Initialisation basique (aléatoire simple pour le test)
    init_1d = random.sample(points_1d, k)
    centres_1d, aff_1d, cout_1d, iter_1d = executer_kmedians(points_1d, init_1d)
    print(f"Convergence en {iter_1d} itérations. Coût L1 final : {cout_1d}")
    afficher_resultat_kmedians(points_1d, centres_1d, aff_1d, f"K-Medians 1D (Coût L1 : {cout_1d})")

    ##############
    #   D2
    #############
    print("\n[K-MEDIANS] Exécution sur le jeu de données 2D...")
    init_2d = random.sample(points_2d, k)
    centres_2d, aff_2d, cout_2d, iter_2d = executer_kmedians(points_2d, init_2d)
    print(f"Convergence en {iter_2d} itérations. Coût L1 final : {cout_2d}")
    afficher_resultat_kmedians(points_2d, centres_2d, aff_2d, f"K-Medians 2D (Coût L1 : {cout_2d})")

    ##############
    #   D3
    #############
    print("\n[K-MEDIANS] Exécution sur le jeu de données 3D...")
    init_3d = random.sample(points_3d, k)
    centres_3d, aff_3d, cout_3d, iter_3d = executer_kmedians(points_3d, init_3d)
    print(f"Convergence en {iter_3d} itérations. Coût L1 final : {cout_3d}")
    afficher_resultat_kmedians(points_3d, centres_3d, aff_3d, f"K-Medians 3D (Coût L1 : {cout_3d})")