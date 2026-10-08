# Thesis Project Summary — Unsupervised Clustering of Alzheimer's/Dementia Patients from Brain MRI

## Goal

Using the OASIS cross-sectional dataset (416 patients, 5 MRI scan types per patient), the
question is whether **image-derived features alone, or combined with clinical variables, produce
patient clusters that align with clinical dementia severity (CDR)** — without ever using CDR
as a clustering input. CDR (0 = healthy, 0.5 = very mild, 1 = mild, 2 = moderate) is known for
only 235 of the 416 patients and is used strictly for **post-hoc evaluation** of whatever clusters
come out.

## Feature extraction

Each patient has five MRI planes (coronal, atlas-registered sagittal and transverse, a
brain-masked transverse, and a native/unregistered sagittal). Each image is padded, resized, and
converted to HOG features (9 orientations, 8×8 cells, 2×2 blocks → 8,100 features/image, 40,500
total per patient). Per image type, PCA is applied with a two-pass strategy that finds the minimum
component count needed for ~59% variance in the hardest type, then refits every type to that
same number of components (110), so all five image types are directly comparable dimensionally.

## Clustering framework

Clustering uses a family of robust, mixed-type distance metrics and a fast k-medoids engine
(`robust_mixed_dist` / `db_robust_clust`, developed by our advisor Fabio Scielzo-Ortiz). This is
the same toolkit used in his Reddit/Gaza-conflict polarization paper — there it clusters LLM-derived
discursive variables extracted from text; here it clusters PCA-reduced HOG features extracted from
MRI images. The core methods:
- **Robust Mahalanobis** distance for single quantitative blocks
- **Generalised Gower** distance for mixing quantitative + binary + categorical clinical variables
- **Related Metric Scaling (RelMS)** for combining several *typed blocks* (e.g. five separate image
  types), each rescaled by its own geometric variability before being combined, so no single block
  dominates purely because it has more columns
- **SampleDistClustering / FasterPAM k-medoids**, which subsamples for tractability and returns
  real patients as cluster medoids (not synthetic centroids)

## What was actually run

1. **Per-image-type clustering** (Euclidean and Robust Mahalanobis, k=3/4, each of the 5 image
   types alone) — best single-type result was `masked_tra` (Euclidean, k=3): ARI = 0.060, NMI = 0.085,
   the strongest CDR alignment found anywhere in the project.
2. **Merged 5-image clustering** (all 550 PCA features concatenated, Euclidean vs. Robust
   Mahalanobis, k=3/4) — ARI stayed in [−0.007, 0.013], NMI in [0.02, 0.05].
3. **Clinical + imaging via Generalised Gower** (all-images-merged, each single image type, and
   clinical-only, all combined with 8 clinical variables) — revealed an anomaly: every one of these
   variants (all-images+clinical, cor+clinical, gfc_sag+clinical, …, and even the clinical-only
   baseline) produced numerically **identical** results (silhouette ≈ 0.328, ARI = 0.016, NMI = 0.022
   at k=3), down to the same cluster sizes. This strongly suggests the clinical block was dominating
   the Generalised Gower distance so completely that the 110–550 image PCA columns contributed
   essentially zero signal.
4. **Two-image concatenation** (masked_tra + cor, Euclidean) — ARI still near zero.
5. **RelMS distance** (Related Metric Scaling), introduced specifically to fix the block-dominance
   problem from step 3, applied to: all 5 images merged; all 5 images + clinical (complete cases,
   n=216); each single image + clinical; and the two most promising two-image combinations
   (`masked_tra+cor`, `masked_tra+gfc_tra`), with and without clinical data. Best result:
   `masked_tra+cor+clinical`, k=4 → ARI = 0.041, NMI = 0.041 — still weak.
6. **Image-type redundancy analysis** — correlated the pairwise-patient-distance matrices of the
   five image types against each other. Most redundant pair: `cor` ↔ `gfc_sag` (r = 0.60). Most
   complementary/independent pair: `masked_tra` ↔ `sbj_sag` (r = 0.016) — meaning the native
   (unregistered) sagittal images carry the most unique structural signal, distinct from everything
   else.
7. **Leave-one-image-out sweep** — systematically removed each image type from the RelMS 5-image
   blend to see which types help vs. hurt CDR alignment. Removing `masked_tra` or `sbj_sag` tended
   to *improve* ARI/NMI slightly (they add noise more than signal in the 5-way blend), while removing
   `gfc_sag` or `gfc_tra` tended to hurt it — but all deltas were small (≤ 0.01), i.e. within noise.
8. **Full cluster profiling** (5 images + clinical, complete cases n=216) — beyond ARI/NMI, this
   notebook profiled each cluster's mean age, MMSE, brain volume (eTIV/nWBV), education, SES, and
   CDR/sex breakdown, with visualizations (boxplots, stacked CDR bars, a z-scored cluster-mean
   heatmap, 2D/3D PCA scatter, and effect-size (η²/Cramér's V) rankings of which clinical features
   actually separate the clusters). It also surfaced a second anomaly: at k=3/4 on a related Tucker
   configuration, Robust Mahalanobis produced degenerate singleton-outlier clusters (e.g. sizes
   {1, 414, 1}) with a deceptively high silhouette (~0.78) — an artifact of isolating 1–2 outliers,
   not real structure.
9. **Per-block distance sensitivity (newest addition)** — following an update from the advisor
   (`robust-mixed-dist` 0.1.27) allowing a *different* distance per quantitative block within RelMS,
   this was tested on the same 5-image + clinical setup: keeping the five image blocks on Euclidean
   while switching only the clinical block to Robust Mahalanobis, switching *all* quantitative blocks
   to Robust Mahalanobis, and switching only `masked_tra`. All four configurations were also compared
   against four alternative distance *functions* (Minkowski, Canberra, Pearson, plain Mahalanobis).
   Result: the distance choice does meaningfully change *who ends up in which cluster* (pairwise ARI
   between distance variants ranged from 0.11 to 0.98), but CDR alignment never moves outside the
   noise band already seen everywhere else (best ARI vs CDR ≈ 0.03, best NMI ≈ 0.02) — so the distance
   metric was not the bottleneck.

## Central finding

Across every method tried — single image type, merged images, Generalised Gower, RelMS, two-image
combinations, leave-one-out sweeps, and multiple distance-function variants — **clustering does not
meaningfully recover CDR groups**. ARI stays roughly in [−0.02, +0.06] and NMI in [0.01, 0.10]
throughout, i.e. barely above what random cluster assignment would produce. The best-performing
single result across the whole project was `masked_tra` alone with Euclidean distance at k=3
(ARI = 0.060). This is a genuine negative result, not a bug: the same features that separate patients
geometrically (image texture/shape via HOG+PCA) simply don't line up with the axis clinicians use
(CDR severity), and swapping distance metrics, block weightings, or image combinations doesn't
change that.

## Two things worth flagging as anomalies (not fully resolved)

1. In the Generalised Gower experiments (step 3), all image+clinical variants were numerically
   identical to the clinical-only baseline — pointing to a likely scaling issue where the clinical
   block dominates that particular distance formulation.
2. In one Tucker-decomposition configuration, Robust Mahalanobis produced degenerate singleton
   clusters with an artificially high silhouette score — a reminder that silhouette alone can be
   misleading when a method isolates a couple of extreme outliers rather than finding real structure.
