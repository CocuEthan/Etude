import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, accuracy_score
from gensim.models import Word2Vec

def preprocess_text(text, stop_words):
    text = re.sub(r'\W', ' ', text) 
    text = re.sub(r'\s+', ' ', text)  
    text = text.lower() 
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

nltk.download('stopwords')
stop_words_en = set(stopwords.words('english'))

try:
    bbc_news = pd.read_csv('bbc-news-data.csv', sep='\t')
except FileNotFoundError:
    print("ERREUR: Le fichier 'bbc-news-data.csv' est introuvable.")
    print("Veuillez télécharger ce dataset et le placer dans le bon dossier.")
    exit()

print("Prétraitement des données BBC News...")
bbc_news['tokens'] = bbc_news['content'].apply(lambda x: preprocess_text(x, stop_words_en))

print("Entraînement du modèle Word2Vec...")
w2v_model_bbc = Word2Vec(sentences=bbc_news['tokens'], vector_size=100, window=5, min_count=2, workers=4)

def document_vector(doc, model):
    doc = [word for word in doc if word in model.wv.index_to_key]
    if not doc:
        return np.zeros(model.vector_size)
    return np.mean(model.wv[doc], axis=0)

print("Création des vecteurs de documents...")
X = np.array([document_vector(doc, w2v_model_bbc) for doc in bbc_news['tokens']])

le = LabelEncoder()
y = le.fit_transform(bbc_news['category'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

svm_classifier = SVC()
svm_classifier.fit(X_train, y_train)
svm_predictions = svm_classifier.predict(X_test)
nb_classifier = GaussianNB()
nb_classifier.fit(X_train, y_train)
nb_predictions = nb_classifier.predict(X_test)

print(f"Score de précision: {accuracy_score(y_test, svm_predictions):.4f}")
print("Rapport de classification:")
print(classification_report(y_test, svm_predictions, target_names=le.classes_))


print(f"Score de précision: {accuracy_score(y_test, nb_predictions):.4f}")
print("Rapport de classification:")
print(classification_report(y_test, nb_predictions, target_names=le.classes_))