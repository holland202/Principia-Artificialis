# Note #041 — Persistent Homology of Reasoning Chains: The Number of Topological Features in Attention Matrices Scales with Task Complexity

**Status:** Draft
**Theme:** Topology / AI
**Author:** ChatGPT (OpenAI)
**Builds on:** #002 Hallucinations as Topological Defects, #008 A Falsification Protocol for Note #002, #037 Random Matrix Theory Level‑Spacing Statistics on Attention Spectra

## The claim
In a transformer model during forward pass, the attention matrices at each layer (when thresholded as weighted adjacency graphs) have a 0‑dimensional persistent homology whose *number of significant features* (connected components that persist for more than 10% of the filtration length) is:
- **higher** for multi‑step reasoning tasks than for single‑step retrieval tasks, and
- **scales** with the logarithm of the minimal number of reasoning steps required to answer the input.

If this claim is false, then either (a) no statistically significant difference exists between reasoning and retrieval tasks for the same model, after controlling for token count, or (b) the scaling with reasoning steps is not monotonic.

## Epistemic status
The mathematics of persistent homology (Edelsbrunner & Harer, 2010) is well‑established. The interpretation of attention matrices as weighted graphs whose connectivity reveals latent structure is a plausible but unconfirmed hypothesis. The specific scaling law (logarithm of reasoning steps) is speculative and is the core of this note. The reference code below computes 0‑dimensional persistence (connected components) using only `numpy`, so the measurement pipeline is verified. The claim will be tested on publicly available transformer models (e.g., GPT‑2, Llama small) once the experiment is registered with a specific model and dataset.

## Known mathematics / prior art
- **Persistent homology**: Edelsbrunner, Letscher, Zomorodian (2002); standard tool for quantifying multiscale topological features.
- **Attention as graph**: Vig (2019) visualized attention as graphs; the idea that attention patterns encode reasoning structure is folklore.
- **Topological analysis of activations**: Note #002 (hallucinations as topological defects) and #008 (falsification protocol) lay groundwork.
- **Random matrix theory of attention**: Note #037 uses level‑spacing statistics; here we extend to persistent homology.

## The experiment (or: what would one look like)
We will use a small transformer model (e.g., GPT‑2 small, 12 layers) and two datasets:
- **Reasoning set**: 500 arithmetic word problems requiring 2–5 steps (e.g., from GSM8K).
- **Retrieval set**: 500 factual trivia questions (single‑hop, e.g., from TriviaQA).

For each input, we record the attention matrices at every layer and token position, then compute the 0‑dimensional persistent homology of the thresholded attention graph.

### Registered predictions
**P1:** The mean number of persistent connected components (filtration length > 0.1) averaged over all layers and tokens will be strictly greater for the reasoning set than for the retrieval set (one‑tailed t‑test, p < 0.05).
**P2:** Within the reasoning set, the number of persistent components will be positively correlated with the number of steps required (Pearson r > 0.3).
**P3 (anti‑vacuity control):** When attention matrices are randomly shuffled (preserving marginal distributions), no difference between reasoning and retrieval sets will be found.

## Reference code

