"""Build EXIF-upright data copy per Decision D-24.

Applies PIL ImageOps.exif_transpose to all 1,701 images in
data/raw/public/hasan_staging/Original Images/ and saves the upright portrait
copies to data/processed/hasan_upright/, preserving class folders and filenames.
"""

from pathlib import Path
import random
import pandas as pd
from PIL import Image, ImageOps

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = WORKSPACE_ROOT / "data" / "raw" / "public" / "hasan_staging" / "Original Images"
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed" / "hasan_upright"
MANIFEST_PATH = WORKSPACE_ROOT / "data" / "metadata" / "split_manifest.csv"

# Cross-class duplicate group_035 excluded per D-17
GROUP_035_FILES = {
    "Bacterial_leaf_Blight  (33).jpg",
    "Leaf_blast  (289).jpg"
}


def build_upright_dataset():
    if not STAGING_DIR.exists():
        raise FileNotFoundError(f"Staging directory not found: {STAGING_DIR}")

    print("Loading split manifest...")
    manifest_df = pd.read_csv(MANIFEST_PATH)
    active_manifest_files = set(manifest_df["filename"])
    print(f"Active images in split_manifest.csv: {len(active_manifest_files)}")

    # Find all images in staging directory
    all_staging_images = sorted(list(STAGING_DIR.glob("*/*.*")))
    total_staging_count = len(all_staging_images)
    print(f"Total original images in staging: {total_staging_count}")

    active_count = 0
    group_035_count = 0
    other_classes_count = 0

    tag_6_images = []

    print(f"\nProcessing {total_staging_count} images to {PROCESSED_DIR}...")
    for idx, img_path in enumerate(all_staging_images, 1):
        rel_class = img_path.parent.name
        filename = img_path.name
        dst_dir = PROCESSED_DIR / rel_class
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_path = dst_dir / filename

        # Track categories
        if filename in active_manifest_files:
            active_count += 1
        elif filename in GROUP_035_FILES:
            group_035_count += 1
        else:
            other_classes_count += 1

        # Inspect EXIF orientation tag before transpose
        with Image.open(img_path) as im:
            exif = im.getexif()
            orient = int(exif.get(0x0112, 1))
            if orient == 6:
                tag_6_images.append((rel_class, filename, img_path, dst_path))

            # Apply EXIF transpose to rotate upright
            im_upright = ImageOps.exif_transpose(im)
            im_upright.save(dst_path, quality=95, subsampling=0)

        if idx % 300 == 0 or idx == total_staging_count:
            print(f"  Processed {idx}/{total_staging_count} images...")

    print("\nProcessing complete.")
    print("=" * 60)
    print("DATASET BUILD SUMMARY:")
    print(f"  - Active images in split_manifest.csv: {active_count}")
    print(f"  - Excluded cross-class duplicate group_035: {group_035_count}")
    print(f"  - Other Hasan dataset classes: {other_classes_count}")
    print(f"  - Total images processed and saved: {active_count + group_035_count + other_classes_count}")
    print(f"  - Total images with EXIF tag 6 (ROTATE_90_CW): {len(tag_6_images)}")
    print("=" * 60)

    # Verification 1: File count equals originals count (1,701)
    processed_images = sorted(list(PROCESSED_DIR.glob("*/*.*")))
    processed_count = len(processed_images)
    print(f"\nVerification 1 - File Count Check:")
    print(f"  - Expected count: {total_staging_count} (1,701)")
    print(f"  - Actual processed count: {processed_count}")
    assert processed_count == total_staging_count, (
        f"Count mismatch! Expected {total_staging_count}, got {processed_count}"
    )
    assert processed_count == 1701, f"Expected exactly 1701 files, got {processed_count}"
    print("  -> File count check: PASSED (1,701 == 1,701)")

    # Verification 2: Sample 20 random tag-6 images and verify dimensions are (1200, 1600) portrait
    print(f"\nVerification 2 - 20 Random Tag-6 Images Dimension Check:")
    rng = random.Random(42)
    sampled_tag6 = rng.sample(tag_6_images, 20)

    print(f"{'#':<3} | {'Class':<22} | {'Filename':<32} | {'Orig Size':<12} | {'Upright Size':<12} | {'Portrait?'}")
    print("-" * 95)
    for i, (cls_name, fname, orig_p, dst_p) in enumerate(sampled_tag6, 1):
        with Image.open(orig_p) as orig_im:
            orig_w, orig_h = orig_im.size
        with Image.open(dst_p) as upright_im:
            upright_w, upright_h = upright_im.size

        is_portrait = (upright_w == 1200 and upright_h == 1600)
        assert is_portrait, f"Image {fname} is not 1200x1600 portrait! Got ({upright_w}, {upright_h})"
        print(f"{i:<3} | {cls_name:<22} | {fname:<32} | {f'{orig_w}x{orig_h}':<12} | {f'{upright_w}x{upright_h}':<12} | {'YES' if is_portrait else 'NO'}")

    print("-" * 95)
    print("  -> All 20 sampled tag-6 images verified exactly width=1200, height=1600 (portrait).")
    print("  -> Dimension check: PASSED (20/20)")

    return {
        "total_processed": processed_count,
        "active_count": active_count,
        "group_035_count": group_035_count,
        "other_classes_count": other_classes_count,
        "tag_6_count": len(tag_6_images),
        "sampled_tag6_count": len(sampled_tag6)
    }


if __name__ == "__main__":
    build_upright_dataset()
