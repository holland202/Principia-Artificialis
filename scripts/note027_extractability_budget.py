#!/usr/bin/env python3
"""
Note #027 - An Extractability Budget for Chain-of-Thought
Toy numerical illustration. NOT evidence from real LLMs.
Generates: figures/note027_extractability_budget.png
Requires: numpy, matplotlib  (Termux: apt install python-numpy python-matplotlib)
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BG = '#0d1117'; AX = '#161b22'; FG = '#c9d1d9'; MUT = '#8b949e'; GRID = '#30363d'
plt.rcParams.update({
    'figure.facecolor': BG, 'axes.facecolor': AX, 'savefig.facecolor': BG,
    'text.color': FG, 'axes.labelcolor': FG, 'axes.edgecolor': GRID,
    'xtick.color': MUT, 'ytick.color': MUT, 'grid.color': GRID,
    'font.size': 10,
})

def h2(p):
    """Binary entropy in bits."""
    p = np.clip(p, 1e-15, 1.0 - 1e-15)
    return -p*np.log2(p) - (1.0-p)*np.log2(1.0-p)

# Panel A: the quantum anchor (exact)
c = np.linspace(0.0, 1.0, 400)
chi   = h2((1.0 - c)/2.0)
p_err = (1.0 - np.sqrt(1.0 - c**2))/2.0
i_acc = 1.0 - h2(p_err)

# Panel B: step-count scaling (toy rate model)
theta = 0.90
gaps  = np.array([2, 4, 8, 16, 32, 64])
budgets = [0.5, 1.0, 2.0]
colors  = {0.5: '#f778ba', 1.0: '#58a6ff', 2.0: '#3fb950'}
rng = np.random.default_rng(7)

def simulate(gap, chi_step, n_trials=400, t_max=4000):
    ts = np.empty(n_trials)
    for k in range(n_trials):
        I, t = 0.0, 0
        target = theta*gap
        while I < target and t < t_max:
            chi_t = max(0.0, rng.normal(chi_step, 0.15*chi_step))
            I += chi_t * (1.0 - I/gap)
            t += 1
        ts[k] = t
    return ts.mean(), ts.std()/np.sqrt(n_trials)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6))

axA.plot(c, chi,   color='#a371f7', lw=2.5, label=r'Holevo  $\chi = S(\bar{\rho})$')
axA.plot(c, i_acc, color='#58a6ff', lw=2.5, ls='--', label=r'Accessible  $I_{acc}$ (Helstrom)')
axA.fill_between(c, i_acc, chi, color='#a371f7', alpha=0.15)
axA.text(0.5, 0.62, 'accessibility gap\n$\\chi \\geq I_{acc}$  (Holevo 1973)',
         color='#d29922', fontsize=10, ha='center')
axA.set_xlabel(r'state overlap  $c = |\langle\psi_0|\psi_1\rangle|$')
axA.set_ylabel('information (bits)')
axA.set_title('A. Per-step budget is finite (exact quantum result)',
              fontweight='bold', color='#f0f6fc')
axA.legend(facecolor=AX, edgecolor=GRID)
axA.grid(alpha=0.3)
axA.set_xlim(0, 1); axA.set_ylim(0, 1.02)

gfit = np.linspace(2, 64, 100)
for b in budgets:
    bound = -np.log(1.0-theta) * gfit / b
    axB.plot(gfit, bound, ls='--', lw=1.5, color=colors[b], alpha=0.8,
             label=f'bound,  chi = {b} bits/step')
    m, e = [], []
    for g in gaps:
        mm, ee = simulate(g, b)
        m.append(mm); e.append(ee)
    axB.errorbar(gaps, m, yerr=e, fmt='o', ms=6, color=colors[b],
                 ecolor=colors[b], capsize=3)
axB.set_xscale('log', base=2)
axB.set_xticks(gaps)
axB.set_xticklabels([str(g) for g in gaps])
axB.set_xlabel(r'information gap  $\Delta I$  (bits)')
axB.set_ylabel('steps to 90% extraction')
axB.set_title(r'B. Conjectured scaling  $N \geq -\ln(1-\theta)\,\Delta I\,/\,\chi$',
              fontweight='bold', color='#f0f6fc')
axB.legend(facecolor=AX, edgecolor=GRID, fontsize=9)
axB.grid(alpha=0.3)

fig.suptitle('Note #027 - Extractability Budget (toy rate model; not evidence from real LLMs)',
             fontsize=13, fontweight='bold', color='#f0f6fc')
fig.tight_layout(rect=[0, 0, 1, 0.94])

os.makedirs('figures', exist_ok=True)
out = 'figures/note027_extractability_budget.png'
if os.path.exists(out):                       # no-clobber guard
    out = 'figures/note027_extractability_budget_kimi.png'
fig.savefig(out, dpi=150, bbox_inches='tight')
print('saved:', out)
