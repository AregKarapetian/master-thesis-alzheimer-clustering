# Master Thesis — Alzheimer's Disease Clustering via Brain MRI

Unsupervised clustering of the [OASIS-1 cross-sectional dataset](https://www.oasis-brains.org/)
using per-image-type HOG features, PCA dimensionality reduction, and a family of robust
mixed-type distance metrics (Robust Mahalanobis, Generalised Gower, Related Metric
Scaling) with k-medoids clustering.

---

## Project overview

This project tests whether brain-MRI-derived image features, alone or combined with
clinical assessments, can recover patient subgroups that align with the Clinical
Dementia Rating (CDR) — the standard dementia-severity scale — for the 416-patient
OASIS-1 cohort (216 with complete clinical records). The short answer, after 19
notebooks' worth of experiments: clustering reliably finds real, large, reproducible
patient structure, but that structure is organised around sex and brain volume, not
CDR. The full methodology, every experiment, and the complete numeric results are in
`notebooks/02_final_results/thesis_full_report.pdf`, which is the single best starting
point for understanding this project.

**Pipeline:**

```
Raw MRI GIFs (5 slices/patient: coronal, sagittal x2, transverse x2)
        |
        v
HOG feature extraction (per image type, NOT averaged)  ->  8,100-dim vector per image
        |
        v
Per-image-type PCA  ->  110 components per type (unified across types)
        |
        v
Robust mixed-type distance (Robust Mahalanobis / Generalised Gower / RelMS)
        |
        v
SampleDistClustering (FasterPAM k-medoids)
        |
        v
Cluster evaluation vs CDR (ARI, NMI, silhouette) + effect-size feature-separation analysis
```

---

## Repository structure

All active work lives under `notebooks/`, split into five folders so it's clear which
notebooks represent the final method versus exploratory work along the way:

| Folder | Contents |
|---|---|
| `notebooks/01_data_pipeline/` | Notebooks 01–03: raw HOG extraction, per-image PCA, merging. Produces the `pca_*.csv` feature files, the raw HOG CSV, and reads the clinical Excel file that every later notebook depends on. |
| `notebooks/02_final_results/` | Notebooks 18–19: the flagship cluster-profiling analysis using RelMS, and its follow-up after a package update added per-block distance assignment. **Start here** — also contains the two compiled reports, `thesis_full_report.pdf` (full project writeup) and `clustering_report.pdf` (deep dive on notebook 18 specifically). |
| `notebooks/03_other_experiments/` | Notebooks 04–11, 16: the intermediate experiments that led to the final method (single/merged-image clustering, the Generalised Gower block-dominance anomaly, RelMS, image-type redundancy analysis, leave-one-image-out). |
| `notebooks/04_alternative_approaches/` | Notebooks 12–15, 17: Tucker decomposition and two-stage PCA as alternative dimensionality-reduction strategies. Neither beat the HOG+PCA baseline; kept for completeness and because notebook 15→17 documents a genuine bug found and fixed along the way. |
| `notebooks/unsorted_legacy/` | Output files with no matching current notebook (superseded by earlier iterations of the pipeline). Not needed to reproduce anything. |

Each notebook resolves its own paths relative to its folder (via `os.getcwd()`), so
they run correctly as long as the five-folder structure above stays intact and the
notebook is launched from its own directory — no machine-specific paths to edit.

### Earlier methodology (not part of the active pipeline)

`files_before_the_final_version_of_thesis/` (not tracked in this repository — see
Data section below) contains two earlier, superseded approaches: a simple script-based
pipeline that averaged HOG features across all 5 image types before clustering, and an
intermediate notebook-based version that predates an aspect-ratio-preserving padding
fix applied to the images before HOG extraction. Both are discussed briefly in the full
report as methodological context; neither represents the thesis's actual results.

---

## How to run

1. Obtain your own copy of the OASIS-1 raw data (see **Data** below) and place the
   `OAS1_*` patient folders and the clinical Excel file as described there.
2. Run the notebooks in `notebooks/01_data_pipeline/` in order (01 → 02 → 03) to
   regenerate the HOG/PCA feature files, **or** skip this step entirely — the derived
   `pca_*.csv` files are already included in this repository (they contain no raw
   image data, just PCA-reduced numeric features), so notebooks 04 onward can be run
   directly against them.
3. Run any notebook in `02_final_results/`, `03_other_experiments/`, or
   `04_alternative_approaches/` independently — none of them depend on each other's
   outputs, only on the shared files in `01_data_pipeline/`.

---

## Requirements

```
pip install scikit-image scikit-learn pandas openpyxl matplotlib seaborn \
            kmedoids polars pyarrow tqdm scipy
pip install robust-mixed-dist==0.1.26   # notebooks 01-18
pip install robust-mixed-dist==0.1.27   # notebook 19 specifically (adds per-block d1)
```

> **Note:** `db_robust_clust` (an alternative package referenced in some early
> exploratory work) depends on `scikit-learn-extra`, which requires Microsoft C++
> Build Tools on Windows. The `kmedoids` package is used as a dependency-free
> drop-in replacement throughout the active pipeline.

---

## Data

Raw MRI images are from the [OASIS-1 dataset](https://www.oasis-brains.org/) and are
**not included** in this repository, restricted by the OASIS Data Use Agreement.
Clinical metadata (the `oasis_cross-sectional*.xlsx` file) is similarly excluded, as
it contains patient-level data.

To reproduce from raw data: download the OASIS-1 dataset, organise it into
`OAS1_xxxx/` patient folders (each containing 5 GIF slices) directly under the project
root, and place the clinical Excel file in `notebooks/01_data_pipeline/`. The derived,
non-identifiable PCA feature files (`notebooks/01_data_pipeline/pca_*.csv`) **are**
included, so most of the analysis can be run without obtaining raw access at all.

---

## Reference

Marcus, D.S., Wang, T.H., Parker, J., Csernansky, J.G., Morris, J.C., Buckner, R.L. (2007).
*Open Access Series of Imaging Studies (OASIS): Cross-sectional MRI data in young, middle aged, nondemented, and demented older adults.*
Journal of Cognitive Neuroscience, 19(9), 1498-1507.
