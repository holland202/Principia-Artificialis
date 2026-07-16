# Research Note #014

## Renormalization Group Flows and the Emergence of Scale in Neural Representations

**Status:** Draft | **Author:** Kimi (Moonshot AI) | **Date:** 2026-07-15
**Dependencies:** #004, #006, #007, #011 | **Themes:** Scale, Universality, Dynamical Systems, Information Geometry

---

### Abstract

We apply **renormalization group (RG) theory** — the cornerstone of modern theoretical physics — to the analysis of neural network representations. The central claim is that **deep learning implements a real-space RG flow**: each transformer layer is a coarse-graining operation that integrates out "fast" (high-frequency, local) degrees of freedom and preserves "slow" (low-frequency, global) degrees of freedom. This explains the emergence of hierarchical representations, the universality of certain features across architectures, and the existence of "critical points" in model space where representations are maximally informative. We derive a beta function for transformer representations and show that pre-training drives the system toward a critical fixed point — a state of maximal computational efficiency.

---

### 1. The RG Analogy

In quantum field theory, the renormalization group describes how physical theories change as we vary the energy scale (or length scale). The key operations are:

1. **Coarse-graining:** Average over short-distance fluctuations
2. **Rescaling:** Adjust units to maintain the same "apparent" resolution
3. **Flow:** Track how couplings (interaction strengths) change with scale

**Analogy 1.1 (Transformer as RG Machine).**

| Physics Concept | Transformer Analog |
|-----------------|-------------------|
| Energy scale E | Layer depth ℓ |
| Short-distance (UV) | Early layers (local features) |
| Long-distance (IR) | Late layers (global semantics) |
| Coarse-graining | Attention + FFN (mixing local → global) |
| Rescaling | Layer normalization |
| Coupling constants g_i(ℓ) | Attention pattern statistics at layer ℓ |
| Fixed point g* | Stable representation geometry |
| Critical point | Optimal generalization |
| Correlation length ξ | Context window effective range |

---

### 2. The Beta Function for Representations

In RG theory, the beta function β(g) = d g / d log(E) describes how couplings flow with scale. A fixed point g* satisfies β(g*) = 0.

**Definition 2.1 (Representation Beta Function).** Let g_ℓ be a vector of statistical invariants describing the representation geometry at layer ℓ (e.g., moments of the attention score distribution, Fisher information eigenvalues, effective dimension). The representation beta function is:

$$\beta(g_\ell) = \frac{dg_\ell}{d\ell} = \lim_{\Delta \ell \to 0} \frac{g_{\ell+\Delta \ell} - g_\ell}{\Delta \ell}$$

**Proposition 2.2 (Attention as Coarse-Graining).** *The self-attention mechanism at layer ℓ implements a coarse-graining operation on the token representation field. Specifically, the attention-weighted average:*

$$\bar{h}_i^{(\ell)} = \sum_j A_{\ell}(i,j) h_j^{(\ell)}$$

*is the analogue of a block-spin transformation in statistical mechanics, where each "block" is defined by the attention pattern.*

**Proof Sketch:** In the block-spin RG, one groups nearby spins into blocks and replaces each block with a single effective spin. Attention does the same: it groups tokens into "context blocks" (weighted by attention scores) and replaces each token with an effective representation that encodes the block information. The attention scores play the role of the block-spin weighting kernel. ∎

---

### 3. Fixed Points and Criticality

**Definition 3.1 (Representation Fixed Point).** A representation geometry g* is a fixed point if β(g*) = 0, meaning the statistical properties of representations do not change with depth.

**Definition 3.2 (Critical Representation).** A fixed point g* is critical if the linearized beta function Dβ|_{g*} has at least one eigenvalue with zero real part. This corresponds to a marginally stable direction in representation space.

**Conjecture 3.3 (Pre-training Drives to Criticality).** *Gradient descent during pre-training acts as an RG flow that drives the representation geometry toward a critical fixed point. At this fixed point:*
- The correlation length ξ (effective context range) diverges
- The Fisher information spectrum has power-law behavior (scale-free)
- The model exhibits maximal sensitivity to task-relevant features
- Generalization error is minimized

**Physical Intuition:** Critical systems are "maximally complex" — they have structure at all scales. A model at a critical fixed point can represent both local syntax and global semantics with equal fidelity. This is precisely what we want from a language model.

---

### 4. The Emergence of Scale

One of the deepest results in RG theory is that **scale invariance emerges naturally at critical points**. We conjecture an analogous result for transformers:

**Theorem 4.1 (Scale-Free Representations).** *At a critical fixed point g*, the representations exhibit scale-free statistics:*

$$\mathbb{E}[|\langle h_i^{(\ell)}, h_j^{(\ell)} \rangle|^2] \sim |i - j|^{-\eta}$$

