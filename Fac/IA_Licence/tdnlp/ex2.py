import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
import re

df = pd.read_csv("Tweets.csv")

plt.figure(figsize=(10,6))
sns.countplot(data=df, x='airline', palette='Set2')
plt.title('Nombre de tweets pour chaque compagnie aérienne')
plt.xlabel('Compagnie Aérienne')
plt.ylabel('Nombre de Tweets')
plt.show()

plt.figure(figsize=(6,4))
sns.countplot(data=df, x='airline_sentiment', palette='muted')
plt.title('Distribution des sentiments')
plt.xlabel('Sentiment')
plt.ylabel('Nombre de Tweets')
plt.show()

plt.figure(figsize=(12,8))
sns.countplot(data=df, x='airline', hue='airline_sentiment', palette='viridis')
plt.title('Répartition des sentiments pour chaque compagnie aérienne')
plt.xlabel('Compagnie Aérienne')
plt.ylabel('Nombre de Tweets')
plt.legend(title='Sentiment')
plt.show()

def preprocess_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

df['clean_text'] = df['text'].apply(preprocess_text)

X = df['clean_text']
y = df['airline_sentiment']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer()
X_train_vect = vectorizer.fit_transform(X_train)
X_test_vect = vectorizer.transform(X_test)

model = RandomForestClassifier()
model.fit(X_train_vect, y_train)

y_pred = model.predict(X_test_vect)

conf_matrix = confusion_matrix(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

print("Matrice de Confusion:")
print(conf_matrix)
print("Accuracy:", accuracy)
print("F1 Score:", f1)
