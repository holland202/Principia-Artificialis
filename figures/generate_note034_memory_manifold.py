#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Note #034: Memory Manifold
# Toy mathematical model + visualization
# ═══════════════════════════════════════════════════════════════
#
# Mathematical setup (toy):
# -------------------------
# Let D = {d_1, ..., d_N} be personal notes.
# Each note d_i is embedded as x_i in R^2 (toy semantic space).
#
# We define three clusters (A, B, C) representing distinct "views"
# on a topic, with time as an additional label t_i.
#
# Cluster centers:
#   mu_A = (-1.5, -1.0)
#   mu_B = ( 0.0,  0.0)
#   mu_C = ( 1.5,  1.0)
#
# Each cluster is a Gaussian cloud:
#   x_i ~ N(mu_K, sigma_K^2 I) for cluster K in {A,B,C}.
#
# Time labels:
#   t_i in [0,1] for A, [1,2] for B, [2,3] for C.
#
# A "loop" of notes L is a circular trajectory in semantic space:
#   x(theta) = c + R * (cos(theta), sin(theta)), theta in [0, 2pi]
# with center c = (0, -0.5) and radius R = 0.6.
#
# This loop represents repeatedly circling the same question.
# Start and end points are close in semantic space but correspond
# to different belief states (early vs later), illustrating holonomy.
#
# Outputs:
# - figures/note034_memory_manifold.png (visualization)
# - data/note034_memory_manifold.csv (toy note embeddings)

import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ----------------------------
# Parameters
# ----------------------------
np.random.seed(42)

# Cluster centers
mu_A = np.array([-1.5, -1.0])
mu_B = np.array([0.0, 0.0])
mu_C = np.array([1.5, 1.0])

# Sigmas
sigma_A = 0.25
sigma_B = 0.30
sigma_C = 0.25

# Sizes
nA = 40
nB = 50
nC = 45

# Generate clusters
A = np.random.randn(nA, 2) * sigma_A + mu_A
B = np.random.randn(nB, 2) * sigma_B + mu_B
C = np.random.randn(nC, 2) * sigma_C + mu_C

# Time labels (toy)
time_A = np.linspace(0, 1, nA)
time_B = np.linspace(1, 2, nB)
time_C = np.linspace(2, 3, nC)

# Loop: circular trajectory (holonomy loop)
n_loop = 60
theta = np.linspace(0, 2*np.pi, n_loop)
R = 0.6
c_loop = np.array([0.0, -0.5])

loop = np.column_stack([
    c_loop[0] + R*np.cos(theta),
    c_loop[1] + R*np.sin(theta)
])
loop += np.random.randn(n_loop, 2) * 0.05  # small noise
time_loop = np.linspace(0.5, 2.5, n_loop)

# Combine all points
points = np.vstack([A, B, C, loop])
times = np.concatenate([time_A, time_B, time_C, time_loop])
labels = (
    ["A"]*nA +
    ["B"]*nB +
    ["C"]*nC +
    ["Loop"]*n_loop
)
ids = list(range(len(points)))

# ----------------------------
# Save toy data as CSV
# ----------------------------
csv_path = "data/note034_memory_manifold.csv"
with open(csv_path, "w") as f:
    f.write("id,x,y,cluster,time
")
    for i, (x, y, lab, t) in enumerate(zip(points[:,0], points[:,1], labels, times)):
        f.write(f"{i},{x:.6f},{y:.6f},{lab},{t:.3f}
")

print(f"CSV saved: {csv_path}")

# ----------------------------
# Plot
# ----------------------------
fig, ax = plt.subplots(figsize=(6, 6))

# Scatter by cluster
for label, color in [("A", "#1f77b4"), ("B", "#ff7f0e"), ("C", "#2ca02c")]:
    mask = np.array(labels) == label
    ax.scatter(points[mask, 0], points[mask, 1], c=color, label=f"Cluster {label}", s=25, alpha=0.7)

# Loop points
mask_loop = np.array(labels) == "Loop"
ax.scatter(points[mask_loop, 0], points[mask_loop, 1], c="#d62728", label="Holonomy loop", s=20, alpha=0.6)

# Draw loop path
ax.plot(loop[:, 0], loop[:, 1], color="#d62728", linewidth=1.5, alpha=0.5)

# Axes
ax.set_xlabel("Semantic dimension 1")
ax.set_ylabel("Semantic dimension 2")
ax.set_title("Toy Memory Manifold (Note #034)
Clusters + Temporal Drift + Holonomy Loop")
ax.legend(loc="upper left", fontsize=8)
ax.set_aspect("equal", "box")

plt.tight_layout()

output_path = "figures/note034_memory_manifold.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Figure generated: {output_path}")
