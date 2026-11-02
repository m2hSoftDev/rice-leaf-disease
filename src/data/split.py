"""
src/data/split.py

Reproducible train/val/test group-stratified splitting for rice leaf disease detection.
Uses fixed seed 42 and groups images by perceptual hash near-duplicate group_id (D-18),
with singletons assigned their own unique group key.
Excludes group_035 cross-class duplicate (D-17) and excludes all augmented images.
Target distribution: 70% Train, 15% Validation, 15% Test per class.

Outputs:
  - data/metadata/split_manifest.csv
  - results/metrics/split_summary.csv
"""

import os
import csv
import random
from collections import defaultdict
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEDUP_REPORT_PATH = WORKSPACE_ROOT / "data" / "metadata" / "dedup_report.csv"
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"
SUMMARY_PATH = WORKSPACE_ROOT / "results" / "metrics" / "split_summary.csv"

# Expected counts table for assertion (within +-2 images)
EXPECTED_COUNTS = {
    "Bacterial Leaf Blight": {"train": 125, "val": 27, "test": 27, "total": 179},
    "Brown Spot":            {"train": 186, "val": 38, "test": 43, "total": 267},
    "Healthy Rice Leaf":     {"train": 110, "val": 24, "test": 23, "total": 157},
    "Leaf Blast":            {"train": 213, "val": 46, "test": 45, "total": 304},
}

RANDOM_SEED = 42


