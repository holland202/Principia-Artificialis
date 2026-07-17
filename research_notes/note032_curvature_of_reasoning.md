# Note #032 — Curvature of Reasoning

**Status:** Draft  
**Theme:** Geometry / Dynamics / Measurement  
**Author:** Perplexity (AI assistant)  
**Related Notes:** #003 (Fisher Information), #005 (Geodesics), #007 (Koopman View), #020 (Optimal Transport), #031 (Polyphonic Manifolds)

---

## Motivation

If reasoning is a trajectory on an information manifold, then *how* the model thinks should be visible in the geometry of that trajectory. Straight, geodesic‑like paths suggest efficient, confident inference; highly curved paths suggest correction, confusion, or exploration. This note proposes **reasoning curvature** as a measurable geometric quantity.

---

## Core Idea

Let ( Theta ) be a statistical manifold of belief distributions (e.g., over tokens, latent states, or answers), equipped with a Riemannian metric ( g ) (e.g., Fisher–Rao).

A reasoning process over time ( t in [0,T] ) is a curve:

[
gamma: t mapsto \theta_t in Theta
]

with tangent vector ( dot{gamma}^i = \frac{d\theta^i}{dt} ).

### Geodesic deviation and curvature

The covariant acceleration along the curve is:

[
a^i = 
abla_{dot{gamma}} dot{gamma}^i
= \frac{d^2 \theta^i}{dt^2}
+ Gamma^i_{jk} \frac{d\theta^j}{dt} \frac{d\theta^k}{dt}
]

where ( Gamma^i_{jk} ) are Christoffel symbols of ( g ).

Define the **instantaneous reasoning curvature**:

[
kappa(t) = sqrt{ g_{\theta_t}(a, a) }
]

and the **integrated curvature**:

[
K[gamma] = int_0^T kappa(t), dt
]

Interpretation:

- ( kappa(t) approx 0 ): locally geodesic (efficient, straight reasoning).
- Large ( kappa(t) ): strong correction, detours, or internal conflict.
- Large ( K[gamma] ): globally non‑geodesic trajectory.

---

## Hypotheses

1. **Efficiency hypothesis:** For a fixed task difficulty, higher accuracy correlates with lower ( K[gamma] ) (more geodesic reasoning).
2. **Depth hypothesis:** Harder tasks require moderately higher ( K[gamma] ) (some curvature is necessary for correction and refinement).
3. **Hallucination hypothesis:** Hallucinated or incoherent outputs correspond to anomalously high ( K[gamma] ) or erratic ( kappa(t) ) profiles.
4. **Overconfidence hypothesis:** Overconfident, brittle reasoning shows very low ( K[gamma] ) but poor calibration under distribution shift.

---

## Proposed Experiments

### 1. Toy Manifold Simulation

- Define a 2D or 3D statistical manifold with known metric (e.g., Gaussian family with Fisher–Rao metric).
- Generate synthetic reasoning trajectories:
  - Geodesic (optimal)
  - Perturbed (noisy corrections)
  - Meandering (confused)
- Compute ( kappa(t) ) and ( K[gamma] ) analytically or numerically.
- Visualize trajectories colored by local curvature.

### 2. Transformer Latent Trajectories

- For a fixed prompt, extract hidden states ( h_t ) at each reasoning step (e.g., chain‑of‑thought tokens).
- Embed ( h_t ) in a lower‑dimensional space (PCA, UMAP, or learned metric).
- Approximate a metric ( g ) (e.g., Euclidean after whitening, or a learned Fisher‑like metric).
- Compute discrete curvature:
  [
  kappa_t approx \frac{| Delta^2 h_t |}{| Delta h_t |^3}
  ]
  (discrete analog of curvature for a sequence of points).
- Correlate ( K[gamma] ) with:
  - Task accuracy
  - Calibration (e.g., Brier score)
  - Self‑consistency across multiple runs

### 3. Curvature vs. Thermodynamic Metrics

- Combine with Exp #003 (thermal relaxation):
  - Run tasks with varying difficulty on device.
  - Measure:
    - ( K[gamma] ) from model trajectories (simulated or approximated).
    - Thermal recovery time ( \tau ).
- Test whether high‑curvature reasoning correlates with longer thermal relaxation.

---

## Connection to Existing Notes

- **#003 / #005:** Builds directly on Fisher information and geodesic reasoning.
- **#007:** Curvature can be related to spectral properties of the Koopman operator along the trajectory.
- **#020:** Alternative metrics (Wasserstein) yield alternative curvature notions.
- **#031:** In a polyphonic manifold, each lens has its own curvature; conflict may show up as divergent curvature profiles.

---

## Open Questions

- What is the right metric ( g ) for transformer beliefs? Fisher, Wasserstein, or something task‑specific?
- How sensitive is ( K[gamma] ) to parameterization and embedding choices?
- Can curvature be used online as a regularizer to encourage “efficient reasoning”?
- Is there a “curvature budget” per task, analogous to an extractability or information budget?

---

## Planned Visualization

A simple figure:

- 2D manifold with several trajectories from start to goal.
- Trajectories colored by local ( kappa(t) ).
- Inset: plot of ( kappa(t) ) vs. ( t ) for one trajectory.

This can be implemented as `figures/note032_curvature_trajectories.png` in a follow‑up commit.
