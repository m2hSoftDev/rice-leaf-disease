# Dataset Licenses & Verification Log

## 1. Primary Public Dataset for v1 (Hasan et al.)

* **Dataset Title:** Rice Leaf Bacterial and Fungal Disease Dataset
* **Platform:** Mendeley Data
* **DOI:** [10.17632/hx6f852hw4.2](https://doi.org/10.17632/hx6f852hw4.2)
* **Authors:** Mehedi Hasan, Sonia Khatun, Md. Abu Raihan, Abdul Hasib Uddin (Khwaja Yunus Ali University, Sirajganj, Bangladesh)
* **Governing Decisions:** D-14 (4 classes), D-15 (single public source for v1)

### 1.1 Archive Integrity and Checksums

| Archive File | Size (Bytes) | Size (GiB) | SHA-256 Checksum | Location |
|---|---|---|---|---|
| `Original Images.zip` | 1,664,385,692 | 1.55 GiB | `eb1e804ae414250d7a333a1c3820c49a520c2f09e2e6a38f280e90f58a4f62fb` | `data/raw/public/hasan_staging/` |
| `Augmented Images.zip` | 2,016,076,446 | 1.88 GiB | `0a1536f49bd78c63b53ab1538d862472f40e6c3970a88e83da80d3b939b1fda4` | `data/raw/public/hasan_augmented/` |

### 1.2 Exact Quoted License Text
> *"Creative Commons Attribution 4.0 International (CC BY 4.0): You can share, copy and modify this dataset so long as you give appropriate credit, provide a link to the CC BY license, and indicate if changes were made, but you may not do so in a way that suggests the rights holder has endorsed you or your use of the dataset. Note that further permission may be required for any content within the dataset that is identified as belonging to a third party."*

* **License Flags:**
  * Non-Commercial (NC) clause: **NONE** (commercial use permitted under attribution).
  * Share-Alike (SA) clause: **NONE** (derivative works do not require CC BY copyleft).
  * Compatibility: **Fully compatible** with MIT open-source project distribution (D-01).

### 1.3 Per-Class Counts in Original Archive (1,701 total)

| Class / Folder Name | Image Count | Status for v1 | Target Rule ($\ge 100$) |
|---|---|---|---|
| `Bacterial Leaf Blight` | 180 | Target Class (Index 0) | ✅ Passed (180 $\ge$ 100) |
| `Brown Spot` | 267 | Target Class (Index 1) | ✅ Passed (267 $\ge$ 100) |
| `Leaf Blast` | 305 | Target Class (Index 2) | ✅ Passed (305 $\ge$ 100) |
| `Healthy Rice Leaf` | 157 | Target Class (Index 3) | ✅ Passed (157 $\ge$ 100) |
| `Leaf scald` | 189 | Non-target (Excluded from v1) | N/A |
| `Narrow Brown Leaf Spot` | 117 | Non-target (Excluded from v1) | N/A |
| `Rice Hispa` | 215 | Non-target (Excluded from v1) | N/A |
| `Sheath Blight` | 271 | Non-target (Excluded from v1) | N/A |
| **Sum across all 8 classes** | **1,701** | Matches reported source total | **909 Target Class Images** |

### 1.4 Augmented Images (5,188 total)
* All 5,188 augmented images are packaged by authors in `Augmented Images.zip` with filename prefix `augmented_image_*.jpg`.
* Quarantined in `data/raw/public/hasan_augmented/` to prevent data leakage into original train/val/test splits.

### 1.5 Metadata Audit
* The archives contain **no metadata tables** (`*.csv`, `*.xlsx`, `*.txt`, `*.md`, `*.json`).
* No per-image farm ID, plot ID, GPS coordinates, or capture session identifiers exist in filenames or archive files.
* **Audit finding:** Field-level splitting by metadata is not possible. Patient/leaf deduplication via perceptual hashing (`T-014`) is strictly mandatory before splitting.

---

## 2. Excluded and Deferred Candidates

### 2.1 Prajapati et al. / Ramesh & Vydeki (UCI ID 486)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
  > *"This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license. This allows for the sharing and adaptation of the datasets for any purpose, provided that the appropriate credit is given."*
* **Status:** **NOT USED in v1 (D-15)**. Contains only 40 Leaf Smut images (violates 100-image threshold). Leaf Smut deferred to v2 (D-14).

### 2.2 Sethy et al. (Mendeley Data DOI 10.17632/fwcj7stb8r.1)
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
* **Status:** **NOT USED in v1 (D-15)**. Contains 0 Healthy images. Cannot be pooled with Hasan without causing a severe source confound. May serve as future external cross-check only after a new DECISION.

### 2.3 Saputra & Anshul M (Kaggle)
* **License:** Unknown.
* **Status:** **EXCLUDED (D-16)**. Prohibited due to undefined intellectual property rights.