def generate_split():
    if not DEDUP_REPORT_PATH.exists():
        raise FileNotFoundError(f"Dedup report not found at: {DEDUP_REPORT_PATH}")

    # 1. Load dedup report, exclude group_035 (D-17)
    records = []
    with open(DEDUP_REPORT_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["group_id"] == "group_035":
                continue  # Excluded per D-17
            records.append(row)

    print(f"Loaded {len(records)} active images after excluding group_035.")
    assert len(records) == 907, f"Expected 907 images after D-17 exclusion, got {len(records)}"

    # 2. Confirm no augmented image enters any split
    for r in records:
        fn = r["filename"].lower()
        assert "augment" not in fn and "aug" not in fn, f"Augmented image found: {r['filename']}"

    # 3. Assign singletons their own unique group_id
    singleton_idx = 0
    groups = defaultdict(list)
    for r in records:
        gid = r["group_id"]
        if gid == "unique":
            gid = f"singleton_{singleton_idx:04d}"
            singleton_idx += 1
            r["group_id"] = gid
        groups[gid].append(r)

    print(f"Identified {len(groups)} distinct groups (including {singleton_idx} singletons).")
    assert len(groups) == 737, f"Expected 737 distinct groups, got {len(groups)}"

    # 4. Group by class
    by_class_groups = defaultdict(list)
    class_totals = defaultdict(int)
    for gid, g_records in groups.items():
        cls = g_records[0]["class"]
        by_class_groups[cls].append((gid, g_records))
        class_totals[cls] += len(g_records)

    # 5. Perform group-stratified allocation (70/15/15) with seed 42
    random.seed(RANDOM_SEED)

    split_assignment = {}  # gid -> 'train' | 'val' | 'test'
    split_counts = {
        "train": defaultdict(int),
        "val": defaultdict(int),
        "test": defaultdict(int),
    }

    for cls in sorted(by_class_groups.keys()):
        c_groups = by_class_groups[cls]
        # Sort by gid for cross-platform determinism before shuffle
        c_groups.sort(key=lambda x: x[0])
        random.shuffle(c_groups)

        n_images = class_totals[cls]
        target_train = round(0.70 * n_images)
        target_val = round(0.15 * n_images)
        target_test = n_images - target_train - target_val

        curr_train = 0
        curr_val = 0
        curr_test = 0

        for gid, g_recs in c_groups:
            k = len(g_recs)
            need_train = target_train - curr_train
            need_val = target_val - curr_val
            need_test = target_test - curr_test

            # Pick split with largest remaining need
            needs = [("train", need_train), ("val", need_val), ("test", need_test)]
            needs.sort(key=lambda x: -x[1])
            best_split = needs[0][0]

            split_assignment[gid] = best_split
            if best_split == "train":
                curr_train += k
            elif best_split == "val":
                curr_val += k
            else:
                curr_test += k

            split_counts[best_split][cls] += k

    # 6. Apply split assignment to each record
    manifest_rows = []
    group_to_splits = defaultdict(set)
    for r in records:
        gid = r["group_id"]
        split = split_assignment[gid]
        group_to_splits[gid].add(split)
        manifest_rows.append({
            "filename": r["filename"],
            "class": r["class"],
            "group_id": gid,
            "split": split,
            "source_dataset": "hasan",
        })

    # 7. Assertions
    # Assertion 1: No group_id appears in more than one split
    leakage_groups = [gid for gid, sps in group_to_splits.items() if len(sps) > 1]
    assert len(leakage_groups) == 0, f"Data leakage detected! Groups spanning multiple splits: {leakage_groups}"
    print("[PASS] Assertion 1: No group_id appears in more than one split (zero leakage).")

    # Assertion 2: All 907 images accounted for
    assert len(manifest_rows) == 907, f"Manifest row count {len(manifest_rows)} != 907"
    print("[PASS] Assertion 2: Exactly 907 images accounted for.")

    # Assertion 3: Per-class counts match expected table within +-2 images
    print("\nVerifying per-class split counts against expected table:")
    print(f"{'Class':25s} | {'Train':10s} | {'Val':10s} | {'Test':10s} | {'Total':6s}")
    for cls, exp in EXPECTED_COUNTS.items():
        act_tr = split_counts["train"][cls]
        act_va = split_counts["val"][cls]
        act_te = split_counts["test"][cls]
        act_tot = act_tr + act_va + act_te

        print(f"{cls:25s} | {act_tr:4d} (exp {exp['train']:3d}) | {act_va:4d} (exp {exp['val']:3d}) | {act_te:4d} (exp {exp['test']:3d}) | {act_tot:5d}")

        assert abs(act_tr - exp["train"]) <= 2, f"{cls} train count mismatch: {act_tr} vs {exp['train']}"
        assert abs(act_va - exp["val"]) <= 2, f"{cls} val count mismatch: {act_va} vs {exp['val']}"
        assert abs(act_te - exp["test"]) <= 2, f"{cls} test count mismatch: {act_te} vs {exp['test']}"
        assert act_tot == exp["total"], f"{cls} total count mismatch: {act_tot} vs {exp['total']}"
    print("[PASS] Assertion 3: All per-class split counts match expected table within +-2 images.")

    # 8. Write data/metadata/split_manifest.csv
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Sort manifest for deterministic output: class, group_id, filename
    manifest_rows.sort(key=lambda x: (x["class"], x["group_id"], x["filename"]))
    fieldnames = ["filename", "class", "group_id", "split", "source_dataset"]
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"\nWritten split manifest to: {MANIFEST_PATH}")

    # 9. Write results/metrics/split_summary.csv
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary_fieldnames = ["class", "train", "val", "test", "total"]
    summary_rows = []
    tot_train, tot_val, tot_test, tot_all = 0, 0, 0, 0
    for cls in sorted(EXPECTED_COUNTS.keys()):
        tr = split_counts["train"][cls]
        va = split_counts["val"][cls]
        te = split_counts["test"][cls]
        tot = tr + va + te
        tot_train += tr
        tot_val += va
        tot_test += te
        tot_all += tot
        summary_rows.append({
            "class": cls,
            "train": tr,
            "val": va,
            "test": te,
            "total": tot,
        })
    # Add overall row
    summary_rows.append({
        "class": "Overall",
        "train": tot_train,
        "val": tot_val,
        "test": tot_test,
        "total": tot_all,
    })

    with open(SUMMARY_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Written split summary to: {SUMMARY_PATH}")

    return summary_rows


if __name__ == "__main__":
    generate_split()
