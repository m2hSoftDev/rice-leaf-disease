# Main Model M1: Stage 2 Fine-Tuned MobileNetV2

## Model Configuration
- **Base Checkpoint**: Initialized from `results/checkpoints/b2_best.keras` (B2 epoch 4, val_macro_f1=0.7670, D-19)
- **Unfreezing Policy**: Last 30 layers unfrozen (BatchNorm frozen, base called with `training=False`)
- **Trainable Parameters**: 1,675,204 (increased from 164,484)
- **Non-Trainable Parameters**: 747,264
- **Total Parameters**: 2,422,468
- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)
- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)
- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-5, balanced class weights
- **Checkpoint Selection & Early Stopping**: Selected by validation macro F1 (patience 5, max 30 epochs, D-19)
- **Epochs Run**: 26 (best epoch: 21)
- **Training Time**: 1459.66 seconds (24.33 min)
- **Hardware**: CPU (oneDNN optimized)

## Gate 2 Evaluation (Threshold: Test Macro F1 >= 0.80)
- **Gate 2 Status**: **MET**
- **Test Macro F1**: **0.8534** (Target: 0.8000)
- **Test Accuracy**: **0.8333 (83.33%)**
- **Test Cohen's Kappa**: **0.7730**

## Comparison with Baselines B0, B1, and B2

| Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |
|---|---|---|---|---|---|
| **B0 (Majority: Leaf Blast)** | 0.3407 (34.07%) | 0.1271 | 0.3261 (32.61%) | **0.1230** | 0.0000 |
| **B1 (Small CNN from Scratch)** | 0.1926 (19.26%) | 0.1012 | 0.1304 (13.04%) | **0.0669** | -0.0504 |
| **B2 (Frozen MobileNetV2 Stage 1)** | 0.7630 (76.30%) | 0.7670 | 0.7101 (71.01%) | **0.7369** | 0.6051 |
| **M1 (Fine-Tuned MobileNetV2 Stage 2)** | 0.8519 (85.19%) | 0.8561 | 0.8333 (83.33%) | **0.8534** | 0.7730 |

## Detailed Per-Class Breakdown (M1)

### Validation Split (N=135)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.7188 | 0.8519 | 0.7797 | 27 |
| Brown Spot | 0.8788 | 0.7632 | 0.8169 | 38 |
| Healthy Rice Leaf | 0.9583 | 0.9583 | 0.9583 | 24 |
| Leaf Blast | 0.8696 | 0.8696 | 0.8696 | 46 |
| **Macro Average** | **0.8564** | **0.8607** | **0.8561** | **135** |

### Test Split (N=138)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.7500 | 0.8889 | 0.8136 | 27 |
| Brown Spot | 0.9697 | 0.7442 | 0.8421 | 43 |
| Healthy Rice Leaf | 1.0000 | 1.0000 | 1.0000 | 23 |
| Leaf Blast | 0.7200 | 0.8000 | 0.7579 | 45 |
| **Macro Average** | **0.8599** | **0.8583** | **0.8534** | **138** |

## Confusion Matrices

### Validation Confusion Matrix (Rows=True, Cols=Pred)
```
[[23  1  0  3]
 [ 6 29  0  3]
 [ 0  1 23  0]
 [ 3  2  1 40]]
```

### Test Confusion Matrix (Rows=True, Cols=Pred)
```
[[24  0  0  3]
 [ 0 32  0 11]
 [ 0  0 23  0]
 [ 8  1  0 36]]
```

Figure saved to `results/figures/m1_confusion.png` (git-ignored).

## Brown Spot to Leaf Blast Confusion Analysis
- Total Brown Spot test images: 43
- Correctly identified Brown Spot: 32 (Recall: 74.42%)
- Total missed Brown Spot images: 11
- Misclassified as Leaf Blast in M1: **11** images (100.00% of missed Brown Spot)
- Comparison with Baseline B2: B2 had **18** Brown Spot -> Leaf Blast errors (M1 count: **11**).

## Analysis and Findings
1. Stage 2 fine-tuning achieved Test Macro F1 of 0.8534 (Accuracy: 83.33%) on held-out test data.
2. Quality Gate 2 (Macro F1 >= 0.80) is **MET**.
3. Selection by validation macro F1 (D-19) strictly guarded against test leakage and balanced performance across all four classes.
