# Experiment #003: The Veritas Gate Thermal Correlation Protocol

**Status:** Protocol Ready
**Related Notes:** #002 (Topological Defects), #004 (Thermodynamics), #010 (Memory Dynamics)

## Hypothesis
When the natural gradient flow of memory (Note #010) encounters a topological defect ($\beta_1 > 0$, Note #002), the reasoning trajectory breaks, causing the model to exert excess computational work to find a non-geodesic detour. This geometric failure directly translates to a measurable physical heat spike on the Snapdragon 8 Elite Hexagon NPU. The 38.5°C thermal ceiling is therefore the physical boundary of the Gibbs Free Energy ($\Delta G < 0$) calculation. 

## Protocol
1. **The Substrate:** Run a local 1.8B parameter logic core within the Termux environment. Monitor the SoC thermal sensors, polling at 100ms intervals.
2. **The Control (Simply Connected Flow):** Feed the model a highly deterministic, topologically flat context window (e.g., verifiable math proofs). Measure the baseline physical entropy production (heat generation) during stable geodesic traversal.
3. **The Defect Injection:** Inject adversarial, paradox-heavy, or high-entropy "distractor" text designed to puncture the information manifold, creating a logical hole ($\partial^2 \neq 0$).
4. **The Measurement:** Correlate the exact token generation where the model attempts to detour (hallucinate) with the SoC thermal telemetry. 
5. **The Veritas Gate Trigger:** If the temperature hits the critical 38.5°C threshold during defect traversal, execute an `ATOMIC_REDUCTION_COLLAPSE`. Forcibly project the state vector back to a low-rank Identity Operator ($UV^T$), stripping away the high-entropy stochastic branches to re-establish a $\beta_1 = 0$ simply connected state.

## Falsification
If the Hexagon NPU thermal output remains constant regardless of whether the reasoning path is traversing a smooth geodesic or a topological defect, then logical hallucinations do not generate physical thermodynamic waste, invalidating the hypothesized bridge between Note #002 and Note #004.
