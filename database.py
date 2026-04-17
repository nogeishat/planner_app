import sqlite3

DB_NAME = "planner.db"

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    column_name TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    updated_at TEXT NOT NULL
)
""")

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS tasks")

    cur.execute("""
    CREATE TABLE tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        column_name TEXT NOT NULL,
        done INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()