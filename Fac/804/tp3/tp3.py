import os
import warnings
import logging

# Suppression des warnings TensorFlow et autres
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

_DIR = os.path.dirname(os.path.abspath(__file__))
import numpy
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.constraints import MaxNorm
from sklearn.model_selection import train_test_split
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV

# ============================================================
# Chargement de la base diabetes
# ============================================================
seed = 7
numpy.random.seed(seed)
dataset = numpy.loadtxt(os.path.join(_DIR, 'pima-indians-diabetes.data.csv'), delimiter=',')
X = dataset[:, 0:8]
Y = dataset[:, 8]

# ============================================================
# Méthode 1 : train_test_split (67% train, 33% test)
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=seed)

# Utilisation de Input(shape=...) comme première couche pour éviter le warning input_shape
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=150, batch_size=10)

# ============================================================
# Méthode 2 : validation_split
# ============================================================
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, Y, validation_split=0.33, epochs=150, batch_size=10)

# ============================================================
# Méthode 3 : K-Fold Cross Validation (10 folds)
# ============================================================
def create_model_diabetes():
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_diabetes, epochs=150, batch_size=10, verbose=0)
kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
results = cross_val_score(model, X, Y, cv=kfold)
print(f"Diabetes - K-Fold CV: {results.mean():.4f} (+/- {results.std():.4f})")

# ============================================================
# Exercice 1 : Trois méthodes de partitionnement sur la base seeds
#              (classification multi-classes : 3 variétés de blé)
# ============================================================

# Chargement de la base seeds (7 features, classes 1/2/3 → converties en 0/1/2)
seeds_data = numpy.loadtxt(os.path.join(_DIR, 'seeds', 'seeds_dataset.txt'))
X_seeds = seeds_data[:, 0:7]
Y_seeds = seeds_data[:, 7] - 1  # classes 1,2,3 → 0,1,2

# --- Seeds Méthode 1 : train_test_split ---
X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(
    X_seeds, Y_seeds, test_size=0.33, random_state=seed)

