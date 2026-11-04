# Baseline B2: Frozen MobileNetV2 (Stage 1 Only)

## Model Configuration
- **Base Architecture**: MobileNetV2 (ImageNet pretrained, alpha 1.0, fully frozen, GlobalAveragePooling)
- **Classification Head**: Dense(128, ReLU) -> Dropout(0.3) -> Dense(4, softmax) (Section 8.3, D-14)
- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)
- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)
- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-3, balanced class weights
- **Checkpoint Selection & Early Stopping**: Selected by validation macro F1 (patience 5, max 20 epochs, D-19)
- **Epochs Run**: 9 (best epoch: 4)
- **Training Time**: 358.05 seconds (5.97 min)
- **Hardware**: CPU (oneDNN optimized)

## Comparison with Baselines B0 and B1

| Baseline Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |
|---|---|---|---|---|---|
| **B0 (Majority: Leaf Blast)** | 0.3407 (34.07%) | 0.1271 | 0.3261 (32.61%) | **0.1230** | 0.0000 |
| **B1 (Small CNN from Scratch)** | 0.1926 (19.26%) | 0.1012 | 0.1304 (13.04%) | **0.0669** | -0.0504 |
| **B2 (Frozen MobileNetV2 Stage 1)** | 0.7630 (76.30%) | 0.7670 | 0.7101 (71.01%) | **0.7369** | 0.6051 |

## Detailed Per-Class Breakdown (B2)

### Validation Split (N=135)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.5714 | 0.7407 | 0.6452 | 27 |
| Brown Spot | 0.9583 | 0.6053 | 0.7419 | 38 |
| Healthy Rice Leaf | 0.9524 | 0.8333 | 0.8889 | 24 |
| Leaf Blast | 0.7273 | 0.8696 | 0.7921 | 46 |
| **Macro Average** | **0.8024** | **0.7622** | **0.7670** | **135** |

### Test Split (N=138)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.6061 | 0.7407 | 0.6667 | 27 |
| Brown Spot | 1.0000 | 0.5116 | 0.6769 | 43 |
| Healthy Rice Leaf | 0.9565 | 0.9565 | 0.9565 | 23 |
| Leaf Blast | 0.5667 | 0.7556 | 0.6476 | 45 |
| **Macro Average** | **0.7823** | **0.7411** | **0.7369** | **138** |

## Confusion Matrices

### Validation Confusion Matrix (Rows=True, Cols=Pred)
```
[[20  0  0  7]
 [10 23  0  5]
 [ 0  1 20  3]
 [ 5  0  1 40]]
```

### Test Confusion Matrix (Rows=True, Cols=Pred)
```
[[20  0  0  7]
 [ 2 22  1 18]
 [ 0  0 22  1]
 [11  0  0 34]]
```

Figure saved to `results/figures/b2_confusion.png` (git-ignored).

## Analysis and Findings
1. Baseline B2 (Frozen MobileNetV2 Stage 1) achieves a Test Macro F1 of 0.7369 (Accuracy: 71.01%) on the held-out test split, evaluated against B0 (0.1230) and B1 (0.0669).
2. Leveraging ImageNet feature representations through a frozen backbone provides substantially superior feature extraction compared to training from scratch (B1), validating transfer learning as the foundational methodology for this dataset.
3. Selection of the best checkpoint based on validation macro F1 (D-19) prevents class-imbalanced bias and avoids premature or degraded checkpoint restoration.
