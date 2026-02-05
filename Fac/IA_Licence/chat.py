import numpy as np  # bibliothèque de calculs sur des objets mathématiques usuels
import random  # bibliothèque de génération de nombres aléatoires
import time  # mesure du temps
from copy import deepcopy

import torch   # bibliothèque PyTorch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import nltk  # pour le ChatBot
from nltk.stem.porter import PorterStemmer

import json

nltk.download('punkt')  # à importer pour le chatBot

stemmer = PorterStemmer()

def tokenize(phrase):
    """
    découpe les phrases en tableaux de mots/tokens
    un token peut être un mot, un signe de ponctuation ou un nombre
    """
    return nltk.word_tokenize(phrase)


def stem(mot):
    """
    to stem = trouver la racine d'un mot
    lower = écrire en minuscule
    examples :
    mots = ["organiser", "organises", "organise"]
    mots = [stem(w) for w in mots]
    -> ["organ", "organ", "organ"]
    """
    return stemmer.stem(mot.lower())


def sac_de_mots(tokenized_phrase, mots):
    """
    retourne  le tableau du sac de mots :
    1 pour chaque mot connu qui figure dans la phrase,
    0 sinon
    example :
    phrase tokenisée = ["bonjour", "comment", "vas", "tu"]
    liste de mots connus = ["salut", "bonjour", "je", "tu", "ciao", "merci", "cool"]
    sac   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]
    """
    # stem chaque mot
    phrase_mots = [stem(mot) for mot in tokenized_phrase]
    # initialise le sac avec 0 pour chaque mot
    sac = np.zeros(len(mots), dtype=np.float32)
    for idx, w in enumerate(mots):
        if w in phrase_mots: 
            sac[idx] = 1

    return sac

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size) 
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out
    with open('intents.json', 'r') as f:
    intents = json.load(f)

all_mots = []
tags = []
xy = []
# boucle sur chaque phrase de nos patterns d'intents
for intent in intents['intents']:
    tag = intent['tag']
    # add to tag list
    tags.append(tag)
    for pattern in intent['patterns']:
        # tokenize chaque mot de la phrase
        w = tokenize(pattern)
        # ajoute à notre liste de mots
        all_mots.extend(w)
        # ajoute à la liste de paires xy
        xy.append((w, tag))

# stem et écrit en minuscule chaque mot
ignore_mots = ['?', '.', '!']
all_mots = [stem(w) for w in all_mots if w not in ignore_mots]

# efface les doublons et trie
all_mots = sorted(set(all_mots))
tags = sorted(set(tags))

# crée les données d'apprentissage
X_train = []
y_train = []
for (pattern_phrase, tag) in xy:
        # X: sac de mots pour chaque pattern_phrase
    sac = sac_de_mots(pattern_phrase, all_mots)
    X_train.append(sac)
    # y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Hyper-parameters 
num_epochs = 1000
batch_size = 8
learning_rate = 0.001
input_size = len(X_train[0])
hidden_size = 8
output_size = len(tags)

class ChatDataset(Dataset):

    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    # supporte l'indexation de manière à ce que dataset[i] puisse être utilisé pour obtenir i-ième échantillon
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    # on peut appeler len(dataset) pour obtenir la taille
    def __len__(self):
        return self.n_samples

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset,
                          batch_size=batch_size,
                          shuffle=True,
                          num_workers=2)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size, output_size).to(device)

# Perte et optimiseur
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Apprentissage du modèle
for epoch in range(num_epochs):
    for (mots, labels) in train_loader:
        mots = mots.to(device)
        labels = labels.to(device)

        # Forward pass
        outputs = model(mots)
        loss = criterion(outputs, labels)

        # Backward et optimisation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch+1) % 100 == 0:
        print (f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

print(f'final loss: {loss.item():.4f}')

donnees = {
"model_state": model.state_dict(),
"input_size": input_size,
"hidden_size": hidden_size,
"output_size": output_size,
"all_mots": all_mots,
"tags": tags
}

FICHIER = "donnees.pth"
torch.save(donnees, FICHIER)

print(f'entrainement terminé. fichier sauvegardé dans {FICHIER}')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FICHIER = "donnees.pth"
donnees = torch.load(FICHIER)

input_size = donnees["input_size"]
hidden_size = donnees["hidden_size"]
output_size = donnees["output_size"]
all_mots = donnees['all_mots']
tags = donnees['tags']
model_state = donnees["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "MonBot"
print("Discutons ! (taper 'fin' pour sortir du Chat)")
while True:
    phrase = input("Vous: ")
    if phrase == "fin":
        break

    phrase = tokenize(phrase)
    X = sac_de_mots(phrase, all_mots)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                print(f"{bot_name}: {random.choice(intent['reponses'])}")
    else:
        print(f"{bot_name}: Je ne comprends pas...")