"""
src/models/rerun_seed42.py

Reproducibility check for seed 42 on EXIF-upright data.
- Retrains M1 from scratch with seed 42 (Stage 1 and Stage 2) end-to-end
- Stage 1: Frozen MobileNetV2 base + Dense 128 (ReLU) -> Dropout 0.3 -> Dense 4 (softmax), Adam lr=1e-3
  monitored on val macro F1 (patience 5, max 20 epochs, D-19)
- Stage 2: Unfreeze last 30 layers (BatchNorm frozen, training=False), Adam lr=1e-5
  monitored on val macro F1 (patience 5, max 30 epochs, D-19)
- Saves Stage 2 checkpoint to results/checkpoints/m1_seed42_rerun.keras (git-ignored)
- Does NOT overwrite results/checkpoints/m1_best.keras
- Writes results/metrics/m1_seed42_rerun.csv
- Compares to reused seed 42 metrics:
    val macro F1: 0.8584
    test macro F1: 0.8149
    best epoch: 12
    Brown Spot to Leaf Blast count: 10
"""

import os
import csv
import time
import random
from pathlib import Path
from collections import Counter

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_recall_fscore_support,
    cohen_kappa_score,
    confusion_matrix,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
UPRIGHT_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"
CHECKPOINT_DIR = WORKSPACE_ROOT / "results" / "checkpoints"
STAGE1_CKPT = CHECKPOINT_DIR / "b2_seed42_rerun.keras"
STAGE2_CKPT = CHECKPOINT_DIR / "m1_seed42_rerun.keras"
OUTPUT_CSV = WORKSPACE_ROOT / "results" / "metrics" / "m1_seed42_rerun.csv"

SEED = 42
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
STAGE1_MAX_EPOCHS = 20
STAGE2_MAX_EPOCHS = 30
PATIENCE = 5
STAGE1_LR = 1e-3
STAGE2_LR = 1e-5

CLASS_NAMES = ["Bacterial Leaf Blight", "Brown Spot", "Healthy Rice Leaf", "Leaf Blast"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_NAMES)}

REUSED_VAL_MACRO_F1 = 0.8584
REUSED_TEST_MACRO_F1 = 0.8149
REUSED_BEST_EPOCH = 12
REUSED_BS_TO_LB = 10


def set_seed(seed):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


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
        ds = ds.map(train_map, num_parallel_calls=tf.data.AUTOTUNE)
    else:
        ds = ds.batch(BATCH_SIZE)
        ds = ds.map(eval_map, num_parallel_calls=tf.data.AUTOTUNE)
    return ds.prefetch(tf.data.AUTOTUNE)


class ValMacroF1EarlyStoppingAndCheckpoint(tf.keras.callbacks.Callback):
    def __init__(self, val_dataset, y_val_true, checkpoint_path, patience=5):
        super().__init__()
        self.val_dataset = val_dataset
        self.y_val_true = y_val_true
        self.checkpoint_path = Path(checkpoint_path)
        self.patience = patience
        self.best_macro_f1 = -1.0
        self.best_epoch = 0
        self.wait = 0

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        y_probs = self.model.predict(self.val_dataset, verbose=0)
        y_pred = np.argmax(y_probs, axis=1)
        macro_f1 = float(f1_score(self.y_val_true, y_pred, average="macro", zero_division=0))
        logs["val_macro_f1"] = macro_f1
        print(f" - val_macro_f1: {macro_f1:.4f}")

        if macro_f1 > self.best_macro_f1:
            print(f"val_macro_f1 improved from {self.best_macro_f1:.4f} to {macro_f1:.4f}. Saving checkpoint to {self.checkpoint_path}...")
            self.best_macro_f1 = macro_f1
            self.best_epoch = epoch + 1
            self.wait = 0
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(self.checkpoint_path))
        else:
            self.wait += 1
            print(f"val_macro_f1 ({macro_f1:.4f}) did not improve from {self.best_macro_f1:.4f} (patience: {self.wait}/{self.patience})")
            if self.wait >= self.patience:
                print(f"Early stopping triggered at epoch {epoch + 1}.")
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
    return tf.keras.Model(inputs=inputs, outputs=outputs, name=f"mobilenetv2_upright_seed_{seed}")


