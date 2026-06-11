import sqlite3
import datetime

DB_FILE = "study_helper.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            topic TEXT,
            score REAL,
            max_score REAL,
            date_taken TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
    conn.close()
    return username

def save_quiz_score(username, subject, topic, score, max_score):
    conn = get_connection()
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO quiz_scores (username, subject, topic, score, max_score, date_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, subject, topic, score, max_score, date_str))
    conn.commit()
    conn.close()

def get_user_progress(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT subject, topic, score, max_score, date_taken 
        FROM quiz_scores 
        WHERE username = ? 
        ORDER BY date_taken DESC
    ''', (username,))
    records = c.fetchall()
    conn.close()
    return records
