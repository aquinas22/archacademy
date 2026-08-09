#!/usr/bin/env python3
"""Generate a self-contained index.html from content.py (no server needed)."""

import base64
import json
from pathlib import Path

from content import LESSONS, TIPS

TUX_B64 = base64.b64encode((Path(__file__).parent / "assets" / "tux-64.png").read_bytes()).decode()

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Linux Academy — Learn Linux by Doing</title>
<link rel="icon" type="image/png" href="data:image/png;base64,__TUX_B64__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Themes ─────────────────────────────────────────────────────────────────── */
:root,[data-theme="dark"] {
  --bg:#0d1117; --bg-dark:#010409; --panel:#161b22; --border:#21262d;
  --fg:#e6edf3; --dim:#8b949e; --dimmer:#484f58;
  --blue:#58a6ff; --blue2:#388bfd; --cyan:#79c0ff; --green:#3fb950;
  --yellow:#e3b341; --orange:#ffa657; --red:#ff7b72; --sel:#1f3a6e;
  --code-bg:#161b22; --code-fg:#c9d1d9;
  --sh-kw:#79c0ff; --sh-bi:#56d364; --sh-str:#a5d6ff; --sh-var:#ffa657;
  --sh-cm:#8b949e; --sh-flag:#e3b341; --sh-op:#6e7681; --sh-num:#e3b341;
}
[data-theme="light"] {
  --bg:#ffffff; --bg-dark:#f6f8fa; --panel:#f0f3f6; --border:#d0d7de;
  --fg:#24292f; --dim:#57606a; --dimmer:#8c959f;
  --blue:#0969da; --blue2:#0550ae; --cyan:#0550ae; --green:#1a7f37;
  --yellow:#9a6700; --orange:#bc4c00; --red:#cf222e; --sel:#dbeafe;
  --code-bg:#f0f3f6; --code-fg:#24292f;
  --sh-kw:#0550ae; --sh-bi:#1a7f37; --sh-str:#0a3069; --sh-var:#bc4c00;
  --sh-cm:#57606a; --sh-flag:#9a6700; --sh-op:#57606a; --sh-num:#9a6700;
}
[data-theme="nord"] {
  --bg:#2e3440; --bg-dark:#242933; --panel:#3b4252; --border:#434c5e;
  --fg:#eceff4; --dim:#d8dee9; --dimmer:#9aa3b2;
  --blue:#81a1c1; --blue2:#5e81ac; --cyan:#88c0d0; --green:#a3be8c;
  --yellow:#ebcb8b; --orange:#d08770; --red:#bf616a; --sel:#434c5e;
  --code-bg:#3b4252; --code-fg:#d8dee9;
  --sh-kw:#81a1c1; --sh-bi:#88c0d0; --sh-str:#a3be8c; --sh-var:#d08770;
  --sh-cm:#9aa3b2; --sh-flag:#ebcb8b; --sh-op:#9aa3b2; --sh-num:#ebcb8b;
}
[data-theme="gruvbox"] {
  --bg:#282828; --bg-dark:#1d2021; --panel:#3c3836; --border:#504945;
  --fg:#ebdbb2; --dim:#bdae93; --dimmer:#928374;
  --blue:#83a598; --blue2:#458588; --cyan:#8ec07c; --green:#b8bb26;
  --yellow:#fabd2f; --orange:#fe8019; --red:#fb4934; --sel:#504945;
  --code-bg:#3c3836; --code-fg:#d5c4a1;
  --sh-kw:#83a598; --sh-bi:#8ec07c; --sh-str:#b8bb26; --sh-var:#fe8019;
  --sh-cm:#928374; --sh-flag:#fabd2f; --sh-op:#928374; --sh-num:#fabd2f;
}

/* ── Base ───────────────────────────────────────────────────────────────────── */
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{
  background:var(--bg);color:var(--fg);
  font-family:'Inter',system-ui,'Segoe UI',sans-serif;
  height:100vh;overflow:hidden;display:flex;flex-direction:column;
  transition:background .2s,color .2s;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
}
::selection{background:var(--sel);}
:focus-visible{outline:2px solid var(--blue2);outline-offset:2px;}

/* ── Topbar ────────────────────────────────────────────────────────────────── */
.topbar{
  display:flex;align-items:center;gap:14px;
  background:var(--bg-dark);border-bottom:1px solid var(--border);
  padding:0 18px;height:52px;flex-shrink:0;
  box-shadow:0 1px 0 rgba(0,0,0,.15),0 4px 16px rgba(0,0,0,.12);
  position:relative;z-index:2;
}
.logo{font-size:17px;font-weight:800;color:var(--blue);letter-spacing:.4px;white-space:nowrap;display:flex;align-items:center;gap:8px;}
.logo-tux{width:24px;height:24px;object-fit:contain;vertical-align:middle;
  filter:drop-shadow(0 0 6px rgba(88,166,255,.35));}
.logo .tag{color:var(--dimmer);font-weight:400;font-size:12px;margin-left:10px;}
.kbd{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--dimmer);
  background:var(--border);padding:1px 5px;border-radius:3px;}
.spacer{flex:1;}
.ring-wrap{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.ring-wrap .pct{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--blue);white-space:nowrap;}
.ring{transform:rotate(-90deg);}
.ring circle{fill:none;stroke-width:5;}
.ring .bg{stroke:var(--border);}
.ring .fg{stroke:var(--blue2);stroke-linecap:round;transition:stroke-dashoffset .4s ease;}
.theme-select{
  background:var(--panel);color:var(--fg);border:1px solid var(--border);
  border-radius:6px;padding:5px 10px;font-size:13px;cursor:pointer;
  outline:none;transition:border-color .15s;
}
.theme-select:hover,.theme-select:focus{border-color:var(--blue2);}

/* ── Layout ────────────────────────────────────────────────────────────────── */
.body{display:flex;flex:1;min-height:0;}
.sidebar{
  width:320px;background:var(--bg);border-right:1px solid var(--border);
  display:flex;flex-direction:column;flex-shrink:0;
  box-shadow:2px 0 12px rgba(0,0,0,.1);position:relative;z-index:1;
}
.search-wrap{padding:12px 12px 0;}
.search{
  width:100%;padding:8px 12px;background:var(--panel);
  border:1px solid var(--border);border-radius:8px;color:var(--fg);
  font-size:13.5px;outline:none;transition:border-color .15s;
}
.search:focus{border-color:var(--blue2);}

