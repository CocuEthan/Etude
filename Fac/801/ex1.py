# exercice 1 ecrire un code qui genere 8 point sur un graphique et qui calcul toute les combinaison possible de 3 point. les coordoné des point sont  [1,3,7,9,15,17,19,21] afficher sur un graphique en une dimension, mettre en couleur les fammilles de chaque point
import matplotlib.pyplot as plt
import itertools
import math
from mpl_toolkits.mplot3d import Axes3D


def calculer_combinaisons(liste_points, taille_groupe=3):
    """
    Calcule toutes les combinaisons uniques possibles.
    Retourne une liste de tuples.
    """
    return list(itertools.combinations(liste_points, taille_groupe))

def configurer_affichage(nb_combos, nb_cols=6):
    """
    Calcule dynamiquement le nombre de lignes nécessaires 
    et prépare la figure matplotlib.
    """
    nb_rows = math.ceil(nb_combos / nb_cols)
    fig, axes = plt.subplots(nb_rows, nb_cols, figsize=(15, 2 * nb_rows))
    if nb_combos == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
        
    return fig, axes

def dessiner_planche_combinaisons(points_base, nb_a_choisir=3, colonnes=6):
    """
    Fonction principale qui orchestre le calcul et le dessin.
    """
    combos = calculer_combinaisons(points_base, nb_a_choisir)
    total = len(combos)
    
    if total == 0:
        print("Erreur : Pas assez de points pour créer des groupes.")
        return
    fig, axes_plats = configurer_affichage(total, colonnes)
    fig.suptitle(f"Visualisation de {total} combinaisons ({nb_a_choisir} points parmi {len(points_base)})", fontsize=16)
    for i in range(len(axes_plats)):
        ax = axes_plats[i]
        
        if i < total:
            combo_actuelle = combos[i]
            ax.scatter(points_base, [0]*len(points_base), color='lightgrey', s=20, zorder=1)
            ax.scatter(combo_actuelle, [0]*nb_a_choisir, color='red', s=40, zorder=2)
            ax.axhline(0, color='black', linewidth=0.5, zorder=0)
            ax.set_xlim(min(points_base)-1, max(points_base)+1)
            ax.set_ylim(-0.1, 0.1)
            ax.set_title(f"n°{i+1}", fontsize=8)
        
        ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

mes_points = [1, 3, 7, 9, 15, 17, 19, 21]
dessiner_planche_combinaisons(mes_points, nb_a_choisir=3, colonnes=7)

#ecercice 2: 3 cluster les point noir serons affecté au point coloré (centre de cluster) le plus proche
# ==========================================
# 1. DONNÉES DE L'EXERCICE
# ==========================================

points_1d = [1, 3, 7, 9, 15, 17, 19, 21]

import matplotlib.pyplot as plt
import itertools
import math

# ==========================================
# 1. DONNÉES 2D ET 3D
# ==========================================

points_2d = [
    [1, 16], [3, 15], [7, 18], [9, 22], 
    [15, 20], [17, 21], [19, 19], [21, 20]
]

points_3d = [
    [1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], 
    [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]
]

# ==========================================
# 2. FONCTIONS DE DISTANCE
# ==========================================

def calculer_L1_multi(p1, p2):
    somme = 0
    for i in range(len(p1)):
        diff = p1[i] - p2[i]
        if diff < 0:
            diff = diff * -1
        somme = somme + diff
    return somme

def calculer_L2_multi(p1, p2):
    somme_carres = 0
    for i in range(len(p1)):
        diff = p1[i] - p2[i]
        somme_carres = somme_carres + (diff ** 2)
    return math.sqrt(somme_carres)

# ==========================================
# 3. CALCUL DU SCORE GLOBAL
# ==========================================

def calculer_score_config_multi(liste_points, centres, type_score):
    score_total = 0
    for p in liste_points:
        distance_min = 9999999
        for c in centres:
            if type_score == "L1":
                d = calculer_L1_multi(p, c)
            else:
                d = calculer_L2_multi(p, c)
            
            if d < distance_min:
                distance_min = d
        score_total = score_total + distance_min
    return score_total

# ==========================================
# 4. FONCTION DE COMPARAISON GRAPHIQUE
# ==========================================

