# PROPOSED Decision D-26: 5-Fold StratifiedGroupKFold Cross-Validation Protocol

**Status**: PROPOSED (Awaiting Developer Approval — Do Not Execute Yet)  
**Date**: 2026-11-04  
**Author**: Antigravity Assistant & Developer  
**Related Decisions**: D-14 (4 classes), D-17 (group_035 exclusion), D-18 (group-level split), D-19 (val macro F1 selection), D-24 (EXIF-upright data), D-25 (canonical seed 42)

---

## 1. Context and Motivation

1. **Gate 2 Outcome on Upright Pipeline**:
   Quality Gate 2 requires a public test macro F1 $\ge 0.80$. On the EXIF-upright pipeline (D-24), evaluation across three seeds yielded:
   - Seed 42: Macro F1 = **0.8149** (Gate 2 MET)
   - Seed 43: Macro F1 = **0.7485** (Gate 2 NOT MET)
   - Seed 44: Macro F1 = **0.7933** (Gate 2 NOT MET)
   - Three-seed mean: **0.7856 $\pm$ 0.0339** (Gate 2 NOT MET overall across seeds).

2. **Test Split Exposure & Disclosure**:
   The held-out test split ($N=138$) was used during the D-24 EXIF orientation diagnostic (Condition a vs Condition b) and for repeated baseline/seed comparisons. While individual training runs did not peek at test data during optimization, evaluating multiple models on the same fixed test split can introduce optimistic estimation bias.

3. **Objective of D-26**:
   A 5-fold Stratified Group Cross-Validation protocol evaluates the model across 100% of the active dataset ($N=907$) without any single-split partitioning artifact, while maintaining zero near-duplicate leakage. It provides a robust, scientifically defensible estimate of generalization mean and variance for academic reporting.

---

## 2. Dataset and Preprocessing Specifications

* **Data Source**: Hasan et al. CC BY 4.0 (`data/processed/hasan_upright/`), oriented portrait/upright per D-24.
* **Active Images**: Exactly 907 images across 737 near-duplicate groups (`group_035` excluded per D-17; no augmented images on disk).
* **Classes (4)**: `bacterial_leaf_blight` (179), `brown_spot` (267), `healthy` (157), `leaf_blast` (304).
* **Input Resolution & Normalization**: 224x224 RGB, bilinear interpolation (half-pixel centers per TF contract), `mobilenet_v2.preprocess_input` (scaling to $[-1, 1]$).
* **Augmentation**: Training folds only per Section 8.2 (random rotation $\pm 30^\circ$, horizontal & vertical flips, random zoom $\pm 20\%$, brightness & contrast adjustments $\pm 20\%$). Zero augmentation applied to validation folds.

---

## 3. Cross-Validation Partitioning Design

* **Algorithm**: `sklearn.model_selection.StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`.
* **Grouping Variable**: `group_id` from perceptual hashing (Hamming distance $\le 5$ per D-18).
  * **Strict Zero Leakage**: All near-duplicates belonging to the same `group_id` are placed into the exact same fold. No group spans multiple folds.
* **Stratification**: Class distribution proportions are balanced across all 5 folds.
* **Artifact Output**: The fold assignments will be saved to:
  ```
  data/metadata/cv_folds.csv
  ```
  with schema: `image_id,group_id,filename,class,fold` (where `fold` $\in \{0, 1, 2, 3, 4\}$).
* **Expected Fold Sizes**: Each fold contains $\approx 181$–$182$ images ($\approx 20\%$).

---

## 4. Model Training Protocol Per Fold

For each fold $k \in \{0, 1, 2, 3, 4\}$:
1. **Split Allocation**:
   - Train set: Folds $\{j \mid j \ne k\}$ ($\approx 725$ images, 80%).
   - Validation set: Fold $k$ ($\approx 182$ images, 20%).
2. **Class Weighting**: Balanced class weights computed on the 4-fold training partition:
   $$\text{weight}_c = \frac{N_{\text{train}}}{4 \times N_{c,\text{train}}}$$
3. **Stage 1 (Head Training)**:
   - Base: MobileNetV2 (ImageNet weights, alpha 1.0, fully frozen, `training=False`).
   - Head: Dense(128, ReLU) $\rightarrow$ Dropout(0.3) $\rightarrow$ Dense(4, Softmax).
   - Optimizer: Adam, learning rate $1 \times 10^{-3}$.
   - Early Stopping & Checkpoint Selection: Monitored on fold validation macro F1 with patience 5, max 20 epochs (per D-19).
4. **Stage 2 (Fine-Tuning)**:
   - Initialized from Stage 1 best checkpoint of that fold.
   - Layers unfrozen: Last 30 layers of MobileNetV2. All BatchNormalization layers remain frozen (`training=False`, `trainable=False`).
   - Optimizer: Adam, learning rate $1 \times 10^{-5}$.
   - Early Stopping & Checkpoint Selection: Monitored on fold validation macro F1 with patience 5, max 30 epochs (per D-19).
5. **Fold Checkpoints**:
   Saved to `results/checkpoints/cv_m1_fold{k}_best.keras` (git-ignored via `*.keras`).

---

## 5. Selection and Reporting Rules

1. **Selection Rule (Strict D-19)**:
   - Within each fold, checkpoint restoration and epoch selection are governed strictly by the fold's validation macro F1.
   - No held-out test data is touched during cross-validation.
2. **Reporting Metrics Per Fold**:
   - Validation Macro F1
   - Validation Accuracy
   - Cohen's Kappa
   - Per-class Precision, Recall, and F1-Score
   - Full $4 \times 4$ Confusion Matrix
   - Brown Spot $\rightarrow$ Leaf Blast misclassification count
3. **Aggregate Reporting**:
   - Metrics saved to:
     - `results/metrics/cv_5fold_metrics.csv`
     - `results/metrics/cv_5fold_report.md`
   - Compute mean and sample standard deviation ($ddof=1$):
     $$\bar{F}_1 = \frac{1}{5} \sum_{k=0}^{4} F_{1,k}, \quad s = \sqrt{\frac{1}{4} \sum_{k=0}^{4} (F_{1,k} - \bar{F}_1)^2}$$
4. **Integration with Public Split & Final Report**:
   - The 5-fold CV results will be presented in the final project report alongside the single 70/15/15 public split.
   - This provides transparent disclosure: the single public test split measures performance on one fixed held-out set, while 5-fold CV reports variance across all 907 images under strict group stratification.

---

## 6. Execution Decision

* **Status**: **PROPOSED**.
* This draft requires explicit user approval before running any scripts or creating fold files.
