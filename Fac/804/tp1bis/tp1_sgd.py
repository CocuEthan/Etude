"""
TP1 bis — Tout le contenu du TP1 +
optimisation par SGD, mini-batch et batch (comparaison).

Sections I-VII : identiques au TP1 (aucune ligne supprimée).
Section VIII   : fonction train_model générique (batch / sgd / mini-batch).
Section IX     : comparaison des trois modes sur les trois modèles.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# ===========================================================
# II. Préparation des données d'apprentissage
# ===========================================================

np.random.seed(42)

# Groupe de base centré en (0,0)
G0 = np.random.randn(50, 2) + np.array([0, 0])
# Groupe centré en (2,2) — linéairement séparable
G1 = np.random.randn(50, 2) + np.array([2, 2])

# X : linéairement séparable
X = np.concatenate((G0, G1), axis=0)

plt.scatter(G0[:, 0], G0[:, 1], color='blue', marker='o', label='Groupe 0')
plt.scatter(G1[:, 0], G1[:, 1], color='red',  marker='^', label='Groupe 1')
plt.xlabel("x1")
plt.ylabel("x2")
plt.title("Dataset 2D linéairement séparable")
plt.legend()
plt.show()

# X_ns : non linéairement séparable (centres quasiment identiques → chevauchement)
G0_ns = np.random.randn(50, 2) + np.array([0,   0  ])
G1_ns = np.random.randn(50, 2) + np.array([0.5, 0.5])
X_ns  = np.concatenate((G0_ns, G1_ns), axis=0)

# X_ls : légèrement séparable (petite marge)
G0_ls = np.random.randn(50, 2) + np.array([0,   0  ])
G1_ls = np.random.randn(50, 2) + np.array([1.5, 1.5])
X_ls  = np.concatenate((G0_ls, G1_ls), axis=0)

# Affichage des trois ensembles dans une même figure
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, data, title in zip(
    axes,
    [X, X_ls, X_ns],
    ['X (linéairement séparable)', 'X_ls (légèrement séparable)', 'X_ns (non séparable)']
):
    ax.scatter(data[:50, 0], data[:50, 1], color='blue', marker='o', label='G0')
    ax.scatter(data[50:, 0], data[50:, 1], color='red',  marker='^', label='G1')
    ax.set_title(title)
    ax.legend()
plt.tight_layout()
plt.show()

# ===========================================================
# III. Préparation des données de test
# ===========================================================

def create_test_grid(X_train, resolution=0.2):
    """
    Crée une grille de points couvrant l'espace du dataset d'entraînement.
    X_train   : données d'apprentissage (n_samples, 2)
    resolution: distance entre deux points de la grille
    Retourne xx, yy (matrices meshgrid) et grid_points (n_points, 2)
    """
    x_min, x_max = X_train[:, 0].min() - 1, X_train[:, 0].max() + 1
    y_min, y_max = X_train[:, 1].min() - 1, X_train[:, 1].max() + 1
    xx, yy = np.meshgrid(
        np.arange(x_min, x_max, resolution),
        np.arange(y_min, y_max, resolution)
    )
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    return xx, yy, grid_points

def plot_test_grid(grid_points):
    """Affiche uniquement les points de test (grille)."""
    plt.figure()
    plt.scatter(grid_points[:, 0], grid_points[:, 1], s=10)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title("Points de test (grille)")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

def count_grid_points(grid_points):
    """Retourne le nombre total de points dans la grille."""
    n_points = grid_points.shape[0]
    print(f"Nombre total de points de test : {n_points}")
    return n_points

# Trois grilles de résolutions différentes
xx_dense,  yy_dense,  grid_dense  = create_test_grid(X, resolution=0.05)
xx_medium, yy_medium, grid_medium = create_test_grid(X, resolution=0.2)
xx_sparse, yy_sparse, grid_sparse = create_test_grid(X, resolution=1.0)

count_grid_points(grid_dense)
count_grid_points(grid_medium)
count_grid_points(grid_sparse)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, grid, title in zip(
    axes,
    [grid_dense, grid_medium, grid_sparse],
    ['Grille dense (res=0.05)', 'Grille moyenne (res=0.2)', 'Grille sparse (res=1.0)']
):
    ax.scatter(grid[:, 0], grid[:, 1], s=2)
    ax.set_title(title)
plt.tight_layout()
plt.show()

# Figure 3×3 : toutes les combinaisons (datasets × grilles)
liste_datasets = [('X (séparable)', X), ('X_ls (légèrement)', X_ls), ('X_ns (non séparable)', X_ns)]
liste_grilles  = [('Grille dense',  grid_dense), ('Grille moyenne', grid_medium), ('Grille sparse', grid_sparse)]

fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for i, (ds_name, ds) in enumerate(liste_datasets):
    for j, (gr_name, gr) in enumerate(liste_grilles):
        ax = axes[i][j]
        ax.scatter(gr[:, 0], gr[:, 1], s=1, color='lightgray')
        ax.scatter(ds[:50, 0], ds[:50, 1], color='blue', s=10, marker='o')
        ax.scatter(ds[50:, 0], ds[50:, 1], color='red',  s=10, marker='^')
        if i == 0:
            ax.set_title(gr_name, fontweight='bold')
        if j == 0:
            ax.set_ylabel(ds_name, fontweight='bold', fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
plt.suptitle("Combinaisons datasets × grilles de test", fontsize=14)
plt.tight_layout()
plt.show()

# ===========================================================
# IV. Architecture commune et fonctions de base du neurone
# ===========================================================

def initialize_weights(n_inputs):
    """Initialise w (vecteur n_inputs) et b (biais) avec de petites valeurs aléatoires (* 0.01)."""
    w = np.random.randn(n_inputs) * 0.01
    b = np.random.randn()         * 0.01
    return w, b

def forward(x, w, b):
    """Calcule la combinaison linéaire z = w·x + b (produit scalaire + biais)."""
    z = np.dot(w, x) + b
    return z

def activation(z, activation_function):
    """Applique la fonction d'activation fournie en paramètre."""
    return activation_function(z)

