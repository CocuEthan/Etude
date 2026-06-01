import csv
import math
from random import random, seed, randrange
import numpy as np

# ===========================================================
# PERCEPTRON SIMPLE
# ===========================================================

# 1. Fonction de prédiction du perceptron simple
def predict(row, weights):
    """
    Calcule la valeur de sortie : 1.0 si la somme pondérée >= 0, sinon 0.0.
    weights[0] est le biais (w0), weights[i+1] est le poids de row[i].
    """
    activation = weights[0]
    for i in range(len(row) - 1):
        activation += weights[i + 1] * row[i]
    return 1.0 if activation >= 0.0 else 0.0

# 2. Apprentissage des poids par gradient stochastique
def train_weights(train, l_rate, n_epoch):
    """
    Estime les poids du perceptron par descente de gradient stochastique.
    Pour chaque exemple : erreur = y_true - y_pred, puis mise à jour des poids.
    """
    weights = [0.0 for i in range(len(train[0]))]
    for epoch in range(n_epoch):
        for row in train:
            prediction = predict(row, weights)
            error      = row[-1] - prediction
            weights[0] = weights[0] + l_rate * error
            for i in range(len(row) - 1):
                weights[i + 1] = weights[i + 1] + l_rate * error * row[i]
    return weights

# ===========================================================
# 3. Application sur la base Sonar (208 exemples, 60 variables, 2 classes)
# ===========================================================

# a) Charger la base à partir d'un fichier CSV
def load_csv(filename):
    dataset = list()
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if not row:
                continue
            dataset.append(row)
    return dataset

# b) Convertir les colonnes de string vers float
def str_column_to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())

# c) Convertir la colonne des classes (ex. 'M'/'R' → 0/1)
def str_column_to_int(dataset, column):
    class_values = [row[column] for row in dataset]
    unique       = set(class_values)
    lookup       = dict()
    for i, value in enumerate(unique):
        lookup[value] = i
    for row in dataset:
        row[column] = lookup[row[column]]
    return lookup

# Découpage aléatoire en k folds
def cross_validation_split(dataset, n_folds):
    dataset_split = list()
    dataset_copy  = list(dataset)
    fold_size     = int(len(dataset) / n_folds)
    for _ in range(n_folds):
        fold = list()
        while len(fold) < fold_size:
            index = randrange(len(dataset_copy))
            fold.append(dataset_copy.pop(index))
        dataset_split.append(fold)
    return dataset_split

# Métrique : précision (accuracy)
def accuracy_metric(actual, predicted):
    correct = sum(1 for a, p in zip(actual, predicted) if a == p)
    return correct / float(len(actual)) * 100.0

# d) Évaluer l'algorithme avec k-fold cross-validation
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
    folds  = cross_validation_split(dataset, n_folds)
    scores = list()
    for fold in folds:
        train_set = list(folds)
        train_set.remove(fold)
        train_set = sum(train_set, [])
        test_set  = list()
        for row in fold:
            row_copy = list(row)
            test_set.append(row_copy)
            row_copy[-1] = None
        predicted = algorithm(train_set, test_set, *args)
        actual    = [row[-1] for row in fold]
        accuracy  = accuracy_metric(actual, predicted)
        scores.append(accuracy)
    return scores

# e) Algorithme perceptron (réutilise predict et train_weights)
def perceptron(train, test, l_rate, n_epoch):
    predictions = list()
    weights     = train_weights(train, l_rate, n_epoch)
    for row in test:
        prediction = predict(row, weights)
        predictions.append(prediction)
    return predictions

# Chargement et préparation de la base Sonar
filename_sonar = 'connectionist+bench+sonar+mines+vs+rocks/sonar.all-data'
dataset_sonar  = load_csv(filename_sonar)
for i in range(len(dataset_sonar[0]) - 1):
    str_column_to_float(dataset_sonar, i)
str_column_to_int(dataset_sonar, len(dataset_sonar[0]) - 1)

seed(1)
scores_sonar = evaluate_algorithm(dataset_sonar, perceptron, 3, 0.01, 500)
print(f"[Sonar – Perceptron] Scores par fold : {scores_sonar}")
print(f"[Sonar – Perceptron] Précision moyenne : {sum(scores_sonar)/len(scores_sonar):.2f}%")

# ===========================================================
# PERCEPTRON MULTICOUCHES (MLP) — pur Python
# ===========================================================

