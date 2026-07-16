# Research Note #006: Can Tensor-Train Compression Reveal the "Effective Rank" of Reasoning?

## Hypothesis

Transformer weight matrices are dense, but the tensor-train (TT) decomposition
literature (Oseledets 2011; Novikov et al. 2015, "Tensorizing Neural Networks")
shows many can be compressed with a low-rank tensor network at small accuracy
cost. If the compression ratio a given layer tolerates without perplexity loss
varies systematically with task type (e.g. factual recall vs. multi-step
reasoning), the tolerable rank itself becomes a cheap diagnostic for how much
"structure" a task is actually using -- not a metaphor, a measured number.

## Question

Does the TT-rank at which a layer's output perplexity degrades by more than
X% correlate with independently-judged task difficulty?

## Known Mathematics (established, not proposed)

A weight matrix $W \in \mathbb{R}^{m \times n}$ reshaped into a $d$-way tensor
admits a tensor-train decomposition:

$$W_{i_1 \dots i_d} = \sum_{\alpha_1, \dots, \alpha_{d-1}} A^{(1)}_{i_1 \alpha_1} A^{(2)}_{\alpha_1 i_2 \alpha_2} \cdots A^{(d)}_{\alpha_{d-1} i_d}$$

with core tensors $A^{(k)}$ of TT-rank $r_k$. Parameter count drops from
$O(mn)$ to roughly $O(d \cdot r^2 \cdot \max(m,n)/d)$ for uniform rank $r$.
This is a real, published, widely-used compression technique -- the open
question below is specific to using it as a *diagnostic*, which is not
established.

## Experiment

1. Take a small open model (e.g. GPT-2 small) and TT-decompose each attention/FFN
   weight matrix at a sweep of ranks.
2. For each rank, measure perplexity on two datasets: a factual-recall set
   (e.g. TriviaQA) and a multi-step reasoning set (e.g. GSM8K).
3. Find the minimum rank at which each dataset's perplexity crosses a fixed
   degradation threshold (e.g. +5%).
4. Compare the two "critical ranks." If reasoning tasks need systematically
   higher rank to avoid degradation, that's a real, falsifiable signal --
   not assumed here.

## Open Questions

- Is "critical rank" stable across model sizes, or an artifact of GPT-2 small specifically?
- Does critical rank correlate with any existing difficulty metric (e.g. token length, human-rated difficulty) better than perplexity alone already does?
- Is there a cheaper proxy than a full rank sweep (e.g. singular value decay of the original dense matrix)?
