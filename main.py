import tkinter as tk
import time
import random
import threading
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#lines for the color pallete, you can change them if you like :)
BG     = "#0c0c0c"    
SURF   = "#111111"    
BORDER = "#1f1f1f"    
FG     = "#c0c0c0"    
DIM    = "#404040"    
HI     = "#f0f0f0"    
GREEN  = "#3ddc84"    
RED    = "#e05757"    
BLUE   = "#4f8ef7"    
GRAPH  = "#3ddc84"    
WHITE =  "#ffffff"
MONO   = "Courier New" #this font gives of mr robot vibes u feel me

# this is like the backup if the API is unreachable, you can add new words here as well
FALLBACK: list[str] = [
    "the","be","to","of","and","a","in","that","have","it","for","not",
    "on","with","he","as","you","do","at","this","but","his","by","from",
    "they","we","say","her","she","or","an","will","my","one","all","would",
    "there","their","what","so","up","out","if","about","who","get","which",
    "go","me","when","make","can","like","time","no","just","him","know",
    "take","people","into","year","your","good","some","could","them","see",
    "other","than","then","now","look","only","come","its","over","think",
    "also","back","after","use","two","how","our","work","first","well",
    "way","even","new","want","because","any","these","give","day","most",
    "us","water","long","little","very","word","called","place","live",
    "every","found","still","learn","plant","cover","food","four","state",
    "keep","never","last","let","thought","city","tree","hard","start",
    "might","story","saw","far","sea","draw","left","late","run","while",
    "close","night","real","life","few","north","open","seem","together",
    "next","white","children","begin","got","walk","example","ease","paper",
    "often","always","music","those","both","mark","book","letter","until",
    "mile","river","car","feet","care","second","group","carry","took",
    "rain","eat","room","friend","began","idea","fish","mountain","stop",
    "once","base","hear","horse","cut","sure","watch","color","face","wood",
    "main","enough","plain","girl","young","ready","above","ever","red",
    "list","feel","talk","bird","soon","body","dog","family","leave","song",
    "door","black","short","wind","question","happen","complete","ship",
    "area","half","rock","order","fire","south","problem","piece","told",
    "knew","pass","since","top","whole","street","week","change","light",
    "voice","power","town","fine","drive","short","road","stand","strong",
    "form","cold","gold","already","done","plan","figure","hold","front",
    "build","force","love","point","play","small","number","off","always",
]


def fetch_words(n: int) -> str:
    try:
        resp = requests.get(
            f"https://random-word-api.vercel.app/api?words={n + 10}&type=lowercase",
            timeout=4,
        )
        if resp.status_code == 200:
            pool = [w for w in resp.json() if w.isalpha() and 2 <= len(w) <= 8]
            if len(pool) >= n:
                return " ".join(random.sample(pool, n))
    except Exception:
        pass
    return " ".join(random.sample(FALLBACK, min(n, len(FALLBACK))))



