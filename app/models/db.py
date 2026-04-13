import sqlite3
from datetime import datetime
import json
import os

DB_PATH = 'database.db'

def get_db_connection():
    # Make sure we're in the right directory or use an absolute path depending on runtime.
    # We will assume a flat run from the root.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    # Create Attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def add_user(name, embedding_vector):
    embedding_str = json.dumps(embedding_vector.tolist())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (name, embedding) VALUES (?, ?)', (name, embedding_str))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return user_id

def mark_attendance(user_id):
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if already marked today
    c.execute('SELECT id FROM attendance WHERE user_id = ? AND date = ?', (user_id, date_str))
    existing = c.fetchone()
    if existing:
        conn.close()
        return False # Already marked
        
    c.execute('INSERT INTO attendance (user_id, date, time) VALUES (?, ?, ?)', (user_id, date_str, time_str))
    conn.commit()
    conn.close()
    return True

def get_attendance_records():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT users.name, attendance.date, attendance.time 
        FROM attendance 
        JOIN users ON attendance.user_id = users.id 
        ORDER BY attendance.date DESC, attendance.time DESC
    ''')
    records = c.fetchall()
    conn.close()
    return records
