import random
import matplotlib.pyplot as plt
from collections import Counter
from Exercice_1 import rattach_point_cluster, calculer_L2_multi,calculer_score_config_multi, generer_toutes_configurations

def affecter_tous_les_points(liste_points, centres, type_dist="L2"):
    affectations = []
    for p in liste_points:
        affectations.append(rattach_point_cluster(p, centres, type_dist))
    return affectations

def initialiser_centres_aleatoires(liste_points, k):
    return random.sample(liste_points, k)

def calculer_nouveaux_centres(liste_points, affectations, k, centres_precedents):
    dim = len(liste_points[0])
    nouveaux_centres = []
    
    for i in range(k):
        # Récupérer les points du cluster i
        points_cluster = []
        for j in range(len(liste_points)):
            if affectations[j] == i:
                points_cluster.append(liste_points[j])
        
        if not points_cluster:
            nouveaux_centres.append(centres_precedents[i])
        else:
            centre_moyen = []
            for d in range(dim):
                somme_dim = 0
                for p in points_cluster:
                    somme_dim += p[d]
                centre_moyen.append(somme_dim / len(points_cluster))
            nouveaux_centres.append(centre_moyen)
            
    return nouveaux_centres

def verifier_convergence(anciens_centres, nouveaux_centres, epsilon=1e-5):
    for i in range(len(anciens_centres)):
        if calculer_L2_multi(anciens_centres[i], nouveaux_centres[i]) > epsilon:
            return False
    return True

def executer_kmeans(liste_points, centres_initiaux, type_dist="L2", max_iter=100, epsilon=1e-5):
    # Création explicite d'une copie des centres pour ne pas modifier l'original
    centres = []
    for c in centres_initiaux:
        centres.append(list(c))
        
    for iteration in range(max_iter):
        affectations = affecter_tous_les_points(liste_points, centres, type_dist)
        nouveaux_centres = calculer_nouveaux_centres(liste_points, affectations, len(centres), centres)
        
        if verifier_convergence(centres, nouveaux_centres, epsilon):
            centres = nouveaux_centres
            break
        centres = nouveaux_centres
        
    cout_final = calculer_score_config_multi(liste_points, centres, type_dist)
    return centres, affectations, cout_final, iteration + 1

def analyser_initialisations_kmeans(liste_points, k, type_dist="L2"):
    combos = generer_toutes_configurations(liste_points, k)
    couts_finaux = []
    
    for init_centres in combos:
        centres_finaux, affectations, cout, iterations = executer_kmeans(liste_points, init_centres, type_dist)
        couts_finaux.append(round(cout, 2))
        
    compte_couts = Counter(couts_finaux)
    valeurs_couts = sorted(list(compte_couts.keys()))
    
    frequences = []
    for v in valeurs_couts:
        frequences.append(compte_couts[v])
    
    plt.figure(figsize=(8, 5))
    valeurs_str = []
    for v in valeurs_couts:
        valeurs_str.append(str(v))
        
    barres = plt.bar(valeurs_str, frequences, color='red', edgecolor='black')
    plt.title(f"Influence de l'initialisation K-means ({len(combos)} tests)")
    plt.xlabel("Coût final")
    plt.ylabel("Nombre d'initialisations")
    
    for barre in barres:
        yval = barre.get_height()
        plt.text(barre.get_x() + barre.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=9)

    plt.grid(axis='y', alpha=0.3)
    plt.show()

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
    print("\n[K-MEANS] Analyse des initialisations sur le jeu de données 1D...")
    analyser_initialisations_kmeans(dataset, k, distance_testee)

    ##############
    #   D2
    #############
    dataset = points_2d
    print("\n[K-MEANS] Analyse des initialisations sur le jeu de données 2D...")
    analyser_initialisations_kmeans(dataset, k, distance_testee)

    ##############
    #   D3
    #############
    dataset = points_3d
    print("\n[K-MEANS] Analyse des initialisations sur le jeu de données 3D...")
    analyser_initialisations_kmeans(dataset, k, distance_testee)