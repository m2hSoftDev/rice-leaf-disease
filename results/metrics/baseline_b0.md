# Baseline B0: Majority Class Predictor

Majority class determined from training split: **Leaf Blast** (213 / 634 train images = 33.6%).
Every instance in validation and test splits is predicted as 'Leaf Blast'.

## Summary Metrics

| Split | Accuracy | Macro F1 | Cohen's Kappa | Total Samples | Majority Predictor |
|---|---|---|---|---|---|
| **Validation** | 0.3407 (34.07%) | 0.1271 | 0.0000 | 135 | Leaf Blast |
| **Test** | 0.3261 (32.61%) | 0.1230 | 0.0000 | 138 | Leaf Blast |

## Detailed Per-Class Breakdown

### Validation Split

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.0000 | 0.0000 | 0.0000 | 27 |
| Brown Spot | 0.0000 | 0.0000 | 0.0000 | 38 |
| Healthy Rice Leaf | 0.0000 | 0.0000 | 0.0000 | 24 |
| Leaf Blast | 0.3407 | 1.0000 | 0.5083 | 46 |
| **Macro Average** | **0.0852** | **0.2500** | **0.1271** | **135** |

### Test Split

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Bacterial Leaf Blight | 0.0000 | 0.0000 | 0.0000 | 27 |
| Brown Spot | 0.0000 | 0.0000 | 0.0000 | 43 |
| Healthy Rice Leaf | 0.0000 | 0.0000 | 0.0000 | 23 |
| Leaf Blast | 0.3261 | 1.0000 | 0.4918 | 45 |
| **Macro Average** | **0.0815** | **0.2500** | **0.1230** | **138** |

## Observations and Analysis

Macro F1 for B0 is very low (~0.12) because predicting a single majority class yields zero precision, recall, and F1 for the other three classes, heavily penalizing the unweighted macro average. This baseline matters because it establishes the foundational lower-bound performance driven purely by class imbalance, proving that any viable machine learning model must learn genuine discriminative features rather than exploiting prior class distributions.
