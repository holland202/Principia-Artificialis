# sovereign_core — honest status

**Last verified: 2026-07-19, on-device** (Samsung Galaxy S25, Termux,
Python 3.14: `pytest test_sovereign.py` → **33 passed**, 0.11 s).
This file states what IS, not what is intended. It replaces the
2026-07-18 STATUS, which honestly reported 27/33 and two open defects —
that count grew to five before it shrank to zero.

## What this directory contains now
The real implementation: `sovereign_core.py` (public API),
`sovereign_core_modules.py` (thermal governor, SIC, Phase-2C gates),
`llm_governor_decision_engine.py`, `llm_providers.py`, and the full
test suite `test_sovereign.py`. The import-shadowing stub `__init__.py`
was removed — it made Python resolve the package name to 21 bytes of
comment instead of the module.

## Five defects found and fixed (2026-07-18/19), kept as lessons
1. **Vocabulary fail-open.** The decision engine's thermal map spoke
   WARNING/CRITICAL/LOCKED — states its own governor never emits — so
   SCAR_LOCK fell through to a neutral default and a scar-locked 50 °C
   device scored ALLOW. Unknown states now fail closed.
2. **Inverted latch hysteresis.** SCAR_LOCK required temperature above
   threshold *plus* hysteresis to engage. A protection latch must be
   easy to enter and hard to leave; entry is now at bare threshold from
   any state, while comfort transitions keep their noise band.
3. **OVERRIDE by score.** Benign inputs scoring ≥ 0.95 were classified
   as emergency overrides. OVERRIDE now requires active mission
   context; a high score alone is just ALLOW.
4. **A stochastic safety gate.** The pre-inference gate decided by
   `np.random.rand() < pass_prob` — admitting low-confidence inferences
   ~15% of the time and rejecting high-confidence ones ~8%. Found only
   because the suite was run repeatedly; a single green run hides a
   coin-flip. The gate is now deterministic.
5. **A hallucinated thermometer.** `ThermalGovernor.update()` fabricated
   temperature from history-mean + unseeded noise, overwriting real
   readings. Simulation is now opt-in (`sim_mode=True`); by default the
   governor trusts the temperature it is given.

Weighted averaging was also given a **weakest-gate floor**: the final
decision can never be more permissive than the worst safety rule's own
verdict. Safety gates are minima, not votes.

## Still unverified (roadmap, not inventory)
`unified_launcher.py` and `sovereign_dashboard.py` have not been
import-tested against this set and are not yet here. `MANIFEST.md` and
`START_HERE.md` still describe an intended deployment; their counts
remain aspirational until every listed file exists, imports, and passes
tests on real hardware.

## Rule of the house
Refuted or inflated claims are corrected in public, not deleted.
A test suite is run repeatedly, on real hardware, before anything is
called verified — one green run is an anecdote.

*Vincit Omnia Veritas.*
