import sqlite3

def create_tables():
    # Connect to the database (it will create the file if it doesn't exist)
    conn = sqlite3.connect('medical_records.db')
    cursor = conn.cursor()

    # Create medical_records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_records (
        record_id INTEGER PRIMARY KEY,
        record_text TEXT
    )
    ''')

    # Create billing_codes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billing_codes (
        code_id INTEGER PRIMARY KEY,
        icd_code TEXT,
        description TEXT
    )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database setup completed successfully.")

def insert_sample_medical_records():
    # Connect to the database
    conn = sqlite3.connect('medical_records.db')
    cursor = conn.cursor()

    # Insert sample medical records
    sample_records = [
        ("Patient has a history of diabetes and hypertension. Complains of chest pain."),
        ("Patient presents with a fractured femur after a car accident."),
        ("Routine check-up. Patient is in good health with no significant issues."),
        ("Patient diagnosed with chronic obstructive pulmonary disease (COPD)."),
        ("Child presents with symptoms of otitis media, including ear pain and fever.")
    ]

    cursor.executemany('INSERT INTO medical_records (record_text) VALUES (?)', [(record,) for record in sample_records])

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Sample medical records inserted successfully.")

def insert_sample_billing_codes():
    # Connect to the database
    conn = sqlite3.connect('medical_records.db')
    cursor = conn.cursor()

    # Insert sample billing codes
    sample_codes = [
        ("E11", "Type 2 diabetes mellitus"),
        ("I10", "Essential (primary) hypertension"),
        ("S72.3", "Fracture of femur"),
        ("J44", "Chronic obstructive pulmonary disease"),
        ("H66.9", "Otitis media, unspecified")
    ]

    cursor.executemany('INSERT INTO billing_codes (icd_code, description) VALUES (?, ?)', sample_codes)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Sample billing codes inserted successfully.")

if __name__ == "__main__":
    # Step 1: Set up the database and create the tables
    create_tables()

    # Step 2: Populate the tables with sample data
    insert_sample_medical_records()
    insert_sample_billing_codes()
