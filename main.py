from uuid import uuid4

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from database import init_db, get_connection


KV = """
<TaskRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: 44
    spacing: 8
    padding: [8, 4, 8, 4]

    canvas.before:
        Color:
            rgba: [1, 1, 1, 0.08] if root.hovered else [0, 0, 0, 0]
        Rectangle:
            pos: self.pos
            size: self.size

    ToggleButton:
        size_hint: None, None
        size: 24, 24
        state: "down" if root.done else "normal"
        pos_hint: {"center_y": 0.5}
        text: ""
        background_normal: ""
        background_down: ""
        background_color: [1, 1, 1, 1] if self.state == "down" else [0, 0, 0, 0]
        on_state: root.toggle_done(self.state == "down")
        canvas.before:
            Color:
                rgba: [1, 1, 1, 1]
            Line:
                width: 1.3
                rectangle: self.x, self.y, self.width, self.height

    Label:
        text: root.display_text
        markup: True
        font_size: "20sp"
        font_name: "Roboto"
        text_size: self.width, None
        halign: "left"
        valign: "middle"

    Button:
        text: "[b]X[/b]"
        markup: True
        font_size: "20sp"
        size_hint_x: None
        width: 20
        opacity: 1 if root.hovered else 0
        disabled: not root.hovered
        background_normal: ""
        background_down: ""
        background_color: [0, 0, 0, 0]
        color: [0.9, 0.15, 0.15, 1]
        on_press: root.delete_task()

<ToDoColumn>:
    orientation: "vertical"
    spacing: 8
    padding: [0, 8, 0, 0]
    size_hint_x: 1

    canvas.before:
        Color:
            rgba: root.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        size_hint_y: None
        height: 28
        text: f"[b]{root.title}[/b]" if root.title else ""
        markup: True
        color: [1, 1, 1, 1]
        font_size: "16sp"

    BoxLayout:
        id: tasks_box
        orientation: "vertical"
        spacing: 2
        size_hint_y: None
        height: self.minimum_height

    Button:
        text: ""
        size_hint_y: 1
        background_normal: ""
        background_down: ""
        background_color: [0, 0, 0, 0]
        color: [0, 0, 0, 0]
        on_press: root.open_add_task_page()

<PlannerRoot>:
    orientation: "vertical"
    spacing: 0
    padding: 0

    BoxLayout:
        size_hint_y: None
        height: 48
        canvas.after:
            Color:
                rgba: [1, 1, 1, 1]
            Line:
                width: 1.2
                points: self.x, self.y, self.right, self.y
            Line:
                width: 1.2
                points: self.center_x, self.y, self.center_x, self.top

        Button:
            text: "Today"
            background_normal: ""
            background_down: ""
            background_color: [1, 1, 1, 0.14] if root.current_view == "today" else [0, 0, 0, 0]
            color: [1, 1, 1, 1]
            font_size: "18sp"
            on_press: root.show_today()

        Button:
            text: "All"
            background_normal: ""
            background_down: ""
            background_color: [1, 1, 1, 0.14] if root.current_view == "all" else [0, 0, 0, 0]
            color: [1, 1, 1, 1]
            font_size: "18sp"
            on_press: root.show_all()

    ScreenManager:
        id: view_manager

        Screen:
            name: "today"

            BoxLayout:
                orientation: "horizontal"
                spacing: 0
                padding: 0

                ToDoColumn:
                    title: "List 1"
                    column_key: "list_1"
                    filter_mode: "today"
                    toggle_mode: "done"
                    bg_color: [243/255, 154/255, 39/255, 1]

                ToDoColumn:
                    title: "List 2"
                    column_key: "list_2"
                    filter_mode: "today"
                    toggle_mode: "done"
                    bg_color: [151/255, 110/255, 215/255, 1]

                ToDoColumn:
                    title: "List 3"
                    column_key: "list_3"
                    filter_mode: "today"
                    toggle_mode: "done"
                    bg_color: [194/255, 59/255, 35/255, 1]

        Screen:
            name: "all"

            BoxLayout:
                orientation: "horizontal"
                spacing: 0
                padding: 0

                ToDoColumn:
                    title: "List 1"
                    column_key: "list_1"
                    filter_mode: "all"
                    toggle_mode: "in_today"
                    bg_color: [243/255, 154/255, 39/255, 1]

                ToDoColumn:
                    title: "List 2"
                    column_key: "list_2"
                    filter_mode: "all"
                    toggle_mode: "in_today"
                    bg_color: [151/255, 110/255, 215/255, 1]

                ToDoColumn:
                    title: "List 3"
                    column_key: "list_3"
                    filter_mode: "all"
                    toggle_mode: "in_today"
                    bg_color: [194/255, 59/255, 35/255, 1]
"""


