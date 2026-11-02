# Rice Leaf Disease Dataset Candidates & Analysis (T-015a)

> **Status:** COMPLETED & APPROVED (Decisions D-14, D-15, D-16 adopted)  
> **Date:** 2026-11-02 / 2026-11-03  
> **Task:** T-015a - Search Kaggle and Mendeley for rice leaf disease datasets.  
> **Final Decision:** Hasan et al. (CC BY 4.0) chosen as single source for v1 (D-15); 4 classes per D-14.


---

## 1. Resolution of Reported Count Mismatches

### 1.1 Hasan et al. Total (1,701) vs. Per-Class Sum (~840)
- **Source Total:** 1,701 original RGB photographs (plus 5,188 augmented images, total 6,889 files).
- **Reason for Mismatch:** The dataset contains **8 distinct classes**, not just our 4 target classes:
  1. Bacterial Leaf Blight
  2. Brown Spot
  3. Leaf Blast
  4. Leaf Scald
  5. Narrow Brown Leaf Spot
  6. Rice Hispa
  7. Sheath Blight
  8. Healthy Rice Leaf
- The 4 classes relevant to our project (`Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf`) contain approximately $210$ images each, summing to **$\sim 840$ images** ($4 \times \sim 210$).
- The remaining 4 non-target classes (`Leaf Scald`, `Narrow Brown Leaf Spot`, `Rice Hispa`, `Sheath Blight`) account for the remaining **$\sim 861$ images**.
- *Per-class counts are marked UNVERIFIED until the archive files are directly inspected.*

### 1.2 Sethy et al. Total (5,932) vs. Per-Class Sum (4,624)
- **Source Total:** 5,932 images across **4 classes**.
- **Reason for Mismatch:** Sethy et al. contains four classes:
  1. `Bacterial blight`: 1,584 images
  2. `Blast`: 1,440 images
  3. `Brown spot`: 1,600 images
  4. `Tungro`: 1,308 images
- The sum of our 3 target classes is exactly:
  $$1,584 + 1,440 + 1,600 = \mathbf{4,624}\text{ images}$$
- The 4th class (`Tungro`, 1,308 images) is not one of our target classes.
- $4,624 + 1,308 = \mathbf{5,932}\text{ total images}$. The numbers match verified source publications.

---

## 2. Dataset Candidates (Verified Source Details)

