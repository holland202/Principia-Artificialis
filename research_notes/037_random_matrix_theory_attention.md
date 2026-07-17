# Research Note #037: Random Matrix Theory Level-Spacing Statistics on Attention Weight Spectra

## Hypothesis

Quantum chaos theory has a precise, well-tested way to distinguish
"chaotic" from "integrable" (regular) dynamics using nothing but the
eigenvalue spectrum of an operator: the statistics of gaps between
consecutive eigenvalues. If trained attention weight matrices carry a
signature of this kind, it would say something concrete and measurable
about whether a layer's dynamics are closer to "chaotic mixing" or
"regular/structured" -- and unlike most notes in this repo, **this one
needs no hidden-state hooks, no benchmark labels, and no training run: it
can be computed today from a single downloaded model's weight files.**

## Question

Do the eigenvalues of trained attention weight matrices (e.g. $W_Q W_K^T$,
or the combined QK circuit) show Wigner-Dyson level-spacing statistics
(associated with chaotic systems), Poisson statistics (associated with
integrable/regular systems), or neither -- and does this differ between
early and late layers, or between attention heads that are known to
specialize (e.g. induction heads) versus generic heads?

## Known Mathematics (established, not proposed)

For a random Hermitian matrix drawn from the **Gaussian Orthogonal
Ensemble (GOE)**, the spacings $s_i = \lambda_{i+1} - \lambda_i$ between
consecutive (unfolded/normalized) eigenvalues follow the **Wigner surmise**:

$$P(s) = \frac{\pi s}{2} \exp\left(-\frac{\pi s^2}{4}\right)$$

This is the level-repulsion signature: small gaps are suppressed
($P(0) = 0$), because GOE eigenvalues "repel" each other. By contrast, for
a sequence of **uncorrelated (Poisson) levels** -- the signature of
integrable/regular systems -- the spacing distribution is exponential:

$$P(s) = \exp(-s)$$

with no repulsion ($P(0)$ is maximal). The **Bohigas-Giannoni-Schmit
conjecture** (1984) proposes that quantum systems whose classical limit is
chaotic show GOE/Wigner-Dyson statistics, while integrable systems show
Poisson statistics -- a real, extensively tested (though still officially a
conjecture, not a theorem) result in quantum chaos physics. This machinery
is unrelated to any claim about neural networks; it is used here purely as
a diagnostic tool with well-understood null distributions.

## Experiment

1. Download a small open model's weights (e.g. GPT-2 small).
2. For each attention head in each layer, form the relevant matrix (e.g.
   $W_Q W_K^T$, symmetrized if needed to have real eigenvalues, or just use
   singular values if a non-symmetric treatment is preferred -- state which
   choice was made, since they are not interchangeable).
3. Compute eigenvalues, **unfold the spectrum** (a standard RMT preprocessing
   step: rescale so the local mean level density is 1, removing
   system-specific overall scale so only the *fluctuation* statistics
   remain) using a standard method (e.g. fit and subtract a smooth
   polynomial trend to the cumulative spectral counting function).
4. Compute the nearest-neighbor spacing distribution and compare (e.g. via
   KS test) against both the Wigner surmise and the Poisson distribution.
5. Repeat across layers/heads and report which null is closer, and whether
   there's a systematic layer-depth or head-specialization trend. This has
   not been run yet in this repo -- the reference code below verifies the
   two reference distributions themselves are implemented correctly, using
   real GOE-sampled matrices as ground truth, not model weights.

## Reference Implementation (real, verified computation)

```python
import numpy as np
from scipy import stats

def sample_goe(n, rng):
    """A real GOE sample: symmetrize a random Gaussian matrix."""
    a = rng.standard_normal((n, n))
    return (a + a.T) / np.sqrt(2 * n)

def unfold_spectrum(eigenvalues, poly_degree=5):
    """
    Standard RMT unfolding: fit a smooth polynomial to the empirical
    cumulative distribution (staircase function) of eigenvalues, then use
    it to rescale spacings so the mean local spacing is 1. This removes
    the overall spectral shape, leaving only fluctuation statistics.
    """
    ev = np.sort(eigenvalues)
    n = len(ev)
    empirical_cdf_counts = np.arange(1, n + 1)
    coeffs = np.polyfit(ev, empirical_cdf_counts, poly_degree)
    smooth_cdf = np.poly1d(coeffs)
    unfolded = smooth_cdf(ev)
    return np.diff(unfolded)  # nearest-neighbor spacings, unfolded

def wigner_surmise_pdf(s):
    return (np.pi * s / 2) * np.exp(-np.pi * s**2 / 4)

def poisson_pdf(s):
    return np.exp(-s)

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = 400
    goe_matrix = sample_goe(n, rng)
    eigenvalues = np.linalg.eigvalsh(goe_matrix)

    spacings = unfold_spectrum(eigenvalues)
    spacings = spacings[(spacings > 0) & (spacings < 5)]  # drop numerical outliers at edges

    mean_spacing = spacings.mean()
    print(f"Mean unfolded spacing (should be close to 1.0): {mean_spacing:.4f}")

    # Compare empirical spacing histogram against both reference laws
    ks_wigner = stats.ks_2samp(
        spacings,
        # Sample from Wigner surmise via inverse-transform-free rejection sampling
        rng.rayleigh(scale=np.sqrt(2 / np.pi), size=len(spacings))
    )
    ks_poisson = stats.ks_2samp(spacings, rng.exponential(scale=1.0, size=len(spacings)))

    print(f"KS statistic vs Wigner-like reference sample: {ks_wigner.statistic:.4f} (p={ks_wigner.pvalue:.4f})")
    print(f"KS statistic vs Poisson reference sample:      {ks_poisson.statistic:.4f} (p={ks_poisson.pvalue:.4f})")
    print("\nFor a REAL GOE matrix (this test), the Wigner comparison should")
    print("show a much smaller KS statistic than the Poisson comparison --")
    print("confirming the reference pipeline correctly detects level repulsion")
    print("before it's ever pointed at real model weights.")
```

## Open Questions

- Is $W_Q W_K^T$ (or any single-matrix summary of a full attention head) even the right object to analyze, given attention is a bilinear form, not a linear operator with a single natural spectrum?
- How much data (how many heads/layers/models) is needed before a KS test has any real power here, given spectral statistics are traditionally computed on much larger matrices than a single attention head provides?
- If different layers show different statistics, is that a "chaos vs. structure" finding, or simply a restatement of known facts about attention specialization (e.g. induction heads having distinctive weight structure) via a fancier vocabulary?
