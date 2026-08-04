#!/usr/bin/env python3
"""Append reciprocal collision footers to every ⚡ pair in NOTES_INDEX.md.
Dry-run by default; pass --apply to write. Idempotent: skips files that
already contain 'Number collision:'."""
import re, sys, pathlib

apply = "--apply" in sys.argv
idx = pathlib.Path("NOTES_INDEX.md").read_text(encoding="utf-8")
groups = {}
for m in re.finditer(r'^\| #(\d+) ⚡ \| \[[^\]]*\]\((research_notes/[^)]+\.md)\)', idx, re.M):
    groups.setdefault(m.group(1), []).append(pathlib.Path(m.group(2)))

planned = skipped = 0
for num, files in sorted(groups.items()):
    if len(files) < 2:
        print(f"WARN #{num}: only {len(files)} file(s) matched — check regex"); continue
    for f in files:
        text = f.read_text(encoding="utf-8")
        if "Number collision:" in text:
            skipped += 1; continue
        others = " and ".join(f"[[{o.stem}]]" for o in files if o != f)
        footer = (f"\n---\n*Number collision: #{num} is also claimed by "
                  f"{others}. Displayed, not resolved.*\n")
        planned += 1
        print(f"{'APPEND' if apply else 'would append'} -> {f}  (links: {others})")
        if apply:
            f.write_text(text + footer, encoding="utf-8")
print(f"\n{len(groups)} collided numbers · {planned} {'appended' if apply else 'planned'} · {skipped} already done")
