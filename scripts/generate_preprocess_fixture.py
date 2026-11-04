import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import tensorflow as tf

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
STAGING_DIR = WORKSPACE_ROOT / "data" / "raw" / "public" / "hasan_staging" / "Original Images"

df = pd.read_csv(MANIFEST_PATH)
sample = df[df["split"] == "test"].sample(3, random_state=42)

points = [(0, 0), (56, 56), (112, 112), (168, 168), (223, 0), (223, 223)]
fixture_data = {
    "metadata": {
        "seed": 42,
        "target_size": [224, 224],
        "points": [[y, x] for y, x in points],
        "formula": "x / 127.5 - 1.0",
        "description": "Preprocessed values at 6 fixed positions for 3 test images under training preprocessing"
    },
    "images": []
}

for _, row in sample.iterrows():
    p = STAGING_DIR / row["class"] / row["filename"]
    
    pil_im = Image.open(p)
    exif = pil_im.getexif()
    orient = int(exif.get(0x0112, 1))
    
    # 1. Training preprocessing (raw tf.image.decode_jpeg, bilinear resize, mobilenet_v2.preprocess_input)
    raw = tf.io.read_file(str(p))
    img_tf = tf.image.decode_jpeg(raw, channels=3)
    img_tf_resized = tf.image.resize(img_tf, (224, 224), method="bilinear")
    norm_tf = ((img_tf_resized.numpy() / 127.5) - 1.0).astype(float)
    
    # 2. Upright with EXIF transpose
    pil_upright = ImageOps.exif_transpose(pil_im)
    pil_upright_resized = pil_upright.resize((224, 224), Image.Resampling.BILINEAR)
    norm_upright = ((np.array(pil_upright_resized, dtype=np.float32) / 127.5) - 1.0).astype(float)
    
    pts_raw = {}
    pts_upright = {}
    for y, x in points:
        pts_raw[f"{y},{x}"] = [round(float(v), 6) for v in norm_tf[y, x].tolist()]
        pts_upright[f"{y},{x}"] = [round(float(v), 6) for v in norm_upright[y, x].tolist()]
        
    # Save python decoded image as lossless PNG for resize and decoder parity tests
    decoded_dir = WORKSPACE_ROOT / "app" / "test" / "fixtures" / "python_decoded"
    decoded_dir.mkdir(parents=True, exist_ok=True)
    safe_name = row['filename'].replace(' ', '_').replace('(', '').replace(')', '') + '.png'
    Image.fromarray(img_tf.numpy()).save(decoded_dir / safe_name)
    
    fixture_data["images"].append({
        "class": row["class"],
        "filename": row["filename"],
        "relative_path": f"{row['class']}/{row['filename']}",
        "exif_orientation": orient,
        "points": pts_raw,
        "points_training_raw": pts_raw,
        "points_exif_upright": pts_upright
    })

out_path = WORKSPACE_ROOT / "app" / "test" / "fixtures" / "preprocess_expected.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(fixture_data, f, indent=2)
print(f"Wrote fixture to {out_path}")

root_fixture = WORKSPACE_ROOT / "test" / "fixtures" / "preprocess_expected.json"
root_fixture.parent.mkdir(parents=True, exist_ok=True)
with open(root_fixture, "w", encoding="utf-8") as f:
    json.dump(fixture_data, f, indent=2)
print(f"Wrote fixture to {root_fixture}")
