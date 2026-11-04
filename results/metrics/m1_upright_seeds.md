# T-033: Three-Seed Statistical Repeat (Main Model M1, EXIF-Upright Data)

## Overview
- **Dataset**: EXIF-upright copies in `data/processed/hasan_upright/` per D-24
- **Methodology**: For each seed (42, 43, 44), Stage 1 trains the classification head on frozen MobileNetV2 with Adam lr=1e-3 (max 20 epochs, patience 5 on val macro F1 per D-19). Stage 2 unfreezes the last 30 layers with Adam lr=1e-5 (max 30 epochs, patience 5 on val macro F1 per D-19).
- **Hardware**: CPU (oneDNN optimized)

## Summary Metrics Across Seeds (Seeds 42, 43, 44)

| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch (St2) | Train Seconds (St2) | Brown Spot -> Leaf Blast Errors |
|---|---|---|---|---|---|---|---|
| **42** | 0.8584 | **0.8149** | 0.7971 (79.71%) | 0.7246 | 12 | 866.10s | 10 |
| **43** | 0.8525 | **0.7485** | 0.7464 (74.64%) | 0.6517 | 5 | 412.68s | 8 |
| **44** | 0.8373 | **0.7933** | 0.7826 (78.26%) | 0.7018 | 17 | 1432.65s | 9 |
| **Mean** | **0.8494** | **0.7856** | **0.7754 (77.54%)** | **0.6927** | - | - | - |
| **Std (ddof=1)** | **0.0109** | **0.0339** | **0.0261** | **0.0373** | - | - | - |

## Quality Gate 2 Evaluation Across Seeds
- **Threshold**: Test Macro F1 $\ge 0.8000$
- **Seed 42**: 0.8149 (MET)
- **Seed 43**: 0.7485 (NOT MET)
- **Seed 44**: 0.7933 (NOT MET)
- **Mean Test Macro F1**: **0.7856 $\pm$ 0.0339**
- **Overall Gate 2 Status**: **NOT MET ON ALL SEEDS**

## Brown Spot to Leaf Blast Confusion Consistency
- **Baseline B2 (Frozen Base, Upright)**: 10 errors
- **Seed 42**: 10 errors
- **Seed 43**: 8 errors
- **Seed 44**: 9 errors
- **Mean Errors**: 9.00 $\pm$ 1.00

## Canonical Seed Selection (D-25)
- Selection is made strictly by **validation macro F1** per D-19 (test scores are not used for selection).
- **Canonical Model**: Seed **42** (Val Macro F1 = **0.8584**).
- Checkpoint: `results/checkpoints/m1_upright_seed42_best.keras`.
