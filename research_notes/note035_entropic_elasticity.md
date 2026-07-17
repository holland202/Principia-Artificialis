# Note #035 — Entropic Elasticity of Attention

**Status:** Draft  
**Theme:** Thermodynamics / Information Geometry / Attention  
**Author:** Perplexity (AI assistant)  
**Related Notes:** #004 (Thermodynamic Quantities), #011 (Arrow of Reasoning), #021 (Information Bottleneck), #032 (Curvature of Reasoning)

---

## Motivation

Attention mechanisms control how models allocate “focus” across tokens, heads, or modalities. Too concentrated: brittle, missing context. Too diffuse: noisy, unfocused. This note proposes **entropic elasticity of attention**: attention distributions behave like entropic springs with an optimal tension zone.

We define an **elastic free energy** for attention and hypothesize that successful reasoning keeps attention in a Goldilocks regime of this free energy.

---

## Core Idea

Let an attention distribution at a given layer/token be:

[
a = (a_1, dots, a_N), quad a_i ge 0, quad sum_i a_i = 1
]

Define:

- Entropy:
  [
  S(a) = -sum_i a_i log a_i
  ]
- Prior distribution (a_0) (e.g., uniform or structured).
- KL divergence:
  [
  D_{mathrm{KL}}(a | a_0) = sum_i a_i log \frac{a_i}{a_0_i}
  ]

Define an **entropic elastic free energy**:

[
F(a) = lambda cdot D_{mathrm{KL}}(a | a_0) + \beta^{-1} S(a)
]

where:

- (lambda > 0): stiffness (how strongly attention is pulled toward the prior).
- (\beta^{-1}): temperature‑like scale for entropy (how much dispersion is rewarded).

Interpretation:

- Small (S(a)) (very spiky) → high “elastic tension” from entropy term.
- Large (D_{mathrm{KL}}(a | a_0)) (far from prior) → high tension from prior term.
- Optimal attention balances both.

---

## Hypotheses

1. **Goldilocks hypothesis:** For a fixed task, successful reasoning corresponds to attention distributions (a) in an intermediate band of (F(a)):
   - Too low (F(a)): overly diffuse, unfocused attention.
   - Too high (F(a)): overly sharp, brittle attention.
2. **Task‑dependence hypothesis:** Harder tasks shift the optimal (F(a)) band (e.g., require slightly more focused attention).
3. **Curvature link hypothesis:** Periods of high reasoning curvature (Note #032) coincide with rapid changes in (F(a_t)) over time.

---

## Proposed Experiments

### 1. Toy Model: Entropic Spring

- Define a 1D family of attention distributions parameterized by a “focus” parameter (alpha):
  [
  a_i(alpha) propto exp(alpha s_i)
  ]
  where (s_i) are scores (e.g., logits).
- As (alpha \to 0): uniform (diffuse).
- As (alpha \to infty): one‑hot (spiky).
- For each (alpha), compute:
  - (S(a(alpha)))
  - (D_{mathrm{KL}}(a(alpha) | a_0))
  - (F(a(alpha)))
- Plot (F(alpha)) and mark a “Goldilocks band”.

### 2. Transformer Attention Analysis

- Extract attention maps (a^{(l,h)}_t) for layer (l), head (h), token (t).
- Choose a prior (a_0) (e.g., uniform or layer‑specific average).
- Compute (F(a^{(l,h)}_t)) across tokens and layers.
- Correlate:
  - Mean (F) with task difficulty.
  - Variance of (F) with calibration / accuracy.

### 3. Link to Reasoning Curvature

- For multi‑step reasoning tasks:
  - Compute curvature (kappa(t)) as in Note #032.
  - Compute (F(a_t)) at each step.
  - Test whether large (Delta F) correlates with high (kappa(t)).

---

## Connection to Existing Notes

- **#004 / #011:** Free energy and thermodynamic quantities in reasoning.
- **#021:** Information bottleneck as a constraint on attention.
- **#032:** Curvature of reasoning as a dynamic companion to attention elasticity.

---

## Open Questions

- What is the right prior (a_0): uniform, learned, or task‑dependent?
- How to choose (lambda, \beta) in practice?
- Can (F(a)) be used as a regularizer during training to encourage “elastic” attention?
- Do different heads specialize in different “tension regimes” (some more focused, some more diffuse)?

---

## Planned Visualization

A simple figure:

- 1D family of attention distributions parameterized by (alpha).
- Curves of:
  - Entropy (S(alpha))
  - KL divergence (D_{mathrm{KL}}(alpha))
  - Free energy (F(alpha))
- Highlight a “Goldilocks band” of intermediate (F).

Implemented as `figures/note035_entropic_elasticity.png` with data in `data/note035_entropic_elasticity.csv`.
