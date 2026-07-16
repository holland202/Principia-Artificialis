import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

np.random.seed(42)
frames = 90
layers, tokens = 12, 16
entropy = np.zeros((frames, layers, tokens))

for f in range(frames):
    t = f / frames * 4 * np.pi
    entropy[f] = 0.5 + 0.5 * np.sin(t + np.outer(np.linspace(0, np.pi, layers), np.linspace(0, 2*np.pi, tokens)))

fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0b0f14')
im = ax.imshow(entropy[0], cmap='plasma', origin='lower', aspect='auto')
ax.set_title('Entanglement Entropy Landscape — Breathing Pattern (𝒯)', color='white', fontsize=14)
ax.set_xlabel('Tokens'); ax.set_ylabel('Layers')
plt.colorbar(im, ax=ax, label='Entanglement Entropy')

def animate(i):
    im.set_array(entropy[i])
    return [im]

ani = FuncAnimation(fig, animate, frames=frames, interval=60, blit=True)
ani.save('figures/entanglement_breathing.gif', writer='pillow', fps=15, dpi=90)
print("Entanglement breathing GIF saved")
