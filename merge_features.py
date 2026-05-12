import pandas as pd

FEATURES_CSV = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\patient_hog_pca_features.csv"
CLINICAL_XLS = r"C:\Users\aregk\Downloads\oasis_cross-sectional-5708aa0a98d82080 (1).xlsx"
OUTPUT_CSV   = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data\oasis_combined.csv"

# ── load ──────────────────────────────────────────────────────────────────────
features = pd.read_csv(FEATURES_CSV)
clinical = pd.read_excel(CLINICAL_XLS)

print(f"Image features : {features.shape}  (patient_id format: '{features['patient_id'].iloc[0]}')")
print(f"Clinical data  : {clinical.shape}   (ID format: '{clinical['ID'].iloc[0]}')")

# ── keep only the first MR session per patient (20 patients have MR1 + MR2) ──
# Images are organised per patient folder (OAS1_xxxx), not per session,
# so MR1 is the canonical record to use.
clinical = clinical[clinical["ID"].str.endswith("_MR1")].copy()
clinical["patient_id"] = clinical["ID"].str.replace(r"_MR\d+$", "", regex=True)
clinical = clinical.drop(columns=["ID"])
print(f"Clinical (MR1 only) : {clinical.shape}")

# ── merge (inner join: only patients with both image features and clinical data)
combined = features.merge(clinical, on="patient_id", how="inner")

print(f"\nAfter inner join: {combined.shape}")
print(f"  Patients with image features : {len(features)}")
print(f"  Patients in clinical data    : {len(clinical)}")
print(f"  Matched patients             : {len(combined)}")

unmatched_img = set(features["patient_id"]) - set(clinical["patient_id"])
unmatched_clin = set(clinical["patient_id"]) - set(features["patient_id"])
if unmatched_img:
    print(f"  Image-only (no clinical)     : {len(unmatched_img)}  e.g. {sorted(unmatched_img)[:3]}")
if unmatched_clin:
    print(f"  Clinical-only (no image)     : {len(unmatched_clin)}  e.g. {sorted(unmatched_clin)[:3]}")

# ── save ──────────────────────────────────────────────────────────────────────
combined.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved to: {OUTPUT_CSV}")

print(f"\nFinal DataFrame shape : {combined.shape}")
print(f"Columns               : {combined.columns.tolist()}")
print(f"\nFirst 3 rows:")
print(combined.head(3).to_string(max_cols=10))
