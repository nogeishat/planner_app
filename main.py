from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from database import init_db, get_connection
from uuid import uuid4

KV = """
BoxLayout:
    orientation: "vertical"
    padding: 10
    spacing: 10

    TextInput:
        id: input
        hint_text: "Enter task"
        multiline: False

    Button:
        text: "Add Task"
        size_hint_y: None
        height: 40
        on_press: app.add_task()

    Label:
        id: output
        text: app.tasks_text
"""

class PlannerApp(App):
    tasks_text = "No tasks yet"

    def build(self):
        init_db()
        return Builder.load_string(KV)

    def add_task(self):
        text = self.root.ids.input.text.strip()
        if not text:
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO tasks (id, title) VALUES (?, ?)",
            (str(uuid4()), text)
        )

        conn.commit()
        conn.close()

        self.root.ids.input.text = ""
        self.refresh_tasks()

    def refresh_tasks(self):
        conn = get_connection()
        cur = conn.cursor()

        rows = cur.execute("SELECT title FROM tasks").fetchall()
        conn.close()

        if not rows:
            self.tasks_text = "No tasks yet"
        else:
            self.tasks_text = "\n".join([r[0] for r in rows])

if __name__ == "__main__":
    PlannerApp().run()