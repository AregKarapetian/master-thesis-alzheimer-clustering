import glob
import os
import numpy as np
import pandas as pd
from PIL import Image
from skimage.transform import resize
from sklearn.decomposition import PCA

DATA_DIR   = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data"
OUTPUT_CSV = os.path.join(DATA_DIR, "method_2_Pixel_PCA", "patient_pixel_pca_features.csv")

TARGET_SIZE  = (128, 128)   # same as HOG pipeline for fair comparison
N_COMPONENTS = 50
FLAT_DIM     = TARGET_SIZE[0] * TARGET_SIZE[1]   # 16,384


def load_image(path):
    img = Image.open(path).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    return resize(arr, TARGET_SIZE, anti_aliasing=True).flatten()   # → 16,384-d


# ── Step 1: load all images ───────────────────────────────────────────────────
patient_dirs = sorted(
    d for d in glob.glob(os.path.join(DATA_DIR, "OAS1_*"))
    if os.path.isdir(d)
)
n_patients = len(patient_dirs)
print(f"Found {n_patients} patient folders")

patient_ids   = []
patient_index = []
pixel_rows    = []

for p_idx, p_dir in enumerate(patient_dirs):
    pid = os.path.basename(p_dir)
    gif_paths = sorted(glob.glob(os.path.join(p_dir, "*.gif")))

    if not gif_paths:
        print(f"  WARNING: no GIFs in {pid}, skipping")
        continue

    patient_ids.append(pid)
    for gpath in gif_paths:
        pixel_rows.append(load_image(gpath))
        patient_index.append(len(patient_ids) - 1)

    if (p_idx + 1) % 50 == 0 or (p_idx + 1) == n_patients:
        print(f"  Loaded: {p_idx + 1}/{n_patients} patients")

pixel_matrix  = np.array(pixel_rows, dtype=np.float32)   # (2080, 16384)
patient_index = np.array(patient_index)
n_images      = pixel_matrix.shape[0]

print(f"\nPixel matrix shape : {pixel_matrix.shape}  ({n_patients} patients x ~{n_images // n_patients} images)")

# ── Step 2: fit PCA on the full pixel matrix ──────────────────────────────────
print(f"\nFitting PCA ({N_COMPONENTS} components) on {n_images} images ...")
pca = PCA(n_components=N_COMPONENTS, random_state=42)
pca.fit(pixel_matrix)

cumvar = np.cumsum(pca.explained_variance_ratio_)
print(f"Variance explained by {N_COMPONENTS} components: {cumvar[-1]*100:.1f}%")

# ── Step 3: transform → (2080, 50) ───────────────────────────────────────────
reduced = pca.transform(pixel_matrix)
print(f"Reduced matrix shape: {reduced.shape}")

# ── Step 4: average 5 slices per patient → (416, 50) ─────────────────────────
n_actual = len(patient_ids)
patient_vectors = np.zeros((n_actual, N_COMPONENTS), dtype=np.float32)
for p_idx in range(n_actual):
    mask = patient_index == p_idx
    patient_vectors[p_idx] = reduced[mask].mean(axis=0)

print(f"Per-patient averaged matrix shape: {patient_vectors.shape}")

# ── Step 5: save ──────────────────────────────────────────────────────────────
col_names = [f"PC{i+1}" for i in range(N_COMPONENTS)]
df = pd.DataFrame(patient_vectors, columns=col_names)
df.insert(0, "patient_id", patient_ids)

df.to_csv(OUTPUT_CSV, index=False)
print(f"\nFinal DataFrame shape : {df.shape}")
print(f"Saved to              : {OUTPUT_CSV}")
print(f"\nFirst 3 rows preview:")
print(df.head(3).to_string(max_cols=8))
