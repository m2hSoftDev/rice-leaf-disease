"""
src/models/train_m1_seed.py

Trains Stage 1 and Stage 2 end-to-end for a single seed with full determinism enabled.
Executed in a fresh subprocess per seed.
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

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, required=True, help="Random seed to train")
args = parser.parse_args()

SEED = args.seed
enable_determinism(SEED)

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
        print(f"Epoch {epoch + 1} - val_macro_f1: {macro_f1:.4f}")

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
    return tf.keras.Model(inputs=inputs, outputs=outputs, name=f"mobilenetv2_stage1_seed_{seed}")


def main():
    print(f"\n=======================================================")
    print(f"STARTING DETERMINISTIC RUN FOR SEED: {SEED}")
    print(f"=======================================================")
    t_start = time.time()

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

    stage1_ckpt = CHECKPOINT_DIR / f"m1_det_seed{SEED}_stage1.keras"
    stage2_ckpt = CHECKPOINT_DIR / f"m1_det_seed{SEED}_best.keras"

    # --- STAGE 1 ---
    print(f"\n[Seed {SEED} - Stage 1: Frozen Base Head Training]")
    model = build_base_stage1_model(seed=SEED, num_classes=4)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb_stage1 = ValMacroF1EarlyStoppingAndCheckpoint(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=stage1_ckpt,
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
    print(f"Seed {SEED} Stage 1 finished in {s1_sec:.2f}s. Best epoch: {cb_stage1.best_epoch}, best val_macro_f1: {cb_stage1.best_macro_f1:.4f}")

    print(f"Restoring best Stage 1 weights from {stage1_ckpt}...")
    model.load_weights(str(stage1_ckpt))

    # --- STAGE 2 ---
    print(f"\n[Seed {SEED} - Stage 2: Fine-Tuning Last 30 Layers]")
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
        checkpoint_path=stage2_ckpt,
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
    print(f"Seed {SEED} Stage 2 finished in {s2_sec:.2f}s. Best epoch: {best_stage2_epoch}, best val_macro_f1: {best_val_macro_f1:.4f}")

    print(f"Restoring best Stage 2 weights from {stage2_ckpt}...")
    model.load_weights(str(stage2_ckpt))

    # --- EVALUATION ---
    print(f"\n[Seed {SEED} - Evaluation on Val and Test]")
    y_val_pred = np.argmax(model.predict(val_ds, verbose=0), axis=1)
    val_acc = float(accuracy_score(y_val_t.numpy(), y_val_pred))
    val_macro_f1 = float(f1_score(y_val_t.numpy(), y_val_pred, average="macro", zero_division=0))

    y_test_pred = np.argmax(model.predict(test_ds, verbose=0), axis=1)
    test_acc = float(accuracy_score(y_test_t.numpy(), y_test_pred))
    test_macro_f1 = float(f1_score(y_test_t.numpy(), y_test_pred, average="macro", zero_division=0))
    test_kappa = float(cohen_kappa_score(y_test_t.numpy(), y_test_pred))
    test_cm = confusion_matrix(y_test_t.numpy(), y_test_pred, labels=[0, 1, 2, 3])

    bs_idx = CLASS_TO_IDX["Brown Spot"]
    lb_idx = CLASS_TO_IDX["Leaf Blast"]
    bs_to_lb = int(test_cm[bs_idx, lb_idx])

    weights_hash = compute_weights_hash(model)
    total_sec = time.time() - t_start

    result = {
        "seed": SEED,
        "val_macro_f1": val_macro_f1,
        "test_macro_f1": test_macro_f1,
        "test_accuracy": test_acc,
        "test_kappa": test_kappa,
        "best_epoch": int(best_stage2_epoch),
        "stage2_seconds": float(s2_sec),
        "total_seconds": float(total_sec),
        "bs_to_lb_errors": int(bs_to_lb),
        "weights_hash": weights_hash,
    }

    out_json = METRICS_DIR / f"m1_det_seed{SEED}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nSeed {SEED} Finished:")
    print(f"  Val Macro F1:  {val_macro_f1:.4f}")
    print(f"  Test Macro F1: {test_macro_f1:.4f}")
    print(f"  Test Acc:      {test_acc:.4f}")
    print(f"  Test Kappa:    {test_kappa:.4f}")
    print(f"  Best Epoch:    {best_stage2_epoch}")
    print(f"  BS->LB:        {bs_to_lb}")
    print(f"  Weights Hash:  {weights_hash}")
    print(f"  Saved to:      {out_json}")


if __name__ == "__main__":
    main()

