# Confidence Calibration Report: Canonical Model (Seed 43)

> [!IMPORTANT]
> **Evaluation Protocol**: Computed strictly on the **validation split only ($N=135$)**. Test split ($N=138$) was NOT accessed for this analysis.

## 1. Overview and Decision Context
- **Model**: Canonical Model M1 (Seed 43, `m1_det_seed43_best.keras`).
- **Dataset**: EXIF-upright Hasan validation split (`data/processed/hasan_upright/`, $N=135$).
- **Confidence Threshold (D-11)**: **60% (0.60)**.
  - Predictions with confidence $\ge 0.60$: Possible condition shown; general care note displayed.
  - Predictions with confidence $< 0.60$: Trigger 'Uncertain' banner, hide advisory, and suggest expert consultation per D-11.
- **Overall Validation Accuracy**: **86.67%** (117 / 135).

---

## 2. Threshold Performance at 60% Confidence (D-11)

| Confidence Group | Condition | Count ($N$) | Fraction of Validation Set | Accuracy | Mean Confidence | Agronomic Handling (D-11) |
|---|---|:---:|:---:|:---:|:---:|---|
| **High Confidence** | Top Conf $\ge 0.60$ | **106** | **78.52%** | **91.51%** | 85.84% | Possible condition shown; general care note displayed |
| **Low Confidence (Uncertain)** | Top Conf $< 0.60$ | **29** | **21.48%** | **68.97%** | 49.60% | Uncertain banner; advisory hidden |
| **Total / Overall** | All validation samples | 135 | 100.00% | 86.67% | 78.06% | - |

### Key Observations:
1. **Filtering Efficacy**: At the 60% threshold, **78.5%** of validation predictions pass as confident. The accuracy among these predictions is **91.51%** (97/106), providing high diagnosis reliability for the user.
2. **Uncertain Warning Value**: For predictions below 60% confidence (21.5% of validation cases), empirical accuracy drops sharply to **68.97%** (20/29). Displaying the D-11 'Uncertain' banner and withholding treatment advice successfully prevents erroneous agronomic interventions on low-confidence inputs.

---

## 3. Reliability Table (5 Bins)

| Bin | Confidence Range | Sample Count ($N$) | % of Validation Split | Mean Confidence ($\bar{p}$) | Empirical Accuracy | Calibration Gap ($|\bar{p} - \text{Acc}|$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | `[0.0, 0.2)` | 0 | 0.0% | 0.00% | 0.00% | 0.00% |
| 2 | `[0.2, 0.4)` | 3 | 2.2% | 36.41% | 33.33% | 3.07% |
| 3 | `[0.4, 0.6)` | 26 | 19.3% | 51.12% | 73.08% | 21.96% |
| 4 | `[0.6, 0.8)` | 30 | 22.2% | 69.52% | 80.00% | 10.48% |
| 5 | `[0.8, 1.0]` | 76 | 56.3% | 92.29% | 96.05% | 3.76% |

- **Expected Calibration Error (ECE, 5 bins)**: **8.75%** (0.0875).

*(Note: For 4-class softmax classification, maximum class probability is bounded below by 0.25; hence bin [0.0, 0.2) naturally contains 0 samples).* 

---

## 4. Calibration Assessment Summary
- **Monotonicity**: Observed accuracy increases monotonically with confidence bin across active bins (bin [0.4, 0.6): 73.1%, bin [0.6, 0.8): 80.0%, bin [0.8, 1.0]: 96.1%).
- **Threshold Safety**: The 60% operational threshold established in D-11 cleanly separates high-reliability predictions (91.51% accuracy) from ambiguous predictions (68.97% accuracy).
