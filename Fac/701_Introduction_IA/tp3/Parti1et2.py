import numpy as np
import pandas as pd
import re
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from gensim.models import Word2Vec

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
try:
    airline_tweets = pd.read_csv('Tweets.csv')
except FileNotFoundError:
    print("ERREUR: Le fichier 'Tweets.csv' est introuvable.")
    exit()
features = airline_tweets.iloc[:, 10].values
labels = airline_tweets.iloc[:, 1].values

processed_features = []
for sentence in range(0, len(features)):
    processed_feature = re.sub(r'\W', ' ', str(features[sentence]))
    processed_feature = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_feature)
    processed_feature = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_feature)
    processed_feature = re.sub(r'\s+', ' ', processed_feature, flags=re.I)
    processed_feature = re.sub(r'^b\s+', '', processed_feature)
    processed_feature = processed_feature.lower()
    processed_features.append(processed_feature)

vectorizer = TfidfVectorizer(max_features=2500, min_df=7, max_df=0.8, stop_words=stop_words)
X_tfidf = vectorizer.fit_transform(processed_features).toarray()
X_train_tfidf, X_test_tfidf, y_train_tfidf, y_test_tfidf = train_test_split(X_tfidf, labels, test_size=0.2, random_state=0)
text_classifier_svm = LinearSVC(random_state=0, max_iter=10000)
text_classifier_svm.fit(X_train_tfidf, y_train_tfidf)

predictions_svm = text_classifier_svm.predict(X_test_tfidf)
print(confusion_matrix(y_test_tfidf, predictions_svm))
print(classification_report(y_test_tfidf, predictions_svm))
print(f"Accuracy Score (SVM): {accuracy_score(y_test_tfidf, predictions_svm):.4f}")
#Partie 2
tokenized_tweets = []
for tweet in processed_features:
    tokens = tweet.split()
    tokens = [word for word in tokens if word not in stop_words]
    tokenized_tweets.append(tokens)
w2v_model = Word2Vec(sentences=tokenized_tweets, vector_size=100, window=5, min_count=1, workers=4)

def document_vector(doc, model):
    doc = [word for word in doc if word in model.wv.index_key]
    if not doc:
        return np.zeros(model.vector_size)
    return np.mean(model.wv[doc], axis=0)
X_w2v = np.array([document_vector(doc, w2v_model) for doc in tokenized_tweets])
y_w2v = labels 
X_train_w2v, X_test_w2v, y_train_w2v, y_test_w2v = train_test_split(X_w2v, y_w2v, test_size=0.2, random_state=0)

text_classifier_rf = RandomForestClassifier(n_estimators=200, random_state=0)
text_classifier_rf.fit(X_train_w2v, y_train_w2v)
predictions_rf = text_classifier_rf.predict(X_test_w2v)
print("\n Résultats:")
print(confusion_matrix(y_test_w2v, predictions_rf))
print(classification_report(y_test_w2v, predictions_rf))
print(f"Accuracy Score (RF): {accuracy_score(y_test_w2v, predictions_rf):.4f}")
