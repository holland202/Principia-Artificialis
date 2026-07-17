import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = '#0a0e1a'
fig, ax = plt.subplots(figsize=(10,6))
gaps = np.array([2,4,8,16,32,64])
steps = -np.log(1-0.9) * gaps / 1.0
ax.plot(gaps, steps, color='#58a6ff', marker='o')
ax.set_xscale('log', base=2)
ax.set_title('Extractability Budget Scaling (Note #027)', color='#f0f6fc')
ax.set_xlabel('Information Gap ΔI (bits)')
ax.set_ylabel('Steps to 90% Extraction')
ax.grid(alpha=0.3)
plt.savefig('figures/extractability_budget_scaling.png', dpi=200, bbox_inches='tight')
print("Budget graph created")
