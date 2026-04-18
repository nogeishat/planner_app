from uuid import uuid4

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from database import init_db, get_connection


KV = """
<ToDoColumn>:
    orientation: "vertical"
    spacing: 8
    padding: 0
    size_hint_x: 1

    canvas.before:
        Color:
            rgba: root.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        id: task_output
        text: root.tasks_text
        markup: False
        size_hint_y: None
        text_size: self.width, None
        halign: "left"
        valign: "top"
        height: self.texture_size[1]

    Button:
        text: ""
        size_hint_y: 1
        background_normal: ""
        background_down: ""
        background_color: [0, 0, 0, 0]
        color: [0, 0, 0, 0]
        on_press: root.open_add_task_page()

<PlannerRoot>:
    orientation: "horizontal"
    spacing: 0
    padding: 0

    ToDoColumn:
        column_key: "list_1"
        bg_color: [243/255, 154/255, 39/255, 1]

    ToDoColumn:
        column_key: "list_2"
        bg_color: [151/255, 110/255, 215/255, 1]

    ToDoColumn:
        column_key: "list_3"
        bg_color: [194/255, 59/255, 35/255, 1]
"""


class ToDoColumn(BoxLayout):
    column_key = StringProperty("")
    tasks_text = StringProperty("No tasks yet.")
    bg_color = ListProperty([0.15, 0.15, 0.18, 1])

    def on_kv_post(self, base_widget):
        self.refresh_tasks()

    def add_task(self, text):
        text = text.strip()
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

        self.refresh_tasks()

    def open_add_task_page(self):
        app = App.get_running_app()
        app.current_column = self

        popup_content = Builder.load_string(
            """
BoxLayout:
    orientation: "vertical"
    spacing: 10
    padding: 12
    canvas.before:
        Color:
            rgba: app.current_column.bg_color if app.current_column else [0.15, 0.15, 0.18, 1]
        Rectangle:
            pos: self.pos
            size: self.size

    TextInput:
        id: popup_task_input
        hint_text: "Add task"
        multiline: False
        size_hint_y: None
        height: 40

    Button:
        text: "Add task"
        size_hint_y: None
        height: 40
        on_press: app.submit_popup_task(root.ids.popup_task_input.text)
"""
        )

        self._active_popup = Popup(
            title="",
            content=popup_content,
            size_hint=(1, 1),
            auto_dismiss=True,
            separator_height=0,
            background="",
        )
        app.current_popup = self._active_popup
        self._active_popup.open()

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
            self.tasks_text = "\n".join(
                f"[{'x' if row[1] else ' '}] {row[0]}" for row in rows
            )


class PlannerRoot(BoxLayout):
    pass


class PlannerApp(App):
    current_column = None
    current_popup = None

    def build(self):
        init_db()
        Builder.load_string(KV)
        return PlannerRoot()

    def submit_popup_task(self, text):
        if not self.current_column:
            return

        self.current_column.add_task(text)
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None


if __name__ == "__main__":
    PlannerApp().run()