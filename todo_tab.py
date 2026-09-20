import customtkinter as ctk
from datetime import datetime

class TodoTab(ctk.CTkFrame):
    def __init__(self, master, on_change_callback=None):
        super().__init__(master)

        self.on_change_callback = on_change_callback
        self.now = datetime.now()
        self.todo_items = []

        self.setup_ui()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        date_str = self.now.strftime("%Y年%m月%d日")
        self.todo_date_label = ctk.CTkLabel(
            header_frame, 
            text=f"🗓 今日の日付: {date_str}", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.todo_date_label.pack(side="left", padx=15, pady=10)

        self.todo_count_label = ctk.CTkLabel(
            header_frame, 
            text="残りのタスク: 0個", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFCC00"
        )
        self.todo_count_label.pack(side="right", padx=15, pady=10)

        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.todo_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="今日やるべきタスクを入力...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.priority_opt = ctk.CTkOptionMenu(
            input_frame,
            values=["高", "中", "低"],
            width=70,
            height=40
        )
        self.priority_opt.set("中")
        self.priority_opt.pack(side="left", padx=5, pady=10)

        add_btn = ctk.CTkButton(
            input_frame, 
            text="タスク追加", 
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.add_todo_item
        )
        add_btn.pack(side="right", padx=(5, 10), pady=10)

        self.todo_scroll = ctk.CTkScrollableFrame(
            self, 
            label_text="TODAY'S TASKS",
            label_font=ctk.CTkFont(size=14, weight="bold")
        )
        self.todo_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def add_todo_item(self, text=None, priority=None, is_done=False):
        if text is None:
            text = self.todo_entry.get().strip()
            if not text:
                return
            priority = self.priority_opt.get()

        priority_colors = {"高": "#FF5555", "中": "#FFB86C", "低": "#8BE9FD"}

        item_frame = ctk.CTkFrame(self.todo_scroll)
        item_frame.pack(fill="x", pady=5, padx=5)

        p_label = ctk.CTkLabel(
            item_frame, 
            text=f"[{priority}]", 
            text_color=priority_colors.get(priority, "white"),
            font=ctk.CTkFont(weight="bold"),
            width=40
        )
        p_label.pack(side="left", padx=(10, 0))

        var = ctk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            item_frame, 
            text=text,
            variable=var,
            font=ctk.CTkFont(size=14),
            command=self.on_item_changed
        )
        chk.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        data_obj = {
            "frame": item_frame, 
            "var": var, 
            "text": text, 
            "priority": priority
        }

        del_btn = ctk.CTkButton(
            item_frame, 
            text="削除", 
            width=50,
            fg_color="#FF5555", 
            hover_color="#CC0000",
            command=lambda: self.remove_todo_item(item_frame, data_obj)
        )
        del_btn.pack(side="right", padx=10, pady=10)

        self.todo_items.append(data_obj)
        self.todo_entry.delete(0, 'end')
        self.update_todo_count()
        self.notify_change()

    def remove_todo_item(self, frame, data_obj):
        frame.destroy()
        if data_obj in self.todo_items:
            self.todo_items.remove(data_obj)
        self.update_todo_count()
        self.notify_change()

    def on_item_changed(self):
        self.update_todo_count()
        self.notify_change()

    def update_todo_count(self):
        remaining = sum(1 for item in self.todo_items if not item["var"].get())
        self.todo_count_label.configure(text=f"残りのタスク: {remaining}個")

    def notify_change(self):
        """変更時に親（main.py）へ保存を通知"""
        if self.on_change_callback:
            self.on_change_callback()

    # --- 一括保存用の共通インターフェース ---
    def get_data(self):
        """現在のTo Doデータをリスト形式で返す"""
        return [
            {
                "text": item["text"],
                "priority": item["priority"],
                "is_done": item["var"].get()
            }
            for item in self.todo_items
        ]

    def set_data(self, data_list):
        """保存データを受け取って画面に復元"""
        for item_data in data_list:
            self.add_todo_item(
                text=item_data.get("text", ""),
                priority=item_data.get("priority", "中"),
                is_done=item_data.get("is_done", False)
            )