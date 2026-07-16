# Research Note #007: A Koopman-Operator View of Multi-Step Reasoning

## Hypothesis

Multi-step reasoning (chain-of-thought) is a discrete-time dynamical system:
each step's hidden state is a nonlinear function of the previous one. Koopman
operator theory (Koopman 1931; Brunton et al. 2022, "Modern Koopman Theory")
provides a way to study nonlinear dynamics through a *linear* operator acting
on a space of observables. If reasoning trajectories admit a good finite-dimensional
Koopman approximation, its eigenvalues/eigenfunctions may separate "reasoning modes"
(e.g. convergent vs. divergent chains) in an interpretable, linear way.

## Question

Do dynamic mode decomposition (DMD) eigenvalues computed from a model's
layer-wise (or step-wise, for chain-of-thought) hidden states differ
systematically between reasoning chains that reach a correct answer and
those that don't?

## Known Mathematics (established, not proposed)

For a nonlinear dynamical system $x_{t+1} = F(x_t)$, the Koopman operator
$\mathcal{K}$ acts on observables $g$ via:

$$(\mathcal{K}g)(x_t) = g(F(x_t)) = g(x_{t+1})$$

$\mathcal{K}$ is linear even though $F$ is not, at the cost of being
infinite-dimensional in general. Dynamic Mode Decomposition (Schmid, 2010)
gives a practical finite-dimensional approximation: given a trajectory
$x_0, x_1, \dots, x_T$, form data matrices $X = [x_0, \dots, x_{T-1}]$,
$X' = [x_1, \dots, x_T]$, and solve for the best-fit linear operator
$A \approx X' X^{+}$ ($X^+$ = pseudoinverse). The eigenvalues of $A$
approximate the Koopman spectrum restricted to the observed data.

## Experiment

1. Extract per-step hidden states from a model doing explicit chain-of-thought
   on a reasoning benchmark (e.g. GSM8K), for both correct and incorrect
   completions.
2. Compute DMD on each trajectory (treating each reasoning step as one time
   sample).
3. Compare eigenvalue magnitude/phase distributions between correct and
   incorrect groups (e.g. permutation test, since this project has
   established that as the right tool for exactly this kind of comparison).
4. If eigenvalues near the unit circle (neutral stability) correlate with
   correctness, and eigenvalues well inside/outside (fast convergence/divergence)
   correlate with errors, that is a real, testable finding -- not assumed here.

## Open Questions

- How many reasoning steps are needed for DMD to be numerically stable (it is data-hungry)?
- Is a linear Koopman approximation even reasonable for the highly nonlinear step-to-step map, or does it need a nonlinear observable dictionary (extended DMD)?
- Does this add anything beyond simpler measures already in this repo (e.g. Note #003's Fisher Information trace)?
