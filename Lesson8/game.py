import random
import tkinter as tk
from tkinter import messagebox


class GuessGameGUI:
    """猜數字遊戲 - 專業版圖形介面"""

    def __init__(self, root):
        self.root = root
        self.root.title("猜數字遊戲")
        self.root.configure(bg="#0d1117")

        win_w, win_h = 460, 600
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.resizable(False, False)

        # Color palette
        self.C_BG = "#0d1117"
        self.C_CARD = "#161b22"
        self.C_BORDER = "#30363d"
        self.C_ACCENT = "#58a6ff"
        self.C_PRIMARY = "#f0883e"
        self.C_PRIMARY_HOVER = "#f9a85b"
        self.C_GOLD = "#d29922"
        self.C_TEXT = "#e6edf3"
        self.C_TEXT_MUTED = "#8b949e"
        self.C_SUCCESS = "#3fb950"
        self.C_HIGH = "#f85149"
        self.C_LOW = "#d29922"
        self.C_INPUT_BG = "#0d1117"

        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.game_over = False
        self.history = []

        self._build_ui()

    def _round_rect(self, c, x1, y1, x2, y2, r=8, **kw):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2 - r,
            x1, y1 + r,
        ]
        return c.create_polygon(points, smooth=True, **kw)

    def _build_ui(self):
        c = tk.Canvas(self.root, bg=self.C_BG, highlightthickness=0)
        c.pack(fill=tk.BOTH, expand=True)
        self.c = c

        # ── Title ──
        c.create_text(230, 38, text="\u6578\u5b57\u8b1c\u5507",  # 數字猜謎
                      font=("Segoe UI", 24, "bold"),
                      fill=self.C_GOLD, anchor="center")
        c.create_text(230, 68, text="Guess The Number  \u2022  1 ~ 100",
                      font=("Segoe UI", 10),
                      fill=self.C_TEXT_MUTED, anchor="center")

        # ── Card ──
        self._round_rect(c, 30, 100, 430, 520, r=14,
                         fill=self.C_CARD, outline=self.C_BORDER, width=1)

        # ── Range label ──
        self.range_id = c.create_text(
            230, 140,
            text=f"\u8acb\u731c {self.low} ~ {self.high} \u4e4b\u9593\u7684\u6578\u5b57",
            font=("Segoe UI", 13), fill=self.C_TEXT, anchor="center",
        )

        # ── Range progress bar ──
        bx1, bx2, by = 55, 405, 172
        self.bx1, self.bx2, self.by = bx1, bx2, by
        self._round_rect(c, bx1, by - 5, bx2, by + 5, r=5,
                         fill="#21262d")
        self.bar_id = self._round_rect(c, bx1, by - 5, bx2, by + 5, r=5,
                                       fill=self.C_ACCENT, width=0)
        c.create_text(bx1, by + 18, text="1",
                      font=("Segoe UI", 9), fill=self.C_TEXT_MUTED, anchor="center")
        c.create_text(bx2, by + 18, text="100",
                      font=("Segoe UI", 9), fill=self.C_TEXT_MUTED, anchor="center")

        # ── Entry ──
        entry_bx, entry_by = 175, 212
        self.entry_bg = self._round_rect(c, entry_bx, entry_by,
                                         entry_bx + 110, entry_by + 50,
                                         r=10, fill=self.C_INPUT_BG,
                                         outline=self.C_BORDER, width=2)

        self.entry = tk.Entry(
            self.root, font=("Segoe UI", 22, "bold"),
            width=4, justify="center", bd=0,
            bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_TEXT,
            highlightthickness=0,
        )
        c.create_window(230, 237, window=self.entry, anchor="center")
        self.entry.bind("<Return>", lambda e: self._on_guess())
        self.entry.bind("<FocusIn>",
                        lambda e: c.itemconfig(self.entry_bg, outline=self.C_ACCENT))
        self.entry.bind("<FocusOut>",
                        lambda e: c.itemconfig(self.entry_bg, outline=self.C_BORDER))

        # ── Guess button ──
        btn_x1, btn_y1, btn_x2, btn_y2 = 120, 282, 340, 332
        self.btn_bg = self._round_rect(c, btn_x1, btn_y1, btn_x2, btn_y2, r=10,
                                       fill=self.C_PRIMARY, width=0)
        self.btn_text = c.create_text(230, 307,
                                      text="\u731c \uff01",  # 猜 ！
                                      font=("Segoe UI", 15, "bold"),
                                      fill="#ffffff", anchor="center")

        for tag in (self.btn_bg, self.btn_text):
            c.tag_bind(tag, "<Button-1>", lambda e: self._on_guess())
            c.tag_bind(tag, "<Enter>",
                       lambda e: c.itemconfig(self.btn_bg, fill=self.C_PRIMARY_HOVER))
            c.tag_bind(tag, "<Leave>",
                       lambda e: c.itemconfig(self.btn_bg, fill=self.C_PRIMARY))

        # ── Result ──
        self.result_id = c.create_text(230, 370, text="",
                                       font=("Segoe UI", 16, "bold"),
                                       fill=self.C_TEXT, anchor="center")

        # ── Attempts ──
        self.attempt_id = c.create_text(230, 402,
                                        text="\u5df2\u731c\u6b21\u6578\uff1a0",
                                        font=("Segoe UI", 11),
                                        fill=self.C_TEXT_MUTED, anchor="center")

        # ── History ──
        c.create_text(230, 434,
                      text="\u2500\u2500 \u731c\u6e2c\u8a18\u9304 \u2500\u2500",
                      font=("Segoe UI", 10),
                      fill=self.C_TEXT_MUTED, anchor="center")
        self.history_id = c.create_text(230, 465, text="",
                                        font=("Segoe UI", 12, "bold"),
                                        fill=self.C_TEXT_MUTED, anchor="center")

        # ── New game ──
        self.new_id = c.create_text(230, 506,
                                    text="\u91cd\u65b0\u958b\u59cb\u65b0\u904a\u6232",
                                    font=("Segoe UI", 11),
                                    fill=self.C_TEXT_MUTED, anchor="center")
        c.tag_bind(self.new_id, "<Button-1>", lambda e: self._new_game())
        c.tag_bind(self.new_id, "<Enter>",
                   lambda e: c.itemconfig(self.new_id, fill=self.C_ACCENT))
        c.tag_bind(self.new_id, "<Leave>",
                   lambda e: c.itemconfig(self.new_id, fill=self.C_TEXT_MUTED))

        # Focus entry on start
        self.entry.focus()

    # ── Bar ────────────────────────────────────────────

    def _update_bar(self):
        self.c.delete(self.bar_id)
        bx1, bx2, by = self.bx1, self.bx2, self.by
        total = 100
        lr = (self.low - 1) / total
        hr = self.high / total
        ax1 = bx1 + lr * (bx2 - bx1)
        ax2 = bx1 + hr * (bx2 - bx1)
        if ax2 - ax1 < 2:
            return
        self.bar_id = self._round_rect(self.c, ax1, by - 5, ax2, by + 5, r=5,
                                       fill=self.C_ACCENT, width=0)

    # ── History ─────────────────────────────────────────

    def _update_history(self):
        if not self.history:
            self.c.itemconfig(self.history_id, text="")
            return
        tokens = []
        for g, r in self.history[-8:]:
            if r == "correct":
                tokens.append(f"\u2713 {g} ")
            elif r == "low":
                tokens.append(f"\u25b2{g} ")
            else:
                tokens.append(f"\u25bc{g} ")
        self.c.itemconfig(self.history_id, text="".join(tokens))

    # ── Game logic ──────────────────────────────────────

    def _on_guess(self):
        if self.game_over:
            return

        raw = self.entry.get().strip()
        if not raw:
            messagebox.showwarning("\u63d0\u793a", "\u8acb\u5148\u8f38\u5165\u4e00\u500b\u6578\u5b57\uff01")
            return
        try:
            guess = int(raw)
        except ValueError:
            messagebox.showerror("\u932f\u8aa4", "\u8acb\u8f38\u5165\u6709\u6548\u7684\u6574\u6578\uff01")
            return
        if guess < self.low or guess > self.high:
            messagebox.showwarning(
                "\u63d0\u793a",
                f"\u8acb\u8f38\u5165 {self.low} ~ {self.high} \u4e4b\u9593\u7684\u6578\u5b57\uff01",
            )
            return

        self.attempts += 1
        self.entry.delete(0, tk.END)

        if guess == self.target:
            self.c.itemconfig(self.result_id,
                              text=f"\u2713 \u6b63\u78ba\uff01\u7b54\u6848\u662f {self.target}",
                              fill=self.C_SUCCESS)
            self.c.itemconfig(self.range_id,
                              text=f"\u7e3d\u5171\u731c\u4e86 {self.attempts} \u6b21",
                              fill=self.C_SUCCESS)
            self.c.itemconfig(self.btn_bg, fill="#2d6a4f")
            self.c.itemconfig(self.btn_text, text="\u731c\u4e2d\u4e86\uff01")
            self.entry.config(state=tk.DISABLED)
            self.game_over = True
            self.history.append((guess, "correct"))
            self._update_bar()

        elif guess < self.target:
            self.low = guess + 1
            self.c.itemconfig(self.result_id,
                              text=f"\u25b2 \u592a\u5c0f\u4e86  (\u5c0f\u65bc {self.target})",
                              fill=self.C_LOW)
            self.history.append((guess, "low"))

        else:
            self.high = guess - 1
            self.c.itemconfig(self.result_id,
                              text=f"\u25bc \u592a\u5927\u4e86  (\u5927\u65bc {self.target})",
                              fill=self.C_HIGH)
            self.history.append((guess, "high"))

        self.c.itemconfig(
            self.range_id,
            text=f"\u8acb\u731c {self.low} ~ {self.high} \u4e4b\u9593\u7684\u6578\u5b57",
            fill=self.C_TEXT,
        )
        self.c.itemconfig(self.attempt_id,
                          text=f"\u5df2\u731c\u6b21\u6578\uff1a{self.attempts}")
        self._update_bar()
        self._update_history()

    def _new_game(self):
        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.game_over = False
        self.history.clear()

        self.c.itemconfig(
            self.range_id,
            text=f"\u8acb\u731c {self.low} ~ {self.high} \u4e4b\u9593\u7684\u6578\u5b57",
            fill=self.C_TEXT,
        )
        self.c.itemconfig(self.result_id, text="")
        self.c.itemconfig(self.attempt_id,
                          text="\u5df2\u731c\u6b21\u6578\uff1a0")
        self.c.itemconfig(self.history_id, text="")
        self.c.itemconfig(self.btn_bg, fill=self.C_PRIMARY)
        self.c.itemconfig(self.btn_text, text="\u731c \uff01")
        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self._update_bar()


if __name__ == "__main__":
    root = tk.Tk()
    app = GuessGameGUI(root)
    root.mainloop()
