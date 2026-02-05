import random
import pandas as pd

# Charger les données à partir du fichier CSV
file_name = input("Entrez le nom du fichier CSV correspondant au genre de film que vous souhaitez recommander: ")
df = pd.read_csv(f"{file_name}.csv")

# Supprimer les lignes avec des valeurs manquantes dans la colonne Genre
df.dropna(subset=["genre"], inplace=True)

# Convertir la colonne Genre en liste de genres
df["genre"] = df["genre"].apply(lambda x: [genre.strip() for genre in x.split(",")])

# Créer un dictionnaire de films avec leurs genres
films = {title: genres for title, genres in zip(df["movie_name"], df["genre"])}

def recommend_movie(genre):
    movies_genre = [movie for movie, genres in films.items() if genre.capitalize() in genres]
    if movies_genre:
        return random.choice(movies_genre)
    else:
        return "Désolé, je n'ai pas de recommandation pour ce genre."

print("Bienvenue dans notre chatbot de recommandation de films!")
while True:
    user_input = input("Quel genre de film recherchez-vous? (action, adventure, animation, biography, crime, family, fantasy, film-noir, history, horror, mystery, romance, scifi, sports, thriller, war). Taper quit pour quitter ")
    if user_input.lower() == "quit":
        print("Merci d'avoir utilisé notre chatbot de recommandation de films. Au revoir!")
        break
    recommendation = recommend_movie(user_input)
    print("Je vous recommande de regarder:", recommendation)