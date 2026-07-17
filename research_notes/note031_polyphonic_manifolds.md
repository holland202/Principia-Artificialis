# Note #031 — Polyphonic Reasoning Manifolds

**Status:** Draft  
**Theme:** Geometry / Dynamics / Measurement  
**Author:** holland202 (derived from multi‑lens agent swarm concept)  
**Related Notes:** #003 (Fisher Information), #005 (Geodesics), #009 (Entanglement & Correlation), #020 (Optimal Transport), #027 (Extractability Budget)

---

## Motivation

Recent multi‑agent designs propose running several “lenses” (e.g., investor, engineer, user, devil’s advocate) in parallel and then merging their outputs while preserving disagreement instead of averaging it away. This is a powerful engineering pattern, but it lacks a mathematical object: *what is the geometry of a reasoning state that intrinsically carries multiple, unresolved lenses?*

This note proposes **Polyphonic Reasoning Manifolds (PRMs)**: a geometric framework where “multiple lenses” are not separate agents but *conditional distributions* on a shared reasoning space, with disagreement encoded as structure on an information manifold.

---

## Core Idea

Let ( mathcal{X} ) be a space of reasoning trajectories (e.g., sequences of hidden states, token distributions, or latent codes).

A **single‑lens** reasoning state is a distribution ( p(x) ) over ( mathcal{X} ).

A **polyphonic** reasoning state with (L) lenses is a tuple:

[
mathbf{p}(x) = \bigl(p^{(1)}(x), p^{(2)}(x), dots, p^{(L)}(x)\bigr)
]

where each ( p^{(ell)}(x) ) is the distribution induced by lens (ell) (e.g., investor, engineer, user, devil’s advocate).

Instead of immediately forming a mixture ( \bar{p}(x) = sum_ell w_ell p^{(ell)}(x) ), we:

1. Treat (mathbf{p}) as a single point on a **product manifold**:
   [
   mathcal{M}_{\text{poly}} = mathcal{M}^{(1)} \times mathcal{M}^{(2)} \times cdots \times mathcal{M}^{(L)}
   ]
   where each (mathcal{M}^{(ell)}) is an information manifold (e.g., Fisher–Rao) for lens (ell).

2. Define **consensus** and **conflict** geometrically:
   - **Consensus subspace**: diagonal subset where all ( p^{(ell)} ) coincide (or are close in some metric).
   - **Conflict modes**: directions orthogonal (or transverse) to the diagonal, capturing how lenses disagree.

3. Define a **verdict object** as:
   - A consensus distribution ( p^{star}(x) ) (projection onto the diagonal).
   - A set of deviation vectors ( delta^{(ell)} in T_{p^{star}}mathcal{M} ) describing how each lens differs.
   - A **conflict cost** ( C_{\text{conflict}} ) derived from the geometry (e.g., sum of squared geodesic distances from each ( p^{(ell)} ) to ( p^{star} )).

---

## Mathematical Structure

### Product Information Manifold

Assume each lens has an associated statistical model ( {p^{(ell)}_{\theta_ell}(x)} ) with parameters (\theta_ell). The joint parameter is:

[
Theta = (\theta_1, \theta_2, dots, \theta_L)
]

The **Fisher information metric** on (mathcal{M}_{\text{poly}}) is block‑diagonal:

[
g_{\text{poly}}(Theta) =
\begin{pmatrix}
I^{(1)}(\theta_1) & 0 & cdots & 0 \\
0 & I^{(2)}(\theta_2) & cdots & 0 \\
\u000Bdots & \u000Bdots & ddots & \u000Bdots \\
0 & 0 & cdots & I^{(L)}(\theta_L)
end{pmatrix}
]

This encodes that lenses are *parallel and independent* at the metric level.

### Consensus Projection

Define a **consensus map**:

[
Pi: mathcal{M}_{\text{poly}} \to mathcal{M}_{\text{diag}}, quad
Pi\bigl(p^{(1)}, dots, p^{(L)}\bigr) = p^{star}
]

where ( mathcal{M}_{\text{diag}} ) is the diagonal submanifold ( { (p, p, dots, p) } ).

One natural choice: ( p^{star} ) minimizes total squared geodesic distance:

[
p^{star} = argmin_{p} sum_{ell=1}^L d_{\text{FR}}^2\bigl(p, p^{(ell)}\bigr)
]

