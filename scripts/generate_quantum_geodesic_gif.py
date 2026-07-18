import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from PIL import Image
import io
import os

os.makedirs("figures", exist_ok=True)

W, H = 800, 500
frames = 72
duration = 5000  # ms total

xs = np.linspace(-0.95, 0.95, 200)
ys = np.linspace(-0.95, 0.95, 200)
X, Y = np.meshgrid(xs, ys)
R2 = X**2 + Y**2
mask = R2 < 1.0

g = np.zeros_like(X)
g[mask] = 1.0 / (1.0 - R2[mask])**2
g = np.log(1 + g)
g = (g - g.min()) / (g.max() - g.min())

def geodesic_curve(theta0, theta1, t):
    theta = theta0 + (theta1 - theta0) * t
    r = 0.9 * (1 - 0.3 * np.sin(2 * np.pi * t))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

num_curves = 5
theta_starts = np.linspace(0, 2*np.pi, num_curves, endpoint=False)
theta_ends = theta_starts + np.pi * (0.7 + 0.3 * np.random.rand(num_curves))

images = []

for f in range(frames):
    t = f / float(frames)
    fig, ax = plt.subplots(1, 1, figsize=(W/100.0, H/100.0), dpi=100)
    ax.set_facecolor("#0b0f14")
    fig.patch.set_facecolor("#0b0f14")

    ax.imshow(g, extent=[xs.min(), xs.max(), ys.min(), ys.max()],
              origin="lower", cmap=cm.plasma, alpha=0.25)

    for i in range(num_curves):
        ts = np.linspace(0, 1, 200)
        xs_c, ys_c = geodesic_curve(theta_starts[i], theta_ends[i], ts)
        ts_shifted = (ts + i/num_curves - t) % 1.0
        xp, yp = geodesic_curve(theta_starts[i], theta_ends[i], ts_shifted[0])

        ax.plot(xs_c, ys_c, color="#00e5ff", linewidth=1.2, alpha=0.7)
        ax.plot(xp, yp, "o", color="#ff0077", markersize=6, alpha=0.9)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal", "box")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB")
    images.append(img)

gif_path = "figures/quantum_geodesic_flow.gif"
images[0].save(
    gif_path,
    save_all=True,
    append_images=images[1:],
    duration=int(duration/frames),
    loop=0,
    optimize=True
)

print(f"GIF saved to {gif_path}")
