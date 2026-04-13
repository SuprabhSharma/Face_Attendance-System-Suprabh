import pg8000.dbapi
from datetime import datetime
import json
import os
import urllib.parse

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL environment variable is not defined.")
    
    result = urllib.parse.urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:] if result.path else ""
    hostname = result.hostname
    port = result.port or 5432
    
    query = urllib.parse.parse_qs(result.query)
    sslmode = query.get('sslmode', [''])[0]
    
    kwargs = {
        "user": username,
        "password": password,
        "host": hostname,
        "port": port,
        "database": database
    }
    
    # If the database URL strictly requires SSL or is an external cloud network
    if sslmode == 'require' or (hostname and hostname != 'localhost' and hostname != '127.0.0.1'):
        import ssl
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ssl_ctx
        
    conn = pg8000.dbapi.connect(**kwargs)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    # Create Attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
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
    
    # Translate tuples list to list of dicts
    cols = [desc[0] for desc in c.description]
    users = [dict(zip(cols, row)) for row in c.fetchall()]
    
    conn.close()
    return users

def add_user(name, embedding_vector):
    embedding_str = json.dumps(embedding_vector.tolist())
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('INSERT INTO users (name, embedding) VALUES (%s, %s) RETURNING id', (name, embedding_str))
    user_id = c.fetchone()[0]
    
    conn.commit()
    conn.close()
    return user_id

def mark_attendance(user_id):
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if already marked today
    c.execute('SELECT id FROM attendance WHERE user_id = %s AND date = %s', (user_id, date_str))
    existing = c.fetchone()
    if existing:
        conn.close()
        return False # Already marked
        
    c.execute('INSERT INTO attendance (user_id, date, time) VALUES (%s, %s, %s)', (user_id, date_str, time_str))
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
    
    # Translate tuples list to list of dicts
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    
    conn.close()
    return records
