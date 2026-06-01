import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import AgglomerativeClustering, Birch
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score
from Exercice_1 import calculer_score_config_multi, calculer_L2_multi
from Exercice_2 import executer_kmeans, initialiser_centres_aleatoires


###############################
# 1. Données
###############################

points_1d = [[1], [3], [7], [9], [15], [17], [19], [21]]
points_2d = [[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]
points_3d = [[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]]


###############################
# 2. Fonctions pont sklearn → projet
###############################

def renumeroter_labels(labels):
    # Garantit des labels contigus de 0 à k-1 (utile notamment pour BIRCH)
    valeurs_uniques = sorted(set(labels))
    correspondance = {}
    for i, v in enumerate(valeurs_uniques):
        correspondance[v] = i
    labels_renumerotes = []
    for l in labels:
        labels_renumerotes.append(correspondance[l])
    return labels_renumerotes

def calculer_centres_depuis_labels(liste_points, labels, k):
    dim = len(liste_points[0])
    centres = []

    for i in range(k):
        # Récupérer les points du cluster i
        points_cluster = []
        for j in range(len(liste_points)):
            if labels[j] == i:
                points_cluster.append(liste_points[j])

        if len(points_cluster) == 0:
            # Cluster vide : utiliser le centroïde global
            centre = []
            for d in range(dim):
                somme = 0
                for p in liste_points:
                    somme += p[d]
                centre.append(somme / len(liste_points))
            centres.append(centre)
        else:
            centre = []
            for d in range(dim):
                somme = 0
                for p in points_cluster:
                    somme += p[d]
                centre.append(somme / len(points_cluster))
            centres.append(centre)

    return centres


###############################
# 3. AGNES
###############################

def executer_agnes(liste_points, k, linkage="ward"):
    modele = AgglomerativeClustering(n_clusters=k, linkage=linkage)
    labels_bruts = modele.fit_predict(liste_points)
    labels = renumeroter_labels(list(labels_bruts))
    centres = calculer_centres_depuis_labels(liste_points, labels, k)
    cout = calculer_score_config_multi(liste_points, centres, "L2")
    return centres, labels, cout

def tester_agnes_linkages(liste_points, k, nom_dataset):
    linkages = ["ward", "complete", "average", "single"]
    resultats = {}

    for linkage in linkages:
        centres, affectations, cout = executer_agnes(liste_points, k, linkage)
        resultats[linkage] = cout
        print(f"  AGNES [{linkage}] sur {nom_dataset} (k={k}) : coût L2 = {round(cout, 2)}")

    afficher_grille_agnes_linkages(liste_points, k, nom_dataset)
    return resultats

def tester_agnes_k_values(liste_points, valeurs_k, linkage, nom_dataset):
    dim = len(liste_points[0])
    nb_cols = len(valeurs_k)

    fig = plt.figure(figsize=(5 * nb_cols, 5))
    fig.suptitle(f"AGNES [{linkage}] sur {nom_dataset} — différentes valeurs de k")

    for idx, k in enumerate(valeurs_k):
        centres, affectations, cout = executer_agnes(liste_points, k, linkage)

        if dim == 3:
            ax = fig.add_subplot(1, nb_cols, idx + 1, projection='3d')
        else:
            ax = fig.add_subplot(1, nb_cols, idx + 1)

        dessiner_cluster(ax, liste_points, centres, affectations)
        ax.set_title(f"k={k}\nCoût={round(cout, 2)}")

    plt.tight_layout()
    plt.show()


###############################
# 4. BIRCH
###############################

def executer_birch(liste_points, k, threshold=0.5, branching_factor=50):
    modele = Birch(n_clusters=k, threshold=threshold, branching_factor=branching_factor)
    labels_bruts = modele.fit_predict(liste_points)
    labels = renumeroter_labels(list(labels_bruts))
    centres = calculer_centres_depuis_labels(liste_points, labels, k)
    cout = calculer_score_config_multi(liste_points, centres, "L2")
    return centres, labels, cout

def tester_birch_parametres(liste_points, k, nom_dataset):
    thresholds = [0.3, 0.5, 1.0, 2.0]
    branching_factors = [10, 50]
    dim = len(liste_points[0])

    nb_lignes = len(branching_factors)
    nb_cols = len(thresholds)

    fig = plt.figure(figsize=(5 * nb_cols, 5 * nb_lignes))
    fig.suptitle(f"BIRCH sur {nom_dataset} (k={k}) — grille threshold × branching_factor")

    idx = 1
    for bf in branching_factors:
        for th in thresholds:
            centres, affectations, cout = executer_birch(liste_points, k, th, bf)

            if dim == 3:
                ax = fig.add_subplot(nb_lignes, nb_cols, idx, projection='3d')
            else:
                ax = fig.add_subplot(nb_lignes, nb_cols, idx)

            dessiner_cluster(ax, liste_points, centres, affectations)
            ax.set_title(f"th={th}, bf={bf}\nCoût={round(cout, 2)}", fontsize=8)
            idx += 1

    plt.tight_layout()
    plt.show()

def tester_birch_k_values(liste_points, valeurs_k, nom_dataset):
    dim = len(liste_points[0])
    nb_cols = len(valeurs_k)

    fig = plt.figure(figsize=(5 * nb_cols, 5))
    fig.suptitle(f"BIRCH sur {nom_dataset} — différentes valeurs de k")

    for idx, k in enumerate(valeurs_k):
        centres, affectations, cout = executer_birch(liste_points, k)

        if dim == 3:
            ax = fig.add_subplot(1, nb_cols, idx + 1, projection='3d')
        else:
            ax = fig.add_subplot(1, nb_cols, idx + 1)

        dessiner_cluster(ax, liste_points, centres, affectations)
        ax.set_title(f"k={k}\nCoût={round(cout, 2)}")

    plt.tight_layout()
    plt.show()


###############################
# 5. Visualisation
###############################

def dessiner_cluster(ax, liste_points, centres, affectations):
    dim = len(liste_points[0])

    # Dessin des points colorés par cluster
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

def afficher_resultat_clustering(liste_points, centres, affectations, titre):
    dim = len(liste_points[0])
    fig = plt.figure(figsize=(8, 6))

    if dim == 3:
        ax = fig.add_subplot(111, projection='3d')
    else:
        ax = fig.add_subplot(111)

    dessiner_cluster(ax, liste_points, centres, affectations)
    plt.title(titre)
    plt.show()

def afficher_grille_agnes_linkages(liste_points, k, nom_dataset):
    linkages = ["ward", "complete", "average", "single"]
    dim = len(liste_points[0])
    nb_cols = len(linkages)

    fig = plt.figure(figsize=(5 * nb_cols, 5))
    fig.suptitle(f"AGNES sur {nom_dataset} (k={k}) — comparaison des linkages")

    for idx, linkage in enumerate(linkages):
        centres, affectations, cout = executer_agnes(liste_points, k, linkage)

        if dim == 3:
            ax = fig.add_subplot(1, nb_cols, idx + 1, projection='3d')
        else:
            ax = fig.add_subplot(1, nb_cols, idx + 1)

        dessiner_cluster(ax, liste_points, centres, affectations)
        ax.set_title(f"linkage={linkage}\nCoût={round(cout, 2)}")

    plt.tight_layout()
    plt.show()

def afficher_grille_birch_thresholds(liste_points, k, nom_dataset):
    thresholds = [0.3, 0.5, 1.0, 2.0]
    dim = len(liste_points[0])
    nb_cols = len(thresholds)

    fig = plt.figure(figsize=(5 * nb_cols, 5))
    fig.suptitle(f"BIRCH sur {nom_dataset} (k={k}) — comparaison des thresholds (bf=50)")

    for idx, th in enumerate(thresholds):
        centres, affectations, cout = executer_birch(liste_points, k, threshold=th)

        if dim == 3:
            ax = fig.add_subplot(1, nb_cols, idx + 1, projection='3d')
        else:
            ax = fig.add_subplot(1, nb_cols, idx + 1)

        dessiner_cluster(ax, liste_points, centres, affectations)
        ax.set_title(f"threshold={th}\nCoût={round(cout, 2)}")

    plt.tight_layout()
    plt.show()


###############################
# 6. Comparaison avec K-means
###############################

def comparer_algorithmes(liste_points, k, nom_dataset, type_dist="L2"):
    resultats = {}

    # K-means : 5 runs, on garde le meilleur coût
    meilleur_cout_kmeans = float('inf')
    for _ in range(5):
        centres_init = initialiser_centres_aleatoires(liste_points, k)
        centres_finaux, affectations, cout, iterations = executer_kmeans(liste_points, centres_init, type_dist)
        if cout < meilleur_cout_kmeans:
            meilleur_cout_kmeans = cout
    resultats["K-means"] = meilleur_cout_kmeans

    # AGNES avec les 4 linkages
    for linkage in ["ward", "complete", "average", "single"]:
        centres, affectations, cout = executer_agnes(liste_points, k, linkage)
        resultats["AGNES-" + linkage] = cout

    # BIRCH avec paramètres par défaut
    centres, affectations, cout = executer_birch(liste_points, k)
    resultats["BIRCH"] = cout

    return resultats

def afficher_comparaison_barchart(resultats, nom_dataset, k):
    noms = list(resultats.keys())
    couts = list(resultats.values())

    # Couleurs selon l'algorithme
    couleurs = []
    for nom in noms:
        if nom.startswith("K-means"):
            couleurs.append("red")
        elif nom.startswith("AGNES"):
            couleurs.append("steelblue")
        else:
            couleurs.append("green")

    plt.figure(figsize=(10, 5))
    barres = plt.bar(noms, couts, color=couleurs, edgecolor='black')
    plt.title(f"Comparaison des coûts L2 — {nom_dataset} (k={k})")
    plt.xlabel("Algorithme")
    plt.ylabel("Coût L2")
    plt.xticks(rotation=20, ha='right')

    for barre in barres:
        yval = barre.get_height()
        plt.text(barre.get_x() + barre.get_width() / 2, yval + 0.1, round(yval, 2), ha='center', va='bottom', fontsize=9)

    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()


###############################
# 7. Données ND (synthétiques / INFO708 stub)
###############################

def generer_donnees_nd_synthetiques(n_samples=80, n_features=10, n_centres=3, random_state=42):
    # Pour remplacer par les vraies données INFO708 :
    # Remplacer liste_points_nd par la matrice de représentation (TF-IDF, BM25, Doc2Vec, etc.)
    # et y_liste par les étiquettes réelles des documents (topics, catégories...)
    X, y_true = make_blobs(n_samples=n_samples, n_features=n_features, centers=n_centres, random_state=random_state)
    # Conversion en listes Python
    liste_points_nd = []
    for ligne in X:
        liste_points_nd.append([float(v) for v in ligne])
    y_liste = [int(v) for v in y_true]
    return liste_points_nd, y_liste

def tester_agnes_nd(liste_points, y_true, k, linkages):
    resultats = {}
    print(f"\n  {'Linkage':<15} {'ARI':>8}")
    print("  " + "-" * 25)

    for linkage in linkages:
        modele = AgglomerativeClustering(n_clusters=k, linkage=linkage)
        labels_bruts = modele.fit_predict(liste_points)
        labels = renumeroter_labels(list(labels_bruts))
        ari = adjusted_rand_score(y_true, labels)
        resultats[linkage] = ari
        print(f"  {linkage:<15} {round(ari, 4):>8}")

    return resultats

def tester_birch_nd(liste_points, y_true, k):
    thresholds = [0.3, 0.5, 1.0, 2.0]
    resultats = {}
    print(f"\n  {'Threshold':<15} {'ARI':>8}")
    print("  " + "-" * 25)

    for th in thresholds:
        modele = Birch(n_clusters=k, threshold=th)
        labels_bruts = modele.fit_predict(liste_points)
        labels = renumeroter_labels(list(labels_bruts))
        ari = adjusted_rand_score(y_true, labels)
        resultats[th] = ari
        print(f"  {th:<15} {round(ari, 4):>8}")

    return resultats

def afficher_tableau_ari(resultats_agnes, resultats_birch):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')

    # Construction des données du tableau
    donnees_tableau = []
    for linkage, ari in resultats_agnes.items():
        donnees_tableau.append(["AGNES-" + linkage, round(ari, 4)])
    for th, ari in resultats_birch.items():
        donnees_tableau.append(["BIRCH (threshold=" + str(th) + ")", round(ari, 4)])

    tableau = ax.table(
        cellText=donnees_tableau,
        colLabels=["Algorithme", "ARI"],
        loc='center',
        cellLoc='center'
    )
    tableau.auto_set_font_size(False)
    tableau.set_fontsize(11)
    tableau.scale(1.5, 1.8)
    plt.title("Scores ARI — Données ND synthétiques")
    plt.tight_layout()
    plt.show()


###############################
# Main
###############################
if __name__ == "__main__":

    k = 3

    ##############################################################
    # PARTIE 1 : AGNES
    ##############################################################

    ##############
    #   D1
    ##############
    print("\n[AGNES] Jeu de données 1D...")
    tester_agnes_linkages(points_1d, k, "1D")
    tester_agnes_k_values(points_1d, [2, 3, 4], "ward", "1D")

    ##############
    #   D2
    ##############
    print("\n[AGNES] Jeu de données 2D...")
    tester_agnes_linkages(points_2d, k, "2D")
    tester_agnes_k_values(points_2d, [2, 3, 4], "ward", "2D")

    ##############
    #   D3
    ##############
    print("\n[AGNES] Jeu de données 3D...")
    tester_agnes_linkages(points_3d, k, "3D")
    tester_agnes_k_values(points_3d, [2, 3, 4], "ward", "3D")

    ##############################################################
    # PARTIE 2 : BIRCH
    ##############################################################

    ##############
    #   D1
    ##############
    print("\n[BIRCH] Jeu de données 1D...")
    tester_birch_parametres(points_1d, k, "1D")
    tester_birch_k_values(points_1d, [2, 3, 4], "1D")

    ##############
    #   D2
    ##############
    print("\n[BIRCH] Jeu de données 2D...")
    tester_birch_parametres(points_2d, k, "2D")
    tester_birch_k_values(points_2d, [2, 3, 4], "2D")

    ##############
    #   D3
    ##############
    print("\n[BIRCH] Jeu de données 3D...")
    tester_birch_parametres(points_3d, k, "3D")
    tester_birch_k_values(points_3d, [2, 3, 4], "3D")

    ##############################################################
    # PARTIE 3 : COMPARAISON AVEC K-MEANS
    ##############################################################

    ##############
    #   D1
    ##############
    print("\n[COMPARAISON] Jeu de données 1D...")
    resultats_1d = comparer_algorithmes(points_1d, k, "1D")
    afficher_comparaison_barchart(resultats_1d, "1D", k)

    ##############
    #   D2
    ##############
    print("\n[COMPARAISON] Jeu de données 2D...")
    resultats_2d = comparer_algorithmes(points_2d, k, "2D")
    afficher_comparaison_barchart(resultats_2d, "2D", k)

    ##############
    #   D3
    ##############
    print("\n[COMPARAISON] Jeu de données 3D...")
    resultats_3d = comparer_algorithmes(points_3d, k, "3D")
    afficher_comparaison_barchart(resultats_3d, "3D", k)

    ##############################################################
    # PARTIE 4 : DONNÉES ND SYNTHÉTIQUES
    ##############################################################

    print("\n[ND] Génération des données synthétiques haute dimension...")
    liste_points_nd, y_true = generer_donnees_nd_synthetiques()

    print("\n[AGNES - ND] Scores ARI :")
    resultats_agnes_nd = tester_agnes_nd(liste_points_nd, y_true, k, ["ward", "complete", "average", "single"])

    print("\n[BIRCH - ND] Scores ARI :")
    resultats_birch_nd = tester_birch_nd(liste_points_nd, y_true, k)

    afficher_tableau_ari(resultats_agnes_nd, resultats_birch_nd)
