# Research Note #015: Category-Theoretic Compositionality of Reasoning Steps

*This note was listed in the README table across several sessions without
ever being written -- filling that gap here rather than leaving the broken
reference in place again.*

## Hypothesis

If individual reasoning steps are morphisms in some category (objects =
"states of understanding," morphisms = "inference steps that transform one
state into another"), then multi-step reasoning is composition of
morphisms, and properties that should compose well (e.g. "step A is valid"
and "step B is valid" implying "A then B is valid") give a concrete,
checkable structure -- if and when a real functor can be defined connecting
model computations to this category.

## Question

Can a functor be defined from "sequences of reasoning steps in a real
model" to "morphisms in a category of belief states" that actually
preserves composition (i.e. is a real functor, not just a suggestive
analogy)? If not, what's the precise obstruction?

## Known Mathematics (established, not proposed)

A category $\mathcal{C}$ consists of objects and morphisms $f: A \to B$
between them, with associative composition $g \circ f: A \to C$ for
$f: A \to B$, $g: B \to C$, and an identity morphism $\text{id}_A: A \to A$
for each object (Mac Lane, *Categories for the Working Mathematician*,
1971). A functor $F: \mathcal{C} \to \mathcal{D}$ maps objects to objects
and morphisms to morphisms, preserving composition and identities:
$F(g \circ f) = F(g) \circ F(f)$.

This is the actual, nontrivial content of "category-theoretic" claims about
reasoning: it's not enough to say reasoning steps "compose" informally --
category theory only adds anything if a genuine functor can be exhibited
and its functor laws checked, not asserted.

## Why this is the hardest note in this collection to make concrete

Every other note in this repo (e.g. #003's Fisher Information, #006's
tensor-train rank) has a natural real-valued or matrix-valued quantity you
can compute from a real model today. Category theory doesn't -- "is this
map a functor" is a yes/no structural question, not a number. The honest
starting point is smaller than "compositionality of reasoning": pick one
concrete candidate category first.

## Concrete Candidate to Test First

- **Objects:** probability distributions over a fixed answer set (e.g. for
  a specific multi-hop QA benchmark where the answer space is enumerable).
- **Morphisms:** stochastic maps (Markov kernels) induced by one reasoning
  step, i.e. $P(\text{state}_{t+1} \mid \text{state}_t)$.
- This category (objects = distributions, morphisms = Markov kernels) is
  already well-studied as the **Kleisli category of the distribution
  monad** (Giry, 1982) -- meaning the "is this a real category" question is
  already answered by existing math, and the actual open question becomes:
  does a real model's step-to-step transition actually behave like a Markov
  kernel in this category (memoryless, given the current state), or does it
  depend on more history than the category can represent?

## Open Questions

- Is the memoryless (Markov) assumption even approximately true for real chain-of-thought, or does state leak in a way that breaks the categorical structure before compositionality is even the interesting question?
- If the Markov assumption fails, is there a richer category (e.g. adding a "history" object) that still gives a checkable functor, or does the framework just not apply?
- Does this connect to Note #007's Koopman-operator view? Both are about structure in state-to-state transitions -- worth checking whether one subsumes the other before treating them as separate notes.
