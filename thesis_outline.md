# Thesis Outline — Working Document

This is a chapter-by-chapter skeleton, not thesis text. Each section lists what should
go there, which notebook/file it comes from, and the exact figures/numbers already
available so you don't have to go hunting. Fill in the prose yourself; delete/reorder
sections as you see fit.

**📁 Folder structure note**: the project was reorganized since this outline was first
written. Everything now lives under `notebooks/`, split into five clearly-labeled
folders instead of one flat `new_results_with_padding/` directory:

| Folder | Contents |
|---|---|
| `notebooks/01_data_pipeline/` | Notebooks 01–03 (HOG extraction → per-image PCA → merge) + the shared `pca_*.csv` / clinical xlsx / raw HOG CSV they produce and everything downstream reads |
| `notebooks/02_final_results/` | Notebooks 18–19 (the flagship RelMS method) + both compiled reports (`thesis_full_report.tex/.pdf`, `clustering_report.tex/.pdf`) + all their figures/results |
| `notebooks/03_other_experiments/` | Notebooks 04–11, 16 + their outputs |
| `notebooks/04_alternative_approaches/` | Notebooks 12–15, 17 (Tucker/two-stage PCA — didn't beat the baseline) |
| `notebooks/unsorted_legacy/` | Orphaned output files with no matching current notebook |

All 19 notebooks' internal paths were fixed to work from these new locations
(no more hardcoded machine-specific paths), and this has been verified by actually
re-running several of them end to end. `thesis_full_report.tex`'s stale figure
references (from an earlier, since-rebuilt version of notebook 19) have also already
been fixed — the report is current and compiles cleanly.

---

## 1. Introduction

**What goes here:**
- The question: can unsupervised clustering of brain MRI + clinical data recover
  clinically meaningful patient subgroups (specifically, groups aligned with CDR —
  Clinical Dementia Rating)?
- Why this matters (unsupervised discovery vs. supervised diagnosis; OASIS-1 as a
  public benchmark).
- One paragraph previewing the actual finding: the clustering reliably finds real,
  large, reproducible structure, it's just organised around sex and brain volume
  rather than CDR — a "mismatch of axes," not an absence of structure.
- Optional: the parallel to your advisor's Gaza-conflict polarization paper (same
  clustering toolkit — Robust Mahalanobis / Generalised Gower / RelMS /
  SampleDistClustering — applied to a different domain).

**Sources:** `notebooks/02_final_results/thesis_full_report.tex` §Introduction already
has a full draft paragraph you can adapt. `thesis_project_summary.md` (project root)
has a shorter version for the abstract.

---

## 2. Related Work / Methodological Framework

