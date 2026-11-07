"""
src/eval/generate_synthetic_fixture.py

Generates a synthetic 224x224 JPEG test fixture image purely in code
(not derived from any dataset image; no copyright or license restrictions),
evaluates it with the canonical float16 TFLite model (model_fp16_seed43.tflite),
and writes expected parity outputs to app/test/fixtures/synthetic_fixture_expected.json.
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = WORKSPACE_ROOT / "app" / "test" / "fixtures"
OUTPUT_IMAGE_PATH = FIXTURES_DIR / "synthetic_leaf.jpg"
OUTPUT_JSON_PATH = FIXTURES_DIR / "synthetic_fixture_expected.json"
TFLITE_MODEL_PATH = WORKSPACE_ROOT / "results" / "export" / "model_fp16_seed43.tflite"

INDEX_TO_LABEL = {
    0: "bacterial_leaf_blight",
    1: "brown_spot",
    2: "healthy",
    3: "leaf_blast",
}


def create_synthetic_image(output_path: Path):
    """Creates a deterministic synthetic 224x224 RGB JPEG image in code."""
    width, height = 224, 224
    np.random.seed(42)

    # Base green leaf gradient
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            # Vertical leaf gradient with slight variation
            r = int(50 + 20 * (x / width) + 15 * np.sin(y / 15.0))
            g = int(140 + 40 * (1.0 - abs(x - width / 2) / (width / 2)))
            b = int(40 + 15 * (y / height))
            arr[y, x] = [np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)]

    img = Image.fromarray(arr, mode="RGB")
    draw = ImageDraw.Draw(img)

    # Add synthetic brown / yellow leaf lesion spots
    # Spot 1: brown spot with halo
    draw.ellipse([80, 50, 130, 90], fill=(160, 130, 50), outline=(120, 80, 30))
    draw.ellipse([90, 60, 120, 80], fill=(100, 50, 20), outline=(70, 35, 15))

    # Spot 2: elongated spindle-like blast lesion
    draw.polygon([(112, 110), (125, 140), (112, 175), (99, 140)], fill=(110, 60, 30), outline=(80, 40, 20))
    draw.polygon([(112, 125), (118, 140), (112, 155), (106, 140)], fill=(200, 200, 200), outline=(140, 90, 50))

    # Spot 3: small circular spot
    draw.ellipse([150, 160, 175, 185], fill=(130, 70, 30), outline=(90, 45, 20))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    print(f"Created synthetic fixture image: {output_path} ({output_path.stat().st_size} bytes)")


def evaluate_fixture(img_path: Path, model_path: Path) -> dict:
    """Evaluates the image using the canonical TFLite model."""
    assert model_path.exists(), f"Model not found at {model_path}"
    assert img_path.exists(), f"Image not found at {img_path}"

    # Load and preprocess image matching training pipeline
    raw = tf.io.read_file(str(img_path))
    img = tf.image.decode_jpeg(raw, channels=3)
    img = tf.image.resize(img, [224, 224], method="bilinear")
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    input_data = np.expand_dims(img.numpy(), axis=0).astype(np.float32)

    # Run TFLite interpreter
    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    in_idx = interpreter.get_input_details()[0]["index"]
    out_idx = interpreter.get_output_details()[0]["index"]

    interpreter.set_tensor(in_idx, input_data)
    interpreter.invoke()
    preds = interpreter.get_tensor(out_idx)[0]

    top_idx = int(np.argmax(preds))
    top_label = INDEX_TO_LABEL[top_idx]
    top_conf = float(preds[top_idx])
    prob_list = [float(p) for p in preds]

    result = {
        "description": "Synthetic 224x224 test fixture image for TFLite inference parity verification. Created purely in code (no dataset image; no license restrictions).",
        "filename": img_path.name,
        "image_size": [224, 224, 3],
        "model_file": model_path.name,
        "top1_label": top_label,
        "top1_index": top_idx,
        "top1_confidence": round(top_conf, 6),
        "class_probabilities": [round(p, 6) for p in prob_list],
        "probabilities_by_class": {
            INDEX_TO_LABEL[i]: round(prob_list[i], 6) for i in range(4)
        },
    }
    return result


def main():
    print("=== Generating Synthetic Test Fixture and Evaluating Parity ===")
    create_synthetic_image(OUTPUT_IMAGE_PATH)
    result = evaluate_fixture(OUTPUT_IMAGE_PATH, TFLITE_MODEL_PATH)

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote expected results to: {OUTPUT_JSON_PATH}")

    print("\nParity Target Output:")
    print(f"  Top-1 Label: {result['top1_label']} (index {result['top1_index']})")
    print(f"  Top-1 Confidence: {result['top1_confidence'] * 100:.2f}% ({result['top1_confidence']})")
    print(f"  Probabilities: {result['class_probabilities']}")


if __name__ == "__main__":
    main()
