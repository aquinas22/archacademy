#!/usr/bin/env python3
"""Linux Academy — Tkinter GUI. Stdlib only. Shares progress + notes with the TUI."""

import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from content import LESSONS, CATEGORIES, TIPS

DATA_DIR       = Path.home() / ".local/share/linux-academy"
PROGRESS_FILE  = DATA_DIR / "progress.json"
FAVORITES_FILE = DATA_DIR / "favorites.json"
NOTES_FILE     = DATA_DIR / "notes.json"

# GitHub-dark palette
BG       = "#0d1117"
BG_DARK  = "#010409"
BG_PANEL = "#161b22"
BORDER   = "#21262d"
FG       = "#e6edf3"
DIM      = "#8b949e"
DIMMER   = "#484f58"
BLUE     = "#58a6ff"
BLUE2    = "#388bfd"
CYAN     = "#79c0ff"
GREEN    = "#3fb950"
YELLOW   = "#e3b341"
RED      = "#ff7b72"
CODE_BG  = "#161b22"
SEL_BG   = "#1f3a6e"

MONO = ("JetBrains Mono", "DejaVu Sans Mono", "Consolas", "monospace")
SANS = ("Inter", "Segoe UI", "DejaVu Sans", "sans-serif")

DIFF_ICON = {1: "🟢", 2: "🟡", 3: "🔴"}
DIFF_NAME = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}


def pkey(cat, idx):
    return f"{cat}:{idx}"


def _set_window_icon(root):
    icon_path = Path(__file__).parent / "assets" / "tux-64.png"
    try:
        icon = tk.PhotoImage(file=str(icon_path))
        root.iconphoto(True, icon)
        root._tux_icon = icon  # keep a reference, Tk drops the image otherwise
    except Exception:
        pass


def load_set(path):
    try:
        return set(json.loads(path.read_text()))
    except Exception:
        return set()


def save_set(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(data)))


