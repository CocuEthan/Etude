# Récapitulatif – TP1 bis : Optimisation par SGD / Mini-batch / Batch

## Objectif

Modifier les sources du TP1 (Perceptron, ADALINE, Neurone logistique) pour implémenter
et **comparer trois modes d'optimisation** :

| Mode | Nom complet | Mise à jour des poids |
|------|-------------|----------------------|
| `batch` | Descente de gradient par lot complet | Une fois par époque, sur **tout** le dataset |
| `sgd` | Descente de gradient stochastique | Après **chaque exemple** individuel |
| `mini-batch` | Descente de gradient par mini-lot | Après chaque **sous-ensemble** de `batch_size` exemples |

---

## Structure du fichier `tp1_sgd.py`

```
tp1bis/
└── tp1_sgd.py        ← code source modifié
└── RECAPITULATIF.md  ← ce fichier
```

---

## Modifications apportées par rapport au TP1

### 1. Fonctions inchangées

Les fonctions suivantes sont **identiques** au TP1 :

- `create_test_grid` — construction de la grille de test
- `initialize_weights` — initialisation des poids
- `forward` — combinaison linéaire z = w·x + b
- `update_weights` — règle de mise à jour w ← w – η·δ
- `predict` — prédiction sur un ensemble de points
- `compute_loss` — calcul du coût (nb erreurs / MSE / cross-entropy)
- `plot_decision_boundary` — visualisation de la frontière de décision
- `perceptron_activation` / `adaline_activation` / `logistic_activation`

### 2. Fonctions de gradient légèrement adaptées

Les fonctions `perceptron_delta`, `adaline_delta`, `logistic_delta` fonctionnent
désormais pour **n'importe quelle taille de lot** (1 exemple, un mini-lot, ou
le dataset complet) :

```python
# Exemple : adaline_delta reçoit un lot X_batch de taille quelconque
def adaline_delta(X_batch, y_batch, y_hat_batch):
    err = y_hat_batch - y_batch
    return np.dot(err, X_batch) / len(X_batch), np.mean(err)
```

La division par `len(X_batch)` assure que le gradient est toujours **moyenné**
sur la taille réelle du lot passé, quelle qu'elle soit.

### 3. Nouvelle fonction `train_model` — AJOUT PRINCIPAL

C'est la modification centrale. Elle remplace les boucles d'apprentissage
spécifiques à chaque modèle par **une seule fonction générique** paramétrée
par le mode d'optimisation.

```python
def train_model(X, y_true, w, b, delta_fn, act_fn,
                learning_rate, n_epochs, model_type,
                mode='batch', batch_size=16):
```

#### Mode `batch` (original TP1)

```
Pour chaque époque :
    y_hat    ← predict(X_entier, w, b)       # tout le dataset
    δw, δb   ← delta_fn(X_entier, y, y_hat)  # gradient global
    w, b     ← update_weights(w, b, δw, δb)  # une seule mise à jour
```

**Comportement** : convergence lisse mais lente ; gradient calculé sur
toutes les données → estimation précise mais coûteuse.

#### Mode `sgd`

```
Pour chaque époque :
    Mélanger aléatoirement les indices (np.random.permutation)
    Pour chaque exemple i :
        y_hat_i  ← predict(X[i:i+1], w, b)        # un seul exemple
        δw, δb   ← delta_fn(X[i:i+1], y[i], y_hat_i)
        w, b     ← update_weights(w, b, δw, δb)    # mise à jour immédiate
```

**Comportement** : convergence rapide en début d'entraînement, mais
**oscillations** autour du minimum car chaque exemple donne un gradient
bruité. Le mélange aléatoire évite les biais dus à l'ordre des données.

#### Mode `mini-batch`

```
Pour chaque époque :
    Mélanger aléatoirement les indices
    Pour chaque lot de taille batch_size :
        y_hat_b  ← predict(X_lot, w, b)
        δw, δb   ← delta_fn(X_lot, y_lot, y_hat_b)
        w, b     ← update_weights(w, b, δw, δb)
```

