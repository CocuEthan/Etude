# =============================================================================
# Devoir 1 – INFO0804
# Classification binaire sur la base « diabetes »
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
import timeit
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
from sklearn.model_selection import train_test_split
from sklearn import metrics
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import initializers
from tensorflow.keras.callbacks import ModelCheckpoint

# -----------------------------------------------------------------------------
# Chargement de la base de données
# -----------------------------------------------------------------------------
dataset = np.loadtxt(os.path.join(_DIR, '../tp2/pima-indians-diabetes.data.csv'), delimiter=',')
X = dataset[:, 0:8]
Y = dataset[:, 8]

seed = 5

# Fonction utilitaire : construit et compile un nouveau modèle (poids fixés)
def build_model():
    initializer = initializers.GlorotUniform(seed=seed)
    model = Sequential()
    model.add(Dense(12, input_shape=(8,), kernel_initializer=initializer, activation='relu'))
    model.add(Dense(8,  kernel_initializer=initializer, activation='relu'))
    model.add(Dense(1,  kernel_initializer=initializer, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


# =============================================================================
# PARTIE I – Influence de la taille de l'ensemble d'apprentissage
# Qst : Tester différentes divisions (10/90, 20/80, 30/70, 50/50, 70/30,
#        80/20, 90/10) avec epochs=500 et batch_size=10.
#        Afficher les courbes d'erreurs et remplir le tableau de résultats.
# =============================================================================

test_sizes = [0.90, 0.80, 0.70, 0.50, 0.30, 0.20, 0.10]

print("=" * 60)
print("PARTIE I – Influence de la taille d'apprentissage")
print("=" * 60)
print(f"{'Test%':>6} {'Train%':>7} {'Tr_Loss':>9} {'Tr_Acc':>8} {'Val_Loss':>10} {'Val_Acc':>9}")

for test_size in test_sizes:
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=test_size, random_state=seed
    )
    model = build_model()
    class_model = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=500,
        batch_size=10,
        verbose=0
    )

    # Résultats finaux (dernière epoch)
    tr_loss  = class_model.history['loss'][-1]
    tr_acc   = class_model.history['accuracy'][-1]
    val_loss = class_model.history['val_loss'][-1]
    val_acc  = class_model.history['val_accuracy'][-1]

    print(f"{int(test_size*100):>5}% {int((1-test_size)*100):>6}%"
          f" {tr_loss:>10.4f} {tr_acc:>8.4f} {val_loss:>10.4f} {val_acc:>9.4f}")

    # Courbe d'apprentissage pour chaque partage
    fig_loss = plt.figure(figsize=(8, 8))
    plt.title(f"Courbe d'apprentissage – Test {int(test_size*100)}% / Train {int((1-test_size)*100)}%")
    plt.plot(class_model.history['loss'],     label='train_loss')
    plt.plot(class_model.history['val_loss'], label='val_loss')
    plt.plot(
        np.argmin(class_model.history['val_loss']),
        np.min(class_model.history['val_loss']),
        marker='x', color='r', label='meilleur modèle'
    )
    plt.xlabel('Epochs')
    plt.ylabel('loss')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'courbe_partieI_test{int(test_size*100)}.png')
    plt.close()


# =============================================================================
# PARTIE II – Apprentissage / Sur-apprentissage
# Qst 1 : Que remarquez-vous pour un partage 30% test, epoch=500, batch_size=10 ?
# Qst 2 : Quel est l'option qui permet de retourner le meilleur modèle (croix rouge) ?
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE II – Apprentissage / Sur-apprentissage (30% test)")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

# Code pour retourner le meilleur modèle :
# L'option est le callback ModelCheckpoint avec save_best_only=True
# Il surveille la val_loss et sauvegarde uniquement le modèle avec la val_loss minimale.
checkpoint = ModelCheckpoint(
    'meilleur_modele.keras',
    monitor='val_loss',
    save_best_only=True,
    verbose=0
)

model_II = build_model()
class_model_II = model_II.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=500,
    batch_size=10,
    callbacks=[checkpoint],
    verbose=0
)

fig_loss = plt.figure(figsize=(8, 8))
plt.title("Partie II – Courbe d'apprentissage (30/70)")
plt.plot(class_model_II.history['loss'],     label='train_loss')
plt.plot(class_model_II.history['val_loss'], label='val_loss')
plt.plot(
    np.argmin(class_model_II.history['val_loss']),
    np.min(class_model_II.history['val_loss']),
    marker='x', color='r', label='meilleur modèle'
)
plt.xlabel('Epochs')
plt.ylabel('loss')
plt.legend()
plt.tight_layout()
plt.savefig('courbe_partieII.png')
plt.close()

