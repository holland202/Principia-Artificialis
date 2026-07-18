"""Self-regenerating notes index for Principia Artificialis.
Parses every research_notes/note*.md for its title / status / theme /
author lines and writes NOTES_INDEX.md. The notes themselves are the
source of truth — the index can never silently go stale or vanish.
Run from repo root:  python scripts/make_index.py
"""
import re, glob, os, datetime

rows = []
for path in sorted(glob.glob("research_notes/note*.md")):
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^#\s*Note\s*#?(\d+)\s*[—–-]\s*(.+)$", txt, re.M)
    num = m.group(1) if m else re.sub(r"\D", "", os.path.basename(path))[:3]
    title = (m.group(2).strip() if m
             else os.path.basename(path).replace(".md", ""))
    def grab(label):
        g = re.search(rf"\*\*{label}:\*\*\s*(.+)", txt)
        return re.sub(r"\s+", " ", g.group(1)).strip() if g else "—"
    status = grab("Status")
    theme  = grab("Theme")
    author = grab("Author")
    # compact long fields for the table
    status_short = re.split(r"[;(]", status)[0].strip()
    if "REFUT" in status.upper() or "FAILED" in status.upper():
        status_short += " ⚠ refutation kept"
    author_short = re.split(r"[—–,(]", author)[0].strip() or author
    link = f"[{title}]({path})"
    rows.append((int(num) if num.isdigit() else 999,
                 num, link, status_short, theme, author_short))

rows.sort()
today = datetime.date.today().isoformat()
out = ["# Notes Index",
       "",
       f"*Auto-generated from the notes themselves by "
       f"`scripts/make_index.py` on {today} — do not edit by hand; "
       f"edit the notes and re-run.*",
       "",
       f"**{len(rows)} notes indexed.** Statuses are read verbatim from "
       f"each note's own header; ⚠ marks notes that registered a claim, "
       f"failed it, and kept the failure (a first-class outcome here).",
       "",
       "| # | Note | Status | Theme | Author |",
       "|---|---|---|---|---|"]
for _, num, link, status, theme, author in rows:
    out.append(f"| #{num} | {link} | {status} | {theme} | {author} |")
open("NOTES_INDEX.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"NOTES_INDEX.md written: {len(rows)} notes")
for _, num, link, status, *_ in rows[:6]:
    print(f"  #{num}  {status}")
