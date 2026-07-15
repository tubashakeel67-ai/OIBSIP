"""
database.py
SQLite logic — create table, save records, fetch history.
"""
import sqlite3
from datetime import datetime


def init_db():
    conn = None
    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                weight REAL,
                height REAL,
                bmi REAL,
                category TEXT,
                date TEXT
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database init error: {e}")
    finally:
        if conn:
            conn.close()


def save_record(name, weight, height, bmi, category):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = None
    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO records (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, weight, height, bmi, category, date))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database save error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_user_history(name):
    conn = None
    try:
        conn = sqlite3.connect("bmi_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM records WHERE name = ? ORDER BY date
        """, (name,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database fetch error: {e}")
        return []
    finally:
        if conn:
            conn.close()