def main():
    print("=== Step 2: Reproducibility Check for Seed 42 from Scratch ===")
    set_seed(SEED)

    train_rows, val_rows, test_rows = load_manifest()
    print(f"Loaded active splits: Train={len(train_rows)}, Val={len(val_rows)}, Test={len(test_rows)}")

    X_train_raw, y_train_t = prefetch_in_memory(train_rows, CLASS_TO_IDX)
    X_val_raw, y_val_t = prefetch_in_memory(val_rows, CLASS_TO_IDX)
    X_test_raw, y_test_t = prefetch_in_memory(test_rows, CLASS_TO_IDX)

    y_train_np = y_train_t.numpy()
    classes_present = np.unique(y_train_np)
    weights = compute_class_weight(class_weight="balanced", classes=classes_present, y=y_train_np)
    class_weight_dict = {int(c): float(w) for c, w in zip(classes_present, weights)}
    print(f"Class weights: {class_weight_dict}")

    train_ds = make_dataset(X_train_raw, y_train_t, seed=SEED, is_train=True)
    val_ds = make_dataset(X_val_raw, y_val_t, seed=SEED, is_train=False)
    test_ds = make_dataset(X_test_raw, y_test_t, seed=SEED, is_train=False)

    # --- STAGE 1 ---
    print("\n--- STAGE 1: Head Training on Frozen Base ---")
    model = build_base_stage1_model(seed=SEED, num_classes=4)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb_stage1 = ValMacroF1EarlyStoppingAndCheckpoint(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=STAGE1_CKPT,
        patience=PATIENCE,
    )
    t0_s1 = time.time()
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[cb_stage1],
        verbose=1,
    )
    s1_sec = time.time() - t0_s1
    print(f"Stage 1 finished in {s1_sec:.2f}s. Best epoch: {cb_stage1.best_epoch}, best val_macro_f1: {cb_stage1.best_macro_f1:.4f}")

    print(f"Restoring best Stage 1 weights from {STAGE1_CKPT}...")
    model.load_weights(str(STAGE1_CKPT))

    # --- STAGE 2 ---
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

    cb_stage2 = ValMacroF1EarlyStoppingAndCheckpoint(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=STAGE2_CKPT,
        patience=PATIENCE,
    )
    t0_s2 = time.time()
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE2_MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[cb_stage2],
        verbose=1,
    )
    s2_sec = time.time() - t0_s2
    best_stage2_epoch = cb_stage2.best_epoch
    best_val_macro_f1 = cb_stage2.best_macro_f1
    print(f"Stage 2 finished in {s2_sec:.2f}s. Best epoch: {best_stage2_epoch}, best val_macro_f1: {best_val_macro_f1:.4f}")

    print(f"Restoring best Stage 2 weights from {STAGE2_CKPT}...")
    model.load_weights(str(STAGE2_CKPT))

    # --- EVALUATION ---
    print("\n--- EVALUATION: Validation and Test Splits ---")
    y_val_probs = model.predict(val_ds, verbose=0)
    y_val_pred = np.argmax(y_val_probs, axis=1)
    y_val_true = y_val_t.numpy()

    y_test_probs = model.predict(test_ds, verbose=0)
    y_test_pred = np.argmax(y_test_probs, axis=1)
    y_test_true = y_test_t.numpy()

    # Val metrics
    val_acc = float(accuracy_score(y_val_true, y_val_pred))
    val_macro_f1 = float(f1_score(y_val_true, y_val_pred, average="macro", zero_division=0))
    val_kappa = float(cohen_kappa_score(y_val_true, y_val_pred))
    val_p, val_r, val_f, val_s = precision_recall_fscore_support(y_val_true, y_val_pred, labels=[0, 1, 2, 3], zero_division=0)

    # Test metrics
    test_acc = float(accuracy_score(y_test_true, y_test_pred))
    test_macro_f1 = float(f1_score(y_test_true, y_test_pred, average="macro", zero_division=0))
    test_kappa = float(cohen_kappa_score(y_test_true, y_test_pred))
    test_p, test_r, test_f, test_s = precision_recall_fscore_support(y_test_true, y_test_pred, labels=[0, 1, 2, 3], zero_division=0)

    test_cm = confusion_matrix(y_test_true, y_test_pred, labels=[0, 1, 2, 3])
    bs_idx = CLASS_TO_IDX["Brown Spot"]
    lb_idx = CLASS_TO_IDX["Leaf Blast"]
    bs_to_lb = int(test_cm[bs_idx, lb_idx])

    # Write results/metrics/m1_seed42_rerun.csv
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["split", "class", "precision", "recall", "f1", "support"])
        for i, cname in enumerate(CLASS_NAMES):
            writer.writerow(["val", cname, f"{val_p[i]:.4f}", f"{val_r[i]:.4f}", f"{val_f[i]:.4f}", int(val_s[i])])
        val_macro_p = float(np.mean(val_p))
        val_macro_r = float(np.mean(val_r))
        writer.writerow(["val", "macro_avg", f"{val_macro_p:.4f}", f"{val_macro_r:.4f}", f"{val_macro_f1:.4f}", len(y_val_true)])
        writer.writerow(["val", "accuracy", "N/A", "N/A", f"{val_acc:.4f}", len(y_val_true)])
        writer.writerow(["val", "cohen_kappa", "N/A", "N/A", f"{val_kappa:.4f}", len(y_val_true)])

        for i, cname in enumerate(CLASS_NAMES):
            writer.writerow(["test", cname, f"{test_p[i]:.4f}", f"{test_r[i]:.4f}", f"{test_f[i]:.4f}", int(test_s[i])])
        test_macro_p = float(np.mean(test_p))
        test_macro_r = float(np.mean(test_r))
        writer.writerow(["test", "macro_avg", f"{test_macro_p:.4f}", f"{test_macro_r:.4f}", f"{test_macro_f1:.4f}", len(y_test_true)])
        writer.writerow(["test", "accuracy", "N/A", "N/A", f"{test_acc:.4f}", len(y_test_true)])
        writer.writerow(["test", "cohen_kappa", "N/A", "N/A", f"{test_kappa:.4f}", len(y_test_true)])

        writer.writerow(["summary", "best_epoch", "N/A", "N/A", best_stage2_epoch, "N/A"])
        writer.writerow(["summary", "train_seconds", "N/A", "N/A", f"{s2_sec:.2f}", "N/A"])
        writer.writerow(["summary", "bs_to_lb_errors", "N/A", "N/A", bs_to_lb, "N/A"])

    print(f"\nWrote rerun metrics to {OUTPUT_CSV}")

    # Comparison
    print("\n" + "=" * 60)
    print("REPRODUCIBILITY COMPARISON: Reused Seed 42 vs Seed 42 Rerun")
    print("=" * 60)
    val_diff = val_macro_f1 - REUSED_VAL_MACRO_F1
    test_diff = test_macro_f1 - REUSED_TEST_MACRO_F1
    epoch_diff = best_stage2_epoch - REUSED_BEST_EPOCH
    bs_diff = bs_to_lb - REUSED_BS_TO_LB

    print(f"Validation Macro F1: Reused={REUSED_VAL_MACRO_F1:.4f}, Rerun={val_macro_f1:.4f}, Diff={val_diff:+.4f}")
    print(f"Test Macro F1:       Reused={REUSED_TEST_MACRO_F1:.4f}, Rerun={test_macro_f1:.4f}, Diff={test_diff:+.4f}")
    print(f"Test Accuracy:       Reused=0.7971, Rerun={test_acc:.4f}, Diff={test_acc - 0.7971:+.4f}")
    print(f"Test Cohen's Kappa:  Reused=0.7246, Rerun={test_kappa:.4f}, Diff={test_kappa - 0.7246:+.4f}")
    print(f"Best Epoch (Stage 2):Reused={REUSED_BEST_EPOCH}, Rerun={best_stage2_epoch}, Diff={epoch_diff:+d}")
    print(f"BS -> LB Errors:     Reused={REUSED_BS_TO_LB}, Rerun={bs_to_lb}, Diff={bs_diff:+d}")
    print("=" * 60)


if __name__ == "__main__":
    main()
