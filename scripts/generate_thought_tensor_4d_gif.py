import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Simple 4D Thought Tensor projection
np.random.seed(42)
t = np.linspace(0, 2*np.pi, 120)
L, K = 8, 6
T4d = np.sin(t[:,None,None]) * np.random.randn(len(t), L, K) + np.cos(t[:,None,None]) * np.random.randn(len(t), L, K)

fig = plt.figure(figsize=(10, 8), facecolor='#0b0f14')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0b0f14')
ln, = ax.plot([], [], [], 'o-', color='#4fd1c5', lw=2, markersize=6)

def update(frame):
    ax.cla()
    ax.set_facecolor('#0b0f14')
    data = T4d[frame]
    X, Y = np.meshgrid(range(data.shape[1]), range(data.shape[0]))
    ax.plot_surface(X, Y, data, cmap='viridis', alpha=0.7)
    ax.set_title(f'Thought Tensor 𝒯 — 4D Projection (t={frame/120:.2f})', color='white')
    ax.set_xlabel('Rank'); ax.set_ylabel('Layers'); ax.set_zlabel('Thought Amplitude')
    return ln,

ani = FuncAnimation(fig, update, frames=len(t), interval=50, blit=False)
ani.save('figures/thought_tensor_4d_rotation.gif', writer='pillow', fps=20, dpi=90)
print("4D Thought Tensor GIF saved to figures/thought_tensor_4d_rotation.gif")
plt.close()