**Comportement** : compromis entre batch et SGD. Moins bruité que SGD,
plus rapide que batch. En pratique c'est le mode le plus utilisé dans les
réseaux profonds (taille typique : 16, 32, 64, 128).

---

## Différences mathématiques entre les modes

### Gradient exact (batch)

Pour ADALINE, sur N exemples :

```
∂L/∂w = (1/N) · Σ (ŷᵢ – yᵢ) · xᵢ
```

### Gradient stochastique (SGD)

Pour un seul exemple i :

```
∂L/∂w ≈ (ŷᵢ – yᵢ) · xᵢ
```

C'est une **approximation bruitée** du gradient exact, mais elle peut
permettre de sortir de minima locaux peu profonds.

### Gradient mini-batch (taille B)

```
∂L/∂w ≈ (1/B) · Σ_{i∈lot} (ŷᵢ – yᵢ) · xᵢ
```

L'espérance est la même que le gradient batch, mais la variance diminue
avec B.

---

## Tableau comparatif des trois modes

| Critère | Batch | SGD | Mini-batch |
|---------|-------|-----|------------|
| Nb de mises à jour / époque | 1 | N (nb exemples) | N / batch_size |
| Bruit du gradient | Faible | Élevé | Modéré |
| Vitesse de convergence | Lente | Rapide au début | Équilibrée |
| Stabilité de la courbe de coût | Lisse | Oscillante | Légèrement oscillante |
| Mémoire requise | Tout le dataset | 1 exemple | batch_size exemples |
| Usage typique | Petits datasets | Streaming, grands datasets | Réseaux profonds |

---

## Ce que montre l'expérience (résultats observables)

### Perceptron

- Les **trois modes convergent** vers la même frontière sur données
  linéairement séparables (même minimum global).
- En mode **SGD**, le coût peut remonter provisoirement entre deux
  exemples (oscillations), mais la frontière finale est équivalente.
- Le mode **batch** donne la courbe la plus régulière.

### ADALINE

- La fonction MSE est **convexe** → un minimum global unique.
- Le mode **SGD** converge plus vite en nombre d'époques, mais chaque
  époque fait N mises à jour (coût de calcul plus élevé).
- Le mode **mini-batch** offre le meilleur compromis vitesse / stabilité.

### Neurone logistique

- Même constat qu'ADALINE (gradient identique après simplification).
- La **cross-entropy** est également convexe pour un modèle linéaire.
- Le mode SGD peut faire baisser la cross-entropy plus vite
  (convergence rapide en début d'entraînement).

---

## Paramètres modifiables

| Paramètre | Valeur par défaut | Effet |
|-----------|-------------------|-------|
| `learning_rate` | 0.01 | Trop grand → divergence ; trop petit → lent |
| `n_epochs` | 100 | Plus d'époques → meilleure convergence |
| `batch_size` | 16 | Augmenter → moins de bruit, plus de mémoire |
| `mode` | `'batch'` | Choisir parmi `'batch'`, `'sgd'`, `'mini-batch'` |

---

## Exemple d'utilisation de `train_model`

```python
# Initialisation des poids
w, b = initialize_weights(n_inputs=2)

# Entraînement ADALINE en mini-batch
w_final, b_final, loss_history = train_model(
    X, y_true_ada, w, b,
    delta_fn      = adaline_delta,
    act_fn        = adaline_activation,
    learning_rate = 0.01,
    n_epochs      = 100,
    model_type    = 'adaline',
    mode          = 'mini-batch',
    batch_size    = 16
)

# Visualisation de la frontière
plot_decision_boundary(X, y_true_ada, w_final, b_final,
                       adaline_activation, 'adaline')
```

---

## Résumé des fichiers

| Fichier | Description |
|---------|-------------|
| `tp1/tp1.py` | TP1 original (descente de gradient batch) |
| `tp1bis/tp1_sgd.py` | TP1 modifié avec SGD / mini-batch / batch |
| `tp1bis/RECAPITULATIF.md` | Ce document explicatif |
