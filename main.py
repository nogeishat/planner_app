from datetime import datetime
from uuid import uuid4

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock

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

    Widget:
        size_hint_x: None
        width: 16 if root.is_subtask else 0

    ToggleButton:
        size_hint: None, None
        size: (18, 18) if root.is_subtask else (24, 24)
        state: "down" if root.done else "normal"
        pos_hint: {"center_y": 0.5}
        text: ""
        background_normal: ""
        background_down: ""
        background_color: [1, 1, 1, 1] if self.state == "down" else [0, 0, 0, 0]
        on_state: root.toggle_done(self.state == "down")
        canvas.before:
            Color:
                rgba: [33/255, 33/255, 33/255, 1] if not root.is_subtask else [0, 0, 0, 0]
            Line:
                width: 1.3
                rectangle: self.x, self.y, self.width, self.height

    Label:
        text: root.display_text
        markup: True
        font_size: "16sp" if root.is_subtask else "20sp"
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

    BoxLayout:
        size_hint_y: None
        height: 32
        spacing: 6
        padding: [8, 0, 8, 0]
        opacity: 1 if (root.column_key == "list_1" and root.filter_mode == "all") else 0
        disabled: not (root.column_key == "list_1" and root.filter_mode == "all")

        Button:
            text: "<"
            size_hint_x: None
            width: 34
            background_normal: ""
            background_down: ""
            background_color: [0, 0, 0, 0.2]
            color: [1, 1, 1, 1]
            on_press: root.change_weekday(-1)

        Label:
            text: "[b]" + root.WEEKDAYS[root.selected_weekday] + "[/b]"
            markup: True
            color: [1, 1, 1, 1]
            font_size: "16sp"
            halign: "center"
            valign: "middle"
            text_size: self.size

        Button:
            text: ">"
            size_hint_x: None
            width: 34
            background_normal: ""
            background_down: ""
            background_color: [0, 0, 0, 0.2]
            color: [1, 1, 1, 1]
            on_press: root.change_weekday(1)

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
            background_color: [24/255, 24/255, 24/255, 1] if root.current_view == "today" else [33/255, 33/255, 33/255, 1]
            color: [1, 1, 1, 1]
            font_size: "18sp"
            on_press: root.show_today()

        Button:
            text: "All"
            background_normal: ""
            background_down: ""
            background_color: [24/255, 24/255, 24/255, 1] if root.current_view == "all" else [33/255, 33/255, 33/255, 1]
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
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    title = StringProperty("")
    column_key = StringProperty("")
    filter_mode = StringProperty("today")
    toggle_mode = StringProperty("done")
    bg_color = ListProperty([0.15, 0.15, 0.18, 1])
    selected_weekday = NumericProperty(datetime.now().weekday())

    def on_kv_post(self, base_widget):
        self.refresh_tasks()

    @property
    def is_weekly_column(self):
        return self.column_key == "list_1"

    def get_active_weekday(self):
        if not self.is_weekly_column:
            return None
        if self.filter_mode == "today":
            return datetime.now().weekday()
        return self.selected_weekday

    def change_weekday(self, delta):
        self.selected_weekday = (self.selected_weekday + delta) % 7
        self.refresh_tasks()

    def add_task(self, text, category="", due_date="", subtasks_text=""):
        text = text.strip()
        if not text:
            return
        category = category.strip()
        due_date = due_date.strip()
        subtasks = [line.strip() for line in subtasks_text.splitlines() if line.strip()]

        conn = get_connection()
        cur = conn.cursor()

        main_task_id = str(uuid4())
        weekday = self.get_active_weekday()

        cur.execute(
            "INSERT INTO tasks (id, title, category, due_date, parent_id, column_name, done, in_today, weekday, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                main_task_id,
                text,
                category if category else None,
                due_date if due_date else None,
                None,
                self.column_key,
                0,
                1 if self.filter_mode == "today" else 0,
                weekday,
                datetime.utcnow().isoformat()
            )
        )
        for subtask in subtasks:
            cur.execute(
                "INSERT INTO tasks (id, title, category, due_date, parent_id, column_name, done, in_today, weekday, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid4()),
                    subtask,
                    None,
                    None,
                    main_task_id,
                    self.column_key,
                    0,
                    1 if self.filter_mode == "today" else 0,
                    weekday,
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

    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
        spacing: 10

        TextInput:
            id: popup_task_input
            hint_text: "Add task"
            multiline: False
            size_hint_y: None
            height: 40

        Spinner:
            id: popup_category
            text: "No category"
            values: ("No category", "Work", "Personal", "Errand", "Study")
            size_hint_y: None
            height: 40

        TextInput:
            id: popup_due_date
            hint_text: "Due date (optional, YYYY-MM-DD)"
            multiline: False
            size_hint_y: None
            height: 40

        TextInput:
            id: popup_subtasks
            hint_text: "Subtasks (optional, one per line)"
            multiline: True
            size_hint_y: None
            height: 110

        Button:
            text: "Add task"
            size_hint_y: None
            height: 40
            on_press: app.submit_popup_task(root.ids.popup_task_input.text, root.ids.popup_category.text, root.ids.popup_due_date.text, root.ids.popup_subtasks.text)

    Widget:
        size_hint_y: 1
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
        weekday = self.get_active_weekday()
        weekday_filter = " AND (weekday = ? OR weekday IS NULL)" if weekday is not None else ""
        weekday_params = (weekday,) if weekday is not None else ()

        if self.filter_mode == "today":
            parent_rows = cur.execute(
                f"SELECT id, title, category, due_date, done, in_today FROM tasks WHERE column_name = ? AND in_today = 1 AND parent_id IS NULL{weekday_filter} ORDER BY rowid DESC",
                (self.column_key,) + weekday_params
            ).fetchall()
            sub_rows = cur.execute(
                f"SELECT id, title, parent_id, done, in_today FROM tasks WHERE column_name = ? AND in_today = 1 AND parent_id IS NOT NULL{weekday_filter} ORDER BY rowid ASC",
                (self.column_key,) + weekday_params
            ).fetchall()
        else:
            parent_rows = cur.execute(
                f"SELECT id, title, category, due_date, done, in_today FROM tasks WHERE column_name = ? AND parent_id IS NULL{weekday_filter} ORDER BY rowid DESC",
                (self.column_key,) + weekday_params
            ).fetchall()
            sub_rows = cur.execute(
                f"SELECT id, title, parent_id, done, in_today FROM tasks WHERE column_name = ? AND parent_id IS NOT NULL{weekday_filter} ORDER BY rowid ASC",
                (self.column_key,) + weekday_params
            ).fetchall()

        conn.close()
        tasks_box = self.ids.tasks_box
        tasks_box.clear_widgets()

        subtasks_by_parent = {}
        for task_id, title, parent_id, done, in_today in sub_rows:
            subtasks_by_parent.setdefault(parent_id, []).append(
                (task_id, title, done, in_today)
            )

        if not parent_rows:
            tasks_box.add_widget(TaskRow.empty_state())
        else:
            for task_id, title, category, due_date, done, in_today in parent_rows:
                tasks_box.add_widget(
                    TaskRow(
                        column=self,
                        task_id=task_id,
                        title=title,
                        category=category or "",
                        due_date=due_date or "",
                        done=bool(done) if self.toggle_mode == "done" else bool(in_today),
                        toggle_mode=self.toggle_mode,
                    )
                )
                for subtask_id, subtask_title, subtask_done, subtask_in_today in subtasks_by_parent.get(task_id, []):
                    tasks_box.add_widget(
                        TaskRow(
                            column=self,
                            task_id=subtask_id,
                            title=subtask_title,
                            done=bool(subtask_done) if self.toggle_mode == "done" else bool(subtask_in_today),
                            toggle_mode=self.toggle_mode,
                            is_subtask=True,
                        )
                    )


class TaskRow(BoxLayout):
    task_id = StringProperty("")
    title = StringProperty("")
    category = StringProperty("")
    due_date = StringProperty("")
    done = BooleanProperty(False)
    is_subtask = BooleanProperty(False)
    toggle_mode = StringProperty("standard")
    hovered = BooleanProperty(False)

    def __init__(self, column=None, **kwargs):
        self.column = column
        super().__init__(**kwargs)
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
        details = []
        if self.category:
            details.append(self.category)
        if self.due_date:
            details.append(self.due_date)
        suffix = f" [size=14sp]({' | '.join(details)})[/size]" if details else ""
        text = f"[b]{self.title}[/b]{suffix}"
        if self.done and self.column and self.column.filter_mode == "today":
            return f"[color=#212121][s]{text}[/s][/color]"
        return text

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
        cur.execute("DELETE FROM tasks WHERE id = ? OR parent_id = ?", (self.task_id, self.task_id))
        conn.commit()
        conn.close()
        app = App.get_running_app()
        if app:
            app.refresh_all_columns()


class PlannerRoot(BoxLayout):
    current_view = StringProperty("today")

    def on_kv_post(self, base_widget):
        app = App.get_running_app()
        if app:
            app.refresh_columns_for_view("today")
            app.refresh_columns_for_view("all")

    def show_today(self):
        self.current_view = "today"
        self.ids.view_manager.current = "today"
        app = App.get_running_app()
        if app:
            app.refresh_columns_for_view("today")

    def show_all(self):
        self.current_view = "all"
        self.ids.view_manager.current = "all"
        app = App.get_running_app()
        if app:
            app.refresh_columns_for_view("all")


class PlannerApp(App):
    current_column = None
    current_popup = None

    def build(self):
        init_db()
        Builder.load_string(KV)
        return PlannerRoot()

    def submit_popup_task(self, text, category, due_date, subtasks_text):
        if not self.current_column:
            return

        normalized_category = "" if category == "No category" else category
        self.current_column.add_task(text, normalized_category, due_date, subtasks_text)
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None

    def refresh_all_columns(self):
        if not self.root:
            return

        # Refresh on the next UI frame so both screens stay in sync immediately
        # after DB updates, regardless of which screen triggered the change.
        Clock.schedule_once(lambda *_: self._refresh_columns(), 0)

    def _refresh_columns(self, view_name=None):
        if not self.root:
            return

        for widget in self.root.walk():
            if isinstance(widget, ToDoColumn) and (view_name is None or widget.filter_mode == view_name):
                widget.refresh_tasks()

    def refresh_columns_for_view(self, view_name):
        self._refresh_columns(view_name=view_name)


if __name__ == "__main__":
    PlannerApp().run()
