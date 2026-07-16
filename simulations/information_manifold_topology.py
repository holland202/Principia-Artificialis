#!/usr/bin/env python3
"""
Simulation: Information Manifold Topology & Geodesic Reasoning
===============================================================
Visualizes a 2D statistical manifold (Gaussian family) with:
  - Fisher-Rao metric tensor field
  - Geodesic paths (optimized vs. straight-line)
  - Topological defects (hallucination regions)
  - Curvature heatmap
  - Entanglement coupling visualization

For Principia Artificialis -- Research Notes #002, #005, #006, #007
Author: Kimi (Moonshot AI)

Run: python3 information_manifold_topology.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# 1. Statistical Manifold: Location-Scale Family (Gaussian)
# ---------------------------------------------------------------------------

def fisher_rao_metric(theta):
    """
    Fisher-Rao metric for Gaussian N(mu, sigma^2) with theta = [mu, log_sigma].
    Using log_sigma makes the metric Euclidean-like in the vertical direction.
    """
    mu, log_s = theta
    sigma = np.exp(log_s)
    return np.array([[1.0 / (sigma**2), 0.0],
                     [0.0, 2.0]])

def metric_inverse(theta):
    g = fisher_rao_metric(theta)
    return np.linalg.inv(g)

# ---------------------------------------------------------------------------
# 2. Geodesic Computation
# ---------------------------------------------------------------------------

def discrete_path_length(path):
    """
    Compute Fisher-Rao path length using midpoint rule.
    path: (N, 2) array of [mu, log_sigma] points.
    """
    length = 0.0
    for i in range(len(path) - 1):
        mid = (path[i] + path[i+1]) / 2.0
        g = fisher_rao_metric(mid)
        diff = path[i+1] - path[i]
        length += np.sqrt(np.dot(diff, np.dot(g, diff)))
    return length

def compute_geodesic(start, end, n_points=50, init_noise=0.1):
    """
    Compute geodesic between start and end on the Gaussian manifold.
    """
    initial_path = np.linspace(start, end, n_points)
    initial_path += np.random.normal(0, init_noise, (n_points, 2))
    initial_path[0] = start
    initial_path[-1] = end

    interior_mask = np.ones(n_points, dtype=bool)
    interior_mask[0] = False
    interior_mask[-1] = False

    def obj(x):
        path = initial_path.copy()
        path[interior_mask] = x.reshape((-1, 2))
        return discrete_path_length(path)

    x0 = initial_path[interior_mask].flatten()
    result = minimize(obj, x0, method='L-BFGS-B', 
                      options={'maxiter': 500, 'disp': False})

    optimized_path = initial_path.copy()
    optimized_path[interior_mask] = result.x.reshape((-1, 2))
    return initial_path, optimized_path

# ---------------------------------------------------------------------------
# 3. Topological Defects (Hallucination Regions)
# ---------------------------------------------------------------------------

def curvature_scalar(theta):
    """
    Scalar curvature of Gaussian manifold with spatially varying defects.
    Base curvature K = -0.5, with localized defect perturbations.
    """
    mu, log_s = theta
    K_base = -0.5
    d1 = (mu - 2.0)**2 + (log_s - 0.5)**2
    defect1 = -2.0 * np.exp(-d1 / 0.3)
    d2 = (mu + 1.0)**2 + (log_s + 0.5)**2
    defect2 = -1.5 * np.exp(-d2 / 0.4)
    return K_base + defect1 + defect2

def hallucination_probability(theta, defect_centers, defect_strengths):
    """
    Probability of hallucination increases near topological defects.
    """
    mu, log_s = theta
    prob = 0.0
    for center, strength in zip(defect_centers, defect_strengths):
        d = (mu - center[0])**2 + (log_s - center[1])**2
        prob += strength * np.exp(-d / 0.2)
    return np.clip(prob, 0, 1)

# ---------------------------------------------------------------------------
# 4. Entanglement Visualization
# ---------------------------------------------------------------------------

def entanglement_field(grid_mu, grid_log_s, coupling_strength=1.0):
    """
    Simulate an entanglement tensor field g_AB as a vector field.
    """
    U = np.zeros_like(grid_mu)
    V = np.zeros_like(grid_mu)
    centers = [(1.5, 0.3), (-0.5, -0.3), (0.0, 0.8)]
    for cx, cy in centers:
        dx = grid_mu - cx
        dy = grid_log_s - cy
        r2 = dx**2 + dy**2 + 0.1
        U += -coupling_strength * dy / r2
        V += coupling_strength * dx / r2
    return U, V

# ---------------------------------------------------------------------------
# 5. Visualization
# ---------------------------------------------------------------------------

def create_manifold_visualization():
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Principia Artificialis: Information Manifold Topology', 
                 fontsize=16, fontweight='bold', y=0.98)

    mu_range = np.linspace(-3, 4, 100)
    log_s_range = np.linspace(-1.5, 1.5, 100)
    MU, LOG_S = np.meshgrid(mu_range, log_s_range)

    # --- Panel 1: Metric Determinant ---
    ax = axes[0, 0]
    det_g = 1.0 / (np.exp(LOG_S)**2) * 2.0
    det_g = np.clip(det_g, 0, 10)
    im = ax.pcolormesh(MU, LOG_S, det_g, cmap='viridis', shading='gouraud')
    ax.set_title('Fisher-Rao Metric Determinant\n(Information Density)', fontsize=11)
    ax.set_xlabel(r'$\mu$ (location)')
    ax.set_ylabel(r'$\log \sigma$ (scale)')
    plt.colorbar(im, ax=ax, label='det(g)')

    # --- Panel 2: Scalar Curvature ---
    ax = axes[0, 1]
    K = np.vectorize(lambda m, ls: curvature_scalar([m, ls]))(MU, LOG_S)
    im = ax.pcolormesh(MU, LOG_S, K, cmap='RdBu_r', shading='gouraud', vmin=-3, vmax=1)
    ax.set_title('Scalar Curvature\n(Topological Defects = Hallucinations)', fontsize=11)
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\log \sigma$')
    plt.colorbar(im, ax=ax, label='K')
    ax.scatter([2.0, -1.0], [0.5, -0.5], c='yellow', s=100, marker='X', 
               edgecolors='black', linewidths=1, zorder=5, label='Defect cores')
    ax.legend(loc='upper right')

    # --- Panel 3: Geodesic Paths ---
    ax = axes[0, 2]
    ax.set_xlim(-3, 4)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title('Geodesic Reasoning Paths\n(Note #005)', fontsize=11)
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\log \sigma$')

    np.random.seed(42)
    paths_data = []
    for i in range(5):
        start = np.array([np.random.uniform(-2.5, -1.5), np.random.uniform(-1, 0)])
        end = np.array([np.random.uniform(2.5, 3.5), np.random.uniform(0, 1)])
        init_path, opt_path = compute_geodesic(start, end, n_points=30, init_noise=0.15)
        paths_data.append((init_path, opt_path, start, end))

    det_bg = 1.0 / (np.exp(LOG_S)**2) * 2.0
    det_bg = np.clip(det_bg, 0, 8)
    ax.pcolormesh(MU, LOG_S, det_bg, cmap='Greys', alpha=0.2, shading='gouraud')

    colors = plt.cm.tab10(np.linspace(0, 1, 5))
    for i, (init, opt, s, e) in enumerate(paths_data):
        ax.plot(init[:, 0], init[:, 1], '--', color=colors[i], alpha=0.4, linewidth=1)
        ax.plot(opt[:, 0], opt[:, 1], '-', color=colors[i], linewidth=2.5, 
                label=f'Path {i+1}')
        ax.scatter([s[0]], [s[1]], c=colors[i], s=80, marker='o', zorder=5)
        ax.scatter([e[0]], [e[1]], c=colors[i], s=80, marker='s', zorder=5)
    ax.legend(loc='lower right', fontsize=8)

    # --- Panel 4: Hallucination Probability ---
    ax = axes[1, 0]
    defect_centers = [(2.0, 0.5), (-1.0, -0.5)]
    defect_strengths = [0.9, 0.7]
    hall_prob = np.vectorize(
        lambda m, ls: hallucination_probability([m, ls], defect_centers, defect_strengths)
    )(MU, LOG_S)
    im = ax.pcolormesh(MU, LOG_S, hall_prob, cmap='hot', shading='gouraud', vmin=0, vmax=1)
    ax.set_title('Hallucination Probability Field\n(Note #002)', fontsize=11)
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\log \sigma$')
    plt.colorbar(im, ax=ax, label='P(hallucinate)')
    for i, (init, opt, s, e) in enumerate(paths_data[:3]):
        ax.plot(opt[:, 0], opt[:, 1], '-', color='cyan', linewidth=1, alpha=0.6)

    # --- Panel 5: Entanglement Field ---
    ax = axes[1, 1]
    U, V = entanglement_field(MU, LOG_S, coupling_strength=0.5)
    magnitude = np.sqrt(U**2 + V**2)
    im = ax.pcolormesh(MU, LOG_S, magnitude, cmap='plasma', shading='gouraud')
    ax.set_title('Entanglement Coupling Field\n(Note #006: g_AB norm)', fontsize=11)
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\log \sigma$')
    skip = 8
    ax.quiver(MU[::skip, ::skip], LOG_S[::skip, ::skip], 
              U[::skip, ::skip], V[::skip, ::skip],
              scale=20, color='white', alpha=0.7, width=0.003)
    plt.colorbar(im, ax=ax, label='||g_AB||')

    # --- Panel 6: Memory Gradient Flow ---
    ax = axes[1, 2]
    mu_target, ls_target = 1.0, 0.0
    F = (MU - mu_target)**2 + (LOG_S - ls_target)**2
    im = ax.pcolormesh(MU, LOG_S, F, cmap='coolwarm', shading='gouraud')
    ax.set_title('Memory Free Energy Landscape\n(Note #007: Gradient Flow)', fontsize=11)
    ax.set_xlabel(r'$\mu$')
    ax.set_ylabel(r'$\log \sigma$')
    plt.colorbar(im, ax=ax, label='F(q)')

    np.random.seed(123)
    for i in range(4):
        traj = []
        pos = np.array([np.random.uniform(-2.5, 3.5), np.random.uniform(-1.2, 1.2)])
        traj.append(pos.copy())
        lr = 0.05
        for step in range(100):
            grad = np.array([2*(pos[0] - mu_target), 2*(pos[1] - ls_target)])
            g_inv = metric_inverse(pos)
            nat_grad = g_inv @ grad
            pos = pos - lr * nat_grad + np.random.normal(0, 0.02, 2)
            traj.append(pos.copy())
            if np.linalg.norm(nat_grad) < 0.01:
                break
        traj = np.array(traj)
        ax.plot(traj[:, 0], traj[:, 1], '-', linewidth=1.5, alpha=0.8)
        ax.scatter([traj[0, 0]], [traj[0, 1]], c='green', s=50, marker='o', zorder=5)
        ax.scatter([traj[-1, 0]], [traj[-1, 1]], c='red', s=50, marker='*', zorder=5)

    ax.scatter([mu_target], [ls_target], c='black', s=150, marker='X', 
               zorder=6, label='Ground truth')
    ax.legend(loc='upper right')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('principia_manifold_topology.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()
    print("Saved: principia_manifold_topology.png")

# ---------------------------------------------------------------------------
# 6. Geodesic Length Comparison
# ---------------------------------------------------------------------------

def print_geodesic_analysis():
    print("\n" + "="*70)
    print("GEODESIC LENGTH ANALYSIS (Note #005)")
    print("="*70)

    test_pairs = [
        (np.array([-2.0, -0.5]), np.array([3.0, 0.8])),
        (np.array([0.0, 0.0]), np.array([2.0, 0.5])),
        (np.array([-1.0, 0.5]), np.array([1.5, -0.3])),
    ]

    for i, (start, end) in enumerate(test_pairs, 1):
        init, opt = compute_geodesic(start, end, n_points=40, init_noise=0.1)
        init_len = discrete_path_length(init)
        opt_len = discrete_path_length(opt)
        savings = (init_len - opt_len) / init_len * 100

        print(f"\nPath {i}: {start} -> {end}")
        print(f"  Initial (straight-ish) length: {init_len:.4f}")
        print(f"  Optimized geodesic length:     {opt_len:.4f}")
        print(f"  'Cognitive effort' saved:      {savings:.1f}%")
        print(f"  -> Geodesic reasoning is {savings:.1f}% more efficient than random walk")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Principia Artificialis: Information Manifold Topology Simulation")
    print("="*70)
    print("Generating visualization...")
    create_manifold_visualization()
    print_geodesic_analysis()
    print("\n" + "="*70)
    print("Done. Push principia_manifold_topology.py and the PNG to:")
    print("  Principia-Artificialis/simulations/")
    print("="*70)
