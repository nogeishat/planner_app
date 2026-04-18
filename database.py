import sqlite3

DB_NAME = "planner.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            due_date TEXT,
            parent_id TEXT,
            column_name TEXT,
            done INTEGER,
            in_today INTEGER DEFAULT 0,
            weekday INTEGER,
            updated_at TEXT
        )
    """)

    columns = [row[1] for row in cur.execute("PRAGMA table_info(tasks)").fetchall()]
    if "in_today" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN in_today INTEGER DEFAULT 0")
    if "category" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN category TEXT")
    if "due_date" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
    if "parent_id" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN parent_id TEXT")
    if "weekday" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN weekday INTEGER")

    conn.commit()
    conn.close()
