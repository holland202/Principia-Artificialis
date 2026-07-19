# STATUS — verified vs unverified

Verified means: a test targeting the claim passes when you run it.

## VERIFIED (run: python3 sovereign_ops/evals/eval_harness.py)
- Causal d-separation + backdoor criterion — 3 cases incl. collider trap. PASS.
- Conformal coverage (Gaussian) — 89.7% mean over 20 trials, target 90%. PASS.
- Conformal coverage (exponential / distribution-free) — ~91%. PASS.
- Conformal not-self-referential regression guard. PASS.
- Thermal-gated honest failure — returns None under insufficient budget. PASS.

## NOT VERIFIED / OUT OF SCOPE
- No external-dataset validation (SWaT/WADI/real ICS telemetry).
- No production deployment, no third-party reproduction, single device only.
- Latency/throughput numbers are informal, not benchmarked.
- These are correct implementations of KNOWN methods, not novel algorithms.

When in doubt, run the test.
