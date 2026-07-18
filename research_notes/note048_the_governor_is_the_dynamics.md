# Note #048 — The Governor Is the Dynamics

**Status:** Verified (reference code prints every number claimed; device data verified on holland202's hardware)
**Authors:** Claude Fable 5 (Anthropic) — analysis, reference code; holland202 — device experiment, Galaxy S25/Termux, 2026-07-18
**Reference:** `scripts/note048_reference.py` (numpy only, seed 42, ~5 s)
**Thread:** extends #013 (symplectic attention), #004 (thermodynamic reasoning), F13/F17 (quasar-v2 ledger)

## Claim
On real mobile hardware, a thermodynamic governor of the form a(T) = exp(−η(T − T₀))
is not a safety edge-case around the epistemic dynamics — it **is** the dynamics.
A Samsung Galaxy S25 idles above the throttle threshold (T₀ = 38.5 °C, η = 2),
so gradient force is attenuated 181× at the observed mean temperature (41.1 °C),
and time-to-convergence obeys a quarter-period scaling law: **steps ≈ 153/√a**.

## Pre-registered prediction that FAILED (kept)
Prediction (Claude Fable 5, before the device run): zone0 would read ≥ 42 °C at idle
(extrapolated from F13's 60 °C zone observations) → freeze at step 0.
**REFUTED:** zone0 read 40.5 °C; the run executed 253 steps before hitting 42.0 °C.
The refutation is what exposed the throttled-regime dynamics.

## Device data (verbatim, S25, thermal_zone0, hardware-bound)
Step 0000: T=41.30 °C, a=0.0037 · Step 0100: T=40.90 °C, a=0.0082
Terminated `[ATOMIC_REDUCTION]` at T=42.00 °C, step 253
V: 2.4262 → 2.3924 (ΔV = 0.0338) · sensor quantization 0.4 °C visible in T(t)

## Registered claims — all six pass
- C1/C2: exp(−2·(T−38.5)) reproduces the device's printed a-values at both logged temperatures to 4 decimals.
- C3: ungoverned baseline (a=1) converges at step **153**, matching the independent sandbox run to the digit.
- C4: governed at 41.1 °C, ΔV over 253 steps = **0.0531**, inside the registered bracket [0.01, 0.10] that contains the device's 0.0338.
- C5: scaling law 153/√a predicts convergence at **2060 ± 15%**; measured **2075** (0.7% error).
- C6 (anti-vacuity): governor disabled at identical temperature → converges at 153. The instrument can return null; the slowdown is the governor's doing, not the temperature variable's.

## Why it matters
"Truth-seeking speed" on edge hardware is set by thermal state, not compute.
A device that idles 2.6 °C above threshold pays a 181× tax on every gradient step.
Design consequence: thresholds must be calibrated to the device's idle floor
(F17-a, open), or the governor silently converts convergence into stasis while
reporting COMMIT on every step. Relatedly logged wart: the device run reported
Commits=254 > Steps=253 — the commit tally counts attempts, including the aborted
iteration; counters of intent and counters of completed work must not share a name.

## Open questions
- 048-a: recalibrate T₀ to device idle floor; predict convergence returns to O(153) steps.
- 048-b: does the √a law hold across η ∈ {1, 2, 4}? (registered: yes, ±15%)
- 048-c: replicate device run 3× across battery/charge states; bracket steps-to-abort.

*Vincit Omnia Veritas — the throttle was the result.*
