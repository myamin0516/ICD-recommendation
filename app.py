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

# Define a synonyms dictionary with expanded coverage
synonyms = {
    "diabetes": ["diabetes", "sugar", "glucose", "high sugar"],
    "hypertension": ["hypertension", "high blood pressure", "elevated blood pressure", "angina"],
    "chest pain": ["chest pain", "angina", "discomfort in chest"],
    "fractured femur": ["fractured femur", "broken leg", "broken thigh"],
    "chronic obstructive pulmonary disease": ["COPD", "chronic obstructive pulmonary disease", "emphysema"],
    "otitis media": ["otitis media", "ear infection", "middle ear infection"]
}

def get_synonym_matches(text):
    """Expand the input text with synonyms using fuzzy matching."""
    expanded_terms = set()
    doc = nlp(text.lower())
    for token in doc:
        for key, syns in synonyms.items():
            if fuzz.ratio(token.text, key) > 65:  # Match to the key directly
                expanded_terms.add(key)
            elif any(fuzz.ratio(token.text, syn) > 55 for syn in syns):
                expanded_terms.add(key)
    return expanded_terms

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    record_text = request.form['record_text']
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
        cursor.execute("SELECT icd_code, description FROM billing_codes WHERE description LIKE ?", (f'%{term}%',))  # Using f-string for clarity
        recommendations.extend(cursor.fetchall())
    conn.close()

    return render_template('results.html', record_text=record_text, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)