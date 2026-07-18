"""
Note #044 — THE CIRCULARITY TEST: when a benchmark validates itself
====================================================================
Motivation (in-repo): notes #041-#043 report a Free Energy of Reasoning
functional with AUC > 0.99 at separating correct from hallucinated
trajectories — on SYNTHETIC benchmarks. This note builds the null
instrument the repo now needs: a demonstration that near-perfect AUC on
self-generated data is the EXPECTED result for ANY functional, including
a deliberately meaningless one — and a protocol to detect it.

REGISTERED:
  C1  A deliberately meaningless scalar functional ("junk score": the
      variance of every 3rd coordinate) achieves AUC >= 0.99 on a
      synthetic benchmark generated to differ along its own axis.
  C2  The same junk functional collapses toward chance (AUC <= 0.65) on
      data generated under a DIFFERENT mechanism of failure.
  C3  Therefore: self-consistent AUC is uninformative; the diagnostic
      quantity is the AUC DROP under mechanism transfer. Registered
      threshold: a trustworthy functional keeps >= 80% of its AUC edge
      (AUC-0.5) under transfer; a circular one keeps < 40%.
This is not an attack on FER — it is the falsification protocol FER
needs before its number means anything. Vincit omnia veritas.
"""
import numpy as np
rng = np.random.default_rng(23)
d, n = 30, 400

def junk_score(X):                       # deliberately meaningless
    return X[:, ::3].var(axis=1)

def auc(s0, s1):
    """P(score of class1 > class0), tie-corrected."""
    allv = np.concatenate([s0, s1])
    r = np.argsort(np.argsort(allv)) + 1
    r1 = r[len(s0):]
    return (r1.sum() - len(s1)*(len(s1)+1)/2) / (len(s0)*len(s1))

# --- benchmark A: generated ALONG the junk functional's own axis ---
good_A = rng.normal(0, 1.0, (n, d))
bad_A  = rng.normal(0, 1.0, (n, d)); bad_A[:, ::3] *= 2.2   # inflate its axis
auc_self = auc(junk_score(good_A), junk_score(bad_A))

# --- benchmark B: a DIFFERENT failure mechanism (mean shift, not var) ---
good_B = rng.normal(0, 1.0, (n, d))
bad_B  = rng.normal(0, 1.0, (n, d)) + rng.normal(0.9, .1, d)  # shifted
auc_transfer = auc(junk_score(good_B), junk_score(bad_B))

edge_kept = (auc_transfer - 0.5) / (auc_self - 0.5)
print(f"junk functional, SELF-generated benchmark : AUC = {auc_self:.3f}")
print(f"junk functional, TRANSFER benchmark       : AUC = {auc_transfer:.3f}")
print(f"edge retained under mechanism transfer    : {100*edge_kept:.0f}%")
print(f"\nC1 meaningless metric scores 'perfectly' on its own benchmark "
      f"(>=0.99): {auc_self >= 0.99}")
print(f"C2 same metric collapses off-mechanism (<=0.65): "
      f"{auc_transfer <= 0.65}")
print(f"C3 circularity verdict (edge kept {100*edge_kept:.0f}% < 40%): "
      f"{edge_kept < 0.40}")
print("\nPROTOCOL for any in-repo functional (incl. FER, #043): report AUC "
      "on (i) its own\nsynthetic benchmark, (ii) a transfer benchmark with "
      "a different failure mechanism,\n(iii) real model outputs. Only (ii) "
      "and (iii) carry information. Edge-retention >= 80%\nis the "
      "registered bar for a non-circular claim.")
