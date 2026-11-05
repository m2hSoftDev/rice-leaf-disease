# T-054: Parity Report (Canonical Seed 43 Keras vs Float16 TFLite)

## 1. Overview and Quality Gate 3 Verification
- **Keras Source Model**: `results/checkpoints/m1_det_seed43_best.keras` (Canonical Seed 43 selected under D-27 by validation macro F1 = 0.8697).
- **TFLite Deployment Model**: `results/export/model_fp16_seed43.tflite` (Float16 optimization per D-21).
- **Preprocessing Contract**: Defined in `results/export/preprocess_config.json` (RGB, 224x224 bilinear, mobilenet_v2 preprocess_input).
- **Label Contract**: Defined in `results/export/labels.json` (alphabetical class index mapping per D-22).
- **Gate 3 Criteria**:
  1. Model file size $\le 5.0$ MB $\rightarrow$ **PASSED** (4.62 MB / 4,846,980 bytes).
  2. TFLite accuracy drop vs Keras $\le 2.0$ percentage points $\rightarrow$ **PASSED** (-1.45 pp on 138-image test split).
  3. Top-1 prediction parity on 20 stratified test images $\rightarrow$ **PASSED** (20 / 20 matches, 100.0%).
- **Overall Quality Gate 3 Status**: **PASSED**.

---

## 2. Parity Table (20 Stratified Test Images, Seed 42 Selection)

| # | Filename | Ground Truth Label | Keras Top-1 Label (Conf) | Float16 TFLite Top-1 Label (Conf) | Parity Match? | Ground Truth Match? | Max Prob Diff |
|---|---|---|---|---|---|---|---|
| 1 | `Bacterial_leaf_Blight  (79).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (97.92%) | `bacterial_leaf_blight` (97.85%) | **YES** | YES | 0.000708 |
| 2 | `Bacterial_leaf_Blight  (133).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (78.06%) | `bacterial_leaf_blight` (77.89%) | **YES** | YES | 0.001773 |
| 3 | `Bacterial_leaf_Blight  (10).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (84.76%) | `bacterial_leaf_blight` (84.38%) | **YES** | YES | 0.003825 |
| 4 | `Bacterial_leaf_Blight  (89).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (81.82%) | `bacterial_leaf_blight` (81.65%) | **YES** | YES | 0.001749 |
| 5 | `Bacterial_leaf_Blight  (157).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (62.86%) | `bacterial_leaf_blight` (62.65%) | **YES** | YES | 0.002044 |
| 6 | `Brown_spot  (92).jpg` | `brown_spot` | `brown_spot` (99.59%) | `brown_spot` (99.58%) | **YES** | YES | 0.000042 |
| 7 | `Brown_spot  (170).jpg` | `brown_spot` | `leaf_blast` (51.39%) | `leaf_blast` (50.98%) | **YES** | NO | 0.004110 |
| 8 | `Brown_spot  (109).jpg` | `brown_spot` | `brown_spot` (63.88%) | `brown_spot` (64.13%) | **YES** | YES | 0.002498 |
| 9 | `Brown_spot  (244).jpg` | `brown_spot` | `brown_spot` (52.58%) | `brown_spot` (52.64%) | **YES** | YES | 0.000946 |
| 10 | `Brown_spot  (242).jpg` | `brown_spot` | `brown_spot` (92.77%) | `brown_spot` (92.78%) | **YES** | YES | 0.000153 |
| 11 | `Healthy_rice_leaf  (80).jpg` | `healthy` | `healthy` (74.62%) | `healthy` (73.90%) | **YES** | YES | 0.007145 |
| 12 | `Healthy_rice_leaf  (124).jpg` | `healthy` | `healthy` (99.92%) | `healthy` (99.91%) | **YES** | YES | 0.000054 |
| 13 | `Healthy_rice_leaf  (108).jpg` | `healthy` | `healthy` (99.99%) | `healthy` (99.99%) | **YES** | YES | 0.000007 |
| 14 | `Healthy_rice_leaf  (17).jpg` | `healthy` | `healthy` (80.49%) | `healthy` (81.15%) | **YES** | YES | 0.006602 |
| 15 | `Healthy_rice_leaf  (15).jpg` | `healthy` | `healthy` (99.57%) | `healthy` (99.53%) | **YES** | YES | 0.000311 |
| 16 | `Leaf_blast  (84).jpg` | `leaf_blast` | `bacterial_leaf_blight` (81.61%) | `bacterial_leaf_blight` (81.59%) | **YES** | NO | 0.000219 |
| 17 | `Leaf_blast  (169).jpg` | `leaf_blast` | `leaf_blast` (93.24%) | `leaf_blast` (93.23%) | **YES** | YES | 0.000095 |
| 18 | `Leaf_blast  (100).jpg` | `leaf_blast` | `bacterial_leaf_blight` (80.30%) | `bacterial_leaf_blight` (79.97%) | **YES** | NO | 0.003259 |
| 19 | `Leaf_blast  (214).jpg` | `leaf_blast` | `leaf_blast` (79.83%) | `leaf_blast` (79.66%) | **YES** | YES | 0.002543 |
| 20 | `Leaf_blast  (206).jpg` | `leaf_blast` | `leaf_blast` (56.89%) | `leaf_blast` (57.09%) | **YES** | YES | 0.001978 |

---

## 3. Summary Statistics on Stratified Sample ($N=20$)
- **Total Evaluated Images**: 20 (5 images per class, test split, seed 42 selection).
- **Top-1 Parity Matches**: **20 / 20 (100.0%)**.
- **Mismatches**: 0.
- **Max Absolute Probability Difference**: 0.007145.
- **Keras Sample Accuracy**: 17 / 20 (85.0%).
- **TFLite Sample Accuracy**: 17 / 20 (85.0%).

---

## 4. Full Public Test Split Evaluation ($N=138$)
- **Keras Test Accuracy**: 75.36% (104 / 138).
- **TFLite Test Accuracy**: 76.81% (106 / 138).
- **Accuracy Drop**: **-1.45 percentage points** (Requirement: $\le 2.0$ pp $\rightarrow$ **PASSED**).
- **Overall Top-1 Prediction Agreement**: 136 / 138 (98.55%).
- **Max Absolute Probability Difference on Test Split**: 0.030043.

---

## 5. Gate Status Conclusion
- **Gate 3 Status**: **PASSED** for model size, accuracy drop, and parity.
- **Gate 2 Status**: **NOT MET** on the five-seed mean (0.7756 ± 0.0339 across seeds 42–46). The canonical model (seed 43, val macro F1 0.8697) achieved test macro F1 0.7627. Per D-27, model is not described as validated to Gate 2.
