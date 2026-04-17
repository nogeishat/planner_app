from uuid import uuid4

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from sync import push_to_supabase, pull_from_supabase

from database import init_db, get_connection


KV = """
<ToDoColumn>:
    orientation: "vertical"
    spacing: 8
    padding: 10
    size_hint_x: 1

    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.18, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

    Label:
        text: root.column_title
        size_hint_y: None
        height: 35
        bold: True
        font_size: 20

    TextInput:
        id: task_input
        hint_text: "Add task"
        multiline: False
        size_hint_y: None
        height: 40
        on_text_validate: root.add_task()

    Button:
        text: "Add"
        size_hint_y: None
        height: 40
        on_press: root.add_task()

    ScrollView:
        do_scroll_x: False

        Label:
            id: task_output
            text: root.tasks_text
            size_hint_y: None
            text_size: self.width, None
            halign: "left"
            valign: "top"
            height: self.texture_size[1]


<PlannerRoot>:
    BoxLayout:
    size_hint_y: None
    height: 50

    Button:
        text: "Sync"
        on_press: app.sync()
    
    orientation: "horizontal"
    spacing: 12
    padding: 12

    ToDoColumn:
        column_title: "To Do List 1"
        column_key: "list_1"

    ToDoColumn:
        column_title: "To Do List 2"
        column_key: "list_2"

    ToDoColumn:
        column_title: "To Do List 3"
        column_key: "list_3"
"""


class ToDoColumn(BoxLayout):
    column_title = StringProperty("")
    column_key = StringProperty("")
    tasks_text = StringProperty("No tasks yet.")

    def on_kv_post(self, base_widget):
        self.refresh_tasks()

    def add_task(self):
        text = self.ids.task_input.text.strip()
        if not text:
            return

        conn = get_connection()
        cur = conn.cursor()

        from datetime import datetime

        cur.execute(
            "INSERT INTO tasks (id, title, column_name, done, updated_at) VALUES (?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                text,
                self.column_key,
                0,
                datetime.utcnow().isoformat()
            )
        )

        conn.commit()
        conn.close()

        self.ids.task_input.text = ""
        self.refresh_tasks()

    def refresh_tasks(self):
        conn = get_connection()
        cur = conn.cursor()

        rows = cur.execute(
            "SELECT title, done FROM tasks WHERE column_name = ? ORDER BY rowid DESC",
            (self.column_key,)
        ).fetchall()

        conn.close()

        if not rows:
            self.tasks_text = "No tasks yet."
        else:
            self.tasks_text = "\\n".join(
                f"[{'x' if row[1] else ' '}] {row[0]}" for row in rows
            )


class PlannerRoot(BoxLayout):
    pass


class PlannerApp(App):
    def sync(self):
        push_to_supabase()
        pull_from_supabase()

        if self.root:
            for child in self.root.children:
                if hasattr(child, "refresh_tasks"):
                    child.refresh_tasks()

    def build(self):
        init_db()
        Builder.load_string(KV)
        return PlannerRoot()


if __name__ == "__main__":
    PlannerApp().run()
