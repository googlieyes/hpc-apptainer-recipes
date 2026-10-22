"""Minimal matplotlib example: renders a sine/cosine plot to a PNG, confirming headless plotting inside the container."""

import os
import matplotlib
matplotlib.use("Agg")          # no display needed — render to file
import matplotlib.pyplot as plt
import numpy as np

# Write the image next to this script, wherever it lives, so it lands in
# your project folder regardless of the current working directory or username.
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot.png")

x = np.linspace(0, 4 * np.pi, 400)
plt.figure(figsize=(8, 4))
plt.plot(x, np.sin(x), label="sin")
plt.plot(x, np.cos(x), label="cos")
plt.title("Rendered inside the container")
plt.legend()
plt.savefig(out_path, dpi=120)
print(f"Wrote {out_path}")
