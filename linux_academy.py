#!/usr/bin/env python3
"""Linux Academy — Learn Linux the right way."""

import json
import random
import subprocess
from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
    Footer, Header, Input, Label, Markdown, Rule, Static, TextArea, Tree
)

from content import LESSONS, CATEGORIES, TIPS

DATA_DIR       = Path.home() / ".local/share/linux-academy"
PROGRESS_FILE  = DATA_DIR / "progress.json"
FAVORITES_FILE = DATA_DIR / "favorites.json"
NOTES_FILE     = DATA_DIR / "notes.json"

FLAT = [(cat, i) for cat in CATEGORIES for i in range(len(LESSONS[cat]))]

DIFF_ICON = {1: "🟢", 2: "🟡", 3: "🔴"}
DIFF_NAME = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}


# ─── Utilities ────────────────────────────────────────────────────────────────

def _pkey(cat: str, idx: int) -> str:
    return f"{cat}:{idx}"


def _load_set(path: Path) -> set:
    try:
        return set(json.loads(path.read_text()))
    except Exception:
        return set()


def _save_set(path: Path, data: set) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(data)))


def _load_dict(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_dict(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


def _copy_to_clipboard(text: str) -> bool:
    for cmd in [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-bi"]]:
        try:
            subprocess.run(cmd, input=text.encode(), check=True, timeout=2, capture_output=True)
            return True
        except Exception:
            continue
    return False


def _progress_bar(done: int, total: int, width: int = 18) -> str:
    if total == 0:
        return "░" * width
    filled = round(width * done / total)
    return "█" * filled + "░" * (width - filled)


# ─── Modals ───────────────────────────────────────────────────────────────────

class TipModal(ModalScreen):
    """Startup tip of the day."""

    def __init__(self, tip: dict) -> None:
        super().__init__()
        self._tip = tip

    def compose(self) -> ComposeResult:
        with Vertical(id="tip-dialog"):
            yield Static("🐧  LINUX ACADEMY", id="tip-logo")
            yield Static("Learn Linux the Right Way", id="tip-tagline")
            yield Rule()
            yield Static("✨  TIP OF THE DAY", id="tip-label")
            yield Static(self._tip["title"], id="tip-title")
            yield Markdown(f"```bash\n{self._tip['tip']}\n```", id="tip-body")
            yield Rule()
            yield Static("Press any key to start →", id="tip-hint")

    def on_key(self, _event) -> None:
        self.dismiss()


class HelpModal(ModalScreen):
    """Keyboard shortcuts reference."""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Static("⌨️   KEYBOARD SHORTCUTS", id="help-title")
            yield Rule()
            yield Markdown("""
## Navigation
| Key | Action |
|-----|--------|
| `↑` / `↓` | Move through lesson tree |
| `←` / `→` | Collapse / expand category |
| `n` / `j` | Next lesson (flows across categories) |
| `p` / `k` | Previous lesson |
| `u` | Jump to next **un**learned lesson |
| `r` | Jump to a random unlearned lesson |

## Filter by Difficulty
| Key | Action |
|-----|--------|
| `1` | Next unlearned 🟢 Beginner |
| `2` | Next unlearned 🟡 Intermediate |
| `3` | Next unlearned 🔴 Advanced |

## Actions
| Key | Action |
|-----|--------|
| `Space` | Mark / unmark lesson as learned ✓ |
| `f` | Toggle favorite ★ |
| `e` | Edit notes 📝 |
| `c` | Copy lesson to clipboard |
| `/` | Search all lessons |
| `?` | This help screen |
| `q` | Quit |

Progress, favorites, and notes live in
`~/.local/share/linux-academy/` — shared with the GUI.
""")
            yield Rule()
            yield Static("Press Esc or ? to close", id="help-hint")

    def on_key(self, event) -> None:
        if event.key in ("escape", "q", "question_mark"):
            self.dismiss()


class SearchModal(ModalScreen):
    """Full-text lesson search."""

    _results: list[tuple[str, int]] = []

    def compose(self) -> ComposeResult:
        from textual.widgets import ListView, ListItem
        with Vertical(id="search-dialog"):
            yield Static("🔍  Search Lessons", id="search-title")
            yield Input(placeholder="Type to search...", id="search-input")
            yield ListView(id="search-results")
            yield Static("↵ open   Esc cancel", id="search-hint")

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        from textual.widgets import ListView, ListItem
        lv = self.query_one("#search-results", ListView)
        lv.clear()
        self._results = []
        q = event.value.strip().lower()
        if not q:
            return
        for cat_name, lessons in LESSONS.items():
            for i, lesson in enumerate(lessons):
                if q in lesson["title"].lower() or q in lesson["body"].lower():
                    self._results.append((cat_name, i))
                    icon = cat_name.split()[0]
                    diff = lesson.get("difficulty", 2)
                    lv.append(ListItem(Label(f"  {icon}  {DIFF_ICON[diff]}  {lesson['title']}")))

    def on_list_view_selected(self, event) -> None:
        from textual.widgets import ListView
        idx = self.query_one("#search-results", ListView).index
        if idx is not None and 0 <= idx < len(self._results):
            self.dismiss(self._results[idx])

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class NotesModal(ModalScreen):
    """Per-lesson notes editor."""

    BINDINGS = [
        Binding("ctrl+s", "save_close", "Save"),
        Binding("escape", "save_close", "Close"),
    ]

    def __init__(self, lesson_title: str, current_notes: str) -> None:
        super().__init__()
        self._title = lesson_title
        self._notes = current_notes

    def compose(self) -> ComposeResult:
        with Vertical(id="notes-dialog"):
            yield Static(f"📝  {self._title}", id="notes-title")
            yield TextArea(self._notes, id="notes-ta")
            yield Static("Ctrl+S  ·  Esc  →  save & close", id="notes-hint")

    def on_mount(self) -> None:
        self.query_one("#notes-ta", TextArea).focus()

    def action_save_close(self) -> None:
        self.dismiss(self.query_one("#notes-ta", TextArea).text)


# ─── Tree widget ──────────────────────────────────────────────────────────────

class LessonTree(Tree):
    SHOW_ROOT = False

    def action_toggle_node(self) -> None:
        # Space on a lesson leaf marks it learned; on a category it expands/collapses.
        node = self.cursor_node
        if node is not None and isinstance(node.data, tuple):
            self.app.action_toggle_learned()
        else:
            super().action_toggle_node()


# ─── Main App ─────────────────────────────────────────────────────────────────

class LinuxAcademy(App):
    TITLE = "🐧 Linux Academy"
    CSS = """
    Screen { background: #0d1117; }

    Header { background: #010409; color: #58a6ff; text-style: bold; }
    Footer { background: #010409; color: #484f58; }

    /* ── Sidebar ── */
    #sidebar {
        width: 30;
        background: #0d1117;
        border-right: solid #21262d;
    }

    #sidebar-header {
        background: #010409;
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
        height: 1;
        border-bottom: solid #21262d;
    }

    LessonTree {
        background: #0d1117;
        padding: 0 1;
        scrollbar-size: 1 1;
        scrollbar-background: #0d1117;
        scrollbar-color: #30363d;
    }

    LessonTree .tree--guides          { color: #21262d; }
    LessonTree .tree--guides-hover    { color: #30363d; }
    LessonTree .tree--guides-selected { color: #388bfd; }
    LessonTree .tree--cursor          {
        background: #1f3a6e;
        color: #79c0ff;
        text-style: bold;
    }
    LessonTree .tree--highlight { background: #161b22; }

    #sidebar-footer {
        border-top: solid #21262d;
        padding: 1 2;
        height: 5;
        background: #010409;
    }

    #progress-label  { color: #484f58; text-style: bold; }
    #progress-bar-widget { color: #388bfd; }
    #progress-count  { color: #58a6ff; }

    /* ── Content area ── */
    #content-area { background: #0d1117; }

    #breadcrumb {
        background: #010409;
        border-bottom: solid #21262d;
        padding: 0 2;
        height: 1;
        color: #6e7681;
    }

    #content-scroll {
        background: #0d1117;
        padding: 1 3;
    }

    Markdown           { background: #0d1117; color: #e6edf3; }
    MarkdownH1         { color: #79c0ff; text-style: bold; }
    MarkdownH2         { color: #58a6ff; text-style: bold; }
    MarkdownH3         { color: #388bfd; }
    MarkdownCode       { background: #161b22; color: #e6edf3; }
    MarkdownCodeBlock  { background: #161b22; margin: 0 0 1 0; }
    MarkdownTableHeader { color: #79c0ff; text-style: bold; }

    #nav-bar {
        height: 3;
        background: #010409;
        border-top: solid #21262d;
        align: center middle;
        padding: 0 2;
    }

    #lesson-counter {
        color: #58a6ff;
        text-style: bold;
        width: 1fr;
        text-align: center;
    }

    Button {
        background: #21262d;
        color: #c9d1d9;
        border: tall #30363d;
        min-width: 10;
    }
    Button:hover { background: #30363d; color: #fff; border: tall #388bfd; }
    Button:focus { background: #30363d; border: tall #58a6ff; }

    /* ── Tip modal ── */
    TipModal { align: center middle; }

    #tip-dialog {
        background: #0d1117;
        border: double #58a6ff;
        padding: 1 3;
        width: 64;
        height: auto;
        max-height: 34;
    }

    #tip-logo    { color: #58a6ff; text-style: bold; text-align: center; }
    #tip-tagline { color: #484f58; text-align: center; padding-bottom: 0; }
    #tip-label   { color: #3fb950; text-style: bold; padding-top: 1; }
    #tip-title   { color: #e6edf3; text-style: bold; padding-bottom: 1; }
    #tip-body    { background: #0d1117; }
    #tip-hint    { color: #484f58; text-align: center; padding-top: 0; }

    /* ── Help modal ── */
    HelpModal { align: center middle; }

    #help-dialog {
        background: #0d1117;
        border: solid #30363d;
        padding: 1 2;
        width: 62;
        height: auto;
        max-height: 40;
    }

    #help-title { color: #58a6ff; text-style: bold; text-align: center; }
    #help-hint  { color: #484f58; text-align: center; padding-top: 1; }

    /* ── Search modal ── */
    SearchModal { align: center middle; }

    #search-dialog {
        background: #0d1117;
        border: solid #388bfd;
        padding: 1 2;
        width: 62;
        height: 22;
    }

    #search-title {
        color: #58a6ff;
        text-style: bold;
        text-align: center;
        border-bottom: solid #21262d;
        padding-bottom: 1;
    }

    #search-input {
        margin: 1 0;
        background: #161b22;
        border: solid #30363d;
        color: #e6edf3;
    }
    #search-input:focus { border: solid #388bfd; }

    #search-results { background: #161b22; height: 1fr; border: solid #21262d; }
    #search-results > ListItem { padding: 0 1; color: #8b949e; }
    #search-results > ListItem.--highlight { background: #1f3a6e; color: #79c0ff; }

    #search-hint { color: #484f58; text-align: center; padding-top: 1; }

    /* ── Notes modal ── */
    NotesModal { align: center middle; }

    #notes-dialog {
        background: #0d1117;
        border: solid #388bfd;
        padding: 1 2;
        width: 80;
        height: 26;
    }

    #notes-title {
        color: #58a6ff;
        text-style: bold;
        border-bottom: solid #21262d;
        padding-bottom: 1;
    }

    #notes-ta {
        height: 1fr;
        margin: 1 0;
        background: #161b22;
        color: #e6edf3;
    }

    #notes-hint {
        color: #484f58;
        text-align: center;
        border-top: solid #21262d;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("/", "search", "Search"),
        Binding("n", "next_lesson", "Next"),
        Binding("p", "prev_lesson", "Prev"),
        Binding("j", "next_lesson", show=False),
        Binding("k", "prev_lesson", show=False),
        Binding("space", "toggle_learned", "Learn"),
        Binding("f", "toggle_favorite", "Fav"),
        Binding("e", "edit_notes", "Notes"),
        Binding("r", "random_lesson", "Random"),
        Binding("u", "next_unlearned", "Next New"),
        Binding("c", "copy_lesson", "Copy"),
        Binding("question_mark", "help", "Help"),
        Binding("1", "diff_jump_1", show=False),
        Binding("2", "diff_jump_2", show=False),
        Binding("3", "diff_jump_3", show=False),
    ]

    _cat_index: int = 0
    _lesson_index: int = 0
    _progress: set = set()
    _favorites: set = set()
    _notes: dict = {}
    _cat_nodes: dict = {}
    _lesson_nodes: dict = {}

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static(" LINUX ACADEMY", id="sidebar-header")
                yield LessonTree("", id="lesson-tree")
                with Vertical(id="sidebar-footer"):
                    yield Static("PROGRESS", id="progress-label")
                    yield Static("", id="progress-bar-widget")
                    yield Static("", id="progress-count")
            with Vertical(id="content-area"):
                yield Static("", id="breadcrumb")
                with ScrollableContainer(id="content-scroll"):
                    yield Markdown("", id="content")
                with Horizontal(id="nav-bar"):
                    yield Static("", id="lesson-counter")
                    from textual.widgets import Button as Btn
                    yield Btn("◀  Prev", id="prev-btn")
                    yield Btn("Next  ▶", id="next-btn")
        yield Footer()

    # ── Mount ─────────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._progress  = _load_set(PROGRESS_FILE)
        self._favorites = _load_set(FAVORITES_FILE)
        self._notes     = _load_dict(NOTES_FILE)
        self._build_tree()
        self._update_content()
        self._update_progress_display()
        self.set_timer(0.05, lambda: self.push_screen(TipModal(random.choice(TIPS))))

    # ── Tree ──────────────────────────────────────────────────────────────────

    def _build_tree(self) -> None:
        tree = self.query_one("#lesson-tree", LessonTree)
        self._cat_nodes = {}
        self._lesson_nodes = {}

        for cat_name, lessons in LESSONS.items():
            done = sum(1 for i in range(len(lessons)) if _pkey(cat_name, i) in self._progress)
            cat_node = tree.root.add(self._cat_label(cat_name, done, len(lessons)), data=None)
            self._cat_nodes[cat_name] = cat_node
            for i, lesson in enumerate(lessons):
                leaf = cat_node.add_leaf(self._lesson_label(cat_name, i, lesson["title"]), data=(cat_name, i))
                self._lesson_nodes[_pkey(cat_name, i)] = leaf

        list(self._cat_nodes.values())[0].expand()
        self.set_timer(0.1, self._init_cursor)

    def _init_cursor(self) -> None:
        node = self._lesson_nodes.get(_pkey(CATEGORIES[0], 0))
        if node:
            self.query_one("#lesson-tree", LessonTree).move_cursor(node)

    def _cat_label(self, cat_name: str, done: int, total: int) -> Text:
        t = Text()
        t.append(cat_name)
        style = "bold green" if done == total and total > 0 else ("cyan" if done > 0 else "dim")
        t.append(f"  {done}/{total}", style=style)
        return t

    def _lesson_label(self, cat: str, idx: int, title: str) -> Text:
        key = _pkey(cat, idx)
        lesson = LESSONS[cat][idx]
        diff = lesson.get("difficulty", 2)
        t = Text()
        if key in self._progress:
            t.append("✓ ", style="bold green")
        else:
            t.append("  ")
        t.append(title)
        if key in self._favorites:
            t.append(" ★", style="bold yellow")
        if self._notes.get(key, "").strip():
            t.append(" 📝", style="dim")
        return t

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        data = event.node.data
        if not isinstance(data, tuple):
            return
        cat_name, idx = data
        new_cat = CATEGORIES.index(cat_name)
        if new_cat == self._cat_index and idx == self._lesson_index:
            return
        self._cat_index = new_cat
        self._lesson_index = idx
        self._update_content()

    # ── Content ───────────────────────────────────────────────────────────────

    def _update_content(self) -> None:
        cat = CATEGORIES[self._cat_index]
        lessons = LESSONS[cat]
        lesson = lessons[self._lesson_index]
        total = len(lessons)

        self.query_one("#content", Markdown).update(lesson["body"])
        self.query_one("#content-scroll", ScrollableContainer).scroll_home(animate=False)

        key = _pkey(cat, self._lesson_index)
        diff = lesson.get("difficulty", 2)
        mark = "✓ learned" if key in self._progress else "○ not learned"
        star = "  ★" if key in self._favorites else ""
        note = "  📝" if self._notes.get(key, "").strip() else ""
        self.query_one("#breadcrumb", Static).update(
            f" {DIFF_ICON[diff]} {DIFF_NAME[diff]}  ·  {cat}  ›  {lesson['title']}   [{mark}]{star}{note}"
        )
        self.query_one("#lesson-counter", Static).update(
            f"  {self._lesson_index + 1} / {total}  "
        )

    def _update_progress_display(self) -> None:
        total = sum(len(v) for v in LESSONS.values())
        done = len(self._progress)
        pct = int(100 * done / total) if total > 0 else 0
        self.query_one("#progress-bar-widget", Static).update(_progress_bar(done, total))
        self.query_one("#progress-count", Static).update(f"{done}/{total}  ({pct}%)")

    def _sync_tree_cursor(self) -> None:
        cat = CATEGORIES[self._cat_index]
        node = self._lesson_nodes.get(_pkey(cat, self._lesson_index))
        if node:
            cat_node = self._cat_nodes[cat]
            if not cat_node.is_expanded:
                cat_node.expand()
            self.query_one("#lesson-tree", LessonTree).move_cursor(node)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _goto(self, cat_name: str, idx: int) -> None:
        self._cat_index = CATEGORIES.index(cat_name)
        self._lesson_index = idx
        self._update_content()
        self._sync_tree_cursor()

    def action_next_lesson(self) -> None:
        pos = FLAT.index((CATEGORIES[self._cat_index], self._lesson_index))
        self._goto(*FLAT[(pos + 1) % len(FLAT)])

    def action_prev_lesson(self) -> None:
        pos = FLAT.index((CATEGORIES[self._cat_index], self._lesson_index))
        self._goto(*FLAT[(pos - 1) % len(FLAT)])

    def action_next_unlearned(self) -> None:
        pos = FLAT.index((CATEGORIES[self._cat_index], self._lesson_index))
        for step in range(1, len(FLAT) + 1):
            cat, idx = FLAT[(pos + step) % len(FLAT)]
            if _pkey(cat, idx) not in self._progress:
                self._goto(cat, idx)
                self.notify(f"→  {LESSONS[cat][idx]['title']}", timeout=3)
                return
        self.notify("🎉  Everything is learned!", timeout=3)

    def _jump_to_diff(self, level: int) -> None:
        pos = FLAT.index((CATEGORIES[self._cat_index], self._lesson_index))
        # First try: unlearned lessons of this difficulty
        for step in range(1, len(FLAT) + 1):
            cat, idx = FLAT[(pos + step) % len(FLAT)]
            lesson = LESSONS[cat][idx]
            if lesson.get("difficulty", 2) == level and _pkey(cat, idx) not in self._progress:
                self._goto(cat, idx)
                self.notify(f"{DIFF_ICON[level]} {DIFF_NAME[level]}: {lesson['title']}", timeout=3)
                return
        # Fallback: any lesson of this difficulty
        for cat, idx in FLAT:
            if LESSONS[cat][idx].get("difficulty", 2) == level:
                self._goto(cat, idx)
                self.notify(f"{DIFF_ICON[level]} All {DIFF_NAME[level]} lessons learned!", timeout=3)
                return
        self.notify(f"No {DIFF_NAME[level]} lessons found", severity="warning", timeout=3)

    def action_diff_jump_1(self) -> None: self._jump_to_diff(1)
    def action_diff_jump_2(self) -> None: self._jump_to_diff(2)
    def action_diff_jump_3(self) -> None: self._jump_to_diff(3)

    def action_toggle_learned(self) -> None:
        cat = CATEGORIES[self._cat_index]
        idx = self._lesson_index
        key = _pkey(cat, idx)
        lesson = LESSONS[cat][idx]

        if key in self._progress:
            self._progress.discard(key)
            msg, sev = "Unmarked", "warning"
        else:
            self._progress.add(key)
            msg, sev = f"✓  Learned: {lesson['title']}", "information"

        _save_set(PROGRESS_FILE, self._progress)
        self._lesson_nodes[key].label = self._lesson_label(cat, idx, lesson["title"])
        done = sum(1 for i in range(len(LESSONS[cat])) if _pkey(cat, i) in self._progress)
        self._cat_nodes[cat].label = self._cat_label(cat, done, len(LESSONS[cat]))
        self.query_one("#lesson-tree", LessonTree).refresh()
        self._update_content()
        self._update_progress_display()
        self.notify(msg, severity=sev, timeout=3)

    def action_toggle_favorite(self) -> None:
        cat = CATEGORIES[self._cat_index]
        idx = self._lesson_index
        key = _pkey(cat, idx)
        lesson = LESSONS[cat][idx]

        if key in self._favorites:
            self._favorites.discard(key)
            msg, sev = "☆  Removed from favorites", "warning"
        else:
            self._favorites.add(key)
            msg, sev = f"★  Favorited: {lesson['title']}", "information"

        _save_set(FAVORITES_FILE, self._favorites)
        self._lesson_nodes[key].label = self._lesson_label(cat, idx, lesson["title"])
        self.query_one("#lesson-tree", LessonTree).refresh()
        self._update_content()
        self.notify(msg, severity=sev, timeout=3)

    def action_edit_notes(self) -> None:
        cat = CATEGORIES[self._cat_index]
        idx = self._lesson_index
        key = _pkey(cat, idx)
        lesson = LESSONS[cat][idx]
        current = self._notes.get(key, "")

        def handle(result) -> None:
            if result is None:
                return
            if result.strip():
                self._notes[key] = result
            elif key in self._notes:
                del self._notes[key]
            _save_dict(NOTES_FILE, self._notes)
            self._lesson_nodes[key].label = self._lesson_label(cat, idx, lesson["title"])
            self.query_one("#lesson-tree", LessonTree).refresh()
            self._update_content()
            self.notify("📝  Notes saved", timeout=2)

        self.push_screen(NotesModal(lesson["title"], current), handle)

    def action_random_lesson(self) -> None:
        unlearned = [(c, i) for c, i in FLAT if _pkey(c, i) not in self._progress]
        cat_name, idx = random.choice(unlearned or FLAT)
        self._goto(cat_name, idx)
        self.notify(f"🎲  {LESSONS[cat_name][idx]['title']}", timeout=3)

    def action_copy_lesson(self) -> None:
        cat = CATEGORIES[self._cat_index]
        lesson = LESSONS[cat][self._lesson_index]
        text = f"# {lesson['title']}\n\n{lesson['body']}"
        if _copy_to_clipboard(text):
            self.notify("📋  Copied to clipboard!", timeout=2)
        else:
            self.notify("Install wl-copy or xclip for clipboard support", severity="error", timeout=4)

    def action_search(self) -> None:
        def handle(result) -> None:
            if result:
                self._goto(*result)
        self.push_screen(SearchModal(), handle)

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def on_button_pressed(self, event) -> None:
        if event.button.id == "next-btn":
            self.action_next_lesson()
        elif event.button.id == "prev-btn":
            self.action_prev_lesson()


if __name__ == "__main__":
    LinuxAcademy().run()
