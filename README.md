# 🐧 Linux Academy

Learn Linux, Arch, Bash, Zsh, Networking, Git, Docker and more — three ways.
All three front-ends share the same lessons from `content.py`.

**116 lessons · 17 categories · 35 tips**

## Run it

```bash
# TUI (terminal — needs textual: pip install textual)
python3 linux_academy.py

# GUI (desktop window — stdlib tkinter, no install needed)
python3 linux_academy_gui.py

# Web app (no server — just open the file in a browser)
xdg-open index.html        # or double-click it
```

## Keyboard shortcuts

### TUI
| Key | Action |
|-----|--------|
| `↑↓` / `←→` | Navigate / expand-collapse tree |
| `n` / `p`   | Next / previous lesson (flows across categories) |
| `j` / `k`   | Same as n / p (vim style) |
| `u`          | Jump to next **un**learned lesson |
| `r`          | Jump to a random unlearned lesson |
| `Space`      | Mark / unmark learned ✓ |
| `f`          | Toggle favorite ★ |
| `e`          | Edit notes 📝 (Ctrl+S / Esc to save) |
| `1` / `2` / `3` | Jump to next unlearned 🟢 / 🟡 / 🔴 lesson |
| `c`          | Copy lesson to clipboard |
| `/`          | Search all lessons |
| `?`          | Help screen |
| `q`          | Quit |

### Web
| Key | Action |
|-----|--------|
| `n` / `p` / `j` / `k` | Navigate lessons |
| `l` / `Space` | Mark learned |
| `f` | Favorite |
| `u` | Next unlearned |
| `r` | Random lesson |
| `c` | Copy lesson |
| `e` | Focus notes textarea |
| `1` / `2` / `3` | Toggle difficulty filter |
| `/` | Focus search |

## Features

- **Difficulty levels** — every lesson tagged 🟢 Beginner / 🟡 Intermediate / 🔴 Advanced
- **Notes** — per-lesson notes, auto-saved (browser localStorage / shared JSON file for TUI+GUI)
- **Bash syntax highlighting** — keywords, builtins, strings, variables, flags, comments (web app)
- **4 themes** — GitHub Dark, GitHub Light, Nord, Gruvbox (web app — persists to localStorage)
- **Difficulty filter** — sidebar buttons to show only beginner / intermediate / advanced lessons
- **Full-text search** across all lesson titles and bodies
- **Progress tracking** — `✓` marks persist between sessions
- **Favorites** — `★` marks shared between TUI and GUI
- **Tip of the day** — random tip from 20 curated one-liners on startup
- **Random / next-unlearned** jumps for when you're not sure what to study
- **Clipboard** copy — copy any lesson's content

Progress, favorites, and notes live in `~/.local/share/linux-academy/` and are
shared between the TUI and GUI (web uses localStorage separately).

## Categories

| Category | Lessons |
|----------|---------|
| 🐧 Linux Basics | 9 |
| 📁 File System | 6 |
| 🏹 Arch Linux | 8 |
| 💻 Bash | 9 |
| 🔧 Zsh & Config | 7 |
| 🌐 Networking | 9 |
| ⚙️ System Admin | 8 |
| 🌿 Git | 6 |
| 🖥️ Tmux & Editors | 6 |
| 🐳 Docker | 8 |
| 🧰 CLI Power Tools | 8 |
| 🛠️ Dev Environments | 6 |
| 📦 Package Managers | 4 |
| 🗄️ Databases & Servers | 5 |
| 🛡️ Security & Reliability | 5 |
| 🧭 Distro Field Guide | 6 |
| 🖥️ Linux Desktop & Hardware | 6 |

## Editing content

`content.py` is the single source of truth. Edit lessons there, then rebuild
the web version:

```bash
python3 build_web.py       # regenerates index.html
```

The TUI and GUI pick up changes automatically (they import `content.py` directly).

## See `checklist.md`

Remaining feature ideas.
