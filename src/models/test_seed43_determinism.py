"""
src/models/test_seed43_determinism.py

Tests full end-to-end determinism (Stage 1 + Stage 2) for seed 43 across two fresh processes.
Outputs epoch-by-epoch loss, val macro F1, test macro F1, and weights hash.
"""

import sys
import os
import csv
import json
import time
import argparse
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.utils.determinism import enable_determinism, compute_weights_hash

SEED = 43
enable_determinism(SEED)

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    cohen_kappa_score,
    confusion_matrix,
)

MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
UPRIGHT_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"
CHECKPOINT_DIR = WORKSPACE_ROOT / "results" / "checkpoints"
METRICS_DIR = WORKSPACE_ROOT / "results" / "metrics"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
STAGE1_MAX_EPOCHS = 20
STAGE2_MAX_EPOCHS = 30
PATIENCE = 5
STAGE1_LR = 1e-3
STAGE2_LR = 1e-5

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


class DetailedEpochCallback(tf.keras.callbacks.Callback):
    def __init__(self, val_dataset, y_val_true, checkpoint_path, stage_name, patience=5):
        super().__init__()
        self.val_dataset = val_dataset
        self.y_val_true = y_val_true
        self.checkpoint_path = Path(checkpoint_path)
        self.stage_name = stage_name
        self.patience = patience
        self.best_macro_f1 = -1.0
        self.best_epoch = 0
        self.wait = 0
        self.history = []

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        y_probs = self.model.predict(self.val_dataset, verbose=0)
        y_pred = np.argmax(y_probs, axis=1)
        macro_f1 = float(f1_score(self.y_val_true, y_pred, average="macro", zero_division=0))
        logs["val_macro_f1"] = macro_f1

        record = {
            "epoch": epoch + 1,
            "loss": float(logs.get("loss", 0.0)),
            "accuracy": float(logs.get("accuracy", 0.0)),
            "val_loss": float(logs.get("val_loss", 0.0)),
            "val_accuracy": float(logs.get("val_accuracy", 0.0)),
            "val_macro_f1": macro_f1,
        }
        self.history.append(record)
        print(f"[{self.stage_name}] Epoch {epoch + 1}: loss={record['loss']:.6f}, val_loss={record['val_loss']:.6f}, val_macro_f1={macro_f1:.6f}")

        if macro_f1 > self.best_macro_f1:
            self.best_macro_f1 = macro_f1
            self.best_epoch = epoch + 1
            self.wait = 0
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(self.checkpoint_path))
        else:
            self.wait += 1
            if self.wait >= self.patience:
                print(f"[{self.stage_name}] Early stopping at epoch {epoch + 1}")
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


def run_pipeline(run_id: int):
    print(f"\n=======================================================")
    print(f"SEED 43 DETERMINISM TEST: RUN {run_id}")
    print(f"=======================================================")
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

    ckpt_s1 = CHECKPOINT_DIR / f"test_seed43_run{run_id}_stage1.keras"
    ckpt_s2 = CHECKPOINT_DIR / f"test_seed43_run{run_id}_stage2.keras"

    # Stage 1
    print("\n--- STAGE 1: Head Training on Frozen Base ---")
    model = build_base_stage1_model(seed=SEED, num_classes=4)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb_s1 = DetailedEpochCallback(val_ds, y_val_t.numpy(), ckpt_s1, "Stage1", PATIENCE)
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[cb_s1],
        verbose=1,
    )

    model.load_weights(str(ckpt_s1))
    s1_weights_hash = compute_weights_hash(model)

    # Stage 2
    print("\n--- STAGE 2: Fine-Tuning Last 30 Layers ---")
    base_model = None
    for l in model.layers:
        if "mobilenetv2" in l.name.lower():
            base_model = l
            break

    base_model.trainable = True
    for l in base_model.layers[:-30]:
        l.trainable = False
    for l in base_model.layers[-30:]:
        if isinstance(l, tf.keras.layers.BatchNormalization):
            l.trainable = False
        else:
            l.trainable = True

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE2_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb_s2 = DetailedEpochCallback(val_ds, y_val_t.numpy(), ckpt_s2, "Stage2", PATIENCE)
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE2_MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[cb_s2],
        verbose=1,
    )

    model.load_weights(str(ckpt_s2))
    s2_weights_hash = compute_weights_hash(model)

    # Evaluation
    print("\n--- FINAL EVALUATION ---")
    y_val_pred = np.argmax(model.predict(val_ds, verbose=0), axis=1)
    val_macro_f1 = float(f1_score(y_val_t.numpy(), y_val_pred, average="macro", zero_division=0))
    val_acc = float(accuracy_score(y_val_t.numpy(), y_val_pred))

    y_test_pred = np.argmax(model.predict(test_ds, verbose=0), axis=1)
    test_macro_f1 = float(f1_score(y_test_t.numpy(), y_test_pred, average="macro", zero_division=0))
    test_acc = float(accuracy_score(y_test_t.numpy(), y_test_pred))
    test_kappa = float(cohen_kappa_score(y_test_t.numpy(), y_test_pred))
    test_cm = confusion_matrix(y_test_t.numpy(), y_test_pred, labels=[0, 1, 2, 3])
    bs_to_lb = int(test_cm[CLASS_TO_IDX["Brown Spot"], CLASS_TO_IDX["Leaf Blast"]])

    result = {
        "run_id": run_id,
        "seed": SEED,
        "stage1_best_epoch": cb_s1.best_epoch,
        "stage1_best_val_macro_f1": cb_s1.best_macro_f1,
        "stage1_weights_hash": s1_weights_hash,
        "stage1_history": cb_s1.history,
        "stage2_best_epoch": cb_s2.best_epoch,
        "stage2_best_val_macro_f1": cb_s2.best_macro_f1,
        "stage2_weights_hash": s2_weights_hash,
        "stage2_history": cb_s2.history,
        "evaluated_val_macro_f1": val_macro_f1,
        "evaluated_val_accuracy": val_acc,
        "evaluated_test_macro_f1": test_macro_f1,
        "evaluated_test_accuracy": test_acc,
        "evaluated_test_kappa": test_kappa,
        "bs_to_lb_errors": bs_to_lb,
    }

    out_file = METRICS_DIR / f"det_seed43_run{run_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nRun {run_id} Results Saved to {out_file}:")
    print(f"  Stage 1 Best Epoch: {cb_s1.best_epoch}, Val Macro F1: {cb_s1.best_macro_f1:.6f}")
    print(f"  Stage 2 Best Epoch: {cb_s2.best_epoch}, Val Macro F1: {cb_s2.best_macro_f1:.6f}")
    print(f"  Final Val Macro F1:  {val_macro_f1:.6f}")
    print(f"  Final Test Macro F1: {test_macro_f1:.6f}")
    print(f"  Stage 2 Weights Hash: {s2_weights_hash}")


