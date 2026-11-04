import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from sklearn.metrics import accuracy_score, f1_score
import tensorflow as tf

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
STAGING_DIR = WORKSPACE_ROOT / "data" / "raw" / "public" / "hasan_staging" / "Original Images"
MODEL_PATH = WORKSPACE_ROOT / "results" / "checkpoints" / "m1_seed44_best.keras"
OUTPUT_CSV = WORKSPACE_ROOT / "results" / "metrics" / "diagnostic_exif_orientation.csv"
OUTPUT_MD = WORKSPACE_ROOT / "results" / "metrics" / "diagnostic_exif_orientation.md"

def main():
    print("Loading split manifest...")
    df = pd.read_csv(MANIFEST_PATH)
    test_df = df[df["split"] == "test"].copy()
    assert len(test_df) == 138, f"Expected 138 test images, got {len(test_df)}"

    class_to_idx = {
        "Bacterial Leaf Blight": 0,
        "Brown Spot": 1,
        "Healthy Rice Leaf": 2,
        "Leaf Blast": 3,
    }
    print(f"Class mapping: {class_to_idx}")

    print(f"Loading canonical model: {MODEL_PATH}")
    model = tf.keras.models.load_model(str(MODEL_PATH))

    # Audit EXIF orientation tags in test split
    exif_counts = {}
    images_raw_list = []
    images_upright_list = []
    y_true = []

    print("Loading test split images in both conditions...")
    for _, row in test_df.iterrows():
        p = STAGING_DIR / row["class"] / row["filename"]
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {p}")

        label_idx = class_to_idx[row["class"]]
        y_true.append(label_idx)

        # Inspect EXIF
        im_pil = Image.open(p)
        exif = im_pil.getexif()
        orient = int(exif.get(0x0112, 1))
        exif_counts[orient] = exif_counts.get(orient, 0) + 1

        # Condition (a): Raw landscape as stored (TensorFlow decode_jpeg, no EXIF transpose)
        raw_bytes = tf.io.read_file(str(p))
        img_raw = tf.image.decode_jpeg(raw_bytes, channels=3)
        img_raw_resized = tf.image.resize(img_raw, (224, 224), method="bilinear")
        img_raw_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(img_raw_resized)
        images_raw_list.append(img_raw_preprocessed)

        # Condition (b): EXIF orientation applied (upright via ImageOps.exif_transpose)
        im_upright = ImageOps.exif_transpose(im_pil)
        arr_upright = np.array(im_upright, dtype=np.float32)
        tensor_upright = tf.convert_to_tensor(arr_upright, dtype=tf.float32)
        img_upright_resized = tf.image.resize(tensor_upright, (224, 224), method="bilinear")
        img_upright_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(img_upright_resized)
        images_upright_list.append(img_upright_preprocessed)

    batch_raw = tf.stack(images_raw_list)
    batch_upright = tf.stack(images_upright_list)
    y_true = np.array(y_true)

    print(f"Test split EXIF tag counts (total N={len(test_df)}): {exif_counts}")
    tag_6_count = exif_counts.get(6, 0)
    print(f"Images with EXIF tag 6 (rotate 90 CW): {tag_6_count} ({tag_6_count / len(test_df) * 100:.2f}%)")

    print("Running inference on Condition (a): Raw stored orientation...")
    preds_raw = model.predict(batch_raw, batch_size=32, verbose=0)
    y_pred_raw = np.argmax(preds_raw, axis=1)
    acc_raw = accuracy_score(y_true, y_pred_raw)
    f1_raw = f1_score(y_true, y_pred_raw, average="macro")

    print("Running inference on Condition (b): EXIF upright orientation...")
    preds_upright = model.predict(batch_upright, batch_size=32, verbose=0)
    y_pred_upright = np.argmax(preds_upright, axis=1)
    acc_upright = accuracy_score(y_true, y_pred_upright)
    f1_upright = f1_score(y_true, y_pred_upright, average="macro")

    print("=" * 60)
    print("EXIF ORIENTATION DIAGNOSTIC RESULTS")
    print(f"Condition (a) - Raw Stored (Landscape): Accuracy = {acc_raw * 100:.2f}%, Macro F1 = {f1_raw:.4f}")
    print(f"Condition (b) - EXIF Upright:            Accuracy = {acc_upright * 100:.2f}%, Macro F1 = {f1_upright:.4f}")
    print(f"Delta (Upright - Raw):                  Accuracy = {(acc_upright - acc_raw) * 100:+.2f} pp, Macro F1 = {f1_upright - f1_raw:+.4f}")
    print("=" * 60)

    # Save to CSV
    csv_rows = [
        {
            "condition": "raw_stored_landscape",
            "description": "Images evaluated in raw stored orientation (training pipeline)",
            "total_images": len(test_df),
            "tag_6_count": tag_6_count,
            "accuracy": round(acc_raw, 4),
            "macro_f1": round(f1_raw, 4)
        },
        {
            "condition": "exif_upright",
            "description": "Images evaluated with EXIF orientation applied (upright portrait)",
            "total_images": len(test_df),
            "tag_6_count": tag_6_count,
            "accuracy": round(acc_upright, 4),
            "macro_f1": round(f1_upright, 4)
        }
    ]
    pd.DataFrame(csv_rows).to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {OUTPUT_CSV}")

    # Save to Markdown
    md_content = f"""# Diagnostic: EXIF Orientation Impact on Test Split

## Overview
Diagnostic evaluation conducted for **T-062** to quantify the impact of EXIF orientation handling on the held-out test split ($N=138$, seed 42) using canonical model `m1_seed44_best.keras`.

## Test Split EXIF Tag Distribution
Total test images: **{len(test_df)}**
- **Orientation 6** (`ROTATE_90_CW`): **{tag_6_count}** images ({tag_6_count / len(test_df) * 100:.2f}%)
- Other orientations:
"""
    for tag, cnt in sorted(exif_counts.items()):
        if tag != 6:
            md_content += f"  - Orientation {tag}: **{cnt}** images ({cnt / len(test_df) * 100:.2f}%)\n"

    gate2_check_raw = "**MET**" if f1_raw >= 0.80 else "**NOT MET**"
    gate2_check_upright = "**MET**" if f1_upright >= 0.80 else "**NOT MET**"

    md_content += f"""
## Diagnostic Results Table

| Condition | Orientation Handling | Accuracy | Macro F1 | Gate 2 Check (Macro F1 >= 0.80) | Tag 6 Count |
|---|---|---|---|---|---|
| **(a) Raw Stored (Landscape)** | Raw JPEG raster without EXIF transpose (`tf.image.decode_jpeg`) | {acc_raw * 100:.2f}% ({acc_raw:.4f}) | {f1_raw:.4f} | {gate2_check_raw} | {tag_6_count} / {len(test_df)} |
| **(b) EXIF Upright** | Upright portrait with EXIF tag 6 transposed 90° CW | {acc_upright * 100:.2f}% ({acc_upright:.4f}) | {f1_upright:.4f} | {gate2_check_upright} | {tag_6_count} / {len(test_df)} |
| **Delta** | Upright vs Raw Stored | {(acc_upright - acc_raw) * 100:+.2f} pp | {f1_upright - f1_raw:+.4f} | — | — |

## Key Findings
1. In the held-out test split, **{tag_6_count} out of {len(test_df)} images ({tag_6_count / len(test_df) * 100:.2f}%)** have EXIF tag 6 (`ROTATE_90_CW`).
2. The training pipeline (`train_m1.py` / `baseline_b2.py`) used `tf.image.decode_jpeg`, which decoded raw landscape rasters without applying EXIF orientation.
3. When evaluated as stored (raw landscape), test macro F1 is **{f1_raw:.4f}** (accuracy {acc_raw * 100:.2f}%).
4. When evaluated upright (EXIF transposed), test macro F1 is **{f1_upright:.4f}** (accuracy {acc_upright * 100:.2f}%).
5. This diagnostic demonstrates the empirical performance difference between raw landscape rasters and EXIF-upright rasters on the Hasan dataset.
"""

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved {OUTPUT_MD}")

if __name__ == "__main__":
    main()
