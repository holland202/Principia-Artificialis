# Note #025 — Measurement, Collapse, and Decision Boundaries

## Thesis
The final readout layer of the model can be interpreted as a **quantum measurement** on the latent state \(\rho_L\):
- Pre-readout state: superposition over outputs.
- Measurement: output heads, logits.
- Collapse: selection of a concrete token.
- Decision boundaries: effective **POVM elements**.

## Measurement model
Model the output layer as a POVM \(\{M_y\}\) with probability \(p(y|x) = \operatorname{Tr}[M_y \rho_L(x)]\). 
- **Fisher-Rao / QFI metric** quantifies how distinguishable outcomes are.
- High curvature regions = sharp decision boundaries.

## Thermodynamic cost
Collapsing \(\rho_L\) reduces uncertainty; by Landauer-style arguments, there is a minimal **heat dissipation** associated with this information gain.