def compare():
    f1 = METRICS_DIR / "det_seed43_run1.json"
    f2 = METRICS_DIR / "det_seed43_run2.json"
    if not f1.exists() or not f2.exists():
        print(f"Missing {f1} or {f2}")
        return False

    with open(f1, "r", encoding="utf-8") as f:
        d1 = json.load(f)
    with open(f2, "r", encoding="utf-8") as f:
        d2 = json.load(f)

    print("\n=======================================================")
    print("SEED 43 FULL PIPELINE DETERMINISM COMPARISON (Run 1 vs Run 2)")
    print("=======================================================")

    diverged_stage = None
    diverged_epoch = None
    first_diff = {}

    for stage_name, h_key in [("Stage 1", "stage1_history"), ("Stage 2", "stage2_history")]:
        h1 = d1[h_key]
        h2 = d2[h_key]
        min_len = min(len(h1), len(h2))
        for i in range(min_len):
            e1 = h1[i]
            e2 = h2[i]
            diffs = {}
            for k in ["loss", "accuracy", "val_loss", "val_accuracy", "val_macro_f1"]:
                delta = abs(e1[k] - e2[k])
                if delta > 1e-7:
                    diffs[k] = (e1[k], e2[k], delta)
            if diffs:
                diverged_stage = stage_name
                diverged_epoch = i + 1
                first_diff = diffs
                break
        if diverged_stage:
            break
        if len(h1) != len(h2):
            diverged_stage = stage_name
            diverged_epoch = min_len + 1
            first_diff = {"length": (len(h1), len(h2), abs(len(h1) - len(h2)))}
            break

    s1_weights_match = (d1["stage1_weights_hash"] == d2["stage1_weights_hash"])
    s2_weights_match = (d1["stage2_weights_hash"] == d2["stage2_weights_hash"])
    val_f1_match = abs(d1["evaluated_val_macro_f1"] - d2["evaluated_val_macro_f1"]) < 1e-7
    test_f1_match = abs(d1["evaluated_test_macro_f1"] - d2["evaluated_test_macro_f1"]) < 1e-7

    print(f"Run 1 Stage 1 Best Epoch: {d1['stage1_best_epoch']}, Run 2: {d2['stage1_best_epoch']}")
    print(f"Run 1 Stage 2 Best Epoch: {d1['stage2_best_epoch']}, Run 2: {d2['stage2_best_epoch']}")
    print(f"Run 1 Val Macro F1:       {d1['evaluated_val_macro_f1']:.6f}, Run 2: {d2['evaluated_val_macro_f1']:.6f}")
    print(f"Run 1 Test Macro F1:      {d1['evaluated_test_macro_f1']:.6f}, Run 2: {d2['evaluated_test_macro_f1']:.6f}")
    print(f"Run 1 Stage 1 Hash:       {d1['stage1_weights_hash']}")
    print(f"Run 2 Stage 1 Hash:       {d2['stage1_weights_hash']}")
    print(f"Run 1 Stage 2 Hash:       {d1['stage2_weights_hash']}")
    print(f"Run 2 Stage 2 Hash:       {d2['stage2_weights_hash']}")
    print(f"Stage 1 Weights Match:    {s1_weights_match}")
    print(f"Stage 2 Weights Match:    {s2_weights_match}")
    print(f"Val & Test F1 Match:      {val_f1_match and test_f1_match}")

    if diverged_stage is None and s1_weights_match and s2_weights_match and val_f1_match and test_f1_match:
        print("\n>>> SEED 43 FULL DETERMINISM PASSED: 100% Exact match across Stage 1, Stage 2, and final weights! <<<")
        return True
    else:
        print(f"\n>>> SEED 43 DETERMINISM FAILED: Divergence in {diverged_stage} at Epoch {diverged_epoch} <<<")
        print(f"Differences: {first_diff}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, choices=[1, 2], help="Run ID to execute")
    parser.add_argument("--compare", action="store_true", help="Compare run 1 and run 2")
    args = parser.parse_args()

    if args.compare:
        match = compare()
        sys.exit(0 if match else 1)
    elif args.run:
        run_pipeline(args.run)
    else:
        parser.print_help()

