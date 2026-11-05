# T-033: Three-Seed Statistical Repeat (Main Model M1, EXIF-Upright Data)

## Overview
- **Dataset**: EXIF-upright copies in `data/processed/hasan_upright/` per D-24
- **Methodology & Provenance**: 
  - Seed 42 in the three-seed summary table was **reused** directly from the upright M1 run (`results/metrics/m1.csv`, `results/metrics/m1.md`), where Stage 1 was trained under `baseline_b2.py` (best epoch 5) and Stage 2 ran under `train_m1.py` (best epoch 12, 866.10s).
  - Seeds 43 and 44 were retrained end-to-end from scratch (Stage 1 + Stage 2 in sequence) within `train_upright_seeds.py`.
  - Not all seeds were retrained from scratch in the original three-seed execution.
- **Hardware**: CPU (oneDNN optimized)

## Summary Metrics Across Seeds (Seeds 42, 43, 44)

| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch (St2) | Train Seconds (St2) | Brown Spot -> Leaf Blast Errors | Provenance |
|---|---|---|---|---|---|---|---|---|
| **42** | 0.8584 | **0.8149** | 0.7971 (79.71%) | 0.7246 | 12 | 866.10s | 10 | Reused from upright M1 run |
| **43** | 0.8525 | **0.7485** | 0.7464 (74.64%) | 0.6517 | 5 | 412.68s | 8 | Retrained end-to-end |
| **44** | 0.8373 | **0.7933** | 0.7826 (78.26%) | 0.7018 | 17 | 1432.65s | 9 | Retrained end-to-end |
| **Mean** | **0.8494** | **0.7856** | **0.7754 (77.54%)** | **0.6927** | - | - | **9.00** | - |
| **Std (ddof=1)** | **0.0109** | **0.0339** | **0.0261** | **0.0373** | - | - | **1.00** | - |

## Reproducibility Check: Seed 42 Retrained from Scratch

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
3. Per D-25 and project scope rules, the canonical model remains the original seed 42 checkpoint (`m1_best.keras`, Val Macro F1 0.8584); the rerun was executed strictly as a reproducibility diagnostic and does not alter canonical model selection.

## Quality Gate 2 Evaluation Across Seeds
- **Threshold**: Test Macro F1 $\ge 0.8000$
- **Seed 42 (Reused)**: 0.8149 (MET)
- **Seed 43**: 0.7485 (NOT MET)
- **Seed 44**: 0.7933 (NOT MET)
- **Mean Test Macro F1**: **0.7856 $\pm$ 0.0339**
- **Overall Gate 2 Status**: **NOT MET ON ALL SEEDS**
*(Note: If the seed 42 rerun of 0.7518 were used, 3-seed mean test macro F1 would be $0.7645 \pm 0.0251$, also NOT MET).*

## Brown Spot to Leaf Blast Confusion Consistency
- **Baseline B2 (Frozen Base, Upright)**: 10 errors
- **Seed 42 (Reused)**: 10 errors
- **Seed 43**: 8 errors
- **Seed 44**: 9 errors
- **Mean Errors**: 9.00 $\pm$ 1.00
*(Seed 42 rerun had 6 errors).*

## Canonical Seed Selection (D-25)
- Selection is made strictly by **validation macro F1** per D-19 (test scores are not used for selection).
- **Canonical Model**: Seed **42** (Val Macro F1 = **0.8584**).
- Checkpoint: `results/checkpoints/m1_upright_seed42_best.keras` (identical to `results/checkpoints/m1_best.keras`).
