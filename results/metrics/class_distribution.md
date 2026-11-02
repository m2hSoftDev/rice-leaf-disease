# Class Distribution Report

Distribution of the 907 active original images across the four locked target classes and splits (seed 42, group-stratified partition):

| Class | Train (70%) | Val (15%) | Test (15%) | Total | % of Total |
|---|---|---|---|---|---|
| **Bacterial Leaf Blight** | 125 | 27 | 27 | 179 | 19.7% |
| **Brown Spot** | 186 | 38 | 43 | 267 | 29.4% |
| **Healthy Rice Leaf** | 110 | 24 | 23 | 157 | 17.3% |
| **Leaf Blast** | 213 | 46 | 45 | 304 | 33.5% |
| **Overall** | **634** | **135** | **138** | **907** | **100.0%** |

## Observations

1. The active dataset comprises 907 unaugmented original photos partitioned by near-duplicate perceptual hash groups, ensuring zero leakage across train, validation, and test splits.
2. Leaf Blast constitutes the largest class with 304 images (33.5%), followed by Brown Spot with 267 images (29.4%) and Bacterial Leaf Blight with 179 images (19.7%).
3. Healthy Rice Leaf is the smallest class with 157 images (17.3%), comfortably surpassing the Section 6 requirement of at least 100 images per class before model training.
4. The 70/15/15 group-stratified distribution is maintained across all classes (634 train, 135 val, 138 test), providing balanced evaluation sets without separating bursts of the same lesion.
