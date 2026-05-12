# Master Thesis — Alzheimer's Disease Clustering via Brain MRI

Unsupervised clustering of the [OASIS-1 cross-sectional dataset](https://www.oasis-brains.org/) using HOG image features, PCA dimensionality reduction, and robust k-medoids clustering.

---

## Project overview

This project combines structural brain MRI images with clinical variables to group 416 patients into 4 clusters, then evaluates how well image-derived clusters align with the Clinical Dementia Rating (CDR) scale.

**Pipeline:**

```
Raw MRI GIFs (5 slices/patient)
        │
        ▼
HOG feature extraction  →  8,100-dim vector per image
        │
        ▼
PCA reduction           →  50 components (59.2 % variance explained)
        │
        ▼
Average 5 slices        →  1 vector per patient  (416 × 50 matrix)
        │
        ▼
Merge with clinical data (age, MMSE, CDR, eTIV, nWBV, …)
        │
        ▼
SampleDistClustering (k-medoids, Euclidean, k=4)
        │
        ▼
Cluster evaluation vs CDR  +  scatter-plot visualisation
```

---

## Repository structure

| File | Description |
|---|---|
| `extract_hog.py` | HOG extraction + PCA on all 416 patients → `patient_hog_pca_features.csv` |
| `merge_features.py` | Merges image features with OASIS clinical Excel file → `oasis_combined.csv` |
| `cluster_patients.py` | Runs `SampleDistClustering` (k=4) → `oasis_clustered.csv` |
| `visualize_clusters.py` | PC1 vs PC2 scatter plots coloured by cluster and by CDR → PNG |
| `organize_oasis.py` | Utility script for organising raw downloads into patient folders |
| `patient_hog_pca_features.csv` | 416 × 51 — `patient_id` + `PC1`–`PC50` |
| `oasis_combined.csv` | 416 × 62 — image features + 11 clinical variables |
| `oasis_clustered.csv` | 416 × 63 — combined data + `cluster` label |
| `cluster_visualization.png` | Side-by-side scatter plots (cluster colours vs CDR colours) |

---

## Key results

| Cluster | n | CDR 0.0 (healthy) | CDR 0.5 | CDR 1.0 |
|---|---|---|---|---|
| 0 | 78 | 93.3 % | 6.7 % | 0 % |
| 1 | 77 | 84.0 % | 16.0 % | 0 % |
| 2 | 112 | 67.3 % | 21.8 % | 9.1 % |
| 3 | 149 | 45.0 % | 37.9 % | 16.4 % |

Image-only clusters show a clear dementia gradient, with Cluster 3 capturing the highest proportion of dementia patients (CDR ≥ 0.5).

---

## Requirements

```
pip install scikit-image scikit-learn pandas openpyxl matplotlib seaborn \
            db_robust_clust kmedoids robust-mixed-dist polars pyarrow tqdm
```

> **Note:** `db_robust_clust` depends on `scikit-learn-extra`, which requires Microsoft C++ Build Tools on Windows. The `kmedoids` package is used as a compatible drop-in replacement.

---

## Data

Raw MRI images are from the [OASIS-1 dataset](https://www.oasis-brains.org/) and are **not included** in this repository (restricted by the OASIS Data Use Agreement). Clinical metadata is available from the same source as `oasis_cross-sectional.xlsx`.

To reproduce, download the OASIS-1 dataset, organise it into `OAS1_xxxx/` patient folders each containing 5 GIF slices, and place the clinical Excel file in the project directory.

---

## Reference

Marcus, D.S., Wang, T.H., Parker, J., Csernansky, J.G., Morris, J.C., Buckner, R.L. (2007).
*Open Access Series of Imaging Studies (OASIS): Cross-sectional MRI data in young, middle aged, nondemented, and demented older adults.*
Journal of Cognitive Neuroscience, 19(9), 1498–1507.
