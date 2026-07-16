# Research Note #020: Optimal Transport as a Model for "Thought Transport"

*Directly follows up on Note #005's Open Question: "Links to optimal
transport and Wasserstein geometry for 'thought transport'?"*

## Hypothesis

If reasoning states are distributions over a concept/token space rather than
single points, the natural notion of "distance traveled while reasoning"
between two states is not Euclidean or even Fisher-Rao geodesic distance --
it's the Wasserstein distance from optimal transport theory, which measures
the minimum "cost" of morphing one distribution into another.

## Question

Does Wasserstein distance between consecutive layers' output distributions
(treating each layer's activation as inducing a distribution, e.g. via a
softmax readout or a kernel density estimate) predict reasoning difficulty
better than the Fisher-Rao geodesic length already proposed in Note #005?

## Known Mathematics (established, not proposed)

For probability measures $\mu, \nu$ on $\mathbb{R}^d$, the 2-Wasserstein
distance is:

$$W_2(\mu, \nu)^2 = \inf_{\pi \in \Pi(\mu, \nu)} \int \|x - y\|^2 \, d\pi(x, y)$$

where $\Pi(\mu, \nu)$ is the set of joint distributions with marginals $\mu$
and $\nu$ (Villani, *Optimal Transport: Old and New*, 2009). For Gaussians
$\mathcal{N}(m_1, \Sigma_1)$ and $\mathcal{N}(m_2, \Sigma_2)$, this has a
closed form:

$$W_2^2 = \|m_1 - m_2\|^2 + \text{Tr}\left(\Sigma_1 + \Sigma_2 - 2(\Sigma_2^{1/2} \Sigma_1 \Sigma_2^{1/2})^{1/2}\right)$$

which is exactly computable, not an approximation -- useful if activation
distributions per layer are approximated as Gaussian (a real, checkable
assumption, not automatically true).

The key structural difference from Note #005: Fisher-Rao geodesic distance
measures the shortest path *within* a fixed parametric family (e.g. varying
mean and variance of a single Gaussian). Wasserstein distance measures the
cost of transporting *mass* between two distributions and doesn't require
them to be in the same parametric family at all -- relevant if a
reasoning step's output distribution changes shape (e.g. unimodal to
bimodal), not just location/scale, which Fisher-Rao in Note #005's simple
Gaussian setup cannot represent.

## Experiment

1. For a small model, extract per-layer output distributions (e.g. softmax
   over the vocabulary, or a Gaussian fit to the hidden state across a batch
   of related prompts).
2. Compute both $W_2$ and the Note #005 Fisher-Rao geodesic length between
   consecutive layers, for the same reasoning and non-reasoning task sets
   Note #005 would use.
3. Compare which one (if either) better separates easy vs. hard reasoning
   examples, using the same permutation-test standard as Notes #003/#008.
4. If they're highly correlated, Wasserstein adds nothing here and that's a
   valid, reportable null result. If they diverge (e.g. Wasserstein catches
   distributional shape changes Fisher-Rao misses), that's the actual
   interesting finding -- not assumed here.

## Open Questions

- Is a Gaussian approximation of per-layer activations reasonable at all, or does it throw away exactly the shape information that would make Wasserstein useful?
- Sinkhorn-regularized (entropic) OT is much cheaper to compute than exact $W_2$ at scale -- does the regularization distort the signal enough to matter for this comparison?
- Does this connect to Note #010's "gradient flow on statistical manifolds"? Wasserstein gradient flows are a real, established object (Jordan-Kinderlehrer-Otto 1998) distinct from the natural-gradient flow Note #010 proposes -- worth checking whether they're being conflated.

## Preliminary Result (toy Gaussian check, real computation)

Before proposing this as worth testing on real models, checked the two
metrics against each other on paper-simple 1D Gaussians. Result: **when only
the mean changes and variance is held fixed, $W_2$ and the Fisher-Rao
geodesic length are exactly identical** (both reduce to $|\Delta\text{mean}|/\sigma$
-- verified numerically to 6 decimal places across a sweep, not just at one
point). They only diverge once variance changes too.

This means the experiment above needs both mean *and* variance to shift
between layers to have any chance of showing Wasserstein adds information
Fisher-Rao doesn't -- a pure location-shift test (which is the easiest thing
to check first) would show zero difference by construction, not because
either hypothesis is wrong. Updated the experiment design accordingly: any
real-model check must confirm layer-to-layer variance actually changes
before treating a null result as informative.
