# Master Thesis — Clustering Alzheimer's patients from brain MRI and clinical data

Unsupervised clustering of the [OASIS-1 cross-sectional dataset](https://www.oasis-brains.org/).
Each patient is described by HOG features of five MRI images (reduced with PCA) and by clinical
variables. Patients are clustered with robust mixed-type distances (robust Mahalanobis, Generalised
Gower and Related Metric Scaling, combined by blocks) and k-medoids, and with k-means as a
comparison.

---

## Main question

Do the images, alone or together with the clinical variables, give clinically meaningful groups of
patients? The configurations are compared with the Pairwise Separability Index (PSI): how clearly the
clusters differ on Age, MMSE, nWBV, eTIV and CDR (|Cliff's δ|) and on Education, SES and sex (Total
Variation Distance).

All configurations use the same 216 patients (complete clinical data and all five image types, no
imputation) and k = 4.

| ID | Data | Method | PSI | Stability (bootstrap ARI) |
|---|---|---|---|---|
| **C1-b** | Clinical | k-means | **0.50** | **0.75** |
| C1 | Clinical | Robust G-Gower + PAM | 0.43 | 0.34 |
| M2 | Images + clinical | Robust G-Gower + PAM | 0.40 | 0.20 |
| M1 | Images + clinical | RelMS + PAM | 0.40 | – |
| C2 | Clinical + CDR | Robust G-Gower + PAM | 0.37 | 0.37 |
| M3 | Images + clinical + CDR | Robust G-Gower + PAM | 0.35 | 0.20 |
| I2 | Images | G-Gower + PAM | 0.22 | 0.16 |
| I1 | Images | RelMS + PAM | 0.21 | – |
| I2-b | Images | k-means | 0.12 | 0.49 |

In short: the clinical variables give the clearest and most stable groups (younger healthy, older
healthy, older men with large heads and very mild impairment, cognitively impaired). Adding the
images does not improve the separation, and the images on their own give groups that hardly differ
clinically. Stability is not computed for the RelMS configurations (I1, M1), because new patients
are assigned with the G-Gower distance.

---

## Repository structure

```
├── requirements.txt        package versions
├── src/                    shared code, used by every analysis notebook
│   ├── setup.ipynb             loads the notebooks below, in this order
│   ├── config.ipynb            settings and the nine configurations
│   ├── data_utils.ipynb        the 216 patients; matrix and blocks of each configuration
│   ├── psi.ipynb               Pairwise Separability Index
│   ├── clustering_utils.ipynb  fitting a configuration; bootstrap refits
│   ├── evaluation_utils.ipynb  PSI tables, cluster numbering, medoids
│   └── plot_utils.ipynb        figures
├── analysis/               the analysis, one notebook per question
│   ├── 00_project_guide           how the code is organised, with small examples
│   ├── 01_choose_k                number of clusters
│   ├── 02_compare_configurations  PSI of every configuration and selection
│   ├── 03_profile_selected        the selected clusters in detail
│   ├── 04_stability               stability of the partitions
│   ├── 05_secondary_results       silhouette and agreement with CDR
│   ├── 06_pca_robustness          number of image components
│   ├── 07_before_after            comparison with the previous method
│   └── 09_results                 summary of all results, including 2-D and 3-D cluster maps
├── results/                figures and tables, one folder per analysis notebook
├── results_v1/             backup of the first revised version (Education and SES as quantitative,
│                           sex not used to build the clusters)
└── notebooks/              data pipeline (HOG features, PCA) and the earlier experiments
```

The best place to start is `analysis/09_results.ipynb`, which collects the main tables and figures.

The code is written as notebooks. The `src/` notebooks only define settings and functions; every
analysis notebook loads them with its first line, `%run -i ../src/setup.ipynb`, so all analyses use
the same code and the same settings.

### Earlier work

`notebooks/` contains the data pipeline (`01_data_pipeline/`: HOG extraction, PCA per image type)
and the experiments that came before the current analysis (`02_final_results/`,
`03_other_experiments/`, `04_alternative_approaches/`). Those earlier experiments compared the
clusters with CDR (ARI/NMI) and used an unscaled clinical block in which head size (eTIV) dominated
the distance; notebook `analysis/07_before_after` compares that method with the current one.

---

## How to run

1. Create a virtual environment with Python 3.12 and install the packages:
   ```
   python -m venv .venv
   .venv\Scripts\activate          (Windows)    or    source .venv/bin/activate
   pip install --no-deps -r requirements.txt
   python -m ipykernel install --user --name thesis-venv --display-name "Python (thesis .venv)"
   ```
   `--no-deps` is needed because `db-robust-clust` declares `scikit-learn-extra` as a dependency,
   which it never imports and which does not build on Windows without C++ Build Tools.
2. Put the clinical spreadsheet in `notebooks/01_data_pipeline/` (see **Data** below).
3. Open the notebooks in `analysis/` with the kernel *Python (thesis .venv)* and run them in order.
   Notebook 02 has to run before 03–07, because they read its selection. Notebook 09 only reads the
   saved results and can be run on its own once 01–07 have been run.

---

## Data

Raw MRI images are from the [OASIS-1 dataset](https://www.oasis-brains.org/) and are **not
included** in this repository, as required by the OASIS Data Use Agreement. The clinical
spreadsheet (`oasis_cross-sectional*.xlsx`) is also excluded, because it contains patient-level data,
and so is the raw HOG feature file (`raw_hog_features_per_image.csv`, over 150 MB), which is only
needed for notebook 06.

The derived PCA features (`notebooks/01_data_pipeline/pca_*.csv`) are included. To rebuild everything
from the raw data, download OASIS-1, put the `OAS1_xxxx/` patient folders in the project root and the
clinical spreadsheet in `notebooks/01_data_pipeline/`, and run the notebooks of
`notebooks/01_data_pipeline/` in order.

---

## References

Pairwise Separability Index and clustering approach: https://hdl.handle.net/10016/51001

Marcus, D.S., Wang, T.H., Parker, J., Csernansky, J.G., Morris, J.C., Buckner, R.L. (2007).
*Open Access Series of Imaging Studies (OASIS): Cross-sectional MRI data in young, middle aged,
nondemented, and demented older adults.* Journal of Cognitive Neuroscience, 19(9), 1498–1507.