/* Difficulty filter pills */
.diff-filter{display:flex;gap:6px;padding:10px 12px 8px;}
.df{
  padding:4px 10px;border:1px solid var(--border);border-radius:20px;
  font-size:12px;cursor:pointer;background:transparent;color:var(--dim);
  transition:all .15s;white-space:nowrap;
}
.df:hover{background:var(--panel);color:var(--fg);}
.df.active{background:var(--blue2);border-color:var(--blue2);color:#fff;}
.df.d1.active{background:var(--green);border-color:var(--green);}
.df.d2.active{background:var(--yellow);border-color:var(--yellow);color:#000;}
.df.d3.active{background:var(--red);border-color:var(--red);}

/* ── Tree ───────────────────────────────────────────────────────────────────── */
.tree{flex:1;overflow-y:auto;padding:0 6px 12px;}
.cat{
  display:flex;align-items:center;gap:6px;padding:7px 10px;cursor:pointer;
  color:var(--dim);font-weight:700;font-size:13.5px;border-radius:6px;
  user-select:none;transition:background .12s,color .12s;
}
.cat:hover{background:var(--panel);color:var(--fg);}
.cat .chev{font-size:10px;transition:transform .15s;color:var(--dimmer);flex-shrink:0;}
.cat.collapsed .chev{transform:rotate(-90deg);}
.cat .count{margin-left:auto;font-family:'JetBrains Mono',monospace;
  font-size:11px;font-weight:400;color:var(--dimmer);}
.cat.done .count{color:var(--green);}
.lessons{overflow:hidden;}
.cat.collapsed+.lessons{display:none;}
.lesson{
  display:flex;align-items:center;gap:6px;padding:6px 10px 6px 26px;
  cursor:pointer;color:var(--fg);font-size:13px;border-radius:6px;
  user-select:none;border-left:2px solid transparent;
  transition:background .12s,border-color .12s;
}
.lesson:hover{background:var(--panel);}
.lesson.active{background:var(--sel);color:var(--cyan);border-left-color:var(--blue);
  box-shadow:inset 0 0 0 1px rgba(88,166,255,.12);}
.lesson .check{width:14px;color:var(--green);font-weight:700;flex-shrink:0;font-size:11px;}
.lesson .ltitle{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.lesson .diff-dot{flex-shrink:0;font-size:10px;line-height:1;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--dimmer);box-shadow:0 0 0 3px color-mix(in srgb,currentColor 12%,transparent)}
.status-dot.d1{background:var(--green)}.status-dot.d2{background:var(--yellow)}.status-dot.d3{background:var(--red)}
.lesson .star{flex-shrink:0;color:var(--yellow);font-size:11px;}
.lesson .note-dot{flex-shrink:0;color:var(--dim);font-size:10px;}
.lesson .ltitle mark{background:var(--yellow);color:#000;border-radius:3px;padding:0 1px;}
.lesson .body-hit{flex-shrink:0;color:var(--dimmer);font-size:10px;font-style:italic;
  border:1px solid var(--border);border-radius:8px;padding:0 5px;}

/* Progress footer */
.pfoot{background:var(--bg-dark);border-top:1px solid var(--border);padding:12px 16px;}
.pfoot .label{font-size:10px;font-weight:700;color:var(--dimmer);letter-spacing:1px;}
.pbar{height:7px;background:var(--border);border-radius:4px;margin:8px 0 6px;overflow:hidden;}
.pbar .fill{height:100%;background:var(--blue2);border-radius:4px;transition:width .4s ease;}
.pfoot .ct{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--blue);}

/* ── Content ────────────────────────────────────────────────────────────────── */
.main{flex:1;display:flex;flex-direction:column;min-width:0;}
.crumb{
  background:var(--bg-dark);border-bottom:1px solid var(--border);
  padding:8px 22px;color:var(--dim);font-size:13px;flex-shrink:0;
  display:flex;align-items:center;gap:8px;
  white-space:nowrap;overflow:hidden;
}
.crumb .diff-badge{font-size:12px;padding:1px 7px;border-radius:10px;
  background:var(--panel);font-weight:600;color:var(--fg);flex-shrink:0;}
.crumb .trail{overflow:hidden;text-overflow:ellipsis;flex:1;}
.crumb .mark{color:var(--dimmer);}
.crumb .mark.learned{color:var(--green);}
.crumb .fav{color:var(--yellow);}
.content{flex:1;overflow-y:auto;padding:24px 40px 32px;max-width:940px;}
.content h1{color:var(--cyan);font-size:25px;margin:4px 0 16px;}
.content h2{color:var(--blue);font-size:18px;margin:24px 0 10px;
  padding-bottom:5px;border-bottom:1px solid var(--border);}
.content h3{color:var(--blue2);font-size:14.5px;margin:18px 0 8px;}
.content p{margin:8px 0;line-height:1.7;color:var(--code-fg);}
.content ul{margin:8px 0 8px 8px;}
.content li{margin:5px 0 5px 20px;line-height:1.6;color:var(--code-fg);}
.content hr{border:none;border-top:1px solid var(--border);margin:18px 0;}
.content code.inline{
  background:var(--panel);color:var(--orange);
  font-family:'JetBrains Mono',monospace;font-size:13px;
  padding:2px 6px;border-radius:5px;
}
.content strong{color:var(--fg);font-weight:700;}

/* ── Code blocks ─────────────────────────────────────────────────────────────── */
.codeblock{position:relative;margin:14px 0;border-radius:8px;overflow:hidden;
  border:1px solid var(--border);box-shadow:0 2px 10px rgba(0,0,0,.15);}
.codeblock .lang-tag{
  position:absolute;top:0;left:0;
  background:var(--border);color:var(--dimmer);
  font-family:'JetBrains Mono',monospace;font-size:10px;
  padding:3px 8px;border-bottom-right-radius:6px;
  letter-spacing:.5px;
}
.codeblock pre{
  background:var(--code-bg);padding:14px 16px 14px;overflow-x:auto;
  font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;
  color:var(--code-fg);
}
.codeblock .copy{
  position:absolute;top:8px;right:8px;background:var(--border);color:var(--dim);
  border:none;border-radius:5px;padding:4px 9px;font-size:11px;cursor:pointer;
  opacity:0;transition:opacity .15s,background .15s;
}
.codeblock:hover .copy{opacity:1;}
.codeblock .copy:hover{background:var(--blue2);color:#fff;}

/* Syntax highlighting */
.sh-kw  {color:var(--sh-kw);font-weight:600;}
.sh-bi  {color:var(--sh-bi);}
.sh-str {color:var(--sh-str);}
.sh-var {color:var(--sh-var);}
.sh-cm  {color:var(--sh-cm);font-style:italic;}
.sh-flag{color:var(--sh-flag);}
.sh-op  {color:var(--sh-op);}
.sh-num {color:var(--sh-num);}

/* ── Tables ─────────────────────────────────────────────────────────────────── */
table{border-collapse:collapse;margin:14px 0;width:auto;font-size:13.5px;}
th,td{border:1px solid var(--border);padding:7px 14px;text-align:left;}
th{background:var(--panel);color:var(--cyan);font-weight:700;}
td{color:var(--code-fg);}
td code,th code{background:var(--bg-dark);color:var(--orange);
  font-family:'JetBrains Mono',monospace;padding:1px 5px;border-radius:4px;}

/* ── Notes ──────────────────────────────────────────────────────────────────── */
.notes-wrap{
  border-top:1px solid var(--border);background:var(--bg-dark);
  padding:10px 22px;flex-shrink:0;
}
.notes-header{
  font-size:11px;font-weight:700;color:var(--dim);letter-spacing:.5px;
  margin-bottom:7px;display:flex;align-items:center;gap:8px;
}
.notes-header .hint{color:var(--dimmer);font-weight:400;}
#notesArea{
  width:100%;height:68px;background:var(--panel);color:var(--fg);
  border:1px solid var(--border);border-radius:6px;padding:8px 12px;
  font-family:inherit;font-size:13px;resize:vertical;outline:none;
  transition:border-color .15s;line-height:1.5;
}
#notesArea:focus{border-color:var(--blue2);}

/* ── Actions ────────────────────────────────────────────────────────────────── */
.actions{
  display:flex;gap:7px;justify-content:center;flex-wrap:wrap;
  background:var(--bg-dark);border-top:1px solid var(--border);
  padding:9px;flex-shrink:0;
}
.btn{
  background:var(--border);color:var(--fg);border:none;border-radius:7px;
  padding:7px 14px;font-size:13px;font-weight:600;cursor:pointer;
  transition:background .15s,color .15s,transform .1s,box-shadow .15s;
}
.btn:hover{background:var(--blue2);color:#fff;box-shadow:0 3px 10px rgba(56,139,253,.35);transform:translateY(-1px);}
.btn:active{transform:translateY(0);}
.btn.on{background:var(--green);color:#fff;}
.btn.fav.on{background:var(--yellow);color:#000;}

/* ── Modal ──────────────────────────────────────────────────────────────────── */
.overlay{
  position:fixed;inset:0;background:rgba(1,4,9,.72);display:flex;
  align-items:center;justify-content:center;z-index:100;
  backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);
}
.overlay.hidden{display:none;}
.modal{
  background:var(--bg);border:2px solid var(--blue);border-radius:14px;
  padding:30px 34px;max-width:560px;width:90%;text-align:center;
  box-shadow:0 20px 60px rgba(0,0,0,.55),0 0 0 1px rgba(88,166,255,.08);
  animation:modal-in .18s ease-out;
}
@keyframes modal-in{from{opacity:0;transform:translateY(8px) scale(.98);}to{opacity:1;transform:none;}}
.modal .ml{font-size:22px;font-weight:800;color:var(--blue);display:flex;align-items:center;justify-content:center;gap:10px;}
.modal .ml .logo-tux{width:30px;height:30px;}
.modal .tl{color:var(--green);font-weight:700;font-size:13px;margin:16px 0 8px;letter-spacing:1px;}
.modal .tt{font-size:16px;font-weight:700;margin-bottom:14px;}
.modal .tip-code{
  background:var(--panel);color:var(--orange);font-family:'JetBrains Mono',monospace;
  font-size:13px;padding:14px;border-radius:8px;text-align:left;line-height:1.5;
}
.modal .start{margin-top:18px;}

/* ── Toast ──────────────────────────────────────────────────────────────────── */
.toast{
  position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
  background:var(--panel);color:var(--fg);border:1px solid var(--blue2);
  padding:10px 20px;border-radius:8px;font-size:13px;opacity:0;
  transition:opacity .25s;pointer-events:none;z-index:200;white-space:nowrap;
}
.toast.show{opacity:1;}

/* ── Scrollbars ─────────────────────────────────────────────────────────────── */
.tree::-webkit-scrollbar,.content::-webkit-scrollbar{width:8px;}
.tree::-webkit-scrollbar-thumb,.content::-webkit-scrollbar-thumb{
  background:var(--border);border-radius:4px;}
.tree,.content{scrollbar-width:thin;scrollbar-color:var(--border) transparent;}

/* ── Content transition ─────────────────────────────────────────────────────── */
.content{animation:content-in .15s ease-out;}
@keyframes content-in{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}

/* ── 2026 refresh: a warmer, editorial learning workspace ─────────────────── */
:root,[data-theme="dark"]{
  --bg:#0b0f14;--bg-dark:#080b0f;--panel:#121820;--border:#26303b;
  --fg:#f2f5f7;--dim:#9ba7b4;--dimmer:#647180;--blue:#87a9ff;
  --blue2:#6f8fff;--cyan:#8de2cf;--green:#67d6a0;--yellow:#f2c86b;
  --orange:#ff9e7a;--red:#ff7f85;--sel:#1d2c43;
}
body{background:
  radial-gradient(circle at 82% -20%,rgba(111,143,255,.12),transparent 35%),var(--bg);}
.topbar{height:72px;padding:0 28px;background:rgba(8,11,15,.88);backdrop-filter:blur(18px);
  box-shadow:none;border-color:rgba(255,255,255,.08)}
.logo{font-size:15px;letter-spacing:.08em;color:var(--fg);gap:11px}
.logo-tux{width:34px;height:34px;filter:drop-shadow(0 5px 10px rgba(0,0,0,.4))}
.brand-copy{display:flex;flex-direction:column;gap:3px}.brand-copy small{font-size:10px;color:var(--dim);
  font-weight:500;letter-spacing:.06em;text-transform:none}
.logo .tag{display:none}
.ring-wrap{background:var(--panel);padding:7px 10px 7px 13px;border:1px solid var(--border);border-radius:999px}
.theme-select{border-radius:999px;padding:8px 13px;background:var(--panel)}
.sidebar{width:350px;background:rgba(11,15,20,.76);box-shadow:none;border-color:var(--border)}
.sidebar-intro{padding:22px 18px 5px}.eyebrow{font-size:10px;letter-spacing:.16em;color:var(--cyan);font-weight:800}
.sidebar-intro h2{font-size:21px;margin:7px 0 5px;letter-spacing:-.03em}.sidebar-intro p{font-size:12px;color:var(--dim);line-height:1.5}
.search-wrap{padding:14px 16px 0}.search{padding:11px 13px;border-radius:12px;background:var(--bg-dark)}
.diff-filter{padding:10px 16px 14px;gap:7px;overflow-x:auto}.df{padding:5px 9px;font-size:11px}
.tree{padding:0 10px 16px}.cat{padding:10px 11px;margin-top:2px}.lesson{padding:8px 10px 8px 28px;border-radius:9px}
.lesson.active{box-shadow:none;background:linear-gradient(90deg,rgba(111,143,255,.2),rgba(111,143,255,.06))}
.pfoot{padding:16px 20px;background:var(--bg-dark)}.pbar{height:5px}.pbar .fill{background:linear-gradient(90deg,var(--blue2),var(--cyan))}
.crumb{padding:12px 34px;background:rgba(8,11,15,.62)}.crumb .diff-badge{padding:4px 9px}
.content{max-width:900px;padding:42px 56px 60px;margin:0 auto;width:100%}
.content h1{font-size:38px;line-height:1.12;letter-spacing:-.045em;color:var(--fg);margin:6px 0 24px}
.content h2{font-size:21px;color:var(--cyan);margin-top:36px;padding-bottom:9px}
.content h3{font-size:16px;color:var(--blue);margin-top:26px}.content p{font-size:15.5px;line-height:1.82}
.content li{line-height:1.75}.codeblock{border-radius:14px;margin:20px 0;box-shadow:0 12px 35px rgba(0,0,0,.2)}
.codeblock pre{padding:22px 20px 18px;font-size:13px}.codeblock .copy{opacity:1;border:1px solid var(--border)}
table{width:100%;border-radius:10px;overflow:hidden}.notes-wrap{padding:12px 32px;background:var(--bg-dark)}
#notesArea{border-radius:10px;height:62px}.actions{padding:12px;background:rgba(8,11,15,.96)}
.btn{border:1px solid var(--border);border-radius:999px;padding:8px 15px;background:var(--panel)}
.modal{border:1px solid var(--border);padding:38px;border-radius:22px;text-align:left;background:var(--bg);
 box-shadow:0 32px 100px rgba(0,0,0,.7)}.modal .ml{justify-content:flex-start;color:var(--fg)}
.modal .tl{color:var(--cyan);margin-top:25px}.modal .tt{font-size:26px;letter-spacing:-.03em}.modal .tip-code{border:1px solid var(--border);border-radius:12px}
.lesson-meta{display:flex;align-items:center;gap:8px;padding:10px 34px;border-bottom:1px solid var(--border);
  background:color-mix(in srgb,var(--bg-dark) 72%,transparent);min-height:45px;overflow-x:auto;scrollbar-width:none}
.lesson-meta::-webkit-scrollbar{display:none}.meta-item,.tag-chip{font-size:11px;color:var(--dim);white-space:nowrap}
.meta-item{display:flex;align-items:center;gap:6px}.meta-item+.meta-item:before{content:"";width:3px;height:3px;border-radius:50%;background:var(--dimmer);margin-right:2px}
.tag-list{display:flex;gap:6px;margin-left:auto}.tag-chip{padding:4px 8px;border:1px solid var(--border);border-radius:999px;background:var(--panel)}
.search-wrap{position:relative}.search-wrap:before{content:"⌕";position:absolute;left:29px;top:25px;color:var(--dimmer);font-size:17px;pointer-events:none}
.search{padding-left:38px}.result-count{padding:0 18px 9px;color:var(--dimmer);font:10px 'JetBrains Mono',monospace;letter-spacing:.04em}
.empty-state{margin:28px 12px;padding:24px 16px;border:1px dashed var(--border);border-radius:12px;text-align:center;color:var(--dim);font-size:12px;line-height:1.6}
.empty-state strong{display:block;color:var(--fg);font-size:14px;margin-bottom:4px}.cat .chev{font-family:system-ui;transition:transform .18s ease}
.modal-close{position:absolute;top:16px;right:16px;width:32px;height:32px;border:1px solid var(--border);border-radius:50%;background:var(--panel);color:var(--dim);cursor:pointer;font-size:18px}
.modal-close:hover{color:var(--fg);border-color:var(--dimmer)}.modal{position:relative}.content>p:first-of-type{font-size:17px;color:var(--dim);line-height:1.75}
.content h2:target{scroll-margin-top:20px}.actions .btn:first-child,.actions .btn:last-child{min-width:82px}
.search::placeholder{color:var(--dimmer)}
@media(max-width:800px){body{height:auto;min-height:100vh;overflow:auto}.topbar{height:64px;padding:0 14px}.ring-wrap{display:none}
 .body{display:block}.sidebar{width:100%;height:auto;border-right:0;border-bottom:1px solid var(--border)}.sidebar-intro{padding-top:18px}
 .tree{max-height:280px}.pfoot{display:none}.main{min-height:70vh}.crumb{padding:10px 16px}.content{padding:30px 20px 45px}
 .lesson-meta{padding:9px 16px}.tag-list{display:none}.content h1{font-size:30px}.notes-wrap{padding:12px 16px}.actions{position:sticky;bottom:0;overflow-x:auto;justify-content:flex-start;flex-wrap:nowrap}
 .btn{white-space:nowrap}.theme-select{max-width:105px}}
</style>
</head>
<body>

<!-- Topbar -->
<div class="topbar">
  <div class="logo"><img src="data:image/png;base64,__TUX_B64__" alt="" class="logo-tux"><span class="brand-copy">LINUX ACADEMY<small>Learn the system. Own the terminal.</small></span>
    <span class="tag">
      <span class="kbd">n/p</span> nav ·
      <span class="kbd">l</span> learn ·
      <span class="kbd">f</span> fav ·
      <span class="kbd">r</span> random ·
      <span class="kbd">u</span> next new ·
      <span class="kbd">e</span> notes ·
      <span class="kbd">/</span> search ·
      <span class="kbd">1/2/3</span> difficulty
    </span>
  </div>
  <div class="spacer"></div>
  <div class="ring-wrap">
    <span class="pct" id="pct">0%</span>
    <svg class="ring" width="34" height="34" viewBox="0 0 34 34">
      <circle class="bg" cx="17" cy="17" r="14"></circle>
      <circle class="fg" id="ring" cx="17" cy="17" r="14"
              stroke-dasharray="87.96" stroke-dashoffset="87.96"></circle>
    </svg>
  </div>
  <select class="theme-select" id="themeSelect" onchange="setTheme(this.value)">
    <option value="dark">🌑 Dark</option>
    <option value="light">☀️ Light</option>
    <option value="nord">🌊 Nord</option>
    <option value="gruvbox">🌿 Gruvbox</option>
  </select>
</div>

<!-- Body -->
<div class="body">
  <aside class="sidebar">
    <div class="sidebar-intro"><div class="eyebrow">YOUR LEARNING PATH</div><h2>Build real Linux fluency.</h2><p>Practical lessons from first command to production systems.</p></div>
    <div class="search-wrap">
      <input class="search" id="search" placeholder="Search lessons...">
    </div>
    <!-- Difficulty filter -->
    <div class="diff-filter">
      <button class="df active"    onclick="filterDiff(0)">All</button>
      <button class="df d1"        onclick="filterDiff(1)"><span class="status-dot d1"></span> Beginner</button>
      <button class="df d2"        onclick="filterDiff(2)"><span class="status-dot d2"></span> Inter.</button>
      <button class="df d3"        onclick="filterDiff(3)"><span class="status-dot d3"></span> Advanced</button>
    </div>
    <div class="result-count" id="resultCount"></div>
    <div class="tree" id="tree"></div>
    <div class="pfoot">
      <div class="label">PROGRESS</div>
      <div class="pbar"><div class="fill" id="pfill"></div></div>
      <div class="ct" id="pct2">0/0 (0%)</div>
    </div>
  </aside>

  <main class="main">
    <div class="crumb" id="crumb"></div>
    <div class="lesson-meta" id="lessonMeta"></div>
    <div class="content" id="content"></div>
    <div class="notes-wrap">
      <div class="notes-header">MY NOTES <span class="hint">auto-saved to browser</span></div>
      <textarea id="notesArea" placeholder="Take notes on this lesson... (saved locally in your browser)"></textarea>
    </div>
    <div class="actions">
      <button class="btn" onclick="nav(-1)">← Prev</button>
      <button class="btn" id="learnBtn" onclick="toggleLearned()">✓ Mark Learned</button>
      <button class="btn fav" id="favBtn" onclick="toggleFav()">☆ Favorite</button>
      <button class="btn" onclick="copyLesson()">Copy</button>
      <button class="btn" onclick="randomLesson()">Random</button>
      <button class="btn" onclick="nextUnlearned()">Next new</button>
      <button class="btn" onclick="nav(1)">Next →</button>
    </div>
  </main>
</div>

<!-- Tip modal -->
<div class="overlay" id="tipOverlay">
  <div class="modal">
    <button class="modal-close" onclick="closeTip()" aria-label="Close tip">×</button>
    <div class="ml"><img src="data:image/png;base64,__TUX_B64__" alt="" class="logo-tux"> LINUX ACADEMY</div>
    <div class="tl">TIP OF THE DAY</div>
    <div class="tt" id="tipTitle"></div>
    <div class="tip-code" id="tipCode"></div>
    <button class="btn start" onclick="closeTip()">Start learning →</button>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const LESSONS = __LESSONS__;
const TIPS    = __TIPS__;
const CATS    = Object.keys(LESSONS);
const FLAT    = [];
CATS.forEach(c => LESSONS[c].forEach((_, i) => FLAT.push([c, i])));

let progress  = new Set(JSON.parse(localStorage.getItem('aa_progress')  || '[]'));
let favorites = new Set(JSON.parse(localStorage.getItem('aa_favorites') || '[]'));
let notes     = JSON.parse(localStorage.getItem('aa_notes') || '{}');
let cur       = [CATS[0], 0];
let curDiff   = 0;  // 0=all, 1/2/3
let curSearch = '';

const DIFF_NAME = ['', 'Beginner', 'Intermediate', 'Advanced'];
const DIFF_ICON = ['', '<span class="status-dot d1"></span>', '<span class="status-dot d2"></span>', '<span class="status-dot d3"></span>'];

const k = (c, i) => c + ':' + i;

function saveProgress() {
  localStorage.setItem('aa_progress',  JSON.stringify([...progress]));
  localStorage.setItem('aa_favorites', JSON.stringify([...favorites]));
}
function saveNotes() {
  localStorage.setItem('aa_notes', JSON.stringify(notes));
}

/* ── Theme ──────────────────────────────────────────────────────────────────── */
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('aa_theme', t);
  document.getElementById('themeSelect').value = t;
}
(function initTheme() {
  const t = localStorage.getItem('aa_theme') || 'dark';
  setTheme(t);
})();

/* ── Syntax highlighting ─────────────────────────────────────────────────────── */
const SH_KW = new Set([
  'if','then','else','elif','fi','for','while','do','done','case','esac',
  'function','return','local','export','source','alias','unset','true','false',
  'exit','break','continue','in','declare','readonly','typeset','select',
  'shift','until','trap','eval','exec',
]);
const SH_BI = new Set([
  'echo','printf','read','test','cd','pwd','ls','mkdir','rm','cp','mv',
  'cat','grep','find','sed','awk','sort','uniq','wc','head','tail','tr',
  'cut','xargs','tee','date','sleep','kill','which','type','curl','wget',
  'sudo','apt','pacman','pip','pip3','python','python3','git','ssh','scp',
  'rsync','chmod','chown','chgrp','touch','ln','stat','du','df','mount',
  'umount','ps','top','pkill','pgrep','systemctl','journalctl','ip','ping',
  'netstat','ss','docker','podman','make','gcc','go','node','npm','yarn',
  'cargo','rustc','tmux','vim','nvim','nano','less','more','man','bc',
  'expr','seq','tput','stty','basename','dirname','realpath','env',
  'pass','gpg','tar','gzip','gunzip','zip','unzip','diff','patch',
  'lsblk','fdisk','parted','mkfs','blkid','fstab','sysctl','modprobe',
  'lsmod','lspci','lsusb','nmcli','iwctl','wpa_supplicant','dhcpcd',
]);

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Keep emoji in persistent lesson keys, but present calmer editorial labels.
function cleanLabel(s) {
  return s.replace(/^[\p{Extended_Pictographic}\p{Emoji_Presentation}\uFE0F\u200D\s]+/u, '').trim();
}

function highlightMatch(text, q) {
  if (!q) return esc(text);
  const idx = text.toLowerCase().indexOf(q);
  if (idx === -1) return esc(text);
  return esc(text.slice(0, idx)) + '<mark>' + esc(text.slice(idx, idx + q.length)) + '</mark>' + esc(text.slice(idx + q.length));
}

function highlightLine(line) {
  let out = '', i = 0, n = line.length;
  while (i < n) {
    const ch = line[i];
    // Comment (only when preceded by whitespace or at start)
    if (ch === '#' && (i === 0 || /[\s\t(|&;]/.test(line[i-1]))) {
      out += '<span class="sh-cm">' + esc(line.slice(i)) + '</span>';
      return out;
    }
    // Single-quoted string
    if (ch === "'") {
      let j = i + 1;
      while (j < n && line[j] !== "'") j++;
      out += '<span class="sh-str">' + esc(line.slice(i, j+1)) + '</span>';
      i = j + 1; continue;
    }
    // Double-quoted string (with $VAR highlighting inside)
    if (ch === '"') {
      let j = i + 1;
      while (j < n && line[j] !== '"') { if (line[j] === '\\') j++; j++; }
      const raw = esc(line.slice(i, j+1));
      // Highlight $VAR / ${VAR} inside the already-escaped string
      const inner = raw.replace(
        /\$\{[^}]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*|\$[#@*?!0-9]/g,
        m => '<span class="sh-var">'+m+'</span>'
      );
      out += '<span class="sh-str">' + inner + '</span>';
      i = j + 1; continue;
    }
    // $(...) subshell or variable
    if (ch === '$') {
      let j = i + 1;
      if (j < n && line[j] === '(') {
        // $( ) — scan for balanced close, render whole thing as var
        let depth = 1; j++;
        while (j < n && depth > 0) {
          if (line[j] === '(') depth++;
          if (line[j] === ')') depth--;
          j++;
        }
      } else if (j < n && line[j] === '{') {
        let end = line.indexOf('}', j); j = end !== -1 ? end+1 : n;
      } else {
        while (j < n && /[a-zA-Z0-9_#@*?!]/.test(line[j])) j++;
      }
      out += '<span class="sh-var">' + esc(line.slice(i, j)) + '</span>';
      i = j; continue;
    }
    // Flag: -x or --long, preceded by space/start
    if (ch === '-' && (i === 0 || /[\s\t(|&;]/.test(line[i-1])) && i+1 < n && /[-a-zA-Z]/.test(line[i+1])) {
      let j = i + 1;
      while (j < n && /[a-zA-Z0-9_=-]/.test(line[j])) j++;
      out += '<span class="sh-flag">' + esc(line.slice(i, j)) + '</span>';
      i = j; continue;
    }
    // Operators
    if ('|&;<>(){}[]'.includes(ch)) {
      out += '<span class="sh-op">' + esc(ch) + '</span>';
      i++; continue;
    }
    // Word: keyword, builtin, or identifier
    if (/[a-zA-Z_]/.test(ch)) {
      let j = i;
      while (j < n && /[a-zA-Z0-9_\-\.\/]/.test(line[j])) j++;
      const w = line.slice(i, j);
      if (SH_KW.has(w))      out += '<span class="sh-kw">'+esc(w)+'</span>';
      else if (SH_BI.has(w)) out += '<span class="sh-bi">'+esc(w)+'</span>';
      else                    out += esc(w);
      i = j; continue;
    }
    // Number
    if (/[0-9]/.test(ch)) {
      let j = i;
      while (j < n && /[0-9.]/.test(line[j])) j++;
      out += '<span class="sh-num">'+esc(line.slice(i,j))+'</span>';
      i = j; continue;
    }
    out += esc(ch); i++;
  }
  return out;
}

const BASH_LANGS = new Set(['', 'bash', 'sh', 'shell', 'zsh', 'fish']);

function highlightCode(raw, lang) {
  if (BASH_LANGS.has(lang)) {
    return raw.split('\n').map(highlightLine).join('\n');
  }
  // Generic: only comment lines
  return raw.split('\n').map(line => {
    const t = line.trimStart();
    if (t.startsWith('#') || t.startsWith('//') || t.startsWith('--')) {
      return '<span class="sh-cm">'+esc(line)+'</span>';
    }
    if (t.startsWith('---') || t.match(/^[A-Z][A-Z_]+\s*:/)) {
      return '<span class="sh-kw">'+esc(line)+'</span>';  // YAML/Dockerfile keys
    }
    return esc(line);
  }).join('\n');
}

/* ── Markdown renderer ──────────────────────────────────────────────────────── */
function inline(s) {
  s = esc(s);
  s = s.replace(/`([^`]+)`/g, '<code class="inline">$1</code>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  return s;
}

function render(md) {
  const lines = md.split('\n');
  let html = '', i = 0;
  while (i < lines.length) {
    let line = lines[i];
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim().toLowerCase();
      const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) { code.push(lines[i]); i++; }
      i++;
      const highlighted = highlightCode(code.join('\n'), lang);
      const langTag = lang ? `<span class="lang-tag">${esc(lang)}</span>` : '';
      html += `<div class="codeblock">${langTag}<button class="copy" onclick="copyCode(this)">copy</button><pre>${highlighted}</pre></div>`;
      continue;
    }
    if (line.startsWith('### ')){ html += '<h3>'+inline(line.slice(4))+'</h3>'; i++; continue; }
    if (line.startsWith('## ')) { html += '<h2>'+inline(line.slice(3))+'</h2>'; i++; continue; }
    if (line.startsWith('# '))  { html += '<h1>'+inline(cleanLabel(line.slice(2)))+'</h1>'; i++; continue; }
    if (line.trim() === '---')  { html += '<hr>'; i++; continue; }
    if (line.trim().startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(lines[i]); i++; }
      html += renderTable(rows); continue;
    }
    if (/^[-*] /.test(line)) {
      const items = [];
      while (i < lines.length && /^[-*] /.test(lines[i])) { items.push(lines[i].slice(2)); i++; }
      html += '<ul>'+items.map(t => '<li>'+inline(t)+'</li>').join('')+'</ul>';
      continue;
    }
    if (line.trim() === '') { i++; continue; }
    html += '<p>'+inline(line)+'</p>'; i++;
  }
  return html;
}

function renderTable(rows) {
  const cells = r => r.trim().replace(/^\||\|$/g,'').split('|').map(c => c.trim());
  if (rows.length < 2) return '';
  const head = cells(rows[0]);
  let h = '<table><thead><tr>'+head.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>';
  for (let r = 2; r < rows.length; r++) {
    h += '<tr>'+cells(rows[r]).map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>';
  }
  return h + '</tbody></table>';
}

/* ── Sidebar tree ──────────────────────────────────────────────────────────── */
function buildTree() {
  const tree = document.getElementById('tree');
  tree.innerHTML = '';
  const q = curSearch;
  let visibleLessons = 0;
  CATS.forEach(cat => {
    const total = LESSONS[cat].length;
    const done  = LESSONS[cat].filter((_,i) => progress.has(k(cat,i))).length;
    let catVisible = false;

    const catEl = document.createElement('div');
    catEl.className = 'cat' + (done === total ? ' done' : '');
    catEl.innerHTML = '<span class="chev">⌄</span><span>'+esc(cleanLabel(cat))+'</span><span class="count">'+done+'/'+total+'</span>';
    catEl.onclick = () => catEl.classList.toggle('collapsed');
    tree.appendChild(catEl);

    const wrap = document.createElement('div');
    wrap.className = 'lessons';

    LESSONS[cat].forEach((lesson, i) => {
      const dl = lesson.difficulty || 2;
      const key = k(cat, i);
      // Filter by difficulty
      if (curDiff && dl !== curDiff) return;
      // Filter by search
      if (q && !lesson.title.toLowerCase().includes(q) && !lesson.body.toLowerCase().includes(q)) return;
      catVisible = true;
      visibleLessons++;

      const el = document.createElement('div');
      el.className = 'lesson' + (cur[0]===cat && cur[1]===i ? ' active' : '');
      el.dataset.key = key;
      const learned = progress.has(key), fav = favorites.has(key), hasNote = notes[key] && notes[key].trim();
      const titleHit = q && lesson.title.toLowerCase().includes(q);
      const bodyOnlyHit = q && !titleHit && lesson.body.toLowerCase().includes(q);
      el.innerHTML =
        '<span class="check">'+(learned?'✓':'')+'</span>'+
        '<span class="ltitle">'+highlightMatch(lesson.title, q)+'</span>'+
        (bodyOnlyHit ? '<span class="body-hit" title="Match found in lesson body">in body</span>' : '')+
        '<span class="diff-dot">'+DIFF_ICON[dl]+'</span>'+
        (hasNote ? '<span class="note-dot">📝</span>' : '')+
        (fav ? '<span class="star">★</span>' : '');
      el.onclick = () => load(cat, i);
      wrap.appendChild(el);
    });

    tree.appendChild(wrap);
    if (!catVisible) catEl.style.display = 'none';
    else catEl.style.display = '';
    if (q || curDiff) catEl.classList.remove('collapsed');
  });
  const noun = visibleLessons === 1 ? 'lesson' : 'lessons';
  document.getElementById('resultCount').textContent = visibleLessons+' '+noun+' shown';
  if (!visibleLessons) {
    tree.innerHTML = '<div class="empty-state"><strong>No lessons found</strong>Try a broader search or clear the difficulty filter.</div>';
  }
}

/* ── Load lesson ─────────────────────────────────────────────────────────────── */
function load(cat, i) {
  // Save current notes before switching
  if (cur[0] !== cat || cur[1] !== i) {
    const oldKey = k(cur[0], cur[1]);
    const val = document.getElementById('notesArea').value;
    if (val.trim()) { notes[oldKey] = val; saveNotes(); }
    else if (notes[oldKey]) { delete notes[oldKey]; saveNotes(); }
  }
  cur = [cat, i];
  localStorage.setItem('aa_last_lesson', JSON.stringify(cur));
  const lesson = LESSONS[cat][i];
  const dl = lesson.difficulty || 2;

  const contentEl = document.getElementById('content');
  contentEl.innerHTML = render(lesson.body);
  contentEl.scrollTop = 0;
  contentEl.style.animation = 'none';
  void contentEl.offsetWidth;
  contentEl.style.animation = '';

  const learned = progress.has(k(cat,i)), fav = favorites.has(k(cat,i));
  document.getElementById('crumb').innerHTML =
    '<span class="diff-badge">'+DIFF_ICON[dl]+' '+DIFF_NAME[dl]+'</span>'+
    '<span class="trail">'+esc(cleanLabel(cat))+' / '+esc(lesson.title)+
    '  <span class="mark'+(learned?' learned':'')+'">['+(learned?'✓ learned':'○ not learned')+']</span>'+
    (fav?' <span class="fav">★</span>':'')+
    '</span>';
  document.getElementById('learnBtn').className = 'btn'+(learned?' on':'');
  document.getElementById('learnBtn').textContent = learned ? '✓ Learned' : '✓ Mark Learned';
  document.getElementById('favBtn').className = 'btn fav'+(fav?' on':'');

  const words = lesson.body.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.ceil(words / 200));
  const position = FLAT.findIndex(([c,n]) => c===cat && n===i) + 1;
  document.getElementById('lessonMeta').innerHTML =
    '<span class="meta-item">Lesson '+position+' of '+FLAT.length+'</span>'+
    '<span class="meta-item">'+minutes+' min read</span>'+
    '<span class="meta-item">'+(lesson.body.match(/```/g)||[]).length/2+' examples</span>'+
    '<span class="tag-list">'+(lesson.tags||[]).slice(0,4).map(t=>'<span class="tag-chip">'+esc(t)+'</span>').join('')+'</span>';

  // Load notes for this lesson
  document.getElementById('notesArea').value = notes[k(cat,i)] || '';

  buildTree(); // rebuild to highlight active + update note dots
}

/* ── Notes auto-save ─────────────────────────────────────────────────────────── */
document.getElementById('notesArea').addEventListener('input', () => {
  const key = k(cur[0], cur[1]);
  const val = document.getElementById('notesArea').value;
  if (val.trim()) { notes[key] = val; }
  else { delete notes[key]; }
  saveNotes();
});

/* ── Actions ─────────────────────────────────────────────────────────────────── */
function toggleLearned() {
  const key = k(cur[0], cur[1]);
  progress.has(key) ? progress.delete(key) : progress.add(key);
  saveProgress(); load(cur[0], cur[1]); updateProgress();
  toast(progress.has(key) ? '✓ Marked as learned' : 'Unmarked');
}
function toggleFav() {
  const key = k(cur[0], cur[1]);
  favorites.has(key) ? favorites.delete(key) : favorites.add(key);
  saveProgress(); load(cur[0], cur[1]);
  toast(favorites.has(key) ? '★ Favorited' : '☆ Unfavorited');
}
function nav(d) {
  let pos = FLAT.findIndex(([c,i]) => c===cur[0] && i===cur[1]);
  pos = (pos + d + FLAT.length) % FLAT.length;
  load(FLAT[pos][0], FLAT[pos][1]);
}
function nextUnlearned() {
  let pos = FLAT.findIndex(([c,i]) => c===cur[0] && i===cur[1]);
  for (let s = 1; s <= FLAT.length; s++) {
    const [c,i] = FLAT[(pos+s)%FLAT.length];
    if (!progress.has(k(c,i))) { load(c,i); toast('⏭ '+LESSONS[c][i].title); return; }
  }
  toast('🎉 Everything is learned!');
}
function randomLesson() {
  const pool = FLAT.filter(([c,i]) => !progress.has(k(c,i)));
  const arr  = pool.length ? pool : FLAT;
  const [c,i] = arr[Math.floor(Math.random()*arr.length)];
  load(c,i); toast('🎲 '+LESSONS[c][i].title);
}
function copyLesson() {
  const l = LESSONS[cur[0]][cur[1]];
  navigator.clipboard.writeText('# '+l.title+'\n\n'+l.body);
  toast('📋 Copied lesson to clipboard');
}
function copyCode(btn) {
  navigator.clipboard.writeText(btn.parentElement.querySelector('pre').innerText);
  btn.textContent = 'copied!';
  setTimeout(() => btn.textContent = 'copy', 1200);
}

function updateProgress() {
  const total = FLAT.length, done = progress.size;
  const pct = total ? Math.round(100*done/total) : 0;
  document.getElementById('pfill').style.width = pct+'%';
  document.getElementById('pct').textContent  = pct+'%';
  document.getElementById('pct2').textContent = done+'/'+total+' ('+pct+'%)';
  const C = 2*Math.PI*14;
  document.getElementById('ring').style.strokeDashoffset = C*(1-pct/100);
}

/* ── Difficulty filter ───────────────────────────────────────────────────────── */
function filterDiff(d) {
  curDiff = d;
  document.querySelectorAll('.df').forEach((btn, i) => {
    btn.classList.toggle('active', i === d);
  });
  buildTree();
}

/* ── Search ─────────────────────────────────────────────────────────────────── */
document.getElementById('search').addEventListener('input', e => {
  curSearch = e.target.value.trim().toLowerCase();
  buildTree();
});

/* ── Keyboard ─────────────────────────────────────────────────────────────────── */
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault(); document.getElementById('search').focus(); return;
  }
  const tag = e.target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA') {
    if (e.key === 'Escape') e.target.blur();
    return;
  }
  if (!document.getElementById('tipOverlay').classList.contains('hidden')) {
    closeTip(); return;
  }
  const map = {
    'n': () => nav(1),    'j': () => nav(1),
    'p': () => nav(-1),   'k': () => nav(-1),
    'u': nextUnlearned,
    'r': randomLesson,
    'c': copyLesson,
    'f': toggleFav,
    '1': () => filterDiff(curDiff===1 ? 0 : 1),
    '2': () => filterDiff(curDiff===2 ? 0 : 2),
    '3': () => filterDiff(curDiff===3 ? 0 : 3),
    'e': () => { e.preventDefault(); document.getElementById('notesArea').focus(); },
    '/': () => { e.preventDefault(); document.getElementById('search').focus(); },
  };
  if (e.key === 'l' || e.key === ' ') { e.preventDefault(); toggleLearned(); return; }
  if (map[e.key]) { map[e.key](); }
});

/* ── Toast ───────────────────────────────────────────────────────────────────── */
let toastT;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg; el.classList.add('show');
  clearTimeout(toastT);
  toastT = setTimeout(() => el.classList.remove('show'), 2000);
}

