import numpy as np
import pandas as pd
import kmedoids
from db_robust_clust.models import SampleDistClustering

DATA_CSV   = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\oasis_combined.csv"
N_CLUSTERS = 4
RANDOM_STATE = 42

# ── load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_CSV)
print(f"Loaded: {df.shape}")

pc_cols = [f"PC{i}" for i in range(1, 51)]
X = df[pc_cols].to_numpy(dtype=np.float64)
print(f"Feature matrix: {X.shape}")

# ── clustering ────────────────────────────────────────────────────────────────
# SampleDistClustering wraps any sklearn-compatible clusterer that accepts a
# precomputed distance matrix.  frac_sample_size=1.0 uses all 416 patients
# (small enough that subsampling isn't needed).
base = kmedoids.KMedoids(
    n_clusters=N_CLUSTERS,
    metric="precomputed",
    method="fasterpam",
    random_state=RANDOM_STATE,
)

model = SampleDistClustering(
    clustering_method=base,
    metric="euclidean",
    frac_sample_size=1.0,   # use all 416 — dataset is small
    random_state=RANDOM_STATE,
    p1=X.shape[1],          # all 50 columns are quantitative
)

print(f"\nFitting SampleDistClustering (k={N_CLUSTERS}, metric=euclidean) ...")
model.fit(X)
labels = model.labels_
print(f"Cluster labels assigned: {np.unique(labels)}")
print(f"Cluster sizes: { {c: int((labels == c).sum()) for c in np.unique(labels)} }")

# ── attach labels and evaluate against CDR ────────────────────────────────────
df["cluster"] = labels

print("\n--- Crosstab: cluster vs CDR ---")
crosstab = pd.crosstab(
    df["cluster"],
    df["CDR"],
    margins=True,
    margins_name="Total",
)
print(crosstab.to_string())

# normalised version (row %) to see dominant CDR per cluster
print("\n--- Row-% (CDR distribution within each cluster) ---")
pct = pd.crosstab(df["cluster"], df["CDR"], normalize="index").mul(100).round(1)
print(pct.to_string())

# ── save result ───────────────────────────────────────────────────────────────
out_path = DATA_CSV.replace("oasis_combined.csv", "oasis_clustered.csv")
df.to_csv(out_path, index=False)
print(f"\nSaved clustered data to: {out_path}")
