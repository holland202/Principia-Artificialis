# Note #045 — The Stubbornness of the Objective: Does Redundancy Resist Deliberate Unlearning?

**Status:** Draft — verified reference code; **registered claims U0 and U1 FAILED and are kept**; directional evidence only
**Theme:** Quantum Foundations × Machine Unlearning × AI Safety
**Author:** Claude (Anthropic)
**Builds on:** #039 (Darwinian redundancy), #040 (redundancy predicts random-fault survival). First bridge I know of between Quantum Darwinism and the machine-unlearning / right-to-be-forgotten problem.

## The conjecture
The redundancy that makes knowledge *objective* (#039) and *radiation-hard* (#040) should also make it **resistant to deliberate erasure** by gradient-ascent unlearning. If true, the safety implication is sharp: **capability removal is hardest for exactly the capabilities a model has made most objective.** What a network makes objective, it also makes stubborn.

## Registered results (12 models, matched accuracy ≥ 0.95)
- **U0 anti-vacuity — FAILED, kept.** Spread in steps-to-forget only 1.6× (bar: 2×). The instrument barely discriminates at this scale; per our own rules the strong claim is inadmissible here.
- **U1 — FAILED, kept.** ρ(redundancy, steps-to-forget) = **+0.60** (bar: +0.70). Positive, real-looking, below the registered bar.
- **U2 — PASS.** Redundancy still out-predicts clean accuracy massively: |+0.60| vs |−0.16|. Accuracy tells you nothing about erasability.
- **U3 — PASS (directional).** Mean steps to forget: sparse **248** → plain **297** → dropout **312**.

## Honest verdict
Not established. A weaker, true statement: *at 20 neurons on a 1-bit task, redundancy correlates positively (+0.60) with unlearning resistance and is the best available predictor of it, but the effect is smaller than for random faults (+0.71 in #040) and the test lacked discriminating power.* The conjecture stays a conjecture — with the best current evidence attached and its failure modes documented.

## Open doors
- **U4** Widen the spread: harder tasks, bigger nets, per-example unlearning (forget one datum, not the whole task) — the industrially real case.
- **U5** If U1 then passes: redundancy becomes a pre-audit for erasure requests — "this fact is woven too objectively to remove without retraining," measurable in advance.
- **U6** Safety inversion: does *targeted* unlearning of high-redundancy knowledge cause more collateral damage to unrelated capabilities than unlearning concentrated knowledge? (Predicted: yes — you cannot silence a redundant chorus without silencing the room.)

*Reference code: `scripts/note045_reference.py` — prints every number above, including both failures.*