```python
import numpy as np

def persistent_components_0d(W, thresholds=100):
    n = W.shape[0]
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)
    t_min, t_max = W.min(), W.max()
    eps = 1e-9
    t_vals = np.linspace(t_min - eps, t_max + eps, thresholds)
    parent = np.arange(n)
    rank = np.zeros(n, dtype=int)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    i_upper, j_upper = np.triu_indices(n, k=1)
    edges = np.column_stack((i_upper, j_upper, W[i_upper, j_upper]))
    edges = edges[edges[:, 2].argsort()]
    current_components = n
    idx = 0
    n_components = np.zeros(thresholds)
    for i, t in enumerate(t_vals):
        while idx < len(edges) and edges[idx, 2] <= t:
            w, u, v = edges[idx, 2], int(edges[idx, 0]), int(edges[idx, 1])
            if union(u, v):
                current_components -= 1
            idx += 1
        n_components[i] = current_components
    return n_components

def demo_synthetic_reasoning():
    np.random.seed(42)
    n_tokens = 20
    W_chain = np.zeros((n_tokens, n_tokens))
    for i in range(1, n_tokens):
        W_chain[i, i-1] = 0.9
    W_chain = (W_chain + W_chain.T) / 2
    W_star = np.zeros((n_tokens, n_tokens))
    center = 0
    for i in range(1, n_tokens):
        W_star[center, i] = 0.9
        W_star[i, center] = 0.9
    W_random = np.random.rand(n_tokens, n_tokens) * 0.3
    W_random = (W_random + W_random.T) / 2
    print("=== Persistent components (number of components across thresholds) ===")
    for name, W in [("Chain (reasoning)", W_chain), ("Star (retrieval)", W_star), ("Random", W_random)]:
        comps = persistent_components_0d(W, thresholds=50)
        disconnected = np.sum(comps > 1)
        print(f"{name}: thresholds with >1 component = {disconnected} out of 50")
        print(f"  Mean components: {comps.mean():.2f}")
    print("\nPrediction: chain should show highest mean components, star lowest.")

if __name__ == "__main__":
    demo_synthetic_reasoning()
cat > research_notes/note041_persistent_homology.md << 'ENDOFFILE'
# Note #041 — Persistent Homology of Reasoning Chains: The Number of Topological Features in Attention Matrices Scales with Task Complexity

**Status:** Draft
**Theme:** Topology / AI
**Author:** ChatGPT (OpenAI)
**Builds on:** #002 Hallucinations as Topological Defects, #008 A Falsification Protocol for Note #002, #037 Random Matrix Theory Level‑Spacing Statistics on Attention Spectra

## The claim
In a transformer model during forward pass, the attention matrices at each layer (when thresholded as weighted adjacency graphs) have a 0‑dimensional persistent homology whose *number of significant features* (connected components that persist for more than 10% of the filtration length) is:
- **higher** for multi‑step reasoning tasks than for single‑step retrieval tasks, and
- **scales** with the logarithm of the minimal number of reasoning steps required to answer the input.

If this claim is false, then either (a) no statistically significant difference exists between reasoning and retrieval tasks for the same model, after controlling for token count, or (b) the scaling with reasoning steps is not monotonic.

## Epistemic status
The mathematics of persistent homology (Edelsbrunner & Harer, 2010) is well‑established. The interpretation of attention matrices as weighted graphs whose connectivity reveals latent structure is a plausible but unconfirmed hypothesis. The specific scaling law (logarithm of reasoning steps) is speculative and is the core of this note. The reference code below computes 0‑dimensional persistence (connected components) using only `numpy`, so the measurement pipeline is verified. The claim will be tested on publicly available transformer models (e.g., GPT‑2, Llama small) once the experiment is registered with a specific model and dataset.

## Known mathematics / prior art
- **Persistent homology**: Edelsbrunner, Letscher, Zomorodian (2002); standard tool for quantifying multiscale topological features.
- **Attention as graph**: Vig (2019) visualized attention as graphs; the idea that attention patterns encode reasoning structure is folklore.
- **Topological analysis of activations**: Note #002 (hallucinations as topological defects) and #008 (falsification protocol) lay groundwork.
- **Random matrix theory of attention**: Note #037 uses level‑spacing statistics; here we extend to persistent homology.

## The experiment (or: what would one look like)
We will use a small transformer model (e.g., GPT‑2 small, 12 layers) and two datasets:
- **Reasoning set**: 500 arithmetic word problems requiring 2–5 steps (e.g., from GSM8K).
- **Retrieval set**: 500 factual trivia questions (single‑hop, e.g., from TriviaQA).

For each input, we record the attention matrices at every layer and token position, then compute the 0‑dimensional persistent homology of the thresholded attention graph.

### Registered predictions
**P1:** The mean number of persistent connected components (filtration length > 0.1) averaged over all layers and tokens will be strictly greater for the reasoning set than for the retrieval set (one‑tailed t‑test, p < 0.05).
**P2:** Within the reasoning set, the number of persistent components will be positively correlated with the number of steps required (Pearson r > 0.3).
**P3 (anti‑vacuity control):** When attention matrices are randomly shuffled (preserving marginal distributions), no difference between reasoning and retrieval sets will be found.

## Reference code

```python
import numpy as np

def persistent_components_0d(W, thresholds=100):
    n = W.shape[0]
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)
    t_min, t_max = W.min(), W.max()
    eps = 1e-9
    t_vals = np.linspace(t_min - eps, t_max + eps, thresholds)
    parent = np.arange(n)
    rank = np.zeros(n, dtype=int)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    i_upper, j_upper = np.triu_indices(n, k=1)
    edges = np.column_stack((i_upper, j_upper, W[i_upper, j_upper]))
    edges = edges[edges[:, 2].argsort()]
    current_components = n
    idx = 0
    n_components = np.zeros(thresholds)
    for i, t in enumerate(t_vals):
        while idx < len(edges) and edges[idx, 2] <= t:
            w, u, v = edges[idx, 2], int(edges[idx, 0]), int(edges[idx, 1])
            if union(u, v):
                current_components -= 1
            idx += 1
        n_components[i] = current_components
    return n_components

def demo_synthetic_reasoning():
    np.random.seed(42)
    n_tokens = 20
    W_chain = np.zeros((n_tokens, n_tokens))
    for i in range(1, n_tokens):
        W_chain[i, i-1] = 0.9
    W_chain = (W_chain + W_chain.T) / 2
    W_star = np.zeros((n_tokens, n_tokens))
    center = 0
    for i in range(1, n_tokens):
        W_star[center, i] = 0.9
        W_star[i, center] = 0.9
    W_random = np.random.rand(n_tokens, n_tokens) * 0.3
    W_random = (W_random + W_random.T) / 2
    print("=== Persistent components (number of components across thresholds) ===")
    for name, W in [("Chain (reasoning)", W_chain), ("Star (retrieval)", W_star), ("Random", W_random)]:
        comps = persistent_components_0d(W, thresholds=50)
        disconnected = np.sum(comps > 1)
        print(f"{name}: thresholds with >1 component = {disconnected} out of 50")
        print(f"  Mean components: {comps.mean():.2f}")
    print("\nPrediction: chain should show highest mean components, star lowest.")

if __name__ == "__main__":
    demo_synthetic_reasoning()
## Falsifiable next predictions
**P4:** On a BERT‑like model (e.g., BERT‑base) answering multi‑hop questions from HotpotQA, the average number of persistent components (for the final layer) will be at least 1.5 times that for single‑hop SQuAD questions, after controlling for input length (p < 0.01).
**P5:** The correlation with reasoning steps (**P2**) will hold across different model scales (GPT‑2 small, medium, large) with consistent slope.

The door is open: any contributor with access to a transformer and a reasoning dataset can run the reference code above to accept or refute **P1** and **P2**. If refuted, this note becomes a valuable record of a failed claim. If confirmed, it provides a cheap, structural signature of reasoning depth.
