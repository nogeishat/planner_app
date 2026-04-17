import requests
from database import get_connection
from supabase_client import SUPABASE_URL, HEADERS


def push_to_supabase():
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, title, column_name, done, updated_at FROM tasks"
    ).fetchall()
    conn.close()

    url = f"{SUPABASE_URL}/rest/v1/tasks"

    for row in rows:
        payload = {
            "id": row[0],
            "title": row[1],
            "column_name": row[2],
            "done": bool(row[3]),
            "updated_at": row[4],
        }

        response = requests.post(
            url,
            headers={
                **HEADERS,
                "Prefer": "resolution=merge-duplicates"
            },
            json=payload,
            timeout=20,
        )
        response.raise_for_status()


def pull_from_supabase():
    url = f"{SUPABASE_URL}/rest/v1/tasks?select=*"

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    data = response.json()

    conn = get_connection()
    cur = conn.cursor()

    for row in data:
        cur.execute("""
            INSERT OR REPLACE INTO tasks
            (id, title, column_name, done, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["title"],
            row["column_name"],
            int(row["done"]),
            row["updated_at"],
        ))

    conn.commit()
    conn.close()