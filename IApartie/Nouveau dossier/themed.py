from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import locale
from datetime import datetime

# Configurer la locale française
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    locale.setlocale(locale.LC_TIME, 'fr_FR')

# Initialiser l'application Flask
app = Flask(__name__)
CORS(app)

# Charger le modèle NLP spaCy
nlp = spacy.load("fr_core_news_sm")

# Exemple de structure des thèmes — À compléter toi-même
themes = {
    "famille": ["famille", "enfant", "parents", "sortie en famille", "parc d'attractions", "zoo", "spectacle enfants"],
    "musique": ["musique", "concert", "festival", "groupe", "jazz", "rock", "classique", "DJ", "soirée musicale"],
    "sport": ["football", "tennis", "sport", "match", "rando", "vélo", "escalade", "natation", "yoga", "course", "fitness"],
    "gastronomie": ["restaurant", "dîner", "cuisine", "gastronomie", "dégustation", "brunch", "repas", "buffet", "pâtisserie"],
    "culture": ["musée", "exposition", "peinture", "art", "théâtre", "opéra", "galerie", "pièce de théâtre", "spectacle"],
    "cinéma": ["cinéma", "film", "projection", "court-métrage", "avant-première"],
    "nature": ["balade", "forêt", "plage", "lac", "nature", "montagne", "pique-nique", "jardin", "camping"],
    "technologie": ["conférence", "startup", "innovation", "robotique", "IA", "hackathon", "coding", "jeu vidéo"],
    "bien-être": ["spa", "massage", "détente", "méditation", "relaxation", "bien-être", "retraite"],
    "romantique": ["couple", "amoureux", "sortie romantique", "dîner aux chandelles", "balade en amoureux"],
    "nocturne": ["soirée", "bar", "boîte", "club", "sortie nocturne", "afterwork"],
    "communautaire": ["événement local", "marché", "fête de quartier", "rencontre", "bénévolat", "association"],
    "shopping": ["shopping", "boutique", "soldes", "centre commercial", "marché artisanal"],
    "science": ["astronomie", "planétarium", "science", "conférence scientifique", "expo scientifique", "espace", "laboratoire"],
    "animaux": ["zoo", "aquarium", "ferme", "animaux", "centre équestre", "refuge", "chien", "chat"],
    "spirituel": ["église", "mosquée", "temple", "spirituel", "prière", "retraite spirituelle", "méditation guidée"],
    "éducation": ["atelier", "cours", "conférence", "formation", "conférence TEDx", "éducation", "masterclass"],
    "écologie": ["écologie", "zéro déchet", "recyclage", "marché bio", "nature", "transition écologique", "jardin partagé"],
    "arts manuels": ["atelier créatif", "peinture", "dessin", "céramique", "bricolage", "DIY", "artisanat"],
    "photo/vidéo": ["photo", "vidéo", "shooting", "studio", "exposition photo", "vlog", "montage vidéo"],
    "lecture/livres": ["livre", "lecture", "bibliothèque", "salon du livre", "rencontre d’auteur", "poésie"],
    "danse": ["danse", "salsa", "hip-hop", "atelier danse", "ballet", "soirée dansante"],
    "jeux/société": ["jeux", "jeux de société", "escape game", "quiz", "soirée jeux", "ludothèque"],
    "festivités": ["carnaval", "foire", "fête", "événement annuel", "parade", "feu d’artifice"],
    "en ligne": ["webinaire", "événement en ligne", "streaming", "conférence Zoom", "atelier virtuel"],
    "volontariat": ["bénévolat", "solidarité", "entraide", "mission humanitaire", "don", "collecte"],
    "langues": ["échange linguistique", "atelier anglais", "cours de français", "polyglotte", "langue étrangère"],
    "seniors": ["senior", "club des aînés", "sortie senior", "atelier mémoire", "activités retraités"],
    "expats/internationaux": ["expatrié", "internationaux", "rencontre expat", "soirée interculturelle"],
}


# Préférences fictives des utilisateurs
user_preferences = {
    "1": ["musique", "culture"],
    "2": ["nature", "sport"],
    # ➕ ajoute les préférences selon les `user_id`
}

# Détection des thèmes dans un message
def detect_themes(message):
    doc = nlp(message.lower())
    found_themes = set()
    for token in doc:
        for theme, keywords in themes.items():
            if token.text in keywords:
                found_themes.add(theme)
    return list(found_themes)

# Recommandation principale
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_message = data.get("message", "")
    user_id = data.get("user_id")

    # Prendre les préférences de l'utilisateur ou détecter via le message
    if user_id and str(user_id) in user_preferences:
        matched_themes = user_preferences[str(user_id)]
    else:
        matched_themes = detect_themes(user_message)

    return jsonify({
        "matched_themes": matched_themes,
        "status": "ok",
        "user_id_used": user_id if user_id else "none"
    })

if __name__ == '__main__':
    app.run(port=3300, debug=True)
