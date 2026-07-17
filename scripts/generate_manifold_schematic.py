import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = '#0a0e1a'
fig, ax = plt.subplots(figsize=(10,8))
ax.set_facecolor('#0a0e1a')
circle = plt.Circle((0,0), 3, color='#3d9db0', alpha=0.2)
ax.add_patch(circle)
ax.plot([0,2], [0,2], color='#a8f0f5', lw=2, label='Geodesic')
ax.set_title('Information Manifold Schematic\n(Geodesics of Reasoning)', color='#f0f6fc')
ax.legend()
ax.axis('off')
plt.savefig('figures/information_manifold_schematic.png', dpi=200, bbox_inches='tight')
print("Manifold schematic created")
