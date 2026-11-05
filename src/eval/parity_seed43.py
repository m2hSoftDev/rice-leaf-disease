"""
src/eval/parity_seed43.py

T-054: Parity check between Keras canonical model (m1_det_seed43_best.keras)
and float16 TFLite model (model_fp16_seed43.tflite):
1. Evaluates on 20 stratified test images (seed 42, 5 per class) from data/processed/hasan_upright/.
2. Evaluates on all 138 test images to measure exact test accuracy drop in percentage points.
3. Checks Quality Gate 3 criteria: size <= 5.0 MB, accuracy drop <= 2.0 pp, top-1 matches 20/20.
4. Outputs results/metrics/parity_seed43.csv and results/metrics/parity_seed43.md.
"""

import json
import csv
import random
from pathlib import Path
import numpy as np
import tensorflow as tf

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
DATA_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"
KERAS_MODEL_PATH = WORKSPACE_ROOT / "results" / "checkpoints" / "m1_det_seed43_best.keras"
TFLITE_MODEL_PATH = WORKSPACE_ROOT / "results" / "export" / "model_fp16_seed43.tflite"
LABELS_PATH = WORKSPACE_ROOT / "results" / "export" / "labels.json"
PREPROCESS_PATH = WORKSPACE_ROOT / "results" / "export" / "preprocess_config.json"

CSV_OUTPUT = WORKSPACE_ROOT / "results" / "metrics" / "parity_seed43.csv"
MD_OUTPUT = WORKSPACE_ROOT / "results" / "metrics" / "parity_seed43.md"

RANDOM_SEED = 42
SAMPLES_PER_CLASS = 5
IMG_SIZE = (224, 224)
MAX_SIZE_MB = 5.0
MAX_ACC_DROP_PP = 2.0

CLASS_MAP = {
    "Bacterial Leaf Blight": "bacterial_leaf_blight",
    "Brown Spot": "brown_spot",
    "Healthy Rice Leaf": "healthy",
    "Leaf Blast": "leaf_blast",
}
INDEX_TO_LABEL = {
    0: "bacterial_leaf_blight",
    1: "brown_spot",
    2: "healthy",
    3: "leaf_blast",
}


def load_image(img_path):
    raw = tf.io.read_file(str(img_path))
    img = tf.image.decode_jpeg(raw, channels=3)
    img = tf.image.resize(img, IMG_SIZE, method="bilinear")
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img.numpy()


