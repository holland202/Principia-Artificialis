#!/usr/bin/env python3
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
