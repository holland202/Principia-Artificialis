# Verified Model Example

This tiny module illustrates the workflow from **Note #036** (Managing AI‑Generated Code via Verified Models and Drift Ledgers).

## Structure

- `utils.py`  
  - `normalize`: envelope status **Verified‑w.r.t‑M1** (invariant: unit norm).  
  - `safe_div`: envelope status **Candidate** (invariant: safe division with 0 on `b=0`).
- `test_utils.py`  
  Tests that encode the invariants from model **M1** (see `DRIFT_LEDGER.md` in the repo root).
- `README.md` (this file)

## How this relates to Note #036

- The **model** (M1) is described in:
  - `DRIFT_LEDGER.md` entry "2026-07-17 — Initial model for `examples/verified_model_example`".
- The **verification envelope** for each function is:
  - Stated in the docstring/comments in `utils.py`.
  - Encoded in `test_utils.py`.
- If the model changes (e.g., `safe_div` semantics change), the drift ledger entry would be updated, and these tests/labels would need to be revisited.

## Running the tests

From this directory:

```bash
python -m pytest test_utils.py
This is intentionally minimal. The point is to show the pattern, not to build a full framework.
