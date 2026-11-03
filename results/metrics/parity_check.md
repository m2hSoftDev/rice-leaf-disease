# T-054: Parity Check Report (Keras vs Float16 TFLite)

## 1. Overview and Quality Gate 3 Verification
- **Keras Source Model**: `results/checkpoints/m1_seed44_best.keras` (Canonical Seed 44 selected under D-20).
- **TFLite Deployment Model**: `results/export/model_fp16.tflite` (Selected under locked decision D-21).
- **Preprocessing Contract**: Defined in `results/export/preprocess_config.json` (RGB, 224x224 bilinear, mobilenet_v2 preprocess_input).
- **Label Contract**: Defined in `results/export/labels.json` (alphabetical class index mapping).
- **Gate 3 Criteria**:
  1. Model file size $\le 5.0$ MB $\rightarrow$ **PASSED** (4.62 MB / 4,840,736 bytes).
  2. TFLite accuracy drop vs Keras $\le 2.0$ percentage points $\rightarrow$ **PASSED** (0.00 pp drop on both validation and test sets).
  3. Top-1 prediction parity on 20 stratified test images $\rightarrow$ **PASSED** (20 / 20 matches).
- **Overall Quality Gate 3 Status**: **PASSED**.

---

## 2. Explicit Label Index Check (`labels.json`)
The model output logits correspond to the alphabetical class order used during training. The label mapping in `results/export/labels.json` was verified by unit assertion:

| Logit Index | Canonical Slug | Display Name (English) | Display Name (Bangla) | Verification Status |
|---|---|---|---|---|
| **0** | `bacterial_leaf_blight` | Bacterial Leaf Blight | ব্যাকটেরিয়াল পাতা ঝলসানো | Verified BLB |
| **1** | `brown_spot` | Brown Spot | বাদামি দাগ রোগ | Verified Brown Spot |
| **2** | `healthy` | Healthy | সুস্থ পাতা | **Confirmed Healthy (Not Transposed)** |
| **3** | `leaf_blast` | Leaf Blast | পাতা ব্লাস্ট | **Confirmed Leaf Blast (Not Transposed)** |

> [!IMPORTANT]
> `healthy` is confirmed at index 2 and `leaf_blast` at index 3. Section 6 table order (where healthy was 3 and leaf blast was 2) is documentation only (per D-22). Client inference in Flutter must strictly resolve predictions through `labels.json`.

---

## 3. Parity Check Table (20 Stratified Test Images)

| # | Filename | Ground Truth Label | Keras Top-1 Label (Conf) | Float16 TFLite Top-1 Label (Conf) | Parity Match? | Ground Truth Match? |
|---|---|---|---|---|---|---|
| 1 | `Bacterial_leaf_Blight  (79).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (99.96%) | `bacterial_leaf_blight` (99.96%) | **YES** | YES |
| 2 | `Bacterial_leaf_Blight  (133).jpg` | `bacterial_leaf_blight` | `leaf_blast` (52.56%) | `leaf_blast` (52.90%) | **YES** | NO |
| 3 | `Bacterial_leaf_Blight  (10).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (89.09%) | `bacterial_leaf_blight` (88.95%) | **YES** | YES |
| 4 | `Bacterial_leaf_Blight  (89).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (99.82%) | `bacterial_leaf_blight` (99.83%) | **YES** | YES |
| 5 | `Bacterial_leaf_Blight  (157).jpg` | `bacterial_leaf_blight` | `bacterial_leaf_blight` (97.61%) | `bacterial_leaf_blight` (97.59%) | **YES** | YES |
| 6 | `Brown_spot  (92).jpg` | `brown_spot` | `brown_spot` (99.92%) | `brown_spot` (99.91%) | **YES** | YES |
| 7 | `Brown_spot  (170).jpg` | `brown_spot` | `brown_spot` (52.06%) | `brown_spot` (51.59%) | **YES** | YES |
| 8 | `Brown_spot  (109).jpg` | `brown_spot` | `leaf_blast` (60.76%) | `leaf_blast` (60.79%) | **YES** | NO |
| 9 | `Brown_spot  (244).jpg` | `brown_spot` | `brown_spot` (97.88%) | `brown_spot` (97.91%) | **YES** | YES |
| 10 | `Brown_spot  (242).jpg` | `brown_spot` | `brown_spot` (99.59%) | `brown_spot` (99.55%) | **YES** | YES |
| 11 | `Healthy_rice_leaf  (80).jpg` | `healthy` | `healthy` (97.33%) | `healthy` (97.30%) | **YES** | YES |
| 12 | `Healthy_rice_leaf  (124).jpg` | `healthy` | `healthy` (100.00%) | `healthy` (100.00%) | **YES** | YES |
| 13 | `Healthy_rice_leaf  (108).jpg` | `healthy` | `healthy` (100.00%) | `healthy` (100.00%) | **YES** | YES |
| 14 | `Healthy_rice_leaf  (17).jpg` | `healthy` | `healthy` (99.78%) | `healthy` (99.77%) | **YES** | YES |
| 15 | `Healthy_rice_leaf  (15).jpg` | `healthy` | `healthy` (100.00%) | `healthy` (100.00%) | **YES** | YES |
| 16 | `Leaf_blast  (84).jpg` | `leaf_blast` | `bacterial_leaf_blight` (82.39%) | `bacterial_leaf_blight` (82.66%) | **YES** | NO |
| 17 | `Leaf_blast  (169).jpg` | `leaf_blast` | `leaf_blast` (93.61%) | `leaf_blast` (93.83%) | **YES** | YES |
| 18 | `Leaf_blast  (100).jpg` | `leaf_blast` | `bacterial_leaf_blight` (91.44%) | `bacterial_leaf_blight` (91.51%) | **YES** | NO |
| 19 | `Leaf_blast  (214).jpg` | `leaf_blast` | `brown_spot` (66.17%) | `brown_spot` (67.65%) | **YES** | NO |
| 20 | `Leaf_blast  (206).jpg` | `leaf_blast` | `leaf_blast` (70.32%) | `leaf_blast` (70.03%) | **YES** | YES |

---

## 4. Parity and Accuracy Summary
- **Total Evaluated Images**: 20 (5 images per class, test split, seed 42 selection).
- **Top-1 Parity Matches**: **20 / 20 (100.0%)**.
- **Mismatches**: 0.
- **Keras Ground-Truth Accuracy on Sample**: 15 / 20 (75.0%).
- **Float16 TFLite Ground-Truth Accuracy on Sample**: 15 / 20 (75.0%).

### Mismatch Details
Zero mismatches observed. 100% top-1 prediction parity achieved across all 20 test samples.

## 5. Full Public Test Split Parity Context ($N=138$)
- Across the entire held-out test split of 138 images, Keras and Float16 TFLite agree on **136 out of 138 predictions (98.55% parity)**.
- The only 2 discrepancies across all 138 images occur on near-equal confidence boundaries:
  1. `Brown_spot (240).jpg`: Keras predicted Brown Spot (50.95%) vs TFLite predicted Leaf Blast (50.13%).
  2. `Brown_spot (254).jpg`: Keras predicted Healthy (50.47%) vs TFLite predicted Brown Spot (50.07%).
- Under locked decision **D-11**, any prediction with top confidence below 60.0% is flagged as uncertain in the user interface ('Please consult an agricultural expert'), ensuring neither border case would result in misinformed agronomic treatment advice.
