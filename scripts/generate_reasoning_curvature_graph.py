import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = '#0a0e1a'
fig, ax = plt.subplots(figsize=(10,6))
x = np.linspace(0, 50, 100)
y = 0.1 * x**1.5 + np.random.normal(0, 2, 100)  # curvature growth
ax.plot(x, y, color='#a371f7', lw=2.5)
ax.set_title('Reasoning Curvature vs Chain Length', color='#f0f6fc')
ax.set_xlabel('Inference Steps')
ax.set_ylabel('Manifold Curvature')
ax.grid(alpha=0.3)
plt.savefig('figures/reasoning_curvature_graph.png', dpi=200, bbox_inches='tight')
print("Curvature graph created")
