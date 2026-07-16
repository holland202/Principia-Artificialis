import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['figure.facecolor'] = '#0a0e1a'

fig = plt.figure(figsize=(8,6), dpi=120)
ax = fig.add_subplot(111, projection='3d')

def update(frame):
    ax.cla()
    u = np.linspace(0, 2*np.pi, 80)
    v = np.linspace(0, np.pi, 60)
    U, V = np.meshgrid(u, v)
    R = 3 + np.sin(frame/8)*0.5
    X = (R + np.cos(V)) * np.cos(U)
    Y = (R + np.cos(V)) * np.sin(U)
    Z = np.sin(V) * (1 + 0.3*np.sin(3*frame/10))
    ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.85)
    ax.set_title('Holographic Bulk Emergence\n(Surface → Deep Thought)', color='#5ce1e6')
    ax.axis('off')

ani = animation.FuncAnimation(fig, update, frames=50, interval=60)
ani.save('figures/holographic_bulk_emergence.gif', writer='pillow', fps=12)
print("Holographic GIF created")
