import customtkinter as ctk
from tkinter import messagebox  # デスクトップポップアップ通知用

class PomodoroTab(ctk.CTkFrame):
    def __init__(self, master, on_change_callback=None):
        super().__init__(master)

        self.on_change_callback = on_change_callback

        # タイマー状態管理
        self.is_running = False
        self.time_left = 25 * 60
        self.current_mode = "study"
        self.completed_sessions = 0

        # 1000時間カウンター
        self.TOTAL_REQUIRED_SECONDS = 1000 * 3600
        self.remaining_seconds = self.TOTAL_REQUIRED_SECONDS

        self.setup_ui()

    def setup_ui(self):
        # 上段：1000時間カウントダウンエリア
        goal_frame = ctk.CTkFrame(self)
        goal_frame.pack(fill="x", padx=15, pady=10)

        goal_title = ctk.CTkLabel(
            goal_frame, 
            text="🔥 1000 HOURS TO BE A MASTER", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        goal_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.goal_label = ctk.CTkLabel(
            goal_frame, 
            text="", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFB86C"
        )
        self.goal_label.pack(padx=15, pady=5)

        self.progress_bar = ctk.CTkProgressBar(goal_frame, width=600, height=15)
        self.progress_bar.pack(padx=15, pady=(5, 10))

        reset_goal_btn = ctk.CTkButton(
            goal_frame, 
            text="🔄 1000時間リセット (テスト用)", 
            width=180,
            height=28,
            fg_color="#44475a",
            hover_color="#6272a4",
            command=self.reset_1000_hours
        )
        reset_goal_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # 中段：メインタイマー表示
        timer_frame = ctk.CTkFrame(self)
        timer_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.mode_label = ctk.CTkLabel(
            timer_frame, 
            text="📚 学習タイム", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8BE9FD"
        )
        self.mode_label.pack(pady=(15, 5))

        self.timer_label = ctk.CTkLabel(
            timer_frame, 
            text="25:00", 
            font=ctk.CTkFont(size=72, weight="bold")
        )
        self.timer_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶ スタート", width=120, height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#50fa7b", text_color="#282a36", hover_color="#40c965",
            command=self.start_timer
        )
        self.start_btn.pack(side="left", padx=10)

        self.pause_btn = ctk.CTkButton(
            btn_frame, text="⏸ 一時停止", width=120, height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ffb86c", text_color="#282a36", hover_color="#e0a050",
            command=self.pause_timer
        )
        self.pause_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(
            btn_frame, text="⏹ リセット", width=120, height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ff5555", hover_color="#cc0000",
            command=self.reset_timer
        )
        self.reset_btn.pack(side="left", padx=10)

        # 下段：設定エリア
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="x", padx=15, pady=10)

        set_time_label = ctk.CTkLabel(settings_frame, text="学習時間(分):", font=ctk.CTkFont(weight="bold"))
        set_time_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 小数点も入力できるように設定
        self.study_entry = ctk.CTkEntry(settings_frame, width=70)
        self.study_entry.insert(0, "25")
        self.study_entry.grid(row=0, column=1, padx=5, pady=10)

        set_btn = ctk.CTkButton(settings_frame, text="セット", width=60, command=self.set_custom_study_time)
        set_btn.grid(row=0, column=2, padx=5, pady=10)

        break_label = ctk.CTkLabel(settings_frame, text="休憩選択:", font=ctk.CTkFont(weight="bold"))
        break_label.grid(row=0, column=3, padx=(20, 10), pady=10, sticky="w")

        for mins in [1, 3, 5]:
            btn = ctk.CTkButton(
                settings_frame, text=f"{mins}分", width=50,
                command=lambda m=mins: self.set_break_time(m)
            )
            btn.grid(row=0, column=3 + [1, 3, 5].index(mins) + 1, padx=2, pady=10)

        # 通知ON/OFFスイッチ
        self.notify_switch = ctk.CTkSwitch(settings_frame, text="🔔 画面通知", font=ctk.CTkFont(weight="bold"))
        self.notify_switch.select()
        self.notify_switch.grid(row=0, column=8, padx=20, pady=10)

        self.suggestion_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF79C6"
        )
        self.suggestion_label.pack(pady=(0, 10))

        self.update_goal_display()
        self.update_timer_display()

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.run_timer()

    def pause_timer(self):
        self.is_running = False

    def reset_timer(self):
        self.is_running = False
        self.set_custom_study_time()

    def run_timer(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            self.after(1000, self.run_timer)
        elif self.time_left == 0 and self.is_running:
            self.is_running = False
            self.on_timer_complete()

    def on_timer_complete(self):
        if self.current_mode == "study":
            try:
                study_mins = float(self.study_entry.get())
            except ValueError:
                study_mins = 25.0

            self.remaining_seconds = max(0, self.remaining_seconds - (study_mins * 60))
            self.completed_sessions += 1
            self.update_goal_display()
            self.notify_change()  # データ変更を親へ通知して保存

            # ポップアップ通知を送る
            if self.notify_switch.get() == 1:
                messagebox.showinfo("時間終了！", "🎉 学習時間が終了しました！お疲れ様です。休憩に入りましょう！")

            if self.completed_sessions % 4 == 0:
                self.suggestion_label.configure(
                    text="🎉 4セット完了！長めの休憩を取りましょう！（提案: 20分 / 30分 / 35分）"
                )
                self.show_long_break_options()
            else:
                self.suggestion_label.configure(text="✨ 学習完了！休憩を選んでリフレッシュしましょう。")

            self.mode_label.configure(text="☕ 休憩を選んでください", text_color="#50FA7B")

        else:
            if self.notify_switch.get() == 1:
                messagebox.showinfo("時間終了！", "💪 休憩時間が終了しました！次の学習を開始しましょう！")

            self.mode_label.configure(text="📚 学習タイム", text_color="#8BE9FD")
            self.suggestion_label.configure(text="💪 休憩終了！次の学習をセットしてスタートしましょう。")
            self.set_custom_study_time()

    def set_custom_study_time(self):
        try:
            val = float(self.study_entry.get())
            if val > 0:
                self.current_mode = "study"
                self.mode_label.configure(text="📚 学習タイム", text_color="#8BE9FD")
                self.time_left = int(val * 60)
                self.update_timer_display()
        except ValueError:
            pass

    def set_break_time(self, mins):
        self.is_running = False
        self.current_mode = "break"
        self.mode_label.configure(text=f"☕ 休憩中 ({mins}分)", text_color="#50FA7B")
        self.time_left = int(mins * 60)
        self.update_timer_display()

    def show_long_break_options(self):
        popup = ctk.CTkToplevel(self)
        popup.title("長めの休憩提案")
        popup.geometry("380x180")
        popup.attributes("-topmost", True)

        lbl = ctk.CTkLabel(
            popup, 
            text="4セットお疲れ様でした！\nしっかり脳を休めましょう。", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl.pack(pady=15)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10)

        for mins in [20, 30, 35]:
            btn = ctk.CTkButton(
                btn_frame, 
                text=f"{mins}分", 
                width=80,
                fg_color="#BD93F9",
                hover_color="#985EFF",
                command=lambda m=mins: [self.set_break_time(m), popup.destroy()]
            )
            btn.pack(side="left", padx=5)

    def update_timer_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")

    def update_goal_display(self):
        rem_hours = self.remaining_seconds / 3600
        done_hours = 1000 - rem_hours
        progress_ratio = done_hours / 1000

        self.goal_label.configure(text=f"一人前まで あと {rem_hours:.2f} 時間 / 1000 時間 ({done_hours:.2f}時間達成！)")
        self.progress_bar.set(progress_ratio)

    def reset_1000_hours(self):
        self.remaining_seconds = self.TOTAL_REQUIRED_SECONDS
        self.completed_sessions = 0
        self.suggestion_label.configure(text="1000時間カウントダウンをリセットしました。")
        self.update_goal_display()
        self.notify_change()  # リセット時もデータ変更を通知

    def notify_change(self):
        """変更時に親（main.py）へ保存を通知"""
        if self.on_change_callback:
            self.on_change_callback()

    # --- 一括保存用の共通インターフェース ---
    def get_data(self):
        """現在の1000時間タイマーデータを返す"""
        return {
            "remaining_seconds": self.remaining_seconds,
            "completed_sessions": self.completed_sessions
        }

    def set_data(self, data):
        """保存データを受け取って復元"""
        if isinstance(data, dict):
            self.remaining_seconds = data.get("remaining_seconds", self.TOTAL_REQUIRED_SECONDS)
            self.completed_sessions = data.get("completed_sessions", 0)
            self.update_goal_display()