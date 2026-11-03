"""
src/models/train_m1.py

Stage 2 fine-tuning for Main Model M1 (T-030).
- Loads B2 best checkpoint from results/checkpoints/b2_best.keras (epoch 4, val_macro_f1=0.7670 per D-19)
- Unfreezes only the last 30 layers of MobileNetV2
- Keeps all BatchNorm layers frozen and base model called with training=False
- Recompiles with Adam lr=1e-5
- Prints trainable parameter count before and after unfreezing
- Dataset: data/metadata/split_manifest.csv only (4 classes, Hasan originals)
- Augmentation: train split only per Section 8.2 (rotation, flip, zoom, brightness, contrast)
- Class weights from train split; seed 42 everywhere
- Early stopping & ModelCheckpoint on val macro F1 (patience 5, max 30 epochs, per D-19)
- Saves best checkpoint to results/checkpoints/m1_best.keras (git-ignored, does not overwrite b2_best.keras)
- Evaluates on val and test once after training ends
- Outputs:
    results/metrics/m1.csv
    results/metrics/m1.md (with B0, B1, B2 beside M1)
    results/figures/m1_confusion.png (git-ignored)
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 1. Reproducibility: Seed 42 everywhere
RANDOM_SEED = 42
os.environ["PYTHONHASHSEED"] = str(RANDOM_SEED)
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
STAGING_DIR = WORKSPACE_ROOT / "data" / "raw" / "public" / "hasan_staging" / "Original Images"

B2_CHECKPOINT_PATH = WORKSPACE_ROOT / "results" / "checkpoints" / "b2_best.keras"
CHECKPOINT_DIR = WORKSPACE_ROOT / "results" / "checkpoints"
M1_CHECKPOINT_PATH = CHECKPOINT_DIR / "m1_best.keras"

METRICS_DIR = WORKSPACE_ROOT / "results" / "metrics"
OUTPUT_CSV = METRICS_DIR / "m1.csv"
OUTPUT_MD = METRICS_DIR / "m1.md"
BASELINES_CSV = METRICS_DIR / "baselines.csv"

FIGURES_DIR = WORKSPACE_ROOT / "results" / "figures"
CONFUSION_PNG = FIGURES_DIR / "m1_confusion.png"

# Hyperparameters for Stage 2
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
MAX_EPOCHS = 30
PATIENCE = 5
STAGE2_LEARNING_RATE = 1e-5
GATE_2_THRESHOLD = 0.80

# Prior Baselines for comparison
B0_TEST_MACRO_F1 = 0.1230
B0_TEST_ACC = 0.3261
B0_VAL_MACRO_F1 = 0.1271
B0_VAL_ACC = 0.3407
B0_TEST_KAPPA = 0.0000

B1_TEST_MACRO_F1 = 0.0669
B1_TEST_ACC = 0.1304
B1_VAL_MACRO_F1 = 0.1012
B1_VAL_ACC = 0.1926
B1_TEST_KAPPA = -0.0504

B2_TEST_MACRO_F1 = 0.7369
B2_TEST_ACC = 0.7101
B2_VAL_MACRO_F1 = 0.7670
B2_VAL_ACC = 0.7630
B2_TEST_KAPPA = 0.6051


def load_manifest():
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    train_rows = []
    val_rows = []
    test_rows = []

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sp = r["split"]
            if sp == "train":
                train_rows.append(r)
            elif sp == "val":
                val_rows.append(r)
            elif sp == "test":
                test_rows.append(r)

    print(f"Loaded manifest - Train: {len(train_rows)}, Val: {len(val_rows)}, Test: {len(test_rows)}")
    assert len(train_rows) == 634
    assert len(val_rows) == 135
    assert len(test_rows) == 138

    return train_rows, val_rows, test_rows


def get_data_augmentation():
    """Augmentation per Section 8.2: rotation +-30 deg, flip, zoom 0.8-1.2, brightness/contrast +-20%."""
    return tf.keras.Sequential([
        tf.keras.layers.RandomRotation(30.0 / 360.0, seed=RANDOM_SEED),
        tf.keras.layers.RandomFlip("horizontal_and_vertical", seed=RANDOM_SEED),
        tf.keras.layers.RandomZoom((-0.2, 0.2), seed=RANDOM_SEED),
        tf.keras.layers.RandomBrightness(0.2, value_range=(0.0, 255.0), seed=RANDOM_SEED),
        tf.keras.layers.RandomContrast(0.2, seed=RANDOM_SEED),
    ], name="data_augmentation")


def prefetch_in_memory(rows, class_to_idx):
    """Loads and decodes raw images once into memory tensors for fast execution."""
    print(f"Pre-loading {len(rows)} images into RAM...")
    images_list = []
    labels_list = []
    for r in rows:
        p = STAGING_DIR / r["class"] / r["filename"]
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {p}")
        raw = tf.io.read_file(str(p))
        img = tf.image.decode_jpeg(raw, channels=3)
        img = tf.image.resize(img, IMG_SIZE, method="bilinear")
        images_list.append(img)
        labels_list.append(class_to_idx[r["class"]])

    images_tensor = tf.stack(images_list)
    labels_tensor = tf.convert_to_tensor(labels_list, dtype=tf.int32)
    print(f"Loaded tensor shape: {images_tensor.shape}, labels: {labels_tensor.shape}")
    return images_tensor, labels_tensor


def make_dataset_from_tensors(images_tensor, labels_tensor, is_train=False):
    """Creates a batch-optimized tf.data.Dataset from in-memory tensors."""
    aug = get_data_augmentation()

    def train_step_map(batch_x, batch_y):
        batch_x = aug(batch_x, training=True)
        batch_x = tf.keras.applications.mobilenet_v2.preprocess_input(batch_x)
        return batch_x, batch_y

    def eval_step_map(batch_x, batch_y):
        batch_x = tf.keras.applications.mobilenet_v2.preprocess_input(batch_x)
        return batch_x, batch_y

    ds = tf.data.Dataset.from_tensor_slices((images_tensor, labels_tensor))

    if is_train:
        ds = ds.shuffle(buffer_size=len(images_tensor), seed=RANDOM_SEED, reshuffle_each_iteration=True)
        ds = ds.batch(BATCH_SIZE)
        ds = ds.map(train_step_map, num_parallel_calls=tf.data.AUTOTUNE)
    else:
        ds = ds.batch(BATCH_SIZE)
        ds = ds.map(eval_step_map, num_parallel_calls=tf.data.AUTOTUNE)

    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


class ValMacroF1EarlyStoppingAndCheckpoint(tf.keras.callbacks.Callback):
    """Custom callback per D-19: selects best checkpoint and stops early based on validation macro F1."""
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
            print(f"val_macro_f1 improved from {self.best_macro_f1:.4f} to {macro_f1:.4f}. Saving best model to {self.checkpoint_path}...")
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


def evaluate_split(model, eval_ds, y_true, idx_to_class):
    """Evaluates model on given evaluation dataset."""
    classes = [idx_to_class[i] for i in range(len(idx_to_class))]
    y_pred_probs = model.predict(eval_ds, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(classes))))

    prec, rec, f1, supp = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(classes))), zero_division=0
    )

    per_class = {}
    for idx, cls in enumerate(classes):
        per_class[cls] = {
            "precision": float(prec[idx]),
            "recall": float(rec[idx]),
            "f1": float(f1[idx]),
            "support": int(supp[idx]),
        }

    return {
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "macro_precision": float(np.mean(prec)),
        "macro_recall": float(np.mean(rec)),
        "cohen_kappa": float(kappa),
        "confusion_matrix": cm,
        "per_class": per_class,
        "total": len(y_true),
    }


def plot_confusion_matrices(val_cm, test_cm, classes, save_path):
    """Plots side-by-side confusion matrices for validation and test splits."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, cm, title in zip(axes, [val_cm, test_cm], ["Validation Confusion Matrix", "Test Confusion Matrix"]):
        im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        tick_marks = np.arange(len(classes))
        short_names = [c.replace(" ", "\n") for c in classes]
        ax.set_xticks(tick_marks)
        ax.set_xticklabels(short_names, fontsize=9)
        ax.set_yticks(tick_marks)
        ax.set_yticklabels(short_names, fontsize=9)

        # Print text inside cells
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontsize=11, fontweight="bold",
                )

        ax.set_ylabel("True Label", fontsize=11, labelpad=8)
        ax.set_xlabel("Predicted Label", fontsize=11, labelpad=8)

    plt.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved confusion matrix figure: {save_path}")


