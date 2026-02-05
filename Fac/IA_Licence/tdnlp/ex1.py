import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
nltk.download('punkt ')
nltk.download('stopwords ')
def cleanWord(text):
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = word_tokenize(text)

    tokens = [word.lower() for word in tokens]

    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    tokens = [word for word in tokens if word not in stop_words]
    
    stemmer = PorterStemmer()
    
    # Appliquer le stemming sur les mots
    tokens = [stemmer.stem(word) for word in tokens]
    return ' '.join(tokens)

with open('tweets.txt', 'r') as file:
    texte = file.read()

resultat = cleanWord(texte)

print(resultat)