class ToDoColumn(BoxLayout):
    title = StringProperty("")
    column_key = StringProperty("")
    filter_mode = StringProperty("today")
    toggle_mode = StringProperty("done")
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
            "INSERT INTO tasks (id, title, column_name, done, in_today, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                text,
                self.column_key,
                0,
                1 if self.filter_mode == "today" else 0,
                datetime.utcnow().isoformat()
            )
        )

        conn.commit()
        conn.close()

        app = App.get_running_app()
        if app:
            app.refresh_all_columns()

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

        if self.filter_mode == "today":
            rows = cur.execute(
                "SELECT id, title, done, in_today FROM tasks WHERE column_name = ? AND in_today = 1 ORDER BY rowid DESC",
                (self.column_key,)
            ).fetchall()
        else:
            rows = cur.execute(
                "SELECT id, title, done, in_today FROM tasks WHERE column_name = ? ORDER BY rowid DESC",
                (self.column_key,)
            ).fetchall()

        conn.close()
        tasks_box = self.ids.tasks_box
        tasks_box.clear_widgets()

        if not rows:
            tasks_box.add_widget(TaskRow.empty_state())
        else:
            for task_id, title, done, in_today in rows:
                tasks_box.add_widget(
                    TaskRow(
                        column=self,
                        task_id=task_id,
                        title=title,
                        done=bool(done) if self.toggle_mode == "done" else bool(in_today),
                        toggle_mode=self.toggle_mode,
                    )
                )


class TaskRow(BoxLayout):
    task_id = StringProperty("")
    title = StringProperty("")
    done = BooleanProperty(False)
    toggle_mode = StringProperty("standard")
    hovered = BooleanProperty(False)

    def __init__(self, column=None, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        Window.bind(mouse_pos=self._on_mouse_pos)

    @staticmethod
    def empty_state():
        row = TaskRow(title="No tasks yet.", done=False)
        row.disabled = True
        return row

    @property
    def display_text(self):
        if self.title == "No tasks yet.":
            return f"[b]{self.title}[/b]"
        return f"[b]{self.title}[/b]"

    def _on_mouse_pos(self, _, pos):
        if not self.get_root_window():
            return
        self.hovered = self.collide_point(*self.to_widget(*pos))

    def toggle_done(self, value):
        if not self.task_id:
            return
        conn = get_connection()
        cur = conn.cursor()
        if self.toggle_mode == "in_today":
            cur.execute("UPDATE tasks SET in_today = ? WHERE id = ?", (1 if value else 0, self.task_id))
        else:
            cur.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if value else 0, self.task_id))
        conn.commit()
        conn.close()
        self.done = value
        app = App.get_running_app()
        if app:
            app.refresh_all_columns()

    def delete_task(self):
        if not self.task_id:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
        conn.commit()
        conn.close()
        app = App.get_running_app()
        if app:
            app.refresh_all_columns()


class PlannerRoot(BoxLayout):
    current_view = StringProperty("today")

    def show_today(self):
        self.current_view = "today"
        self.ids.view_manager.current = "today"

    def show_all(self):
        self.current_view = "all"
        self.ids.view_manager.current = "all"


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

    def refresh_all_columns(self):
        if not self.root:
            return
        for widget in self.root.walk():
            if isinstance(widget, ToDoColumn):
                widget.refresh_tasks()


if __name__ == "__main__":
    PlannerApp().run()
