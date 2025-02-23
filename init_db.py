import sqlite3

def init_database():
    conn = sqlite3.connect('bloodbank_users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            hospital_name TEXT,
            donor_id TEXT
        )
    ''')
    
    # Create donors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            location TEXT NOT NULL,
            medical_report TEXT,
            last_donation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  # Ensure last_donation column is added
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create blood requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            quantity_ml INTEGER NOT NULL,
            hospital TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
