# Five-Seed Deterministic Statistical Evaluation (Main Model M1, Upright Data)

## Overview
- **Dataset**: EXIF-upright Hasan originals in `data/processed/hasan_upright/` (907 active images).
- **Determinism**: Enabled via `enable_determinism(seed)` (`TF_DETERMINISTIC_OPS=1`, `TF_ENABLE_ONEDNN_OPTS=0`, `tf.keras.utils.set_random_seed(seed)`, `tf.config.experimental.enable_op_determinism()`).
- **Process Isolation**: Each seed was trained end-to-end (Stage 1 + Stage 2) in an independent fresh Python subprocess.
- **Checkpoint Selection**: Strictly by validation macro F1 within each seed per D-19 (max 20 epochs for Stage 1, max 30 epochs for Stage 2, patience 5).
- **Test Evaluation**: Held-out test split ($N=138$) evaluated exactly once per seed after training concluded.

## Summary Metrics Across Five Seeds

| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch (St2) | BS -> LB Errors | Gate 2 (Test F1 >= 0.80) | Weights SHA-256 (Truncated) |
|---|---|---|---|---|---|---|---|---|
| **42** | 0.8451 | **0.7666** | 75.36% | 0.6691 | 3 | 7 | **NOT MET** | `09490419b0c11aed...` |
| **43** | 0.8697 | **0.7627** | 75.36% | 0.6622 | 1 | 7 | **NOT MET** | `1041038f95c65132...` |
| **44** | 0.8409 | **0.8008** | 79.71% | 0.7230 | 21 | 4 | **MET** | `91b0e354dc3403b5...` |
| **45** | 0.8436 | **0.8168** | 80.43% | 0.7350 | 11 | 5 | **MET** | `5fd37850168ca6fa...` |
| **46** | 0.8178 | **0.7308** | 72.46% | 0.6255 | 9 | 6 | **NOT MET** | `563e751b3cf493ec...` |
| **Mean** | **0.8434** | **0.7756** | **76.67%** | **0.6830** | - | **5.80** | **NOT MET** | - |
| **Std (ddof=1)** | **0.0184** | **0.0339** | **3.34%** | **0.0454** | - | **1.30** | - | - |

## Quality Gate 2 Evaluation
- **Threshold**: Test Macro F1 $\ge 0.8000$
- **Seed 42**: Test Macro F1 = 0.7666 (NOT MET)
- **Seed 43**: Test Macro F1 = 0.7627 (NOT MET)
- **Seed 44**: Test Macro F1 = 0.8008 (MET)
- **Seed 45**: Test Macro F1 = 0.8168 (MET)
- **Seed 46**: Test Macro F1 = 0.7308 (NOT MET)
- **Five-Seed Mean**: **0.7756 $\pm$ 0.0339**
- **Range ($1\sigma$)**: [0.7417, 0.8094]
- **Overall Gate 2 Status**: **NOT MET** (Mean is 0.7756; lower bound 0.7417 is < 0.80)

## Brown Spot to Leaf Blast Confusion Analysis
- Seed 42: 7 errors
- Seed 43: 7 errors
- Seed 44: 4 errors
- Seed 45: 5 errors
- Seed 46: 6 errors
- **Mean Errors**: 5.80 $\pm$ 1.30

## Canonical Seed Selection (Validation Macro F1 Only per D-19)
- Candidate selected strictly by highest validation macro F1 (test performance is not used for selection):
- **Canonical Seed**: **43**
- **Validation Macro F1**: **0.8697**
- **Test Macro F1**: 0.7627
- **Weights SHA-256**: `1041038f95c65132cb802d769ce15944ff7d69e7daca0fe6fd38dce2cc4f4787`
- **Checkpoint Path**: `results/checkpoints/m1_det_seed43_best.keras`
