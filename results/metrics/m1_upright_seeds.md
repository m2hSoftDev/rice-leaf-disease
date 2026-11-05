# T-033: Three-Seed Statistical Repeat (Main Model M1, EXIF-Upright Data)

> [!WARNING]
> **SUPERSEDED BY DETERMINISTIC PIPELINE (D-27)**:
> The three-seed upright results in this document—including the reused seed 42 result (test macro F1 0.8149) and the rerun (test macro F1 0.7518)—are **SUPERSEDED** by the five-seed deterministic statistical evaluation in [`results/metrics/m1_det_seeds.md`](file:///i:/University_Projects/Rice%20Leaf%20Disease/results/metrics/m1_det_seeds.md) (where seed 42 test macro F1 is 0.7666, and canonical seed 43 val macro F1 is 0.8697 / test macro F1 is 0.7627).
> **Reason**: The earlier runs were not produced under the full deterministic pipeline (`TF_DETERMINISTIC_OPS=1`, `TF_ENABLE_ONEDNN_OPTS=0`, `tf.keras.utils.set_random_seed()`, and `enable_op_determinism()`). These historical files are preserved for provenance tracking and reproducibility audit.

## Overview
- **Dataset**: EXIF-upright copies in `data/processed/hasan_upright/` per D-24
- **Methodology & Provenance**: 
  - Seed 42 in the three-seed summary table was **reused** directly from the upright M1 run (`results/metrics/m1.csv`, `results/metrics/m1.md`), where Stage 1 was trained under `baseline_b2.py` (best epoch 5) and Stage 2 ran under `train_m1.py` (best epoch 12, 866.10s).
  - Seeds 43 and 44 were retrained end-to-end from scratch (Stage 1 + Stage 2 in sequence) within `train_upright_seeds.py`.
  - Not all seeds were retrained from scratch in the original three-seed execution.
- **Hardware**: CPU (oneDNN optimized)

## Summary Metrics Across Seeds (Seeds 42, 43, 44) [SUPERSEDED]

| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch (St2) | Train Seconds (St2) | Brown Spot -> Leaf Blast Errors | Provenance | Status |
|---|---|---|---|---|---|---|---|---|---|
| **42** | 0.8584 | **0.8149** | 0.7971 (79.71%) | 0.7246 | 12 | 866.10s | 10 | Reused from upright M1 run | **SUPERSEDED** by `m1_det_seeds` |
| **43** | 0.8525 | **0.7485** | 0.7464 (74.64%) | 0.6517 | 5 | 412.68s | 8 | Retrained end-to-end | **SUPERSEDED** by `m1_det_seeds` |
| **44** | 0.8373 | **0.7933** | 0.7826 (78.26%) | 0.7018 | 17 | 1432.65s | 9 | Retrained end-to-end | **SUPERSEDED** by `m1_det_seeds` |
| **Mean** | **0.8494** | **0.7856** | **0.7754 (77.54%)** | **0.6927** | - | - | **9.00** | - | **SUPERSEDED** |
| **Std (ddof=1)** | **0.0109** | **0.0339** | **0.0261** | **0.0373** | - | - | **1.00** | - | - |

## Reproducibility Check: Seed 42 Retrained from Scratch [SUPERSEDED]

To test end-to-end reproducibility, seed 42 was retrained from scratch through both Stage 1 and Stage 2 in sequence without reusing the `b2_best.keras` checkpoint.
- **Artifacts**: Checkpoint saved to `results/checkpoints/m1_seed42_rerun.keras` (git-ignored); metrics saved to `results/metrics/m1_seed42_rerun.csv`.
- **Rerun Results vs Reused Metrics**:

| Metric | Reused Seed 42 (`m1.csv`) | Seed 42 Rerun from Scratch (`m1_seed42_rerun.csv`) | Difference |
|---|---|---|---|
| **Validation Macro F1** | 0.8584 | 0.8349 | -0.0235 |
| **Test Macro F1** | 0.8149 | 0.7518 | -0.0631 |
| **Test Accuracy** | 0.7971 (79.71%) | 0.7391 (73.91%) | -5.80 pp |
| **Test Cohen's Kappa** | 0.7246 | 0.6514 | -0.0732 |
| **Best Epoch (Stage 2)** | 12 | 5 | -7 epochs |
| **Stage 2 Train Seconds** | 866.10s | 436.12s | -429.98s |
| **Brown Spot -> Leaf Blast Errors** | 10 | 6 | -4 errors |

### Reproducibility Findings
1. The rerun does **not** match the reused seed 42 metrics exactly (Test Macro F1 diff: -0.0631; Val Macro F1 diff: -0.0235).
2. **Root Cause**: The reused seed 42 run trained Stage 2 in an independent process (`train_m1.py`) starting from the `b2_best.keras` checkpoint (best epoch 5, val macro F1 0.8249) with a fresh global seed 42. In contrast, the continuous end-to-end rerun trained Stage 1 to epoch 13 (best epoch 8, val macro F1 0.8428), and Stage 2 inherited an advanced RNG state, leading to earlier early stopping at epoch 5.
3. Both of these runs are **SUPERSEDED** by the deterministic five-seed run (`results/metrics/m1_det_seeds.md`), where full determinism (`TF_DETERMINISTIC_OPS=1`, `TF_ENABLE_ONEDNN_OPTS=0`, `enable_op_determinism()`) is enforced and seed 42 achieves test macro F1 0.7666. Per D-27, Seed 43 is canonical.

## Quality Gate 2 Evaluation Across Seeds
- **Threshold**: Test Macro F1 $\ge 0.8000$
- **Seed 42 (Reused)**: 0.8149 (MET) [SUPERSEDED]
- **Seed 43**: 0.7485 (NOT MET) [SUPERSEDED]
- **Seed 44**: 0.7933 (NOT MET) [SUPERSEDED]
- **Mean Test Macro F1**: **0.7856 $\pm$ 0.0339** [SUPERSEDED]
- **Overall Gate 2 Status**: **NOT MET ON ALL SEEDS**

## Brown Spot to Leaf Blast Confusion Consistency
- **Baseline B2 (Frozen Base, Upright)**: 10 errors
- **Seed 42 (Reused)**: 10 errors [SUPERSEDED]
- **Seed 43**: 8 errors [SUPERSEDED]
- **Seed 44**: 9 errors [SUPERSEDED]
- **Mean Errors**: 9.00 $\pm$ 1.00 [SUPERSEDED]

## Canonical Seed Selection (D-25 / D-27)
- D-25 selection of Seed 42 is **SUPERSEDED** by D-27 (Seed 43 selected under deterministic pipeline).
