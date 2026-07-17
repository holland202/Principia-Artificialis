#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Note #031 Visualization
# Polyphonic Reasoning Manifold: Lenses + Consensus + Conflict Cost
# ═══════════════════════════════════════════════════════════════

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import os

# Ensure output directory exists
os.makedirs("figures", exist_ok=True)

# ----------------------------
# Toy lens distributions (2D Gaussians visualized as ellipses)
# ----------------------------

lenses = [
    {
        "name": "Investor",
        "mu": np.array([-1.0, 0.0]),
        "a": 0.8,  # width
        "b": 0.4,  # height
        "angle": 30,  # degrees
    },
    {
        "name": "Engineer",
        "mu": np.array([1.0, 0.0]),
        "a": 0.6,
        "b": 0.6,
        "angle": -20,
    },
    {
        "name": "User",
        "mu": np.array([0.0, 1.0]),
        "a": 0.7,
        "b": 0.35,
        "angle": 60,
    },
]

# Simple consensus: average of means, average of ellipse params (toy)
mu_consensus = np.mean(np.array([l["mu"] for l in lenses]), axis=0)
a_consensus = np.mean([l["a"] for l in lenses])
b_consensus = np.mean([l["b"] for l in lenses])
angle_consensus = np.mean([l["angle"] for l in lenses])

# Toy conflict cost: sum of squared distances of lens means from consensus
conflict_cost = sum(np.sum((l["mu"] - mu_consensus)**2) for l in lenses)

# ----------------------------
# Plotting
# ----------------------------
fig, ax = plt.subplots(figsize=(6, 6))

colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

def ellipse_patch(mu, a, b, angle, color, alpha=0.25, linewidth=2, label=None):
    return Ellipse(
        xy=mu,
        width=2*a,
        height=2*b,
        angle=angle,
        fill=True,
        alpha=alpha,
        color=color,
        linewidth=linewidth,
        label=label,
    )

# Plot lens ellipses
for i, lens in enumerate(lenses):
    ell = ellipse_patch(
        lens["mu"],
        lens["a"],
        lens["b"],
        lens["angle"],
        color=colors[i],
        alpha=0.25,
        linewidth=2,
        label=f"Lens: {lens['name']}",
    )
    ax.add_patch(ell)
    ax.plot(lens["mu"][0], lens["mu"][1], "o", color=colors[i], markersize=8)

# Plot consensus ellipse
ell_cons = ellipse_patch(
    mu_consensus,
    a_consensus,
    b_consensus,
    angle_consensus,
    color="black",
    alpha=0.15,
    linewidth=2,
    label="Consensus (p*)",
)
ax.add_patch(ell_cons)
ax.plot(mu_consensus[0], mu_consensus[1], "ko", markersize=8)

# Arrows from consensus to each lens
for i, lens in enumerate(lenses):
    dx, dy = lens["mu"] - mu_consensus
    ax.arrow(
        mu_consensus[0],
        mu_consensus[1],
        dx,
        dy,
        head_width=0.08,
        head_length=0.12,
        fc=colors[i],
        ec=colors[i],
        alpha=0.7,
        linewidth=1.5,
    )

# Axes and labels
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-2.0, 2.0)
ax.set_aspect("equal", "box")
ax.axhline(0, color="gray", linewidth=0.5, alpha=0.4)
ax.axvline(0, color="gray", linewidth=0.5, alpha=0.4)

ax.set_xlabel("Reasoning dimension 1")
ax.set_ylabel("Reasoning dimension 2")

title_str = "Polyphonic Reasoning Manifold (toy) - C_conflict = {:.3f}".format(conflict_cost)
ax.set_title(title_str)

ax.legend(loc="upper left", fontsize=8)

plt.tight_layout()

output_path = "figures/note031_polyphonic_manifold.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Figure generated: {output_path}")
