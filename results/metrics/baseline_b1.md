# Baseline B1: Small CNN from Scratch

## Model Configuration
- **Architecture**: 3 Convolutional Blocks (Conv2D -> BatchNorm -> ReLU -> MaxPool) + GAP + Dense(128) + Dropout(0.3) + Dense(4, softmax)
- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)
- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)
- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-3, balanced class weights
- **Stopping & Checkpoint**: Early stopping on `val_loss` (patience 5, max 40 epochs); best checkpoint restored
- **Epochs Run**: 6 (best epoch: 1)
- **Training Time**: 644.53 seconds (10.74 min)
- **Hardware**: CPU (oneDNN optimized)

## Comparison with Baseline B0

| Baseline Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |
|---|---|---|---|---|---|
| **B0 (Majority: Leaf Blast)** | 0.3407 (34.07%) | 0.1271 | 0.3261 (32.61%) | **0.1230** | 0.0000 |
| **B1 (Small CNN from Scratch)** | 0.1926 (19.26%) | 0.1012 | 0.1304 (13.04%) | **0.0669** | -0.0504 |

## Detailed Per-Class Breakdown (B1)

### Validation Split (N=135)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.0000 | 0.0000 | 0.0000 | 27 |
| Brown Spot | 0.5000 | 0.0526 | 0.0952 | 38 |
| Healthy Rice Leaf | 0.1832 | 1.0000 | 0.3097 | 24 |
| Leaf Blast | 0.0000 | 0.0000 | 0.0000 | 46 |
| **Macro Average** | **0.1708** | **0.2632** | **0.1012** | **135** |

### Test Split (N=138)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.0000 | 0.0000 | 0.0000 | 27 |
| Brown Spot | 0.2500 | 0.0233 | 0.0426 | 43 |
| Healthy Rice Leaf | 0.1328 | 0.7391 | 0.2252 | 23 |
| Leaf Blast | 0.0000 | 0.0000 | 0.0000 | 45 |
| **Macro Average** | **0.0957** | **0.1906** | **0.0669** | **138** |

## Confusion Matrices

### Validation Confusion Matrix (Rows=True, Cols=Pred)
```
[[ 0  0 27  0]
 [ 0  2 36  0]
 [ 0  0 24  0]
 [ 0  2 44  0]]
```

### Test Confusion Matrix (Rows=True, Cols=Pred)
```
[[ 0  0 27  0]
 [ 0  1 42  0]
 [ 6  0 17  0]
 [ 0  3 42  0]]
```

Figure saved to `results/figures/b1_confusion.png` (git-ignored).

## Analysis and Findings
1. B1 small CNN from scratch achieves a Test Macro F1 of 0.0669 (Accuracy: 13.04%) compared to B0's 0.1230 (Accuracy: 32.61%).
2. Training a CNN from scratch on 634 training images from random initialization quickly memorizes training features (training accuracy reached ~66% by epoch 6 while validation loss increased from 1.3694 to 2.4559). Early stopping selected epoch 1 weights, where predictions clustered heavily on Healthy Rice Leaf before broader discriminative features could generalize.
3. This empirical result demonstrates the severe limitation of training convolutional networks from scratch on small-scale agricultural datasets without pretraining, providing concrete justification for transfer learning with pretrained MobileNetV2 in future milestones.
