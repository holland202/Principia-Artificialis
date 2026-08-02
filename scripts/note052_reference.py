#!/usr/bin/env python3
"""Reference code for note052_verification_that_cannot_fail.md.

Embeds four minimal fixtures reproducing the 2 Type A / 2 Type B split
from the 2026-07-26 finding, runs vacuity_lint against them, and asserts
the measured detection rate is exactly 2 of 4. Also asserts the P9/P10
anti-vacuity pair: zero findings on a clean tree, findings on a defective
one.

Requires vacuity_lint.py adjacent to this script or importable.
Exit 0 only if every assertion holds; any failure exits 1.
"""
import os
import subprocess
import sys
import tempfile

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


def find_lint():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (
        os.path.join(here, "vacuity_lint.py"),
        os.path.join(here, "..", "vacuity_lint.py"),
        os.path.expanduser("~/vacuity-lint/vacuity_lint.py"),
    ):
        if os.path.isfile(cand):
            return os.path.abspath(cand)
    sys.exit("vacuity_lint.py not found — place it beside this script")


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
    lint = find_lint()
    failures = []

    with tempfile.TemporaryDirectory() as td:
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