def main():
    print("=== T-054: Parity Evaluation (Canonical Seed 43 Keras vs Float16 TFLite) ===")

    # 1. Verify model files exist
    assert KERAS_MODEL_PATH.exists(), f"Keras model missing: {KERAS_MODEL_PATH}"
    assert TFLITE_MODEL_PATH.exists(), f"TFLite model missing: {TFLITE_MODEL_PATH}"
    tflite_size_bytes = TFLITE_MODEL_PATH.stat().st_size
    tflite_size_mb = tflite_size_bytes / (1024 * 1024)
    print(f"TFLite size: {tflite_size_bytes:,} bytes ({tflite_size_mb:.2f} MB)")

    # 2. Load manifest rows
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    test_rows = [r for r in reader if r["split"] == "test"]
    assert len(test_rows) == 138, f"Expected 138 test images, got {len(test_rows)}"
    print(f"Total test split images: {len(test_rows)}")

    # 3. Select 20 stratified test images (seed 42, 5 per class, sorted by filename)
    classes = sorted(list({r["class"] for r in test_rows}))
    selected_20 = []
    for c in classes:
        c_rows = sorted([r for r in test_rows if r["class"] == c], key=lambda x: x["filename"])
        sampled = random.Random(RANDOM_SEED).sample(c_rows, SAMPLES_PER_CLASS)
        selected_20.extend(sampled)
    assert len(selected_20) == 20, f"Expected 20 samples, got {len(selected_20)}"
    print(f"Selected 20 stratified test images ({SAMPLES_PER_CLASS} per class).")

    # 4. Initialize models
    print("\nLoading models for inference...")
    keras_model = tf.keras.models.load_model(KERAS_MODEL_PATH)
    interpreter = tf.lite.Interpreter(model_path=str(TFLITE_MODEL_PATH))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    in_idx = input_details[0]["index"]
    out_idx = output_details[0]["index"]

    # 5. Evaluate the 20 stratified images
    print("\nEvaluating 20 stratified test images...")
    results_20 = []
    max_prob_diff_overall = 0.0

    for idx, r in enumerate(selected_20):
        img_path = DATA_DIR / r["class"] / r["filename"]
        assert img_path.exists(), f"Image not found: {img_path}"
        img_arr = load_image(img_path)
        img_batch = np.expand_dims(img_arr, axis=0).astype(np.float32)

        # Keras prediction
        keras_prob = keras_model.predict(img_batch, verbose=0)[0]
        keras_pred_idx = int(np.argmax(keras_prob))
        keras_label = INDEX_TO_LABEL[keras_pred_idx]
        keras_conf = float(keras_prob[keras_pred_idx])

        # TFLite prediction
        interpreter.set_tensor(in_idx, img_batch)
        interpreter.invoke()
        tflite_prob = interpreter.get_tensor(out_idx)[0]
        tflite_pred_idx = int(np.argmax(tflite_prob))
        tflite_label = INDEX_TO_LABEL[tflite_pred_idx]
        tflite_conf = float(tflite_prob[tflite_pred_idx])

        true_label = CLASS_MAP[r["class"]]
        parity_match = "YES" if keras_label == tflite_label else "NO"
        keras_correct = "YES" if keras_label == true_label else "NO"
        tflite_correct = "YES" if tflite_label == true_label else "NO"

        # Probability difference
        prob_diff = np.max(np.abs(keras_prob - tflite_prob))
        if prob_diff > max_prob_diff_overall:
            max_prob_diff_overall = float(prob_diff)

        results_20.append({
            "index": idx + 1,
            "filename": r["filename"],
            "true_label": true_label,
            "keras_label": keras_label,
            "keras_confidence": f"{keras_conf:.4f}",
            "tflite_label": tflite_label,
            "tflite_confidence": f"{tflite_conf:.4f}",
            "parity_match": parity_match,
            "keras_correct": keras_correct,
            "tflite_correct": tflite_correct,
            "max_prob_diff": f"{prob_diff:.6f}",
        })

    # Summary on 20 images
    matches_20 = sum(1 for r in results_20 if r["parity_match"] == "YES")
    print(f"\n20-Image Parity Matches: {matches_20} / 20 ({matches_20 / 20 * 100:.1f}%)")
    print(f"Max absolute probability difference across 20 images: {max_prob_diff_overall:.6f}")

    # 6. Full Test Split Evaluation (N=138)
    print("\nEvaluating all 138 test images for accuracy drop measurement...")
    keras_correct_138 = 0
    tflite_correct_138 = 0
    parity_matches_138 = 0
    max_prob_diff_138 = 0.0

    for r in test_rows:
        img_path = DATA_DIR / r["class"] / r["filename"]
        img_arr = load_image(img_path)
        img_batch = np.expand_dims(img_arr, axis=0).astype(np.float32)

        # Keras
        keras_prob = keras_model.predict(img_batch, verbose=0)[0]
        keras_pred_idx = int(np.argmax(keras_prob))
        keras_label = INDEX_TO_LABEL[keras_pred_idx]

        # TFLite
        interpreter.set_tensor(in_idx, img_batch)
        interpreter.invoke()
        tflite_prob = interpreter.get_tensor(out_idx)[0]
        tflite_pred_idx = int(np.argmax(tflite_prob))
        tflite_label = INDEX_TO_LABEL[tflite_pred_idx]

        true_label = CLASS_MAP[r["class"]]
        if keras_label == true_label:
            keras_correct_138 += 1
        if tflite_label == true_label:
            tflite_correct_138 += 1
        if keras_label == tflite_label:
            parity_matches_138 += 1

        prob_diff = float(np.max(np.abs(keras_prob - tflite_prob)))
        if prob_diff > max_prob_diff_138:
            max_prob_diff_138 = prob_diff

    keras_acc_138 = keras_correct_138 / len(test_rows)
    tflite_acc_138 = tflite_correct_138 / len(test_rows)
    acc_drop_pp = (keras_acc_138 - tflite_acc_138) * 100.0

    print(f"Keras Test Accuracy: {keras_acc_138 * 100:.2f}% ({keras_correct_138}/138)")
    print(f"TFLite Test Accuracy: {tflite_acc_138 * 100:.2f}% ({tflite_correct_138}/138)")
    print(f"Measured Accuracy Drop: {acc_drop_pp:+.2f} percentage points")
    print(f"Full Test Set Parity: {parity_matches_138} / 138 ({parity_matches_138 / 138 * 100:.2f}%)")
    print(f"Max prob diff on full test set: {max_prob_diff_138:.6f}")

    # 7. Check Gate 3 criteria
    size_passed = tflite_size_mb <= MAX_SIZE_MB
    drop_passed = acc_drop_pp <= MAX_ACC_DROP_PP
    parity_passed = matches_20 == 20
    gate3_passed = size_passed and drop_passed and parity_passed

    print("\n=== Quality Gate 3 Checklist ===")
    print(f"1. Model Size <= 5.0 MB: {'PASSED' if size_passed else 'FAILED'} ({tflite_size_mb:.2f} MB)")
    print(f"2. Top-1 Parity 20/20:   {'PASSED' if parity_passed else 'FAILED'} ({matches_20}/20 matches)")
    print(f"3. Accuracy Drop <= 2.0 pp: {'PASSED' if drop_passed else 'FAILED'} ({acc_drop_pp:+.2f} pp)")
    print(f"Overall Gate 3 Status: {'PASSED' if gate3_passed else 'FAILED'}")

    # 8. Write CSV
    print(f"\nWriting {CSV_OUTPUT}...")
    fieldnames = [
        "filename",
        "true_label",
        "keras_label",
        "keras_confidence",
        "tflite_label",
        "tflite_confidence",
        "parity_match",
        "keras_correct",
        "tflite_correct",
        "max_prob_diff",
    ]
    with open(CSV_OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results_20:
            writer.writerow({k: r[k] for k in fieldnames})
    print(f"Saved {CSV_OUTPUT}")

    # 9. Write Markdown Report
    print(f"Writing {MD_OUTPUT}...")
    md_lines = [
        "# T-054: Parity Report (Canonical Seed 43 Keras vs Float16 TFLite)",
        "",
        "## 1. Overview and Quality Gate 3 Verification",
        f"- **Keras Source Model**: `results/checkpoints/m1_det_seed43_best.keras` (Canonical Seed 43 selected under D-27 by validation macro F1 = 0.8697).",
        f"- **TFLite Deployment Model**: `results/export/model_fp16_seed43.tflite` (Float16 optimization per D-21).",
        f"- **Preprocessing Contract**: Defined in `results/export/preprocess_config.json` (RGB, 224x224 bilinear, mobilenet_v2 preprocess_input).",
        f"- **Label Contract**: Defined in `results/export/labels.json` (alphabetical class index mapping per D-22).",
        f"- **Gate 3 Criteria**:",
        f"  1. Model file size $\\le 5.0$ MB $\\rightarrow$ **{'PASSED' if size_passed else 'FAILED'}** ({tflite_size_mb:.2f} MB / {tflite_size_bytes:,} bytes).",
        f"  2. TFLite accuracy drop vs Keras $\\le 2.0$ percentage points $\\rightarrow$ **{'PASSED' if drop_passed else 'FAILED'}** ({acc_drop_pp:+.2f} pp on 138-image test split).",
        f"  3. Top-1 prediction parity on 20 stratified test images $\\rightarrow$ **{'PASSED' if parity_passed else 'FAILED'}** ({matches_20} / 20 matches, 100.0%).",
        f"- **Overall Quality Gate 3 Status**: **{'PASSED' if gate3_passed else 'NOT PASSED'}**.",
        "",
        "---",
        "",
        "## 2. Parity Table (20 Stratified Test Images, Seed 42 Selection)",
        "",
        "| # | Filename | Ground Truth Label | Keras Top-1 Label (Conf) | Float16 TFLite Top-1 Label (Conf) | Parity Match? | Ground Truth Match? | Max Prob Diff |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for r in results_20:
        parity_badge = "**YES**" if r["parity_match"] == "YES" else "**NO (MISMATCH)**"
        gt_badge = "YES" if r["tflite_correct"] == "YES" else "NO"
        md_lines.append(
            f"| {r['index']} | `{r['filename']}` | `{r['true_label']}` | `{r['keras_label']}` ({float(r['keras_confidence'])*100:.2f}%) | `{r['tflite_label']}` ({float(r['tflite_confidence'])*100:.2f}%) | {parity_badge} | {gt_badge} | {r['max_prob_diff']} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Summary Statistics on Stratified Sample ($N=20$)",
        f"- **Total Evaluated Images**: 20 (5 images per class, test split, seed 42 selection).",
        f"- **Top-1 Parity Matches**: **{matches_20} / 20 ({matches_20/20*100:.1f}%)**.",
        f"- **Mismatches**: {20 - matches_20}.",
        f"- **Max Absolute Probability Difference**: {max_prob_diff_overall:.6f}.",
        f"- **Keras Sample Accuracy**: {sum(1 for r in results_20 if r['keras_correct'] == 'YES')} / 20 ({(sum(1 for r in results_20 if r['keras_correct'] == 'YES')/20)*100:.1f}%).",
        f"- **TFLite Sample Accuracy**: {sum(1 for r in results_20 if r['tflite_correct'] == 'YES')} / 20 ({(sum(1 for r in results_20 if r['tflite_correct'] == 'YES')/20)*100:.1f}%).",
        "",
        "---",
        "",
        "## 4. Full Public Test Split Evaluation ($N=138$)",
        f"- **Keras Test Accuracy**: {keras_acc_138*100:.2f}% ({keras_correct_138} / 138).",
        f"- **TFLite Test Accuracy**: {tflite_acc_138*100:.2f}% ({tflite_correct_138} / 138).",
        f"- **Accuracy Drop**: **{acc_drop_pp:+.2f} percentage points** (Requirement: $\\le 2.0$ pp $\\rightarrow$ **{'PASSED' if drop_passed else 'FAILED'}**).",
        f"- **Overall Top-1 Prediction Agreement**: {parity_matches_138} / 138 ({parity_matches_138 / 138 * 100:.2f}%).",
        f"- **Max Absolute Probability Difference on Test Split**: {max_prob_diff_138:.6f}.",
        "",
        "---",
        "",
        "## 5. Gate Status Conclusion",
        f"- **Gate 3 Status**: **{'PASSED' if gate3_passed else 'NOT PASSED'}** for model size, accuracy drop, and parity.",
        f"- **Gate 2 Status**: **NOT MET** on the five-seed mean (0.7756 ± 0.0339 across seeds 42–46). The canonical model (seed 43, val macro F1 0.8697) achieved test macro F1 0.7627. Per D-27, model is not described as validated to Gate 2.",
    ])

    with open(MD_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Saved {MD_OUTPUT}")
    print("\n=== Parity Evaluation Completed Successfully ===")


if __name__ == "__main__":
    main()
