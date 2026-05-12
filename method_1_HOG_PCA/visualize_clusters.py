import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

DATA_CSV = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\oasis_clustered.csv"
OUT_PNG  = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\cluster_visualization.png"

df = pd.read_csv(DATA_CSV)
df["cluster"] = df["cluster"].astype(int)

x = df["PC1"]
y = df["PC2"]

# ── colour maps ───────────────────────────────────────────────────────────────
cluster_colors = {0: "#2196F3", 1: "#FF5722", 2: "#4CAF50", 3: "#9C27B0"}
cdr_colors     = {0.0: "#4CAF50", 0.5: "#FFC107", 1.0: "#FF5722", 2.0: "#B71C1C"}
cdr_labels     = {0.0: "CDR 0.0 (healthy)", 0.5: "CDR 0.5 (very mild)",
                  1.0: "CDR 1.0 (mild)",    2.0: "CDR 2.0 (moderate)"}

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("OASIS Brain MRI — HOG+PCA Feature Space (PC1 vs PC2)",
             fontsize=13, fontweight="bold", y=1.01)

# ── LEFT: coloured by cluster ─────────────────────────────────────────────────
ax = axes[0]
for cid, color in cluster_colors.items():
    mask = df["cluster"] == cid
    ax.scatter(x[mask], y[mask], c=color, s=18, alpha=0.7,
               edgecolors="none", label=f"Cluster {cid}  (n={mask.sum()})")
ax.set_xlabel("PC1", fontsize=11)
ax.set_ylabel("PC2", fontsize=11)
ax.set_title("Coloured by Cluster", fontsize=12)
ax.legend(title="Cluster", fontsize=9, title_fontsize=9, markerscale=1.5)
ax.grid(True, linewidth=0.4, alpha=0.5)

# ── RIGHT: coloured by CDR ────────────────────────────────────────────────────
ax = axes[1]

# plot NaN CDR patients first (grey, background layer)
nan_mask = df["CDR"].isna()
ax.scatter(x[nan_mask], y[nan_mask], c="#CCCCCC", s=14, alpha=0.4,
           edgecolors="none", label=f"CDR unknown  (n={nan_mask.sum()})", zorder=1)

# plot known CDR patients on top
for cdr_val, color in cdr_colors.items():
    mask = df["CDR"] == cdr_val
    ax.scatter(x[mask], y[mask], c=color, s=20, alpha=0.85,
               edgecolors="none", label=f"{cdr_labels[cdr_val]}  (n={mask.sum()})", zorder=2)

ax.set_xlabel("PC1", fontsize=11)
ax.set_ylabel("PC2", fontsize=11)
ax.set_title("Coloured by CDR", fontsize=12)
ax.legend(title="CDR", fontsize=9, title_fontsize=9, markerscale=1.5)
ax.grid(True, linewidth=0.4, alpha=0.5)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print(f"Saved: {OUT_PNG}")
