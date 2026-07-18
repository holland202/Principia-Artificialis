import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import os

os.makedirs("figures", exist_ok=True)

# Synthetic Thought Tensor: L x N x d x K
L, N, d, K = 24, 64, 32, 6
np.random.seed(0)
T = np.random.randn(L, N, d, K)

# 1. Norms
norm_LN = np.linalg.norm(T, axis=(2,3))
T_task = [np.linalg.norm(T[:,:,:,k], axis=2) for k in range(K)]

# 2. Stats
ranks, ents = [], []
for l in range(L):
    M = T[l].reshape(N, d*K)
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    s /= (s.sum() + 1e-12)
    ranks.append(np.exp(-np.sum(s * np.log(s + 1e-12))))
    ents.append(-np.sum(s * np.log(s + 1e-12)))

# 3. RG Flow
def coarse_grain_norms(T):
    norms = []
    curr = T
    while curr.shape[0] >= 1:
        flat = curr.reshape(curr.shape[0], -1)
        norms.append(np.linalg.norm(flat, axis=1))
        if curr.shape[0] == 1: break
        curr = (curr[0::2] + curr[1::2]) / 2.0
    return norms
rg_norms = coarse_grain_norms(T)

# 4. Simple Geometry (Centroid distance instead of SVD)
task_flat = T.reshape(L*N*d, K).T
task_emb = np.array([[np.sum(task_flat[i] * task_flat[j]) for j in range(K)] for i in range(K)])
task_emb = task_emb[:, :2] # Simple projection

# Plotting
fig, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=100)
fig.patch.set_facecolor("#0b0f14")
axes[0,0].imshow(norm_LN, cmap=cm.viridis, origin="lower"); axes[0,0].set_title("1. Raw norm")
for k in range(K): axes[0,1].imshow(T_task[k], cmap=cm.viridis, origin="lower", extent=[k, k+1, 0, L])
axes[0,1].set_title("2. Task slices"); axes[0,2].plot(ranks, color="#4fd1c5"); axes[0,2].set_title("3. Rank")
axes[1,0].plot(ents, color="#f6ad55"); axes[1,0].set_title("4. Entropy")
for i, n in enumerate(rg_norms): axes[1,1].plot(np.linspace(0, L, len(n)), n, label=f"scale {i}")
axes[1,1].set_title("5. RG flow")
axes[1,2].scatter(task_emb[:,0], task_emb[:,1], c=range(K), cmap=cm.tab10, s=80); axes[1,2].set_title("6. Geometry")
plt.tight_layout()
plt.savefig("figures/note027_thought_tensor_decomp.png", facecolor="#0b0f14")
print("Success")
