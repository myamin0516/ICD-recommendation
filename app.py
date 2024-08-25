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
        "diabetes", "type 2 diabetes", "type 2 diabetes mellitus",
        "glucose", "high blood sugar", "hyperglycemia"
    ],
    "hypertension": [
        "hypertension", "high blood pressure", "elevated blood pressure", 
        "angina"
    ],
    "fractured femur": [
        "fractured femur", "broken leg", "broken thigh",
        "femoral fracture", "thigh bone fracture", "femur break",
        "break femur"
    ],
    "chronic obstructive pulmonary disease": [
        "COPD", "chronic obstructive pulmonary disease", "emphysema", 
        "chronic bronchitis", "airway obstruction", "lung disease", 
        "chronic lung disease", "obstructive airway disease"
    ],
    "otitis media": [
        "otitis media", "ear infection", "middle ear infection", 
        "ear inflammation", "ear pain"
    ]
}

# Sample medical records
sample_records = [
    {
        "title": "Patient A - Diabetes and Hypertension",
        "text": "The patient has a history of type 2 diabetes mellitus and essential hypertension. They are currently on metformin and lisinopril."
    },
    {
        "title": "Patient B - COPD and Otitis Media",
        "text": "The patient is diagnosed with chronic obstructive pulmonary disease (COPD) and has a recent history of otitis media."
    },
    {
        "title": "Patient C - Fractured Femur",
        "text": "The patient sustained a fractured femur after a fall. They are scheduled for surgery."
    }
]

def preprocess_text(text):
    """Preprocess the input text by converting to lowercase and stripping unwanted characters."""
    return text.lower().strip()

def get_synonym_matches(text):
    """Expand the input text with synonyms using fuzzy matching."""
    expanded_terms = set()
    doc = nlp(text.lower())
    for token in doc:
        for key, syns in synonyms.items():
            if fuzz.ratio(token.text, key) > 70:  # Match to the key directly
                expanded_terms.add(key)
            elif any(fuzz.ratio(token.text, syn) > 75 for syn in syns):
                expanded_terms.add(key)
    return expanded_terms

def rank_matches(matches, expanded_terms):
    """Rank the matches based on their relevance to the expanded terms."""
    ranked_matches = sorted(matches, key=lambda x: fuzz.ratio(x[1].lower(), ' '.join(expanded_terms)), reverse=True)
    return ranked_matches

@app.route('/')
def index():
    return render_template('index.html', sample_records=sample_records)

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
    recommendations = set()  # Use a set to avoid duplicates
    
    for term in expanded_terms:
        term_parts = term.split()
        for part in term_parts:
            cursor.execute("SELECT icd_code, description FROM billing_codes WHERE LOWER(description) LIKE ?", (f'%{part}%',))
            results = cursor.fetchall()
            print(f"Database query results for part '{part}' of term '{term}': {results}")
            # Add each result to the set to ensure uniqueness
            recommendations.update(results)
    
    conn.close()

    # Convert the set back to a list for ranking and rendering
    recommendations = list(recommendations)
    
    # Rank the matches based on relevance
    ranked_recommendations = rank_matches(recommendations, expanded_terms)
    print(f"Ranked recommendations: {ranked_recommendations}")

    return render_template('results.html', record_text=record_text, recommendations=ranked_recommendations)


if __name__ == '__main__':
    app.run(debug=True)