def comparer_L1_L2(liste_points, nb_centres):
    # Générer les combinaisons
    combos = list(itertools.combinations(liste_points, nb_centres))
    
    # Listes pour stocker les scores
    scores_L1 = []
    scores_L2 = []
    indices = []
    
    compteur = 1
    for c in combos:
        # On calcule les deux scores pour la MÊME configuration
        s1 = calculer_score_config_multi(liste_points, c, "L1")
        s2 = calculer_score_config_multi(liste_points, c, "L2")
        
        scores_L1.append(s1)
        scores_L2.append(s2)
        indices.append(compteur)
        compteur = compteur + 1
        
    # Création du graphique de comparaison
    plt.figure(figsize=(14, 7))
    
    # Courbe L1
    plt.plot(indices, scores_L1, label='Score L1 (Manhattan)', color='orange', marker='o', markersize=3, linewidth=1.5)
    
    # Courbe L2
    plt.plot(indices, scores_L2, label='Score L2 (Euclidien)', color='blue', marker='s', markersize=3, linewidth=1.5)
    
    # Esthétique
    dimensions = len(liste_points[0])
    plt.title(f"Comparaison des scores L1 et L2 en {dimensions}D\n({len(combos)} configurations testées)")
    plt.xlabel("Index de la configuration")
    plt.ylabel("Score Total (Somme des distances)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # On ajoute une zone colorée entre les deux pour bien voir l'écart
    plt.fill_between(indices, scores_L1, scores_L2, color='gray', alpha=0.1, label='Différence L1-L2')
    
    plt.show()

# ==========================================
# 5. EXÉCUTION
# ==========================================

# Comparaison pour les points 2D
#print("Génération du graphique de comparaison 2D...")
#comparer_L1_L2(points_2d, 3)

# Comparaison pour les points 3D
#print("Génération du graphique de comparaison 3D...")
#comparer_L1_L2(points_3d, 3)




# faire recherche cas kmeans pour 1d , toujours l2 + faire un histogramme pour voire convergence des donées 
def trouver_meilleure_config(liste_points, k):
    combos = list(itertools.combinations(liste_points, k))
    meilleur_score = float('inf')
    meilleurs_centres = None
    
    for centres in combos:
        score_actuel = sum(min(calculer_L2_multi(p, c) for c in centres) for p in liste_points)
        if score_actuel < meilleur_score:
            meilleur_score = score_actuel
            meilleurs_centres = centres
    return meilleurs_centres, meilleur_score

def assigner_clusters(liste_points, centres):
    return [dist_min_index(p, centres) for p in liste_points]

def dist_min_index(p, centres):
    distances = [calculer_L2_multi(p, c) for c in centres]
    return distances.index(min(distances))

# --- Fonctions de recherche et d'affichage ---

def kmeans_1d(points_bruts, k=3):
    points = [[x] for x in points_bruts]
    centres, score = trouver_meilleure_config(points, k)
    
    # Affichage des centres dans la console
    print(f"\n--- Résultats K-means 1D (k={k}) ---")
    for i, c in enumerate(centres):
        print(f"Centre {i+1} : x = {c[0]}")
    print(f"Score total L2 : {score:.2f}")

    clusters = assigner_clusters(points, centres)
    plt.figure(figsize=(10, 2))
    plt.scatter(points_bruts, [0]*len(points_bruts), c=clusters, cmap='viridis', s=100, zorder=2)
    plt.scatter([c[0] for c in centres], [0]*k, marker='x', color='red', s=200, label="Centres")
    plt.title(f"K-means 1D - Centres : {[c[0] for c in centres]}")
    plt.yticks([])
    plt.show()

def kmeans_2d(points, k=3):
    centres, score = trouver_meilleure_config(points, k)
    
    # Affichage des centres dans la console
    print(f"\n--- Résultats K-means 2D (k={k}) ---")
    for i, c in enumerate(centres):
        print(f"Centre {i+1} : [x={c[0]}, y={c[1]}]")
    print(f"Score total L2 : {score:.2f}")

    clusters = assigner_clusters(points, centres)
    plt.figure(figsize=(8, 6))
    plt.scatter([p[0] for p in points], [p[1] for p in points], c=clusters, cmap='viridis', s=50)
    plt.scatter([c[0] for c in centres], [c[1] for c in centres], marker='x', color='red', s=200, label="Centres")
    plt.title(f"K-means 2D - Score L2 : {score:.2f}")
    plt.grid(True, alpha=0.3)
    plt.show()

def kmeans_3d(points, k=3):
    centres, score = trouver_meilleure_config(points, k)
    
    # Affichage des centres dans la console
    print(f"\n--- Résultats K-means 3D (k={k}) ---")
    for i, c in enumerate(centres):
        print(f"Centre {i+1} : [x={c[0]}, y={c[1]}, z={c[2]}]")
    print(f"Score total L2 : {score:.2f}")

    clusters = assigner_clusters(points, centres)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter([p[0] for p in points], [p[1] for p in points], [p[2] for p in points], c=clusters, cmap='viridis', s=50)
    ax.scatter([c[0] for c in centres], [c[1] for c in centres], [c[2] for c in centres], marker='x', color='red', s=200, label="Centres")
    ax.set_title(f"K-means 3D - Score L2 : {score:.2f}")
    plt.show()
def histogramme_minima(liste_points, k=3, titre="Distribution des scores"):
    """
    Calcule les scores de TOUTES les combinaisons et affiche leur distribution.
    """
    # 1. Préparation des points si c'est du 1D
    if isinstance(liste_points[0], (int, float)):
        points = [[p] for p in liste_points]
    else:
        points = liste_points
        
    # 2. Calcul de tous les scores possibles
    combos = list(itertools.combinations(points, k))
    tous_les_scores = []
    
    for centres in combos:
        score_actuel = sum(min(calculer_L2_multi(p, c) for c in centres) for p in points)
        tous_les_scores.append(score_actuel)
    
    meilleur_score = min(tous_les_scores)
    
    # 3. Création de l'histogramme
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(tous_les_scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    
    # Ajouter une ligne verticale pour le score minimum (le meilleur)
    plt.axvline(meilleur_score, color='red', linestyle='dashed', linewidth=2, label=f'Meilleur score : {meilleur_score:.2f}')
    
    # Esthétique
    plt.title(f"{titre}\n({len(combos)} combinaisons testées)")
    plt.xlabel("Score (Somme des distances L2)")
    plt.ylabel("Nombre de combinaisons")
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    print(f"Analyse terminée : {len(tous_les_scores)} combinaisons évaluées.")
    print(f"Score min : {meilleur_score:.2f} | Score max : {max(tous_les_scores):.2f}")
    
    plt.show()
# --- Données de test ---
p1d = [1, 3, 7, 9, 15, 17, 19, 21]
p2d = [[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]
p3d = [[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]]

# Exécution
kmeans_1d(p1d, 3)
kmeans_2d(p2d, 3)
kmeans_3d(p3d, 3)
histogramme_minima(p1d, k=3, titre="Histogramme des scores - Points 1D")
histogramme_minima(p2d, k=3, titre="Histogramme des scores - Points 2D")
histogramme_minima(p3d, k=3, titre="Histogramme des scores - Points 1D")


def convergence_1d(points_bruts, k=3):
    # Transformation des points en format [x, 0] pour le calcul
    points = np.array([[x, 0] for x in points_bruts])
    # Initialisation : on choisit k points au hasard
    centres = points[np.random.choice(len(points), k, replace=False)].astype(float)
    
    historique = [centres.copy()]
    
    # Boucle d'itération
    for _ in range(10):
        # 1. Assignation
        distances = np.linalg.norm(points[:, np.newaxis] - centres, axis=2)
        clusters = np.argmin(distances, axis=1)
        
        # 2. Mise à jour
        nouveaux_centres = np.array([points[clusters == i].mean(axis=0) if len(points[clusters == i]) > 0 else centres[i] for i in range(k)])
        if np.allclose(centres, nouveaux_centres): break
        centres = nouveaux_centres
        historique.append(centres.copy())

    # Visualisation
    plt.figure(figsize=(10, 5))
    for it, c_pos in enumerate(historique):
        plt.scatter(c_pos[:, 0], [it] * k, marker='x', color='red', s=100)
        if it > 0: # Dessiner les lignes de mouvement
            for j in range(k):
                plt.plot([historique[it-1][j, 0], c_pos[j, 0]], [it-1, it], 'r--', alpha=0.4)
    
    plt.scatter(points[:, 0], [-1] * len(points), c=clusters, cmap='viridis', s=100)
    plt.title("Convergence 1D : Les centres (x) montent au fil des itérations")
    plt.xlabel("Position des points")
    plt.ylabel("Itérations")
    plt.show()

def convergence_2d(points_list, k=3):
    points = np.array(points_list)
    indices = np.random.choice(len(points), k, replace=False)
    centres = points[indices].astype(float)
    historique = [centres.copy()]
    
    for _ in range(10):
        distances = np.linalg.norm(points[:, np.newaxis] - centres, axis=2)
        clusters = np.argmin(distances, axis=1)
        nouveaux_centres = np.array([points[clusters == i].mean(axis=0) if len(points[clusters == i]) > 0 else centres[i] for i in range(k)])
        if np.allclose(centres, nouveaux_centres): break
        centres = nouveaux_centres
        historique.append(centres.copy())

    plt.figure(figsize=(8, 6))
    plt.scatter(points[:, 0], points[:, 1], c=clusters, cmap='viridis', alpha=0.5)
    
    historique = np.array(historique)
    for j in range(k):
        traj = historique[:, j, :]
        plt.plot(traj[:, 0], traj[:, 1], 'o-', label=f'Centre {j+1}')
        plt.scatter(traj[0, 0], traj[0, 1], marker='s', s=100, color='black') # Départ
        plt.scatter(traj[-1, 0], traj[-1, 1], marker='X', s=200, color='red') # Fin
        
    plt.title("Convergence 2D : Trajectoire des centres")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def convergence_3d(points_list, k=3):
    points = np.array(points_list)
    centres = points[np.random.choice(len(points), k, replace=False)].astype(float)
    historique = [centres.copy()]
    
    for _ in range(10):
        distances = np.linalg.norm(points[:, np.newaxis] - centres, axis=2)
        clusters = np.argmin(distances, axis=1)
        nouveaux_centres = np.array([points[clusters == i].mean(axis=0) if len(points[clusters == i]) > 0 else centres[i] for i in range(k)])
        if np.allclose(centres, nouveaux_centres): break
        centres = nouveaux_centres
        historique.append(centres.copy())

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=clusters, cmap='viridis', alpha=0.3)
    
    historique = np.array(historique)
    for j in range(k):
        traj = historique[:, j, :]
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'o-', linewidth=2)
        ax.scatter(traj[-1, 0], traj[-1, 1], traj[-1, 2], marker='X', s=200)

    plt.title("Convergence 3D : Mouvement dans l'espace")
    plt.show()
