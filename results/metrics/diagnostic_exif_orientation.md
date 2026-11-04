# Diagnostic: EXIF Orientation Impact on Test Split

## Overview
Diagnostic evaluation conducted for **T-062** to quantify the impact of EXIF orientation handling on the held-out test split ($N=138$, seed 42) using canonical model `m1_seed44_best.keras`.

## Test Split EXIF Tag Distribution
Total test images: **138**
- **Orientation 6** (`ROTATE_90_CW`): **123** images (89.13%)
- Other orientations:
  - Orientation 1: **12** images (8.70%)
  - Orientation 3: **3** images (2.17%)

## Diagnostic Results Table

| Condition | Orientation Handling | Accuracy | Macro F1 | Gate 2 Check (Macro F1 >= 0.80) | Tag 6 Count |
|---|---|---|---|---|---|
| **(a) Raw Stored (Landscape)** | Raw JPEG raster without EXIF transpose (`tf.image.decode_jpeg`) | 86.96% (0.8696) | 0.8761 | **MET** | 123 / 138 |
| **(b) EXIF Upright** | Upright portrait with EXIF tag 6 transposed 90° CW | 70.29% (0.7029) | 0.7205 | **NOT MET** | 123 / 138 |
| **Delta** | Upright vs Raw Stored | -16.67 pp | -0.1555 | — | — |

## Key Findings
1. In the held-out test split, **123 out of 138 images (89.13%)** have EXIF tag 6 (`ROTATE_90_CW`).
2. The training pipeline (`train_m1.py` / `baseline_b2.py`) used `tf.image.decode_jpeg`, which decoded raw landscape rasters without applying EXIF orientation.
3. When evaluated as stored (raw landscape), test macro F1 is **0.8761** (accuracy 86.96%).
4. When evaluated upright (EXIF transposed), test macro F1 is **0.7205** (accuracy 70.29%).
5. This diagnostic demonstrates the empirical performance difference between raw landscape rasters and EXIF-upright rasters on the Hasan dataset.