def update_weights(w, b, delta_w, delta_b, learning_rate):
    """
    Applique la descente de gradient :
      w ← w - η · delta_w
      b ← b - η · delta_b
    """
    w = w - learning_rate * delta_w
    b = b - learning_rate * delta_b
    return w, b

def predict(X, w, b, activation_function):
    """
    Prédit la sortie du neurone pour chaque point de X :
    1. Calcule z avec forward
    2. Applique la fonction d'activation
    3. Stocke la prédiction
    """
    y_hats = []
    for x in X:
        z     = forward(x, w, b)
        y_hat = activation(z, activation_function)
        y_hats.append(y_hat)
    return np.array(y_hats)

def compute_loss(y_true, y_hat, model_type):
    """
    Calcule le coût selon le modèle :
    - perceptron : nombre total d'exemples mal classés
    - adaline    : MSE (moyenne des erreurs quadratiques)
    - logistic   : cross-entropy moyenne (avec clipping numérique eps=1e-10)
    """
    if model_type == 'perceptron':
        loss = np.sum(y_hat != y_true)

    elif model_type == 'adaline':
        loss = np.mean((y_true - y_hat) ** 2)

    elif model_type == 'logistic':
        eps           = 1e-10
        y_hat_clipped = np.clip(y_hat, eps, 1 - eps)
        loss = -np.mean(
            y_true * np.log(y_hat_clipped) +
            (1 - y_true) * np.log(1 - y_hat_clipped)
        )
    return loss

def plot_decision_boundary(X, y_true, w, b, activation_function, model_type, resolution=0.02):
    """
    Trace la frontière de décision d'un neurone simple sur un dataset 2D.
    Réutilise create_test_grid et predict.
    """
    xx, yy, grid_points = create_test_grid(X, resolution)
    Z = predict(grid_points, w, b, activation_function)

    if model_type == 'logistic':
        Z = np.where(Z >= 0.5, 1, 0)
    else:
        Z = np.where(Z >= 0, 1, -1)

    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    plt.scatter(X[:, 0], X[:, 1], c=y_true, cmap=plt.cm.coolwarm, edgecolors='k', s=50)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title(f'Frontière de décision ({model_type})')
    plt.show()

