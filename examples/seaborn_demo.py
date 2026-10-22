"""
Statistical-analysis demo for the scipy-notebook container.

Generates its own dataset (no download, no cache — works offline inside the
container) and shows a typical research workflow: build -> aggregate (pandas)
-> visualise (seaborn/matplotlib). Headless (Agg backend) — writes a PNG next
to this script, so it works on a compute node with no display.

Run:  ~/bin/vscode-python-wrapper.sh <path>/seaborn_demo.py
"""

import os
import matplotlib
matplotlib.use("Agg")                      # no display needed
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")
rng = np.random.default_rng(42)            # reproducible

# --- Build a synthetic "restaurant tips" dataset ----------------------------
# No sns.load_dataset(): that downloads and caches to a read-only path inside
# the container. Generating it here keeps the demo offline and self-contained.
n = 244
days = rng.choice(["Thur", "Fri", "Sat", "Sun"], size=n, p=[0.25, 0.15, 0.35, 0.25])
times = np.where(np.isin(days, ["Sat", "Sun"]), "Dinner",
                 rng.choice(["Lunch", "Dinner"], size=n))
size = rng.integers(1, 5, size=n) + 1                      # party size 2..5
total_bill = np.round(8 + 6 * size + rng.gamma(2.0, 3.0, n), 2)
tip = np.round(total_bill * rng.normal(0.16, 0.04, n).clip(0.05, 0.30), 2)

tips = pd.DataFrame({
    "total_bill": total_bill,
    "tip": tip,
    "size": size,
    "day": pd.Categorical(days, categories=["Thur", "Fri", "Sat", "Sun"], ordered=True),
    "time": times,
})
tips["tip_pct"] = 100 * tips["tip"] / tips["total_bill"]

# --- A little pandas analysis, printed to the console -----------------------
print("Dataset shape:", tips.shape)
print("\nAverage tip %% by day:")
by_day = (tips.groupby("day", observed=True)["tip_pct"]
              .mean().round(2).sort_values(ascending=False))
print(by_day.to_string())

# --- 4-panel statistical figure ---------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
fig.suptitle("scipy-notebook container — statistical analysis demo", fontsize=14)

# Panel 1: regression — does the bill predict the tip?
sns.regplot(data=tips, x="total_bill", y="tip", ax=axes[0, 0],
            scatter_kws={"s": 15, "alpha": 0.5})
axes[0, 0].set_title("Tip vs total bill (regression)")

# Panel 2: distribution of tip % by time of day
sns.histplot(data=tips, x="tip_pct", hue="time", kde=True,
             bins=25, ax=axes[0, 1])
axes[0, 1].set_title("Tip %% distribution by time")

# Panel 3: spread of bills across days
sns.boxplot(data=tips, x="day", y="total_bill", ax=axes[1, 0])
axes[1, 0].set_title("Total bill by day")

# Panel 4: average tip % by day and party size (pivot -> heatmap)
pivot = tips.pivot_table(values="tip_pct", index="day",
                         columns="size", aggfunc="mean", observed=True)
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis", ax=axes[1, 1])
axes[1, 1].set_title("Mean tip %% by day & party size")

fig.tight_layout(rect=(0, 0, 1, 0.96))

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "seaborn_demo.png")
fig.savefig(out_path, dpi=120)
print(f"\nWrote {out_path}")