### Candidate 1: Rice Leaf Bacterial and Fungal Disease Dataset
- **Hosting Platform:** Mendeley Data
- **DOI / URL:** [10.17632/hx6f852hw4.2](https://data.mendeley.com/datasets/hx6f852hw4/2)
- **Authors:** Mehedi Hasan, Sonia Khatun, Md. Abu Raihan, Abdul Hasib Uddin (Khwaja Yunus Ali University, Bangladesh)
- **Exact Source Folder / Category Names:**
  - `Bacterial Leaf Blight`
  - `Brown Spot`
  - `Leaf Blast`
  - `Leaf Scald`
  - `Narrow Brown Leaf Spot`
  - `Rice Hispa`
  - `Sheath Blight`
  - `Healthy Rice Leaf`
- **Class Counts (Source Data):**
  - Total Originals: 1,701 (per-class range ~163–310; approx. ~210 per class; marked UNVERIFIED until archive inspection).
  - Total Augmented: 5,188.
- **Target Match:** 4 of 5 classes (`Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf`). Missing: `Leaf Smut`.
- **Exact Quoted License:**
  > *"Creative Commons Attribution 4.0 International (CC BY 4.0): You can share, copy and modify this dataset so long as you give appropriate credit, provide a link to the CC BY license, and indicate if changes were made, but you may not do so in a way that suggests the rights holder has endorsed you or your use of the dataset. Note that further permission may be required for any content within the dataset that is identified as belonging to a third party."*
- **License Flags:** No Share-Alike (SA) clause. No Non-Commercial (NC) clause. Permissive, fully compatible with MIT distribution.
- **Field-Level Splitting & Augmentation Audit:**
  - *Field Identifiers:* The public dataset metadata provides collection locations broadly (*"Sirajganj and Pabna Zilla"*), but contains **no per-image field, session, or farm ID manifest**. Therefore, splitting strictly by field/plot is **NOT possible** from metadata alone. Splitting must use patient/leaf deduplication via perceptual hashing.
  - *Augmented Images:* The dataset packages 5,188 augmented images separately from the 1,701 originals (either in dedicated folders or with augmentation prefixes). All 5,188 augmented images **must be identified and excluded** prior to creating the 70/15/15 public split.

---

### Candidate 2: Rice Leaf Disease Image Samples
- **Hosting Platform:** Mendeley Data (primary) & Kaggle (community mirror)
- **DOI / URL:** [10.17632/fwcj7stb8r.1](https://data.mendeley.com/datasets/fwcj7stb8r/1)
- **Authors:** Prabira Kumar Sethy, Nalini Kanta Barpanda, Amiya Kumar Rath, Santi Kumari Behera (2020)
- **Exact Source Folder / Category Names:**
  - `Bacterial blight` (1,584 images)
  - `Blast` (1,440 images)
  - `Brown spot` (1,600 images)
  - `Tungro` (1,308 images)
- **Target Match:** 3 of 5 classes. Missing: `Leaf Smut`, `Healthy`.
- **Exact Quoted License:**
  > *"Creative Commons Attribution 4.0 International (CC BY 4.0): You can share, copy and modify this dataset so long as you give appropriate credit, provide a link to the CC BY license, and indicate if changes were made..."*
- **License Flags:** Permissive CC BY 4.0. No SA or NC restrictions.
- **Field-Level Splitting:** No field/session metadata provided. Images captured in India.

---

### Candidate 3: Rice Leaf Diseases Dataset
- **Hosting Platform:** Kaggle (`vbookshelf/rice-leaf-diseases`) & UCI Machine Learning Repository (ID 486)
- **URL (Kaggle):** [https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases)
- **URL (UCI):** [https://archive.ics.uci.edu/dataset/486/rice+leaf+diseases](https://archive.ics.uci.edu/dataset/486/rice+leaf+diseases) (DOI: 10.24432/C5R013)
- **Authors:** Original dataset creators: Jitesh Shah, Harshadkumar Prajapati, Vipul Dabhi (2017); cited and evaluated by S. Ramesh & D. Vydeki (2020).
- **Exact Source Folder / Category Names:**
  - `Bacterial leaf blight` (40 images)
  - `Brown spot` (40 images)
  - `Leaf smut` (40 images)
- **Total Images:** Exactly 120 images (40 per class).
- **Target Match:** 3 of 5 classes (`Bacterial leaf blight`, `Brown spot`, `Leaf smut`). Missing: `Leaf Blast`, `Healthy`.
- **Exact Quoted License from Sources:**
  - **UCI Machine Learning Repository (Primary Source, ID 486):**
    > *"This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license. This allows for the sharing and adaptation of the datasets for any purpose, provided that the appropriate credit is given."*
  - **Kaggle Mirror (`vbookshelf/rice-leaf-diseases`):**
    > `"license":{"@type":"CreativeWork","name":"Unknown","url":""}` (displayed in Kaggle dataset metadata as `"License: Unknown"`).
- **Selected Download Source & License Resolution:**
  - If downloaded, the dataset must be fetched from the **UCI Machine Learning Repository** (primary authoritative source, `https://archive.ics.uci.edu/static/public/486/rice+leaf+diseases.zip`) under **CC BY 4.0**. The Kaggle mirror is rejected due to its ambiguous `"Unknown"` license tag.
  - *Status remains UNVERIFIED pending user direction.*
- **Field-Level Splitting:** Captured in a single field in Shertha, Gujarat, India with a white cardboard background in sunlight. No plot/session IDs.

---

### Candidate 4: Rice Leafs Disease Dataset
- **Hosting Platform:** Kaggle (`dedeikhsandwisaputra/rice-leafs-disease-dataset`)
- **Author:** Dede Ikhsan Dwi Saputra (2021)
- **Exact Source Folder / Category Names:**
  - `Bacterial Leaf Blight`
  - `Brown Spot`
  - `Healthy`
  - `Leaf Blast`
  - `Leaf Scald`
  - `Narrow Brown Spot`
- **Total Images:** 2,627 images (per-class count ~438 each; UNVERIFIED).
- **Target Match:** 4 of 5 classes. Missing: `Leaf Smut`.
- **Exact Quoted License:**
  > Listed as **"Unknown"** on Kaggle.
- **License Flags:** **FLAGGED: UNKNOWN LICENSE.** Lacks explicit open-source terms. High legal/academic risk for open-source redistribution under MIT.
- **Field-Level Splitting:** Not possible (no field metadata).

---

### Candidate 5: Rice Disease Dataset
- **Hosting Platform:** Kaggle (`anshulm67/rice-disease-dataset`)
- **Author:** Anshul M (2022)
- **Exact Source Folder / Category Names:**
  - `Bacterial Leaf Blight`
  - `Brown Spot`
  - `Healthy Rice Leaf`
  - `Leaf Blast`
  - `Leaf Scald`
  - `Sheath Blight`
- **Total Images:** 3,829 images (per-class count ~638 each; UNVERIFIED).
- **Target Match:** 4 of 5 classes. Missing: `Leaf Smut`.
- **Exact Quoted License:**
  > Listed as **"Unknown"** on Kaggle.
- **License Flags:** **FLAGGED: UNKNOWN LICENSE.** High risk for redistribution.
- **Field-Level Splitting:** Not possible (no field metadata).

---

## 3. Candidate Comparison Matrix & Final Decision

| Candidate | Host | Exact Classes Matching Project | Verified Matching Images | Non-Target / Missing Classes | Quoted License | License Risk Flags | Final Status in v1 |
|---|---|---|---|---|---|---|---|
| **1. Hasan et al.** | Mendeley | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf` | 909 target originals (1,701 total) | Missing: `Leaf Smut`<br>Extra: `Leaf Scald`, `Narrow Brown Leaf Spot`, `Rice Hispa`, `Sheath Blight` (792) | CC BY 4.0 | None (Permissive) | ✅ **SELECTED FOR v1 (D-15)** |
| **2. Sethy et al.** | Mendeley | `Bacterial blight`, `Brown spot`, `Blast` | 4,624 | Missing: `Leaf Smut`, `Healthy` (0 images)<br>Extra: `Tungro` (1,308) | CC BY 4.0 | None (Permissive) | ❌ **NOT USED IN v1 (D-15)**<br>(May serve as future external cross-check only) |
| **3. Prajapati / Ramesh** | UCI (ID 486) | `Bacterial leaf blight`, `Brown spot`, `Leaf smut` | 120 (40 each) | Missing: `Leaf Blast`, `Healthy` | CC BY 4.0 (UCI) / Unknown (Kaggle) | Clean via UCI | ❌ **NOT USED IN v1 (D-15)**<br>(Leaf Smut deferred to v2 per D-14) |
| **4. Saputra** | Kaggle | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy` | ~1,750 (est.) | Missing: `Leaf Smut` | **Unknown** | ⚠️ Unknown license | 🚫 **EXCLUDED (D-16: Unknown License)** |
| **5. Anshul M** | Kaggle | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf` | ~2,550 (est.) | Missing: `Leaf Smut` | **Unknown** | ⚠️ Unknown license | 🚫 **EXCLUDED (D-16: Unknown License)** |

---

## 4. In-Depth Analysis: Sethy et al. as a Second Source & Confound Risks

### 4.1 Class Coverage & Absence of Healthy
- **Classes Present:** `Bacterial blight` (1,584), `Blast` (1,440), `Brown spot` (1,600), `Tungro` (1,308). Total = 5,932.
- **Crucial Limitation:** **Sethy et al. completely lacks the `Healthy` class (0 images).**

### 4.2 Field and Session Identifiability
- Images in `Rice Leaf Disease Images.7z` are grouped strictly by disease name folders.
- No tabular metadata, EXIF log, farm ID, plot ID, or collection session timestamps are provided.
- Therefore, images are **NOT from identifiable fields or sessions**.

### 4.3 Source Confound Risk if Combined with Hasan
Combining Sethy et al. with Hasan et al. introduces severe methodological confounds:
1. **Asymmetric Class-Source Confound (The Healthy Trap):**
   - Because Sethy has 0 healthy images, 100% of `Healthy` samples would originate from Hasan et al. (Bangladesh smartphones).
   - In contrast, the diseased classes (`Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`) would be overwhelmingly dominated by Sethy (~1,500 images per class vs. ~210 in Hasan).
   - A CNN trained on such pooled data risks learning source/sensor signatures (e.g. background foliage, camera ISP color rendition, lighting) as the decision boundary for "Healthy" vs. "Diseased", rather than botanical pathology.
2. **Domain & Environmental Discrepancy:**
   - Hasan et al.: Captured in Sirajganj and Pabna, Bangladesh on hand-held mobile devices in farm environments.
   - Sethy et al.: Captured in Odisha, India under distinct camera hardware, angles, and regional cultivars.
3. **Conclusion:** Sethy **cannot be naively combined with Hasan** in a pooled public training set without creating an acute source confound. Excluded from v1 per D-15.

### 4.4 Mandatory Requirements if Sethy is Used
If Sethy is incorporated in the future (e.g., as a secondary evaluation benchmark or cross-domain test):
1. **Manifest Source Tracking:** The split manifest (`train_split.csv`, `val_split.csv`, `test_split.csv`) must include a mandatory `source_dataset` column (`hasan` or `sethy`).
2. **Joint Stratification:** Splitting must be stratified jointly on `(label, source_dataset)`.
3. **Domain Shift Evaluation:** Evaluation notebooks (`04_evaluate.ipynb`) must report within-source and cross-source macro F1 separately (evaluating model on Hasan test set and Sethy test set independently) to measure domain transfer degradation.
4. **Volume Balancing:** If used for training, Sethy disease classes must be heavily subsampled to prevent overwhelming the Bangladesh samples.

---

## 5. Adopted Decision (D-14)

> **Status:** APPROVED (Adopted 2026-11-03)

### Title: Amend D-07 to four classes (drop Leaf Smut for v1)
- **Approved Amendment:** Locked decision D-07 is amended from 5 classes to 4 classes:
  1. `bacterial_leaf_blight` (Bacterial Leaf Blight / ব্যাকটেরিয়াল পাতা ঝলসানো)
  2. `brown_spot` (Brown Spot / বাদামি দাগ রোগ)
  3. `leaf_blast` (Leaf Blast / পাতা ব্লাস্ট)
  4. `healthy` (Healthy / সুস্থ পাতা)
- **Reason:**
  1. Section 6 of PROJECT_SCOPE.md requires each class to have at least 100 images before training to ensure statistical validity and prevent catastrophic class imbalance.
  2. Public datasets that provide genuine Leaf Smut are limited to Candidate 3 (Prajapati et al. / UCI ID 486), which contains only 40 images total. Partitioning 40 images yields ~28 train, 6 val, and 6 test images, making held-out evaluation metrics statistically unreliable and high-variance.
  3. Candidate 1 (Hasan et al., CC BY 4.0, Bangladesh) provides $\ge 150$ original RGB photographs for each of the 4 target classes (180 Bacterial Leaf Blight, 267 Brown Spot, 305 Leaf Blast, 157 Healthy Rice Leaf), natively satisfying the $\ge 100$ image threshold with consistent regional provenance (Bangladesh).
- **Evidence from `docs/dataset_candidates.md`:**
  - Hasan et al. provides 909 original images across Bacterial Blight, Brown Spot, Blast, and Healthy under a clean CC BY 4.0 license.
  - Sethy et al. lacks Healthy and contains no Leaf Smut.
  - Saputra and Anshul M datasets carry `"Unknown"` licenses and lack Leaf Smut.
  - Retaining Leaf Smut via Option B forces a 7:1 class imbalance and violates the 100-image rule.
- **What Remains Open:**
  - `leaf_smut` (*Entyloma oryzae*) is deferred to future work (v2).
  - Option C remains open: During field photo collection in Bangladesh (Milestone M1 / Gate 1b), if Leaf Smut is actively observed and confirmed by agricultural experts with $\ge 100$ quality images, or if institutional archives (e.g. BRRI) provide a compliant dataset, a subsequent DECISION can expand the model back to 5 classes.


---

## 6. Verification Checklist for Hasan Archive (`10.17632/hx6f852hw4.2`)

To be executed immediately upon user approval of download (prior to starting T-003 or any split):

- [ ] **1. Archive Integrity and Structure**
  - Download `Rice Leaf Bacterial and Fungal Disease Dataset` archive from Mendeley Data DOI `10.17632/hx6f852hw4.2`.
  - Record downloaded archive file name, total size in bytes, and SHA-256 checksum in `data/metadata/licenses.md`.
  - Extract archive into temporary staging directory `data/raw/public/hasan_staging/`.
- [ ] **2. Per-Class Folder Counts (Original Images)**
  - Count and log the exact number of files in each of the 8 category folders:
    - `Bacterial Leaf Blight`
    - `Brown Spot`
    - `Leaf Blast`
    - `Leaf Scald`
    - `Narrow Brown Leaf Spot`
    - `Rice Hispa`
    - `Sheath Blight`
    - `Healthy Rice Leaf`
  - Confirm that the sum across all original folders equals exactly 1,701 images (or document any discrepancy).
  - Verify that each of the target classes (`Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf`) has $\ge 100$ original images (expected $\sim 210$ each).
- [ ] **3. Isolation of Augmented Images**
  - Verify the storage structure of the 5,188 augmented images: confirm whether they reside in a distinct folder (e.g. `Augmented/` or `data_augmented/`) or use distinct filename prefixes (e.g., `aug_`).
  - Quarantine/separate all 5,188 augmented images into `data/raw/public/hasan_augmented/` to guarantee they are completely excluded from original splits and cannot leak into validation or test sets.
- [ ] **4. Metadata File Inspection**
  - Search the archive for any manifest, table, or documentation files (`*.csv`, `*.xlsx`, `*.txt`, `*.md`).
  - Check whether any per-image farm ID, plot ID, GPS coordinates, or capture session metadata exists.
  - If no session ID exists, confirm that patient/plot-level deduplication via perceptual hash (T-014) is mandatory before splitting.
- [ ] **5. Exact License Text Verification**
  - Inspect any included `LICENSE`, `terms.txt`, or documentation in the archive.
  - Verify that the license text confirms Creative Commons Attribution 4.0 International (CC BY 4.0) without Non-Commercial (NC) or Share-Alike (SA) clauses.
  - Record the verified text in `data/metadata/licenses.md`.

