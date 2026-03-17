import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import itertools
import math

###############################
# 1. Distance et coût
###############################

def calculer_L1_multi(p1, p2):
    somme = 0
    for i in range(len(p1)):
        somme += abs(p1[i] - p2[i])
    return somme

def calculer_L2_multi(p1, p2):
    somme_carres = 0
    for i in range(len(p1)):
        somme_carres += (p1[i] - p2[i]) ** 2
    return math.sqrt(somme_carres)

def calculer_score_config_multi(liste_points, centres, type_score="L2"):
    score_total = 0
    for p in liste_points:
        distance_min = float('inf')
        for c in centres:
            d = calculer_L1_multi(p, c) if type_score == "L1" else calculer_L2_multi(p, c)
            if d < distance_min:
                distance_min = d
        score_total += distance_min
    return score_total

###############################
# 2. configuration
###############################

def calculer_P(N, k):
    return math.comb(N, k)

def generer_toutes_configurations(liste_points, k):
    return list(itertools.combinations(liste_points, k))

###############################
# 3. Affectations
###############################

def rattach_point_cluster(point, centres, type_dist="L2"):
    distances = []
    for c in centres:
        if type_dist == "L1":
            distances.append(calculer_L1_multi(point, c))
        else:
            distances.append(calculer_L2_multi(point, c))
    return distances.index(min(distances))

def affecter_non_centres(liste_points, centres, type_dist="L2"):
    affectations = []
    for p in liste_points:
        if list(p) in [list(c) for c in centres]:
            affectations.append(-1) # -1 = centre
        else:
            affectations.append(rattach_point_cluster(p, centres, type_dist))
    return affectations

###############################
# 4. Graphique
###############################

def tracer_cout_configurations_l1_l2(liste_points, k):
    combos = generer_toutes_configurations(liste_points, k)
    
    couts_L1 = [calculer_score_config_multi(liste_points, c, "L1") for c in combos]
    couts_L2 = [calculer_score_config_multi(liste_points, c, "L2") for c in combos]
    
    min_L1, min_L2 = min(couts_L1), min(couts_L2)
    idx_min_L1, idx_min_L2 = couts_L1.index(min_L1), couts_L2.index(min_L2)
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(range(len(couts_L1)), couts_L1, label='Coût L1 (Manhattan)', color='orange', marker='o', markersize=4)
    plt.plot(range(len(couts_L2)), couts_L2, label='Coût L2 (Euclidien)', color='blue', marker='s', markersize=4)
    
    plt.scatter([idx_min_L1], [min_L1], color='red', s=150, zorder=5, 
                label=f'Min Global L1: {min_L1:.2f} (Config n°{idx_min_L1})')
    plt.scatter([idx_min_L2], [min_L2], color='darkred', s=150, zorder=5, marker='X', 
                label=f'Min Global L2: {min_L2:.2f} (Config n°{idx_min_L2})')
    
    plt.title(f"Comparaison des coûts L1 et L2 pour {len(combos)} configurations (k={k})")
    plt.xlabel("Index de la configuration")
    plt.ylabel("Coût total")
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.show()

###############################
# 5. Affichage
###############################