class App(tk.Tk):
    W, H = 940, 580
    PAD  = 52          # horizontal padding for content

    def __init__(self) -> None:
        super().__init__()
        self.title("Speed Type")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.target: str        = ""
        self.typed: list[str]   = []
        self.t_start: float|None = None
        self.history: list[tuple[float, int]] = []   # (elapsed_s, wpm)

        self._tick_id:  str|None = None
        self._blink_id: str|None = None
        self._cursor_on: bool    = True
        self._result_data: dict  = {}
        self._mpl_fig            = None

        self._frames: dict[str, tk.Frame] = {}
        self._build_start()
        self._build_test()
        self._build_result()
        self._show("start")

    def _show(self, name: str) -> None:
        for f in self._frames.values():
            f.place_forget()
        self._frames[name].place(x=0, y=0, width=self.W, height=self.H)
        self._frames[name].lift()

    def _hline(self, parent: tk.Widget, **place_kw) -> tk.Frame:
        bar = tk.Frame(parent, bg=BORDER, height=1)
        bar.place(**place_kw)
        return bar

    def _monolabel(
        self, parent, text="", size=10, weight="normal", fg=FG, **kw
    ) -> tk.Label:
        return tk.Label(
            parent, text=text, bg=BG, fg=fg,
            font=(MONO, size, weight), **kw
        )

    def _build_start(self) -> None:
        f = tk.Frame(self, bg=BG)
        self._frames["start"] = f
        self._hline(f, x=0, y=0, relwidth=1)
        self._hline(f, x=0, rely=1.0, y=-1, relwidth=1)
        hero = tk.Frame(f, bg=BG)
        hero.place(relx=0.5, rely=0.40, anchor="center")

        tk.Label(
            hero, text="SPEED TYPE", bg=BG, fg=HI,
            font=(MONO, 42, "bold"),
        ).pack()

        tk.Frame(hero, bg=BORDER, height=1).pack(fill="x", pady=(8, 0))

        tk.Label(
            hero, text="github: @shayaanthedev",
            bg=BG, fg=DIM, font=(MONO, 10),
        ).pack(pady=(7, 0))

        
        chips = tk.Frame(f, bg=BG)
        chips.place(relx=0.5, rely=0.63, anchor="center")

        for label in ("15 – 30 random words", "live WPM counter", "speed graph"):
            shell = tk.Frame(chips, bg=BORDER)
            shell.pack(side="left", padx=10)
            inner = tk.Frame(shell, bg=SURF)
            inner.pack(padx=1, pady=1)
            tk.Label(
                inner, text=f"  {label}  ",
                bg=SURF, fg=DIM, font=(MONO, 9), pady=5,
            ).pack()

        
        cta_shell = tk.Frame(f, bg=GREEN)
        cta_shell.place(relx=0.5, rely=0.82, anchor="center")
        tk.Label(
            cta_shell, text="   PRESS ENTER TO START   ",
            bg=GREEN, fg="#0c0c0c", font=(MONO, 12, "bold"), pady=9,
        ).pack()

        
        tk.Label(
            f, text="ESC  quit", bg=BG, fg=DIM, font=(MONO, 8),
        ).place(relx=0.5, rely=0.94, anchor="center")

        self.bind("<Return>", self._on_enter_start)
        self.bind("<Escape>", lambda _: self.destroy())

    def _on_enter_start(self, _=None) -> None:
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self._reset_state()
        self._show("test")
        self.bind("<Key>",    self._on_key)
        self.bind("<Escape>", self._restart)
        self._load_words()


    def _build_test(self) -> None:
        f = tk.Frame(self, bg=BG)
        self._frames["test"] = f

        hdr = tk.Frame(f, bg=BG, height=56)
        hdr.place(x=0, y=0, relwidth=1)
        self._hline(f, x=0, y=56, relwidth=1)

        for col, (key, attr) in enumerate([
            ("WPM",  "_ui_wpm"),
            ("ACC",  "_ui_acc"),
            ("TIME", "_ui_time"),
        ]):
            block = tk.Frame(hdr, bg=BG)
            block.place(x=self.PAD + col * 148, y=8)
            tk.Label(block, text=key, bg=BG, fg=DIM, font=(MONO, 8)).pack(anchor="w")
            val = tk.Label(block, text="–", bg=BG, fg=HI, font=(MONO, 20, "bold"))
            val.pack(anchor="w")
            setattr(self, attr, val)

        self._ui_progress = tk.Label(hdr, text="", bg=BG, fg=DIM, font=(MONO, 8))
        self._ui_progress.place(relx=1.0, x=-self.PAD, rely=0.5, anchor="e")

        BOX_Y      = 76
        BOX_HEIGHT = 170
        BOX_WIDTH  = self.W - self.PAD * 2

        shell = tk.Frame(f, bg=BORDER)
        shell.place(x=self.PAD, y=BOX_Y, width=BOX_WIDTH, height=BOX_HEIGHT)

        inner = tk.Frame(shell, bg=SURF)
        inner.place(x=1, y=1, width=BOX_WIDTH - 2, height=BOX_HEIGHT - 2)

        self._txt = tk.Text(
            inner,
            bg=SURF, fg=DIM,
            font=(MONO, 16),
            wrap="word",
            height=5,
            relief="flat",
            bd=0,
            state="disabled",
            cursor="arrow",
            spacing1=6,
            spacing3=6,
            padx=20,
            pady=14,
            insertbackground=SURF,
            selectbackground=SURF,
        )
        self._txt.pack(fill="both", expand=True)

        self._txt.tag_configure("correct", foreground=GREEN)
        self._txt.tag_configure("wrong",   foreground=RED, background="#2a1414")
        self._txt.tag_configure("cursor",  foreground=BG,  background=WHITE)
        self._txt.tag_configure("pending", foreground=DIM)
        self._txt.tag_configure("loading", foreground=DIM)

        self._ui_hint = tk.Label(
            f, text="loading words…", bg=BG, fg=DIM, font=(MONO, 9),
        )
        self._ui_hint.place(x=self.PAD, y=BOX_Y + BOX_HEIGHT + 12)

        self._hline(f, x=0, rely=1.0, y=-34, relwidth=1)
        tk.Label(
            f, text="ESC  quit / restart", bg=BG, fg=DIM, font=(MONO, 8),
        ).place(relx=0.5, rely=1.0, y=-17, anchor="center")


    def _load_words(self) -> None:
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.insert("end", "fetching words…", "loading")
        self._txt.config(state="disabled")
        self._ui_hint.config(text="loading words…")

        def _worker():
            n    = random.randint(15, 30)
            text = fetch_words(n)
            self.after(0, lambda: self._set_target(text))

        threading.Thread(target=_worker, daemon=True).start()

    def _set_target(self, text: str) -> None:
        self.target = text
        self._redraw()
        self._ui_hint.config(text="start typing…")
        self._start_blink()


    def _on_key(self, event: tk.Event) -> None:
        if not self.target:
            return

        ch  = event.char
        key = event.keysym

        if key == "BackSpace":
            if self.typed:
                self.typed.pop()
        elif key == "Escape":
            return  # handled by binding
        elif ch and len(ch) == 1 and ord(ch) >= 32:
            if len(self.typed) < len(self.target):
                if self.t_start is None:
                    self.t_start = time.time()
                    self._start_tick()
                self.typed.append(ch)
        else:
            return

        self._redraw()
        self._update_stats()

        if "".join(self.typed) == self.target:
            self._finish()

    def _redraw(self) -> None:
        td = self._txt
        td.config(state="normal")
        td.delete("1.0", "end")

        if not self.target:
            td.config(state="disabled")
            return

        n = len(self.typed)
        for i, ch in enumerate(self.target):
            if i < n:
                tag = "correct" if self.typed[i] == ch else "wrong"
                # show typed char (so wrong chars are still visible)
                td.insert("end", self.typed[i] if self.typed[i] == ch else ch, tag)
            elif i == n:
                td.insert("end", ch, "cursor" if self._cursor_on else "pending")
            else:
                td.insert("end", ch, "pending")

        td.config(state="disabled")

        done  = len(self.typed)
        total = len(self.target)
        pct   = done * 100 // total if total else 0
        self._ui_progress.config(text=f"{done}/{total}  {pct}%")

    def _update_stats(self) -> None:
        if not self.t_start:
            return
        elapsed = max(time.time() - self.t_start, 0.1)
        correct = sum(
            1 for i, c in enumerate(self.typed)
            if i < len(self.target) and c == self.target[i]
        )
        wpm = round((correct / 5) / (elapsed / 60))
        acc = round(correct / max(len(self.typed), 1) * 100)
        s   = int(elapsed)
        self._ui_wpm.config(text=str(wpm))
        self._ui_acc.config(text=f"{acc}%")
        self._ui_time.config(text=f"{s // 60}:{s % 60:02d}")


    def _start_tick(self) -> None:
        """Record a (elapsed, wpm) sample every second for the graph."""
        def _tick():
            if self.t_start:
                elapsed = time.time() - self.t_start
                correct = sum(
                    1 for i, c in enumerate(self.typed)
                    if i < len(self.target) and c == self.target[i]
                )
                wpm = round((correct / 5) / max(elapsed / 60, 0.001))
                self.history.append((round(elapsed, 1), wpm))
            self._tick_id = self.after(1000, _tick)

        self._tick_id = self.after(1000, _tick)

    def _start_blink(self) -> None:
        """Blink the cursor block every 530 ms."""
        def _blink():
            self._cursor_on  = not self._cursor_on
            self._redraw()
            self._blink_id = self.after(530, _blink)

        self._blink_id = self.after(530, _blink)

    def _cancel_timers(self) -> None:
        if self._tick_id:
            self.after_cancel(self._tick_id)
            self._tick_id = None
        if self._blink_id:
            self.after_cancel(self._blink_id)
            self._blink_id = None

    

    def _finish(self) -> None:
        self._cancel_timers()
        self.unbind("<Key>")

        elapsed = time.time() - self.t_start
        n       = len(self.typed)
        correct = sum(1 for i, c in enumerate(self.typed) if c == self.target[i])
        wpm     = round((correct / 5) / max(elapsed / 60, 0.001))
        acc     = round(correct / max(n, 1) * 100)
        s       = int(elapsed)

        self._result_data = {"wpm": wpm, "acc": acc, "s": s}
        self._show_result()

    def _restart(self, _=None) -> None:
        self._cancel_timers()
        self.unbind("<Key>")
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self._clear_graph()
        self._show("start")
        self.bind("<Return>", self._on_enter_start)
        self.bind("<Escape>", lambda _: self.destroy())

    def _reset_state(self) -> None:
        self.target   = ""
        self.typed    = []
        self.t_start  = None
        self.history  = []
        self._cursor_on = True
        for attr in ("_ui_wpm", "_ui_acc", "_ui_time"):
            try:
                getattr(self, attr).config(text="–")
            except Exception:
                pass
        try:
            self._ui_progress.config(text="")
        except Exception:
            pass


    def _build_result(self) -> None:
        f = tk.Frame(self, bg=BG)
        self._frames["result"] = f
        self._hline(f, x=0, y=54, relwidth=1)

        tk.Label(
            f, text="RESULT", bg=BG, fg=HI, font=(MONO, 13, "bold"),
        ).place(x=self.PAD, y=16)

        self._r_divider = tk.Frame(f, bg=BORDER, width=1, height=38)
        self._r_divider.place(x=self.PAD + 90, y=8)

        self._r_stats = tk.Label(f, text="", bg=BG, fg=FG, font=(MONO, 10))
        self._r_stats.place(x=self.PAD + 108, y=22)

        GW = self.W - self.PAD * 2
        GH = 440

        shell = tk.Frame(f, bg=BORDER)
        shell.place(x=self.PAD, y=66, width=GW, height=GH)

        self._graph_inner = tk.Frame(shell, bg=SURF)
        self._graph_inner.place(x=1, y=1, width=GW - 2, height=GH - 2)

        self._hline(f, x=0, rely=1.0, y=-34, relwidth=1)
        tk.Label(
            f, text="ENTER  try again    ESC  quit",
            bg=BG, fg=DIM, font=(MONO, 8),
        ).place(relx=0.5, rely=1.0, y=-17, anchor="center")

    def _show_result(self) -> None:
        d = self._result_data
        s = d["s"]
        self._r_stats.config(
            text=f"WPM  {d['wpm']}   ·   ACC  {d['acc']}%   ·   TIME  {s // 60}:{s % 60:02d}"
        )
        self._clear_graph()
        self._draw_graph()
        self._show("result")
        self.bind("<Return>", self._restart)
        self.bind("<Escape>", lambda _: self.destroy())


    def _draw_graph(self) -> None:
        inner = self._graph_inner
        GW    = self.W - self.PAD * 2 - 2
        GH    = 438

        if len(self.history) < 2:
            tk.Label(
                inner, text="not enough data — type longer next time",
                bg=SURF, fg=DIM, font=(MONO, 10),
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        times = [t for t, _ in self.history]
        wpms  = [w for _, w in self.history]
        avg   = round(sum(wpms) / len(wpms))
        peak  = max(wpms)

        fig = Figure(figsize=(GW / 100, GH / 100), dpi=100, facecolor=SURF)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(SURF)


        ax.plot(times, wpms, color=GRAPH, linewidth=2.2,
                zorder=3, solid_capstyle="round")
        ax.fill_between(times, wpms, alpha=0.07, color=GRAPH)
        ax.scatter(times, wpms, color=GRAPH, s=30, zorder=4, linewidths=0)

        ax.axhline(avg, color=DIM, linewidth=1, linestyle="--", zorder=2)
        ax.text(
            times[-1], avg + peak * 0.03,
            f"avg {avg}",
            color=DIM, fontsize=8, fontfamily="monospace", ha="right",
        )


        peak_t = times[wpms.index(peak)]
        ax.annotate(
            f"peak  {peak} wpm",
            xy=(peak_t, peak),
            xytext=(peak_t, peak + peak * 0.10),
            color=GRAPH, fontsize=9, fontfamily="monospace", ha="center",
            arrowprops=dict(arrowstyle="-", color=GRAPH, lw=1),
        )


        ax.set_xlabel("seconds elapsed",    color=DIM, fontsize=9, fontfamily="monospace")
        ax.set_ylabel("words per minute",   color=DIM, fontsize=9, fontfamily="monospace")
        ax.tick_params(colors=DIM, labelsize=9)
        ax.tick_params(axis="both", which="both", length=0)
        for spine in ax.spines.values():
            spine.set_color(BORDER)
        ax.grid(True, color=BORDER, linestyle="--", linewidth=0.6, alpha=0.8)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        fig.tight_layout(pad=1.8)

        canvas = FigureCanvasTkAgg(fig, master=inner)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mpl_canvas = canvas
        self._mpl_fig    = fig

    def _clear_graph(self) -> None:
        for widget in self._graph_inner.winfo_children():
            widget.destroy()
        if self._mpl_fig is not None:
            import matplotlib.pyplot as plt
            plt.close(self._mpl_fig)
            self._mpl_fig = None


if __name__ == "__main__":
    app = App()
    app.mainloop()
