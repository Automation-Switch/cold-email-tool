import sqlite3
from hashlib import sha256

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create the users table with id, username, email, and password_hash
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                  (username, email, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username or Email already exists!")
    conn.close()

if __name__ == '__main__':
    create_database()
    # Optionally add a test user
    add_user('testuser', 'test@example.com', 'password123')