# ===========================================================
# V. Le Perceptron
# ===========================================================

def perceptron_activation(z):
    """
    Fonction seuil (signe) : retourne +1 si z >= 0, -1 sinon.
    ŷ ∈ {-1, +1}
    """
    if z >= 0:
        return 1
    else:
        return -1

def perceptron_delta(X, y_true, y_hat):
    """
    Calcule les deltas moyens uniquement sur les points mal classés du batch.
      δw  = -(y · x)  si mal classé, 0 sinon
      δw0 = -y         si mal classé, 0 sinon
    Retourne delta_w et delta_b.
    Fonctionne pour n'importe quelle taille de lot (1 exemple, mini-batch, dataset complet).
    """
    n_samples           = X.shape[0]
    delta_w_total       = np.zeros(X.shape[1])
    delta_b_total       = 0.0
    count_misclassified = 0

    for i in range(n_samples):
        if y_hat[i] != y_true[i]:
            delta_w_total       += -y_true[i] * X[i]
            delta_b_total       += -y_true[i]
            count_misclassified += 1

    if count_misclassified > 0:
        delta_w = delta_w_total / count_misclassified
        delta_b = delta_b_total / count_misclassified
    else:
        delta_w = np.zeros_like(delta_w_total)
        delta_b = 0.0
    return delta_w, delta_b

# --- Boucle d'apprentissage du Perceptron (mode batch — TP1 original) ---

# Labels : -1 pour G0, +1 pour G1
y_true_perc = np.array([-1] * len(G0) + [1] * len(G1))

w, b          = initialize_weights(n_inputs=2)
learning_rate = 0.01
n_epochs      = 50

w_history         = []
b_history         = []
loss_history_perc = []

for epoch in range(n_epochs):
    y_hat            = predict(X, w, b, perceptron_activation)
    delta_w, delta_b = perceptron_delta(X, y_true_perc, y_hat)
    w, b             = update_weights(w, b, delta_w, delta_b, learning_rate)
    w_history.append(w.copy())
    b_history.append(b)
    loss = compute_loss(y_true_perc, y_hat, model_type='perceptron')
    loss_history_perc.append(loss)
    print(f"Epoch {epoch+1:3d} - coût (mal classés) : {loss}")

# Évolution du coût
plt.plot(loss_history_perc)
plt.xlabel("Epoch")
plt.ylabel("Coût (nb mal classés)")
plt.title("Évolution du coût – Perceptron")
plt.show()

# --- Test du modèle sur les données de test (grille) ---
xx, yy, grid_points = create_test_grid(X, resolution=0.5)
grid_predictions    = predict(grid_points, w, b, perceptron_activation)

grid_class_neg = grid_points[grid_predictions == -1]
grid_class_pos = grid_points[grid_predictions ==  1]

plt.figure(figsize=(8, 6))
plt.scatter(grid_class_neg[:, 0], grid_class_neg[:, 1],
            color='lightblue', s=15, label='Grille (Prédit -1)')
plt.scatter(grid_class_pos[:, 0], grid_class_pos[:, 1],
            color='pink', s=15, label='Grille (Prédit +1)')
plt.scatter(X[y_true_perc == -1, 0], X[y_true_perc == -1, 1],
            color='blue', marker='o', edgecolors='k', s=50, label='Train -1')
plt.scatter(X[y_true_perc ==  1, 0], X[y_true_perc ==  1, 1],
            color='red',  marker='x', s=50, label='Train +1')
plt.xlabel("x1")
plt.ylabel("x2")
plt.title("Prédiction des points de test – Perceptron")
plt.legend()
plt.show()

# --- Analyse de la frontière de décision ---
plot_decision_boundary(X, y_true_perc, w, b, perceptron_activation, model_type='perceptron')
print(f"Poids finaux : w1={w[0]:.4f}, w2={w[1]:.4f}, w0={b:.4f}")

# --- Affichage dynamique de la frontière de décision (animation) ---