best_epoch = np.argmin(class_model_II.history['val_loss'])
print(f"Meilleur modèle à l'epoch {best_epoch} "
      f"(val_loss = {class_model_II.history['val_loss'][best_epoch]:.4f})")


# =============================================================================
# PARTIE III – Influence du nombre d'epochs sur les performances
# Qst : Tester epochs = 10, 50, 100, 200, 250, 300, 350, 400, 500
#        avec 30% test et batch_size=10.
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE III – Influence du nombre d'epochs")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

epochs_list = [10, 50, 100, 200, 250, 300, 350, 400, 500]
print(f"{'Epochs':>7} {'Tr_Loss':>9} {'Tr_Acc':>8} {'Val_Loss':>10} {'Val_Acc':>9}")

for nb_epochs in epochs_list:
    model = build_model()
    hist = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=nb_epochs,
        batch_size=10,
        verbose=0
    )
    tr_loss  = hist.history['loss'][-1]
    tr_acc   = hist.history['accuracy'][-1]
    val_loss = hist.history['val_loss'][-1]
    val_acc  = hist.history['val_accuracy'][-1]
    print(f"{nb_epochs:>7} {tr_loss:>10.4f} {tr_acc:>8.4f} {val_loss:>10.4f} {val_acc:>9.4f}")


# =============================================================================
# PARTIE IV – Influence de la taille du batch sur le temps d'exécution
# Qst 1 : 537/537 représente le numéro du batch courant / nombre total de batchs
#          par epoch. Avec N=537 exemples et batch_size=1 : ceil(537/1) = 537 batchs.
# Qst 2 : Formule : nb_batchs = ceil(N / K)  avec N=taille base, K=taille batch
#          Tableau :
#            batch=1   → 537/537
#            batch=2   → 269/269
#            batch=10  → 54/54
#            batch=16  → 34/34
#            batch=32  → 17/17
#            batch=64  → 9/9
#            batch=128 → 5/5
#            Max (=N)  → 1/1
# Qst 3 : La valeur Max possible est N (=537 pour l'ensemble d'apprentissage
#          avec 30% de test sur 768 exemples), car un seul batch contient
#          tous les exemples → 1 mise à jour de poids par epoch (batch gradient).
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE IV – Influence de la taille du batch sur le temps d'exécution")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

N = len(X_train)   # 537 pour 70% de 768
Max = N            # valeur Max = taille totale de l'ensemble d'apprentissage

import math
print(f"Taille ensemble d'apprentissage N = {N}")
print(f"Valeur Max (batch_size) = {Max}")
print(f"\n{'batch_size':>12} {'nb_batchs':>12}")
for k in [1, 2, 10, 16, 32, 64, 128, Max]:
    print(f"{k:>12} {math.ceil(N/k):>12}")

# Mesure du temps d'exécution pour chaque taille de batch (epochs=50)
print("\nTemps d'exécution (epochs=50) :")
print(f"{'batch_size':>12} {'temps (s)':>12}")