**What goes here:**
- Brief background on unsupervised clustering for neuroimaging / dementia staging
  (you'll want 2-3 citations here — not something I can supply).
- Introduce the distance-metric family used throughout, in order of sophistication:
  - **Robust Mahalanobis** — single quantitative block, outlier-resistant
  - **Generalised Gower (G-Gower)** — mixes quantitative + binary + categorical blocks
  - **Related Metric Scaling (RelMS)** — combines several *typed* blocks (e.g. 5 image
    types), each rescaled by its own geometric variability before combining
  - **SampleDistClustering / FasterPAM k-medoids** — the clustering engine
- Cite the package: `robust_mixed_dist` / `db_robust_clust` (Fabio Scielzo-Ortiz,
  your advisor). If you want to explicitly reference the Gaza-polarization paper as a
  sibling application, this is the place.

**Sources:** `notebooks/02_final_results/thesis_full_report.tex` §Clustering
Methodology.

---

## 3. Data and Preprocessing

**What goes here:**
- OASIS-1 dataset: 416 subjects, CDR scale (0/0.5/1/2), 235 of 416 have known CDR.
- Five MRI planes per patient: `cor`, `gfc_sag`, `gfc_tra`, `masked_tra`, `sbj_sag` —
  describe what each one is (registered vs. native space, masked vs. not).
- HOG feature extraction: padding → resize 128×128 → HOG (9 orientations, 8×8 cells,
  2×2 blocks) → 8,100 features/image, 40,500/patient.
- Per-image PCA: two-pass strategy → unified 110 components/type.
- Clinical variables: Age, M/F, Education, SES, MMSE, eTIV, nWBV, ASF. Complete-case
  filtering (drop missing Educ/SES/MMSE, no imputation) → **n=216**.
- **Worth one paragraph**: the padding fix. Earlier work resized images to square
  without preserving aspect ratio, distorting them before HOG extraction. This was
  corrected before any of the current notebooks 01–19 work began — a concrete,
  citable data-quality correction.

**Sources:** `notebooks/01_data_pipeline/01_raw_hog_features_per_image.ipynb`,
`02_pca_per_image_new_method.ipynb`, `03_pca_per_image_merged_clustering.ipynb`.
`notebooks/02_final_results/thesis_full_report.tex` §Data and Preprocessing.

---

## 4. Methodological Evolution (short, optional but recommended — ~1 page)

**What goes here**, to preempt "didn't an earlier version of this work show a positive
result?":
- Era 1 (`files_before_the_final_version_of_thesis/method_1_HOG_PCA`,
  `method_2_Pixel_PCA`): plain scripts, HOG features **averaged across all 5 image
  types** into a single PCA vector, basic k-medoids. Your project's own `README.md`
  reports what looks like a clean dementia gradient from this era (Cluster 3: 45%
  healthy vs. Cluster 0: 93% healthy, k=4).
- Era 2 (`files_before_the_final_version_of_thesis/old_results_no_padding/`): moved to
  per-image-type features, but without the aspect-ratio-preserving padding fix.
- Era 3 (`notebooks/01_data_pipeline/` through `04_alternative_approaches/` —
  the rest of this thesis): padding fixed, per-image-type features kept separate (not
  averaged), progressively more rigorous distance/clustering framework built up
  specifically because earlier, simpler configurations (see §5) kept producing
  artifacts rather than real structure.
- **The honest framing**: the apparent "positive" result in Era 1 was produced by a
  pipeline with none of the safeguards later found necessary (no per-type separation,
  no aspect-ratio correction, no robust distance handling, no leave-one-out or
  redundancy validation). This section is what justifies why the thesis doesn't stop
  at Era 1's seemingly good numbers.

**Sources:** `README.md` (root — note: still describes the Era 1 pipeline and needs a
rewrite before anyone reads it expecting the current methodology),
`files_before_the_final_version_of_thesis/`. No notebook-based results to cite here —
this is prose framing, not a results table.
**Decision for you**: how much of Era 1/2 to show. I'd suggest a single summary
paragraph, not full tables/figures from that era, unless your advisor wants to see it.

---

## 5. Core Experiments

### 5.1 Single-image-type and merged-image clustering
- Notebook 04 (merged 5 images, 550 features, Euclidean vs. Robust Mahalanobis) and
  notebook 05 (each of the 5 image types alone, same two distances, k=3/4 — 20
  combinations). Both in `notebooks/03_other_experiments/`.
- **Headline number**: best single result in the *entire* project —
  `masked_tra`, Euclidean, k=3: ARI=0.060, NMI=0.085.
- Table source: `notebooks/03_other_experiments/results_single_image.csv`,
  `results_all_images_merged.csv`.
- Point worth making: merging all 5 images performs *worse* than the single best type
  alone — early evidence that naive concatenation dilutes rather than reinforces signal.

### 5.2 Clinical + imaging fusion, and the Generalised Gower anomaly
- Notebook 06 (`notebooks/03_other_experiments/`): all-images-merged, each single
  image type, and clinical-only, all fused with 8 clinical variables via Generalised
  Gower.
- **The anomaly**: every image-inclusive variant produced numerically identical
  results to the clinical-only baseline (same silhouette, ARI, NMI, cluster sizes to
  4 decimal places) — strong evidence the clinical block was completely dominating the
  distance under this configuration.
- Table source: `notebooks/03_other_experiments/results_combined_clinical_image.csv`.
- This anomaly is *why* RelMS gets introduced next — make that causal link explicit.

### 5.3 Two-image concatenation (bridge experiment)
- Notebook 07 (`notebooks/03_other_experiments/`): `masked_tra`+`cor`, Euclidean, no
  block reweighting.
- Figure: `notebooks/03_other_experiments/elbow_masked_tra_cor_euclidean.png`.
- Still near zero; motivates block-aware distance combination (RelMS) rather than
  plain concatenation.

### 5.4 RelMS: the fix for block dominance
- Notebooks 08 (5 images, no clinical), 09 (5 images + clinical, first pass), 11 (best
  2-image combos, with/without clinical) — all in `notebooks/03_other_experiments/`.
- RelMS rescales each declared block by its own geometric variability before
  combining — directly targets the §5.2 anomaly.
- Table sources (all in `notebooks/03_other_experiments/`):
  `results_new_distance_5images.csv`, `results_combined_clinical_image_new.csv`,
  `results_best_image_combinations.csv`, `results_pair_clinical_profiling.csv`,
  `results_recommended_pairs_profiling.csv`.
- Best RelMS result: `masked_tra+cor+clinical`, k=4: ARI=0.041, NMI=0.041 — better than
  plain concatenation, still weak.

### 5.5 Image-type redundancy and leave-one-out (pair these two together)
- Notebook 10 (`notebooks/03_other_experiments/`): correlated the pairwise-patient-
  distance matrices of the 5 image types. Most redundant pair: `cor`↔`gfc_sag`
  (r=0.598). Most independent/complementary pair: `masked_tra`↔`sbj_sag` (r=0.016).
  Figure: `notebooks/03_other_experiments/image_correlation_heatmap.png`.
- Notebook 16 (`notebooks/03_other_experiments/`): systematically removed each image
  type from the 5-image RelMS blend. Removing `masked_tra`/`sbj_sag` tends to help
  slightly; removing `gfc_sag`/`gfc_tra` tends to hurt slightly — consistent with the
  redundancy finding, but all deltas small (≤0.007), within noise.
  Table source: `notebooks/03_other_experiments/results_leave_one_out.csv`.
- Nice self-contained subsection: "which images carry unique information, and does
  removing the redundant ones actually help?" (Answer: marginally, not meaningfully.)

**Sources for this whole section**:
`notebooks/02_final_results/thesis_full_report.tex` §Experiments and Results already
has full prose + tables for 5.1–5.5 — this is your most reusable existing draft.

---

## 6. Flagship Analysis: Full Cluster Profiling

**What goes here** — this should be your main results chapter, most detailed section:
- Notebook 18 (`notebooks/02_final_results/`), four configurations, all on the same
  n=216 cohort:
  1. All 5 images + clinical (558 features)
  2. Clinical only (8 features)
  3. Images only (550 features)
  4. Best 2-image combo (`cor`+`gfc_sag`) + clinical (228 features)
- For each: optimal-k selection (elbow/silhouette/Davies-Bouldin), cluster profiling
  tables (mean±std per feature per cluster, CDR/sex/education/SES breakdowns),
  visualizations, PCA scatter (2D/3D), and — the analytical core — effect-size
  (η²/Cramér's V) rankings of which clinical features actually drive each clustering.
- **Key figures** (all in `notebooks/02_final_results/`):
  `k_selection_criteria.png`, `cluster_profile_k2.png`, `cluster_profile_k3.png`,
  `cluster_profile_heatmap.png`, `cluster_cdr_detail.png`,
  `cluster_pca_separation_n216.png`, `pca_3d_full_k3.png`, `silhouette_diagrams.png`,
  `clinical_only_profile_k2/k3.png`, `clinical_only_pca_scatter.png`,
  `pca_3d_clinical_k3.png`, `img_only_profile_k2/k3.png`, `img_only_pca_scatter.png`,
  `best_combo_profile_k2/k3.png`, `best_combo_pca_scatter.png`,
  `pca_3d_best_combo_k3.png`, **`feature_separation_eta2.png`** (the "money plot" —
  probably your single most important figure).
- Table source: `notebooks/02_final_results/results_cluster_profiling.csv`.
- **The headline finding to state explicitly**: effect sizes show sex (M/F) and eTIV
  (brain volume, largely reflecting head size) are consistently the strongest cluster
  differentiators — *not* MMSE, Age, or anything CDR-adjacent. That's the mechanistic
  explanation for why ARI/NMI stay near zero everywhere: the clusters are real, just
  organized around a different axis than disease severity.

**Sources:** `notebooks/02_final_results/clustering_report.tex/.pdf` is a full,
ready-made draft of exactly this chapter (17 figures, full tables) — this is your best
existing scaffold, probably needs the least rewriting of anything in this outline.

---

## 7. Distance-Sensitivity Follow-up (the package update)

**What goes here** — this documents your response to the advisor's `robust-mixed-dist`
0.1.27 update (per-quantitative-block `d1`):
- Notebook 19 (`notebooks/02_final_results/`, current version): **exact structural
  mirror of notebook 18** — same four configurations, same section titles, same
  profiling depth — rebuilt on 0.1.27, with the rule "images always Euclidean,
  clinical block always Robust Mahalanobis wherever a clinical block exists"
  (images-only is untouched, since it has no clinical block).
- Figures (all in `notebooks/02_final_results/`):
  `updated_cluster_profile_k2/k3.png`, `updated_cluster_profile_heatmap.png`,
  `updated_cluster_cdr_detail.png`, `updated_cluster_pca_separation_n216.png`,
  `updated_pca_3d_full_k3.png`, `updated_k_selection_criteria.png`,
  `updated_silhouette_diagrams.png`, `updated_clinical_only_profile_k2/k3.png`,
  `updated_clinical_only_pca_scatter.png`, `updated_pca_3d_clinical_k3.png`,
  `updated_img_only_profile_k2/k3.png`, `updated_img_only_pca_scatter.png`,
  `updated_best_combo_profile_k2/k3.png`, `updated_best_combo_pca_scatter.png`,
  `updated_pca_3d_best_combo_k3.png`, `updated_feature_separation_eta2.png`.
- Table source: `notebooks/02_final_results/updated_results_cluster_profiling.csv`.
- **Result to report plainly**: Robust Mahalanobis on the clinical block made 3 of 4
  configurations *worse* at matching CDR and left images-only unchanged (no clinical
  block to affect). The one apparent improvement (clinical-only, k=3) is small enough
  to be noise.
- **The diagnostic finding worth a paragraph**: `eTIV` and `ASF` are correlated at
  **r=−0.99** in this cohort (ASF is essentially a mathematical rescaling of eTIV) —
  the clinical block's correlation matrix is nearly singular (smallest eigenvalue
  0.010 vs. largest 2.26). Robust Mahalanobis inverts that correlation structure,
  which amplifies noise along the near-duplicate eTIV/ASF direction. A follow-up check
  showed Robust Mahalanobis *does* give MMSE (the clinically-relevant variable) far
  more influence over the resulting clusters than Euclidean does (η² 0.093 vs. 0.017 at
  k=3) — the update is doing something real and defensible — it just isn't enough to
  overcome the underlying absence of CDR signal.
- **This is a good place to state your overall verdict on distance choice**: not the
  bottleneck. The absence of CDR-discriminative signal in the underlying features is.

**Sources:** `notebooks/02_final_results/thesis_full_report.tex` §Per-Block Distance
Update now has a full draft of this section already (including an old-vs-new
comparison table across all four notebook 18 configurations, and the feature-
comparison figures) — this is a reusable source now, even though notebook 19 itself
only contains the "new" side of that comparison (the four updated configurations on
their own, not literally paired with the old ones in the same notebook).

---

## 8. Discussion

**What goes here** — tie every section above together:
- Restate the central finding: across every configuration tried (19 notebooks, every
  distance metric, every image combination, every block-assignment strategy), the
  clustering recovers real, large, reproducible structure — just not structure that
  aligns with CDR. ARI stays in roughly [−0.02, +0.06], NMI in [0.01, 0.10] against
  CDR specifically.
- The mechanistic explanation from §6: clusters are organized around sex and brain
  volume (and sometimes education/SES), not dementia-relevant variables.
- The §7 finding that distance-metric choice isn't the lever either — it can shift
  which features get more influence, but not enough to recover CDR alignment.
- The §4 framing: earlier, less careful methodology suggested a signal that more
  rigorous methodology dissolved — a cautionary methodological point in its own right,
  and arguably a contribution independent of the substantive result.
- Optional: brief callback to the Gaza-polarization paper as a contrasting case where
  the same toolkit succeeded — what was different (validated, low-dimensional,
  domain-expert-chosen features vs. generic HOG descriptors)?

---

## 9. Limitations and Future Work

**Candidates to include:**
- Small sample after complete-case filtering (n=216 of 416) — clinical-variable
  imputation instead of dropping could be explored.
- OASIS-1 is cross-sectional — no longitudinal signal to exploit.
- HOG is a generic, texture/edge-oriented descriptor; it was never designed for
  neuroanatomical structure — a purpose-built feature extractor (e.g. a pretrained
  medical-imaging CNN, or segmentation-based volumetric features per brain region)
  might carry more CDR-relevant signal than HOG+PCA does.
- Tucker decomposition and two-stage PCA (notebooks 12–15, 17, in
  `notebooks/04_alternative_approaches/`) were explored as alternative
  dimensionality-reduction strategies; neither beat the HOG+PCA baseline, and
  notebook 15 surfaced a genuine implementation bug (Tucker rank misuse on the
  patient axis, fixed in notebook 17) — worth a paragraph as "we tried this, it didn't
  help, here's why," possibly in an appendix rather than main text.
- The eTIV/ASF collinearity finding (§7) suggests future block-distance work should
  first check for near-duplicate variables within a block before choosing Mahalanobis-
  family distances.

---

## Appendix candidates

- Full notebook 05 table (all 20 single-image-type combinations) if you don't want it
  in-body.
- Notebooks 12–15, 17 (`notebooks/04_alternative_approaches/`, Tucker/two-stage PCA) —
  condensed: setup, headline table (`results_two_stage_pca_mahalanobis.csv`,
  `results_tucker_clustering.csv`, `results_tucker_clustering_fixed.csv`), and the
  nb15→nb17 bug-fix story.
- Reproducibility appendix: package versions (`robust-mixed-dist==0.1.26` for
  notebooks 01–18, `==0.1.27` for notebook 19), full pipeline folder structure (see
  the table at the top of this document).

---

## Open decisions only you can make

1. **How much of Era 1/2 (§4) to show** — one paragraph (recommended) vs. a full
   subsection with their old tables/figures.
2. **Tucker/two-stage PCA (§9 / appendix)** — condensed mention vs. full appendix
   vs. cut entirely. The bug-and-fix story (nb15→nb17) is a nice rigor anecdote if
   your advisor likes seeing that kind of debugging transparency.
3. **How prominently to feature the Gaza-polarization paper** — as a one-line
   methodological citation, or as an explicit "contrasting case study" woven through
   the discussion.
4. **Chapter vs. section granularity** — the outline above assumes §5 alone might be
   3-4 subsections; you may want to split it into two chapters ("Preliminary
   Experiments" and "Methodology Refinement") depending on your program's expected
   thesis length.
5. **`README.md` is still stale** (flagged in §4 above) — it describes the Era 1
   averaged-HOG pipeline and the old flat file layout, not the current notebook
   structure. Worth a full rewrite before anyone (professor included) opens the repo
   expecting it to match what's actually there.
