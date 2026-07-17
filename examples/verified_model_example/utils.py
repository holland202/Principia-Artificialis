# ═══════════════════════════════════════════════════════════════
# verified_model_example — utils.py
# Envelope status: Verified‑w.r.t‑M1 (for normalize), Candidate (for safe_div)
# Model: M1 (see DRIFT_LEDGER.md entry 2026‑07‑17)
# ═══════════════════════════════════════════════════════════════

import numpy as np


def normalize(x: np.ndarray) -> np.ndarray:
    """
    Normalize vector x to unit norm.

    Invariant (M1):
        For any non‑zero x, np.isclose(np.linalg.norm(normalize(x)), 1.0).

    Envelope status: Verified‑w.r.t‑M1 (subject to tests in test_utils.py).
    """
    x = np.asarray(x, dtype=float)
    norm = np.linalg.norm(x)
    if norm == 0:
        return np.zeros_like(x)
    return x / norm


def safe_div(a: float, b: float) -> float:
    """
    Safe division: return 0.0 when b == 0, else a / b.

    Invariant (M1):
        safe_div(a, 0) == 0.0
        safe_div(a, b) == a / b for b != 0

    Envelope status: Candidate (tests present, invariants not fully checked).
    """
    if b == 0:
        return 0.0
    return a / b