/* ── Tip modal ───────────────────────────────────────────────────────────────── */
function showTip() {
  const tip = TIPS[Math.floor(Math.random()*TIPS.length)];
  document.getElementById('tipTitle').textContent = tip.title;
  document.getElementById('tipCode').textContent  = tip.tip;
}
function closeTip() { document.getElementById('tipOverlay').classList.add('hidden'); }

/* ── Init ───────────────────────────────────────────────────────────────────── */
const today = new Date().toISOString().slice(0,10);
if (localStorage.getItem('aa_tip_seen') === today) {
  document.getElementById('tipOverlay').classList.add('hidden');
} else {
  localStorage.setItem('aa_tip_seen', today);
  showTip();
}
buildTree();
let start = [CATS[0], 0];
try {
  const saved = JSON.parse(localStorage.getItem('aa_last_lesson'));
  if (saved && LESSONS[saved[0]] && LESSONS[saved[0]][saved[1]]) start = saved;
} catch (_) {}
load(start[0], start[1]);
updateProgress();
</script>
</body>
</html>
"""


def main():
    html = TEMPLATE.replace("__LESSONS__", json.dumps(LESSONS, ensure_ascii=False))
    html = html.replace("__TIPS__",    json.dumps(TIPS,    ensure_ascii=False))
    html = html.replace("__TUX_B64__", TUX_B64)
    with open("index.html", "w") as f:
        f.write(html)
    total = sum(len(v) for v in LESSONS.values())
    size  = len(html) // 1024
    print(f"Wrote index.html — {total} lessons across {len(LESSONS)} categories, {len(TIPS)} tips, {size} KB")


if __name__ == "__main__":
    main()
