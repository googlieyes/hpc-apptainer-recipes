"""
Capability demo for the scipy-notebook container.

Exercises numpy, scipy, pandas, scikit-learn and matplotlib together and
renders a 4-panel summary figure. Headless (Agg backend) — writes a PNG
next to this script, so it works on a compute node with no display.

Run:  ~/bin/vscode-python-wrapper.sh <path>/capability_demo.py
"""

import os
import matplotlib
matplotlib.use("Agg")                      # no display needed
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from scipy import stats, signal
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

rng = np.random.default_rng(12)            # reproducible

# --- Panel 1: noisy signal + smoothed (numpy + scipy.signal) ----------------
t = np.linspace(0, 1, 500)
clean = np.sin(2 * np.pi * 7 * t) + 0.5 * np.sin(2 * np.pi * 13 * t)
noisy = clean + rng.normal(0, 0.4, t.size)
smoothed = signal.savgol_filter(noisy, window_length=31, polyorder=3)

# --- Panel 2: linear regression (pandas + scikit-learn) ---------------------
n = 120
x = rng.uniform(0, 10, n)
y = 2.3 * x + 1.0 + rng.normal(0, 2.0, n)
df = pd.DataFrame({"x": x, "y": y})
model = LinearRegression().fit(df[["x"]], df["y"])
xs = np.linspace(0, 10, 100)
fit = model.predict(pd.DataFrame({"x": xs}))   # DataFrame keeps feature names consistent

# --- Panel 3: distribution + fitted normal (scipy.stats) --------------------
sample = rng.normal(loc=5, scale=2, size=2000)
mu, sigma = stats.norm.fit(sample)
pdf_x = np.linspace(sample.min(), sample.max(), 200)
pdf_y = stats.norm.pdf(pdf_x, mu, sigma)

# --- Panel 4: KMeans clustering (scikit-learn) ------------------------------
centers = np.array([[0, 0], [4, 5], [8, 1]])
pts = np.vstack([c + rng.normal(0, 0.8, (80, 2)) for c in centers])
km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(pts)

# --- Figure -----------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
fig.suptitle("scipy-notebook container — capability demo", fontsize=14)

ax = axes[0, 0]
ax.plot(t, noisy, color="0.7", lw=0.8, label="noisy")
ax.plot(t, smoothed, color="C3", lw=1.8, label="Savitzky–Golay")
ax.set_title("Signal smoothing (scipy.signal)")
ax.legend(fontsize=8)

ax = axes[0, 1]
ax.scatter(df["x"], df["y"], s=12, alpha=0.6)
ax.plot(xs, fit, color="C1", lw=2,
        label=f"fit: y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}")
ax.set_title("Linear regression (scikit-learn)")
ax.legend(fontsize=8)

ax = axes[1, 0]
ax.hist(sample, bins=40, density=True, color="C0", alpha=0.6)
ax.plot(pdf_x, pdf_y, color="C3", lw=2,
        label=f"N(μ={mu:.1f}, σ={sigma:.1f})")
ax.set_title("Distribution fit (scipy.stats)")
ax.legend(fontsize=8)

ax = axes[1, 1]
ax.scatter(pts[:, 0], pts[:, 1], c=km.labels_, cmap="viridis", s=14, alpha=0.7)
ax.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
           c="red", marker="X", s=120, label="centroids")
ax.set_title("KMeans clustering (scikit-learn)")
ax.legend(fontsize=8)

fig.tight_layout(rect=(0, 0, 1, 0.96))

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "capability_demo.png")
fig.savefig(out_path, dpi=120)
print(f"Wrote {out_path}")

# A little console output too, to show the libraries are live.
print(f"pandas DataFrame: {df.shape[0]} rows, columns {list(df.columns)}")
print(f"regression R^2: {model.score(df[['x']], df['y']):.3f}")
print(f"normal fit: mu={mu:.3f}, sigma={sigma:.3f}")
print(f"cluster sizes: {np.bincount(km.labels_).tolist()}")
