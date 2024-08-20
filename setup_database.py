import sqlite3

def create_tables():
    # Connect to the database (it will create the file if it doesn't exist)
    conn = sqlite3.connect('medical_records.db')
    cursor = conn.cursor()

    # Drop the billing_codes table if it exists
    cursor.execute('DROP TABLE IF EXISTS billing_codes')

    # Create billing_codes table
    cursor.execute('''
    CREATE TABLE billing_codes (
        code_id INTEGER PRIMARY KEY,
        icd_code TEXT,
        description TEXT
    )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database setup completed successfully.")

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
    insert_sample_billing_codes()
