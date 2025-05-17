from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pickle
import os
import spacy
import re
from datetime import datetime, timedelta
import locale

# Configurer la locale française pour les dates
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    locale.setlocale(locale.LC_TIME, 'fr_FR')

# Créer l'application Flask
app = Flask(__name__)
CORS(app)

# Charger le modèle NLP
nlp = spacy.load("fr_core_news_sm")

# Thèmes de sorties
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

def load_sorties(filepath="sortie.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier {filepath} introuvable.")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_recommendations(filepath="recommandations.pkl"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier {filepath} introuvable.")
    with open(filepath, "rb") as f:
        return pickle.load(f)

import re

def extract_lieux(text):
    doc = nlp(text)
    lieux = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "GPE"]]

    # Villes connues à ajouter si non détectées
    villes_connues = ["paris", "lyon", "marseille", "toulouse", "nice", "nantes", "strasbourg"]
    for ville in villes_connues:
        if ville in text.lower() and ville.capitalize() not in lieux:
            lieux.append(ville.capitalize())

    # Expressions contextuelles : à, chez, dans
    motifs = [
        r"\bà\s+([A-Z][a-zéèê\-]+)",
        r"\bchez\s+([A-Z][a-zéèê\-]+)",
        r"\bdans\s+([A-Z][a-zéèê\-]+(?:\s+[A-Z][a-zéèê\-]+)*)"
    ]
    for motif in motifs:
        matches = re.findall(motif, text)
        for match in matches:
            if match not in lieux:
                lieux.append(match)

    return lieux

def extract_date(text):
    text = text.lower()
    now = datetime.now()
    if "demain" in text:
        return now + timedelta(days=1)
    elif "aujourd'hui" in text:
        return now
    elif "week-end" in text:
        return now + timedelta(days=(5 - now.weekday()) if now.weekday() < 5 else 0)
    elif "samedi" in text:
        return now + timedelta((5 - now.weekday()) % 7)
    elif "dimanche" in text:
        return now + timedelta((6 - now.weekday()) % 7)
    return None

import difflib

def detect_theme(text):
    text = text.lower()
    found = []
    
    # D'abord vérifier les correspondances exactes
    for theme, keywords in themes.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords):
            found.append(theme)
    
    # Si rien trouvé, faire une recherche plus large
    if not found:
        for theme, keywords in themes.items():
            if any(kw in text for kw in keywords):
                found.append(theme)
    
    return list(set(found))


def detect_intention(text):
    text = text.lower()
    if any(w in text for w in ["est-ce que", "où", "à", "comment", "qui"]):
        return "question"
    elif any(w in text for w in ["aidez", "besoin", "pouvez-vous", "aide"]):
        return "aide"
    elif any(w in text for w in ["j'aime", "je veux", "je cherche"]):
        return "préférence"
    return "général"

# Générer une réponse basée sur l’intention
def generate_response(user_input):
    themes_found = detect_theme(user_input)
    lieux = extract_lieux(user_input)
    date = extract_date(user_input)
    intention = detect_intention(user_input)

    if intention == "aide":
        return "Bien sûr, je suis là pour vous aider !"
    elif intention == "question":
        return "Bonne question ! Je vais chercher ça pour vous."
    elif intention == "préférence":
        theme_text = ", ".join(themes_found) if themes_found else "divers thèmes"
        lieu_text = f" à {', '.join(lieux)}" if lieux else ""
        date_text = f" pour {date.strftime('%A %d %B %Y')}" if date else ""
        return f"Super ! Je peux vous recommander une sortie liée à {theme_text}{lieu_text}{date_text}."
    else:
        return "D'accord, dites-m'en un peu plus sur ce que vous aimez."

# ROUTE principale
# ROUTE principale - version modifiée pour la recherche par mots-clés
@app.route("/loisir", methods=["POST"])
def get_loisirs():
    data = request.get_json()

    if not data:
        return jsonify({"activites": [], "erreur": "Aucune donnée reçue."}), 400

    try:
        sorties = load_sorties()
    except FileNotFoundError as e:
        return jsonify({"activites": [], "erreur": str(e)}), 500

    # Recommandations personnalisées
    if "user_id" in data:
        try:
            recommandations = load_recommendations()
        except FileNotFoundError as e:
            return jsonify({"activites": [], "erreur": str(e)}), 500

        user_id = data["user_id"]
        if user_id in recommandations:
            sortie_ids = recommandations[user_id]["recommended_sortie_ids"]
            activites = [s for s in sorties if s["id"] in sortie_ids][:3]
            return jsonify({"activites": activites}) if activites else jsonify({"activites": [], "erreur": "Aucune recommandation."})
        else:
            return jsonify({"activites": [], "erreur": "Aucune recommandation pour cet utilisateur."})

    # Recherche par préférences
    elif "preferences" in data:
        prefs = data["preferences"]
        champs_recherche = ["type", "titre", "description", "lieu"]
        
        filtered = [
            s for s in sorties
            if any(
                pref.lower() in str(s.get(field, "")).lower()
                for field in champs_recherche
                for pref in prefs
            )
        ][:3]
        
        return jsonify({"activites": filtered}) if filtered else jsonify({"activites": [], "erreur": "Aucune sortie correspondant à ces préférences."})

    # Recherche par message texte
    elif "message" in data:
        user_input = data["message"].lower()
        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({"activites": [], "erreur": "Le message doit être un texte non vide."}), 400

        # Analyse du message
        themes_found = detect_theme(user_input)
        lieux = extract_lieux(user_input)
        date = extract_date(user_input)

        # Recherche dans les sorties
        filtered = []
        for sortie in sorties:
            # Vérifier si la sortie correspond aux critères
            match_theme = not themes_found or any(
                theme.lower() in sortie.get("type", "").lower() 
                for theme in themes_found
            )
            
            match_lieu = not lieux or any(
                lieu.lower() in sortie.get("lieu", "").lower()
                for lieu in lieux
            )
            
            match_date = not date or date.strftime('%Y-%m-%d') in sortie.get("dateHeure", "")

            # Vérifier aussi dans le titre et description
            texte_sortie = f"{sortie.get('titre','')} {sortie.get('description','')}".lower()
            match_texte = any(
                term.lower() in texte_sortie 
                for term in user_input.split() 
                if len(term) > 2
            )

            if (match_theme or match_texte) and match_lieu and match_date:
                filtered.append(sortie)
                if len(filtered) >= 3:
                    break

        return jsonify({
            "activites": filtered,
            "themes": themes_found,
            "lieux": lieux,
            "date": date.strftime('%A %d %B %Y') if date else None
        })
if __name__ == "__main__":
    app.run(port=3300, debug=True)