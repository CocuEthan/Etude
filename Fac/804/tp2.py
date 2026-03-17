# Make a prediction with weights 
def predict(row, weights): 
    activation = weights[0] 
    for i in range(len(row)-1): 
        activation += weights[i + 1] * row[i] 
    return 1.0 if activation >= 0.0 else 0.0

# Estimate Perceptron weights using stochastic gradient descent 
def train_weights(train, l_rate, n_epoch): 
    weights = [0.0 for i in range(len(train[0]))] 
    for epoch in range(n_epoch): 
        for row in train: 
            prediction = predict(row, weights) 
            error = row[-1] - prediction 
            weights[0] = weights[0] + l_rate * error 
            for i in range(len(row)-1): 
                weights[i + 1] = weights[i + 1] + l_rate * error * row[i] 
    return weights


import csv

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

# c) Convertir la colonne des classes 
def str_column_to_int(dataset, column):
    class_values = [row[column] for row in dataset]
    unique = set(class_values)
    lookup = dict()
    for i, value in enumerate(unique):
        lookup[value] = i
    for row in dataset:
        row[column] = lookup[row[column]]
    return lookup

# d) Évaluer l'algorithme
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
    folds = list()
    dataset_copy = list(dataset)
    fold_size = int(len(dataset) / n_folds)
    for _ in range(n_folds):
        fold = list()
        while len(fold) < fold_size:
            fold.append(dataset_copy.pop(0))
        folds.append(fold)
    
    scores = list()
    for fold in folds:
        train_set = list(folds)
        train_set.remove(fold)
        train_set = sum(train_set, [])
        test_set = list()
        for row in fold:
            row_copy = list(row)
            test_set.append(row_copy)
            row_copy[-1] = None
        predicted = algorithm(train_set, test_set, *args)
        actual = [row[-1] for row in fold]
        correct = 0
        for i in range(len(actual)):
            if actual[i] == predicted[i]:
                correct += 1
        accuracy = (correct / float(len(actual))) * 100.0
        scores.append(accuracy)
    return scores

# e) La fonction perceptron 
def perceptron(train, test, l_rate, n_epoch):
    predictions = list()
    weights = train_weights(train, l_rate, n_epoch)
    for row in test:
        prediction = predict(row, weights)
        predictions.append(prediction)
    return predictions

from random import random
# Initialize a network 
def initialize_network(n_inputs, n_hidden, n_outputs): 
    network = list() 
    
    hidden_layer = [{'weights': [random() for i in range(n_inputs + 1)]} 
                    for i in range(n_hidden)] 
    network.append(hidden_layer) 
    
    output_layer = [{'weights': [random() for i in range(n_hidden + 1)]} 
                    for i in range(n_outputs)]
    network.append(output_layer) 
    
    return network


# Forward propagate input to a network output 
def forward_propagate(network, row): 
    inputs = row 
    for layer in network: 
        new_inputs = [] 
        for neuron in layer: 
            activation = activate(neuron['weights'], inputs) 
            neuron['output'] = transfer(activation) 
            new_inputs.append(neuron['output']) 
        inputs = new_inputs 
    return inputs

# Backpropagate error and store in neurons 
def backward_propagate_error(network, expected): 
    for i in reversed(range(len(network))): 
        layer = network[i] 
        errors = list() 
        if i != len(network)-1: 
            for j in range(len(layer)): 
                error = 0.0 
                for neuron in network[i + 1]: 
                    error += (neuron['weights'][j] * neuron['delta']) 
                errors.append(error) 
        else: 
            for j in range(len(layer)): 
                neuron = layer[j] 
                errors.append(neuron['output'] - expected[j]) 
        for j in range(len(layer)): 
            neuron = layer[j] 
            neuron['delta'] = errors[j] * transfer_derivative(neuron['output']) 

#Train a network for a fixed number of epochs 
def train_network(network, train, l_rate, n_epoch, n_outputs): 
    for epoch in range(n_epoch): 
        for row in train: 
            outputs = forward_propagate(network, row) 
            expected = [0 for i in range(n_outputs)] 
            expected[row[-1]] = 1 
            backward_propagate_error(network, expected) 
            update_weights(network, row, l_rate) 

