import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from PIL import Image
import io
import os

os.makedirs("figures", exist_ok=True)

W, H = 700, 450
frames = 60
duration = 5000  # ms total

# Grid: layer (x) vs token/index (y)
nx, ny = 60, 40
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)
X, Y = np.meshgrid(x, y)

# Base entanglement-like pattern: smooth hills and valleys
def entanglement_field(X, Y, t):
    # Combine several sinusoidal modes + slow time modulation
    f1 = np.sin(2*np.pi*X + t) * np.cos(3*np.pi*Y)
    f2 = np.sin(4*np.pi*X) * np.cos(2*np.pi*Y + 0.5*t)
    f3 = np.sin(6*np.pi*(X + Y) + 0.3*t)
    E = np.abs(f1 + 0.7*f2 + 0.5*f3)
    # Add a slow global "breathing" factor
    breathe = 0.7 + 0.3 * np.sin(t)
    return E * breathe

images = []

for f in range(frames):
    t = 2*np.pi * f / float(frames)
    E = entanglement_field(X, Y, t)

    fig, ax = plt.subplots(1, 1, figsize=(W/100.0, H/100.0), dpi=100)
    ax.set_facecolor("#0b0f14")
    fig.patch.set_facecolor("#0b0f14")

    # Heatmap of entanglement entropy
    im = ax.imshow(E, extent=[0, 1, 0, 1], origin="lower",
                   cmap=cm.viridis, vmin=0, vmax=1.2)

    ax.set_xlabel("Layer (normalized)")
    ax.set_ylabel("Token / index (normalized)")
    ax.set_title("Entanglement entropy landscape")

    # Minimal colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Entropy (a.u.)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    for label in ax.get_xticklabels():
        label.set_fontsize(8)
    for label in ax.get_yticklabels():
        label.set_fontsize(8)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB")
    images.append(img)

gif_path = "figures/entanglement_landscape.gif"
images[0].save(
    gif_path,
    save_all=True,
    append_images=images[1:],
    duration=int(duration/frames),
    loop=0,
    optimize=True
)

print(f"GIF saved to {gif_path}")
