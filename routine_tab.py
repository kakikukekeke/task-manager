import tkinter as tk
import customtkinter as ctk
import calendar
from datetime import datetime

class RoutineTab(ctk.CTkScrollableFrame):
    def __init__(self, master, on_change_callback=None):
        super().__init__(master)

        self.on_change_callback = on_change_callback
        self.now = datetime.now()
        self.days_in_month = calendar.monthrange(self.now.year, self.now.month)[1]
        self.days = list(range(1, self.days_in_month + 1))

        self.default_routines = ["筋トレ", "読書 (20分)", "英語学習", "瞑想"]
        self.routine_entries = []
        self.checkbox_vars = {}
        self.daily_counts = {day: 0 for day in self.days}

        self.setup_ui()

    def setup_ui(self):
        # --- グラフエリア ---
        graph_frame = ctk.CTkFrame(self)
        graph_frame.pack(fill="x", padx=10, pady=10)

        graph_title = ctk.CTkLabel(
            graph_frame, 
            text=f"📊 {self.now.month}月の達成個数グラフ", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        graph_title.pack(anchor="w", padx=15, pady=(10, 0))

        self.canvas = tk.Canvas(
            graph_frame, height=180, bg="#1f1f1f", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.update_graph())

        # --- テーブルエリア ---
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        table_title = ctk.CTkLabel(
            table_frame, 
            text="📅 毎日のルーティーントラッカー", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        table_title.pack(anchor="w", padx=15, pady=10)

        table_scroll = ctk.CTkScrollableFrame(table_frame, orientation="horizontal", height=240)
        table_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ヘッダー
        header_task = ctk.CTkLabel(table_scroll, text="ルーティーン項目 (編集可)", font=ctk.CTkFont(weight="bold"), width=140)
        header_task.grid(row=0, column=0, padx=5, pady=5)

        for day in self.days:
            is_today = (day == self.now.day)
            color = "#1F6AA5" if is_today else "transparent"
            lbl = ctk.CTkLabel(
                table_scroll, 
                text=f"{day}日", 
                width=35, 
                fg_color=color, 
                corner_radius=4,
                font=ctk.CTkFont(weight="bold" if is_today else "normal")
            )
            lbl.grid(row=0, column=day, padx=2, pady=5)

        # 4つのルーチン行
        for r_idx in range(4):
            entry = ctk.CTkEntry(
                table_scroll, 
                width=130, 
                height=30,
                font=ctk.CTkFont(size=12)
            )
            entry.insert(0, self.default_routines[r_idx])
            entry.grid(row=r_idx + 1, column=0, padx=5, pady=5)
            entry.bind("<FocusOut>", lambda e: self.notify_change())
            self.routine_entries.append(entry)

            for day in self.days:
                var = ctk.BooleanVar(value=False)
                self.checkbox_vars[(r_idx, day)] = var

                chk = ctk.CTkCheckBox(
                    table_scroll, 
                    text="", 
                    variable=var, 
                    width=24, 
                    checkbox_width=18, 
                    checkbox_height=18,
                    command=self.on_check_changed
                )
                chk.grid(row=r_idx + 1, column=day, padx=7, pady=5)

        self.on_check_changed(trigger_save=False)

    def on_check_changed(self, trigger_save=True):
        """チェックボックスの状態が変わった時の処理"""
        for day in self.days:
            count = sum(1 for r_idx in range(4) if self.checkbox_vars[(r_idx, day)].get())
            self.daily_counts[day] = count
        self.update_graph()
        if trigger_save:
            self.notify_change()

    def notify_change(self):
        """親クラス（main.py）に保存を通知"""
        if self.on_change_callback:
            self.on_change_callback()

    def update_graph(self):
        """Canvasを用いた超高速グラフ描画"""
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return

        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 60:
            w = 880
            h = 180

        pad_left = 50
        pad_right = 25
        pad_top = 20
        pad_bottom = 30
        pw = max(10, w - pad_left - pad_right)
        ph = max(10, h - pad_top - pad_bottom)

        # Y軸グリッド線と数値ラベル
        for y in range(5):
            yp = pad_top + ph * (1 - y / 4.0)
            self.canvas.create_line(
                pad_left, yp, w - pad_right, yp, fill="#333333", dash=(4, 4)
            )
            self.canvas.create_text(
                pad_left - 8, yp, text=str(y), fill="#888888", font=("Helvetica", 9), anchor="e"
            )

        # Y軸タイトル
        self.canvas.create_text(
            15, pad_top + 5, text="達成数", fill="#888888", font=("Helvetica", 9), anchor="w"
        )

        num_days = len(self.days)
        if num_days <= 1:
            return

        coords = []
        polygon_coords = [pad_left, pad_top + ph]

        for idx, d in enumerate(self.days):
            cnt = self.daily_counts.get(d, 0)
            xp = pad_left + idx / (num_days - 1) * pw
            yp = pad_top + ph * (1 - cnt / 4.0)
            coords.append((xp, yp))
            polygon_coords.extend([xp, yp])

            # X軸日付ラベル（奇数日のみ表示して重複回避）
            if d % 2 == 1:
                self.canvas.create_text(
                    xp, h - pad_bottom + 12, text=f"{d}", fill="#888888", font=("Helvetica", 8)
                )

        polygon_coords.extend([pad_left + pw, pad_top + ph])

        # 塗りつぶし領域
        if len(polygon_coords) >= 6:
            self.canvas.create_polygon(polygon_coords, fill="#19324d", outline="")

        # 折れ線
        if len(coords) >= 2:
            flat_coords = [c for pt in coords for c in pt]
            self.canvas.create_line(flat_coords, fill="#1F6AA5", width=2)

        # データ点
        for xp, yp in coords:
            self.canvas.create_oval(
                xp - 3, yp - 3, xp + 3, yp + 3, fill="#8BE9FD", outline="#1F6AA5", width=1.5
            )

    # --- 一括保存用の共通インターフェース ---
    def get_data(self):
        """現在のルーティンデータを辞書形式で返す"""
        routines = [e.get() for e in self.routine_entries]
        checks = {f"{r}_{d}": var.get() for (r, d), var in self.checkbox_vars.items()}
        return {"routines": routines, "checks": checks}

    def set_data(self, data):
        """保存データを受け取って画面に反映"""
        routines = data.get("routines", [])
        checks = data.get("checks", {})

        for r_idx, entry in enumerate(self.routine_entries):
            if r_idx < len(routines):
                entry.delete(0, 'end')
                entry.insert(0, routines[r_idx])

        for (r_idx, day), var in self.checkbox_vars.items():
            key = f"{r_idx}_{day}"
            if key in checks:
                var.set(checks[key])

        self.on_check_changed(trigger_save=False)