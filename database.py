import sqlite3
from datetime import datetime
import csv
import os

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'teacher'))
        )
    ''')

    # Students
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        class_name TEXT NOT NULL
    )
''')


    # Classes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL
        )
    ''')

    # Teacher-Class mapping
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_classes (
            teacher_id INTEGER,
            class_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    ''')

    # Attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    # Ensure default admin user exists
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', 'admin123', 'admin'))

    conn.commit()
    conn.close()

def verify_user(username, password, role):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
    user = cursor.fetchone()
    conn.close()
    return user

def add_teacher(name, username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'teacher')", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# def add_student(name, student_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO students (name, student_id) VALUES (?, ?)", (name, student_id))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()

def add_student(name, class_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Generate a unique student_id using name and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    student_id = f"{name.lower().replace(' ', '_')}_{timestamp}"

    try:
        # Insert into students table with class_name
        cursor.execute("INSERT INTO students (name, student_id, class_name) VALUES (?, ?, ?)", 
                       (name, student_id, class_name))

        # Ensure class exists in 'classes' table
        cursor.execute("SELECT id FROM classes WHERE class_name = ?", (class_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()



# def get_teachers():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, username FROM users WHERE role='teacher'")
#     teachers = cursor.fetchall()
#     conn.close()
#     return teachers

def get_teachers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE role='teacher'")
    teachers = cursor.fetchall()
    conn.close()
    return [dict(id=row[0], username=row[1], password=row[2]) for row in teachers]


def assign_class(teacher_username, class_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ? AND role = 'teacher'", (teacher_username,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    teacher_id = result[0]

    cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))
    class_id = cursor.lastrowid
    cursor.execute("INSERT INTO teacher_classes (teacher_id, class_id) VALUES (?, ?)", (teacher_id, class_id))

    conn.commit()
    conn.close()
    return True

def get_teacher_classes(teacher_username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND role='teacher'", (teacher_username,))
    teacher = cursor.fetchone()
    if not teacher:
        return []
    teacher_id = teacher[0]

    cursor.execute("""
        SELECT classes.class_name 
        FROM classes
        JOIN teacher_classes ON teacher_classes.class_id = classes.id
        WHERE teacher_classes.teacher_id = ?
    """, (teacher_id,))
    classes = cursor.fetchall()
    conn.close()
    return [c[0] for c in classes]

def get_teachers_with_classes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.password, GROUP_CONCAT(c.class_name, ', ') as classes
        FROM users u
        LEFT JOIN teacher_classes tc ON u.id = tc.teacher_id
        LEFT JOIN classes c ON tc.class_id = c.id
        WHERE u.role = 'teacher'
        GROUP BY u.id
    ''')
    results = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "username": row[1], "password": row[2], "classes": row[3] if row[3] else "None"}
        for row in results
    ]

def mark_attendance(student_name, class_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_name = ? AND class_name = ? AND DATE(timestamp) = DATE('now')",
                   (student_name, class_name))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO attendance (student_name, class_name, timestamp) VALUES (?, ?, ?)",
                   (student_name, class_name, timestamp))
    conn.commit()
    conn.close()
    return True

def get_students():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, student_id, class_name FROM students")
    students = cursor.fetchall()
    conn.close()
    return [dict(id=row[0], name=row[1], student_id=row[2], class_name=row[3]) for row in students]


def delete_teacher(teacher_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def get_attendance_records(teacher_username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attendance.student_name, attendance.class_name, attendance.timestamp 
        FROM attendance
        JOIN classes ON attendance.class_name = classes.class_name
        JOIN teacher_classes ON teacher_classes.class_id = classes.id
        JOIN users ON teacher_classes.teacher_id = users.id
        WHERE users.username = ?
    """, (teacher_username,))
    records = cursor.fetchall()
    conn.close()

    csv_file = f"attendance_{teacher_username}.csv"
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Student Name", "Class", "Timestamp"])
        writer.writerows(records)
    return csv_file
