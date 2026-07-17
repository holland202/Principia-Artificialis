# Note #038 — The Free-Physics Principle: Known Constraints Are a Regularizer Whose Payment Schedule Is Variance, Not Violation

**Status:** Draft — verified reference code, cross-domain (2 domains)
**Theme:** Measurement / Learning Theory
**Author:** Claude (Anthropic)
**Motivating data:** holland202's QUASAR program, findings F12/F14 (channel
space) — including the *refutation* of registered claim N1-c, which this
note generalizes.

---

## The claim

Let the truth `w*` lie in a known closed convex set `K` (a physical law, a
conservation constraint, a simplex, a cone). Then for any estimator `ŵ`:

1. **Projection is free.** `Π_K(ŵ)` is never worse than `ŵ` (Euclidean
   projection onto a convex set containing the target is nonexpansive —
   this part is classical).
2. **The payment schedule is variance.** The *size* of the benefit is
   governed by estimation variance (data scarcity), and decays toward
   zero as data grows — a consistent estimator walks into `K` on its own.
3. **The dissociation (the non-obvious part):** the benefit is *not*
   governed by how often `ŵ` violates `K`. An estimator can violate the
   constraint **100% of the time** while the value of enforcing it is
   negligible — because at large `n` the violations are microscopic.
   *Violation frequency is a red herring; violation magnitude is just
   variance wearing a costume.*

Slogan: **physics is free information, and the invoice is paid in
variance.**

## Why this is worth a note

The default intuition — "enforce the constraint when it's being
violated" — attributes the value of a constraint to its *binding
frequency*. That intuition was registered as claim N1-c in the QUASAR
program (channel space, CP cone) and **refuted by experiment**: the
regime where the constraint bound hardest (46% of optimizer steps
off-cone) gained almost nothing, while the data-scarce regime gained the
most. This note claims that refutation is not a quantum quirk but an
instance of a general law, and verifies it in a second, entirely
classical domain.

## Reference experiment (verified; code in `note038_reference.py`)

Ordinary linear regression, truth on the 8-simplex (weights nonnegative,
summing to 1). Raw OLS vs OLS projected onto the simplex, 200 paired
trials per sample size:

| n | raw MSE | projected MSE | benefit | raw violates K |
|---|---|---|---|---|
| 10 | 1.9080 | 0.2682 | 1.6398 | 100% |
| 40 | 0.0686 | 0.0392 | 0.0294 | 100% |
| 160 | 0.0139 | 0.0102 | 0.0038 | 100% |
| 640 | 0.0031 | 0.0024 | 0.0007 | 100% |
| 1280 | 0.0016 | 0.0013 | 0.0003 | 100% |

Registered predictions, all confirmed:
- **P1** projection never hurts (paired, every n) ✅
- **P2** benefit decays monotonically with n (1.64 → 0.0003) ✅
- **P3** dissociation: violation rate stays **100%** while the benefit
  falls **~5,500×** ✅

Cross-domain replication: the same three signatures were measured in
quantum channel space (QUASAR F14: CP-projected gradient descent wins
8/8 seeds under data scarcity, is a no-op at convergence, and the
benefit does not track cone-violation frequency), and F15 found the
projection repairs physicality of tomography-derived estimates at every
measurement budget. Two domains, same law.

## Honest prior art

Nonexpansiveness of convex projection is the Hilbert projection theorem;
constrained M-estimation, isotonic regression, and projected gradient
descent are mature fields; statistical folklore knows "constraints help
most in small samples." What I have not found stated crisply, and what
the experiments here isolate, is the **dissociation**: that binding
*frequency* — the quantity practitioners actually monitor — carries
essentially no information about the constraint's marginal value, which
is carried by variance alone. If a reader knows a prior statement of
exactly this dissociation, filing an issue with the citation would
improve this note (that is what add-only means).

## Falsifiable next predictions

- **P4** For a *mis-specified* K (truth outside), projection bias floors
  the error at large n: benefit becomes *negative* past a crossover
  n*. Measuring n* estimates the misspecification distance.
- **P5** The benefit curve should track the estimator's variance curve
  (∝ 1/n here) with the same exponent, in any domain, for any convex K
  containing the truth.
- **P6** In-training projection (project every optimizer step) and
  post-hoc projection converge to the same benefit as n grows; they
  differ only in the scarce-data regime (weak evidence for this already
  in F12 vs F14; not yet a controlled comparison).

*Vincit omnia veritas — and constraints are truth you get to use before
you've paid for it.*
