import tkinter as tk
import customtkinter as ctk
import calendar
from datetime import datetime

class CalendarTab(ctk.CTkFrame):
    def __init__(self, master, on_change_callback=None):
        super().__init__(master)

        self.on_change_callback = on_change_callback

        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month

        # 予定データ: {(year, month, day): [{"title": "...", "all_day": True, "start_time": "10:00", "end_time": "12:00"}]}
        self.events = {}

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 月切り替えヘッダー
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        prev_btn = ctk.CTkButton(
            header_frame, text="◀ 前月", width=70, height=32, command=self.prev_month
        )
        prev_btn.pack(side="left")

        self.month_label = ctk.CTkLabel(
            header_frame, text="", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.month_label.pack(side="left", expand=True)

        next_btn = ctk.CTkButton(
            header_frame, text="次月 ▶", width=70, height=32, command=self.next_month
        )
        next_btn.pack(side="right")

        # --- 曜日表示ヘッダーエリア（固定） ---
        dow_frame = ctk.CTkFrame(main_frame, fg_color="#1E1E2E", corner_radius=6)
        dow_frame.pack(fill="x", padx=10, pady=(0, 5))

        days_of_week = ["月", "火", "水", "木", "金", "土", "日"]
        for col, dow in enumerate(days_of_week):
            text_color = "#FF79C6" if dow == "日" else ("#8BE9FD" if dow == "土" else "white")
            lbl = ctk.CTkLabel(
                dow_frame, text=dow, font=ctk.CTkFont(size=14, weight="bold"),
                text_color=text_color
            )
            lbl.grid(row=0, column=col, padx=2, pady=6, sticky="nsew")
            dow_frame.grid_columnconfigure(col, weight=1, uniform="dow")

        # カレンダー日付描画フレーム
        self.cal_grid_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.cal_grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.render_calendar()

    def render_calendar(self):
        # 既存の日付セルをクリア
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        self.month_label.configure(text=f"{self.current_year}年 {self.current_month}月")

        month_cal = calendar.monthcalendar(self.current_year, self.current_month)

        for row_idx, week in enumerate(month_cal):
            for col_idx, day in enumerate(week):
                cell = ctk.CTkFrame(
                    self.cal_grid_frame, 
                    fg_color="#21222c" if day == 0 else "#282a36",
                    border_width=1,
                    border_color="#44475a"
                )
                cell.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

                if day == 0:
                    continue

                is_today = (
                    self.current_year == self.today.year and
                    self.current_month == self.today.month and
                    day == self.today.day
                )

                date_lbl = ctk.CTkLabel(
                    cell, text=str(day), font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#FF79C6" if is_today else "white"
                )
                date_lbl.pack(anchor="nw", padx=5, pady=2)

                events_container = ctk.CTkFrame(cell, fg_color="transparent")
                events_container.pack(fill="both", expand=True, padx=2, pady=2)

                date_key = (self.current_year, self.current_month, day)
                day_events = self.events.get(date_key, [])

                # 最大2件まで表示
                for ev in day_events[:2]:
                    if ev["all_day"]:
                        bar_text = f"終日: {ev['title']}"
                    else:
                        bar_text = f"{ev['start_time']} {ev['title']}"
                    
                    event_bar = ctk.CTkLabel(
                        events_container, text=bar_text,
                        font=ctk.CTkFont(size=10, weight="bold"),
                        fg_color="#BD93F9" if ev["all_day"] else "#6272A4",
                        text_color="white", corner_radius=4, height=18, anchor="w"
                    )
                    event_bar.pack(fill="x", pady=1, padx=1)

                if len(day_events) > 2:
                    more_lbl = ctk.CTkLabel(
                        events_container, text=f"+他{len(day_events)-2}件",
                        font=ctk.CTkFont(size=9), text_color="gray"
                    )
                    more_lbl.pack(anchor="e", padx=2)

                # ダブルクリック判定
                for w in [cell, date_lbl, events_container] + events_container.winfo_children():
                    w.bind("<Double-Button-1>", lambda e, d=day: self.open_day_detail_modal(d))

        for i in range(7):
            self.cal_grid_frame.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(6):
            if i < len(month_cal):
                self.cal_grid_frame.grid_rowconfigure(i, weight=1, uniform="row")
            else:
                self.cal_grid_frame.grid_rowconfigure(i, weight=0, uniform="")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar()

    def delete_event(self, date_key, idx, day, modal):
        """予定を削除して状態を反映"""
        if date_key in self.events and len(self.events[date_key]) > idx:
            self.events[date_key].pop(idx)
            if not self.events[date_key]:
                del self.events[date_key]
            
            self.render_calendar()
            self.notify_change()
            modal.destroy()
            self.open_day_detail_modal(day)

    # -----------------------------------------------------------------
    # 日付詳細・一覧画面
    # -----------------------------------------------------------------
    def open_day_detail_modal(self, day):
        modal = ctk.CTkToplevel(self)
        modal.title(f"{self.current_year}年{self.current_month}月{day}日の予定")
        modal.geometry("400x500")
        modal.attributes("-topmost", True)
        modal.grab_set()

        date_key = (self.current_year, self.current_month, day)

        title_lbl = ctk.CTkLabel(
            modal, text=f"📅 {self.current_year}/{self.current_month}/{day} の予定一覧",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#8BE9FD"
        )
        title_lbl.pack(pady=15)

        add_btn = ctk.CTkButton(
            modal, text="➕ 予定を追加", font=ctk.CTkFont(weight="bold"),
            fg_color="#50FA7B", text_color="#282A36", hover_color="#40C965",
            command=lambda: [modal.destroy(), self.open_add_event_modal(day)]
        )
        add_btn.pack(pady=(0, 10))

        scroll_frame = ctk.CTkScrollableFrame(modal, width=340, height=340)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)

        day_events = self.events.get(date_key, [])

        if not day_events:
            no_lbl = ctk.CTkLabel(scroll_frame, text="予定はありません", text_color="gray")
            no_lbl.pack(pady=30)
        else:
            for idx, ev in enumerate(day_events):
                card = ctk.CTkFrame(scroll_frame)
                card.pack(fill="x", pady=5, padx=5)

                if ev["all_day"]:
                    time_str = "【終日】"
                else:
                    time_str = f"【{ev['start_time']} - {ev['end_time']}】"

                lbl_text = f"{time_str}\n{ev['title']}"

                lbl = ctk.CTkLabel(card, text=lbl_text, anchor="w", font=ctk.CTkFont(size=12), justify="left")
                lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)

                del_btn = ctk.CTkButton(
                    card, text="削除", width=45, height=28, fg_color="#FF5555", hover_color="#CC0000",
                    command=lambda i=idx: self.delete_event(date_key, i, day, modal)
                )
                del_btn.pack(side="right", padx=5)

        close_btn = ctk.CTkButton(
            modal, text="閉じる", width=120, height=32,
            fg_color="#44475a", hover_color="#6272a4",
            command=modal.destroy
        )
        close_btn.pack(pady=(0, 10))

    # -----------------------------------------------------------------
    # 予定追加画面
    # -----------------------------------------------------------------
    def open_add_event_modal(self, day):
        modal = ctk.CTkToplevel(self)
        modal.title("新規予定の追加")
        modal.geometry("380x480")
        modal.attributes("-topmost", True)
        modal.grab_set()

        title_lbl = ctk.CTkLabel(
            modal, text=f"✨ 予定を入力 ({self.current_month}/{day})",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_lbl.pack(pady=15)

        name_entry = ctk.CTkEntry(modal, placeholder_text="予定の名前を入力...", width=300, height=35)
        name_entry.pack(pady=10)

        all_day_var = ctk.BooleanVar(value=False)

        def toggle_time_selector():
            state = "disabled" if all_day_var.get() else "normal"
            start_hour_opt.configure(state=state)
            start_min_opt.configure(state=state)
            end_hour_opt.configure(state=state)
            end_min_opt.configure(state=state)

        chk = ctk.CTkCheckBox(
            modal, text="終日イベントにする", variable=all_day_var,
            font=ctk.CTkFont(weight="bold"), command=toggle_time_selector
        )
        chk.pack(pady=10)

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]

        start_frame = ctk.CTkFrame(modal, fg_color="transparent")
        start_frame.pack(pady=5)

        s_lbl = ctk.CTkLabel(start_frame, text="開始:", font=ctk.CTkFont(weight="bold"), width=50)
        s_lbl.pack(side="left", padx=5)

        start_hour_opt = ctk.CTkOptionMenu(start_frame, values=hours, width=70)
        start_hour_opt.set("10")
        start_hour_opt.pack(side="left", padx=2)

        ctk.CTkLabel(start_frame, text=":", font=ctk.CTkFont(weight="bold")).pack(side="left")

        start_min_opt = ctk.CTkOptionMenu(start_frame, values=minutes, width=70)
        start_min_opt.set("00")
        start_min_opt.pack(side="left", padx=2)

        end_frame = ctk.CTkFrame(modal, fg_color="transparent")
        end_frame.pack(pady=5)

        e_lbl = ctk.CTkLabel(end_frame, text="終了:", font=ctk.CTkFont(weight="bold"), width=50)
        e_lbl.pack(side="left", padx=5)

        end_hour_opt = ctk.CTkOptionMenu(end_frame, values=hours, width=70)
        end_hour_opt.set("11")
        end_hour_opt.pack(side="left", padx=2)

        ctk.CTkLabel(end_frame, text=":", font=ctk.CTkFont(weight="bold")).pack(side="left")

        end_min_opt = ctk.CTkOptionMenu(end_frame, values=minutes, width=70)
        end_min_opt.set("00")
        end_min_opt.pack(side="left", padx=2)

        def save_event():
            title = name_entry.get().strip()
            if not title:
                return

            date_key = (self.current_year, self.current_month, day)
            if date_key not in self.events:
                self.events[date_key] = []

            is_all_day = all_day_var.get()
            s_time = f"{start_hour_opt.get()}:{start_min_opt.get()}"
            e_time = f"{end_hour_opt.get()}:{end_min_opt.get()}"

            self.events[date_key].append({
                "title": title,
                "all_day": is_all_day,
                "start_time": s_time,
                "end_time": e_time
            })

            self.render_calendar()
            self.notify_change()  # 変更を通知
            modal.destroy()
            self.open_day_detail_modal(day)

        btn_box = ctk.CTkFrame(modal, fg_color="transparent")
        btn_box.pack(pady=20)

        save_btn = ctk.CTkButton(
            btn_box, text="保存する", width=140, height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#BD93F9", hover_color="#985EFF",
            command=save_event
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_box, text="キャンセル", width=100, height=40,
            fg_color="#44475a", hover_color="#6272a4",
            command=modal.destroy
        )
        cancel_btn.pack(side="left", padx=10)

    # -----------------------------------------------------------------
    # 一括保存・復元用の共通インターフェース
    # -----------------------------------------------------------------
    def notify_change(self):
        """親クラス (main.py) に保存を通知"""
        if self.on_change_callback:
            self.on_change_callback()

    def get_data(self):
        """タプル型のキー (YYYY, MM, DD) を 'YYYY-MM-DD' に変換して返す"""
        formatted_events = {}
        for (year, month, day), ev_list in self.events.items():
            key_str = f"{year:04d}-{month:02d}-{day:02d}"
            formatted_events[key_str] = ev_list
        return formatted_events

    def set_data(self, data):
        """'YYYY-MM-DD' 形式のデータを (YYYY, MM, DD) に復元"""
        if not isinstance(data, dict):
            return

        self.events = {}
        for key_str, ev_list in data.items():
            try:
                parts = key_str.split("-")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    self.events[(year, month, day)] = ev_list
            except ValueError:
                continue

        self.render_calendar()