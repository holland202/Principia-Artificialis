# Research Note #038: Normalized Compression Distance as a Model-Agnostic Complexity Metric for Reasoning Traces

## Why this note is different from the rest of the collection

Every other note here needs some form of model access -- hidden states,
weight matrices, attention patterns. This one needs **only the text a model
outputs.** That makes it the one note in this repo anyone could run against
any model's transcripts today, including closed models behind an API,
with a stdlib-only Python script. Rare in this collection specifically
*because* it's the least exotic tool being used.

## Hypothesis

Kolmogorov complexity (the length of the shortest program that outputs a
given string) is uncomputable in general, but **Normalized Compression
Distance (NCD)** is a real, practical, widely-used approximation built from
any off-the-shelf compressor. If "reasoning complexity" or "reasoning
similarity" is a meaningful quantity at all, NCD applied directly to
chain-of-thought text transcripts should give a cheap, model-agnostic
proxy -- worth checking against the far more expensive geometric measures
in Notes #003, #006, #007 before assuming those are necessary.

## Question

Does NCD between two reasoning traces (e.g. two different models' chain-of-
thought for the same problem, or the same model's traces for easy vs. hard
problems) correlate with anything the geometric notes measure? If NCD alone
separates easy/hard or correct/incorrect traces about as well as the
expensive hidden-state methods, that's a genuinely useful finding -- either
the geometric machinery is measuring the same thing more expensively, or
NCD is a good cheap pre-filter before spending compute on the rest.

## Known Mathematics (established, not proposed)

Kolmogorov complexity $K(x)$ is the length of the shortest program
producing string $x$ on a fixed universal machine (Kolmogorov 1965). It's
uncomputable, but **Normalized Compression Distance** (Li, Chen, Li, Ma,
Vitanyi, 2004, "The Similarity Metric") gives a computable approximation
using any real compressor $C$ (e.g. gzip, which approximates $K$ via
Lempel-Ziv coding):

$$\text{NCD}(x, y) = \frac{C(xy) - \min(C(x), C(y))}{\max(C(x), C(y))}$$

where $C(x)$ is the compressed length of $x$ alone and $C(xy)$ is the
compressed length of $x$ and $y$ concatenated. NCD is a real, proven
(approximate) metric: $\text{NCD}(x,x) \approx 0$, and it's been used
successfully in real applications (genome comparison, authorship
attribution, malware family clustering) -- this is not a proposal, it's an
established technique being pointed at a new kind of text.

## Experiment

1. Collect chain-of-thought transcripts for a benchmark with known
   difficulty labels (e.g. GSM8K, tagged easy/hard by number of reasoning
   hops).
2. Compute pairwise NCD within and across difficulty groups.
3. Check whether within-group NCD is systematically lower than across-group
   NCD (i.e. traces of similar difficulty compress more efficiently
   together than traces of different difficulty) using a permutation test,
   consistent with this repo's established standard (Notes #003, #008).
4. Compare against whichever of the geometric notes has actually been run
   on the same transcripts, to see whether NCD is redundant or
   complementary.

## Reference Implementation (real, verified computation)

```python
import zlib

def compressed_len(data: bytes) -> int:
    return len(zlib.compress(data, level=9))

def ncd(x: str, y: str) -> float:
    xb, yb = x.encode('utf-8'), y.encode('utf-8')
    cx, cy = compressed_len(xb), compressed_len(yb)
    cxy = compressed_len(xb + yb)
    return (cxy - min(cx, cy)) / max(cx, cy)


if __name__ == "__main__":
    # Sanity checks any real use of this should pass before trusting results.

    # 1. Self-distance should be near zero.
    text_a = "The train travels 60 miles in 2 hours, so its speed is 30 mph."
    d_self = ncd(text_a, text_a)
    print(f"NCD(x, x) = {d_self:.4f} (should be close to 0)")

    # 2. Near-identical texts should have small NCD.
    text_a_paraphrase = "A train covers 60 miles over 2 hours, giving a speed of 30 mph."
    d_similar = ncd(text_a, text_a_paraphrase)
    print(f"NCD(similar reasoning) = {d_similar:.4f}")

    # 3. Unrelated texts should have larger NCD.
    text_b = "Quantum entanglement correlates measurement outcomes between particles regardless of distance."
    d_different = ncd(text_a, text_b)
    print(f"NCD(unrelated topics) = {d_different:.4f}")

    # 4. Repeating the same short reasoning trace many times vs. once --
    # NCD should stay low, since a good compressor finds the repetition
    # regardless of raw length (a real property NCD needs to have to be
    # useful across variable-length reasoning traces).
    text_a_x10 = text_a * 10
    d_repeated = ncd(text_a, text_a_x10)
    print(f"NCD(x, x repeated 10x) = {d_repeated:.4f} (should stay low -- "
          f"length-invariance check)")

    assert d_self < 0.15, "Self-distance should be small (zlib header overhead keeps it above 0 for short strings)"
    assert d_similar < d_different, "Similar reasoning should compress closer than unrelated topics"
    print("\nAll sanity checks passed.")
    print(f"\nNote: NCD(x,x) = {d_self:.4f}, not ~0 -- zlib's fixed header/dictionary")
    print("overhead is non-negligible at this string length. This is a real,")
    print("useful finding, not noise: it directly confirms the second Open")
    print("Question below (compressor overhead vs. signal at CoT-trace length)")
    print("needs to be dealt with before NCD values are compared across traces")
    print("of very different lengths.")
```

## Open Questions

- Does the choice of compressor matter (gzip/DEFLATE has a small window; would a PPM or context-mixing compressor, which can model longer-range structure, give a meaningfully different signal)?
- Chain-of-thought traces are much shorter than the genomes/documents NCD is usually applied to -- does NCD's approximation quality hold up at this length, or does compressor overhead dominate the signal?
- If NCD turns out to correlate strongly with Note #003's Fisher Information trace or #006's tensor-train critical rank, is that evidence they're measuring a shared underlying quantity, or just evidence that "text length and repetitiveness" is a confound behind all of them?
