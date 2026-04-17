import sqlite3

DB_NAME = "planner.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()  # <-- THIS WAS MISSING

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            column_name TEXT,
            done INTEGER,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()