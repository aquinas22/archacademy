# Linux Academy — Feature Checklist

## Already shipped ✅

- [x] Three front-ends sharing one content source: **TUI** (Textual), **GUI** (Tkinter), **Web** (single HTML)
- [x] **116 lessons** across **17 categories**, including distro guidance, desktop/hardware, and security/reliability
- [x] **Readline / ZLE keybinding cheat sheets** for Bash and Zsh (Ctrl+R, Ctrl+X Ctrl+E, vi mode, custom `bindkey`)
- [x] **Databases & Servers** category — PostgreSQL, MySQL/MariaDB, SQLite, Redis, Nginx
- [x] **Make & Makefiles**, **GnuPG & OpenSSL** lessons
- [x] **Search match highlighting** (checklist idea #9) — bolds the matched substring in sidebar titles, tags body-only hits
- [x] **Difficulty levels** — 🟢 Beginner / 🟡 Intermediate / 🔴 Advanced on every lesson
- [x] **Bash syntax highlighting** in web app (keywords, builtins, strings, variables, flags, comments, operators)
- [x] **4 themes** — GitHub Dark, GitHub Light, Nord, Gruvbox (web app, persists)
- [x] **Per-lesson notes** — auto-saved (localStorage in web; shared notes.json for TUI + GUI)
- [x] **Difficulty filter** — sidebar pill buttons + keyboard `1/2/3`
- [x] Full-text search across every lesson
- [x] Progress tracking (`✓` mark) persisted to disk / localStorage
- [x] Favorites / bookmarks `★`
- [x] **Tip of the day** from 20 curated one-liners on startup
- [x] Random-lesson and next-unlearned jumps
- [x] `⏭ Next New` button (web + GUI) and `u` keyboard shortcut everywhere
- [x] Clipboard copy — lesson body or individual code blocks (web)
- [x] Progress bar + percentage (TUI & GUI) and animated SVG ring (web)
- [x] Keyboard-driven navigation everywhere
- [x] TUI and GUI **share the same progress / favorites / notes files**
- [x] `1/2/3` keys jump to next unlearned lesson of that difficulty (TUI + web)
- [x] Language tag shown on code blocks (web)

## Ideas for later

- [ ] **1. Interactive quizzes** — Multiple-choice or fill-in-the-blank after each lesson. Track a score.

- [ ] **2. Try-it sandbox** — Safe shell pane (or asciinema recording) where you can run commands from the current lesson without leaving the app.

- [ ] **3. Streaks & achievements** — Daily-learning streak counter and badges ("Pacman Master", "Network Ninja", "Docker Captain").

- [ ] **4. Spaced-repetition review** — Resurface lessons you marked learned a while ago (Anki-style intervals). A "Review Mode" that shows old lessons before new ones.

- [ ] **5. Custom learning paths** — "New to Linux", "Arch Install Day", "Sysadmin Bootcamp" guided tracks that order lessons by difficulty and dependency.

- [ ] **6. Command-of-the-day notification** — Optional desktop notification (or shell MOTD hook) that teaches one new command each morning.

- [ ] **7. Live system integration** — "Run on this machine" buttons that execute safe, read-only commands (`df -h`, `ip a`, `uname -r`) and display real output inline.

- [ ] **8. User-contributed lessons** — Load extra lessons from `~/.config/linux-academy/` drop-in folder so teams can add their own runbooks.

- [ ] **9. TUI theme switcher** — Port the 4 themes to the Textual TUI using CSS custom properties / `--variable` syntax.
