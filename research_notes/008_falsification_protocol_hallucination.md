# Research Note #008: A Falsification Protocol for Note #002 (Hallucinations as Topological Defects)

## Hypothesis

This note doesn't propose new math -- it proposes the specific control
condition Note #002 is missing, since a persistent-homology signature is only
evidence of something if it doesn't show up just as often in *correct*
outputs. Without that comparison, any nonzero Betti number can be
retroactively called a "defect."

## Question

Does persistent homology of hidden-state trajectories distinguish
hallucinated from correct outputs *better than a trivial baseline*
(e.g. output length, or token-level entropy alone)?

## Known Mathematics

Same as Note #002: Vietoris-Rips filtration of a point cloud sampled from a
hidden-state trajectory, persistence diagrams computed via `ripser` or
`gudhi`, Betti numbers $\beta_0, \beta_1$ as features.

## Experiment (the falsification protocol)

1. Build three labeled sets from the same model on the same prompts:
   (a) known-correct outputs, (b) known-hallucinated outputs (e.g. via a
   fact-checking pipeline or curated benchmark like TruthfulQA), (c) a
   shuffled-control set (real hidden states, but randomly paired with the
   wrong correctness label, to establish the null distribution).
2. Compute $\beta_0$, $\beta_1$, and total persistence for each trajectory.
3. Fit a simple classifier (logistic regression is enough) predicting
   correct/hallucinated from: (i) topological features alone, (ii) output
   length + mean token entropy alone (the trivial baseline), (iii) both
   combined.
4. **The claim in Note #002 is only supported if (i) or (iii) beats (ii) by
   more than noise (permutation test, per this project's established
   practice) on held-out data.** If topological features add nothing over
   the trivial baseline, Note #002's hypothesis is falsified as stated, and
   that is a valid, useful outcome to publish here, not a failure to hide.

## Preliminary Result (synthetic control, not yet real model data)

Ran the protocol's control condition on two synthetic 16-dim trajectories --
one moving in a straight line with small Gaussian noise, one built with a
deliberate large loop -- as a sanity check on the pipeline before spending
compute on real model data. Real `ripser` output, not fabricated:

| Trajectory | H1 loops found | Lifetimes |
|------------|----------------|-----------|
| Straight (noise only) | 2 | 0.001, 0.007 |
| Deliberate large loop | 1 | 1.837 |

**The noise-only trajectory still produced two H1 features.** Their
lifetimes are ~300x shorter than the genuine loop's, but a naive "count of
H1 features > 0" -- which is what a literal reading of Note #002 proposes --
would have scored the noise trajectory as having a topological defect too.

This means Note #002's detector, as originally stated, needs a lifetime
threshold, not a raw count, or it will read noise as hallucination-shaped
structure. That's a concrete, testable refinement this synthetic check
surfaced before wasting a real-model run finding it out. **Open Questions**
below is updated accordingly.

## Open Questions (updated)

- What's the minimum sample size for the permutation test to have reasonable power, given persistence diagrams are expensive to compute?
- Should the trivial baseline also include the model's own token-level confidence (logprob), which is a strong hallucination predictor in existing literature independent of any geometry?
- If topology does add signal, is it redundant with Note #003's Fisher Information trace, or complementary?
- **New:** what lifetime threshold separates "genuine loop" from "noise artifact" on real hidden-state trajectories, where the noise floor is unknown (unlike this synthetic check, where we built the noise ourselves)?
