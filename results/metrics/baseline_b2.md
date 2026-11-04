# Baseline B2: Frozen MobileNetV2 (Stage 1 Only)

## Model Configuration
- **Base Architecture**: MobileNetV2 (ImageNet pretrained, alpha 1.0, fully frozen, GlobalAveragePooling)
- **Classification Head**: Dense(128, ReLU) -> Dropout(0.3) -> Dense(4, softmax) (Section 8.3, D-14)
- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)
- **Dataset**: EXIF-upright dataset (`data/processed/hasan_upright/`) per D-24
- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)
- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-3, balanced class weights
- **Checkpoint Selection & Early Stopping**: Selected by validation macro F1 (patience 5, max 20 epochs, D-19)
- **Epochs Run**: 10 (best epoch: 5)
- **Training Time**: 465.03 seconds (7.75 min)
- **Hardware**: CPU (oneDNN optimized)

## Comparison with Baselines B0, B1, and Superseded B2

| Baseline Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |
|---|---|---|---|---|---|
| **B0 (Majority: Leaf Blast)** | 0.3407 (34.07%) | 0.1271 | 0.3261 (32.61%) | **0.1230** | 0.0000 |
| **B1 (Small CNN from Scratch)** | 0.1926 (19.26%) | 0.1012 | 0.1304 (13.04%) | **0.0669** | -0.0504 |
| **B2 (Superseded: Raw Orientation)** | 0.7630 (76.30%) | 0.7670 | 0.7101 (71.01%) | **0.7369** | 0.6051 |
| **B2 (EXIF-Upright Orientation)** | 0.8148 (81.48%) | 0.8249 | 0.7391 (73.91%) | **0.7530** | 0.6445 |

## Detailed Per-Class Breakdown (B2)

### Validation Split (N=135)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.7188 | 0.8519 | 0.7797 | 27 |
| Brown Spot | 0.9000 | 0.7105 | 0.7941 | 38 |
| Healthy Rice Leaf | 0.9200 | 0.9583 | 0.9388 | 24 |
| Leaf Blast | 0.7708 | 0.8043 | 0.7872 | 46 |
| **Macro Average** | **0.8274** | **0.8313** | **0.8249** | **135** |

### Test Split (N=138)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.6111 | 0.8148 | 0.6984 | 27 |
| Brown Spot | 0.8378 | 0.7209 | 0.7750 | 43 |
| Healthy Rice Leaf | 0.9474 | 0.7826 | 0.8571 | 23 |
| Leaf Blast | 0.6739 | 0.6889 | 0.6813 | 45 |
| **Macro Average** | **0.7676** | **0.7518** | **0.7530** | **138** |

## Confusion Matrices

### Validation Confusion Matrix (Rows=True, Cols=Pred)
```
[[23  0  0  4]
 [ 3 27  1  7]
 [ 0  1 23  0]
 [ 6  2  1 37]]
```

### Test Confusion Matrix (Rows=True, Cols=Pred)
```
[[22  0  0  5]
 [ 2 31  0 10]
 [ 0  5 18  0]
 [12  1  1 31]]
```

Figure saved to `results/figures/b2_confusion.png` (git-ignored).

## Analysis and Findings
1. Baseline B2 (EXIF-Upright Orientation, Stage 1) achieves a Test Macro F1 of 0.7530 (Accuracy: 73.91%) on the held-out test split, compared to Superseded B2 (0.7369), B0 (0.1230), and B1 (0.0669).
2. Leveraging ImageNet feature representations through a frozen backbone provides substantially superior feature extraction compared to training from scratch (B1), validating transfer learning as the foundational methodology for this dataset.
3. Selection of the best checkpoint based on validation macro F1 (D-19) prevents class-imbalanced bias and avoids premature or degraded checkpoint restoration.
4. Per D-24, all images are oriented upright according to EXIF tags before training and evaluation, establishing orientation consistency across the entire pipeline.