# Calcul de la somme pondérée : activation = Σ(w_i * x_i) + biais
def activate(weights, inputs):
    activation = weights[-1]          # biais en dernière position
    for i in range(len(weights) - 1):
        activation += weights[i] * inputs[i]
    return activation

# Fonction d'activation sigmoïde
def transfer(activation):
    return 1.0 / (1.0 + math.exp(-activation))

# Dérivée de la sigmoïde : σ'(x) = σ(x) · (1 – σ(x))
def transfer_derivative(output):
    return output * (1.0 - output)

# 1. Initialisation aléatoire du réseau
def initialize_network(n_inputs, n_hidden, n_outputs):
    network      = list()
    hidden_layer = [{'weights': [random() for _ in range(n_inputs  + 1)]}
                    for _ in range(n_hidden)]
    network.append(hidden_layer)
    output_layer = [{'weights': [random() for _ in range(n_hidden + 1)]}
                    for _ in range(n_outputs)]
    network.append(output_layer)
    return network

# 2. Propagation avant
def forward_propagate(network, row):
    inputs = row
    for layer in network:
        new_inputs = []
        for neuron in layer:
            act            = activate(neuron['weights'], inputs)
            neuron['output'] = transfer(act)
            new_inputs.append(neuron['output'])
        inputs = new_inputs
    return inputs

# 3. Rétropropagation de l'erreur
def backward_propagate_error(network, expected):
    for i in reversed(range(len(network))):
        layer  = network[i]
        errors = list()
        if i != len(network) - 1:
            for j in range(len(layer)):
                error = 0.0
                for neuron in network[i + 1]:
                    error += neuron['weights'][j] * neuron['delta']
                errors.append(error)
        else:
            for j in range(len(layer)):
                neuron = layer[j]
                errors.append(neuron['output'] - expected[j])
        for j in range(len(layer)):
            neuron           = layer[j]
            neuron['delta']  = errors[j] * transfer_derivative(neuron['output'])

# Mise à jour des poids avec la règle : w ← w – η · δ · entrée
def update_weights_mlp(network, row, l_rate):
    for i, layer in enumerate(network):
        inputs = row[:-1] if i == 0 else [neuron['output'] for neuron in network[i - 1]]
        for neuron in layer:
            for j in range(len(inputs)):
                neuron['weights'][j] -= l_rate * neuron['delta'] * inputs[j]
            neuron['weights'][-1] -= l_rate * neuron['delta']     # biais

# 4. Entraînement du réseau
def train_network(network, train, l_rate, n_epoch, n_outputs):
    for epoch in range(n_epoch):
        for row in train:
            outputs  = forward_propagate(network, row)
            expected = [0] * n_outputs
            expected[row[-1]] = 1
            backward_propagate_error(network, expected)
            update_weights_mlp(network, row, l_rate)

# Prédiction avec le MLP (classe = indice de la sortie maximale)
def predict_mlp(network, row):
    outputs = forward_propagate(network, row)
    return outputs.index(max(outputs))

# Algorithme MLP encapsulé pour evaluate_algorithm
def back_propagation(train, test, l_rate, n_epoch, n_hidden):
    n_inputs  = len(train[0]) - 1
    n_outputs = len(set(row[-1] for row in train))
    network   = initialize_network(n_inputs, n_hidden, n_outputs)
    train_network(network, train, l_rate, n_epoch, n_outputs)
    return [predict_mlp(network, row) for row in test]

# 5. Application sur la base Seeds (201 obs., 7 variables, 3 classes)
def load_seeds(filename):
    dataset = list()
    with open(filename, 'r') as file:
        for line in file:
            row = line.strip().split()
            if row:
                dataset.append([float(v) for v in row])
    return dataset

dataset_seeds = load_seeds('seeds/seeds_dataset.txt')
for row in dataset_seeds:
    row[-1] = int(row[-1]) - 1      # classes 1,2,3 → 0,1,2

seed(1)
scores_seeds = evaluate_algorithm(dataset_seeds, back_propagation, 5, 0.3, 500, 5)
print(f"\n[Seeds – MLP] Scores par fold : {scores_seeds}")
print(f"[Seeds – MLP] Précision moyenne : {sum(scores_seeds)/len(scores_seeds):.2f}%")

# ===========================================================
# EXERCICE 1 : Perceptron pour les fonctions logiques NOT, AND, OR
# ===========================================================

print("\n===== EXERCICE 1 : Fonctions logiques avec Perceptron simple =====")

