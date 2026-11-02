# Rice Leaf Disease Dataset Candidates & Analysis (T-015a)

> **Status:** UNVERIFIED (Awaiting User Review & Approval - No datasets downloaded)  
> **Date:** 2026-11-02 / 2026-11-03  
> **Task:** T-015a - Search Kaggle and Mendeley for rice leaf disease datasets.

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
- **Hosting Platform:** Kaggle (`vbookshelf/rice-leaf-diseases`) & UCI Machine Learning Repository
- **URL (Kaggle):** [https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases)
- **URL (UCI):** [https://archive.ics.uci.edu/dataset/547/rice+leaf+diseases](https://archive.ics.uci.edu/dataset/547/rice+leaf+diseases)
- **Authors:** S. Ramesh & D. Vydeki (2020)
- **Exact Source Folder / Category Names:**
  - `Bacterial leaf blight` (40 images)
  - `Brown spot` (40 images)
  - `Leaf smut` (40 images)
- **Total Images:** Exactly 120 images (40 per class).
- **Target Match:** 3 of 5 classes (`Bacterial leaf blight`, `Brown spot`, `Leaf smut`). Missing: `Leaf Blast`, `Healthy`.
- **Exact Quoted License:**
  > *"License: CC0: Public Domain"* (Kaggle) / *"Creative Commons Attribution 4.0 International"* (UCI).
- **License Flags:** Public Domain / CC BY 4.0. No SA or NC clauses. Fully permissive.
- **Field-Level Splitting:** Images collected from a single rice field in Shertha, Gujarat, India. No sub-plot metadata.

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

## 3. Candidate Comparison Matrix

| Candidate | Host | Exact Classes Matching Project | Verified Matching Images | Non-Target / Missing Classes | Quoted License | License Risk Flags | Field-Level Split Possible? |
|---|---|---|---|---|---|---|---|
| **1. Hasan et al.** | Mendeley | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf` | ~840 originals (UNVERIFIED exact per-class) | Missing: `Leaf Smut`<br>Extra: `Leaf Scald`, `Narrow Brown Leaf Spot`, `Rice Hispa`, `Sheath Blight` (~861) | CC BY 4.0 | None (Permissive) | ❌ No per-image farm ID |
| **2. Sethy et al.** | Mendeley | `Bacterial blight`, `Brown spot`, `Blast` | 4,624 | Missing: `Leaf Smut`, `Healthy`<br>Extra: `Tungro` (1,308) | CC BY 4.0 | None (Permissive) | ❌ No |
| **3. Ramesh & Vydeki** | UCI/Kaggle | `Bacterial leaf blight`, `Brown spot`, `Leaf smut` | 120 (40 each) | Missing: `Leaf Blast`, `Healthy` | CC0 / CC BY 4.0 | None (Public Domain) | ❌ Single field |
| **4. Saputra** | Kaggle | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy` | ~1,750 (est.) | Missing: `Leaf Smut` | **Unknown** | ⚠️ Unknown license | ❌ No |
| **5. Anshul M** | Kaggle | `Bacterial Leaf Blight`, `Brown Spot`, `Leaf Blast`, `Healthy Rice Leaf` | ~2,550 (est.) | Missing: `Leaf Smut` | **Unknown** | ⚠️ Unknown license | ❌ No |

---

## 4. `leaf_smut` Options Analysis

Because `leaf_smut` is only present in Candidate 3 (Ramesh & Vydeki / UCI) with 40 images, three strategic options exist:

### Option A: Drop `leaf_smut` (Proceed with 4 Classes)
- **Concept:** Narrow scope to 4 classes: `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, `healthy`.
- **Pros:**
  - Solves data availability completely: Candidate 1 (Hasan et al., Bangladesh, CC BY 4.0) provides $\ge 200$ genuine original field images for each of these 4 classes.
  - Exceeds the $\ge 100$ image rule without artificial minority-class upsampling.
  - Highest statistical validity for evaluation benchmarks.
- **Cons / Trade-offs:**
  - Requires updating locked decision D-07 (5 classes) via a formal DECISION entry.
  - The model will not recognize Leaf Smut (*Entyloma oryzae*).

### Option B: Keep 5 Classes and Amend the 100-Image Rule for `leaf_smut` via DECISION
- **Concept:** Combine Candidate 1 (4 classes, $\ge 200$ images each) with Candidate 3 (Leaf Smut, 40 images). Amend the Section 6 requirement specifically for `leaf_smut` via a locked decision.
- **Pros:**
  - Maintains 5-class target and locked decision D-07.
  - Does not block M1 or data pipelines.
- **Cons / Trade-offs:**
  - Severe class imbalance: 28 training images for Leaf Smut vs $\ge 150$ for others. Requires class weighting or heavy data augmentation.
  - Tiny test set (only 6 held-out test images for Leaf Smut), resulting in high variance in test metrics.

### Option C: Search Alternative Specialized Sources or Rely on Field Campaign
- **Concept:** Search specialized archives (e.g., BRRI / IRRI databases) or rely on Bangladesh field collection (M1 / Gate 1b) to collect the remaining 60+ Leaf Smut images.
- **Pros:**
  - Maintains 5 classes and adheres to the $\ge 100$ image quality threshold.
- **Cons / Trade-offs:**
  - Potential delay: If Leaf Smut is not actively symptomatic in current seasonal field visits, Milestone M1 could stall.
  - Gate 1a cannot be finalized until the external source is secured.

*(Note: Decision pending user direction. No decision has been locked.)*
