import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

# Charger les données utilisateurs
with open("user.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)

# Charger les données de sorties
with open("sortie.json", "r", encoding="utf-8") as f:
    sorties_data = json.load(f)

# Préparation des sorties
sorties_df = pd.DataFrame(sorties_data)
sorties_df["features"] = sorties_df["type"] + " " + sorties_df["description"].fillna("")

# Vectorisation TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(sorties_df["features"])

# Création d’un dictionnaire pour sauvegarder les recommandations
recommendations = {}

# Boucle sur chaque utilisateur
for user in users_data:
    user_id = user["utilisateur"]["id"]
    interets = " ".join(user["utilisateur"]["interets"])
    
    # Vectorisation des intérêts
    user_vec = vectorizer.transform([interets])
    
    # Similarité cosinus entre les intérêts utilisateur et les sorties
    cosine_sim = cosine_similarity(user_vec, tfidf_matrix).flatten()
    
    # Index des sorties les plus similaires
    top_indices = cosine_sim.argsort()[::-1][:5]  # top 5 recommandations

    # Sauvegarde des résultats
    recommendations[user_id] = {
        "recommended_sortie_ids": sorties_df.iloc[top_indices]["id"].tolist(),
        "scores": cosine_sim[top_indices].tolist()
    }

# Sauvegarder le modèle et les recommandations
with open("recommandations.pkl", "wb") as f:
    pickle.dump(recommendations, f)

print("✅ Entraînement terminé. Recommandations sauvegardées dans recommandations.pkl.")
