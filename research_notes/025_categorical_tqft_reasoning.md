# Research Note #025: Topological Quantum Field Theory as a (Highly Speculative) Model for Reasoning Composition

## Epistemic Status (read first)

This is the most speculative note in the collection so far. The underlying
math -- topological quantum field theory (TQFT), the Atiyah-Segal axioms --
is real, established mathematical physics, decades old and rigorously
studied. **The connection to reasoning, "emergent geometry," or anything
resembling gravity is not established in any sense.** There is currently no
known mechanism, experiment, or even a precise conjecture linking TQFT to
how language models compose reasoning steps. Treat everything past the
"Known Mathematics" section as a structural analogy someone might find
generative, not a hypothesis with a clear test attached yet -- weaker
epistemic footing than any other note in this repo, including #005 and
#020, which at least have a concrete proposed experiment.

## Hypothesis (stated precisely, so it can be precisely rejected)

Note #015 asked whether reasoning steps form a category. This note asks a
narrower, more structured version: if reasoning steps are "cobordisms"
between "states of understanding" (objects), does the composition rule
follow the same algebraic pattern that 2D TQFTs are *proven* to follow --
namely, that of a commutative Frobenius algebra? If reasoning genuinely has
this structure, splitting a reasoning thread into sub-questions and
recombining the answers should satisfy specific algebraic identities
(below), which are checkable in principle on real hidden-state data.

## Known Mathematics (established, not proposed)

**Atiyah-Segal axioms** (Atiyah 1988): an $n$-dimensional TQFT is a
symmetric monoidal functor $Z$ from the category of $n$-dimensional
cobordisms (objects = $(n-1)$-manifolds, morphisms = $n$-manifolds
connecting them) to the category of vector spaces, sending disjoint union
to tensor product.

**The real theorem this note leans on:** 2D TQFTs are in exact
correspondence with commutative Frobenius algebras (Dijkgraaf 1989; Kock,
*Frobenius Algebras and 2D Topological Quantum Field Theories*, 2004). A
commutative Frobenius algebra is a commutative algebra $A$ with
multiplication $m: A \otimes A \to A$, unit $\eta: \mathbb{C} \to A$,
comultiplication $\Delta: A \to A \otimes A$, and counit $\epsilon: A \to
\mathbb{C}$, satisfying the Frobenius identity:

$$(m \otimes \text{id}) \circ (\text{id} \otimes \Delta) = \Delta \circ m = (\text{id} \otimes m) \circ (\Delta \otimes \text{id})$$

Diagrammatically: splitting then merging a strand equals merging then
splitting, equals a single pass-through with a "handle." This identity is
exactly the algebraic content of the "pair of pants" cobordism (one circle
splitting into two, or two merging into one) being associative and
coherent with its dual.

## Speculative Bridge (clearly labeled as such)

*If* "understanding state" objects and "reasoning step" morphisms formed a
symmetric monoidal category with duals, splitting a reasoning thread into
parallel sub-questions and recombining the answers would need to satisfy
the same Frobenius identity above for the composition to be coherent
(order-independent in the relevant sense). This is a strong, specific,
checkable-in-principle structural claim -- not a claim about gravity,
spacetime, or physics beyond providing the categorical vocabulary.

## Experiment (what would actually need to happen)

1. Define a concrete toy "split and merge": e.g. a multi-hop QA task where
   the model can be prompted to split into two sub-questions and later
   combine the answers.
2. Extract hidden-state representations at the split point and both
   recombination orders (if there are multiple valid decompositions of the
   same question).
3. Check whether the two recombination paths converge to representations
   related the way the Frobenius identity requires, or diverge.
4. This has not been run. Section below verifies only that the *toy
   algebra itself* satisfies the identity -- confirming the reference
   structure is implemented correctly, not that reasoning follows it.

## Reference Implementation (real, verified computation)

```python
import numpy as np

# A concrete 2D commutative Frobenius algebra: functions on a finite set
# of 2 points (the standard toy example -- Kock 2004, Example 2.3.14).
# Verifies the Frobenius identity numerically rather than asserting it.

dim = 2
m = np.zeros((dim, dim, dim))
for i in range(dim):
    m[i, i, i] = 1.0

a = np.array([1.0, 1.0])
delta = np.zeros((dim, dim, dim))
for i in range(dim):
    delta[i, i, i] = 1.0 / a[i]


def apply_m(x, y):
    return np.einsum('ijk,i,j->k', m, x, y)


def apply_delta(x):
    return np.einsum('ijk,i->jk', delta, x)


def explicit_check():
    basis = np.eye(dim)
    ok = True
    for i in range(dim):
        for j in range(dim):
            x, y = basis[i], basis[j]
            dy = apply_delta(y)
            lhs = np.zeros((dim, dim))
            for p in range(dim):
                for q in range(dim):
                    lhs[:, q] += dy[p, q] * apply_m(x, basis[p])
            xy = apply_m(x, y)
            rhs = apply_delta(xy)
            if not np.allclose(lhs, rhs, atol=1e-8):
                ok = False
                print(f"MISMATCH at basis ({i},{j}): lhs=\n{lhs}\nrhs=\n{rhs}")
    return ok


if __name__ == "__main__":
    result = explicit_check()
    print(f"Frobenius identity holds on all basis pairs: {result}")
```

## Open Questions

- Is "symmetric monoidal category with duals" even a reasonable structural claim for reasoning, or does it smuggle in an assumption (e.g. that splitting and recombining is always well-defined) that's false for real multi-hop reasoning?
- If real hidden states don't satisfy the Frobenius identity, is that because the analogy is wrong, or because the *specific* toy algebra chosen doesn't match the model's actual algebra (there are many inequivalent Frobenius algebras)?
- Is there a weaker, more defensible claim buried in here (e.g. "some" cobordism-like structure exists without insisting on the full 2D TQFT classification) that would survive contact with real data even if the strong version doesn't?
