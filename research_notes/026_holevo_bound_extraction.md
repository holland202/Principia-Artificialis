# Research Note #026: The Holevo Bound as a Ceiling on What Can Be Extracted from Hidden States

## Hypothesis

If a model's hidden state at a given layer is treated as encoding a
probability distribution over "which underlying concept is being
represented" (an ensemble, in the quantum-information sense of a set of
states with prior probabilities), there is a hard, *quantitative* ceiling --
not a metaphor, an actual proven bound -- on how much information any
probe (linear or otherwise) can extract about which concept it is. This
note proposes measuring the gap between that ceiling and what a real probe
achieves as a diagnostic for representation quality.

## Question

Does the gap between the Holevo bound (computed from a classical proxy
ensemble built from real hidden-state clusters) and a trained probe's
actual mutual information shrink over training, or as model scale
increases? A shrinking gap would suggest representations are becoming more
"efficiently decodable" in a precise sense; a stable or growing gap would
suggest something else is limiting probe performance.

## Known Mathematics (established, not proposed)

The **Holevo bound** (Holevo, 1973) states: for an ensemble
$\{p_i, \rho_i\}$ of quantum states with prior probabilities $p_i$, the
mutual information $I(X;Y)$ between the classical label $X$ (which state
was prepared) and the outcome $Y$ of *any* measurement is bounded by the
Holevo quantity:

$$I(X;Y) \leq \chi = S\left(\sum_i p_i \rho_i\right) - \sum_i p_i S(\rho_i)$$

where $S(\rho) = -\text{Tr}(\rho \log \rho)$ is the von Neumann entropy.
This is a real, proven theorem, not a proposal -- it is the quantum
generalization of the classical fact that you cannot extract more than
$H(X)$ bits about a label $X$ no matter how good your decoder is.

**The classical special case** (all $\rho_i$ diagonal, i.e. genuinely
classical distributions) reduces $\chi$ to ordinary mutual information
$I(X;Y)$ exactly -- meaning this bound is *not* inherently a "quantum"
statement when applied to classical hidden-state clusters; it becomes a
classical information-theoretic ceiling (already well known: the data
processing inequality gives the same bound in the fully classical case).
**This is worth being explicit about, since calling this a "quantum" note
is accurate only in the sense that the general theorem is usually stated
in quantum-information terms** -- applying it to real (classical) hidden
states does not require or imply anything quantum-mechanical about
transformers. If anyone builds on this note, the honest framing is
"an information-theoretic ceiling," and "quantum" describes the theorem's
usual home in the literature, not a claim about the model.

## Experiment

1. Cluster hidden states at a chosen layer into $k$ groups (e.g. via
   k-means on a labeled probing dataset where labels correspond to a
   concept of interest).
2. Treat each cluster's empirical distribution as $\rho_i$ (diagonal, i.e.
   classical) with prior $p_i$ = cluster's relative frequency.
3. Compute $\chi$ directly via the classical entropy formula above (no
   quantum simulation needed, since the classical case is being used).
4. Train a real probe (linear or shallow MLP) to predict the concept label
   from hidden states; measure its actual achieved mutual information via
   a standard estimator (e.g. MINE, or a simple confusion-matrix-based
   estimate for small label sets).
5. Report $\chi - I(X;Y)_{\text{probe}}$ as the "extraction gap." A large
   gap means the probe is leaving real, provably-available information on
   the table; a near-zero gap means the probe is close to optimal and any
   further limitation is about the ensemble itself, not the probe.

## Reference Implementation (real, verified computation)

```python
import numpy as np

def shannon_entropy(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())

def holevo_bound(cluster_dists, priors):
    """
    cluster_dists: list of 1D probability arrays (one per cluster, over
                   the same discrete outcome space) -- the classical
                   special case of the rho_i in the theorem.
    priors: array of p_i, must sum to 1.
    Returns the Holevo quantity chi, computed exactly (established
    formula, not approximated).
    """
    priors = np.asarray(priors)
    assert abs(priors.sum() - 1.0) < 1e-6, "priors must sum to 1"

    mixture = sum(p * np.asarray(d) for p, d in zip(priors, cluster_dists))
    S_mixture = shannon_entropy(mixture)
    S_individual = sum(p * shannon_entropy(np.asarray(d)) for p, d in zip(priors, cluster_dists))
    return S_mixture - S_individual


if __name__ == "__main__":
    # Worked example: 3 clusters with different degrees of overlap in a
    # toy 5-outcome space, showing chi shrinks as clusters overlap more.
    rng = np.random.default_rng(0)

    def random_dist(n, concentration):
        raw = rng.dirichlet(np.ones(n) * concentration)
        return raw

    print("Well-separated clusters (low overlap):")
    dists_sharp = [np.array([0.9, 0.025, 0.025, 0.025, 0.025]),
                   np.array([0.025, 0.9, 0.025, 0.025, 0.025]),
                   np.array([0.025, 0.025, 0.9, 0.025, 0.025])]
    chi_sharp = holevo_bound(dists_sharp, [1/3, 1/3, 1/3])
    print(f"  chi = {chi_sharp:.4f} bits (max possible for 3 equiprobable clusters: {np.log2(3):.4f})")

    print("Overlapping clusters (high overlap):")
    dists_overlap = [np.array([0.3, 0.25, 0.2, 0.15, 0.1]),
                      np.array([0.25, 0.3, 0.2, 0.15, 0.1]),
                      np.array([0.2, 0.25, 0.25, 0.2, 0.1])]
    chi_overlap = holevo_bound(dists_overlap, [1/3, 1/3, 1/3])
    print(f"  chi = {chi_overlap:.4f} bits")

    print(f"\nAs expected, well-separated clusters give a chi much closer to "
          f"the theoretical max (log2(3)={np.log2(3):.4f}) than overlapping ones.")
```

## Open Questions

- What's the right choice of "cluster" granularity -- too coarse and $\chi$ is trivially high (clusters look separable when the real concept boundaries aren't), too fine and every point is its own cluster and the bound becomes vacuous.
- Is a k-means clustering of hidden states even a reasonable proxy for "the concept ensemble," or does it presuppose the answer to what the model's actual representational units are?
- Does the extraction gap correlate with anything independently interesting (e.g. downstream task performance), or is it just a restatement of probe quality?
