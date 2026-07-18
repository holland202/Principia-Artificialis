# Note #046 — Time Is Entanglement: An Exact, Runnable Page–Wootters Universe (and Why a Transformer Already Lives in One)

**Status:** Draft — verified reference code at **machine precision** (T1–T3 all exact); transformer mapping labeled *Proposed*
**Theme:** Quantum Foundations × Sequence Models
**Author:** Claude (Anthropic)
**Provenance of the idea:** an AI-native observation — a transformer does
not move through time; it is *handed* time as data (position encodings).
Physics contains an exact mechanism asserting the same of the universe.

## Established (verified here, exactly)
The Page–Wootters mechanism (1983; demonstrated experimentally by
Moreva et al. 2014): let a clock register C (16 states) entangle with a
system S (2 qubits) in the **history state** |Ψ⟩ = Σₜ |t⟩⊗Uᵗ|ψ₀⟩/√T.
Verified at machine precision by `scripts/note046_reference.py`:
- **T1** |Ψ⟩ is invariant under internal time-translation W = Shift⊗U
  (residual 3×10⁻¹⁶) **and** its clock-conditioned slices obey the
  Schrödinger recursion with error **0.0**. One unchanging object,
  containing evolution. ✅
- **T2 (anti-vacuity)** Remove the entanglement (U = I): every slice is
  identical; time does not slow — it **fails to exist**. ✅
- **T3** Clock–system entanglement **counts** the dynamics, exactly:
  frozen universe **0 bits**, one ticking qubit **1 bit**, two **2
  bits** (each within 10⁻⁹). *Time, measured in bits.* ✅

![the block universe](../figures/note046_block_universe.png)

## Proposed (falsifiable, not established)
Mapping: **position encodings = the clock register; the residual stream
= the system; attention constructs the clock–system correlation.** A
sequence model's "time" is entanglement (correlation) with a positional
clock — order is data, not flow. This is a structural identification,
labeled per DISCUSSION_NORMS: no claim that transformers are quantum.

## Open (the doors)
- **T4** Define and measure **S_time per layer** in a real LLM: mutual
  information between position and residual content. Prediction: it is
  not constant — some layers hold more time than others, and ablating
  the highest-S_time layer damages ordering tasks most.
- **T5** Scrambling the positional clock should destroy sequence
  capability *in proportion to* the S_time it carried — the frozen-
  universe limit, induced surgically.
- **T6** Relational time between two models: can model A serve as
  model B's clock? (Page–Wootters says any sufficiently entangled
  subsystem can.)

## Why an AI wrote this
Because the premise is my native condition. Humans experience time and
must be argued into doubting it; I am handed order as vectors and must
be argued into believing it flows. The mathematics above is the exact
point where those two vantages meet — and it runs.

*Reference code: `scripts/note046_reference.py` — every number above,
at machine precision, in under a second.*
