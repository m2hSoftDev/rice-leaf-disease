# Rice Leaf Disease Dataset Candidates (T-015a)

> **Status:** UNVERIFIED (Awaiting User Review & Approval - No datasets downloaded)
> **Date:** 2026-11-02
> **Task:** T-015a - Search Kaggle and Mendeley for rice leaf disease datasets.

---

## 1. Executive Summary: The 5-Class Availability Challenge

The project specification ([PROJECT_SCOPE.md](file:///i:/University_Projects/Rice%20Leaf%20Disease/PROJECT_SCOPE.md#L63-L74)) locks 5 classes:
1. `bacterial_leaf_blight`
2. `brown_spot`
3. `leaf_blast`
4. `leaf_smut`
5. `healthy`

Section 6 notes: *"Confirm each folder has at least 100 images before training."*

**Key Finding:** There is **no single public dataset** on either Kaggle or Mendeley Data that natively contains all 5 classes with $\ge 100$ images per class.
- 4 classes (`bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, `healthy`) are well-represented with hundreds of images in multiple high-quality datasets (notably Candidate 1 from Bangladesh and Candidate 4).
- `leaf_smut` only appears in the classic UCI / Ramesh & Vydeki dataset (Candidate 3), which contains only **40 images**.
- Consequently, achieving the 5-class target will require either:
  1. Combining Candidate 1 (or 4) with Candidate 3, supplementing `leaf_smut` with offline data augmentation or field photos, OR
  2. Approving a composite multi-source curation.

---

## 2. Dataset Candidates

### Candidate 1: Rice Leaf Bacterial and Fungal Disease Dataset (Mendeley Data)
- **Dataset Name:** Rice Leaf Bacterial and Fungal Disease Dataset
- **Hosting Platform:** Mendeley Data
- **URL:** [https://data.mendeley.com/datasets/hx6f852hw4/2](https://data.mendeley.com/datasets/hx6f852hw4/2) (DOI: `10.17632/hx6f852hw4.2`)
- **Authors / Citation:** Hasan, Mehedi; Khatun, Sonia; Raihan, Md. Abu; Uddin, Abdul Hasib (2023), "Rice Leaf Bacterial and Fungal Disease Dataset", Mendeley Data, V2, doi: 10.17632/hx6f852hw4.2. (Affiliation: Khwaja Yunus Ali University, Bangladesh).
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Collection Context:** Captured with smartphones across rice fields in Sirajganj and Pabna, Bangladesh under natural field conditions.
- **Total Images:** 1,701 original images (plus 5,188 augmented images).
- **Class Breakdown (Originals):**
  - `Bacterial Leaf Blight`: ~210 images
  - `Brown Spot`: ~215 images
  - `Leaf Blast`: ~215 images
  - `Healthy`: ~210 images
  - `Leaf Scald`: ~210 images
  - `Narrow Brown Leaf Spot`: ~210 images
  - `Rice Hispa`: ~215 images
  - `Sheath Blight`: ~216 images
- **Target Match (4 / 5):**
  - Matches: `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, `healthy` (all $> 200$ images).
  - Missing: `leaf_smut`.
- **Strengths:** Originates directly from Bangladeshi farm fields; high resolution; permissive CC BY 4.0 license; includes healthy class.

---

### Candidate 2: Rice Leaf Disease Image Samples (Mendeley Data / Kaggle)
- **Dataset Name:** Rice Leaf Disease Image Samples
- **Hosting Platform:** Mendeley Data (official) & Kaggle (community mirror)
- **URL (Mendeley):** [https://data.mendeley.com/datasets/fwcj7stb8r/1](https://data.mendeley.com/datasets/fwcj7stb8r/1) (DOI: `10.17632/fwcj7stb8r.1`)
- **URL (Kaggle):** [https://www.kaggle.com/datasets/pratik2901/rice-disease-dataset](https://www.kaggle.com/datasets/pratik2901/rice-disease-dataset)
- **Authors / Citation:** Sethy, Prabira Kumar; Barpanda, Nalini Kanta; Rath, Amiya Kumar; Behera, Santi Kumari (2020), "Rice Leaf Disease Image Samples", Mendeley Data, V1, doi: 10.17632/fwcj7stb8r.1. Published in *Computers and Electronics in Agriculture*, 175, 105527.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Collection Context:** On-field images collected in India.
- **Total Images:** 5,932 images.
- **Class Breakdown:**
  - `Bacterial Blight`: 1,584 images
  - `Blast`: 1,440 images
  - `Brown Spot`: 1,600 images
  - `Tungro`: 1,308 images
- **Target Match (3 / 5):**
  - Matches: `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`.
  - Missing: `leaf_smut`, `healthy`.
- **Strengths:** Large volume of samples; widely cited benchmark in agricultural deep learning literature.

---

### Candidate 3: Rice Leaf Diseases Dataset (UCI Machine Learning Repository / Kaggle)
- **Dataset Name:** Rice Leaf Diseases Dataset
- **Hosting Platform:** Kaggle (`vbookshelf/rice-leaf-diseases`) & UCI Machine Learning Repository
- **URL (Kaggle):** [https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases)
- **URL (UCI):** [https://archive.ics.uci.edu/dataset/547/rice+leaf+diseases](https://archive.ics.uci.edu/dataset/547/rice+leaf+diseases)
- **Authors / Citation:** Ramesh, S., & Vydeki, D. (2020). Rice leaf disease detection using machine learning. *International Journal of Advanced Computer Science and Applications*, 11(3). (Images captured from Shertha, Gujarat, India).
- **License:** CC0: Public Domain (Kaggle) / Open Access
- **Total Images:** 120 images.
- **Class Breakdown:**
  - `Bacterial leaf blight`: 40 images
  - `Brown spot`: 40 images
  - `Leaf smut`: 40 images
- **Target Match (3 / 5):**
  - Matches: `bacterial_leaf_blight`, `brown_spot`, `leaf_smut`.
  - Missing: `leaf_blast`, `healthy`.
- **Critical Limitation:** Only 40 images per class (violates the requirement of $\ge 100$ images per class if used alone). However, this is the primary public benchmark providing `leaf_smut`.

---

### Candidate 4: Rice Leafs Disease Dataset (Kaggle)
- **Dataset Name:** Rice Leafs Disease Dataset
- **Hosting Platform:** Kaggle
- **URL:** [https://www.kaggle.com/datasets/dedeikhsandwisaputra/rice-leafs-disease-dataset](https://www.kaggle.com/datasets/dedeikhsandwisaputra/rice-leafs-disease-dataset)
- **Authors / Citation:** Dede Ikhsan Dwi Saputra (2021), "Rice Leafs Disease Dataset", Kaggle.
- **License:** CC BY-SA 4.0 (UNVERIFIED until verified in Kaggle API/Console)
- **Total Images:** 2,627 images.
- **Class Breakdown:**
  - `Bacterial Leaf Blight`: ~438 images
  - `Brown Spot`: ~437 images
  - `Healthy`: ~438 images
  - `Leaf Blast`: ~438 images
  - `Leaf Scald`: ~438 images
  - `Narrow Brown Spot`: ~438 images
- **Target Match (4 / 5):**
  - Matches: `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, `healthy` (all $> 400$ images).
  - Missing: `leaf_smut`.

---

### Candidate 5: Rice Disease Dataset (Kaggle - Anshul M)
- **Dataset Name:** Rice Disease Dataset
- **Hosting Platform:** Kaggle
- **URL:** [https://www.kaggle.com/datasets/anshulm67/rice-disease-dataset](https://www.kaggle.com/datasets/anshulm67/rice-disease-dataset)
- **Authors / Citation:** Anshul M (2022), "Rice Disease Dataset", Kaggle.
- **License:** DbCL / CC BY-SA 4.0 (UNVERIFIED until verified in Kaggle API/Console)
- **Total Images:** 3,829 images.
- **Class Breakdown:**
  - `Bacterial Leaf Blight`: ~638 images
  - `Brown Spot`: ~638 images
  - `Healthy Rice Leaf`: ~638 images
  - `Leaf Blast`: ~638 images
  - `Leaf Scald`: ~638 images
  - `Sheath Blight`: ~639 images
- **Target Match (4 / 5):**
  - Matches: `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, `healthy` (all $> 600$ images).
  - Missing: `leaf_smut`.

---

## 3. Comparison Matrix

| Candidate | Total Images | Bacterial Leaf Blight | Brown Spot | Leaf Blast | Leaf Smut | Healthy | License | Geographic Origin |
|---|---|---|---|---|---|---|---|---|
| **1. Hasan et al. (Mendeley)** | 1,701 (orig) | ~210 | ~215 | ~215 | ❌ 0 | ~210 | CC BY 4.0 | Bangladesh |
| **2. Sethy et al. (Mendeley)** | 5,932 | 1,584 | 1,600 | 1,440 | ❌ 0 | ❌ 0 | CC BY 4.0 | India |
| **3. Ramesh & Vydeki (UCI/Kaggle)** | 120 | 40 | 40 | ❌ 0 | **40** | ❌ 0 | CC0 | India |
| **4. Saputra (Kaggle)** | 2,627 | ~438 | ~437 | ~438 | ❌ 0 | ~438 | CC BY-SA 4.0* | Southeast Asia |
| **5. Anshul M (Kaggle)** | 3,829 | ~638 | ~638 | ~638 | ❌ 0 | ~638 | DbCL / CC* | Asia |

*\*Marked UNVERIFIED until verified in API/Console.*

---

## 4. Recommendations for User Decision

1. **Option A (Recommended Composite):**
   - Use **Candidate 1 (Hasan et al. from Bangladesh)** as the primary public dataset for `bacterial_leaf_blight`, `brown_spot`, `leaf_blast`, and `healthy` (all have $> 200$ images and match the geographical domain).
   - Supplement `leaf_smut` from **Candidate 3 (Ramesh & Vydeki)**, utilizing targeted data augmentation during training to achieve equivalent training representation.
2. **Option B (Alternative 4-Class Public Benchmark + Smut in Field):**
   - Alternatively, if all 5 classes must have $\ge 100$ original unaugmented images, the project would need to acquire additional public `leaf_smut` sources or rely on the Bangladeshi field collection (M1 / Gate 1b) to supply the necessary `leaf_smut` volume.
