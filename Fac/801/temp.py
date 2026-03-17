import matplotlib.pyplot as plt
import itertools
import math
from mpl_toolkits.mplot3d import Axes3D
# faire kmedian, kmean et exhaustive: calculeconvergence.
# ==========================================
# 1. FONCTIONS DE DISTANCE (BOUCLES EXPLICITES)
# ==========================================
def tracer_toutes_combinaisons(points, k, nom_dim):
    """Génère une planche de graphiques montrant chaque combinaison possible."""
    combos = list(itertools.combinations(points, k))
    nb_combos = len(combos)
    
    # On calcule le nombre de colonnes et de lignes pour la grille
    nb_cols = 7
    nb_rows = math.ceil(nb_combos / nb_cols)
    
    fig, axes = plt.subplots(nb_rows, nb_cols, figsize=(18, 2 * nb_rows))
    fig.suptitle(f"Toutes les combinaisons possibles - {nom_dim} ({nb_combos} au total)", fontsize=16)
    
    # On transforme la grille en liste simple pour boucler facilement
    axes_plats = axes.flatten()
    
    compteur = 0
    for i in range(len(axes_plats)):
        ax = axes_plats[i]
        
        if i < nb_combos:
            combo_actuelle = combos[i]
            
            # 1. Dessiner tous les points en gris (fond)
            for p in points:
                if len(p) == 1: # 1D
                    ax.scatter(p[0], 0, color='lightgrey', s=20, zorder=1)
                else: # 2D
                    ax.scatter(p[0], p[1], color='lightgrey', s=20, zorder=1)
            
            # 2. Dessiner les centres de cette combinaison en rouge
            for c in combo_actuelle:
                if len(c) == 1: # 1D
                    ax.scatter(c[0], 0, color='red', s=40, zorder=2)
                else: # 2D
                    ax.scatter(c[0], c[1], color='red', s=40, zorder=2)
            
            ax.set_title(f"n°{i+1}", fontsize=8)
        
        # On cache les axes pour que ce soit plus propre
        ax.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def calculer_distance_l1(p1, p2):
    """Calcule la distance de Manhattan (L1)."""
    somme = 0
    for i in range(len(p1)):
        diff = p1[i] - p2[i]
        if diff < 0:
            diff = diff * -1
        somme = somme + diff
    return somme

def calculer_distance_l2(p1, p2):
    """Calcule la distance Euclidienne (L2)."""
    somme_carres = 0
    for i in range(len(p1)):
        diff = p1[i] - p2[i]
        somme_carres = somme_carres + (diff ** 2)
    resultat = math.sqrt(somme_carres)
    return resultat

# ==========================================
# 2. FONCTIONS DE CALCUL DES SCORES
# ==========================================

def calculer_score_global(points, centres, metrique):
    """Calcule la somme des distances minimales pour une config donnée."""
    score_total = 0
    for p in points:
        dist_min = 999999999.0
        for c in centres:
            if metrique == "L1":
                d = calculer_distance_l1(p, c)
            else:
                d = calculer_distance_l2(p, c)
            
            if d < dist_min:
                dist_min = d
        score_total = score_total + dist_min
    return score_total

def obtenir_tous_les_scores(points, k, metrique):
    """Retourne la liste des scores de toutes les combinaisons possibles."""
    combos = list(itertools.combinations(points, k))
    liste_resultats = []
    for c in combos:
        s = calculer_score_global(points, c, metrique)
        liste_resultats.append(s)
    return liste_resultats

def trouver_meilleurs_centres(points, k, metrique):
    """Recherche exhaustive de la meilleure configuration (K-means optimal)."""
    combos = list(itertools.combinations(points, k))
    meilleur_score = 999999999.0
    meilleurs_centres = None
    
    for c in combos:
        score_actuel = calculer_score_global(points, c, metrique)
        if score_actuel < meilleur_score:
            meilleur_score = score_actuel
            meilleurs_centres = c
            
    return meilleurs_centres, meilleur_score

# ==========================================
# 3. FONCTIONS DE GRAPHIQUES (1 SEULE UTILITÉ)
# ==========================================

def tracer_visualisation_clusters(ax, points, centres, metrique, titre):
    """Affiche les points colorés par cluster (Gère 1D, 2D, 3D)."""
    dim = len(points[0])
    couleurs = []
    
    for p in points:
        d_min = 99999999.0
        idx = 0
        for i in range(len(centres)):
            if metrique == "L1":
                d = calculer_distance_l1(p, centres[i])
            else:
                d = calculer_distance_l2(p, centres[i])
            if d < d_min:
                d_min = d
                idx = i
        couleurs.append(idx)
    
    if dim == 1:
        for i in range(len(points)):
            ax.scatter(points[i][0], 0, c=[couleurs[i]], cmap='viridis', s=100)
        for c in centres:
            ax.scatter(c[0], 0, marker='x', color='red', s=200)
        ax.set_yticks([])
    elif dim == 2:
        px, py = [], []
        for p in points:
            px.append(p[0])
            py.append(p[1])
        ax.scatter(px, py, c=couleurs, cmap='viridis', s=80)
        for c in centres:
            ax.scatter(c[0], c[1], marker='x', color='red', s=200)
    elif dim == 3:
        px, py, pz = [], [], []
        for p in points:
            px.append(p[0]); py.append(p[1]); pz.append(p[2])
        ax.scatter(px, py, pz, c=couleurs, cmap='viridis', s=60)
        for c in centres:
            ax.scatter(c[0], c[1], c[2], marker='x', color='red', s=200)
    ax.set_title(titre)

