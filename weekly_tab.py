import json
import os
import sys
from datetime import datetime, timedelta
import tkinter as tk
import customtkinter as ctk


class WeeklyTab(ctk.CTkFrame):

  def __init__(self, master, json_filename="weekly_events.json"):
    super().__init__(master)

    self.today = datetime.now()
    self.start_of_week = self.today - timedelta(days=self.today.weekday())

    if getattr(sys, "frozen", False):
      base_dir = os.path.dirname(sys.executable)
    elif len(sys.argv) > 0 and sys.argv[0]:
      base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
      base_dir = os.path.dirname(os.path.abspath(__file__))

    self.json_path = os.path.join(base_dir, json_filename)
    self.events = {}

    self.load_events()
    self.setup_ui()

  # -----------------------------------------------------------------
  # データ保存・読み込み機能
  # -----------------------------------------------------------------
  def load_events(self):
    """JSONファイルから予定データを読み込む"""
    if not os.path.exists(self.json_path):
      self.events = {}
      return

    try:
      with open(self.json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

      self.events = {}
      for date_str, event_list in raw_data.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_key = (dt.year, dt.month, dt.day)
        self.events[date_key] = event_list
    except Exception as e:
      print(f"データ読み込みエラー: {e}")
      self.events = {}

  def save_events(self):
    """現在の予定データをJSONファイルへ保存する"""
    try:
      save_data = {}
      for (y, m, d), event_list in self.events.items():
        date_str = f"{y:04d}-{m:02d}-{d:02d}"
        save_data[date_str] = event_list

      with open(self.json_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
      print(f"データ保存エラー: {e}")

  def delete_event(self, dt, ev):
    """予定を削除して保存・再描画"""
    date_key = (dt.year, dt.month, dt.day)
    if date_key in self.events:
      if ev in self.events[date_key]:
        self.events[date_key].remove(ev)
      if not self.events[date_key]:
        del self.events[date_key]
      self.save_events()
      self.render_weekly_grid()

  def setup_ui(self):
    main_frame = ctk.CTkFrame(self)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ヘッダー（週切り替え）
    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(5, 10))

    prev_btn = ctk.CTkButton(
        header_frame, text="◀ 前週", width=70, height=32, command=self.prev_week
    )
    prev_btn.pack(side="left")

    self.week_label = ctk.CTkLabel(
        header_frame, text="", font=ctk.CTkFont(size=18, weight="bold")
    )
    self.week_label.pack(side="left", expand=True)

    next_btn = ctk.CTkButton(
        header_frame, text="次週 ▶", width=70, height=32, command=self.next_week
    )
    next_btn.pack(side="right")

    self.cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    self.cards_frame.pack(fill="both", expand=True)

    self.render_weekly_grid()

  def render_weekly_grid(self):
    for widget in self.cards_frame.winfo_children():
      widget.destroy()

    end_of_week = self.start_of_week + timedelta(days=6)
    self.week_label.configure(
        text=(
            f"📅 {self.start_of_week.strftime('%Y/%m/%d')} 〜"
            f" {end_of_week.strftime('%m/%d')}"
        )
    )

    days_of_week = ["月", "火", "水", "木", "金", "土", "日"]
    week_dates = [self.start_of_week + timedelta(days=i) for i in range(7)]

    for i in range(7):
      self.cards_frame.grid_columnconfigure(i, weight=1)
    self.cards_frame.grid_rowconfigure(0, weight=1)

    for col_idx, (dow, dt) in enumerate(zip(days_of_week, week_dates)):
      is_today = dt.date() == self.today.date()
      header_bg = "#1F6AA5" if is_today else "#2A2A3C"
      text_color = (
          "#FF79C6" if dow == "日" else ("#8BE9FD" if dow == "土" else "white")
      )

      day_card = ctk.CTkFrame(
          self.cards_frame,
          fg_color="#1E1E2E",
          border_width=1,
          border_color="#313244",
          corner_radius=8,
      )
      day_card.grid(row=0, column=col_idx, padx=3, pady=2, sticky="nsew")

      # 1. 曜日ヘッダー
      hdr = ctk.CTkFrame(
          day_card, fg_color=header_bg, height=35, corner_radius=6
      )
      hdr.pack(fill="x", padx=4, pady=4)

      hdr_lbl = ctk.CTkLabel(
          hdr,
          text=f"{dow} ({dt.month}/{dt.day})",
          font=ctk.CTkFont(size=12, weight="bold"),
          text_color=text_color,
      )
      hdr_lbl.pack(expand=True, pady=4)

      # 曜日ヘッダーをダブルクリックでその日の予定一覧・削除モーダルを表示
      for w in [hdr, hdr_lbl]:
        w.bind("<Double-Button-1>", lambda e, d=dt: self.open_day_detail_modal(d))

      # 2. タイムラインエリア
      timeline_scroll = ctk.CTkScrollableFrame(
          day_card, fg_color="transparent"
      )
      timeline_scroll.pack(fill="both", expand=True, padx=2, pady=(0, 4))
      timeline_scroll.bind(
          "<Double-Button-1>", lambda e, d=dt: self.open_day_detail_modal(d)
      )

      # 終日イベント表示
      date_key = (dt.year, dt.month, dt.day)
      day_events = self.events.get(date_key, [])
      allday_events = [ev for ev in day_events if ev.get("all_day")]

      for ev in allday_events:
        ad_bar = ctk.CTkLabel(
            timeline_scroll,
            text=f"★ {ev['title']}",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#BD93F9",
            text_color="white",
            corner_radius=4,
        )
        ad_bar.pack(fill="x", padx=2, pady=2)
        ad_bar.bind(
            "<Double-Button-1>",
            lambda e, d=dt, target_ev=ev: self.open_event_detail_modal(d, target_ev),
        )

      # 0〜23時 タイムライン構築（軽量標準ウィジェットで高速描画）
      for hour in range(24):
        matching_events = [
            ev
            for ev in day_events
            if not ev.get("all_day") and (ev["start_hour"] <= hour < ev["end_hour"])
        ]

        row_frame = tk.Frame(timeline_scroll, bg="#1E1E2E", height=22)
        row_frame.pack(fill="x", pady=0)
        row_frame.pack_propagate(False)

        time_lbl = tk.Label(
            row_frame,
            text=f"{hour:02d}",
            font=("Helvetica", 8),
            bg="#1E1E2E",
            fg="#6C7086",
            width=3,
            anchor="w",
        )
        time_lbl.pack(side="left", padx=(1, 2))

        content_box = tk.Frame(row_frame, bg="#1E1E2E")
        content_box.pack(side="left", fill="both", expand=True)

        if matching_events:
          ev = matching_events[0]
          line_bar = tk.Frame(content_box, bg="#BD93F9", width=3)
          line_bar.pack(side="left", fill="y", padx=(0, 3))

          text_frame = tk.Frame(content_box, bg="#1E1E2E")
          text_frame.pack(side="left", fill="both", expand=True)

          if ev["start_hour"] == hour:
            t_lbl = tk.Label(
                text_frame,
                text=ev["title"],
                font=("Helvetica", 9, "bold"),
                bg="#1E1E2E",
                fg="#F5E0DC",
                anchor="w",
            )
            t_lbl.pack(fill="x", anchor="w")
          elif ev["start_hour"] + 1 == hour:
            time_str = f"({ev['start_hour']}~{ev['end_hour']})"
            sub_lbl = tk.Label(
                text_frame,
                text=time_str,
                font=("Helvetica", 8),
                bg="#1E1E2E",
                fg="#BAC2DE",
                anchor="w",
            )
            sub_lbl.pack(fill="x", anchor="w")

          # 予定がある場所をダブルクリック -> 予定詳細・削除画面を開く
          for w in [row_frame, time_lbl, content_box, line_bar, text_frame]:
            w.bind(
                "<Double-Button-1>",
                lambda e, d=dt, target_ev=ev: self.open_event_detail_modal(d, target_ev),
            )
        else:
          divider = tk.Frame(content_box, bg="#2A2A3C", height=1)
          divider.pack(fill="x", expand=True)

          # 空欄をダブルクリック -> 新規予定の追加画面を開く
          for w in [row_frame, time_lbl, content_box, divider]:
            w.bind(
                "<Double-Button-1>",
                lambda e, d=dt, h=hour: self.open_add_event_modal(d, h),
            )

  def prev_week(self):
    self.start_of_week -= timedelta(days=7)
    self.render_weekly_grid()

  def next_week(self):
    self.start_of_week += timedelta(days=7)
    self.render_weekly_grid()

  # -----------------------------------------------------------------
  # 予定の詳細・削除モーダル
  # -----------------------------------------------------------------
  def open_event_detail_modal(self, dt, ev):
    modal = ctk.CTkToplevel(self)
    modal.title("予定の確認・削除")
    modal.geometry("380x280")
    modal.attributes("-topmost", True)
    modal.grab_set()

    date_str = dt.strftime("%Y/%m/%d (%a)")
    title_lbl = ctk.CTkLabel(
        modal,
        text="📅 予定の詳細",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#8BE9FD",
    )
    title_lbl.pack(pady=(15, 5))

    date_sub = ctk.CTkLabel(
        modal, text=date_str, font=ctk.CTkFont(size=13), text_color="#A0A0B0"
    )
    date_sub.pack(pady=(0, 10))

    card = ctk.CTkFrame(modal, fg_color="#1E1E2E", corner_radius=8)
    card.pack(fill="x", padx=20, pady=10)

    if ev.get("all_day"):
      time_str = "【終日イベント】"
    else:
      s_min = ev.get("start_min", 0)
      e_min = ev.get("end_min", 0)
      time_str = f"【{ev.get('start_hour', 0):02d}:{s_min:02d} 〜 {ev.get('end_hour', 0):02d}:{e_min:02d}】"

    t_lbl = ctk.CTkLabel(
        card,
        text=time_str,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#BD93F9",
    )
    t_lbl.pack(anchor="w", padx=15, pady=(10, 2))

    ev_title = ctk.CTkLabel(
        card,
        text=ev.get("title", ""),
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="white",
        wraplength=300,
        justify="left",
    )
    ev_title.pack(anchor="w", padx=15, pady=(2, 10))

    btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
    btn_frame.pack(pady=15)

    def do_delete():
      self.delete_event(dt, ev)
      modal.destroy()

    del_btn = ctk.CTkButton(
        btn_frame,
        text="🗑️ この予定を削除",
        width=150,
        height=38,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#FF5555",
        hover_color="#CC0000",
        command=do_delete,
    )
    del_btn.pack(side="left", padx=10)

    close_btn = ctk.CTkButton(
        btn_frame,
        text="閉じる",
        width=90,
        height=38,
        fg_color="#44475a",
        hover_color="#6272a4",
        command=modal.destroy,
    )
    close_btn.pack(side="left", padx=10)

  # -----------------------------------------------------------------
  # 日別予定一覧・削除モーダル
  # -----------------------------------------------------------------
  def open_day_detail_modal(self, dt):
    modal = ctk.CTkToplevel(self)
    date_str = dt.strftime("%Y/%m/%d (%a)")
    modal.title(f"{date_str} の予定一覧")
    modal.geometry("400x500")
    modal.attributes("-topmost", True)
    modal.grab_set()

    title_lbl = ctk.CTkLabel(
        modal,
        text=f"📅 {date_str} の予定一覧",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#8BE9FD",
    )
    title_lbl.pack(pady=15)

    add_btn = ctk.CTkButton(
        modal,
        text="➕ 新規予定を追加",
        font=ctk.CTkFont(weight="bold"),
        fg_color="#50FA7B",
        text_color="#282A36",
        hover_color="#40C965",
        command=lambda: [modal.destroy(), self.open_add_event_modal(dt)],
    )
    add_btn.pack(pady=(0, 10))

    scroll_frame = ctk.CTkScrollableFrame(modal, width=340, height=340)
    scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)

    date_key = (dt.year, dt.month, dt.day)
    day_events = list(self.events.get(date_key, []))

    if not day_events:
      no_lbl = ctk.CTkLabel(
          scroll_frame, text="予定はありません", text_color="gray"
      )
      no_lbl.pack(pady=30)
    else:
      for ev in day_events:
        card = ctk.CTkFrame(scroll_frame)
        card.pack(fill="x", pady=5, padx=5)

        if ev.get("all_day"):
          time_str = "【終日】"
        else:
          s_m = ev.get("start_min", 0)
          e_m = ev.get("end_min", 0)
          time_str = f"【{ev.get('start_hour', 0):02d}:{s_m:02d} - {ev.get('end_hour', 0):02d}:{e_m:02d}】"

        lbl_text = f"{time_str}\n{ev.get('title', '')}"

        lbl = ctk.CTkLabel(
            card,
            text=lbl_text,
            anchor="w",
            font=ctk.CTkFont(size=12),
            justify="left",
        )
        lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)

        def make_delete_cmd(target_ev=ev):
          def delete_and_refresh():
            self.delete_event(dt, target_ev)
            modal.destroy()
            self.open_day_detail_modal(dt)

          return delete_and_refresh

        del_btn = ctk.CTkButton(
            card,
            text="削除",
            width=50,
            height=28,
            fg_color="#FF5555",
            hover_color="#CC0000",
            command=make_delete_cmd(ev),
        )
        del_btn.pack(side="right", padx=5)

  # -----------------------------------------------------------------
  # 予定追加モーダル
  # -----------------------------------------------------------------
  def open_add_event_modal(self, dt, default_hour=9):
    modal = ctk.CTkToplevel(self)
    modal.title("予定の追加")
    modal.geometry("380x480")
    modal.attributes("-topmost", True)
    modal.grab_set()

    date_str = dt.strftime("%Y/%m/%d (%a)")
    title_lbl = ctk.CTkLabel(
        modal,
        text=f"予定を入力\n{date_str}",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    title_lbl.pack(pady=15)

    name_entry = ctk.CTkEntry(
        modal, placeholder_text="予定の名前を入力 (例: バイト)", width=300, height=35
    )
    name_entry.pack(pady=10)

    all_day_var = ctk.BooleanVar(value=False)

    def toggle_time_selector():
      state = "disabled" if all_day_var.get() else "normal"
      start_hour_opt.configure(state=state)
      start_min_opt.configure(state=state)
      end_hour_opt.configure(state=state)
      end_min_opt.configure(state=state)

    chk = ctk.CTkCheckBox(
        modal,
        text="終日イベントにする",
        variable=all_day_var,
        font=ctk.CTkFont(weight="bold"),
        command=toggle_time_selector,
    )
    chk.pack(pady=10)

    hours = [f"{h:02d}" for h in range(24)]
    minutes = [f"{m:02d}" for m in range(0, 60, 5)]

    # 開始時間
    start_frame = ctk.CTkFrame(modal, fg_color="transparent")
    start_frame.pack(pady=5)
    ctk.CTkLabel(
        start_frame, text="開始:", font=ctk.CTkFont(weight="bold"), width=50
    ).pack(side="left", padx=5)
    start_hour_opt = ctk.CTkOptionMenu(start_frame, values=hours, width=70)
    start_hour_opt.set(f"{default_hour:02d}")
    start_hour_opt.pack(side="left", padx=2)
    ctk.CTkLabel(start_frame, text=":", font=ctk.CTkFont(weight="bold")).pack(
        side="left"
    )
    start_min_opt = ctk.CTkOptionMenu(start_frame, values=minutes, width=70)
    start_min_opt.set("00")
    start_min_opt.pack(side="left", padx=2)

    # 終了時間
    end_frame = ctk.CTkFrame(modal, fg_color="transparent")
    end_frame.pack(pady=5)
    ctk.CTkLabel(
        end_frame, text="終了:", font=ctk.CTkFont(weight="bold"), width=50
    ).pack(side="left", padx=5)
    end_hour_opt = ctk.CTkOptionMenu(end_frame, values=hours, width=70)
    end_hour_opt.set(f"{min(23, default_hour + 1):02d}")
    end_hour_opt.pack(side="left", padx=2)
    ctk.CTkLabel(end_frame, text=":", font=ctk.CTkFont(weight="bold")).pack(
        side="left"
    )
    end_min_opt = ctk.CTkOptionMenu(end_frame, values=minutes, width=70)
    end_min_opt.set("00")
    end_min_opt.pack(side="left", padx=2)

    def save_event():
      title = name_entry.get().strip()
      if not title:
        return

      date_key = (dt.year, dt.month, dt.day)
      if date_key not in self.events:
        self.events[date_key] = []

      is_all_day = all_day_var.get()
      s_h = int(start_hour_opt.get())
      s_m = int(start_min_opt.get())
      e_h = int(end_hour_opt.get())
      e_m = int(end_min_opt.get())

      if not is_all_day and e_h <= s_h:
        e_h = min(23, s_h + 1)

      self.events[date_key].append({
          "title": title,
          "all_day": is_all_day,
          "start_hour": s_h,
          "start_min": s_m,
          "end_hour": e_h,
          "end_min": e_m,
      })

      # ファイルへの保存を実行
      self.save_events()

      # 画面描画の更新
      self.render_weekly_grid()
      modal.destroy()

    btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
    btn_frame.pack(pady=20)

    save_btn = ctk.CTkButton(
        btn_frame,
        text="保存する",
        width=150,
        height=40,
        font=ctk.CTkFont(size=15, weight="bold"),
        fg_color="#BD93F9",
        hover_color="#985EFF",
        command=save_event,
    )
    save_btn.pack(side="left", padx=10)

    cancel_btn = ctk.CTkButton(
        btn_frame,
        text="キャンセル",
        width=100,
        height=40,
        fg_color="#44475a",
        hover_color="#6272a4",
        command=modal.destroy,
    )
    cancel_btn.pack(side="left", padx=10)