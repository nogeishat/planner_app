from supabase_client import supabase
from database import get_connection


def push_to_supabase():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM tasks").fetchall()

    for row in rows:
        supabase.table("tasks").upsert({
            "id": row[0],
            "title": row[1],
            "column_name": row[2],
            "done": bool(row[3]),
            "updated_at": row[4]
        }).execute()

    conn.close()


def pull_from_supabase():
    response = supabase.table("tasks").select("*").execute()

    conn = get_connection()
    cur = conn.cursor()

    for row in response.data:
        cur.execute("""
        INSERT OR REPLACE INTO tasks (id, title, column_name, done, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["title"],
            row["column_name"],
            int(row["done"]),
            row["updated_at"]
        ))

    conn.commit()
    conn.close()