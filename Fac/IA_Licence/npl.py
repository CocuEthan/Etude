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

# nltk.download('punkt')  # à importer pour le chatBot


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