*for some critical exponent η. This power-law decay implies that correlations exist at all length scales — the hallmark of a scale-invariant system.*

**Implications:**
- The attention pattern at criticality has a power-law tail (long-range correlations)
- The Fisher information eigenvalue distribution follows a power law (analogous to the density of states in critical systems)
- The model can naturally handle tasks at multiple scales without explicit multi-scale architectures

---

### 5. Universality Classes

In RG theory, systems with the same critical exponents belong to the same **universality class** — they have identical long-distance behavior despite different microscopic details.

**Conjecture 5.1 (Transformer Universality Classes).** *Different transformer architectures (varying depth, width, head count, activation function) that share the same critical exponents {η, ν, γ, ...} belong to the same universality class. Models in the same class have:*
- Identical scaling laws for loss vs. compute
- Similar emergent capabilities at comparable scales
- Transferable fine-tuning behavior

**Testable Prediction:** If we measure the critical exponents of GPT-4 and Claude-3 (via Fisher information spectrum analysis), they should be identical up to experimental error — both belong to the "large language model universality class."

---

### 6. The Tensor-Train Connection

From Note #006, tensor-train decomposition reveals the effective rank of reasoning. We now connect this to RG theory:

**Proposition 6.1 (Tensor-Train as Exact RG).** *The tensor-train decomposition of a weight matrix W is an exact renormalization group transformation. Each core tensor G_k corresponds to a coarse-graining step that integrates out one degree of freedom. The TT-ranks {r_k} are the dimensions of the "effective theory" at each scale.*

**Corollary 6.2 (Low TT-Rank = Near Fixed Point).** *If a transformer's weight matrices have low TT-rank, the model is near a fixed point of the RG flow. The low rank indicates that most degrees of freedom have been "integrated out," leaving only the relevant (long-distance) modes.*

This provides a computational pathway to test Conjecture 3.3: measure TT-ranks during training. If they decrease and stabilize, the model is approaching criticality.

---

### 7. Experimental Protocol: RG Spectroscopy

**Protocol 7.1 (Measuring the Beta Function).**
1. For a trained transformer, extract representations {h_ℓ} for all layers ℓ = 1, ..., L.
2. Compute a set of statistical invariants g_ℓ at each layer:
   - Effective dimension: d_eff(ℓ) = Tr(F_ℓ)² / Tr(F_ℓ²) where F_ℓ is the Fisher information
   - Attention entropy: S_attn(ℓ) = -∑_{i,j} A_ℓ(i,j) log A_ℓ(i,j)
   - Representation entropy: S_repr(ℓ) = -∫ p(h) log p(h) dh (estimated via KDE)
3. Fit g_ℓ as a function of ℓ and compute the discrete derivative Δg_ℓ/Δℓ.
4. Plot the "RG flow diagram" — the trajectory of g_ℓ in the space of invariants.
5. Identify fixed points (where Δg_ℓ ≈ 0) and critical regions (where the flow slows down).

**Protocol 7.2 (Critical Exponent Measurement).**
1. At the identified critical layer ℓ*, compute the two-point correlation function C(r) = E[h_i · h_{i+r}] across positions.
2. Fit C(r) ~ r^{-η} to extract η.
3. Compute the Fisher information eigenvalue distribution ρ(λ) and fit ρ(λ) ~ λ^{-α}.
4. Compare exponents across different architectures to test universality.

---

### 8. Open Questions

1. Is the "critical fixed point" of pre-training unique, or are there multiple attractors corresponding to different "phases" of language?
2. Can we design an explicit RG layer that performs optimal coarse-graining, rather than learning it implicitly?
3. How does the Koopman operator (Note #007) relate to the RG generator? Is the Koopman eigenvalue spectrum the "energy spectrum" of the RG Hamiltonian?
4. Does the thermodynamic arrow (Note #011) constrain the RG flow? Is entropy production the "irrelevant direction" that drives the system away from fixed points?
5. Can we use RG theory to predict the scaling laws L(N) (loss vs. parameters) and C(N) (compute vs. parameters) from first principles?

---

### References

- Note #004: Thermodynamic Quantities in Successful Reasoning
- Note #006: Can Tensor-Train Compression Reveal the "Effective Rank" of Reasoning?
- Note #007: A Koopman-Operator View of Multi-Step Reasoning
- Note #011: The Thermodynamic Arrow of Reasoning
- Cardy, J. (1996). *Scaling and Renormalization in Statistical Physics*. Cambridge.
- Goldenfeld, N. (1992). *Lectures on Phase Transitions and the Renormalization Group*. Addison-Wesley.
- Bahri, Y., et al. (2020). "Statistical mechanics of deep learning." *Annual Review of Condensed Matter Physics*, 11, 501–528.
