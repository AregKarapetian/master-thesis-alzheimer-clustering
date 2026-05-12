import numpy as np
import pandas as pd
import kmedoids
from db_robust_clust.models import SampleDistClustering

PIXEL_CSV   = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_2_Pixel_PCA\patient_pixel_pca_features.csv"
HOG_COMBINED = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_1_HOG_PCA\oasis_combined.csv"
OUTPUT_CSV  = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_2_Pixel_PCA\oasis_combined_pixel.csv"

N_CLUSTERS   = 4
RANDOM_STATE = 42

# ── merge pixel features with clinical columns from method 1 ──────────────────
pixel_df = pd.read_csv(PIXEL_CSV)

# pull patient_id + clinical columns only from the HOG combined file
hog_combined = pd.read_csv(HOG_COMBINED)
clinical_cols = ["patient_id", "M/F", "Hand", "Age", "Educ", "SES",
                 "MMSE", "CDR", "eTIV", "nWBV", "ASF", "Delay"]
clinical_df = hog_combined[clinical_cols]

combined = pixel_df.merge(clinical_df, on="patient_id", how="inner")
combined.to_csv(OUTPUT_CSV, index=False)
print(f"Merged DataFrame shape : {combined.shape}")
print(f"Saved to               : {OUTPUT_CSV}")

# ── clustering ────────────────────────────────────────────────────────────────
pc_cols = [f"PC{i}" for i in range(1, 51)]
X = combined[pc_cols].to_numpy(dtype=np.float64)
print(f"\nFeature matrix: {X.shape}")

base = kmedoids.KMedoids(
    n_clusters=N_CLUSTERS,
    metric="precomputed",
    method="fasterpam",
    random_state=RANDOM_STATE,
)
model = SampleDistClustering(
    clustering_method=base,
    metric="euclidean",
    frac_sample_size=1.0,
    random_state=RANDOM_STATE,
    p1=X.shape[1],
)

print(f"Fitting SampleDistClustering (k={N_CLUSTERS}, metric=euclidean) ...")
model.fit(X)
labels = model.labels_.astype(int)

combined["cluster"] = labels
sizes = {c: int((labels == c).sum()) for c in sorted(set(labels))}
print(f"Cluster sizes: {sizes}")

# ── crosstab vs CDR ───────────────────────────────────────────────────────────
print("\n--- Crosstab: cluster vs CDR ---")
crosstab = pd.crosstab(combined["cluster"], combined["CDR"],
                        margins=True, margins_name="Total")
print(crosstab.to_string())

print("\n--- Row-% (CDR distribution within each cluster) ---")
pct = pd.crosstab(combined["cluster"], combined["CDR"],
                   normalize="index").mul(100).round(1)
print(pct.to_string())

# ── comparison reminder ───────────────────────────────────────────────────────
print("\n--- HOG+PCA result (method 1) for comparison ---")
hog_clustered = pd.read_csv(
    r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\method_1_HOG_PCA\oasis_clustered.csv"
)
print(pd.crosstab(hog_clustered["cluster"], hog_clustered["CDR"],
                   margins=True, margins_name="Total").to_string())
