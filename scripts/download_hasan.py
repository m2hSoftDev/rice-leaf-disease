import os
import sys
import time
import hashlib
import zipfile
import urllib.request
import concurrent.futures

URL_ORIGINAL = "https://data.mendeley.com/public-files/datasets/hx6f852hw4/files/bb4d2847-1cab-4e56-aa7a-4aa73f6dcdfc/file_downloaded"
EXPECTED_SIZE = 1664385692
EXPECTED_SHA256 = "eb1e804ae414250d7a333a1c3820c49a520c2f09e2e6a38f280e90f58a4f62fb"

STAGING_DIR = r"I:\University_Projects\Rice Leaf Disease\data\raw\public\hasan_staging"
ZIP_PATH = os.path.join(STAGING_DIR, "Original Images.zip")
AUGMENTED_DIR = r"I:\University_Projects\Rice Leaf Disease\data\raw\public\hasan_augmented"

def download_file():
    os.makedirs(STAGING_DIR, exist_ok=True)
    os.makedirs(AUGMENTED_DIR, exist_ok=True)
    
    # Check if already fully downloaded
    if os.path.exists(ZIP_PATH) and os.path.getsize(ZIP_PATH) == EXPECTED_SIZE:
        print(f"Archive already downloaded at {ZIP_PATH} ({EXPECTED_SIZE} bytes). Verifying SHA-256...")
        hasher = hashlib.sha256()
        with open(ZIP_PATH, "rb") as f:
            while chunk := f.read(1024 * 1024):
                hasher.update(chunk)
        calc_sha = hasher.hexdigest()
        print(f"SHA-256: {calc_sha}")
        if calc_sha == EXPECTED_SHA256:
            print("SHA-256 matches expected!")
            return
        else:
            print("SHA-256 mismatch, re-downloading...")

    print(f"Starting multi-part download of Original Images.zip ({EXPECTED_SIZE} bytes)...")
    num_parts = 16
    part_size = EXPECTED_SIZE // num_parts
    parts = []
    for i in range(num_parts):
        start = i * part_size
        end = EXPECTED_SIZE - 1 if i == num_parts - 1 else (i + 1) * part_size - 1
        parts.append((i, start, end))

    temp_parts = [os.path.join(STAGING_DIR, f"part_{i}.tmp") for i in range(num_parts)]

    def download_part(part_info):
        i, start, end = part_info
        temp_file = temp_parts[i]
        
        # Check if part already completed
        expected_part_len = end - start + 1
        if os.path.exists(temp_file) and os.path.getsize(temp_file) == expected_part_len:
            print(f"Part {i} already complete.")
            return i

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Range": f"bytes={start}-{end}"
        }
        req = urllib.request.Request(URL_ORIGINAL, headers=headers)
        with urllib.request.urlopen(req) as resp, open(temp_file, "wb") as f:
            copied = 0
            while chunk := resp.read(1024 * 512):
                f.write(chunk)
                copied += len(chunk)
        print(f"Part {i} finished ({copied} bytes).")
        return i

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(download_part, p) for p in parts]
        for f in concurrent.futures.as_completed(futures):
            f.result()
    t1 = time.time()
    print(f"All parts downloaded in {round(t1 - t0, 1)} s. Combining parts...")

    hasher = hashlib.sha256()
    with open(ZIP_PATH, "wb") as outfile:
        for temp_file in temp_parts:
            with open(temp_file, "rb") as infile:
                while chunk := infile.read(1024 * 1024):
                    outfile.write(chunk)
                    hasher.update(chunk)
            os.remove(temp_file)

    calc_sha = hasher.hexdigest()
    print(f"Combined {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes).")
    print(f"Computed SHA-256: {calc_sha}")
    assert calc_sha == EXPECTED_SHA256, f"SHA256 mismatch! {calc_sha} != {EXPECTED_SHA256}"

def extract_and_verify():
    print("Extracting Original Images.zip...")
    t0 = time.time()
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        zf.extractall(STAGING_DIR)
    t1 = time.time()
    print(f"Extraction complete in {round(t1 - t0, 1)} s.")

    orig_dir = os.path.join(STAGING_DIR, "Original Images")
    if not os.path.exists(orig_dir):
        orig_dir = STAGING_DIR

    print(f"Inspecting directory: {orig_dir}")
    counts = {}
    metadata_files = []
    for root, dirs, files in os.walk(orig_dir):
        rel = os.path.relpath(root, orig_dir)
        if rel != ".":
            counts[rel] = len([f for f in files if not f.startswith(".")])
        for f in files:
            ext = f.split(".")[-1].lower() if "." in f else ""
            if ext in ["csv", "xlsx", "txt", "md", "json"]:
                metadata_files.append(os.path.join(rel, f))

    print("\n--- Per-Class Counts in Original Images ---")
    total_files = 0
    for folder, count in sorted(counts.items()):
        print(f"  {folder}: {count}")
        total_files += count
    print(f"Total files: {total_files} (expected: 1701)")
    print(f"Metadata files found: {metadata_files}")

if __name__ == "__main__":
    download_file()
    extract_and_verify()
