import sqlite3
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
            hospital_name TEXT
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
            quantity_ml INTEGER,
            hospital TEXT NOT NULL,
            last_donation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

    admin_username = "admin1"
    admin_password = hash_password("admin123")
    admin_email = "admin@bloodbank.com"
    
    cursor.execute('SELECT username FROM users WHERE username = ?', (admin_username,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, password, email, role, hospital_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_username, admin_password, admin_email, "admin", None))
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
    
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