fig_anim, ax_anim = plt.subplots(figsize=(8, 6))
ax_anim.set_xlim(X[:, 0].min() - 1, X[:, 0].max() + 1)
ax_anim.set_ylim(X[:, 1].min() - 1, X[:, 1].max() + 1)
ax_anim.scatter(X[y_true_perc == -1, 0], X[y_true_perc == -1, 1],
                color='blue', label='Classe -1', edgecolor='k', marker='o')
ax_anim.scatter(X[y_true_perc ==  1, 0], X[y_true_perc ==  1, 1],
                color='red',  label='Classe +1', edgecolor='k', marker='D')
ax_anim.set_xlabel("x1")
ax_anim.set_ylabel("x2")
ax_anim.legend()

line, = ax_anim.plot([], [], 'k--', lw=2, label='Frontière apprentissage')

def init():
    line.set_data([], [])
    return line,

def update(epoch):
    x_vals = np.array([X[:, 0].min(), X[:, 0].max()])
    w2 = w_history[epoch][1]
    if abs(w2) > 1e-10:  # protection division par zéro si w2 ≈ 0
        y_vals = (-(w_history[epoch][0] / w2) * x_vals
                  -  (b_history[epoch]  / w2))
    else:
        y_vals = np.zeros_like(x_vals)
    line.set_data(x_vals, y_vals)
    ax_anim.set_title(f"Epoch {epoch + 1}")
    return line,

ani = animation.FuncAnimation(fig_anim, update, frames=len(w_history),
                               init_func=init, blit=True, interval=500)
plt.show()

# Export HTML (pour Jupyter Notebook)
from IPython.display import HTML
HTML(ani.to_jshtml())

# Export GIF
ani.save('perceptron_evolution.gif', writer='pillow')

# ===========================================================
# VI. L'ADALINE
# ===========================================================

def adaline_activation(z):
    """Fonction identité : ŷ = z (sortie réelle ∈ ℝ)."""
    return z

def adaline_delta(X, y_true, y_hat):
    """
    Calcule les deltas moyens sur le batch complet (tous les exemples) :
      δw  = (ŷ – y) · x   moyenné sur le batch
      δw0 = moyenne de (ŷ – y)
    Fonctionne pour n'importe quelle taille de lot.
    """
    errors  = y_hat - y_true
    delta_w = np.dot(errors, X) / X.shape[0]
    delta_b = np.mean(errors)
    return delta_w, delta_b

# Labels ADALINE : -1 pour G0, +1 pour G1
y_true_ada = np.array([-1] * len(G0) + [1] * len(G1))

w_ada, b_ada     = initialize_weights(n_inputs=2)
learning_rate    = 0.01
n_epochs         = 50
loss_history_ada = []

for epoch in range(n_epochs):
    y_hat_ada            = predict(X, w_ada, b_ada, adaline_activation)
    delta_w, delta_b     = adaline_delta(X, y_true_ada, y_hat_ada)
    w_ada, b_ada         = update_weights(w_ada, b_ada, delta_w, delta_b, learning_rate)
    loss = compute_loss(y_true_ada, y_hat_ada, model_type='adaline')
    loss_history_ada.append(loss)
    print(f"Epoch {epoch+1:3d} - coût MSE : {loss:.6f}")

plt.plot(loss_history_ada)
plt.xlabel("Epoch")
plt.ylabel("MSE")
plt.title("Évolution du coût – ADALINE")
plt.show()

plot_decision_boundary(X, y_true_ada, w_ada, b_ada, adaline_activation, model_type='adaline')

# ===========================================================
# VII. Le neurone logistique (régression logistique)
# ===========================================================

def logistic_activation(z):
    """Fonction sigmoïde : ŷ = 1 / (1 + exp(-z))  →  ŷ ∈ [0, 1]."""
    return 1.0 / (1.0 + np.exp(-z))

def logistic_delta(X, y_true, y_hat):
    """
    Calcule les deltas moyens sur le batch complet :
      δw  = (ŷ – y) · x   (gradient de la cross-entropy + sigmoïde simplifié)
      δw0 = moyenne de (ŷ – y)
    Fonctionne pour n'importe quelle taille de lot.
    """
    errors  = y_hat - y_true
    delta_w = np.dot(errors, X) / X.shape[0]
    delta_b = np.mean(errors)
    return delta_w, delta_b

