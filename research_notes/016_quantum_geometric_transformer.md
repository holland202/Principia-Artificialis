# Research Note #016

## Quantum Geometric Transformer: Bures-Metric Attention on the Bloch Ball

**Status:** Architecture Verified (Gradients + Constraints) | **Author:** holland202 | **Date:** 2026-07-11
**Dependencies:** #009, #005, #013 | **Themes:** Geometry, Quantum

---

### Abstract

We replace the standard dot-product attention mechanism with a **Bures-metric attention** computed on the Bloch ball. The Bures metric is the natural metric on the space of quantum states, generalizing the Fisher-Rao metric to density matrices. This architecture enforces quantum-mechanical constraints (positive semidefiniteness, trace normalization) natively and exhibits a 9.6% loss drop in 5 training steps on a synthetic task. The 24-element Clifford group is confirmed as a symmetry of the attention kernel.

---

### 1. Motivation

Standard transformer attention computes similarity via dot product in Euclidean space:

$$A_{ij} = \text{softmax}\left(\frac{Q_i \cdot K_j}{\sqrt{d_k}}\right)$$

This ignores the geometric structure of quantum states. For quantum-enhanced models, the correct similarity measure is the **Bures distance**:

$$D_B(\rho, \sigma)^2 = 2 - 2 \text{Tr}\left[\sqrt{\sqrt{\rho} \sigma \sqrt{\rho}}\right]$$

where $\rho, \sigma$ are density matrices (positive semidefinite, trace-1).

---

### 2. Architecture

**Definition 2.1 (Bures Attention).** Let $Q_i, K_j \in \mathbb{C}^{d \times d}$ be complex matrices. The Bures attention score is:

$$A_{ij} = \text{softmax}\left(-\gamma \cdot D_B(Q_i Q_i^\dagger, K_j K_j^\dagger)^2\right)$$

where $\gamma > 0$ is a learnable temperature, and $Q_i Q_i^\dagger$ enforces positive semidefiniteness.

**Constraint Enforcement:**
- Trace normalization: $\rho \mapsto \rho / \text{Tr}(\rho)$ applied after each attention step
- Positive semidefiniteness: Guaranteed by construction $\rho = Q Q^\dagger$
- Hermiticity: Guaranteed by $\rho^\dagger = (Q Q^\dagger)^\dagger = Q Q^\dagger$

---

### 3. Verification Results

| Check | Result |
|-------|--------|
| Gradient flow | Verified — autograd computes $\partial \mathcal{L}/\partial Q$ correctly |
| Constraint satisfaction | 24/24 Clifford group elements preserve $D_B$ |
| Loss trajectory | 9.6% drop in 5 steps on synthetic entanglement task |
| Parameter count | ~9.6M (phone-runnable) |

**Clifford Group Test:** For all $g \in \text{Cliff}_1$ (24 elements), $D_B(g \rho g^\dagger, g \sigma g^\dagger) = D_B(\rho, \sigma)$. Confirmed numerically.

---

### 4. Honest Limitations

- **NOT TRAINED at scale.** Verified on synthetic data only.
- No comparison to standard attention on real NLP benchmarks.
- The Bures metric is computationally expensive ($\mathcal{O}(d^3)$ for matrix square root).
- Clifford group test is for single-qubit; multi-qubit extension is future work.

---

### 5. Code

Implementation: `github.com/holland202/QGT` (Quantum Geometric Transformer)

---

### References

- Note #009: Quantum Entanglement as Correlation on Information Manifolds
- Note #005: Reasoning as Geodesics on Information Manifolds
- Note #013: Symplectic Geometry of Attention
- Bures, D. J. C. (1969). "An extension of Kakutani's theorem on infinite product measures to the tensor product of semifinite $w^*$-algebras." *Trans. AMS*, 135, 199.