# NOT : 1 entrée  [entrée, sortie_attendue]
data_not = [[0, 1], [1, 0]]
weights_not = train_weights(data_not, l_rate=0.1, n_epoch=20)
print("\nNOT :")
for row in data_not:
    print(f"  NOT({int(row[0])}) = {int(predict(row, weights_not))}  (attendu {int(row[-1])})")

# AND : 2 entrées  [x1, x2, sortie_attendue]
data_and = [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 1]]
weights_and = train_weights(data_and, l_rate=0.1, n_epoch=20)
print("\nAND :")
for row in data_and:
    print(f"  {int(row[0])} AND {int(row[1])} = {int(predict(row, weights_and))}  (attendu {int(row[-1])})")

# OR : 2 entrées
data_or = [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]]
weights_or = train_weights(data_or, l_rate=0.1, n_epoch=20)
print("\nOR :")
for row in data_or:
    print(f"  {int(row[0])} OR  {int(row[1])} = {int(predict(row, weights_or))}  (attendu {int(row[-1])})")

# ===========================================================
# EXERCICE 2 : MLP pour la fonction logique XOR
# ===========================================================
# XOR n'est pas linéairement séparable → le perceptron simple échoue.
# Un MLP à 2 neurones cachés peut l'apprendre.

print("\n===== EXERCICE 2 : XOR avec MLP =====")

data_xor = [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]

seed(42)
network_xor = initialize_network(n_inputs=2, n_hidden=2, n_outputs=2)
train_network(network_xor, data_xor, l_rate=0.5, n_epoch=2000, n_outputs=2)

print("\nXOR :")
for row in data_xor:
    pred = predict_mlp(network_xor, row)
    print(f"  {int(row[0])} XOR {int(row[1])} = {pred}  (attendu {int(row[-1])})")

# ===========================================================
# EXERCICE 3 : Implémentation MLP avec Keras sur la base diabetes
# ===========================================================

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy

numpy.random.seed(7)

dataset_diab = numpy.loadtxt('pima-indians-diabetes.data.csv', delimiter=',')
X_diab = dataset_diab[:, 0:8]
Y_diab = dataset_diab[:, 8]

# Définition du modèle : 8 entrées → couche 12 → couche 8 → 1 sortie sigmoïde
model = Sequential()
model.add(Dense(12, input_shape=(8,), activation='relu'))
model.add(Dense(8,  activation='relu'))
model.add(Dense(1,  activation='sigmoid'))

# Compilation : cross-entropy binaire + optimiseur Adam
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Entraînement
model.fit(X_diab, Y_diab, epochs=150, batch_size=10, verbose=0)

# Évaluation
_, accuracy = model.evaluate(X_diab, Y_diab, verbose=0)
print(f'\n[Keras – diabetes] Précision du modèle de base : {accuracy * 100:.2f}%')

# Prédictions sur les 5 premiers exemples
predictions = (model.predict(X_diab) > 0.5).astype(int)
print("5 premières prédictions :")
for i in range(5):
    print(f'  {X_diab[i].tolist()} => {int(predictions[i])} (attendu {int(Y_diab[i])})')

# ===========================================================
# EXERCICE 4 : Architecture modifiée (plus de couches / neurones)
# ===========================================================

print("\n[Keras – diabetes] Architecture modifiée (16-16-8-1) :")

model_modifie = Sequential()
model_modifie.add(Dense(16, input_shape=(8,), activation='relu'))
model_modifie.add(Dense(16, activation='relu'))
model_modifie.add(Dense(8,  activation='relu'))
model_modifie.add(Dense(1,  activation='sigmoid'))

model_modifie.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model_modifie.fit(X_diab, Y_diab, epochs=150, batch_size=10, verbose=0)

_, accuracy_mod = model_modifie.evaluate(X_diab, Y_diab, verbose=0)
print(f'Précision du modèle modifié : {accuracy_mod * 100:.2f}%')

# ===========================================================
# Implémentation MLP avec SciKeras
# ===========================================================

from scikeras.wrappers import KerasClassifier

def baseline_model():
    """Modèle de base Keras pour KerasClassifier."""
    model = Sequential()
    model.add(Dense(12, input_shape=(8,), activation='relu'))
    model.add(Dense(8,  activation='relu'))
    model.add(Dense(1,  activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

estimator = KerasClassifier(model=baseline_model, epochs=200, batch_size=5, verbose=0)