def tracer_comparaison_metriques(ax, scores_l1, scores_l2):
    """Affiche la comparaison linéaire entre L1 et L2."""
    ax.plot(scores_l1, label="Scores L1 (Manhattan)", color="orange")
    ax.plot(scores_l2, label="Scores L2 (Euclidien)", color="blue")
    ax.set_title("Comparaison L1 vs L2")
    ax.legend()

def tracer_paysage_minimas(ax, scores):
    """Affiche le graphique des scores et pointe le minimum avec une flèche."""
    indices = []
    for i in range(len(scores)):
        indices.append(i)
    
    # Dessin de la courbe
    ax.plot(indices, scores, color="green", linewidth=1.5, alpha=0.7)
    
    # 1. Recherche du minimum
    val_min = scores[0]
    idx_min = 0
    for i in range(len(scores)):
        if scores[i] < val_min:
            val_min = scores[i]
            idx_min = i
            
    # 2. Ajout du point rouge sur le minimum
    ax.scatter(idx_min, val_min, color="red", s=30, zorder=5)

    # 3. Ajout de la flèche avec annotation
    # On décale le texte vers le haut de 15% de la hauteur totale du graphique
    hauteur_max = 0
    for s in scores:
        if s > hauteur_max:
            hauteur_max = s
    offset = hauteur_max * 0.15

    ax.annotate(
        f"Min: {val_min:.2f}", 
        xy=(idx_min, val_min), 
        xytext=(idx_min, val_min + offset),
        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=7),
        horizontalalignment='center',
        fontweight='bold',
        color='red'
    )
    
    ax.set_title("Paysage des Minimas (L2)")
    ax.set_xlabel("Index de la combinaison")
    ax.set_ylabel("Score (Distance)")
def tracer_histogramme_distribution(ax, scores):
    """Affiche la distribution des scores pour voir la convergence."""
    ax.hist(scores, bins=15, color="skyblue", edgecolor="black")
    ax.set_title("Distribution des Scores")

# ==========================================
# 4. FONCTION D'ORCHESTRATION
# ==========================================

def executer_analyse_complete(points, k, label):
    """Lance tous les calculs et affiche les résultats dans une fenêtre."""
    # Calculs
    centres_opti, score_final = trouver_meilleurs_centres(points, k, "L2")
    scores_l1 = obtenir_tous_les_scores(points, k, "L1")
    scores_l2 = obtenir_tous_les_scores(points, k, "L2")
    
    # Création de la figure avec 4 sous-graphiques
    fig = plt.figure(figsize=(14, 9))
    fig.suptitle(f"Analyse Clustering {label} (k={k})", fontsize=16)
    
    # Choix de la projection pour le graphique de clusters
    if len(points[0]) == 3:
        ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    else:
        ax1 = fig.add_subplot(2, 2, 1)
        
    # Appels des fonctions de dessin
    tracer_visualisation_clusters(ax1, points, centres_opti, "L2", "Meilleur Cas")
    tracer_comparaison_metriques(fig.add_subplot(2, 2, 2), scores_l1, scores_l2)
    tracer_paysage_minimas(fig.add_subplot(2, 2, 3), scores_l2)
    tracer_histogramme_distribution(fig.add_subplot(2, 2, 4), scores_l2)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    
    return centres_opti, score_final

# ==========================================
# 5. DONNÉES DE TEST ET EXÉCUTION
# ==========================================

# Préparation des points
p1d = [[1], [3], [7], [9], [15], [17], [19], [21]]
p2d = [[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]
p3d = [[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], 
       [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]]

# Lancement pour les 3 cas
print("Lancement de l'analyse 1D...")
tracer_toutes_combinaisons(p1d, 3, "1D")
executer_analyse_complete(p1d, 3, "1D")

print("Lancement de l'analyse 2D...")
tracer_toutes_combinaisons(p2d, 3, "2D")
executer_analyse_complete(p2d, 3, "2D")

print("Lancement de l'analyse 3D...")
tracer_toutes_combinaisons(p3d, 3, "3D")
executer_analyse_complete(p3d, 3, "3D")

#affiche score en fonction des configs
#kmean   d1 d2 d3
#kmedian d1 d2 d3
#kmean++ d1 d2 d3
#faire kmean et le reste directement sur les document