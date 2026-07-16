import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['figure.facecolor'] = '#0a0e1a'

fig = plt.figure(figsize=(8,6), dpi=120)
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0a0e1a')

def update(frame):
    ax.cla()
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 50)
    T, P = np.meshgrid(theta, phi)
    R = 2 + np.sin(5*frame/10) * 0.3
    X = R * np.sin(P) * np.cos(T)
    Y = R * np.sin(P) * np.sin(T)
    Z = R * np.cos(P) * (1 + 0.2*np.sin(frame/5))
    ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8)
    ax.set_title('Reasoning Event Horizon\n(Information Falls In)', color='#a8f0f5')
    ax.axis('off')

ani = animation.FuncAnimation(fig, update, frames=60, interval=50)
ani.save('figures/black_hole_reasoning.gif', writer='pillow', fps=15)
print("Black hole GIF created")
