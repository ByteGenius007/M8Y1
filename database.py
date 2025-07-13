import sqlite3
from datetime import datetime

DB_NAME = 'data/professions.db'


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cursor = conn.cursor()

    # Таблица профессий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER NOT NULL,
            interests TEXT,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_profession(category, title, description):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO professions (category, title, description)
        VALUES (?, ?, ?)
    ''', (category, title, description))
    conn.commit()
    conn.close()


def get_professions_by_category(category):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, description FROM professions
        WHERE category = ?
    ''', (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_user(tg_id, interests):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (tg_id, interests, created_at)
        VALUES (?, ?, ?)
    ''', (tg_id, interests, datetime.now().isoformat()))
    conn.commit()
    conn.close()
