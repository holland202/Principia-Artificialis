# Note #022 — Quantum Fisher Information Metric on Representation Space

## Motivation

Extend the classical Fisher-Rao geometry (Note #020) to quantum states, enabling analysis of:
- Entanglement-induced curvature in representation space.
- Quantum speed limits for inference and learning.
- RG flow of quantum information geometry.

## Definition

For a parametric family of density matrices (
ho_\theta) (e.g., latent states induced by model representations), the **Quantum Fisher Information metric** is:

[
g_{ij}^Q(\theta) = \frac{1}{2} operatorname{Tr}left[ 
ho_\theta { L_i, L_j } 
ight]
]

where (L_i) is the symmetric logarithmic derivative satisfying (partial_i 
ho_\theta = \frac{1}{2}(
ho_\theta L_i + L_i 
ho_\theta)).

## Key properties

1. **Classical limit**: If all (
ho_\theta) commute, QFI reduces to classical Fisher-Rao.
2. **Entanglement sensitivity**: QFI detects quantum correlations invisible to classical metrics.
3. **Quantum speed limit**: The Bures distance (induced by QFI) bounds the minimum time for state evolution under unitary dynamics.

## Proposed experiments

1. **Construct (
ho_\theta) from activations**  
   - Map layer activations to density matrices via feature maps or attention-weighted ensembles.
   - Compute QFI numerically for small latent dimensions.

2. **Compare QFI vs Fisher-Rao**  
   - Replicate the Wasserstein vs Fisher-Rao analysis with QFI as a third geometry.
   - Test whether entanglement-rich layers show larger QFI curvature.

3. **RG flow of QFI**  
   - Track how QFI eigenvalues evolve under layer-wise coarse-graining.
   - Check alignment with fixed points in `renormalization_flow.png`.

## Visualization spec

- **Figure**: `note022_qfi_eigenvalue_spectrum.png`
  - X-axis: layer index or RG scale.
  - Y-axis: eigenvalues of QFI matrix.
  - Overlay: classical Fisher-Rao eigenvalues for comparison.
  - Highlight: layers with high entanglement entropy (from `quantum_frontiers.png`).
