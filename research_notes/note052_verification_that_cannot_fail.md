# Note 052 — Verification That Cannot Fail

**Status:** Draft, verified reference code
**Authors:** holland202 (Chad Holland), Claude (Anthropic)
**Date:** 2026-08-02
**Instruments:** vacuity_lint.py (github.com/holland202/vacuity_lint.py, selftest 18/18 on aarch64/Termux/Py3.14), vacuity_scan.py (clean-room reimplementation, sandbox only — numbers from the two instruments are NOT comparable)
**Related:** [[note036_verified_models_drift_ledgers]] · [[note044_circularity_test]] · [[NOTES_INDEX]]

---

## What broke (failures lead)

1. **Both registered predictions about the estate were refuted.**
   P1 predicted findings in at least half of 13 repositories; the measurement
   was 6 of 13 (46%). P2 predicted under 10 findings after precision fixes;
   the measurement was 13. Both kept below.

2. **The instruments built to find the defect contained the defect.**
   arch_map.py's selftest initially could not distinguish exit 0 from exit 1 —
   an always-clean script would have scored as gated (fixed, added as its
   P10b). vacuity_scan.py's suppression-marker regex used `\s*`, which matched
   newlines and let a bare marker swallow the next source line as its
   "reason" — the mute button the design exists to prevent. Two selftest
   fixtures were misnamed so their tests never ran; the gate caught it, not
   the authors.

3. **First-pass precision was poor.** Of 7 findings in one repository, 5 were
   false positives (library modules matched on filename alone; runnable
   scripts that correctly exit non-zero were flagged as uncollectable). The
   first estate total of 21 dropped to 13 after the fixes — a 38% cut.

4. **A defect class the linter cannot see at all** was found during this work:
   a test suite that was genuinely written and genuinely passed (18 checks)
   but never reached the public repository. Scanning the public repo finds
   nothing wrong — there is no bad code, just an absent suite everyone
   believed in. "Verified" and "published" are different steps. This sits one
   level above the Type A/B taxonomy below and is not addressed by this note's
   instrument.

---

## The finding

On 2026-07-26, four independent codebases were found to contain a
verification construct that could not fail: a tomography self-check with no
fail path, a pytest suite that collected zero tests, a generated-file guard
whose marker was never written, and a smoke test whose boolean branch was
dead. Different authors, different AI models, written in different months.
Nobody had noticed, because the failure path in each had never been taken —
so nobody discovered it could not be reported.

A gate you have never seen fail is not evidence that anything passed.

## Taxonomy

- **Type A — no fail path exists.** No assert, no raise, no non-zero exit,
  no `def test_`. Statically detectable.
- **Type B — a fail path exists but cannot fire.** A marker defined but never
  written; a boolean branch dead because one condition implies another.
  Requires reachability analysis.

The original four defects split exactly 2 / 2. The instrument catches every
Type A case and misses every Type B case: measured detection rate **2 of 4**.
The blind spot is encoded as instrument selftest P12 rather than omitted.

## Registered predictions and results

Registered before measuring, in order. Refutations kept per method.

**Instrument 1: vacuity_lint.py, estate scan (device, 2026-07-27)**

- **P1 — REFUTED.** "Findings in at least half the repos." Result: 6 of 13
  (46%). Refuted narrowly.
- **P2 — REFUTED.** "Under 10 findings total after precision fixes."
  Result: 13.
- Corrected metric: findings are not files (one file produced two findings).
  Distinct affected files: 12. Corrected again to a true denominator on
  2026-07-27: of **26 verification-shaped entry points** across 12
  repositories, **9 had no fail path**, plus 1 declared intentional.

**Instrument 2: vacuity_scan.py, control-group comparison (sandbox,
2026-07-27; both arms cloned and scanned by one tool on one day)**

- **P3 — CONFIRMED, hollow.** "Fires at least once on the control group."
  It fired 3 times; all 3 were false positives.
- **P4 — CONFIRMED.** "Majority of control findings are false positives."
  3 of 3.
- **P5 — CONFIRMED directionally, confounded.** "Higher true-positive rate in
  this estate than in the control." 2/15 (13.3%) vs 0/347 (0%). n=15 is weak,
  and the pre-registered confounds are unresolved: the estate is solo,
  unreviewed, CI-less research code; the controls are reviewed, CI-gated,
  shipped libraries. Review process explains the gap at least as well as
  authorship does. Do not cite this as "AI code fails more."

**The result that matters is the denominator, not the rate.**
Verification-shaped files per repository: control **34.7**, this estate
**1.2** — a 28× difference. The problem was mostly not that gates failed;
it was that there were almost none to fail.

## Anti-vacuity control

The instrument's selftest includes P9 (a clean tree yields zero findings) and
P10 (a defective tree yields findings). A detector must be shown capable of
returning nothing and something; without both, this instrument would be an
instance of the defect it looks for. The reference script below carries the
same pair.

## Reference code

`scripts/note052_reference.py` — embeds four minimal fixture files
reproducing the 2 Type A / 2 Type B split, runs vacuity_lint.py against
them, and asserts the detection rate is exactly 2 of 4 (exit 1 otherwise).
It also asserts the P9/P10 pair on embedded clean and defective trees.
Requires vacuity_lint.py: looked for beside the script, one level up, then
in ~/vacuity-lint/. Failing all three it fetches the pinned commit 718d103
from github.com/holland202/vacuity_lint.py and verifies sha256 before use.
A failed fetch or a hash mismatch exits 1 -- the instrument is never
silently skipped. Both branches were exercised on device 2026-08-04.

The estate and control measurements (9/26, 2/15 vs 0/347, 34.7 vs 1.2) are
not reproduced by the reference script — they require cloning 23
repositories. They are reproducible from the two repo lists in the
instrument repositories' records, with instrument and date stated above.
Numbers in this section were pasted from tool output, not paraphrased.

## Open predictions (the door)

- **P6 — UNRUN.** Within human-authored repositories, those without CI
  (`.github/workflows` absent) show a higher true-positive vacuity rate than
  those with CI. The 2026-07-27 control sample was CI-uniform (10/10) and
  could not test this. The solo-maintainer, no-CI human stratum is the
  control that would separate authorship from review, and it has not been
  built.
- **P7 — UNRUN.** Type B detection via reachability analysis (a marker that
  is defined but never written; dead boolean branches) will catch at least
  one of the two known Type B instances without exceeding a 20% false-positive
  rate on the fixture set. This is the open problem and the half the current
  instrument does not solve.

---

*Vincit Omnia Veritas.*
