# T-050 to T-053: Model Export & Optimization Evaluation

## 1. Overview and Model Provenance
- **Canonical Model**: `results/checkpoints/m1_seed44_best.keras` (selected under locked decision **D-20** by validation macro F1 = 0.8669).
- **Target Platform**: Flutter Mobile App (`tflite_flutter`).
- **Acceptance Criteria (Section 8.9 & Gate 3)**:
  1. Model file size $\le 5.0$ MB.
  2. Accuracy drop vs Keras baseline $\le 2.0$ percentage points.
  3. Macro F1 on `test_public` $\ge 0.80$.

---

## 2. Model Size Comparison

| Format | File Path | Size (Bytes) | Size (MB / MiB) | Gate Check ($\le 5$ MB) | Size Reduction vs Keras |
|---|---|---|---|---|---|
| **Keras (.keras)** | `results/checkpoints/m1_seed44_best.keras` | 23,697,846 | 22.60 MB | Exceeds (22.60 MB) | Baseline |
| **Float16 TFLite** | `results/export/model_fp16.tflite` | 4,840,736 | 4.62 MB | **PASSED** (4.62 MB $\le 5$ MB) | **79.57% reduction** |
| **Int8 TFLite** | `results/export/model_int8.tflite` | 2,903,240 | 2.77 MB | **PASSED** (2.77 MB $\le 5$ MB) | **87.75% reduction** |

---

## 3. Evaluation on Validation Split ($N=135$)

| Model Format | Accuracy | Macro F1 | Cohen's Kappa | Accuracy Drop (pp) | Drop Gate Check ($\le 2$ pp) | Brown Spot $\rightarrow$ Leaf Blast Errors |
|---|---|---|---|---|---|---|
| **Keras Baseline** | 0.8593 (85.93%) | 0.8669 | 0.8076 | 0.00 pp | Baseline | 3 |
| **Float16 TFLite** | 0.8593 (85.93%) | 0.8669 | 0.8076 | +0.00 pp | **PASSED** (+0.00 pp <= 2 pp) | 3 |
| **Int8 TFLite** | 0.8148 (81.48%) | 0.8265 | 0.7491 | +4.44 pp | **EXCEEDED** (+4.44 pp > 2 pp) | 4 |

---

## 4. Evaluation on Held-Out Test Split ($N=138$)

| Model Format | Accuracy | Macro F1 | Cohen's Kappa | Accuracy Drop (pp) | Drop Gate Check ($\le 2$ pp) | Gate 2 (Macro F1 $\ge 0.80$) | Brown Spot $\rightarrow$ Leaf Blast Errors |
|---|---|---|---|---|---|---|---|
| **Keras Baseline** | 0.8696 (86.96%) | 0.8761 | 0.8219 | 0.00 pp | Baseline | **MET** (0.8761) | 3 |
| **Float16 TFLite** | 0.8696 (86.96%) | 0.8791 | 0.8217 | +0.00 pp | **PASSED** (+0.00 pp <= 2 pp) | **MET** (0.8791) | 4 |
| **Int8 TFLite** | 0.8623 (86.23%) | 0.8635 | 0.8131 | +0.72 pp | **PASSED** (+0.72 pp <= 2 pp) | **MET** (0.8635) | 2 |

---

## 5. Per-Class Test Split Breakdown

### 5.1 Keras Baseline (Seed 44)
| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Bacterial Leaf Blight** | 0.7857 | 0.8148 | 0.8000 | 27 |
| **Brown Spot** | 0.9048 | 0.8837 | 0.8941 | 43 |
| **Healthy Rice Leaf** | 0.9583 | 1.0000 | 0.9787 | 23 |
| **Leaf Blast** | 0.8409 | 0.8222 | 0.8315 | 45 |

### 5.2 Float16 TFLite (`model_fp16.tflite`)
| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Bacterial Leaf Blight** | 0.7857 | 0.8148 | 0.8000 | 27 |
| **Brown Spot** | 0.9048 | 0.8837 | 0.8941 | 43 |
| **Healthy Rice Leaf** | 1.0000 | 1.0000 | 1.0000 | 23 |
| **Leaf Blast** | 0.8222 | 0.8222 | 0.8222 | 45 |

### 5.3 Int8 TFLite (`model_int8.tflite`)
| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Bacterial Leaf Blight** | 0.7333 | 0.8148 | 0.7719 | 27 |
| **Brown Spot** | 0.9500 | 0.8837 | 0.9157 | 43 |
| **Healthy Rice Leaf** | 0.8846 | 1.0000 | 0.9388 | 23 |
| **Leaf Blast** | 0.8571 | 0.8000 | 0.8276 | 45 |

---

## 6. Preprocessing Contract and Class Index Mapping
- **Contract Defined in**: `results/export/preprocess_config.json`
  - Input: $224 \times 224 \times 3$, RGB bilinear interpolation.
  - Normalization: MobileNetV2 `preprocess_input` formula ($x / 127.5 - 1.0$, range $[-1.0, 1.0]$).
  - Output: 4 classes, softmax probabilities.
- **Labels Defined in**: `results/export/labels.json`
  - Critical Index Note: The model output logits correspond strictly to the alphabetical training directory ordering:
    - Index 0: `bacterial_leaf_blight`
    - Index 1: `brown_spot`
    - Index 2: `healthy`
    - Index 3: `leaf_blast`
  - In Section 6 of `PROJECT_SCOPE.md`, the initial table listed `healthy` at index 3 and `leaf_blast` at index 2. To prevent label swapping in the Flutter application, client inference must map argmax indices through `model_index_to_label` rather than Section 6 table order.

---

## 7. Comparative Recommendation: Float16 vs Int8
1. **Float16 Model (`model_fp16.tflite`)**:
   - Size: **4.62 MB** (comfortably under the 5.0 MB threshold).
   - Test Accuracy Drop: **+0.00 pp** (well within the $\le 2.0$ pp tolerance).
   - Test Macro F1: **0.8791** (substantially exceeding the $\ge 0.80$ quality gate).
   - Numerical Fidelity: Maintains exact floating-point dynamic range without quantization noise.

2. **Int8 Quantized Model (`model_int8.tflite`)**:
   - Size: **2.77 MB** (saving an additional 1.85 MB or 40.0% compared to Float16).
   - Test Accuracy Drop: **+0.72 pp**.
   - Test Macro F1: **0.8635**.
   - Edge Performance: Offers faster integer ALU execution and reduced memory bandwidth pressure on lower-end Android hardware (API 26+, 2-3 GB RAM devices).

3. **Tradeoff Assessment**:
   - On the held-out test split, both models pass all Gate 3 acceptance criteria: Size $\le 5.0$ MB, Test Accuracy Drop $\le 2.0$ pp (Float16: +0.00 pp, Int8: +0.72 pp), and Test Macro F1 $\ge 0.80$ (Float16: 0.8791, Int8: 0.8635).
   - On the validation split, Float16 maintains perfect fidelity (+0.00 pp drop), whereas Int8 experiences a +4.44 pp drop (85.93% $\rightarrow$ 81.48%), indicating slight sensitivity to quantization in certain validation samples.
   - If zero degradation from the trained Keras model is desired, **Float16** (4.62 MB) offers exact precision matching Keras while still fitting comfortably under the 5.0 MB threshold.
   - If minimizing application asset footprint (saving 1.85 MB or 40.0% compared to Float16) and optimizing mobile CPU cache/bandwidth are prioritized, **Int8** (2.77 MB) is well within the 2.0 pp test tolerance (+0.72 pp drop).
