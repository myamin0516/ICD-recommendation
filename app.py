from flask import Flask, render_template, request
import sqlite3
import spacy
from spacy.matcher import PhraseMatcher
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load the SpaCy model
nlp = spacy.load('en_core_web_sm')

# Initialize PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
patterns = [
    "diabetes", "hypertension", "chest pain",
    "fractured femur", "chronic obstructive pulmonary disease", "otitis media"
]
pattern_docs = [nlp(text) for text in patterns]
matcher.add("MEDICAL_TERMS", pattern_docs)

# Expanded synonyms dictionary
synonyms = {
    "diabetes": [
        "diabetes", "type 2 diabetes", "type 2 diabetes mellitus", "sugar", 
        "glucose", "high sugar", "hyperglycemia", "insulin resistance"
    ],
    "hypertension": [
        "hypertension", "high blood pressure", "elevated blood pressure", 
        "angina", "essential hypertension", "primary hypertension"
    ],
    "chest pain": [
        "chest pain", "angina", "discomfort in chest", "cardiac pain", 
        "sternal pain", "thoracic pain", "heart pain"
    ],
    "fractured femur": [
        "fractured femur", "broken leg", "broken thigh", "femoral fracture", 
        "thigh bone fracture", "femur break"
    ],
    "chronic obstructive pulmonary disease": [
        "COPD", "chronic obstructive pulmonary disease", "emphysema", 
        "chronic bronchitis", "airway obstruction", "lung disease", 
        "chronic lung disease", "obstructive airway disease"
    ],
    "otitis media": [
        "otitis media", "ear infection", "middle ear infection", 
        "ear inflammation", "ear pain", "otitis media unspecified"
    ]
}

def preprocess_text(text):
    """Preprocess the input text by converting to lowercase and stripping unwanted characters."""
    return text.lower().strip()

def get_synonym_matches(text):
    """Expand the input text with synonyms using fuzzy matching."""
    expanded_terms = set()
    doc = nlp(text.lower())
    for token in doc:
        for key, syns in synonyms.items():
            if fuzz.ratio(token.text, key) > 65:  # Match to the key directly
                expanded_terms.add(key)
            elif any(fuzz.ratio(token.text, syn) > 59 for syn in syns):
                expanded_terms.add(key)
    return expanded_terms

def rank_matches(matches, expanded_terms):
    """Rank the matches based on their relevance to the expanded terms."""
    ranked_matches = sorted(matches, key=lambda x: fuzz.ratio(x[1].lower(), ' '.join(expanded_terms)), reverse=True)
    return ranked_matches

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    record_text = preprocess_text(request.form['record_text'])
    print(f"Input text: {record_text}")

    # Process the text using SpaCy NLP
    doc = nlp(record_text)

    # Use PhraseMatcher to extract terms
    matches = matcher(doc)
    extracted_terms = [doc[start:end].text.lower() for match_id, start, end in matches]
    print(f"Extracted terms: {extracted_terms}")

    # Expand terms with synonyms
    expanded_terms = set(extracted_terms)
    expanded_terms.update(get_synonym_matches(record_text))
    print(f"Expanded terms: {expanded_terms}")

    # Connect to the database and query for matching billing codes
    conn = sqlite3.connect('medical_records.db')
    cursor = conn.cursor()
    recommendations = []
    
    for term in expanded_terms:
        cursor.execute("SELECT icd_code, description FROM billing_codes WHERE LOWER(description) LIKE ?", (f'%{term}%',))
        recommendations.extend(cursor.fetchall())
    
    conn.close()

    # Rank the matches based on relevance
    ranked_recommendations = rank_matches(recommendations, expanded_terms)
    print(f"Ranked recommendations: {ranked_recommendations}")

    return render_template('results.html', record_text=record_text, recommendations=ranked_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
