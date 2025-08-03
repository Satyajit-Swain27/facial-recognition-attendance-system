import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def mark_attendance(name):
    if check_attendance_marked(name):
        return False

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
    conn.commit()
    conn.close()
    return True

def check_attendance_marked(name):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM attendance 
        WHERE name = ? AND DATE(timestamp) = ?
    """, (name, today))
    record = cursor.fetchone()
    conn.close()
    return record is not None

