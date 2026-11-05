"""
src/models/train_five_seeds.py

Orchestrates 5-seed deterministic rerun of M1 across seeds 42, 43, 44, 45, 46.
Each seed executes in its own fresh Python subprocess.
Generates results/metrics/m1_det_seeds.csv and results/metrics/m1_det_seeds.md.
"""

import sys
import subprocess
import json
import csv
import numpy as np
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = sys.executable
SEED_SCRIPT = WORKSPACE_ROOT / "src" / "models" / "train_m1_seed.py"
METRICS_DIR = WORKSPACE_ROOT / "results" / "metrics"
OUTPUT_CSV = METRICS_DIR / "m1_det_seeds.csv"
OUTPUT_MD = METRICS_DIR / "m1_det_seeds.md"

SEEDS = [42, 43, 44, 45, 46]
GATE_2_THRESHOLD = 0.80


def main():
    print("=================================================================")
    print("STARTING FIVE-SEED DETERMINISTIC TRAINING (Seeds: 42, 43, 44, 45, 46)")
    print("=================================================================")

    results = []
    for seed in SEEDS:
        print(f"\n>>> Spawning fresh process for Seed {seed}...")
        cmd = [PYTHON_EXE, str(SEED_SCRIPT), "--seed", str(seed)]
        res = subprocess.run(cmd, cwd=str(WORKSPACE_ROOT))
        if res.returncode != 0:
            print(f"ERROR: Process for Seed {seed} failed with return code {res.returncode}")
            sys.exit(res.returncode)

        json_path = METRICS_DIR / f"m1_det_seed{seed}.json"
        if not json_path.exists():
            print(f"ERROR: Expected metrics file not found: {json_path}")
            sys.exit(1)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            results.append(data)

    # Compute statistics across 5 seeds
    val_f1s = [r["val_macro_f1"] for r in results]
    test_f1s = [r["test_macro_f1"] for r in results]
    test_accs = [r["test_accuracy"] for r in results]
    test_kappas = [r["test_kappa"] for r in results]
    bs_lbs = [r["bs_to_lb_errors"] for r in results]

    mean_val_f1 = float(np.mean(val_f1s))
    sd_val_f1 = float(np.std(val_f1s, ddof=1))

    mean_test_f1 = float(np.mean(test_f1s))
    sd_test_f1 = float(np.std(test_f1s, ddof=1))

    mean_acc = float(np.mean(test_accs))
    sd_acc = float(np.std(test_accs, ddof=1))

    mean_kappa = float(np.mean(test_kappas))
    sd_kappa = float(np.std(test_kappas, ddof=1))

    mean_bs_lb = float(np.mean(bs_lbs))
    sd_bs_lb = float(np.std(bs_lbs, ddof=1))

    # Write results/metrics/m1_det_seeds.csv
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "seed",
            "val_macro_f1",
            "test_macro_f1",
            "test_accuracy",
            "test_kappa",
            "best_epoch",
            "bs_to_lb_errors",
            "weights_hash",
        ])
        for r in results:
            writer.writerow([
                r["seed"],
                f"{r['val_macro_f1']:.4f}",
                f"{r['test_macro_f1']:.4f}",
                f"{r['test_accuracy']:.4f}",
                f"{r['test_kappa']:.4f}",
                r["best_epoch"],
                r["bs_to_lb_errors"],
                r["weights_hash"],
            ])
        writer.writerow([
            "mean",
            f"{mean_val_f1:.4f}",
            f"{mean_test_f1:.4f}",
            f"{mean_acc:.4f}",
            f"{mean_kappa:.4f}",
            "N/A",
            f"{mean_bs_lb:.2f}",
            "N/A",
        ])
        writer.writerow([
            "std_sample",
            f"{sd_val_f1:.4f}",
            f"{sd_test_f1:.4f}",
            f"{sd_acc:.4f}",
            f"{sd_kappa:.4f}",
            "N/A",
            f"{sd_bs_lb:.2f}",
            "N/A",
        ])

    print(f"\nSaved CSV to {OUTPUT_CSV}")

    # Write results/metrics/m1_det_seeds.md
    md_lines = [
        "# Five-Seed Deterministic Statistical Evaluation (Main Model M1, Upright Data)",
        "",
        "## Overview",
        "- **Dataset**: EXIF-upright Hasan originals in `data/processed/hasan_upright/` (907 active images).",
        "- **Determinism**: Enabled via `enable_determinism(seed)` (`TF_DETERMINISTIC_OPS=1`, `TF_ENABLE_ONEDNN_OPTS=0`, `tf.keras.utils.set_random_seed(seed)`, `tf.config.experimental.enable_op_determinism()`).",
        "- **Process Isolation**: Each seed was trained end-to-end (Stage 1 + Stage 2) in an independent fresh Python subprocess.",
        "- **Checkpoint Selection**: Strictly by validation macro F1 within each seed per D-19 (max 20 epochs for Stage 1, max 30 epochs for Stage 2, patience 5).",
        "- **Test Evaluation**: Held-out test split ($N=138$) evaluated exactly once per seed after training concluded.",
        "",
        "## Summary Metrics Across Five Seeds",
        "",
        "| Seed | Val Macro F1 | Test Macro F1 | Test Accuracy | Test Cohen's Kappa | Best Epoch (St2) | BS -> LB Errors | Gate 2 (Test F1 >= 0.80) | Weights SHA-256 (Truncated) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for r in results:
        gate_status = "MET" if r["test_macro_f1"] >= GATE_2_THRESHOLD else "NOT MET"
        h_trunc = r["weights_hash"][:16] + "..."
        md_lines.append(
            f"| **{r['seed']}** | {r['val_macro_f1']:.4f} | **{r['test_macro_f1']:.4f}** | {r['test_accuracy']*100:.2f}% | {r['test_kappa']:.4f} | {r['best_epoch']} | {r['bs_to_lb_errors']} | **{gate_status}** | `{h_trunc}` |"
        )

    overall_gate = "MET" if mean_test_f1 >= GATE_2_THRESHOLD and (mean_test_f1 - sd_test_f1) >= GATE_2_THRESHOLD else "NOT MET"

    md_lines.extend([
        f"| **Mean** | **{mean_val_f1:.4f}** | **{mean_test_f1:.4f}** | **{mean_acc*100:.2f}%** | **{mean_kappa:.4f}** | - | **{mean_bs_lb:.2f}** | **{overall_gate}** | - |",
        f"| **Std (ddof=1)** | **{sd_val_f1:.4f}** | **{sd_test_f1:.4f}** | **{sd_acc*100:.2f}%** | **{sd_kappa:.4f}** | - | **{sd_bs_lb:.2f}** | - | - |",
        "",
        "## Quality Gate 2 Evaluation",
        f"- **Threshold**: Test Macro F1 $\\ge 0.8000$",
    ])

    for r in results:
        st = "MET" if r["test_macro_f1"] >= GATE_2_THRESHOLD else "NOT MET"
        md_lines.append(f"- **Seed {r['seed']}**: Test Macro F1 = {r['test_macro_f1']:.4f} ({st})")

    md_lines.extend([
        f"- **Five-Seed Mean**: **{mean_test_f1:.4f} $\\pm$ {sd_test_f1:.4f}**",
        f"- **Range ($1\\sigma$)**: [{mean_test_f1 - sd_test_f1:.4f}, {mean_test_f1 + sd_test_f1:.4f}]",
        f"- **Overall Gate 2 Status**: **{overall_gate}** (Mean is {mean_test_f1:.4f}; lower bound {mean_test_f1 - sd_test_f1:.4f} is < 0.80)",
        "",
        "## Brown Spot to Leaf Blast Confusion Analysis",
    ])

    for r in results:
        md_lines.append(f"- Seed {r['seed']}: {r['bs_to_lb_errors']} errors")
    md_lines.append(f"- **Mean Errors**: {mean_bs_lb:.2f} $\\pm$ {sd_bs_lb:.2f}")

    # Best seed selection by validation macro F1 strictly (D-19)
    best_seed_entry = max(results, key=lambda x: x["val_macro_f1"])
    md_lines.extend([
        "",
        "## Canonical Seed Selection (Validation Macro F1 Only per D-19)",
        f"- Candidate selected strictly by highest validation macro F1 (test performance is not used for selection):",
        f"- **Canonical Seed**: **{best_seed_entry['seed']}**",
        f"- **Validation Macro F1**: **{best_seed_entry['val_macro_f1']:.4f}**",
        f"- **Test Macro F1**: {best_seed_entry['test_macro_f1']:.4f}",
        f"- **Weights SHA-256**: `{best_seed_entry['weights_hash']}`",
        f"- **Checkpoint Path**: `results/checkpoints/m1_det_seed{best_seed_entry['seed']}_best.keras`",
    ])

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Saved Markdown report to {OUTPUT_MD}")
    print("\n=================================================================")
    print("FIVE-SEED DETERMINISTIC RUN COMPLETE")
    print(f"Mean Val Macro F1:  {mean_val_f1:.4f} ± {sd_val_f1:.4f}")
    print(f"Mean Test Macro F1: {mean_test_f1:.4f} ± {sd_test_f1:.4f}")
    print(f"Overall Gate 2:     {overall_gate}")
    print(f"Selected Canonical Seed by Val Macro F1: Seed {best_seed_entry['seed']} (Val F1: {best_seed_entry['val_macro_f1']:.4f})")
    print("=================================================================")


if __name__ == "__main__":
    main()

