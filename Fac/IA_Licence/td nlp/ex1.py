import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import nltk
nltk.download('stopwords')
nltk.download('punkt')

def cleanWord(text):
    # Enlever les ponctuations
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Découper les mots en utilisant la tokenization
    words = word_tokenize(text)

    # Mettre les mots en minuscule
    words = [word.lower() for word in words]

    # Éliminer les stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Appliquer le stemming sur les mots
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]

    # Retourner la liste des mots résultants sous forme d’une chaîne
    return ' '.join(words)

with open('tweets.txt', 'r', encoding='utf-8') as file:
    texte = file.read()

resultat = cleanWord(texte)

print(resultat)
