"""
src/models/baseline_b2.py

Trains and evaluates Baseline B2 (Frozen MobileNetV2 base, Stage 1 only) for T-023.
- Contract: RGB, 224x224 bilinear, mobilenet_v2.preprocess_input (Section 8.1)
- Base: MobileNetV2, ImageNet weights, alpha 1.0, fully frozen
- Head: Dense 128 (ReLU) -> Dropout 0.3 -> Dense 4 (softmax) (Section 8.3, D-14)
- Augmentation: training set only, per Section 8.2 (rotation, flip, zoom, brightness, contrast)
- Class weights from train split; seed 42 everywhere
- Optimizer: Adam lr=1e-3, max 20 epochs
- Checkpoint & EarlyStopping: monitored on validation macro F1 with patience 5 (D-19)
- Best checkpoint saved to results/checkpoints/b2_best.keras (git-ignored)
- Evaluates on val and held-out test once training finishes
- Outputs:
    results/metrics/baseline_b2.csv
    results/metrics/baseline_b2.md (with B0 and B1 test macro F1 beside it)
    results/figures/b2_confusion.png (git-ignored)
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
UPRIGHT_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"

CHECKPOINT_DIR = WORKSPACE_ROOT / "results" / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "b2_best.keras"

METRICS_DIR = WORKSPACE_ROOT / "results" / "metrics"
OUTPUT_CSV = METRICS_DIR / "baseline_b2.csv"
OUTPUT_MD = METRICS_DIR / "baseline_b2.md"

FIGURES_DIR = WORKSPACE_ROOT / "results" / "figures"
CONFUSION_PNG = FIGURES_DIR / "b2_confusion.png"

# Hyperparameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
MAX_EPOCHS = 20
PATIENCE = 5
LEARNING_RATE = 1e-3

# Previous Baselines for comparison
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

B2_SUPERSEDED_VAL_ACC = 0.7630
B2_SUPERSEDED_VAL_MACRO_F1 = 0.7670
B2_SUPERSEDED_TEST_ACC = 0.7101
B2_SUPERSEDED_TEST_MACRO_F1 = 0.7369
B2_SUPERSEDED_TEST_KAPPA = 0.6051


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


def build_b2_model(num_classes=4):
    """MobileNetV2 frozen base (ImageNet weights, alpha 1.0) + Dense 128 + Dropout 0.3 + Dense 4."""
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
        alpha=1.0,
        pooling="avg",
    )
    base_model.trainable = False

    # Keep batchnorm in inference mode
    x = base_model(inputs, training=False)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense128")(x)
    x = tf.keras.layers.Dropout(0.3, seed=RANDOM_SEED, name="dropout")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="b2_frozen_mobilenetv2")
    return model


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
        p = UPRIGHT_DIR / r["class"] / r["filename"]
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
    print("=== T-023: Baseline B2 Frozen MobileNetV2 (Stage 1 Only) ===")
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

    # Build model
    model = build_b2_model(num_classes=len(classes))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    # Callbacks (D-19: val macro F1 selection and early stopping)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    f1_cb = ValMacroF1EarlyStoppingAndCheckpoint(
        val_dataset=val_ds,
        y_val_true=y_val_t.numpy(),
        checkpoint_path=CHECKPOINT_PATH,
        patience=PATIENCE,
    )

    print("\nStarting training (max 20 epochs, patience 5 on val macro F1 per D-19)...")
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

    print(f"\nTraining finished in {total_train_sec:.2f}s ({epochs_run} epochs run).")
    print(f"Best model selected from epoch {best_epoch_idx} with val_macro_f1: {best_val_macro_f1:.4f}")

    # Restore best checkpoint weights strictly from validation
    print(f"Restoring best checkpoint from {CHECKPOINT_PATH}...")
    model.load_weights(str(CHECKPOINT_PATH))

    # Evaluate on val and test
    print("\nEvaluating on validation set...")
    val_metrics = evaluate_split(model, val_ds, y_val_t.numpy(), idx_to_class)
    print(f"Val Accuracy: {val_metrics['accuracy']:.4f}, Val Macro F1: {val_metrics['macro_f1']:.4f}, Kappa: {val_metrics['cohen_kappa']:.4f}")

    print("\nEvaluating on test set (held-out)...")
    test_metrics = evaluate_split(model, test_ds, y_test_t.numpy(), idx_to_class)
    print(f"Test Accuracy: {test_metrics['accuracy']:.4f}, Test Macro F1: {test_metrics['macro_f1']:.4f}, Kappa: {test_metrics['cohen_kappa']:.4f}")

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

    # Build Markdown report
    md_lines = [
        "# Baseline B2: Frozen MobileNetV2 (Stage 1 Only)",
        "",
        "## Model Configuration",
        "- **Base Architecture**: MobileNetV2 (ImageNet pretrained, alpha 1.0, fully frozen, GlobalAveragePooling)",
        "- **Classification Head**: Dense(128, ReLU) -> Dropout(0.3) -> Dense(4, softmax) (Section 8.3, D-14)",
        "- **Input**: 224x224 RGB, bilinear resize, `mobilenet_v2.preprocess_input` (Section 8.1)",
        "- **Dataset**: EXIF-upright dataset (`data/processed/hasan_upright/`) per D-24",
        "- **Augmentation**: Training set only per Section 8.2 (rotation +-30 deg, flip, zoom, brightness, contrast)",
        "- **Loss & Optimizer**: Sparse Categorical Crossentropy, Adam lr=1e-3, balanced class weights",
        "- **Checkpoint Selection & Early Stopping**: Selected by validation macro F1 (patience 5, max 20 epochs, D-19)",
        f"- **Epochs Run**: {epochs_run} (best epoch: {best_epoch_idx})",
        f"- **Training Time**: {total_train_sec:.2f} seconds ({total_train_sec / 60.0:.2f} min)",
        f"- **Hardware**: {hardware_str}",
        "",
        "## Comparison with Baselines B0, B1, and Superseded B2",
        "",
        "| Baseline Model | Val Accuracy | Val Macro F1 | Test Accuracy | Test Macro F1 | Test Cohen's Kappa |",
        "|---|---|---|---|---|---|",
        f"| **B0 (Majority: Leaf Blast)** | {B0_VAL_ACC:.4f} ({B0_VAL_ACC*100:.2f}%) | {B0_VAL_MACRO_F1:.4f} | {B0_TEST_ACC:.4f} ({B0_TEST_ACC*100:.2f}%) | **{B0_TEST_MACRO_F1:.4f}** | {B0_TEST_KAPPA:.4f} |",
        f"| **B1 (Small CNN from Scratch)** | {B1_VAL_ACC:.4f} ({B1_VAL_ACC*100:.2f}%) | {B1_VAL_MACRO_F1:.4f} | {B1_TEST_ACC:.4f} ({B1_TEST_ACC*100:.2f}%) | **{B1_TEST_MACRO_F1:.4f}** | {B1_TEST_KAPPA:.4f} |",
        f"| **B2 (Superseded: Raw Orientation)** | {B2_SUPERSEDED_VAL_ACC:.4f} ({B2_SUPERSEDED_VAL_ACC*100:.2f}%) | {B2_SUPERSEDED_VAL_MACRO_F1:.4f} | {B2_SUPERSEDED_TEST_ACC:.4f} ({B2_SUPERSEDED_TEST_ACC*100:.2f}%) | **{B2_SUPERSEDED_TEST_MACRO_F1:.4f}** | {B2_SUPERSEDED_TEST_KAPPA:.4f} |",
        f"| **B2 (EXIF-Upright Orientation)** | {val_metrics['accuracy']:.4f} ({val_metrics['accuracy']*100:.2f}%) | {val_metrics['macro_f1']:.4f} | {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.2f}%) | **{test_metrics['macro_f1']:.4f}** | {test_metrics['cohen_kappa']:.4f} |",
        "",
        "## Detailed Per-Class Breakdown (B2)",
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
        "Figure saved to `results/figures/b2_confusion.png` (git-ignored).",
        "",
        "## Analysis and Findings",
        f"1. Baseline B2 (EXIF-Upright Orientation, Stage 1) achieves a Test Macro F1 of {test_metrics['macro_f1']:.4f} (Accuracy: {test_metrics['accuracy']*100:.2f}%) on the held-out test split, compared to Superseded B2 ({B2_SUPERSEDED_TEST_MACRO_F1:.4f}), B0 ({B0_TEST_MACRO_F1:.4f}), and B1 ({B1_TEST_MACRO_F1:.4f}).",
        f"2. Leveraging ImageNet feature representations through a frozen backbone provides substantially superior feature extraction compared to training from scratch (B1), validating transfer learning as the foundational methodology for this dataset.",
        "3. Selection of the best checkpoint based on validation macro F1 (D-19) prevents class-imbalanced bias and avoids premature or degraded checkpoint restoration.",
        "4. Per D-24, all images are oriented upright according to EXIF tags before training and evaluation, establishing orientation consistency across the entire pipeline.",
    ])

    md_text = "\n".join(md_lines) + "\n"

    # Assert required comparisons
    assert f"{B0_TEST_MACRO_F1:.4f}" in md_text, "B0 test macro F1 must be reported in markdown table"
    assert f"{B1_TEST_MACRO_F1:.4f}" in md_text, "B1 test macro F1 must be reported in markdown table"
    assert f"{B2_SUPERSEDED_TEST_MACRO_F1:.4f}" in md_text, "Superseded B2 test macro F1 must be reported in markdown table"
    assert f"{test_metrics['macro_f1']:.4f}" in md_text, "B2 test macro F1 must be reported in markdown table"

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
    }


if __name__ == "__main__":
    main()

