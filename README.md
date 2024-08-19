Project Overview

This project provides a web application to recommend billing codes based on a user-entered medical record text. It leverages Natural Language Processing (NLP) techniques to extract relevant keywords and utilizes a pre-populated SQLite database containing billing code information.

Features

Accepts user input for a medical record text.
Analyzes the text using SpaCy NLP to identify key medical terms.
Expands identified terms with synonyms for broader coverage.
Queries a database of billing codes based on extracted and expanded terms.
Presents a list of recommended billing codes with their descriptions.
Allows users to return to the main page for entering a new record.
Technology Stack

Flask (web framework)
SpaCy (NLP library)
FuzzyWuzzy (fuzzy string matching)
SQLite (database)
