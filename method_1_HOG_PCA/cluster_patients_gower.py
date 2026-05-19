import numpy as np
import pandas as pd
import kmedoids
from robust_mixed_dist.mixed import simple_gower_dist_matrix

DATA_CSV     = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_1_HOG_PCA\oasis_combined.csv"
OUTPUT_CSV   = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_1_HOG_PCA\oasis_clustered_gower.csv"
N_CLUSTERS   = 4
RANDOM_STATE = 42

# ── load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_CSV)
print(f"Loaded: {df.shape}")

pc_cols = [f"PC{i}" for i in range(1, 51)]
X = df[pc_cols].to_numpy(dtype=np.float64)
print(f"Feature matrix: {X.shape}")

# ── Gower distance matrix ─────────────────────────────────────────────────────
# All 50 PC columns are quantitative: p1=50, p2=0 (binary), p3=0 (multi-class)
print("\nComputing simple Gower distance matrix ...")
D = simple_gower_dist_matrix(X, p1=50, p2=0, p3=0)
print(f"Distance matrix shape : {D.shape}")
print(f"Value range           : [{D.min():.4f}, {D.max():.4f}]")

# ── clustering ────────────────────────────────────────────────────────────────
print(f"\nFitting FasterPAM k-medoids (k={N_CLUSTERS}, metric=gower) ...")
result = kmedoids.fasterpam(D, medoids=N_CLUSTERS, random_state=RANDOM_STATE)
labels = np.array(result.labels)

print(f"Loss: {result.loss:.4f}")
print(f"Medoid patient IDs: {df['patient_id'].iloc[list(result.medoids)].tolist()}")
sizes = {c: int((labels == c).sum()) for c in sorted(set(labels))}
print(f"Cluster sizes: {sizes}")

# ── attach labels and evaluate against CDR ────────────────────────────────────
df["cluster"] = labels

print("\n--- Crosstab: cluster vs CDR ---")
has_cdr = df[df["CDR"].notnull()].copy()
has_cdr["CDR"] = has_cdr["CDR"].astype(str)
crosstab = pd.crosstab(has_cdr["cluster"], has_cdr["CDR"],
                       margins=True, margins_name="Total")
print(crosstab.to_string())

print("\n--- Row-% (CDR distribution within each cluster) ---")
pct = pd.crosstab(has_cdr["cluster"], has_cdr["CDR"],
                  normalize="index").mul(100).round(1)
print(pct.to_string())

# ── save result ───────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved clustered data to: {OUTPUT_CSV}")