def main():
    print("=== T-030: Main Model M1 Stage 2 Fine-Tuning ===")
    start_time = time.time()

    # Detect hardware
    gpus = tf.config.list_physical_devices("GPU")
    hardware_str = f"GPU ({len(gpus)} device)" if gpus else "CPU (oneDNN optimized)"
    print(f"Hardware: {hardware_str}")

    # Load data manifest
    train_rows, val_rows, test_rows = load_manifest()
    classes = sorted(list({r["class"] for r in train_rows}))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    print(f"Classes ({len(classes)}): {classes}")

    # Class weights from train split
    y_train = np.array([class_to_idx[r["class"]] for r in train_rows])
    weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
    class_weight_dict = {i: float(w) for i, w in enumerate(weights)}
    print("Class weights (train):")
    for cls, idx in class_to_idx.items():
        print(f"  {cls} (class {idx}): count={Counter(y_train)[idx]}, weight={class_weight_dict[idx]:.4f}")

    # Pre-load image tensors into memory
    X_train_raw, y_train_t = prefetch_in_memory(train_rows, class_to_idx)
    X_val_raw, y_val_t = prefetch_in_memory(val_rows, class_to_idx)
    X_test_raw, y_test_t = prefetch_in_memory(test_rows, class_to_idx)

    train_ds = make_dataset_from_tensors(X_train_raw, y_train_t, is_train=True)
    val_ds = make_dataset_from_tensors(X_val_raw, y_val_t, is_train=False)
    test_ds = make_dataset_from_tensors(X_test_raw, y_test_t, is_train=False)

    # 1. Load B2 best checkpoint
    if not B2_CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"B2 best checkpoint not found: {B2_CHECKPOINT_PATH}")
    print(f"\nLoading starting weights from B2 best checkpoint: {B2_CHECKPOINT_PATH}")
    model = tf.keras.models.load_model(str(B2_CHECKPOINT_PATH))

    # Parameter count BEFORE unfreezing
    trainable_before = sum([tf.size(w).numpy() for w in model.trainable_weights])
    non_trainable_before = sum([tf.size(w).numpy() for w in model.non_trainable_weights])
    total_before = trainable_before + non_trainable_before
    print(f"\n[Parameter Count BEFORE Unfreezing]")
    print(f"  Trainable params:     {trainable_before:,}")
    print(f"  Non-trainable params: {non_trainable_before:,}")
    print(f"  Total params:         {total_before:,}")

    # 2. Unfreeze only last 30 layers of MobileNetV2, keep all BatchNorm frozen
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break
    if base_model is None:
        raise ValueError("MobileNetV2 base model layer not found in loaded model!")

    base_model.trainable = True
    # Freeze all layers except last 30
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    # For last 30 layers, keep BatchNorm frozen
    for layer in base_model.layers[-30:]:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
        else:
            layer.trainable = True

    # Parameter count AFTER unfreezing
    trainable_after = sum([tf.size(w).numpy() for w in model.trainable_weights])
    non_trainable_after = sum([tf.size(w).numpy() for w in model.non_trainable_weights])
    total_after = trainable_after + non_trainable_after
    print(f"\n[Parameter Count AFTER Unfreezing (Last 30 Layers)]")
    print(f"  Trainable params:     {trainable_after:,}")
    print(f"  Non-trainable params: {non_trainable_after:,}")
    print(f"  Total params:         {total_after:,}")
    assert trainable_after > trainable_before, "Trainable parameters must increase after unfreezing!"

    # 3. Recompile with Adam lr 1e-5
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE2_LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    print(f"Recompiled model with Adam(lr={STAGE2_LEARNING_RATE})")

    # Callbacks (D-19: val macro F1 selection and early stopping)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    f1_cb = ValMacroF1EarlyStoppingAndCheckpoint(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=M1_CHECKPOINT_PATH,
        patience=PATIENCE,
    )

    print("\nStarting Stage 2 training (max 30 epochs, patience 5 on val macro F1 per D-19)...")
    train_start = time.time()
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=MAX_EPOCHS,
        class_weight=class_weight_dict,
        callbacks=[f1_cb],
        verbose=1,
    )
    total_train_sec = time.time() - train_start
    epochs_run = len(history.history["loss"])
    best_epoch_idx = f1_cb.best_epoch
    best_val_macro_f1 = f1_cb.best_macro_f1

    print(f"\nStage 2 training finished in {total_train_sec:.2f}s ({epochs_run} epochs run).")
    print(f"Best model selected from epoch {best_epoch_idx} with val_macro_f1: {best_val_macro_f1:.4f}")

    # Restore best checkpoint weights strictly from validation
    print(f"Restoring best checkpoint from {M1_CHECKPOINT_PATH}...")
    model.load_weights(str(M1_CHECKPOINT_PATH))

    # Evaluate on val and test
    print("\nEvaluating on validation set...")
    val_metrics = evaluate_split(model, val_ds, y_val_t.numpy(), idx_to_class)
    print(f"Val Accuracy: {val_metrics['accuracy']:.4f}, Val Macro F1: {val_metrics['macro_f1']:.4f}, Kappa: {val_metrics['cohen_kappa']:.4f}")

    print("\nEvaluating on test set (held-out)...")
    test_metrics = evaluate_split(model, test_ds, y_test_t.numpy(), idx_to_class)
    print(f"Test Accuracy: {test_metrics['accuracy']:.4f}, Test Macro F1: {test_metrics['macro_f1']:.4f}, Kappa: {test_metrics['cohen_kappa']:.4f}")

    # Gate 2 Check
    gate_2_met = test_metrics["macro_f1"] >= GATE_2_THRESHOLD
    gate_2_status_str = "MET" if gate_2_met else "NOT MET"
    print(f"\n==========================================")
    print(f"QUALITY GATE 2 STATUS: {gate_2_status_str}")
    print(f"Test Macro F1: {test_metrics['macro_f1']:.4f} (Threshold: {GATE_2_THRESHOLD:.4f})")
    print(f"==========================================\n")

    # Plot and save confusion matrices
    plot_confusion_matrices(
        val_metrics["confusion_matrix"],
        test_metrics["confusion_matrix"],
        classes,
        CONFUSION_PNG,
    )

    # Save CSV
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    csv_rows = []
    for sp_name, m in [("val", val_metrics), ("test", test_metrics)]:
        for cls in classes:
            cm = m["per_class"][cls]
            csv_rows.append({
                "split": sp_name,
                "class": cls,
                "precision": f"{cm['precision']:.4f}",
                "recall": f"{cm['recall']:.4f}",
                "f1": f"{cm['f1']:.4f}",
                "support": cm["support"],
            })
        csv_rows.append({
            "split": sp_name,
            "class": "macro_avg",
            "precision": f"{m['macro_precision']:.4f}",
            "recall": f"{m['macro_recall']:.4f}",
            "f1": f"{m['macro_f1']:.4f}",
            "support": m["total"],
        })
        csv_rows.append({
            "split": sp_name,
            "class": "accuracy",
            "precision": "N/A",
            "recall": "N/A",
            "f1": f"{m['accuracy']:.4f}",
            "support": m["total"],
        })
        csv_rows.append({
            "split": sp_name,
            "class": "cohen_kappa",
            "precision": "N/A",
            "recall": "N/A",
            "f1": f"{m['cohen_kappa']:.4f}",
            "support": m["total"],
        })

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["split", "class", "precision", "recall", "f1", "support"])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Saved metrics CSV: {OUTPUT_CSV}")

    # Confusion breakdown: Brown Spot (index 1) to Leaf Blast (index 3)
    test_cm = test_metrics["confusion_matrix"]
    bs_idx = class_to_idx["Brown Spot"]
    lb_idx = class_to_idx["Leaf Blast"]
    bs_to_lb_count = int(test_cm[bs_idx, lb_idx])
    bs_total = int(np.sum(test_cm[bs_idx, :]))
    bs_correct = int(test_cm[bs_idx, bs_idx])
    bs_missed = bs_total - bs_correct

    # Build Markdown report
    md_lines = [
        "# Main Model M1: Stage 2 Fine-Tuned MobileNetV2",
        "",
        "## Model Configuration",
        "- **Base Checkpoint**: Initialized from `results/checkpoints/b2_best.keras` (B2 epoch 4, val_macro_f1=0.7670, D-19)",
        f"- **Unfreezing Policy**: Last 30 layers unfrozen (BatchNorm frozen, base called with `training=False`)",
        f"- **Trainable Parameters**: {trainable_after:,} (increased from {trainable_before:,})",
        f"- **Non-Trainable Parameters**: {non_trainable_after:,}",
        f"- **Total Parameters**: {total_after:,}",
        "- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)",
        "- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)",
        "- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-5, balanced class weights",
        "- **Checkpoint Selection & Early Stopping**: Selected by validation macro F1 (patience 5, max 30 epochs, D-19)",
        f"- **Epochs Run**: {epochs_run} (best epoch: {best_epoch_idx})",
        f"- **Training Time**: {total_train_sec:.2f} seconds ({total_train_sec / 60.0:.2f} min)",
        f"- **Hardware**: {hardware_str}",
        "",
        "## Gate 2 Evaluation (Threshold: Test Macro F1 >= 0.80)",
        f"- **Gate 2 Status**: **{gate_2_status_str}**",
        f"- **Test Macro F1**: **{test_metrics['macro_f1']:.4f}** (Target: {GATE_2_THRESHOLD:.4f})",
        f"- **Test Accuracy**: **{test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.2f}%)**",
        f"- **Test Cohen's Kappa**: **{test_metrics['cohen_kappa']:.4f}**",
        "",
        "## Comparison with Baselines B0, B1, and B2",
        "",
        "| Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |",
        "|---|---|---|---|---|---|",
        f"| **B0 (Majority: Leaf Blast)** | {B0_VAL_ACC:.4f} ({B0_VAL_ACC*100:.2f}%) | {B0_VAL_MACRO_F1:.4f} | {B0_TEST_ACC:.4f} ({B0_TEST_ACC*100:.2f}%) | **{B0_TEST_MACRO_F1:.4f}** | {B0_TEST_KAPPA:.4f} |",
        f"| **B1 (Small CNN from Scratch)** | {B1_VAL_ACC:.4f} ({B1_VAL_ACC*100:.2f}%) | {B1_VAL_MACRO_F1:.4f} | {B1_TEST_ACC:.4f} ({B1_TEST_ACC*100:.2f}%) | **{B1_TEST_MACRO_F1:.4f}** | {B1_TEST_KAPPA:.4f} |",
        f"| **B2 (Frozen MobileNetV2 Stage 1)** | {B2_VAL_ACC:.4f} ({B2_VAL_ACC*100:.2f}%) | {B2_VAL_MACRO_F1:.4f} | {B2_TEST_ACC:.4f} ({B2_TEST_ACC*100:.2f}%) | **{B2_TEST_MACRO_F1:.4f}** | {B2_TEST_KAPPA:.4f} |",
        f"| **M1 (Fine-Tuned MobileNetV2 Stage 2)** | {val_metrics['accuracy']:.4f} ({val_metrics['accuracy']*100:.2f}%) | {val_metrics['macro_f1']:.4f} | {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.2f}%) | **{test_metrics['macro_f1']:.4f}** | {test_metrics['cohen_kappa']:.4f} |",
        "",
        "## Detailed Per-Class Breakdown (M1)",
        "",
        "### Validation Split (N=135)",
        "",
        "| Class | Precision | Recall | F1-Score | Support |",
        "|---|---|---|---|---|",
    ]
    for cls in classes:
        cm = val_metrics["per_class"][cls]
        md_lines.append(f"| {cls} | {cm['precision']:.4f} | {cm['recall']:.4f} | {cm['f1']:.4f} | {cm['support']} |")
    md_lines.append(f"| **Macro Average** | **{val_metrics['macro_precision']:.4f}** | **{val_metrics['macro_recall']:.4f}** | **{val_metrics['macro_f1']:.4f}** | **{val_metrics['total']}** |")

    md_lines.extend([
        "",
        "### Test Split (N=138)",
        "",
        "| Class | Precision | Recall | F1-Score | Support |",
        "|---|---|---|---|---|",
    ])
    for cls in classes:
        cm = test_metrics["per_class"][cls]
        md_lines.append(f"| {cls} | {cm['precision']:.4f} | {cm['recall']:.4f} | {cm['f1']:.4f} | {cm['support']} |")
    md_lines.append(f"| **Macro Average** | **{test_metrics['macro_precision']:.4f}** | **{test_metrics['macro_recall']:.4f}** | **{test_metrics['macro_f1']:.4f}** | **{test_metrics['total']}** |")

    md_lines.extend([
        "",
        "## Confusion Matrices",
        "",
        "### Validation Confusion Matrix (Rows=True, Cols=Pred)",
        "```",
        np.array2string(val_metrics["confusion_matrix"]),
        "```",
        "",
        "### Test Confusion Matrix (Rows=True, Cols=Pred)",
        "```",
        np.array2string(test_metrics["confusion_matrix"]),
        "```",
        "",
        "Figure saved to `results/figures/m1_confusion.png` (git-ignored).",
        "",
        "## Brown Spot to Leaf Blast Confusion Analysis",
        f"- Total Brown Spot test images: {bs_total}",
        f"- Correctly identified Brown Spot: {bs_correct} (Recall: {bs_correct/bs_total*100:.2f}%)",
        f"- Total missed Brown Spot images: {bs_missed}",
        f"- Misclassified as Leaf Blast in M1: **{bs_to_lb_count}** images ({bs_to_lb_count/bs_missed*100:.2f}% of missed Brown Spot)",
        f"- Comparison with Baseline B2: B2 had **18** Brown Spot -> Leaf Blast errors (M1 count: **{bs_to_lb_count}**).",
        "",
        "## Analysis and Findings",
        f"1. Stage 2 fine-tuning achieved Test Macro F1 of {test_metrics['macro_f1']:.4f} (Accuracy: {test_metrics['accuracy']*100:.2f}%) on held-out test data.",
        f"2. Quality Gate 2 (Macro F1 >= 0.80) is **{gate_2_status_str}**.",
        "3. Selection by validation macro F1 (D-19) strictly guarded against test leakage and balanced performance across all four classes.",
    ])

    md_text = "\n".join(md_lines) + "\n"

    # Assert required comparisons
    assert f"{B0_TEST_MACRO_F1:.4f}" in md_text
    assert f"{B1_TEST_MACRO_F1:.4f}" in md_text
    assert f"{B2_TEST_MACRO_F1:.4f}" in md_text
    assert f"{test_metrics['macro_f1']:.4f}" in md_text

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"Saved metrics Markdown: {OUTPUT_MD}")

    return {
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "epochs_run": epochs_run,
        "best_epoch": best_epoch_idx,
        "train_time_sec": total_train_sec,
        "hardware": hardware_str,
        "gate_2_met": gate_2_met,
        "trainable_before": trainable_before,
        "trainable_after": trainable_after,
        "bs_to_lb_count": bs_to_lb_count,
    }


if __name__ == "__main__":
    main()