for i in range(1, Max + 1, max(1, Max // 10)):   # sous-ensemble pour ne pas trop attendre
    model = build_model()
    t_start = timeit.default_timer()
    model.fit(X_train, y_train,
              validation_data=(X_test, y_test),
              epochs=50, batch_size=i, verbose=0)
    t_end = timeit.default_timer()
    print(f"{i:>12} {t_end - t_start:>12.3f}")

# Note : en Jupyter, utiliser la cellule suivante à la place :
# for i in range(1, Max):
#     %timeit -n1 -r1 model.fit(X_train, y_train,
#                                validation_data=(X_test, y_test),
#                                epochs=50, batch_size=i, verbose=0)


# =============================================================================
# PARTIE V – Influence de la taille du batch sur les performances
# Qst : Tester batch_size = 1, 2, 10, 16, 32, 64, 128, Max
#        avec 30% test et epochs=100.
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE V – Influence de la taille du batch sur les performances")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

batch_sizes = [1, 2, 10, 16, 32, 64, 128, N]
print(f"{'batch_size':>12} {'Tr_Loss':>9} {'Tr_Acc':>8} {'Val_Loss':>10} {'Val_Acc':>9}")

for bs in batch_sizes:
    model = build_model()
    hist = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=bs,
        verbose=0
    )
    tr_loss  = hist.history['loss'][-1]
    tr_acc   = hist.history['accuracy'][-1]
    val_loss = hist.history['val_loss'][-1]
    val_acc  = hist.history['val_accuracy'][-1]
    print(f"{bs:>12} {tr_loss:>10.4f} {tr_acc:>8.4f} {val_loss:>10.4f} {val_acc:>9.4f}")


# =============================================================================
# PARTIE VI – Utilisation de l'ensemble de validation
# Qst : Entraîner le modèle SANS validation_data, puis évaluer sur le test.
#        Comparer avec les résultats des parties précédentes.
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE VI – Sans ensemble de validation")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

# Entraînement sans ensemble de validation
model_VI = build_model()
class_model_VI = model_VI.fit(
    X_train, y_train,
    epochs=100,
    batch_size=10,
    verbose=1
)

# Évaluation – méthode 1 : model.evaluate
score = model_VI.evaluate(X_test, y_test, batch_size=10)
print(f"\nmodel.evaluate → loss={score[0]:.4f}, accuracy={score[1]:.4f}")

# Évaluation – méthode 2 : matrice de confusion (sklearn)
pred = (model_VI.predict(X_test) > 0.5).astype(int).flatten()
print("\nMatrice de confusion :")
print(metrics.confusion_matrix(y_test, pred))
print(f"Accuracy (sklearn) : {metrics.accuracy_score(y_test, pred):.4f}")


# =============================================================================
# PARTIE VII – Partage de la base en train / validation / test
# Qst 1 : Écrire un code pour partager la base en train/validation/test.
# Qst 2 : Entraîner et tester le modèle sur la base diabetes.
# =============================================================================

print("\n" + "=" * 60)
print("PARTIE VII – Partage train / validation / test")
print("=" * 60)

# Étape 1 : séparer 30% pour le test
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

# Étape 2 : séparer 15% de l'ensemble restant pour la validation
#           (≈ 10% de la base totale)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=0.15, random_state=seed
)

print(f"Train : {len(X_train)} | Validation : {len(X_val)} | Test : {len(X_test)}")

# Code pour retourner le meilleur modèle
checkpoint_VII = ModelCheckpoint(
    'meilleur_modele_VII.keras',
    monitor='val_loss',
    save_best_only=True,
    verbose=0
)

model_VII = build_model()
class_model_VII = model_VII.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=500,
    batch_size=10,
    callbacks=[checkpoint_VII],
    verbose=0
)

# Évaluation sur le test (modèle final)
score_VII = model_VII.evaluate(X_test, y_test, verbose=0)
print(f"\nPerformances sur le test (modèle final) :"
      f" loss={score_VII[0]:.4f}, accuracy={score_VII[1]:.4f}")

# Évaluation du meilleur modèle sauvegardé
from tensorflow.keras.models import load_model
best_model_VII = load_model('meilleur_modele_VII.keras')
score_best = best_model_VII.evaluate(X_test, y_test, verbose=0)
print(f"Performances sur le test (meilleur modèle) :"
      f" loss={score_best[0]:.4f}, accuracy={score_best[1]:.4f}")

# Courbe d'apprentissage
fig_loss = plt.figure(figsize=(8, 8))
plt.title("Partie VII – Courbe d'apprentissage (train/val/test)")
plt.plot(class_model_VII.history['loss'],     label='train_loss')
plt.plot(class_model_VII.history['val_loss'], label='val_loss')
plt.plot(
    np.argmin(class_model_VII.history['val_loss']),
    np.min(class_model_VII.history['val_loss']),
    marker='x', color='r', label='meilleur modèle'
)
plt.xlabel('Epochs')
plt.ylabel('loss')
plt.legend()
plt.tight_layout()
plt.savefig('courbe_partieVII.png')
plt.close()


# =============================================================================
# CHANGEMENT DU NOMBRE DE COUCHES
# Configuration : une couche cachée de 4 neurones
# =============================================================================

print("\n" + "=" * 60)
print("CHANGEMENT DU NOMBRE DE COUCHES – 1 couche cachée (4 neurones)")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.30, random_state=seed
)

initializer = initializers.GlorotUniform(seed=seed)
model_4 = Sequential()
model_4.add(Dense(4, input_shape=(8,), kernel_initializer=initializer, activation='relu'))
model_4.add(Dense(1, kernel_initializer=initializer, activation='sigmoid'))
model_4.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

hist_4 = model_4.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=500,
    batch_size=10,
    verbose=0
)

tr_loss  = hist_4.history['loss'][-1]
tr_acc   = hist_4.history['accuracy'][-1]
val_loss = hist_4.history['val_loss'][-1]
val_acc  = hist_4.history['val_accuracy'][-1]
print(f"Train  → loss={tr_loss:.4f}, accuracy={tr_acc:.4f}")
print(f"Test   → loss={val_loss:.4f}, accuracy={val_acc:.4f}")
