"""
src/export/export_seed43.py

Exports canonical model (m1_det_seed43_best.keras) to float16 TFLite:
- Verifies model weights SHA-256 against expected hash (1041038f...).
- Converts to float16 TFLite and saves to results/export/model_fp16_seed43.tflite.
- Asserts model size <= 5.0 MB.
- Regenerates results/export/labels.json and preprocess_config.json, confirming
  identical content to existing contract.
"""

import json
import hashlib
from pathlib import Path
import tensorflow as tf

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = WORKSPACE_ROOT / "results" / "checkpoints" / "m1_det_seed43_best.keras"
EXPORT_DIR = WORKSPACE_ROOT / "results" / "export"
TFLITE_OUTPUT_PATH = EXPORT_DIR / "model_fp16_seed43.tflite"
LABELS_PATH = EXPORT_DIR / "labels.json"
PREPROCESS_CONFIG_PATH = EXPORT_DIR / "preprocess_config.json"

EXPECTED_WEIGHTS_HASH = "1041038f95c65132cb802d769ce15944ff7d69e7daca0fe6fd38dce2cc4f4787"
MAX_SIZE_MB = 5.0


def compute_weights_hash(model):
    hasher = hashlib.sha256()
    for weight in model.get_weights():
        hasher.update(weight.tobytes())
    return hasher.hexdigest()


def main():
    print("=== Step 1: Export Canonical Model (Seed 43) to Float16 TFLite ===")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load canonical checkpoint
    print(f"Loading checkpoint from {CHECKPOINT_PATH}...")
    assert CHECKPOINT_PATH.exists(), f"Checkpoint not found at {CHECKPOINT_PATH}"
    model = tf.keras.models.load_model(CHECKPOINT_PATH)

    # 2. Verify weights hash
    actual_hash = compute_weights_hash(model)
    print(f"Computed weights SHA-256: {actual_hash}")
    print(f"Expected weights SHA-256: {EXPECTED_WEIGHTS_HASH}")
    assert actual_hash == EXPECTED_WEIGHTS_HASH, (
        f"Weights hash mismatch! Expected {EXPECTED_WEIGHTS_HASH}, got {actual_hash}"
    )
    print("[PASS] Checkpoint weights hash verified exactly.")

    # 3. Convert to Float16 TFLite
    print("\nConverting model to float16 TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_bytes = converter.convert()

    # 4. Save to results/export/model_fp16_seed43.tflite
    with open(TFLITE_OUTPUT_PATH, "wb") as f:
        f.write(tflite_bytes)
    size_bytes = len(tflite_bytes)
    size_mb = size_bytes / (1024 * 1024)

    print(f"Saved TFLite model to {TFLITE_OUTPUT_PATH}")
    print(f"Size: {size_bytes:,} bytes ({size_mb:.2f} MB / {size_mb:.4f} MiB)")
    assert size_mb <= MAX_SIZE_MB, f"Model size {size_mb:.2f} MB exceeds {MAX_SIZE_MB} MB limit!"
    print(f"[PASS] Model size check passed: {size_mb:.2f} MB <= {MAX_SIZE_MB} MB")

    # 5. Regenerate and verify labels.json and preprocess_config.json
    print("\nRegenerating results/export/labels.json and preprocess_config.json...")

    # Read existing content for comparison
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        existing_labels = json.load(f)
    with open(PREPROCESS_CONFIG_PATH, "r", encoding="utf-8") as f:
        existing_preprocess = json.load(f)

    # Define regenerated content per D-22 and Section 8
    labels_content = {
        "model_classes": [
            "bacterial_leaf_blight",
            "brown_spot",
            "healthy",
            "leaf_blast"
        ],
        "model_index_to_label": {
            "0": "bacterial_leaf_blight",
            "1": "brown_spot",
            "2": "healthy",
            "3": "leaf_blast"
        },
        "model_index_to_display_name_en": {
            "0": "Bacterial Leaf Blight",
            "1": "Brown Spot",
            "2": "Healthy",
            "3": "Leaf Blast"
        },
        "model_index_to_display_name_bn": {
            "0": "ব্যাকটেরিয়াল পাতা ঝলসানো",
            "1": "বাদামি দাগ রোগ",
            "2": "সুস্থ পাতা",
            "3": "পাতা ব্লাস্ট"
        },
        "section6_classes": [
            "bacterial_leaf_blight",
            "brown_spot",
            "leaf_blast",
            "healthy"
        ],
        "note": "Model output logits are ordered alphabetically by training folder: 0=bacterial_leaf_blight, 1=brown_spot, 2=healthy, 3=leaf_blast. In Flutter inference, index 2 is 'healthy' and index 3 is 'leaf_blast'. Do NOT use Section 6 table order (where healthy was 3 and leaf_blast was 2), or Healthy and Leaf Blast predictions will be transposed."
    }

    preprocess_content = {
        "input_size": [
            224,
            224
        ],
        "color_mode": "RGB",
        "interpolation": "bilinear",
        "normalization": "mobilenet_v2.preprocess_input",
        "formula": "x / 127.5 - 1.0",
        "value_range": [
            -1.0,
            1.0
        ],
        "output_activation": "softmax",
        "num_classes": 4,
        "input_tensor_shape": [
            1,
            224,
            224,
            3
        ],
        "input_tensor_dtype": "float32",
        "output_tensor_shape": [
            1,
            4
        ],
        "output_tensor_dtype": "float32"
    }

    assert labels_content == existing_labels, "labels_content differs from existing labels.json!"
    assert preprocess_content == existing_preprocess, "preprocess_content differs from existing preprocess_config.json!"

    # Write files
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_content, f, indent=2, ensure_ascii=False)
    with open(PREPROCESS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(preprocess_content, f, indent=2)

    print("[PASS] labels.json and preprocess_config.json regenerated and content confirmed identical.")
    print("\nStep 1 export completed successfully.")


if __name__ == "__main__":
    main()