# Labels logistique : 0 pour G0, 1 pour G1
y_true_log = np.array([0] * len(G0) + [1] * len(G1))

w_log, b_log     = initialize_weights(n_inputs=2)
learning_rate    = 0.01
n_epochs         = 50
loss_history_log = []

for epoch in range(n_epochs):
    y_hat_log            = predict(X, w_log, b_log, logistic_activation)
    delta_w, delta_b     = logistic_delta(X, y_true_log, y_hat_log)
    w_log, b_log         = update_weights(w_log, b_log, delta_w, delta_b, learning_rate)
    loss = compute_loss(y_true_log, y_hat_log, model_type='logistic')
    loss_history_log.append(loss)
    print(f"Epoch {epoch+1:3d} - cross-entropy : {loss:.6f}")

plt.plot(loss_history_log)
plt.xlabel("Epoch")
plt.ylabel("Cross-entropy")
plt.title("Évolution du coût – Neurone Logistique")
plt.show()

plot_decision_boundary(X, y_true_log, w_log, b_log, logistic_activation, model_type='logistic')

# ===========================================================
# VIII. AJOUT SGD — Fonction d'entraînement générique
#       Supporte trois modes : 'batch', 'sgd', 'mini-batch'
# ===========================================================

def train_model(X, y_true, w, b, delta_fn, act_fn,
                learning_rate, n_epochs, model_type,
                mode='batch', batch_size=16):
    """
    Entraîne un neurone selon le mode d'optimisation choisi.

    Paramètres
    ----------
    X, y_true     : données d'apprentissage
    w, b          : poids et biais initiaux (non modifiés en place)
    delta_fn      : fonction de gradient spécifique au modèle
                    (perceptron_delta / adaline_delta / logistic_delta)
    act_fn        : fonction d'activation du modèle
    learning_rate : taux d'apprentissage η
    n_epochs      : nombre d'époques
    model_type    : 'perceptron', 'adaline' ou 'logistic'
    mode          : 'batch'      → un gradient sur tout le dataset par époque
                    'sgd'        → un gradient par exemple individuel
                    'mini-batch' → un gradient par lot de batch_size exemples
    batch_size    : taille du mini-lot (ignoré si mode != 'mini-batch')

    Retourne
    --------
    w, b          : poids et biais après entraînement
    loss_history  : liste des coûts mesurés à la fin de chaque époque
    """
    loss_history = []
    n = len(X)

    for epoch in range(n_epochs):

        # -------------------------------------------------------
        # MODE BATCH (identique aux boucles TP1)
        # Un seul calcul de gradient sur l'intégralité du dataset,
        # suivi d'une seule mise à jour des poids.
        # -------------------------------------------------------
        if mode == 'batch':
            y_hat            = predict(X, w, b, act_fn)
            delta_w, delta_b = delta_fn(X, y_true, y_hat)
            w, b             = update_weights(w, b, delta_w, delta_b, learning_rate)

        # -------------------------------------------------------
        # MODE SGD
        # Les exemples sont mélangés aléatoirement à chaque époque
        # pour éviter les biais liés à l'ordre. Après chaque exemple
        # individuel, les poids sont mis à jour immédiatement.
        # -------------------------------------------------------
        elif mode == 'sgd':
            indices = np.random.permutation(n)
            for i in indices:
                xi    = X[i:i+1]        # tableau (1, n_features)
                yi    = y_true[i:i+1]   # tableau (1,)
                y_hat = predict(xi, w, b, act_fn)
                delta_w, delta_b = delta_fn(xi, yi, y_hat)
                w, b = update_weights(w, b, delta_w, delta_b, learning_rate)

        # -------------------------------------------------------
        # MODE MINI-BATCH
        # Les exemples sont mélangés, puis découpés en lots de
        # taille batch_size. Le gradient est moyenné sur chaque lot
        # avant la mise à jour. Compromis entre batch et SGD.
        # -------------------------------------------------------
        elif mode == 'mini-batch':
            indices = np.random.permutation(n)
            for start in range(0, n, batch_size):
                idx     = indices[start : start + batch_size]
                X_lot   = X[idx]
                y_lot   = y_true[idx]
                y_hat   = predict(X_lot, w, b, act_fn)
                delta_w, delta_b = delta_fn(X_lot, y_lot, y_hat)
                w, b = update_weights(w, b, delta_w, delta_b, learning_rate)

        # Coût mesuré sur le dataset complet à la fin de l'époque
        y_hat_full = predict(X, w, b, act_fn)
        loss_history.append(compute_loss(y_true, y_hat_full, model_type))

    return w, b, loss_history