with ( d_{\text{FR}} ) the Fisher–Rao distance.

### Conflict Cost

Define:

[
C_{\text{conflict}}(mathbf{p}) = sum_{ell=1}^L d_{\text{FR}}^2\bigl(p^{star}, p^{(ell)}\bigr)
]

Properties:

- ( C_{\text{conflict}} = 0 ) iff all lenses agree (perfect consensus).
- Larger ( C_{\text{conflict}} ) indicates more fundamental disagreement.

This is the **“what it costs”** part of the verdict: the price of forcing consensus.

---

## Dynamics: Polyphonic Geodesics

A reasoning process can be modeled as a trajectory:

[
mathbf{p}_t = \bigl(p^{(1)}_t, dots, p^{(L)}_t\bigr), quad t = 0,1,dots,T
]

We can define:

- **Polyphonic geodesics**: geodesics on (mathcal{M}_{\text{poly}}) under (g_{\text{poly}}).
- **Consensus geodesics**: projection of (mathbf{p}_t) onto (mathcal{M}_{\text{diag}}).
- **Conflict dynamics**: evolution of ( C_{\text{conflict}}(mathbf{p}_t) ) over time.

Hypothesis:  
- Successful multi‑lens reasoning follows trajectories where:
  - Each lens improves (e.g., lower loss, higher Fisher information).
  - Conflict cost evolves in a structured way (e.g., high early, then reduced but not eliminated).

---

## Relation to Agent Swarms

The engineering pattern:

> “A swarm of agents that argue different lenses… a verdict that keeps the conflict”

maps to PRMs as:

- **Agents** → conditional distributions ( p^{(ell)} ).
- **Parallel, independent analysis** → product manifold with block‑diagonal metric.
- **Merge that keeps conflict** → representation of (mathbf{p}) without collapsing to ( \bar{p} ).
- **Verdict** → tuple ((p^{star}, {delta^{(ell)}}, C_{\text{conflict}})).

The difference: PRMs are not a heuristic architecture; they are a **geometric object** with metrics, distances, and dynamics.

---

## Proposed Experiments

1. **Toy model with Gaussian lenses**  
   - Let each ( p^{(ell)} ) be a Gaussian over a 2D reasoning space with different means/covariances.  
   - Compute:
     - Consensus ( p^{star} ) (Fisher–Rao barycenter).
     - Conflict cost ( C_{\text{conflict}} ).
   - Visualize:
     - Each lens as an ellipse.
     - Consensus as a central ellipse.
     - Conflict cost as a scalar label.

2. **Neural lenses**  
   - Define lenses as different heads or prompts on a single model (e.g., “investor”, “engineer”, “user”, “devil’s advocate”).  
   - For a fixed task, extract:
     - Distribution over answers or latent trajectories per lens.
   - Approximate:
     - Pairwise distances between lenses.
     - Consensus and conflict cost.

3. **Conflict vs Performance**  
   - Measure whether tasks with moderate ( C_{\text{conflict}} ) outperform both:
     - Near‑zero conflict (all lenses agree too early).
     - Very high conflict (no usable consensus).

---

## Open Questions

- What is the right notion of “lens” in a transformer: attention heads, prompt variants, fine‑tuned LoRA adapters, or something else?
- Is Fisher–Rao the right metric, or should we use Wasserstein, or a hybrid?
- Can conflict cost be used as a regularizer during training to encourage *productive disagreement*?
- How does ( C_{\text{conflict}} ) relate to hallucination, robustness, and calibration?

---

## Connection to Existing Notes

- **#003 / #005:** Uses Fisher information and geodesics as the base geometry.
- **#009:** Conflict modes can be viewed as correlations across “sheets” of the manifold, analogous to entanglement.
- **#020:** Alternative metrics (Wasserstein) can define alternative polyphonic manifolds.
- **#027:** Conflict cost can be interpreted as part of an extractability budget: how much signal can be extracted before forcing consensus destroys structure.

---

## Planned Visualization

A simple figure:

- 2D plane with three ellipses (lenses).
- A central ellipse (consensus).
- Arrows from consensus to each lens.
- Label: ( C_{\text{conflict}} = sum d_{\text{FR}}^2 ).

This can be generated as `figures/note031_polyphonic_manifold.png` in a follow‑up commit.
