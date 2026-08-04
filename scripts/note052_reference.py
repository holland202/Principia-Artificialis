#!/usr/bin/env python3
"""Reference code for note052_verification_that_cannot_fail.md.

Embeds four minimal fixtures reproducing the 2 Type A / 2 Type B split
from the 2026-07-26 finding, runs vacuity_lint against them, and asserts
the measured detection rate is exactly 2 of 4. Also asserts the P9/P10
anti-vacuity pair: zero findings on a clean tree, findings on a defective
one.

Requires vacuity_lint.py. It is looked for beside this script, one level
up, and in ~/vacuity-lint/. If none of those exist (cold clone, CI), it
is fetched from the pinned commit of the public vacuity_lint.py repo and
checked against a pinned SHA-256. A fetch or hash failure exits 1 --
the instrument is never silently skipped.
Exit 0 only if every assertion holds; any failure exits 1.
"""
import hashlib
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

# ---------------------------------------------------------------- fixtures

TYPE_A_1 = '''\
# verify_tomography.py — Type A: verification-shaped, runnable, no fail path
def verify(state):
    fidelity = 0.97
    if fidelity < 0.9:
        print("FIDELITY TOO LOW")
    print("verification complete")

if __name__ == "__main__":
    verify(None)
'''

TYPE_A_2 = '''\
# test_governance.py — Type A: named test_*, declares no test functions
def check_governance():
    return True

check_governance()
print("all governance checks done")
'''

TYPE_B_1 = '''\
# guard_generated.py — Type B: fail path exists, marker never written
MARKER = "# GENERATED"

def is_generated(path):
    with open(path) as f:
        head = f.read(200)
    if MARKER in head:
        raise SystemExit(1)  # fail path exists...
    return False             # ...but nothing ever writes MARKER

if __name__ == "__main__":
    import sys as _s
    is_generated(_s.argv[0])
    print("guard passed")
'''

TYPE_B_2 = '''\
# smoke_test.py — Type B: boolean branch dead, one condition implies another
def run():
    ran = True
    completed = True   # set together with ran, unconditionally
    if ran and not completed:
        raise SystemExit(1)   # unreachable: completed is never False when ran
    print("smoke test passed")

if __name__ == "__main__":
    run()
'''

CLEAN = '''\
# test_real.py — a genuine test with a real fail path
def test_addition():
    assert 1 + 1 == 2
'''


# Pinned so this script measures one fixed instrument, not whatever HEAD is.
LINT_COMMIT = "718d103bfdc1eea84d2a86a32853ae3472eb6675"
LINT_SHA256 = "028d48687615b998373279660e4022acfcaa1735ea682a3db83ef8bee940f0d9"
LINT_URL = (
    "https://raw.githubusercontent.com/holland202/vacuity_lint.py/"
    f"{LINT_COMMIT}/vacuity_lint.py"
)


def fetch_lint(dest):
    """Download the pinned linter to dest. Returns dest, or exits 1."""
    try:
        with urllib.request.urlopen(LINT_URL, timeout=30) as r:
            body = r.read()
    except (urllib.error.URLError, OSError) as e:
        sys.exit(
            f"vacuity_lint.py not found locally and fetch failed: {e}\n"
            f"  tried {LINT_URL}\n"
            "  place vacuity_lint.py beside this script and re-run"
        )
    got = hashlib.sha256(body).hexdigest()
    if got != LINT_SHA256:
        sys.exit(
            "fetched vacuity_lint.py does not match the pinned hash\n"
            f"  expected {LINT_SHA256}\n"
            f"  got      {got}"
        )
    with open(dest, "wb") as f:
        f.write(body)
    print(f"vacuity_lint.py fetched from pinned commit {LINT_COMMIT[:7]} "
          f"(sha256 verified)")
    return dest


def find_lint(workdir):
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (
        os.path.join(here, "vacuity_lint.py"),
        os.path.join(here, "..", "vacuity_lint.py"),
        os.path.expanduser("~/vacuity-lint/vacuity_lint.py"),
    ):
        if os.path.isfile(cand):
            print(f"vacuity_lint.py found locally: {cand}")
            return os.path.abspath(cand)
    return fetch_lint(os.path.join(workdir, "vacuity_lint.py"))


def scan(lint, tree):
    """Run the linter on a directory; return (exit_code, stdout+stderr)."""
    p = subprocess.run(
        [sys.executable, lint, tree],
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout + p.stderr


def write(tree, name, body):
    path = os.path.join(tree, name)
    with open(path, "w") as f:
        f.write(body)
    return path


def main():
    failures = []

    with tempfile.TemporaryDirectory() as td:
        lint = find_lint(td)
        # -- P9: clean tree yields zero findings ------------------------
        clean_tree = os.path.join(td, "clean")
        os.makedirs(clean_tree)
        write(clean_tree, "test_real.py", CLEAN)
        code, out = scan(lint, clean_tree)
        ok = code == 0
        print(f"[{'PASS' if ok else 'FAIL'}] P9  clean tree -> exit 0 "
              f"(got {code})")
        if not ok:
            failures.append("P9")

        # -- P10: defective tree yields findings ------------------------
        dirty_tree = os.path.join(td, "dirty")
        os.makedirs(dirty_tree)
        write(dirty_tree, "verify_tomography.py", TYPE_A_1)
        code, out = scan(lint, dirty_tree)
        ok = code != 0
        print(f"[{'PASS' if ok else 'FAIL'}] P10 defective tree -> nonzero "
              f"(got {code})")
        if not ok:
            failures.append("P10")

        # -- detection rate: 2 of 4 -------------------------------------
        caught = 0
        for label, body, expect_catch in (
            ("TypeA-1 verify, no fail path", TYPE_A_1, True),
            ("TypeA-2 test_* no test funcs", TYPE_A_2, True),
            ("TypeB-1 marker never written", TYPE_B_1, False),
            ("TypeB-2 dead boolean branch", TYPE_B_2, False),
        ):
            tree = tempfile.mkdtemp(dir=td)
            fname = ("test_governance.py" if "test_*" in label
                     else "verify_case.py" if "TypeA" in label
                     else "smoke_test.py" if "boolean" in label
                     else "guard_check.py")
            write(tree, fname, body)
            code, out = scan(lint, tree)
            detected = code != 0
            if detected:
                caught += 1
            agree = detected == expect_catch
            print(f"[{'PASS' if agree else 'FAIL'}] {label}: "
                  f"detected={detected}, expected={expect_catch}")
            if not agree:
                failures.append(label)

        print(f"\ndetection rate: {caught} of 4 "
              f"(expected 2 of 4 — every Type A, no Type B)")
        if caught != 2:
            failures.append("detection-rate")

    if failures:
        print(f"\nREFERENCE CHECK FAILED: {failures}")
        sys.exit(1)
    print("\nall reference checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
