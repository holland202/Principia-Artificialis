#!/usr/bin/env python3
"""patch_runner_gate.py — give scripts/run_all_notes.py a real verdict.

Three guarded string replacements:
  1. run_all_synthetic wraps each runner in try/except so a failing
     reference records status "synthetic_failed" instead of crashing
     with no report.
  2. __main__ prints a per-note verdict line including failures.
  3. The script exits 1 unless every synthetic status is "synthetic_ok"
     — the report is still written either way.

Protocol: each replacement requires EXACTLY one match or the patch
refuses and changes nothing. ast.parse verifies the result before it is
written. A .bak of the original is kept beside the file.
"""
import ast
import shutil
import sys

PATH = "scripts/run_all_notes.py"

REPLACEMENTS = [
    # 1 — guarded runner loop
    (
        """def run_all_synthetic():
    results = {}
    results['041'] = run_note041_synthetic()
    results['042'] = run_note042_synthetic()
    results['043'] = run_note043_synthetic()
    return results""",
        """def run_all_synthetic():
    results = {}
    for key, fn in (('041', run_note041_synthetic),
                    ('042', run_note042_synthetic),
                    ('043', run_note043_synthetic)):
        try:
            results[key] = fn()
        except Exception as e:
            results[key] = {"note": key, "status": "synthetic_failed",
                            "error": f"{type(e).__name__}: {e}"}
    return results""",
    ),
    # 2 — verdict-aware status print
    (
        """    for k in ['041','042','043']:
        print(f"Note #{k}: {syn[k]['status']}")""",
        """    for k in ['041','042','043']:
        line = f"Note #{k}: {syn[k]['status']}"
        if syn[k]['status'] != 'synthetic_ok':
            line += f" — {syn[k].get('error', 'no detail')}"
        print(line)""",
    ),
    # 3 — exit code carries the verdict
    (
        """    print("\\nReport saved to results/last_run_report.json")""",
        """    print("\\nReport saved to results/last_run_report.json")
    ok = all(v.get('status') == 'synthetic_ok' for v in syn.values())
    if not ok:
        print("SYNTHETIC RUN FAILED — see statuses above")
    sys.exit(0 if ok else 1)""",
    ),
]


def main():
    with open(PATH) as f:
        src = f.read()

    for i, (old, new) in enumerate(REPLACEMENTS, 1):
        n = src.count(old)
        if n != 1:
            sys.exit(f"REFUSED: replacement {i} matches {n} times "
                     f"(need exactly 1). File unchanged.")
        src = src.replace(old, new)

    try:
        ast.parse(src)
    except SyntaxError as e:
        sys.exit(f"REFUSED: patched source does not parse: {e}. "
                 f"File unchanged.")

    shutil.copy2(PATH, PATH + ".bak")
    with open(PATH, "w") as f:
        f.write(src)
    print(f"patched {PATH} (3 replacements, ast OK, backup at {PATH}.bak)")


if __name__ == "__main__":
    main()
