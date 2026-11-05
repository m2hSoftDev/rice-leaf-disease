"""
src/models/test_determinism.py

Determinism test for Stage 1 MobileNetV2 on EXIF-upright data.
Runs Stage 1 for seed 42 in a single fresh process.
Outputs epoch-by-epoch metrics, final val & test macro F1, and SHA-256 weights hash.
"""

import sys
import os
import csv
import json
import time
import argparse
from pathlib import Path

# Enable determinism before importing TensorFlow
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.utils.determinism import enable_determinism, compute_weights_hash

SEED = 42
enable_determinism(SEED)

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score

MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
UPRIGHT_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"
CHECKPOINT_DIR = WORKSPACE_ROOT / "results" / "checkpoints"
METRICS_DIR = WORKSPACE_ROOT / "results" / "metrics"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
STAGE1_MAX_EPOCHS = 20
PATIENCE = 5
STAGE1_LR = 1e-3

CLASS_NAMES = ["Bacterial Leaf Blight", "Brown Spot", "Healthy Rice Leaf", "Leaf Blast"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_NAMES)}


def load_manifest():
    train_rows, val_rows, test_rows = [], [], []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["split"] == "train":
                train_rows.append(r)
            elif r["split"] == "val":
                val_rows.append(r)
            elif r["split"] == "test":
                test_rows.append(r)
    return train_rows, val_rows, test_rows


def prefetch_in_memory(rows, class_to_idx):
    images_list, labels_list = [], []
    for r in rows:
        p = UPRIGHT_DIR / r["class"] / r["filename"]
        raw = tf.io.read_file(str(p))
        img = tf.image.decode_jpeg(raw, channels=3)
        img = tf.image.resize(img, IMG_SIZE, method="bilinear")
        images_list.append(img)
        labels_list.append(class_to_idx[r["class"]])
    return tf.stack(images_list), tf.convert_to_tensor(labels_list, dtype=tf.int32)


def get_data_augmentation(seed):
    return tf.keras.Sequential([
        tf.keras.layers.RandomRotation(30.0 / 360.0, seed=seed),
        tf.keras.layers.RandomFlip("horizontal_and_vertical", seed=seed),
        tf.keras.layers.RandomZoom((-0.2, 0.2), seed=seed),
        tf.keras.layers.RandomBrightness(0.2, value_range=(0.0, 255.0), seed=seed),
        tf.keras.layers.RandomContrast(0.2, seed=seed),
    ], name=f"data_augmentation_{seed}")


def make_dataset(images_tensor, labels_tensor, seed, is_train=False):
    aug = get_data_augmentation(seed)

    def train_map(bx, by):
        bx = aug(bx, training=True)
        bx = tf.keras.applications.mobilenet_v2.preprocess_input(bx)
        return bx, by

    def eval_map(bx, by):
        bx = tf.keras.applications.mobilenet_v2.preprocess_input(bx)
        return bx, by

    ds = tf.data.Dataset.from_tensor_slices((images_tensor, labels_tensor))
    if is_train:
        ds = ds.shuffle(buffer_size=len(images_tensor), seed=seed, reshuffle_each_iteration=True)
        ds = ds.batch(BATCH_SIZE)
        ds = ds.map(train_map, num_parallel_calls=tf.data.AUTOTUNE, deterministic=True)
    else:
        ds = ds.batch(BATCH_SIZE)
        ds = ds.map(eval_map, num_parallel_calls=tf.data.AUTOTUNE, deterministic=True)
    return ds.prefetch(tf.data.AUTOTUNE)


