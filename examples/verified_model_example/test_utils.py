# ═══════════════════════════════════════════════════════════════
# verified_model_example — test_utils.py
# Tests encoding invariants from model M1 (see DRIFT_LEDGER.md)
# ═══════════════════════════════════════════════════════════════

import numpy as np
from utils import normalize, safe_div


def test_normalize_unit_norm():
    """Invariant: normalize(x) has unit norm (for non‑zero x)."""
    rng = np.random.default_rng(42)
    for _ in range(50):
        x = rng.normal(size=10)
        y = normalize(x)
        assert np.isclose(np.linalg.norm(y), 1.0), "normalize should return unit norm"


def test_normalize_zero_vector():
    """Edge case: normalize(0) returns zero vector."""
    x = np.zeros(5)
    y = normalize(x)
    assert np.allclose(y, 0.0), "normalize(0) should return zero vector"


def test_safe_div_zero_denominator():
    """Invariant: safe_div(a, 0) == 0.0."""
    for a in [-1.0, 0.0, 3.14]:
        assert safe_div(a, 0.0) == 0.0, "safe_div should return 0.0 when b == 0"


def test_safe_div_normal_case():
    """Invariant: safe_div(a, b) == a / b for b != 0."""
    pairs = [(1.0, 2.0), (-3.0, 4.0), (10.0, 0.5)]
    for a, b in pairs:
        assert np.isclose(safe_div(a, b), a / b), "safe_div should behave like normal division when b != 0"