model_s = Sequential([
    Input(shape=(7,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(3, activation='softmax')  # 3 classes → softmax + sparse_categorical_crossentropy
])
model_s.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model_s.fit(X_s_train, y_s_train, validation_data=(X_s_test, y_s_test), epochs=150, batch_size=10)

# --- Seeds Méthode 2 : validation_split ---
model_s = Sequential([
    Input(shape=(7,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(3, activation='softmax')
])
model_s.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model_s.fit(X_seeds, Y_seeds, validation_split=0.33, epochs=150, batch_size=10)

# --- Seeds Méthode 3 : K-Fold Cross Validation ---
def create_model_seeds():
    m = Sequential([
        Input(shape=(7,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(3, activation='softmax')
    ])
    m.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model_s = KerasClassifier(model=create_model_seeds, epochs=150, batch_size=10, verbose=0)
kfold_s = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
results_s = cross_val_score(model_s, X_seeds, Y_seeds, cv=kfold_s)
print(f"Seeds - K-Fold CV: {results_s.mean():.4f} (+/- {results_s.std():.4f})")

# ============================================================
# Partie 2 : GridSearchCV - Optimisation des hyperparamètres (diabetes)
# IMPORTANT : n_jobs=1 pour éviter les crashs/blocages sur Windows avec TensorFlow
# n_jobs=-1 lance trop de processus TF en parallèle → crash mémoire
# ============================================================

dataset = numpy.loadtxt(os.path.join(_DIR, 'pima-indians-diabetes.data.csv'), delimiter=',')
X = dataset[:, 0:8]
Y = dataset[:, 8]

# --- 3. Nombre de neurones dans la couche cachée ---
def create_model_neurons(neurons=12):
    m = Sequential([
        Input(shape=(8,)),
        Dense(neurons, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_neurons, epochs=150, batch_size=10, verbose=0)
param_grid = dict(model__neurons=[1, 5, 15, 25, 30])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- 1. Méthode d'initialisation des poids du réseau ---
def create_model_init(init_mode='uniform'):
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, kernel_initializer=init_mode, activation='relu'),
        Dense(8, kernel_initializer=init_mode, activation='relu'),
        Dense(1, kernel_initializer=init_mode, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_init, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__init_mode=['uniform', 'normal', 'zero'])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- 2. Fonctions d'activation ---
def create_model_activation(activation='relu'):
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, activation=activation),
        Dense(8, activation=activation),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_activation, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__activation=['relu', 'tanh', 'sigmoid', 'linear'])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- 4. Algorithme d'optimisation pour le gradient stochastique ---
def create_model_optimizer(optimizer='adam'):
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_optimizer, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__optimizer=['SGD', 'RMSprop', 'Adam'])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- 5. Taux d'apprentissage et Momentum (avec SGD) ---
# Le modèle ne compile PAS ici : scikeras gère le compilateur via les kwargs
def create_model_lr():
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    return m

model = KerasClassifier(model=create_model_lr, loss="binary_crossentropy",
                        optimizer="SGD", epochs=100, batch_size=10, verbose=0)
learn_rate = [0.01, 0.1, 0.2]
momentum = [0.0, 0.2, 0.4, 0.8]
param_grid = dict(optimizer__learning_rate=learn_rate, optimizer__momentum=momentum)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- 6. Taille du batch et nombre d'epochs ---
def create_model_batch():
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_batch, verbose=0)
param_grid = dict(batch_size=[20, 40, 60, 80], epochs=[10, 50, 100])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- Dropout et contrainte de poids ---
def create_model_dropout(dropout_rate=0.0, weight_constraint=1.0):
    m = Sequential([
        Input(shape=(8,)),
        Dense(12, kernel_initializer='uniform', activation='relu',
              kernel_constraint=MaxNorm(weight_constraint)),
        Dropout(dropout_rate),
        Dense(8, activation='relu', kernel_constraint=MaxNorm(weight_constraint)),
        Dropout(dropout_rate),
        Dense(1, activation='sigmoid')
    ])
    m.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model = KerasClassifier(model=create_model_dropout, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__dropout_rate=[0.0, 0.2, 0.4, 0.6, 0.8],
                  model__weight_constraint=[1.0, 2.0, 3.0])
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=3)
grid_result = grid.fit(X, Y)
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
for mean, stdev, param in zip(grid_result.cv_results_['mean_test_score'],
                               grid_result.cv_results_['std_test_score'],
                               grid_result.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# ============================================================
# Exercice 2 : Modèle final diabetes avec les paramètres optimaux
#              Remplacer les valeurs par celles obtenues dans les GridSearchCV ci-dessus
# ============================================================
# Exemple de paramètres optimaux (à adapter selon vos résultats) :
# - neurons = 25
# - init_mode = 'uniform'
# - activation = 'linear'
# - optimizer = 'Adam'
# - batch_size = 20, epochs = 100
# - dropout_rate = 0.2, weight_constraint = 2.0

best_model_diabetes = Sequential([
    Input(shape=(8,)),
    Dense(25, kernel_initializer='uniform', activation='linear',
          kernel_constraint=MaxNorm(2.0)),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
best_model_diabetes.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=seed)
best_model_diabetes.fit(X_train, y_train, validation_data=(X_test, y_test),
                        epochs=100, batch_size=20, verbose=1)
_, acc_diabetes = best_model_diabetes.evaluate(X_test, y_test, verbose=0)
print(f"Modèle final diabetes (paramètres optimaux) - Accuracy: {acc_diabetes:.4f}")

# ============================================================
# Exercice 3 : GridSearchCV sur la base seeds (multi-classes)
# ============================================================

seeds_data = numpy.loadtxt(os.path.join(_DIR, 'seeds', 'seeds_dataset.txt'))
X_seeds = seeds_data[:, 0:7]
Y_seeds = seeds_data[:, 7] - 1  # 1,2,3 → 0,1,2

# --- Seeds : Nombre de neurones ---
def create_model_seeds_neurons(neurons=12):
    m = Sequential([
        Input(shape=(7,)),
        Dense(neurons, activation='relu'),
        Dense(3, activation='softmax')
    ])
    m.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model_s = KerasClassifier(model=create_model_seeds_neurons, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__neurons=[1, 5, 15, 25, 30])
grid_s = GridSearchCV(estimator=model_s, param_grid=param_grid, n_jobs=1, cv=3)
grid_result_s = grid_s.fit(X_seeds, Y_seeds)
print("Seeds neurons - Best: %f using %s" % (grid_result_s.best_score_, grid_result_s.best_params_))
for mean, stdev, param in zip(grid_result_s.cv_results_['mean_test_score'],
                               grid_result_s.cv_results_['std_test_score'],
                               grid_result_s.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- Seeds : Fonction d'activation ---
def create_model_seeds_activation(activation='relu'):
    m = Sequential([
        Input(shape=(7,)),
        Dense(12, activation=activation),
        Dense(8, activation=activation),
        Dense(3, activation='softmax')
    ])
    m.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model_s = KerasClassifier(model=create_model_seeds_activation, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__activation=['relu', 'tanh', 'sigmoid', 'linear'])
grid_s = GridSearchCV(estimator=model_s, param_grid=param_grid, n_jobs=1, cv=3)
grid_result_s = grid_s.fit(X_seeds, Y_seeds)
print("Seeds activation - Best: %f using %s" % (grid_result_s.best_score_, grid_result_s.best_params_))
for mean, stdev, param in zip(grid_result_s.cv_results_['mean_test_score'],
                               grid_result_s.cv_results_['std_test_score'],
                               grid_result_s.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- Seeds : Algorithme d'optimisation ---
def create_model_seeds_optimizer(optimizer='adam'):
    m = Sequential([
        Input(shape=(7,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(3, activation='softmax')
    ])
    m.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return m

model_s = KerasClassifier(model=create_model_seeds_optimizer, epochs=100, batch_size=10, verbose=0)
param_grid = dict(model__optimizer=['SGD', 'RMSprop', 'Adam'])
grid_s = GridSearchCV(estimator=model_s, param_grid=param_grid, n_jobs=1, cv=3)
grid_result_s = grid_s.fit(X_seeds, Y_seeds)
print("Seeds optimizer - Best: %f using %s" % (grid_result_s.best_score_, grid_result_s.best_params_))
for mean, stdev, param in zip(grid_result_s.cv_results_['mean_test_score'],
                               grid_result_s.cv_results_['std_test_score'],
                               grid_result_s.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# --- Seeds : Taille du batch et epochs ---
def create_model_seeds_batch():
    m = Sequential([
        Input(shape=(7,)),
        Dense(12, activation='relu'),
        Dense(8, activation='relu'),
        Dense(3, activation='softmax')
    ])
    m.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

model_s = KerasClassifier(model=create_model_seeds_batch, verbose=0)
param_grid = dict(batch_size=[10, 20, 40], epochs=[50, 100, 150])
grid_s = GridSearchCV(estimator=model_s, param_grid=param_grid, n_jobs=1, cv=3)
grid_result_s = grid_s.fit(X_seeds, Y_seeds)
print("Seeds batch/epochs - Best: %f using %s" % (grid_result_s.best_score_, grid_result_s.best_params_))
for mean, stdev, param in zip(grid_result_s.cv_results_['mean_test_score'],
                               grid_result_s.cv_results_['std_test_score'],
                               grid_result_s.cv_results_['params']):
    print("%f (%f) with: %r" % (mean, stdev, param))

# ============================================================
# Exercice 4 : Modèle final seeds avec les paramètres optimaux
#              Remplacer les valeurs par celles obtenues dans les GridSearchCV ci-dessus
# ============================================================

best_model_seeds = Sequential([
    Input(shape=(7,)),
    Dense(25, kernel_initializer='uniform', activation='relu'),
    Dense(8, activation='relu'),
    Dense(3, activation='softmax')
])
best_model_seeds.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(
    X_seeds, Y_seeds, test_size=0.33, random_state=seed)
best_model_seeds.fit(X_s_train, y_s_train, validation_data=(X_s_test, y_s_test),
                     epochs=100, batch_size=20, verbose=1)
_, acc_seeds = best_model_seeds.evaluate(X_s_test, y_s_test, verbose=0)
print(f"Modèle final seeds (paramètres optimaux) - Accuracy: {acc_seeds:.4f}")