# ===========================================================
# IX. Comparaison batch / SGD / mini-batch sur les 3 modèles
# ===========================================================

LR         = 0.01
N_EPOCHS   = 100
BATCH_SIZE = 16
MODES      = ['batch', 'sgd', 'mini-batch']
COULEURS   = {'batch': 'blue', 'sgd': 'orange', 'mini-batch': 'green'}

# ----------------------------------------------------------
# 9.1  PERCEPTRON
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("COMPARAISON DES MODES — PERCEPTRON")
print("=" * 60)

resultats_perc = {}
for mode in MODES:
    np.random.seed(0)
    w0, b0 = initialize_weights(2)
    wf, bf, hist = train_model(
        X, y_true_perc, w0, b0,
        perceptron_delta, perceptron_activation,
        LR, N_EPOCHS, 'perceptron',
        mode=mode, batch_size=BATCH_SIZE
    )
    resultats_perc[mode] = (wf, bf, hist)
    print(f"  [{mode:10s}]  coût final = {hist[-1]:5.1f}  "
          f"w1={wf[0]:.3f}  w2={wf[1]:.3f}  b={bf:.3f}")

# Courbes de coût
plt.figure(figsize=(8, 4))
for mode, (_, _, hist) in resultats_perc.items():
    plt.plot(hist, label=mode, color=COULEURS[mode])
plt.xlabel("Époque")
plt.ylabel("Coût (nb mal classés)")
plt.title("Perceptron — Coût selon le mode d'optimisation")
plt.legend()
plt.tight_layout()
plt.show()

