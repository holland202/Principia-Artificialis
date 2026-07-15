# Research Note #003: Can Fisher Information Predict Confidence Better Than Logits?

## Hypothesis

Fisher Information provides a more geometrically grounded measure of model confidence than raw logit entropy.

## Question

Is the trace of the Fisher Information matrix at a given token predictive of calibration quality?

## Known Mathematics

Fisher Information $I(\theta) = \mathbb{E}[-\nabla^2 \log p(x|\theta)]$

## Experiment

- Compute local Fisher Information approximations during generation.
- Correlate with human-rated confidence or calibration benchmarks (e.g., TruthfulQA).

## Open Questions

- Efficient approximation methods for large models?
- Relation to Hessian of the loss?