class DeterministicEpochCallback(tf.keras.callbacks.Callback):
    def __init__(self, val_dataset, y_val_true, checkpoint_path, patience=5):
        super().__init__()
        self.val_dataset = val_dataset
        self.y_val_true = y_val_true
        self.checkpoint_path = Path(checkpoint_path)
        self.patience = patience
        self.best_macro_f1 = -1.0
        self.best_epoch = 0
        self.wait = 0
        self.epoch_history = []

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        y_probs = self.model.predict(self.val_dataset, verbose=0)
        y_pred = np.argmax(y_probs, axis=1)
        macro_f1 = float(f1_score(self.y_val_true, y_pred, average="macro", zero_division=0))
        logs["val_macro_f1"] = macro_f1

        ep_record = {
            "epoch": epoch + 1,
            "loss": float(logs.get("loss", 0.0)),
            "accuracy": float(logs.get("accuracy", 0.0)),
            "val_loss": float(logs.get("val_loss", 0.0)),
            "val_accuracy": float(logs.get("val_accuracy", 0.0)),
            "val_macro_f1": macro_f1,
        }
        self.epoch_history.append(ep_record)
        print(f"Epoch {epoch + 1}: loss={ep_record['loss']:.6f}, acc={ep_record['accuracy']:.6f}, val_loss={ep_record['val_loss']:.6f}, val_acc={ep_record['val_accuracy']:.6f}, val_macro_f1={macro_f1:.6f}")

        if macro_f1 > self.best_macro_f1:
            self.best_macro_f1 = macro_f1
            self.best_epoch = epoch + 1
            self.wait = 0
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(self.checkpoint_path))
        else:
            self.wait += 1
            if self.wait >= self.patience:
                print(f"Early stopping at epoch {epoch + 1}")
                self.model.stop_training = True


def build_base_stage1_model(seed, num_classes=4):
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
        alpha=1.0,
        pooling="avg",
    )
    base_model.trainable = False

    x = base_model(inputs, training=False)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense128")(x)
    x = tf.keras.layers.Dropout(0.3, seed=seed, name="dropout")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    return tf.keras.Model(inputs=inputs, outputs=outputs, name=f"mobilenetv2_stage1_seed_{seed}")


def run_stage1_determinism(run_id: int):
    print(f"=== Running Stage 1 Determinism Test (Run {run_id}) ===")
    t0 = time.time()

    train_rows, val_rows, test_rows = load_manifest()
    X_train_raw, y_train_t = prefetch_in_memory(train_rows, CLASS_TO_IDX)
    X_val_raw, y_val_t = prefetch_in_memory(val_rows, CLASS_TO_IDX)
    X_test_raw, y_test_t = prefetch_in_memory(test_rows, CLASS_TO_IDX)

    y_train_np = y_train_t.numpy()
    classes_present = np.unique(y_train_np)
    weights = compute_class_weight(class_weight="balanced", classes=classes_present, y=y_train_np)
    class_weight_dict = {int(c): float(w) for c, w in zip(classes_present, weights)}

    train_ds = make_dataset(X_train_raw, y_train_t, seed=SEED, is_train=True)
    val_ds = make_dataset(X_val_raw, y_val_t, seed=SEED, is_train=False)
    test_ds = make_dataset(X_test_raw, y_test_t, seed=SEED, is_train=False)

    model = build_base_stage1_model(seed=SEED, num_classes=4)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    ckpt_path = CHECKPOINT_DIR / f"determinism_test_run{run_id}.keras"
    cb = DeterministicEpochCallback(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=ckpt_path,
        patience=PATIENCE,
    )

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[cb],
        verbose=1,
    )
    elapsed = time.time() - t0

    # Restore best checkpoint
    print(f"Restoring best checkpoint from {ckpt_path}...")
    model.load_weights(str(ckpt_path))

    # Evaluate on val and test
    y_val_pred = np.argmax(model.predict(val_ds, verbose=0), axis=1)
    val_macro_f1 = float(f1_score(y_val_t.numpy(), y_val_pred, average="macro", zero_division=0))
    val_acc = float(accuracy_score(y_val_t.numpy(), y_val_pred))

    y_test_pred = np.argmax(model.predict(test_ds, verbose=0), axis=1)
    test_macro_f1 = float(f1_score(y_test_t.numpy(), y_test_pred, average="macro", zero_division=0))
    test_acc = float(accuracy_score(y_test_t.numpy(), y_test_pred))
    test_kappa = float(cohen_kappa_score(y_test_t.numpy(), y_test_pred))

    weights_hash = compute_weights_hash(model)

    output_data = {
        "run_id": run_id,
        "seed": SEED,
        "elapsed_seconds": elapsed,
        "best_epoch": cb.best_epoch,
        "best_val_macro_f1": cb.best_macro_f1,
        "evaluated_val_macro_f1": val_macro_f1,
        "evaluated_val_accuracy": val_acc,
        "evaluated_test_macro_f1": test_macro_f1,
        "evaluated_test_accuracy": test_acc,
        "evaluated_test_kappa": test_kappa,
        "weights_hash": weights_hash,
        "epoch_history": cb.epoch_history,
    }

    out_file = METRICS_DIR / f"determinism_test_run{run_id}.json"
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nRun {run_id} Complete:")
    print(f"  Best Epoch: {cb.best_epoch}")
    print(f"  Val Macro F1: {val_macro_f1:.6f}")
    print(f"  Test Macro F1: {test_macro_f1:.6f}")
    print(f"  Weights SHA-256: {weights_hash}")
    print(f"  Saved to: {out_file}")


