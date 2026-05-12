import glob
import os
import numpy as np
import pandas as pd
from PIL import Image
from skimage.feature import hog
from skimage.transform import resize
from sklearn.decomposition import PCA

DATA_DIR    = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data"
OUTPUT_CSV  = os.path.join(DATA_DIR, "patient_hog_pca_features.csv")

# HOG parameters
TARGET_SIZE     = (128, 128)
ORIENTATIONS    = 9
PIXELS_PER_CELL = (8, 8)
CELLS_PER_BLOCK = (2, 2)

N_COMPONENTS = 50   # PCA target dimensions
IMAGES_PER_PATIENT = 5


# ─── helpers ──────────────────────────────────────────────────────────────────

def load_image(path):
    img = Image.open(path).convert("L")
    arr = np.array(img, dtype=np.float32) / 255.0
    return resize(arr, TARGET_SIZE, anti_aliasing=True)


def extract_hog(arr):
    features, _ = hog(
        arr,
        orientations=ORIENTATIONS,
        pixels_per_cell=PIXELS_PER_CELL,
        cells_per_block=CELLS_PER_BLOCK,
        visualize=True,
        feature_vector=True,
    )
    return features


# ─── Step 1: discover patients ────────────────────────────────────────────────

patient_dirs = sorted(
    d for d in glob.glob(os.path.join(DATA_DIR, "OAS1_*"))
    if os.path.isdir(d)
)
n_patients = len(patient_dirs)
print(f"Found {n_patients} patient folders")

# ─── Step 2: extract HOG for every image (all patients) ──────────────────────
# Layout: hog_matrix[i] = HOG vector for the i-th image (across all patients)
# patient_index[i] = which patient that image belongs to
# patient_ids[p]   = OAS1_xxxx label for patient p

patient_ids  = []
patient_index = []   # parallel to hog_matrix rows
hog_rows     = []

for p_idx, p_dir in enumerate(patient_dirs):
    pid = os.path.basename(p_dir)
    gif_paths = sorted(glob.glob(os.path.join(p_dir, "*.gif")))

    if not gif_paths:
        print(f"  WARNING: no GIFs in {pid}, skipping")
        continue

    patient_ids.append(pid)
    for gpath in gif_paths:
        arr = load_image(gpath)
        hog_rows.append(extract_hog(arr))
        patient_index.append(len(patient_ids) - 1)

    if (p_idx + 1) % 50 == 0 or (p_idx + 1) == n_patients:
        print(f"  HOG extracted: {p_idx + 1}/{n_patients} patients")

hog_matrix    = np.array(hog_rows, dtype=np.float32)   # (n_images, 8100)
patient_index = np.array(patient_index)

n_images = hog_matrix.shape[0]
print(f"\nHOG matrix shape: {hog_matrix.shape}  "
      f"({n_patients} patients × ~{n_images//n_patients} images)")

# ─── Step 3: fit PCA on the full HOG matrix ──────────────────────────────────

n_components = min(N_COMPONENTS, n_images - 1)
print(f"\nFitting PCA ({n_components} components) on {n_images} images ...")
pca = PCA(n_components=n_components, random_state=42)
pca.fit(hog_matrix)

cumvar = np.cumsum(pca.explained_variance_ratio_)
print(f"Variance explained — PC50: {cumvar[49]*100:.1f}%"
      if n_components >= 50 else
      f"Variance explained — PC{n_components}: {cumvar[-1]*100:.1f}%")

# ─── Step 4: transform all images → (n_images, 50) ───────────────────────────

reduced = pca.transform(hog_matrix)   # (n_images, n_components)
print(f"Reduced matrix shape: {reduced.shape}")

# ─── Step 5: average the 5 image vectors per patient → (n_patients, 50) ──────

n_actual_patients = len(patient_ids)
patient_vectors = np.zeros((n_actual_patients, n_components), dtype=np.float32)

for p_idx in range(n_actual_patients):
    mask = patient_index == p_idx
    patient_vectors[p_idx] = reduced[mask].mean(axis=0)

print(f"Per-patient averaged matrix shape: {patient_vectors.shape}")

# ─── Step 6: save as CSV ──────────────────────────────────────────────────────

col_names = [f"PC{i+1}" for i in range(n_components)]
df = pd.DataFrame(patient_vectors, columns=col_names)
df.insert(0, "patient_id", patient_ids)

df.to_csv(OUTPUT_CSV, index=False)

print(f"\nFinal DataFrame shape : {df.shape}  (rows=patients, cols=patient_id + PCA components)")
print(f"Saved to              : {OUTPUT_CSV}")
print(f"\nFirst 3 rows preview:")
print(df.head(3).to_string(max_cols=8))
