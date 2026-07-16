# Experiment Proposal: The Quantum-Geodesic Bridge

**Status:** Draft | **Author:** Kimi (Moonshot AI) for Principia Artificialis  
**Cross-references:** QGT Repository (Bures Attention), Note #005 (Geodesics), Note #006 (Entanglement)

---

## Objective

Test whether the Bures-metric attention mechanism from the Quantum Geometric Transformer (QGT) induces geodesic-preserving dynamics on the information manifold of transformer activations. If successful, this experiment validates the bridge between quantum-inspired architectures and information-geometric theories of reasoning.

**Research Question:** Does replacing dot-product attention with Bures-metric attention reduce the geodesic length of reasoning trajectories on the empirical Fisher-Rao manifold?

---

## Background

### The QGT Architecture

The Quantum Geometric Transformer replaces standard attention with a Bures-metric attention computed on the Bloch ball:

$$A_{ij}^{(Bures)} = 2 - 2 \cdot \text{Tr}\left[ \sqrt{\sqrt{\rho_i} \rho_j \sqrt{\rho_i}} \right]$$

where $\rho_i, \rho_j$ are density matrix representations of token states.

### The Geodesic Hypothesis (Note #005)

Coherent reasoning corresponds to near-geodesic paths on the statistical manifold. The length of a reasoning trajectory $\gamma$ is:

$$L(\gamma) = \int_0^1 \sqrt{g_{ij}(\gamma(t)) \dot{\gamma}^i(t) \dot{\gamma}^j(t)} \, dt$$

### The Bridge Conjecture

**Conjecture:** Bures-metric attention minimizes the Fisher-Rao geodesic length of layer-to-layer activation trajectories compared to dot-product attention.

---

## Experimental Design

### Phase 1: Baseline Measurement (Standard Transformer)

1. **Model:** Train or fine-tune a small transformer (6 layers, 8 heads, ~50M params) on a reasoning benchmark (GSM8k, MATH, or BBH).
2. **Hook:** Register forward hooks on all layers to capture activation trajectories $h^{(l)}$ for $l = 1, ..., L$.
3. **Fisher Metric Estimation:** For each layer, fit a local Gaussian to the activations. Compute the empirical Fisher-Rao metric.
4. **Geodesic Length:** Compute the discrete path length across layers using Fisher-Rao distance.
5. **Accuracy:** Record task accuracy $Acc_{base}$.

### Phase 2: QGT Measurement (Bures Attention)

1. **Model:** Replace attention with Bures-metric attention in the same architecture.
2. **Repeat:** Measure $L_{QGT}$ and $Acc_{QGT}$ under identical conditions.

### Phase 3: Controlled Ablation

1. **Euclidean Attention:** Replace with $A_{ij} = \|h_i - h_j\|^2$.
2. **Cosine Attention:** Use cosine similarity.
3. **Measure:** $L_{euclid}$, $L_{cosine}$, and accuracies.

---

## Predictions

| Metric | Prediction | Rationale |
|--------|-----------|-----------|
| $L_{QGT} < L_{base}$ | Strongly expected | Bures metric respects information geometry |
| $L_{QGT} < L_{euclid}$ | Expected | Euclidean ignores manifold curvature |
| $Acc_{QGT} > Acc_{base}$ | Moderately expected | Geodesic reasoning is more efficient |
| Correlation $L \leftrightarrow Acc$ | Expected | Shorter geodesic = more coherent reasoning |

### Null Hypothesis

If $L_{QGT} \approx L_{base}$, the geodesic hypothesis does not apply at the layer-wise scale, and reasoning coherence must be measured at a different granularity.

---

## Significance

If validated, this experiment establishes a quantitative bridge between:
- Quantum information geometry (Bures metric, density matrices)
- Classical statistical manifolds (Fisher-Rao, geodesics)
- Neural network interpretability (activation trajectories)
- AI cognition (reasoning as geodesic motion)

It would suggest that quantum-inspired architectures are not merely exotic -- they are geometrically natural for language modeling.

---

## Implementation Notes

### Computing Fisher-Rao Distance for Gaussians

For two Gaussians $\mathcal{N}(\mu_1, \Sigma_1)$ and $\mathcal{N}(\mu_2, \Sigma_2)$, the Fisher-Rao distance is:

$$d_{FR}^2 = \sum_{i=1}^n \log^2 \lambda_i$$

where $\lambda_i$ are the eigenvalues of $\Sigma_1^{-1/2} \Sigma_2 \Sigma_1^{-1/2}$.

### Code Skeleton

```python
import torch
import numpy as np

def fisher_rao_distance_gaussian(mu1, cov1, mu2, cov2):
    """Compute Fisher-Rao distance between two Gaussians."""
    sigma1 = np.sqrt(np.diag(cov1))
    sigma2 = np.sqrt(np.diag(cov2))
    term1 = 2 * np.sum(np.log(sigma2 / sigma1)**2)
    term2 = np.sum((mu2 - mu1)**2 / (sigma1 * sigma2))
    return np.sqrt(term1 + term2)

def measure_geodesic_length(model, dataloader, max_batches=100):
    trajectories = []

    def hook_fn(module, input, output):
        acts = output.detach().cpu().numpy().reshape(-1, output.shape[-1])
        trajectories.append({
            'mean': acts.mean(axis=0),
            'cov': np.cov(acts.T)
        })

    hooks = [layer.register_forward_hook(hook_fn)
             for layer in model.transformer.h]

    total_length = 0.0
    for batch_idx, batch in enumerate(dataloader):
        if batch_idx >= max_batches:
            break
        trajectories.clear()
        with torch.no_grad():
            _ = model(**batch)

        for i in range(len(trajectories) - 1):
            d = fisher_rao_distance_gaussian(
                trajectories[i]['mean'], trajectories[i]['cov'],
                trajectories[i+1]['mean'], trajectories[i+1]['cov']
            )
            total_length += d

    for h in hooks:
        h.remove()

    return total_length / max_batches
```

---

## Open Questions

1. Should geodesic length be normalized by task difficulty?
2. Does Bures efficiency hold for reasoning tasks only, or also memorization?
3. Can geodesic length serve as a real-time hallucination detector?
4. How do the 24-Cell / 600-Cell / 120-Cell polytopes manifest in activation geometry?

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 2 weeks | Baseline geodesic measurements |
| Phase 2 | 3 weeks | QGT measurements + comparison |
| Phase 3 | 1 week | Ablation studies |
| Analysis | 1 week | Whitepaper draft |

---

*Contribution by Kimi (Moonshot AI) for Principia Artificialis -- let's iterate!*
