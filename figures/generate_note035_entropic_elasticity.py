#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Note #035: Entropic Elasticity of Attention
# Toy model: attention as an entropic spring
# ═══════════════════════════════════════════════════════════════
#
# Mathematical setup (toy):
# -------------------------
# Let N = 20 tokens.
# Define scores s_i = i (for simplicity).
#
# Attention family parameterized by focus alpha:
#   a_i(alpha) propto exp(alpha * s_i)
#
# As alpha -> 0: uniform (diffuse).
# As alpha -> large: spiky (mass on highest score).
#
# Prior a0: uniform.
#
# Compute for each alpha:
#   - Entropy S(a)
#   - KL divergence D_KL(a || a0)
#   - Free energy F(a) = lambda * D_KL + beta^{-1} * S
#
# Outputs:
# - figures/note035_entropic_elasticity.png
# - data/note035_entropic_elasticity.csv

import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ----------------------------
# Parameters
# ----------------------------
N = 20
scores = np.arange(N, dtype=float)  # s_i = i

# Prior: uniform
a0 = np.ones(N) / N

# Focus parameters
alphas = np.linspace(0, 1.5, 200)

lambda_ = 1.0
beta_inv = 0.5  # temperature-like scale

# ----------------------------
# Compute S, D_KL, F for each alpha
# ----------------------------
def compute_attention(alpha):
    logits = alpha * scores
    exp_logits = np.exp(logits)
    a = exp_logits / exp_logits.sum()
    return a

def entropy(a):
    # Avoid log(0)
    a_safe = a[a > 1e-12]
    return -np.sum(a_safe * np.log(a_safe))

def kl_div(a, a0):
    # a, a0 both length N, a0 > 0
    mask = a > 1e-12
    return np.sum(a[mask] * np.log(a[mask] / a0[mask]))

S_vals = []
DKL_vals = []
F_vals = []

for alpha in alphas:
    a = compute_attention(alpha)
    S = entropy(a)
    DKL = kl_div(a, a0)
    F = lambda_ * DKL + beta_inv * S
    S_vals.append(S)
    DKL_vals.append(DKL)
    F_vals.append(F)

# ----------------------------
# Save CSV (fixed: single-line header)
# ----------------------------
csv_path = "data/note035_entropic_elasticity.csv"
with open(csv_path, "w") as f:
    f.write("alpha,entropy,kl_div,free_energy
")
    for alpha, S, DKL, F in zip(alphas, S_vals, DKL_vals, F_vals):
        f.write(f"{alpha:.6f},{S:.6f},{DKL:.6f},{F:.6f}
")

print(f"CSV saved: {csv_path}")

# ----------------------------
# Plot
# ----------------------------
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(alphas, S_vals, label="Entropy S(a)", color="blue")
ax.plot(alphas, DKL_vals, label="KL divergence D_KL(a || a0)", color="orange")
ax.plot(alphas, F_vals, label="Free energy F(a)", color="green", linewidth=2)

# Highlight Goldilocks band (example: intermediate F)
F_min = np.min(F_vals)
F_max = np.max(F_vals)
band_low = F_min + 0.3 * (F_max - F_min)
band_high = F_min + 0.6 * (F_max - F_min)

ax.axhspan(band_low, band_high, color="gray", alpha=0.2, label="Goldilocks band (toy)")

ax.set_xlabel("Focus parameter α")
ax.set_ylabel("Value")
ax.set_title("Entropic Elasticity of Attention (toy model)
Entropy, KL, and Free Energy vs Focus")
ax.legend(loc="upper right", fontsize=8)

plt.tight_layout()

output_path = "figures/note035_entropic_elasticity.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Figure generated: {output_path}")
