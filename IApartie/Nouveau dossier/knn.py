from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pickle
import os
import spacy
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialisation
app = Flask(__name__)
CORS(app)
nlp = spacy.load("fr_core_news_sm")

# Chargement des modèles ML
model_embedding = SentenceTransformer('dangvantuan/sentence-camembert-base')
kmeans = KMeans(n_clusters=10)  # Pour le clustering des sorties

class RecommendationSystem:
    def __init__(self):
        self.sorties = self.load_data()
        self.user_profiles = {}
        self.vectorizer = TfidfVectorizer()
        self.initialize_ml_models()

    def load_data(self):
        with open("sorties.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def initialize_ml_models(self):
        # Embedding des descriptions
        descriptions = self.sorties['description'].tolist()
        self.embeddings = model_embedding.encode(descriptions)
        
        # Clustering
        self.sorties['cluster'] = kmeans.fit_predict(self.embeddings)
        
        # TF-IDF pour recherche textuelle
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.sorties.apply(lambda x: f"{x['titre']} {x['description']} {x['type']}", axis=1)
        )

    def update_user_profile(self, user_id, interaction):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferences': [],
                'history': []
            }
        self.user_profiles[user_id]['history'].append(interaction)
        
        # Mise à jour des préférences avec ML
        interaction_embedding = model_embedding.encode([interaction])
        closest_cluster = kmeans.predict(interaction_embedding)[0]
        self.user_profiles[user_id]['preferences'].append(closest_cluster)

    def recommend(self, user_id=None, query=None):
        if user_id and user_id in self.user_profiles:
            # Recommandation personnalisée
            user_clusters = self.user_profiles[user_id]['preferences']
            cluster_scores = {c: user_clusters.count(c) for c in set(user_clusters)}
            recommended = self.sorties[
                self.sorties['cluster'].isin(cluster_scores.keys())
            ].sort_values(by='cluster', key=lambda x: x.map(cluster_scores))
            return recommended.to_dict('records')
        
        elif query:
            # Recherche sémantique
            query_embed = model_embedding.encode([query])
            sim_scores = cosine_similarity(query_embed, self.embeddings)[0]
            top_indices = np.argsort(sim_scores)[-5:][::-1]
            return self.sorties.iloc[top_indices].to_dict('records')
        
        return self.sorties.sample(5).to_dict('records')

# Initialisation du système
rec_system = RecommendationSystem()

# API Endpoints
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    user_id = data.get("user_id")
    query = data.get("query")
    
    if user_id:
        rec_system.update_user_profile(user_id, query if query else "default_interaction")
    
    recommendations = rec_system.recommend(user_id=user_id, query=query)
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(port=3300, debug=True)