def load_dict(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def save_dict(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


class LinuxAcademyGUI:
    def __init__(self, root):
        self.root = root
        self.progress  = load_set(PROGRESS_FILE)
        self.favorites = load_set(FAVORITES_FILE)
        self.notes     = load_dict(NOTES_FILE)
        self.current   = (CATEGORIES[0], 0)
        self.diff_filter = 0  # 0=all, 1/2/3
        self.iid_map     = {}
        self.lesson_iids = {}
        self.cat_iids    = {}

        root.title("🐧 Linux Academy")
        root.geometry("1280x800")
        root.configure(bg=BG)
        root.minsize(960, 600)
        _set_window_icon(root)

        self._setup_styles()
        self._build_layout()
        self._populate_tree()
        self._show_tip()
        self._load_lesson(*self.current)
        self._update_progress()

        root.bind("<Control-f>",  lambda e: self.search_var.set("") or self.search_entry.focus())
        root.bind("<Right>",      lambda e: self._nav(1))
        root.bind("<Left>",       lambda e: self._nav(-1))
        root.bind("<Control-n>",  lambda e: self._nav(1))
        root.bind("<Control-p>",  lambda e: self._nav(-1))

    # ── Styling ──────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame",     background=BG)
        s.configure("Panel.TFrame", background=BG_DARK)
        s.configure("Side.TFrame",  background=BG)
        s.configure("TLabel",     background=BG, foreground=FG, font=(SANS, 10))
        s.configure("Head.TLabel",  background=BG_DARK, foreground=BLUE, font=(SANS, 11, "bold"))
        s.configure("Crumb.TLabel", background=BG_DARK, foreground=DIM,  font=(SANS, 10))
        s.configure("Dim.TLabel",   background=BG, foreground=DIMMER, font=(SANS, 8, "bold"))
        s.configure("Count.TLabel", background=BG, foreground=BLUE,  font=(MONO, 9))

        s.configure("Treeview", background=BG, fieldbackground=BG, foreground=FG,
                    borderwidth=0, font=(SANS, 10), rowheight=24)
        s.map("Treeview", background=[("selected", SEL_BG)], foreground=[("selected", CYAN)])
        s.configure("Treeview.Heading", background=BG_DARK, foreground=DIM)
        s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        s.configure("Accent.TButton", background=BORDER, foreground=FG,
                    font=(SANS, 9, "bold"), borderwidth=0, focuscolor=BG)
        s.map("Accent.TButton",
              background=[("active", BLUE2), ("pressed", BLUE)],
              foreground=[("active", "#ffffff")])

        s.configure("Bar.Horizontal.TProgressbar", troughcolor=BORDER,
                    background=BLUE2, borderwidth=0, thickness=10)

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_layout(self):
        # Top bar
        top = tk.Frame(self.root, bg=BG_DARK, height=46)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="  🐧 LINUX ACADEMY", bg=BG_DARK, fg=BLUE,
                 font=(SANS, 14, "bold")).pack(side="left", pady=8)
        tk.Label(top, text="Learn Linux the Right Way  ", bg=BG_DARK, fg=DIMMER,
                 font=(SANS, 10)).pack(side="right", pady=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(side="top", fill="both", expand=True)

        # ── Sidebar ──
        side = tk.Frame(body, bg=BG, width=330)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")

        # Search
        sf = tk.Frame(side, bg=BG)
        sf.pack(side="top", fill="x", padx=10, pady=(10, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_tree())
        self.search_entry = tk.Entry(
            sf, textvariable=self.search_var, bg=BG_PANEL, fg=FG,
            insertbackground=FG, relief="flat", font=(SANS, 10),
            highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE2)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Label(sf, text=" 🔍", bg=BG, fg=DIM).pack(side="right")

        # Difficulty filter buttons
        df = tk.Frame(side, bg=BG)
        df.pack(side="top", fill="x", padx=10, pady=(0, 6))
        tk.Label(df, text="FILTER:", bg=BG, fg=DIMMER,
                 font=(SANS, 8, "bold")).pack(side="left", padx=(0, 6))
        self._diff_btns = []
        for val, label, color in [
            (0, "All",  DIM),
            (1, "🟢 Beginner",      GREEN),
            (2, "🟡 Inter.",         YELLOW),
            (3, "🔴 Advanced",       RED),
        ]:
            btn = tk.Button(df, text=label, bg=BG_PANEL, fg=color,
                            font=(SANS, 8), relief="flat", bd=0,
                            padx=6, pady=2,
                            cursor="hand2",
                            command=lambda v=val: self._set_diff_filter(v))
            btn.pack(side="left", padx=2)
            self._diff_btns.append(btn)
        self._diff_btns[0].configure(bg=BLUE2, fg="#fff")  # "All" starts active

        # Tree
        tf = tk.Frame(side, bg=BG)
        tf.pack(side="top", fill="both", expand=True, padx=6, pady=4)
        self.tree = ttk.Treeview(tf, show="tree", selectmode="browse")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.tag_configure("cat",   foreground=DIM,   font=(SANS, 10, "bold"))
        self.tree.tag_configure("done",  foreground=GREEN)
        self.tree.tag_configure("lesson", foreground=FG)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Progress footer
        pf = tk.Frame(side, bg=BG_DARK, height=70)
        pf.pack(side="bottom", fill="x")
        pf.pack_propagate(False)
        tk.Label(pf, text="PROGRESS", bg=BG_DARK, fg=DIMMER,
                 font=(SANS, 8, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
        self.pbar = ttk.Progressbar(pf, style="Bar.Horizontal.TProgressbar", maximum=100)
        self.pbar.pack(fill="x", padx=14)
        self.pcount = tk.Label(pf, text="", bg=BG_DARK, fg=BLUE, font=(MONO, 9))
        self.pcount.pack(anchor="w", padx=14, pady=(3, 0))

        # ── Main content area ──
        main = tk.Frame(body, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        # Breadcrumb
        self.crumb = tk.Label(main, text="", bg=BG_DARK, fg=DIM, anchor="w",
                              font=(SANS, 10), padx=14)
        self.crumb.pack(side="top", fill="x", ipady=6)

        # Action bar (pack bottom first so notes + content fill correctly)
        bar = tk.Frame(main, bg=BG_DARK, height=52)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)
        inner = tk.Frame(bar, bg=BG_DARK)
        inner.pack(expand=True)
        for txt, cmd in [
            ("◀ Prev",        lambda: self._nav(-1)),
            ("✓ Mark Learned", self._toggle_learned),
            ("★ Favorite",    self._toggle_favorite),
            ("📋 Copy",        self._copy),
            ("🎲 Random",      self._random),
            ("⏭ Next New",    self._next_unlearned),
            ("Next ▶",        lambda: self._nav(1)),
        ]:
            ttk.Button(inner, text=txt, style="Accent.TButton",
                       command=cmd).pack(side="left", padx=4, pady=9, ipadx=6, ipady=3)

        # Notes panel (above action bar, below content)
        nf = tk.Frame(main, bg=BG_DARK, height=110)
        nf.pack(side="bottom", fill="x")
        nf.pack_propagate(False)
        tk.Frame(nf, bg=BORDER, height=1).pack(side="top", fill="x")
        nl = tk.Frame(nf, bg=BG_DARK)
        nl.pack(side="top", fill="x", padx=14, pady=(8, 4))
        tk.Label(nl, text="📝 MY NOTES", bg=BG_DARK, fg=DIMMER,
                 font=(SANS, 8, "bold")).pack(side="left")
        tk.Label(nl, text="  auto-saved", bg=BG_DARK, fg=DIMMER,
                 font=(SANS, 8)).pack(side="left")
        self.notes_text = tk.Text(
            nf, bg=BG_PANEL, fg=FG, relief="flat", font=(SANS, 10),
            padx=10, pady=6, insertbackground=FG, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=BLUE2,
            wrap="word", height=3)
        self.notes_text.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.notes_text.bind("<FocusOut>", self._save_notes_event)
        self.notes_text.bind("<KeyRelease>", self._save_notes_event)

        # Content text widget
        ct = tk.Frame(main, bg=BG)
        ct.pack(side="top", fill="both", expand=True)
        self.text = tk.Text(ct, bg=BG, fg=FG, relief="flat", wrap="word",
                            font=(SANS, 11), padx=24, pady=16,
                            spacing1=2, spacing3=4,
                            cursor="arrow", borderwidth=0, highlightthickness=0)
        tvsb = ttk.Scrollbar(ct, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=tvsb.set)
        self.text.pack(side="left", fill="both", expand=True)
        tvsb.pack(side="right", fill="y")
        self._setup_text_tags()
        self.text.configure(state="disabled")

    def _setup_text_tags(self):
        t = self.text
        t.tag_configure("h1", foreground=CYAN, font=(SANS, 18, "bold"), spacing3=10, spacing1=6)
        t.tag_configure("h2", foreground=BLUE, font=(SANS, 14, "bold"), spacing1=10, spacing3=6)
        t.tag_configure("h3", foreground=BLUE2, font=(SANS, 12, "bold"), spacing1=6, spacing3=4)
        t.tag_configure("body", foreground=FG, font=(SANS, 11))
        t.tag_configure("bold", foreground=FG, font=(SANS, 11, "bold"))
        t.tag_configure("code", foreground="#ffa657", font=(MONO, 10), background=CODE_BG)
        t.tag_configure("codeblock", foreground="#c9d1d9", font=(MONO, 10),
                        background=CODE_BG, lmargin1=20, lmargin2=20,
                        spacing1=0, spacing3=0, rmargin=20)
        t.tag_configure("comment", foreground=DIM, font=(MONO, 10), background=CODE_BG)
        t.tag_configure("kw",    foreground=BLUE, font=(MONO, 10, "bold"), background=CODE_BG)
        t.tag_configure("var",   foreground="#ffa657", font=(MONO, 10), background=CODE_BG)
        t.tag_configure("str",   foreground=GREEN, font=(MONO, 10), background=CODE_BG)
        t.tag_configure("flag",  foreground=YELLOW, font=(MONO, 10), background=CODE_BG)
        t.tag_configure("bullet", foreground=FG, font=(SANS, 11), lmargin1=18, lmargin2=32)
        t.tag_configure("table", foreground=CYAN, font=(MONO, 10))
        t.tag_configure("rule",  foreground=BORDER)

    # ── Tree ─────────────────────────────────────────────────────────────────
    def _populate_tree(self):
        for cat in CATEGORIES:
            done = sum(1 for i in range(len(LESSONS[cat])) if pkey(cat, i) in self.progress)
            cid = self.tree.insert(
                "", "end",
                text=f"{cat}  ({done}/{len(LESSONS[cat])})",
                open=(cat == CATEGORIES[0]),
                tags=("cat",))
            self.cat_iids[cat] = cid
            for i, lesson in enumerate(LESSONS[cat]):
                lid = self.tree.insert(cid, "end",
                                       text=self._lesson_text(cat, i),
                                       tags=("lesson",))
                self.iid_map[lid] = (cat, i)
                self.lesson_iids[pkey(cat, i)] = lid
        first = self.lesson_iids[pkey(CATEGORIES[0], 0)]
        self.tree.selection_set(first)
        self.tree.focus(first)

    def _lesson_text(self, cat, i):
        lesson = LESSONS[cat][i]
        diff = lesson.get("difficulty", 2)
        mark = "✓ " if pkey(cat, i) in self.progress else "   "
        star = "  ★" if pkey(cat, i) in self.favorites else ""
        note = "  📝" if self.notes.get(pkey(cat, i), "").strip() else ""
        return f"{mark}{DIFF_ICON[diff]} {lesson['title']}{star}{note}"

    def _refresh_tree_item(self, cat, i):
        self.tree.item(self.lesson_iids[pkey(cat, i)], text=self._lesson_text(cat, i))
        done = sum(1 for j in range(len(LESSONS[cat])) if pkey(cat, j) in self.progress)
        self.tree.item(self.cat_iids[cat],
                       text=f"{cat}  ({done}/{len(LESSONS[cat])})")

    def _set_diff_filter(self, level):
        self.diff_filter = level
        for i, btn in enumerate(self._diff_btns):
            if i == level:
                btn.configure(bg=BLUE2, fg="#fff")
            else:
                btn.configure(bg=BG_PANEL,
                              fg=[DIM, GREEN, YELLOW, RED][i])
        self._filter_tree()

    def _filter_tree(self):
        q = self.search_var.get().strip().lower()
        diff = self.diff_filter
        for cat in CATEGORIES:
            cat_has = False
            for i, lesson in enumerate(LESSONS[cat]):
                lid = self.lesson_iids[pkey(cat, i)]
                match_q = (not q) or (q in lesson["title"].lower() or q in lesson["body"].lower())
                match_d = (diff == 0) or (lesson.get("difficulty", 2) == diff)
                if match_q and match_d:
                    self.tree.reattach(lid, self.cat_iids[cat], "end")
                    cat_has = True
                else:
                    self.tree.detach(lid)
            self.tree.item(self.cat_iids[cat], open=bool(q or diff) and cat_has)

    def _on_select(self, _e):
        sel = self.tree.selection()
        if not sel:
            return
        data = self.iid_map.get(sel[0])
        if data:
            self._save_notes()
            self.current = data
            self._load_lesson(*data)

    # ── Content rendering ────────────────────────────────────────────────────
    def _load_lesson(self, cat, idx):
        lesson = LESSONS[cat][idx]
        diff = lesson.get("difficulty", 2)
        key = pkey(cat, idx)
        mark = "✓ learned" if key in self.progress else "○ not learned"
        star = "   ★ favorite" if key in self.favorites else ""
        note_ind = "  📝" if self.notes.get(key, "").strip() else ""
        self.crumb.configure(
            text=f"  {DIFF_ICON[diff]} {DIFF_NAME[diff]}  ·  {cat}  ›  {lesson['title']}      [{mark}]{star}{note_ind}"
        )

        t = self.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        self._render_markdown(lesson["body"])
        t.configure(state="disabled")
        t.yview_moveto(0)

        # Load notes
        self.notes_text.delete("1.0", "end")
        stored = self.notes.get(key, "")
        if stored:
            self.notes_text.insert("1.0", stored)

    def _render_markdown(self, md):
        t = self.text
        in_code = False
        for raw in md.split("\n"):
            line = raw.rstrip("\n")
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                self._render_code_line(line)
            elif line.startswith("# "):
                t.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                t.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("### "):
                t.insert("end", line[4:] + "\n", "h3")
            elif line.strip().startswith("|"):
                t.insert("end", line + "\n", "table")
            elif line.strip() == "---":
                t.insert("end", "─" * 60 + "\n", "rule")
            elif line.startswith("- ") or line.startswith("* "):
                t.insert("end", "  •  ", "bullet")
                self._render_inline(line[2:])
                t.insert("end", "\n")
            elif line.strip() == "":
                t.insert("end", "\n")
            else:
                self._render_inline(line)
                t.insert("end", "\n")

    _BASH_KW = frozenset([
        "if", "then", "else", "elif", "fi", "for", "while", "do", "done",
        "case", "esac", "function", "return", "local", "export", "source",
        "alias", "unset", "true", "false", "exit", "break", "continue",
        "in", "declare", "readonly", "typeset", "select", "shift", "until",
    ])

    def _render_code_line(self, line):
        t = self.text
        # Full comment line
        stripped = line.lstrip()
        if stripped.startswith("#"):
            t.insert("end", (line or " ") + "\n", "comment")
            return
        # Tokenize: comment, flag, $var, 'str', "str", keyword, plain
        i, n = 0, len(line)
        while i < n:
            ch = line[i]
            # Inline comment (preceded by whitespace)
            if ch == "#" and (i == 0 or line[i - 1] in " \t"):
                t.insert("end", line[i:] + "\n", "comment")
                return
            # Single-quoted string
            if ch == "'":
                j = line.find("'", i + 1)
                j = j if j != -1 else n - 1
                t.insert("end", line[i:j + 1], "str")
                i = j + 1
                continue
            # Double-quoted string
            if ch == '"':
                j = i + 1
                while j < n and line[j] != '"':
                    if line[j] == '\\':
                        j += 1
                    j += 1
                t.insert("end", line[i:j + 1], "str")
                i = j + 1
                continue
            # Variable
            if ch == "$":
                j = i + 1
                if j < n and line[j] == "{":
                    end = line.find("}", j)
                    j = (end + 1) if end != -1 else n
                elif j < n and line[j] == "(":
                    end = line.find(")", j)
                    j = (end + 1) if end != -1 else n
                else:
                    while j < n and (line[j].isalnum() or line[j] in "_#@*?!"):
                        j += 1
                t.insert("end", line[i:j], "var")
                i = j
                continue
            # Flag: -x or --long at word boundary
            if ch == "-" and (i == 0 or line[i - 1] in " \t(|&;") and i + 1 < n and line[i + 1] in "-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                j = i + 1
                while j < n and line[j] not in " \t\n|&;)":
                    j += 1
                t.insert("end", line[i:j], "flag")
                i = j
                continue
            # Word: keyword or plain
            if ch.isalpha() or ch == "_":
                j = i
                while j < n and (line[j].isalnum() or line[j] in "_.-"):
                    j += 1
                word = line[i:j]
                tag = "kw" if word in self._BASH_KW else "codeblock"
                t.insert("end", word, tag)
                i = j
                continue
            # Default
            t.insert("end", ch, "codeblock")
            i += 1
        t.insert("end", "\n")

    def _render_inline(self, text):
        t = self.text
        i, n = 0, len(text)
        while i < n:
            if text[i] == "`":
                end = text.find("`", i + 1)
                if end != -1:
                    t.insert("end", text[i + 1:end], "code")
                    i = end + 1
                    continue
            if text.startswith("**", i):
                end = text.find("**", i + 2)
                if end != -1:
                    t.insert("end", text[i + 2:end], "bold")
                    i = end + 2
                    continue
            t.insert("end", text[i], "body")
            i += 1

    # ── Notes ────────────────────────────────────────────────────────────────
    def _save_notes(self):
        cat, idx = self.current
        key = pkey(cat, idx)
        text = self.notes_text.get("1.0", "end-1c").strip()
        changed = False
        if text:
            if self.notes.get(key) != text:
                self.notes[key] = text
                changed = True
        elif key in self.notes:
            del self.notes[key]
            changed = True
        if changed:
            save_dict(NOTES_FILE, self.notes)
            self._refresh_tree_item(cat, idx)

    def _save_notes_event(self, _event=None):
        self._save_notes()

    # ── Actions ──────────────────────────────────────────────────────────────
    def _toggle_learned(self):
        cat, idx = self.current
        key = pkey(cat, idx)
        if key in self.progress:
            self.progress.discard(key)
        else:
            self.progress.add(key)
        save_set(PROGRESS_FILE, self.progress)
        self._refresh_tree_item(cat, idx)
        self._load_lesson(cat, idx)
        self._update_progress()

    def _toggle_favorite(self):
        cat, idx = self.current
        key = pkey(cat, idx)
        if key in self.favorites:
            self.favorites.discard(key)
        else:
            self.favorites.add(key)
        save_set(FAVORITES_FILE, self.favorites)
        self._refresh_tree_item(cat, idx)
        self._load_lesson(cat, idx)

    def _copy(self):
        cat, idx = self.current
        lesson = LESSONS[cat][idx]
        self.root.clipboard_clear()
        self.root.clipboard_append(f"# {lesson['title']}\n\n{lesson['body']}")
        old = self.crumb.cget("text")
        self.crumb.configure(text="  📋  Copied to clipboard!")
        self.root.after(1200, lambda: self.crumb.configure(text=old))

    def _random(self):
        unlearned = [(c, i) for c in CATEGORIES for i in range(len(LESSONS[c]))
                     if pkey(c, i) not in self.progress]
        pool = unlearned or [(c, i) for c in CATEGORIES for i in range(len(LESSONS[c]))]
        self._select_lesson(*random.choice(pool))

    def _next_unlearned(self):
        flat = [(c, i) for c in CATEGORIES for i in range(len(LESSONS[c]))]
        pos = flat.index(self.current)
        for step in range(1, len(flat) + 1):
            c, i = flat[(pos + step) % len(flat)]
            if pkey(c, i) not in self.progress:
                self._select_lesson(c, i)
                return
        old = self.crumb.cget("text")
        self.crumb.configure(text="  🎉 Everything is learned!")
        self.root.after(1800, lambda: self.crumb.configure(text=old))

    def _nav(self, delta):
        flat = [(c, i) for c in CATEGORIES for i in range(len(LESSONS[c]))]
        pos = flat.index(self.current)
        self._select_lesson(*flat[(pos + delta) % len(flat)])

    def _select_lesson(self, cat, idx):
        self._save_notes()
        lid = self.lesson_iids[pkey(cat, idx)]
        self.tree.item(self.cat_iids[cat], open=True)
        self.tree.selection_set(lid)
        self.tree.focus(lid)
        self.tree.see(lid)

    def _update_progress(self):
        total = sum(len(v) for v in LESSONS.values())
        done = len(self.progress)
        pct = int(100 * done / total) if total else 0
        self.pbar["value"] = pct
        self.pcount.configure(text=f"{done}/{total}   ({pct}%)")

    def _show_tip(self):
        tip = random.choice(TIPS)
        win = tk.Toplevel(self.root, bg=BG)
        win.title("Tip of the Day")
        win.configure(highlightbackground=BLUE, highlightthickness=2)
        w, h = 560, 300
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{max(x,0)}+{max(y,0)}")
        win.transient(self.root)
        tk.Label(win, text="🐧 LINUX ACADEMY", bg=BG, fg=BLUE,
                 font=(SANS, 16, "bold")).pack(pady=(22, 0))
        tk.Label(win, text="✨ TIP OF THE DAY", bg=BG, fg=GREEN,
                 font=(SANS, 10, "bold")).pack(pady=(14, 4))
        tk.Label(win, text=tip["title"], bg=BG, fg=FG,
                 font=(SANS, 12, "bold")).pack()
        tk.Label(win, text=tip["tip"], bg=CODE_BG, fg="#ffa657", font=(MONO, 10),
                 wraplength=500, justify="left", padx=14, pady=10).pack(
            pady=14, padx=24, fill="x")
        ttk.Button(win, text="Start learning →", style="Accent.TButton",
                   command=win.destroy).pack(pady=4, ipadx=8, ipady=3)
        win.bind("<Return>", lambda e: win.destroy())
        win.focus_set()


def main():
    root = tk.Tk()
    LinuxAcademyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
