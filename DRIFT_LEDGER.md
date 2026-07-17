# Drift Ledger

This is a minimal example of a **drift ledger** as described in Note #036.

Purpose: track when the **model** of the system changes, and what that means for prior verification claims.

## Entry format

Each entry has:

- `Date`
- `Model change` (what changed in the intended behavior / invariants)
- `Affected components` (files, functions, notes, experiments)
- `Required actions` (what must be re‑verified or updated)
- `Status` (Open / In progress / Done)

---

## Entry — 2026‑07‑17 — Initial model for `examples/verified_model_example`

- **Date:** 2026‑07‑17  
- **Model change:**  
  Introduced initial model M1 for `examples/verified_model_example`:
  - `normalize(x)` returns a vector with unit norm.
  - `safe_div(a, b)` returns `0.0` when `b = 0`, otherwise `a / b`.
- **Affected components:**
  - `examples/verified_model_example/utils.py`
  - `examples/verified_model_example/test_utils.py`
  - Note #036 (Verified Models and Drift Ledgers)
- **Required actions:**
  - Ensure tests encode the invariants.
  - Label functions with envelope status in comments.
  - Mark this entry as Done once labels and tests are in place.
- **Status:** Open

---

Future entries will follow this same pattern. The goal is not bureaucracy; it’s to make model changes visible and explicit.
