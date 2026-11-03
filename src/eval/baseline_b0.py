"""
src/eval/baseline_b0.py

Computes Baseline B0 (Majority Class Predictor) metrics on validation and test splits
using only data/metadata/split_manifest.csv.
Finds majority class on train (Leaf Blast, 213 images) and evaluates constant prediction.
Outputs:
  - results/metrics/baseline_b0.csv
  - results/metrics/baseline_b0.md
"""

import csv
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, cohen_kappa_score

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
OUTPUT_CSV = WORKSPACE_ROOT / "results" / "metrics" / "baseline_b0.csv"
OUTPUT_MD = WORKSPACE_ROOT / "results" / "metrics" / "baseline_b0.md"


def evaluate_b0():
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    # 1. Load manifest records
    train_records = []
    val_records = []
    test_records = []

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sp = row["split"]
            if sp == "train":
                train_records.append(row)
            elif sp == "val":
                val_records.append(row)
            elif sp == "test":
                test_records.append(row)

    print(f"Loaded records - Train: {len(train_records)}, Val: {len(val_records)}, Test: {len(test_records)}")
    assert len(train_records) == 634
    assert len(val_records) == 135
    assert len(test_records) == 138

    # 2. Identify majority class from train
    train_counts = Counter(r["class"] for r in train_records)
    majority_class, majority_count = train_counts.most_common(1)[0]
    print(f"Majority class in train: '{majority_class}' with {majority_count} images.")
    assert majority_class == "Leaf Blast"
    assert majority_count == 213

    classes = sorted(list(train_counts.keys()))
    print(f"Classes ({len(classes)}): {classes}")

    # 3. Evaluate on a split
    def compute_metrics(split_name, records):
        y_true = [r["class"] for r in records]
        y_pred = [majority_class] * len(records)

        acc = accuracy_score(y_true, y_pred)
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        kappa = cohen_kappa_score(y_true, y_pred)

        prec, rec, f1, supp = precision_recall_fscore_support(
            y_true, y_pred, labels=classes, zero_division=0
        )

        class_metrics = {}
        for idx, cls in enumerate(classes):
            class_metrics[cls] = {
                "precision": float(prec[idx]),
                "recall": float(rec[idx]),
                "f1": float(f1[idx]),
                "support": int(supp[idx]),
            }

        macro_p = float(np.mean(prec))
        macro_r = float(np.mean(rec))

        return {
            "split": split_name,
            "accuracy": float(acc),
            "macro_f1": float(macro_f1),
            "macro_precision": macro_p,
            "macro_recall": macro_r,
            "cohen_kappa": float(kappa),
            "total_samples": len(records),
            "class_metrics": class_metrics,
        }

    val_res = compute_metrics("val", val_records)
    test_res = compute_metrics("test", test_records)

    # 4. Save results/metrics/baseline_b0.csv
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    csv_rows = []
    for res in [val_res, test_res]:
        sp = res["split"]
        for cls in classes:
            cm = res["class_metrics"][cls]
            csv_rows.append({
                "split": sp,
                "class": cls,
                "precision": f"{cm['precision']:.4f}",
                "recall": f"{cm['recall']:.4f}",
                "f1": f"{cm['f1']:.4f}",
                "support": cm["support"],
            })
        csv_rows.append({
            "split": sp,
            "class": "macro_avg",
            "precision": f"{res['macro_precision']:.4f}",
            "recall": f"{res['macro_recall']:.4f}",
            "f1": f"{res['macro_f1']:.4f}",
            "support": res["total_samples"],
        })
        csv_rows.append({
            "split": sp,
            "class": "accuracy",
            "precision": "N/A",
            "recall": "N/A",
            "f1": f"{res['accuracy']:.4f}",
            "support": res["total_samples"],
        })
        csv_rows.append({
            "split": sp,
            "class": "cohen_kappa",
            "precision": "N/A",
            "recall": "N/A",
            "f1": f"{res['cohen_kappa']:.4f}",
            "support": res["total_samples"],
        })

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["split", "class", "precision", "recall", "f1", "support"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Written: {OUTPUT_CSV}")

    # 5. Save results/metrics/baseline_b0.md
    md_lines = [
        "# Baseline B0: Majority Class Predictor",
        "",
        f"Majority class determined from training split: **{majority_class}** (213 / 634 train images = 33.6%).",
        f"Every instance in validation and test splits is predicted as '{majority_class}'.",
        "",
        "## Summary Metrics",
        "",
        "| Split | Accuracy | Macro F1 | Cohen's Kappa | Total Samples | Majority Predictor |",
        "|---|---|---|---|---|---|",
        f"| **Validation** | {val_res['accuracy']:.4f} ({val_res['accuracy']*100:.2f}%) | {val_res['macro_f1']:.4f} | {val_res['cohen_kappa']:.4f} | {val_res['total_samples']} | {majority_class} |",
        f"| **Test** | {test_res['accuracy']:.4f} ({test_res['accuracy']*100:.2f}%) | {test_res['macro_f1']:.4f} | {test_res['cohen_kappa']:.4f} | {test_res['total_samples']} | {majority_class} |",
        "",
        "## Detailed Per-Class Breakdown",
        "",
        "### Validation Split",
        "",
        "| Class | Precision | Recall | F1-Score | Support |",
        "|---|---|---|---|---|",
    ]

    for cls in classes:
        cm = val_res["class_metrics"][cls]
        md_lines.append(f"| {cls} | {cm['precision']:.4f} | {cm['recall']:.4f} | {cm['f1']:.4f} | {cm['support']} |")
    md_lines.append(f"| **Macro Average** | **{val_res['macro_precision']:.4f}** | **{val_res['macro_recall']:.4f}** | **{val_res['macro_f1']:.4f}** | **{val_res['total_samples']}** |")

    md_lines.extend([
        "",
        "### Test Split",
        "",
        "| Class | Precision | Recall | F1-Score | Support |",
        "|---|---|---|---|---|",
    ])
    for cls in classes:
        cm = test_res["class_metrics"][cls]
        md_lines.append(f"| {cls} | {cm['precision']:.4f} | {cm['recall']:.4f} | {cm['f1']:.4f} | {cm['support']} |")
    md_lines.append(f"| **Macro Average** | **{test_res['macro_precision']:.4f}** | **{test_res['macro_recall']:.4f}** | **{test_res['macro_f1']:.4f}** | **{test_res['total_samples']}** |")

    md_lines.extend([
        "",
        "## Observations and Analysis",
        "",
        "Macro F1 for B0 is very low (~0.12) because predicting a single majority class yields zero precision, recall, and F1 for the other three classes, heavily penalizing the unweighted macro average. This baseline matters because it establishes the foundational lower-bound performance driven purely by class imbalance, proving that any viable machine learning model must learn genuine discriminative features rather than exploiting prior class distributions.",
    ])

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Written: {OUTPUT_MD}")

    return val_res, test_res


if __name__ == "__main__":
    evaluate_b0()