def compare_runs():
    f1 = METRICS_DIR / "determinism_test_run1.json"
    f2 = METRICS_DIR / "determinism_test_run2.json"
    if not f1.exists() or not f2.exists():
        print(f"Cannot compare: missing {f1} or {f2}")
        return False

    with open(f1, "r", encoding="utf-8") as f:
        d1 = json.load(f)
    with open(f2, "r", encoding="utf-8") as f:
        d2 = json.load(f)

    print("\n=======================================================")
    print("DETERMINISM COMPARISON: Run 1 vs Run 2")
    print("=======================================================")
    h1 = d1["epoch_history"]
    h2 = d2["epoch_history"]

    min_len = min(len(h1), len(h2))
    diverged_epoch = None
    first_diff = {}

    for i in range(min_len):
        e1 = h1[i]
        e2 = h2[i]
        diffs = {}
        for k in ["loss", "accuracy", "val_loss", "val_accuracy", "val_macro_f1"]:
            delta = abs(e1[k] - e2[k])
            if delta > 1e-7:
                diffs[k] = (e1[k], e2[k], delta)
        if diffs:
            diverged_epoch = i + 1
            first_diff = diffs
            break

    if len(h1) != len(h2) and diverged_epoch is None:
        diverged_epoch = min_len + 1
        first_diff = {"length": (len(h1), len(h2), abs(len(h1) - len(h2)))}

    weights_match = (d1["weights_hash"] == d2["weights_hash"])
    val_f1_match = abs(d1["evaluated_val_macro_f1"] - d2["evaluated_val_macro_f1"]) < 1e-7
    test_f1_match = abs(d1["evaluated_test_macro_f1"] - d2["evaluated_test_macro_f1"]) < 1e-7

    print(f"Run 1 Best Epoch: {d1['best_epoch']}, Run 2 Best Epoch: {d2['best_epoch']}")
    print(f"Run 1 Val Macro F1: {d1['evaluated_val_macro_f1']:.6f}, Run 2 Val Macro F1: {d2['evaluated_val_macro_f1']:.6f}")
    print(f"Run 1 Test Macro F1: {d1['evaluated_test_macro_f1']:.6f}, Run 2 Test Macro F1: {d2['evaluated_test_macro_f1']:.6f}")
    print(f"Run 1 Weights Hash: {d1['weights_hash']}")
    print(f"Run 2 Weights Hash: {d2['weights_hash']}")
    print(f"Weights Hash Match: {weights_match}")

    if diverged_epoch is None and weights_match and val_f1_match and test_f1_match:
        print("\n>>> DETERMINISM TEST PASSED: Run 1 and Run 2 match EXACTLY across all epochs and weights. <<<")
        return True
    else:
        print(f"\n>>> DETERMINISM TEST FAILED: Divergence detected at Epoch {diverged_epoch} <<<")
        print(f"Differences: {first_diff}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, choices=[1, 2], help="Run ID to execute")
    parser.add_argument("--compare", action="store_true", help="Compare run 1 and run 2")
    args = parser.parse_args()

    if args.compare:
        match = compare_runs()
        sys.exit(0 if match else 1)
    elif args.run:
        run_stage1_determinism(args.run)
    else:
        parser.print_help()

