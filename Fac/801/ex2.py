import matplotlib.pyplot as plt
import numpy as np
import itertools

# ==========================================
# 1. DONNÉES
# ==========================================
datasets = {
    "1D": np.array([1, 3, 7, 9, 15, 17, 19, 21]).reshape(-1, 1),
    "2D": np.array([[1, 16], [3, 15], [7, 18], [9, 22], [15, 20], [17, 21], [19, 19], [21, 20]]),
    "3D": np.array([[1, 16, 55], [3, 15, 50], [7, 18, 60], [9, 22, 70], 
                    [15, 20, 70], [17, 21, 65], [19, 19, 55], [21, 20, 60]])
}

def calculer_score(points, centres):
    """Calcul de la somme des distances L2 au centre le plus proche."""
    distances = np.linalg.norm(points[:, np.newaxis] - centres, ord=2, axis=2)
    return np.sum(np.min(distances, axis=1))

# ==========================================
# 2. ANALYSE ET GRAPHIQUES "STYLE TABLEAU"
# ==========================================

def produire_analyse_tableau(nom, points, k=3):
    # 1. Calcul de TOUTES les combinaisons (Surface d'erreur)
    combos_indices = list(itertools.combinations(range(len(points)), k))
    tous_les_scores = []
    
    for idx in combos_indices:
        centres = points[list(idx)]
        tous_les_scores.append(calculer_score(points, centres))
    
    tous_les_scores = np.array(tous_les_scores)
    scores_uniques, counts = np.unique(np.round(tous_les_scores, 2), return_counts=True)
    
    # --- AFFICHAGE DES VALEURS DANS LA CONSOLE ---
    print(f"\n{'='*50}")
    print(f"ANALYSE DES CONVERGENCES - DATASET {nom}")
    print(f"{'='*50}")
    print(f"Nombre total de configurations : {len(tous_les_scores)}")
    print("\nRépartition des scores (Histogramme) :")
    for s, c in zip(scores_uniques, counts):
        print(f"  Score {s:6.2f} : trouvé dans {c:2d} configurations")
    
    meilleur_score = np.min(tous_les_scores)
    idx_meilleur = np.where(np.round(tous_les_scores, 2) == round(meilleur_score, 2))[0][0]
    meilleurs_centres = points[list(combos_indices[idx_meilleur])]
    
    print(f"\nMEILLEUR MINIMUM (Score {meilleur_score:.2f}) :")
    print(f"  Centres optimaux : {meilleurs_centres.tolist()}")

    # --- CRÉATION DES GRAPHIQUES ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 2]})
    plt.subplots_adjust(hspace=0.3)

    # A. Histogramme des scores (Haut du tableau)
    ax1.bar(range(len(scores_uniques)), counts, color='lightgray', edgecolor='black')
    ax1.set_xticks(range(len(scores_uniques)))
    ax1.set_xticklabels([f"S={s}" for s in scores_uniques], rotation=45, fontsize=8)
    ax1.set_title(f"Répartition des 56 configurations par Score - {nom}")
    ax1.set_ylabel("Nombre de configurations")
    
    # Ajout des étiquettes de texte sur les barres (comme le 27/28 du tableau)
    for i, c in enumerate(counts):
        ax1.text(i, c + 0.5, str(c), ha='center', fontweight='bold')

    # B. Graphique des scores "en dents de scie" (Bas du tableau)
    ax2.plot(tous_les_scores, color='black', linewidth=1.5)
    ax2.set_title(f"Surface d'Erreur (Scores de toutes les combinaisons) - {nom}")
    ax2.set_xlabel("Index de la configuration (0 à 55)")
    ax2.set_ylabel("Score (Somme distances L2)")
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Marquer les points bas (minima)
    ax2.scatter(np.argmin(tous_les_scores), meilleur_score, color='red', s=100, label="Minimum Global")
    
    plt.show()

# ==========================================
# 3. EXÉCUTION
# ==========================================
for nom, data in datasets.items():
    produire_analyse_tableau(nom, data)