def evaluate_algorithm(dataset, algorithm, n_folds, *args): 
    folds = cross_validation_split(dataset, n_folds) 
    scores = list() 
    for fold in folds: 
        train_set = list(folds) 
        train_set.remove(fold) 
        train_set = sum(train_set, []) 
        test_set = list() 
        for row in fold: 
            row_copy = list(row) 
            test_set.append(row_copy) 
            row_copy[-1] = None 
        predicted = algorithm(train_set, test_set, *args) 
        actual = [row[-1] for row in fold] 
        accuracy = accuracy_metric(actual, predicted) 
        scores.append(accuracy) 
    return scores 

def predict(inputs, weights):
    activation = weights[0]
    for i in range(len(inputs)):
        activation += weights[i + 1] * inputs[i]
    return 1.0 if activation >= 0.0 else 0.0

import math

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def forward_propagate(network, row):
    inputs = row
    for layer in network:
        new_inputs = []
        for neuron in layer:
            activation = neuron['weights'][-1] 
            for i in range(len(neuron['weights'])-1):
                activation += neuron['weights'][i] * inputs[i]
            neuron['output'] = sigmoid(activation)
            new_inputs.append(neuron['output'])
        inputs = new_inputs
    return inputs

from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Dense 
from sklearn.model_selection import train_test_split 
import numpy 
# fix random seed for reproducibility 
seed = 7 
numpy.random.seed(seed) 
# load the dataset 
dataset = numpy.loadtxt("diabetes.csv", delimiter=",") 
# split into input (X) and output (Y) variables 
X = dataset[:,0:8] 
Y = dataset[:,8] 

# create model 
model = Sequential() 
model.add(Dense(12, input_dim=8, activation='relu')) 
model.add(Dense(8, activation='relu')) 
model.add(Dense(1, activation='sigmoid')) 

# Compile model 
model.compile(loss='binary_crossentropy', optimizer='adam', 
metrics=['accuracy']) 

# Fit the model 
model.fit(X,Y, epochs=150, batch_size=10) 

# evaluate the keras model 
_, accuracy = model.evaluate(X, Y) 
print('Accuracy: %.2f' % (accuracy*100)) 
import numpy as np
# make class predictions with the model 
predictions = (model.predict(X) > 0.5).astype(int) 
# summarize the first 5 cases 
for i in range(5): 
    print('%s => %d (expected %d)' % (X[i].tolist(), predictions[i], Y[i]))

dataset = np.loadtxt('pima-indians-diabetes.csv', delimiter=',')
X = dataset[:, 0:8] 
Y = dataset[:, 8]   
model = Sequential()
model.add(Dense(12, input_shape=(8,), activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

print("Entraînement en cours...")
model.fit(X, Y, epochs=150, batch_size=10, verbose=0) # verbose=0 masque les logs pour plus de clarté

_, accuracy = model.evaluate(X, Y)
print('Précision du modèle de base : %.2f%%' % (accuracy * 100))


model_modifie = Sequential()

model_modifie.add(Dense(16, input_shape=(8,), activation='relu'))

model_modifie.add(Dense(16, activation='relu'))
model_modifie.add(Dense(8, activation='relu'))
model_modifie.add(Dense(1, activation='sigmoid'))

model_modifie.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print("Entraînement du modèle modifié en cours...")
model_modifie.fit(X, Y, epochs=150, batch_size=10, verbose=0)

_, accuracy_modifie = model_modifie.evaluate(X, Y)
print('Précision du modèle modifié : %.2f%%' % (accuracy_modifie * 100))


from scikeras.wrappers import KerasClassifier 
# define baseline model 
def baseline_model(): 
# create model 
    model = Sequential() 
# Compile model 
    return model 
estimator = KerasClassifier(model=baseline_model, epochs=200, batch_size=5, verbose=0)