"""
Perceptual hash deduplication analysis for public rice leaf disease datasets (T-014).
Computes 64-bit DCT perceptual hash (pHash) and clusters near-duplicate images.
"""

import os
import csv
import cv2
import numpy as np
from collections import defaultdict

TARGET_CLASSES = [
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Leaf Blast",
    "Healthy Rice Leaf",
]

DEFAULT_STAGING_DIR = r"I:\University_Projects\Rice Leaf Disease\data\raw\public\hasan_staging\Original Images"
DEFAULT_OUTPUT_CSV = r"I:\University_Projects\Rice Leaf Disease\data\metadata\dedup_report.csv"
HAMMING_THRESHOLD = 5  # Standard threshold for 64-bit pHash (distance <= 5 considered near-duplicates)


def compute_phash(image_path: str, hash_size: int = 8, highfreq_factor: int = 4) -> str:
    """
    Computes a 64-bit DCT-based perceptual hash for an image.
    1. Read grayscale and resize to 32x32.
    2. Compute 2D Discrete Cosine Transform (DCT).
    3. Extract top-left 8x8 low-frequency coefficients.
    4. Compute median of coefficients.
    5. Generate binary hash (1 if > median else 0).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size = hash_size * highfreq_factor  # 32
    resized = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))
    dct_lowfreq = dct[:hash_size, :hash_size]
    med = np.median(dct_lowfreq)
    bits = (dct_lowfreq > med).flatten()
    int_val = int("".join("1" if b else "0" for b in bits), 2)
    return f"{int_val:016x}"


def hamming_distance(hash1: str, hash2: str) -> int:
    """Computes the Hamming distance between two 16-character hex hashes."""
    v1 = int(hash1, 16)
    v2 = int(hash2, 16)
    return bin(v1 ^ v2).count("1")


class UnionFind:
    def __init__(self, elements):
        self.parent = {el: el for el in elements}

    def find(self, el):
        if self.parent[el] != el:
            self.parent[el] = self.find(self.parent[el])
        return self.parent[el]

    def union(self, el1, el2):
        r1 = self.find(el1)
        r2 = self.find(el2)
        if r1 != r2:
            self.parent[r2] = r1


def run_deduplication(
    staging_dir: str = DEFAULT_STAGING_DIR,
    output_csv: str = DEFAULT_OUTPUT_CSV,
    threshold: int = HAMMING_THRESHOLD,
):
    print(f"Scanning target classes in: {staging_dir}")
    print(f"Hamming distance threshold: <= {threshold}")

    images = []  # list of dicts: {'path', 'filename', 'class', 'hash'}
    counts_before = {}

    for cls in TARGET_CLASSES:
        cls_dir = os.path.join(staging_dir, cls)
        if not os.path.exists(cls_dir):
            raise FileNotFoundError(f"Directory not found: {cls_dir}")
        files = [f for f in sorted(os.listdir(cls_dir)) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        counts_before[cls] = len(files)
        print(f"  Class '{cls}': {len(files)} images")

        for f in files:
            full_path = os.path.join(cls_dir, f)
            h = compute_phash(full_path)
            images.append({
                "path": full_path,
                "filename": f,
                "class": cls,
                "hash": h,
            })

    total_images = len(images)
    print(f"\nTotal images hashed: {total_images}")

    # Compare all pairs and build connected components (Union-Find)
    uf = UnionFind(range(total_images))
    pair_count = 0

    for i in range(total_images):
        for j in range(i + 1, total_images):
            dist = hamming_distance(images[i]["hash"], images[j]["hash"])
            if dist <= threshold:
                uf.union(i, j)
                pair_count += 1

    print(f"Found {pair_count} near-duplicate pairs at threshold <= {threshold}.")

    # Group components
    components = defaultdict(list)
    for i in range(total_images):
        root = uf.find(i)
        components[root].append(i)

    # Assign group IDs
    duplicate_groups = [comp for comp in components.values() if len(comp) > 1]
    duplicate_groups.sort(key=lambda g: (-len(g), images[g[0]]["class"], images[g[0]]["filename"]))

    group_map = {}  # index -> group_id
    for g_idx, comp in enumerate(duplicate_groups, start=1):
        group_id = f"group_{g_idx:03d}"
        for idx in comp:
            group_map[idx] = group_id

    # Compute duplicates to remove per class
    # For each group, we keep 1 representative. If a group spans multiple images in the same class,
    # the extra images in that class are removed.
    duplicates_removed_per_class = defaultdict(int)
    for comp in duplicate_groups:
        # Group members by class
        by_class = defaultdict(list)
        for idx in comp:
            by_class[images[idx]["class"]].append(idx)
        
        # If group is homogeneous (all same class): keep 1, remove (k - 1)
        # If cross-class: keep 1 representative overall (first class) and remove the rest
        first_rep = True
        for cls, idxs in by_class.items():
            if first_rep:
                # Keep first image
                duplicates_removed_per_class[cls] += (len(idxs) - 1)
                first_rep = False
            else:
                # All cross-class duplicates removed
                duplicates_removed_per_class[cls] += len(idxs)

    # Write dedup_report.csv
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "class", "group_id", "hash"])
        for i, img in enumerate(images):
            gid = group_map.get(i, "unique")
            writer.writerow([img["filename"], img["class"], gid, img["hash"]])

    print(f"\nDeduplication report saved to: {output_csv}")

    # Summary report
    print("\n================ DEDUPLICATION ANALYSIS SUMMARY ================")
    print(f"Standard Threshold Used: Hamming distance <= {threshold} on 64-bit DCT pHash")
    print(f"Total Near-Duplicate Groups (size >= 2): {len(duplicate_groups)}")
    
    # Per-class breakdown
    print("\nPer-Class Counts Before and After Removing 1 Representative Per Group:")
    all_passed = True
    results = {}

    for cls in TARGET_CLASSES:
        before = counts_before[cls]
        removed = duplicates_removed_per_class[cls]
        after = before - removed
        passed = (after >= 100)
        if not passed:
            all_passed = False
        results[cls] = {
            "before": before,
            "removed": removed,
            "after": after,
            "passed": passed,
        }
        status_str = "PASSED" if passed else "FAILED (<100)"
        print(f"  {cls:25s} | Before: {before:3d} | Removed: {removed:3d} | After: {after:3d} | Threshold >= 100: {status_str}")

    print("=================================================================")
    if all_passed:
        print("RESULT: ALL 4 TARGET CLASSES PASS THE 100-IMAGE RULE AFTER DEDUPLICATION.")
    else:
        print("RESULT: AT LEAST ONE CLASS FAILED THE 100-IMAGE RULE. T-014 IS BLOCKED.")

    return results, len(duplicate_groups), all_passed


if __name__ == "__main__":
    run_deduplication()
