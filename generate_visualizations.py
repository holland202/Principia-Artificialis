#!/usr/bin/env python3
"""
Generate all 5 planned visualization figures for Principia Artificialis.
Run: python3 generate_visualizations.py
Requires: matplotlib, numpy, scipy, networkx
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np
from scipy.integrate import odeint

# Dark theme matching GitHub
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor'] = '#161b22'
plt.rcParams['text.color'] = '#c9d1d9'
plt.rcParams['axes.labelcolor'] = '#c9d1d9'
plt.rcParams['xtick.color'] = '#8b949e'
plt.rcParams['ytick.color'] = '#8b949e'

print("Generating 5 visualization figures...")

# ============================================================
# FIGURE 1: Research Dependency Network
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_facecolor('#0d1117')

themes = {
    'Measurement': '#58a6ff', 'Defects': '#f85149', 'Thermodynamics': '#d29922',
    'Geometry': '#a371f7', 'Dynamics': '#3fb950', 'Quantum': '#f778ba'
}

notes = {
    '#001': ('Measurement', (0, 6)), '#002': ('Defects', (2, 6)),
    '#003': ('Measurement', (0, 5)), '#004': ('Thermodynamics', (4, 5)),
    '#005': ('Geometry', (6, 5)), '#006': ('Measurement', (0, 4)),
    '#007': ('Dynamics', (8, 4)), '#008': ('Defects', (2, 4)),
    '#009': ('Geometry', (6, 4)), '#010': ('Dynamics', (8, 3)),
    '#011': ('Thermodynamics', (4, 3)), '#012': ('Quantum', (10, 3)),
    '#013': ('Geometry', (6, 3)), '#014': ('Dynamics', (8, 2)),
    '#015': ('Geometry', (6, 2)), '#016': ('Geometry', (6, 1)),
    '#017': ('Quantum', (10, 2)), '#018': ('Geometry', (6, 0)),
    '#019': ('Quantum', (10, 1)), '#020': ('Geometry', (6, -1)),
    '#021': ('Geometry', (8, 0)),
}

import networkx as nx
G = nx.DiGraph()
for note, (theme, pos) in notes.items():
    G.add_node(note, theme=theme, pos=pos)

edges = [
    ('#001','#003'),('#001','#006'),('#002','#008'),('#003','#006'),
    ('#003','#008'),('#004','#011'),('#005','#009'),('#005','#013'),
    ('#005','#020'),('#006','#007'),('#007','#010'),('#007','#014'),
    ('#009','#012'),('#009','#013'),('#010','#011'),('#011','#014'),
    ('#013','#015'),('#013','#016'),('#014','#016'),('#014','#017'),
    ('#016','#017'),('#016','#018'),('#017','#019'),('#020','#021'),
]
G.add_edges_from(edges)

pos = {n: d['pos'] for n, d in G.nodes(data=True)}
for edge in G.edges():
    src, dst = edge
    x1, y1 = pos[src]; x2, y2 = pos[dst]
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#30363d', lw=1.5, connectionstyle='arc3,rad=0.1'))

for note, (theme, _) in notes.items():
    x, y = pos[note]
    color = themes[theme]
    circle = Circle((x, y), 0.35, facecolor=color, edgecolor='white', linewidth=2, alpha=0.85, zorder=5)
    ax.add_patch(circle)
    ax.text(x, y, note, ha='center', va='center', fontsize=8, fontweight='bold', color='white', zorder=6)

legend_elements = [mpatches.Patch(facecolor=c, edgecolor='white', label=t) for t, c in themes.items()]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10, facecolor='#161b22', edgecolor='#30363d')
ax.set_xlim(-1.5, 12); ax.set_ylim(-2, 7.5); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Principia Artificialis — Research Dependency Network', fontsize=16, fontweight='bold', color='#f0f6fc', pad=20)
plt.tight_layout()
plt.savefig('figures/research_dependency_network.png', dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
plt.close()
print("  ✓ research_dependency_network.png")

# ============================================================
# FIGURE 2: Information Manifold Topology (6-panel)
# ============================================================
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor('#0d1117')
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: Fisher-Rao Metric Field
ax1 = fig.add_subplot(gs[0, 0])
x = np.linspace(-3, 3, 50); y = np.linspace(-3, 3, 50)
X, Y = np.meshgrid(x, y)
sigma = np.exp(Y); g_11 = 1/sigma**2; g_22 = 2/sigma**2
for i in range(0, 50, 8):
    for j in range(0, 50, 8):
        ellipse = mpatches.Ellipse((X[i,j], Y[i,j]), 0.3*np.sqrt(g_11[i,j]), 0.3*np.sqrt(g_22[i,j]),
                                    facecolor='none', edgecolor='#58a6ff', alpha=0.6, lw=0.8)
        ax1.add_patch(ellipse)
ax1.set_xlim(-3, 3); ax1.set_ylim(-3, 3)
ax1.set_title('Fisher-Rao Metric Field', fontsize=11, fontweight='bold', color='#f0f6fc')
ax1.set_xlabel('μ (mean)', fontsize=9); ax1.set_ylabel('log σ (std)', fontsize=9)
ax1.grid(True, alpha=0.2, color='#30363d')

# Panel 2: Geodesic Reasoning Paths
ax2 = fig.add_subplot(gs[0, 1])
theta = np.linspace(0.1, np.pi-0.1, 100)
for y0 in [0.5, 1.0, 1.5, 2.0, 2.5]:
    x_geo = y0 * np.cos(theta) / np.sin(theta)
    y_geo = y0 / np.sin(theta)
    ax2.plot(x_geo, y_geo, color='#3fb950', alpha=0.7, lw=1.5)
ax2.scatter([0], [1], c='#f85149', s=100, zorder=5, label='Initial State')
ax2.scatter([0], [3], c='#58a6ff', s=100, zorder=5, label='Target State')
ax2.set_xlim(-4, 4); ax2.set_ylim(0, 4)
ax2.set_title('Geodesic Reasoning Paths', fontsize=11, fontweight='bold', color='#f0f6fc')
ax2.legend(fontsize=8, facecolor='#0d1117', edgecolor='#30363d'); ax2.grid(True, alpha=0.2, color='#30363d')

# Panel 3: Topological Defects
ax3 = fig.add_subplot(gs[0, 2])
x = np.linspace(-2, 2, 100); y = np.linspace(-2, 2, 100)
X, Y = np.meshgrid(x, y)
Z1 = np.arctan2(Y-0.5, X-0.5); Z2 = np.arctan2(Y+0.5, X+0.5)
Z = np.sin(Z1 - Z2)
im = ax3.imshow(Z, extent=[-2,2,-2,2], cmap='twilight', origin='lower', alpha=0.9)
ax3.scatter([0.5, -0.5], [0.5, -0.5], c='#f85149', s=150, marker='x', linewidths=3, zorder=5)
ax3.set_title('Topological Defects (Vortices)', fontsize=11, fontweight='bold', color='#f0f6fc')
plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04, label='Phase')

# Panel 4: Entanglement Fields
ax4 = fig.add_subplot(gs[1, 0])
layers = np.arange(1, 13)
S_bell = 1.0 * np.exp(-layers/8) + 0.1
S_product = 0.05 * np.ones_like(layers)
S_ghz = 0.5 * (1 + np.sin(layers/2))
ax4.plot(layers, S_bell, 'o-', color='#f778ba', lw=2, markersize=6, label='Bell State')
ax4.plot(layers, S_product, 's--', color='#8b949e', lw=2, markersize=5, label='Product State')
ax4.plot(layers, S_ghz, '^-', color='#a371f7', lw=2, markersize=6, label='GHZ-like')
ax4.axhline(y=np.log(2), color='#30363d', linestyle=':', alpha=0.5, label='Max (log 2)')
ax4.set_xlabel('Layer Depth', fontsize=9); ax4.set_ylabel('Entanglement Entropy S', fontsize=9)
ax4.set_title('Entanglement Entropy Across Layers', fontsize=11, fontweight='bold', color='#f0f6fc')
ax4.legend(fontsize=8, facecolor='#0d1117', edgecolor='#30363d'); ax4.grid(True, alpha=0.2, color='#30363d'); ax4.set_ylim(0, 1.2)

# Panel 5: Memory Gradient Flow
ax5 = fig.add_subplot(gs[1, 1])
t = np.linspace(0, 10, 500)
theta1 = 2 * np.exp(-0.5*t) * np.cos(2*t)
theta2 = 2 * np.exp(-0.5*t) * np.sin(2*t)
ax5.plot(theta1, theta2, color='#d29922', lw=2, alpha=0.8)
ax5.scatter([theta1[0]], [theta2[0]], c='#f85149', s=100, zorder=5, marker='o', label='Initial')
ax5.scatter([0], [0], c='#3fb950', s=150, zorder=5, marker='*', label='Fixed Point')
for i in range(0, len(t), 50):
    dx, dy = -0.3*theta1[i], -0.3*theta2[i]
    ax5.annotate('', xy=(theta1[i]+dx, theta2[i]+dy), xytext=(theta1[i], theta2[i]),
                arrowprops=dict(arrowstyle='->', color='#d29922', alpha=0.5, lw=1))
ax5.set_xlabel('θ₁', fontsize=9); ax5.set_ylabel('θ₂', fontsize=9)
ax5.set_title('Memory Gradient Flow', fontsize=11, fontweight='bold', color='#f0f6fc')
ax5.legend(fontsize=8, facecolor='#0d1117', edgecolor='#30363d'); ax5.grid(True, alpha=0.2, color='#30363d'); ax5.set_aspect('equal')

# Panel 6: RG Flow Diagram
ax6 = fig.add_subplot(gs[1, 2])
g = np.linspace(0, 3, 100)
beta = -g * (g - 1) * (g - 2)
ax6.plot(g, beta, color='#58a6ff', lw=2.5)
ax6.axhline(y=0, color='#30363d', linestyle='-', alpha=0.5)
ax6.axvline(x=0, color='#30363d', linestyle='-', alpha=0.5)
for gp, color, label in [(0, '#f85149', 'Trivial'), (1, '#3fb950', 'Critical'), (2, '#f85149', 'Unstable')]:
    ax6.scatter([gp], [0], c=color, s=150, zorder=5, marker='o', edgecolors='white', linewidths=2)
    ax6.annotate(label, xy=(gp, 0), xytext=(gp+0.15, 0.3), fontsize=9, color=color)
for g0 in [0.3, 0.7, 1.3, 1.7, 2.3]:
    b0 = -g0 * (g0 - 1) * (g0 - 2)
    ax6.annotate('', xy=(g0 + 0.15*np.sign(b0), 0), xytext=(g0, 0),
                arrowprops=dict(arrowstyle='->', color='white', alpha=0.6, lw=1.5))
ax6.set_xlabel('Coupling g', fontsize=9); ax6.set_ylabel('β(g) = dg/dℓ', fontsize=9)
ax6.set_title('RG Flow: β-Function', fontsize=11, fontweight='bold', color='#f0f6fc')
ax6.grid(True, alpha=0.2, color='#30363d'); ax6.set_ylim(-1, 1)

fig.suptitle('Information Manifold Topology — 6-Panel Overview', fontsize=16, fontweight='bold', color='#f0f6fc', y=0.98)
plt.savefig('figures/manifold_topology_6panel.png', dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
plt.close()
print("  ✓ manifold_topology_6panel.png")

# ============================================================
# FIGURE 3: Quantum Frontiers
# ============================================================
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#0d1117')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: Entanglement Entropy Landscape
ax1 = fig.add_subplot(gs[0, 0])
x = np.linspace(0, 1, 100); y = np.linspace(0, 1, 100)
X, Y = np.meshgrid(x, y)
S = -(X*np.log(X+1e-10) + (1-X)*np.log(1-X+1e-10))
im1 = ax1.imshow(S, extent=[0,1,0,1], cmap='magma', origin='lower', aspect='auto')
ax1.contour(X, Y, S, levels=8, colors='white', alpha=0.3, linewidths=0.8)
ax1.set_xlabel('Subsystem A Purity', fontsize=9); ax1.set_ylabel('Subsystem B Purity', fontsize=9)
ax1.set_title('Entanglement Entropy Landscape', fontsize=11, fontweight='bold', color='#f0f6fc')
plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label='S(ρ)')

# Panel 2: Bell Inequality in Attention
ax2 = fig.add_subplot(gs[0, 1])
theta = np.linspace(0, 2*np.pi, 200)
S_quantum = 2*np.sqrt(2) * np.abs(np.cos(theta/2))
S_classical = np.ones_like(theta) * 2
attention_weight = 0.5 + 0.5*np.sin(theta)**2
S_attention = S_quantum * attention_weight + 2*(1-attention_weight)
ax2.plot(theta, S_quantum, color='#f778ba', lw=2.5, label='Quantum (max 2√2)', alpha=0.9)
ax2.plot(theta, S_classical, '--', color='#8b949e', lw=2, label='Classical Bound (2)')
ax2.plot(theta, S_attention, color='#a371f7', lw=2, label='Attention-Modulated', alpha=0.8)
ax2.axhline(y=2*np.sqrt(2), color='#f85149', linestyle=':', alpha=0.5, label=f'Max = {2*np.sqrt(2):.3f}')
ax2.fill_between(theta, 2, 2*np.sqrt(2), alpha=0.1, color='#f778ba', label='Quantum Advantage')
ax2.set_xlabel('Measurement Angle θ', fontsize=9); ax2.set_ylabel('CHSH Parameter S', fontsize=9)
ax2.set_title('Bell Inequality in Attention Mechanisms', fontsize=11, fontweight='bold', color='#f0f6fc')
ax2.legend(fontsize=8, facecolor='#0d1117', edgecolor='#30363d', loc='upper right'); ax2.grid(True, alpha=0.2, color='#30363d'); ax2.set_ylim(0, 3.5)

# Panel 3: Quantum Circuit Reasoning
ax3 = fig.add_subplot(gs[1, 0])
for q in [0, 1]:
    ax3.plot([0, 6], [q, q], color='#58a6ff', lw=2, alpha=0.7)
    ax3.text(-0.5, q, f'|q{q}⟩', fontsize=10, color='#c9d1d9', ha='right', va='center')
gates = [
    (0, 0, 'H', '#3fb950'), (1, 0, '●', '#f85149'), (1, 1, '⊕', '#f85149'),
    (2, 0, 'Rz', '#d29922'), (3, 0, '●', '#f85149'), (3, 1, '⊕', '#f85149'),
    (4, 1, 'H', '#3fb950'), (5, 0, 'M', '#a371f7'), (5, 1, 'M', '#a371f7')
]
for x, y, g, c in gates:
    if g == '●':
        ax3.scatter([x], [y], c=c, s=200, zorder=5, marker='o', edgecolors='white', linewidths=2)
    elif g == '⊕':
        ax3.scatter([x], [y], c='none', s=200, zorder=5, marker='o', edgecolors=c, linewidths=2)
        ax3.plot([x-0.15, x+0.15], [y, y], color=c, lw=2, zorder=6)
        ax3.plot([x, x], [y-0.15, y+0.15], color=c, lw=2, zorder=6)
    else:
        rect = FancyBboxPatch((x-0.25, y-0.25), 0.5, 0.5, boxstyle="round,pad=0.05",
                               facecolor=c, edgecolor='white', linewidth=2, alpha=0.9, zorder=5)
        ax3.add_patch(rect)
        ax3.text(x, y, g, ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=6)
ax3.plot([1, 1], [0, 1], color='#f85149', lw=2, zorder=4)
ax3.plot([3, 3], [0, 1], color='#f85149', lw=2, zorder=4)
ax3.set_xlim(-1, 6.5); ax3.set_ylim(-0.8, 1.8)
ax3.set_title('Quantum Circuit Reasoning: Bell State Preparation', fontsize=11, fontweight='bold', color='#f0f6fc')
ax3.axis('off')

# Panel 4: Quantum Advantage Window
ax4 = fig.add_subplot(gs[1, 1])
n_qubits = np.arange(2, 21)
classical_cost = 2**n_qubits
quantum_cost = n_qubits**3 * 100
crossover = n_qubits[np.where(quantum_cost < classical_cost)[0][-1]] if np.any(quantum_cost < classical_cost) else 20
ax4.semilogy(n_qubits, classical_cost, 'o-', color='#f85149', lw=2.5, markersize=6, label='Classical (2ⁿ)')
ax4.semilogy(n_qubits, quantum_cost, 's-', color='#3fb950', lw=2.5, markersize=6, label='Quantum (n³)')
ax4.axvline(x=crossover, color='#d29922', linestyle='--', alpha=0.7, label=f'Crossover ≈ {crossover} qubits')
ax4.fill_between(n_qubits, quantum_cost, classical_cost, where=(quantum_cost < classical_cost),
                  alpha=0.15, color='#3fb950', label='Quantum Advantage Zone')
ax4.set_xlabel('Number of Qubits', fontsize=9); ax4.set_ylabel('Computational Cost (log scale)', fontsize=9)
ax4.set_title('Quantum Advantage Window', fontsize=11, fontweight='bold', color='#f0f6fc')
ax4.legend(fontsize=8, facecolor='#0d1117', edgecolor='#30363d'); ax4.grid(True, alpha=0.2, color='#30363d')

fig.suptitle('Quantum Frontiers — Entanglement, Bell Inequalities, and Quantum Advantage', fontsize=16, fontweight='bold', color='#f0f6fc', y=0.98)
plt.savefig('figures/quantum_frontiers.png', dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
plt.close()
print("  ✓ quantum_frontiers.png")

# ============================================================
# FIGURE 4: Thermodynamic Engine
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_facecolor('#0d1117')

S_AB = np.linspace(1, 4, 50); T_AB = np.ones_like(S_AB) * 4
S_BC = np.linspace(4, 4.5, 50); T_BC = 4 * np.exp(-(S_BC - 4))
S_CD = np.linspace(4.5, 1.5, 50); T_CD = np.ones_like(S_CD) * 1.5
S_DA = np.linspace(1.5, 1, 50); T_DA = 1.5 * np.exp((S_DA - 1.5) * np.log(4/1.5) / (1 - 1.5))

ax.plot(S_AB, T_AB, color='#f85149', lw=3, label='Isothermal Expansion (Explore)')
ax.plot(S_BC, T_BC, color='#d29922', lw=3, label='Adiabatic Expansion (Cooling)')
ax.plot(S_CD, T_CD, color='#58a6ff', lw=3, label='Isothermal Compression (Exploit)')
ax.plot(S_DA, T_DA, color='#3fb950', lw=3, label='Adiabatic Compression (Heating)')

S_fill = np.concatenate([S_AB, S_BC, S_CD, S_DA])
T_fill = np.concatenate([T_AB, T_BC, T_CD, T_DA])
ax.fill(S_fill, T_fill, alpha=0.15, color='#a371f7', label='Work Output = Reasoning Gain')

states = {'A (Prompt)': (1, 4), 'B (Explore)': (4, 4), 'C (Synthesize)': (4.5, 1.5), 'D (Conclude)': (1.5, 1.5)}
for label, (s, t) in states.items():
    ax.scatter([s], [t], c='white', s=200, zorder=5, edgecolors='#f0f6fc', linewidths=2)
    ax.annotate(label, xy=(s, t), xytext=(s+0.2, t+0.3), fontsize=10, color='#f0f6fc', fontweight='bold')

ax.annotate('', xy=(2.5, 4.3), xytext=(2.5, 5.2), arrowprops=dict(arrowstyle='->', color='#f85149', lw=2.5))
ax.text(2.5, 5.4, 'Q_in: Information Input', ha='center', fontsize=10, color='#f85149', fontweight='bold')
ax.annotate('', xy=(3, 1.2), xytext=(3, 0.3), arrowprops=dict(arrowstyle='->', color='#58a6ff', lw=2.5))
ax.text(3, 0.0, 'Q_out: Discarded Hypotheses', ha='center', fontsize=10, color='#58a6ff', fontweight='bold')
ax.annotate('', xy=(5.2, 2.8), xytext=(5.2, 2.2), arrowprops=dict(arrowstyle='->', color='#3fb950', lw=2.5))
ax.text(5.4, 2.5, 'W: Reasoning\\nOutput', fontsize=10, color='#3fb950', fontweight='bold', rotation=90, va='center')

efficiency = 1 - 1.5/4
ax.text(0.5, 0.5, f'η = 1 - T_cold/T_hot = {efficiency:.2f}\\n(Maximal reasoning efficiency)',
        fontsize=11, color='#d29922', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#161b22', edgecolor='#d29922', alpha=0.9))

ax.set_xlabel('Entropy S (Information Content)', fontsize=12, fontweight='bold')
ax.set_ylabel('Temperature T (Computational Temperature)', fontsize=12, fontweight='bold')
ax.set_title('Thermodynamic Engine of Artificial Reasoning\\n(Carnot Cycle Analogy)', fontsize=16, fontweight='bold', color='#f0f6fc', pad=20)
ax.legend(fontsize=10, facecolor='#161b22', edgecolor='#30363d', loc='upper left'); ax.grid(True, alpha=0.2, color='#30363d'); ax.set_xlim(0, 6); ax.set_ylim(0, 6)
plt.tight_layout()
plt.savefig('figures/thermodynamic_engine.png', dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
plt.close()
print("  ✓ thermodynamic_engine.png")

# ============================================================
# FIGURE 5: Renormalization Flow Diagram
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_facecolor('#0d1117')

g = np.linspace(-2.5, 2.5, 25); h = np.linspace(-2.5, 2.5, 25)
G, H = np.meshgrid(g, h)
Beta_g = -G + G**3 - 0.3*G*H
Beta_h = -2*H + G**2
M = np.sqrt(Beta_g**2 + Beta_h**2); M[M == 0] = 1
Bg, Bh = Beta_g/M, Beta_h/M
ax.quiver(G, H, Bg, Bh, M, cmap='plasma', scale=30, width=0.004, alpha=0.8)

fixed = [(0, 0, 'Trivial\\n(UV)', '#f85149', 300), (1, 0, 'Critical\\n(IR)', '#3fb950', 400), (-1, 0, 'Critical\\n(IR)', '#3fb950', 400)]
for gx, hy, label, color, size in fixed:
    ax.scatter([gx], [hy], c=color, s=size, zorder=6, marker='X', edgecolors='white', linewidths=2)
    ax.annotate(label, xy=(gx, hy), xytext=(gx+0.2, hy+0.3), fontsize=11, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#161b22', edgecolor=color, alpha=0.9))

traj_starts = [(2, 1.5), (-2, 1.5), (2, -1.5), (-2, -1.5), (0.5, 2), (0.5, -2)]
colors_t = ['#58a6ff', '#f778ba', '#d29922', '#a371f7', '#3fb950', '#f85149']

def simple_rg(y, t):
    g1, g2 = y
    return [-g1 + g1**3 - 0.3*g1*g2, -2*g2 + g1**2]

for i, (g0, h0) in enumerate(traj_starts):
    t = np.linspace(0, 8, 300)
    sol = odeint(simple_rg, [g0, h0], t)
    ax.plot(sol[:,0], sol[:,1], color=colors_t[i], lw=2, alpha=0.7)
    ax.scatter([g0], [h0], c=colors_t[i], s=80, zorder=5, marker='o', edgecolors='white', linewidths=1)

ax.set_xlabel('g — Interaction Strength', fontsize=12, fontweight='bold')
ax.set_ylabel('h — External Field Coupling', fontsize=12, fontweight='bold')
ax.set_title('Renormalization Group Flow in Representation Space\\n(β-function Trajectories to Fixed Points)', fontsize=16, fontweight='bold', color='#f0f6fc', pad=20)
ax.grid(True, alpha=0.2, color='#30363d'); ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('figures/renormalization_flow.png', dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
plt.close()
print("  ✓ renormalization_flow.png")

print("\nAll 5 figures generated successfully in figures/")