def afficher_grille_configurations(liste_points, liste_centres, titre_global, type_score="L2"):
    """
    Fonction utilitaire qui prend une liste de configurations de centres 
    et les dessine toutes sur la même page (grille).
    """
    dim = len(liste_points[0])
    total = len(liste_centres)
    colonnes = 7 
    lignes = math.ceil(total / colonnes)
    fig = plt.figure(figsize=(3 * colonnes, 3 * lignes))
    fig.suptitle(titre_global, fontsize=16, y=0.98)
    
    for i, centres in enumerate(liste_centres):
        affectations = affecter_non_centres(liste_points, centres, type_score)
        cout = calculer_score_config_multi(liste_points, centres, type_score)
        
        if dim == 3:
            ax = fig.add_subplot(lignes, colonnes, i + 1, projection='3d')
        else:
            ax = fig.add_subplot(lignes, colonnes, i + 1)
            
        for j, p in enumerate(liste_points):
            est_centre = affectations[j] == -1
            couleur = affectations[j] if not est_centre else 'gray'
            marqueur = 'X' if est_centre else 'o'
            taille = 60 if est_centre else 20
            bordure = 'red' if est_centre else 'none'
            
            if dim == 1:
                ax.scatter(p[0], 0, c=couleur, marker=marqueur, s=taille, edgecolors=bordure, cmap='tab10' if isinstance(couleur, int) else None, zorder=3 if est_centre else 2)
                ax.set_yticks([])
            elif dim == 2:
                ax.scatter(p[0], p[1], c=couleur, marker=marqueur, s=taille, edgecolors=bordure, cmap='tab10' if isinstance(couleur, int) else None, zorder=3 if est_centre else 2)
            elif dim == 3:
                ax.scatter(p[0], p[1], p[2], c=couleur, marker=marqueur, s=taille, edgecolors=bordure, cmap='tab10' if isinstance(couleur, int) else None, zorder=3 if est_centre else 2)
        
        ax.set_title(f"n°{i} | Coût: {cout:.1f}", fontsize=10)
        if dim != 3:
            ax.axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def afficher_toutes_configurations_page(liste_points, k, type_score="L2"):
    """Affiche absolument toutes les combinaisons possibles sur la même page."""
    combos = generer_toutes_configurations(liste_points, k)
    afficher_grille_configurations(
        liste_points, 
        combos, 
        titre_global=f"toutes les {len(combos)} configurations (k={k}, Distance {type_score})", 
        type_score=type_score
    )

def afficher_meilleures_configurations_page(liste_points, k, type_score="L2", tolerance=0.01):
    """Trouve le coût minimum et affiche toutes les configurations qui ont ce coût sur la même page."""
    combos = generer_toutes_configurations(liste_points, k)
    
    couts = [calculer_score_config_multi(liste_points, c, type_score) for c in combos]
    cout_min = min(couts)
    
    meilleures_configs = []
    for i, c in enumerate(combos):
        if abs(couts[i] - cout_min) <= tolerance:
            meilleures_configs.append(c)
            
    afficher_grille_configurations(
        liste_points, 
        meilleures_configs, 
        titre_global=f"Meilleures configurations (Coût minimum = {cout_min:.2f} | Distance {type_score})", 
        type_score=type_score
    )

###############################
# Main
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
    dataset = points_1d
    
    print(f"Calcul des combinaisons pour P = {calculer_P(len(dataset), k)}...")

    print("Affichage de toutes les configurations")
    afficher_toutes_configurations_page(dataset, k, distance_testee)

    tracer_cout_configurations_l1_l2(dataset, k)
    print("Affichage des meilleures configurations ")
    afficher_meilleures_configurations_page(dataset, k, distance_testee)


    ##############
    #   D2
    #############
    dataset = points_2d
    
    print(f"Calcul des combinaisons pour P = {calculer_P(len(dataset), k)}...")

    print("Affichage de toutes les configurations")
    afficher_toutes_configurations_page(dataset, k, distance_testee)

    tracer_cout_configurations_l1_l2(dataset, k)
    print("Affichage des meilleures configurations ")
    afficher_meilleures_configurations_page(dataset, k, distance_testee)

    ##############
    #   D3
    #############
    dataset = points_3d
    
    print(f"Calcul des combinaisons pour P = {calculer_P(len(dataset), k)}...")

    print("Affichage de toutes les configurations")
    afficher_toutes_configurations_page(dataset, k, distance_testee)

    tracer_cout_configurations_l1_l2(dataset, k)
    print("Affichage des meilleures configurations ")
    afficher_meilleures_configurations_page(dataset, k, distance_testee)