# Frontières de décision côte à côte
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, mode in zip(axes, MODES):
    wf, bf, _ = resultats_perc[mode]
    plt.sca(ax)
    xx_g, yy_g, gp = create_test_grid(X, resolution=0.1)
    Z = predict(gp, wf, bf, perceptron_activation)
    Z = np.where(Z >= 0, 1, -1).reshape(xx_g.shape)
    ax.contourf(xx_g, yy_g, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    ax.scatter(X[:, 0], X[:, 1], c=y_true_perc, cmap=plt.cm.coolwarm,
               edgecolors='k', s=30)
    ax.set_title(f"Perceptron – {mode}")
    ax.set_xlabel("x1"); ax.set_ylabel("x2")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 9.2  ADALINE
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("COMPARAISON DES MODES — ADALINE")
print("=" * 60)

resultats_ada = {}
for mode in MODES:
    np.random.seed(0)
    w0, b0 = initialize_weights(2)
    wf, bf, hist = train_model(
        X, y_true_ada, w0, b0,
        adaline_delta, adaline_activation,
        LR, N_EPOCHS, 'adaline',
        mode=mode, batch_size=BATCH_SIZE
    )
    resultats_ada[mode] = (wf, bf, hist)
    print(f"  [{mode:10s}]  MSE finale = {hist[-1]:.6f}  "
          f"w1={wf[0]:.3f}  w2={wf[1]:.3f}  b={bf:.3f}")

plt.figure(figsize=(8, 4))
for mode, (_, _, hist) in resultats_ada.items():
    plt.plot(hist, label=mode, color=COULEURS[mode])
plt.xlabel("Époque")
plt.ylabel("MSE")
plt.title("ADALINE — Coût selon le mode d'optimisation")
plt.legend()
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, mode in zip(axes, MODES):
    wf, bf, _ = resultats_ada[mode]
    plt.sca(ax)
    xx_g, yy_g, gp = create_test_grid(X, resolution=0.1)
    Z = predict(gp, wf, bf, adaline_activation)
    Z = np.where(Z >= 0, 1, -1).reshape(xx_g.shape)
    ax.contourf(xx_g, yy_g, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    ax.scatter(X[:, 0], X[:, 1], c=y_true_ada, cmap=plt.cm.coolwarm,
               edgecolors='k', s=30)
    ax.set_title(f"ADALINE – {mode}")
    ax.set_xlabel("x1"); ax.set_ylabel("x2")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 9.3  NEURONE LOGISTIQUE
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("COMPARAISON DES MODES — NEURONE LOGISTIQUE")
print("=" * 60)

resultats_log = {}
for mode in MODES:
    np.random.seed(0)
    w0, b0 = initialize_weights(2)
    wf, bf, hist = train_model(
        X, y_true_log, w0, b0,
        logistic_delta, logistic_activation,
        LR, N_EPOCHS, 'logistic',
        mode=mode, batch_size=BATCH_SIZE
    )
    resultats_log[mode] = (wf, bf, hist)
    print(f"  [{mode:10s}]  cross-entropy finale = {hist[-1]:.6f}  "
          f"w1={wf[0]:.3f}  w2={wf[1]:.3f}  b={bf:.3f}")

plt.figure(figsize=(8, 4))
for mode, (_, _, hist) in resultats_log.items():
    plt.plot(hist, label=mode, color=COULEURS[mode])
plt.xlabel("Époque")
plt.ylabel("Cross-entropy")
plt.title("Neurone logistique — Coût selon le mode d'optimisation")
plt.legend()
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, mode in zip(axes, MODES):
    wf, bf, _ = resultats_log[mode]
    plt.sca(ax)
    xx_g, yy_g, gp = create_test_grid(X, resolution=0.1)
    Z = predict(gp, wf, bf, logistic_activation)
    Z = np.where(Z >= 0.5, 1, 0).reshape(xx_g.shape)
    ax.contourf(xx_g, yy_g, Z, alpha=0.3, cmap=plt.cm.coolwarm)
    ax.scatter(X[:, 0], X[:, 1], c=y_true_log, cmap=plt.cm.coolwarm,
               edgecolors='k', s=30)
    ax.set_title(f"Logistique – {mode}")
    ax.set_xlabel("x1"); ax.set_ylabel("x2")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 9.4  Figure récapitulative 3×3 : tous les modèles × tous les modes
# ----------------------------------------------------------
configs = [
    ('Perceptron', y_true_perc, resultats_perc, perceptron_activation, 'perceptron'),
    ('ADALINE',    y_true_ada,  resultats_ada,  adaline_activation,    'adaline'),
    ('Logistique', y_true_log,  resultats_log,  logistic_activation,   'logistic'),
]

fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for row, (nom, y_t, res, act_fn, mtype) in enumerate(configs):
    for col, mode in enumerate(MODES):
        wf, bf, _ = res[mode]
        ax = axes[row][col]
        xx_g, yy_g, gp = create_test_grid(X, resolution=0.1)
        Z = predict(gp, wf, bf, act_fn)
        if mtype == 'logistic':
            Z = np.where(Z >= 0.5, 1, 0)
        else:
            Z = np.where(Z >= 0, 1, -1)
        Z = Z.reshape(xx_g.shape)
        ax.contourf(xx_g, yy_g, Z, alpha=0.3, cmap=plt.cm.coolwarm)
        ax.scatter(X[:, 0], X[:, 1], c=y_t, cmap=plt.cm.coolwarm,
                   edgecolors='k', s=20)
        if row == 0:
            ax.set_title(mode, fontweight='bold', fontsize=11)
        if col == 0:
            ax.set_ylabel(nom, fontweight='bold', fontsize=11)
        ax.set_xlabel("x1")

plt.suptitle("Frontières de décision – 3 modèles × 3 modes d'optimisation", fontsize=13)
plt.tight_layout()
plt.show()
