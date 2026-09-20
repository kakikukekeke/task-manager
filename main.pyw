import json
import os
import sys
import customtkinter as ctk


def get_data_file_path(filename="app_data.json"):
  """どこから実行しても、main.pyw が存在するフォルダの絶対パスを返す"""
  if getattr(sys, "frozen", False):
    # exe化している場合
    base_dir = os.path.dirname(sys.executable)
  elif len(sys.argv) > 0 and sys.argv[0]:
    # python / pyw で実行されている場合
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
  else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

  return os.path.join(base_dir, filename)


# 絶対パスで DATA_FILE を定義
DATA_FILE = get_data_file_path("app_data.json")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TaskApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("MY ROUTINE & TASK MANAGER")
    self.geometry("1000x800")
    self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # 1. まずデータをファイルから読み込む
    self.app_data = self.load_data()

    # タブインスタンスの管理（遅延初期化用）
    self.routine_tab = None
    self.todo_tab = None
    self.pomodoro_tab = None
    self.calendar_tab = None
    self.weekly_tab = None

    # 保存処理のディバウンス用タイマー
    self._save_timer = None

    self.title_label = ctk.CTkLabel(
        self,
        text="⚡ FOCUS TASKS & ROUTINE",
        font=ctk.CTkFont(size=24, weight="bold"),
    )
    self.title_label.pack(pady=(15, 5))

    # 2. UI（タブビュー）の構築（タブ切り替え時に遅延読み込み）
    self.tabview = ctk.CTkTabview(
        self, width=940, height=700, command=self.on_tab_change
    )
    self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

    self.tab_1_name = "ルーティーン管理"
    self.tab_2_name = "今日のTo Do"
    self.tab_3_name = "ポモドーロ"
    self.tab_4_name = "月間カレンダー"
    self.tab_5_name = "週間カレンダー"

    self.tabview.add(self.tab_1_name)
    self.tabview.add(self.tab_2_name)
    self.tabview.add(self.tab_3_name)
    self.tabview.add(self.tab_4_name)
    self.tabview.add(self.tab_5_name)

    # 3. 起動時は初期表示のタブ（ルーティーン管理）のみを即座に生成
    self.ensure_tab_loaded(self.tab_1_name)

  def on_tab_change(self):
    """タブが切り替えられた際に、未生成のタブがあれば遅延生成"""
    selected = self.tabview.get()
    self.ensure_tab_loaded(selected)

  def ensure_tab_loaded(self, tab_name):
    """指定されたタブが未作成であれば生成し、保存データを反映"""
    if tab_name == self.tab_1_name and self.routine_tab is None:
      from routine_tab import RoutineTab

      self.routine_tab = RoutineTab(
          self.tabview.tab(self.tab_1_name), on_change_callback=self.save_data
      )
      self.routine_tab.pack(fill="both", expand=True)
      if "routine" in self.app_data and hasattr(self.routine_tab, "set_data"):
        self.routine_tab.set_data(self.app_data["routine"])

    elif tab_name == self.tab_2_name and self.todo_tab is None:
      from todo_tab import TodoTab

      self.todo_tab = TodoTab(
          self.tabview.tab(self.tab_2_name), on_change_callback=self.save_data
      )
      self.todo_tab.pack(fill="both", expand=True)
      if "todo" in self.app_data and hasattr(self.todo_tab, "set_data"):
        self.todo_tab.set_data(self.app_data["todo"])

    elif tab_name == self.tab_3_name and self.pomodoro_tab is None:
      from pomodoro_tab import PomodoroTab

      self.pomodoro_tab = PomodoroTab(
          self.tabview.tab(self.tab_3_name), on_change_callback=self.save_data
      )
      self.pomodoro_tab.pack(fill="both", expand=True)
      if "pomodoro" in self.app_data and hasattr(self.pomodoro_tab, "set_data"):
        self.pomodoro_tab.set_data(self.app_data["pomodoro"])

    elif tab_name == self.tab_4_name and self.calendar_tab is None:
      from calendar_tab import CalendarTab

      self.calendar_tab = CalendarTab(
          self.tabview.tab(self.tab_4_name), on_change_callback=self.save_data
      )
      self.calendar_tab.pack(fill="both", expand=True)
      if "calendar" in self.app_data and hasattr(self.calendar_tab, "set_data"):
        self.calendar_tab.set_data(self.app_data["calendar"])

    elif tab_name == self.tab_5_name and self.weekly_tab is None:
      from weekly_tab import WeeklyTab

      self.weekly_tab = WeeklyTab(self.tabview.tab(self.tab_5_name))
      self.weekly_tab.pack(fill="both", expand=True)

  def load_data(self):
    """JSONファイルから全データを読み込む"""
    if os.path.exists(DATA_FILE):
      try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception as e:
        print(f"データ読み込みエラー: {e}")
    return {}

  def save_data(self):
    """ディバウンス（遅延実行）により過剰なファイル書き込みを防止して保存"""
    if self._save_timer is not None:
      self.after_cancel(self._save_timer)
    # 350ミリ秒操作が途切れたらファイルへ保存
    self._save_timer = self.after(350, self._commit_save)

  def _commit_save(self):
    """初期化済みタブの最新値で app_data を更新し、ディスクに一括書き出し"""
    self._save_timer = None
    data = dict(self.app_data)

    if self.routine_tab and hasattr(self.routine_tab, "get_data"):
      data["routine"] = self.routine_tab.get_data()

    if self.todo_tab and hasattr(self.todo_tab, "get_data"):
      data["todo"] = self.todo_tab.get_data()

    if self.calendar_tab and hasattr(self.calendar_tab, "get_data"):
      data["calendar"] = self.calendar_tab.get_data()

    if self.pomodoro_tab and hasattr(self.pomodoro_tab, "get_data"):
      data["pomodoro"] = self.pomodoro_tab.get_data()

    self.app_data = data
    try:
      with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
      print(f"データ保存エラー: {e}")

  def on_closing(self):
    """×ボタンが押された時に未完了の保存を即座にコミットして終了"""
    try:
      # 保留中のディバウンスタイマーがあれば解除
      if self._save_timer is not None:
        self.after_cancel(self._save_timer)
        self._save_timer = None

      # 1. ポモドーロタイマーが動いていれば停止させる
      if self.pomodoro_tab and hasattr(self.pomodoro_tab, "is_running"):
        self.pomodoro_tab.is_running = False

      # 2. データを確実に即時保存
      self._commit_save()
      print("データ保存が完了しました。")

    except Exception as e:
      print(f"終了時保存エラー: {e}")

    finally:
      # 3. イベントループを終了してからウィンドウを破棄
      self.quit()
      self.destroy()


if __name__ == "__main__":
  app = TaskApp()
  app.mainloop()