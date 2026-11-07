# Dataset Card: Rice Leaf Bacterial and Fungal Disease Dataset (Hasan et al.)

> **Status:** DRAFT (Task T-005)  
> **Last Updated:** 2026-11-03  
> **Governing Decisions:** D-14 (4 classes for v1), D-15 (single source for v1), D-16 (exclusion of unknown licenses), D-24 (EXIF upright processing), D-29 (dataset credit placement)

---

## 1. Dataset Summary

The primary public dataset for training and initial benchmark evaluation in version 1 of the Rice Leaf Disease Detection project is the **Rice Leaf Bacterial and Fungal Disease Dataset**, contributed by Mehedi Hasan et al. from Khwaja Yunus Ali University, Bangladesh.

* **Repository:** Mendeley Data
* **DOI:** [10.17632/hx6f852hw4.2](https://doi.org/10.17632/hx6f852hw4.2)
* **Dataset Version:** Version 2 (Published 2023-11-25)
* **Authors:** Mehedi Hasan, Sonia Khatun, Md. Abu Raihan, Abdul Hasib Uddin
* **Institution:** Khwaja Yunus Ali University, Sirajganj, Bangladesh

---

## 2. Licensing & Legal Terms

* **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
* **Full Attribution & Citation (Decision D-29):**
  > Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: images were re-oriented according to EXIF data and re-encoded for training.
* **Exact Quoted License Text:**
  > *"Creative Commons Attribution 4.0 International (CC BY 4.0): You can share, copy and modify this dataset so long as you give appropriate credit, provide a link to the CC BY license, and indicate if changes were made, but you may not do so in a way that suggests the rights holder has endorsed you or your use of the dataset. Note that further permission may be required for any content within the dataset that is identified as belonging to a third party."*
* **Modification Statement (CC BY 4.0 compliance & Decision D-24):**
  Images were modified from their original archive state: orientation tag 6 images were transposed $90^\circ$ clockwise into native upright portrait rasters (`ImageOps.exif_transpose`) and re-encoded at quality=95 with 4:4:4 subsampling (`subsampling=0`) in `data/processed/hasan_upright/`.
* **Attribution Scope (Decision D-29):**
  Dataset credit appears on the About screen, README.md, docs/dataset_card.md, and the Play Store listing. It does not appear on Scan, Result, History, splash, onboarding, or navigation.
* **License Audit:**
  * Non-Commercial (NC) restriction: **None** (commercial use permissible with credit).
  * Share-Alike (SA) restriction: **None** (derivative works do not require CC copyleft).
  * Compatibility: **Fully compatible** with project open-source MIT distribution (D-01).
* **Third-Party Clause:** The license explicitly notes that *"further permission may be required for any content within the dataset that is identified as belonging to a third party."* No third-party proprietary assets or watermarks were identified during inspection.

---

## 3. Data Collection & Provenance

* **Geographic Origin:** Sirajganj and Pabna districts, Bangladesh (as declared by dataset authors).
* **Collection Method:** Smartphone photographs taken in farmer fields under natural ambient sunlight.
* **Verification Status:** **UNVERIFIED beyond the source authors' own published textual description.** The dataset archive contains no raw camera EXIF metadata, GPS latitude/longitude logs, farmer consent IDs, or camera make/model specifications.
* **Botanical Context:** Rice (*Oryza sativa*). Specific crop cultivars, growth stages, fertilizer regimens, and weather conditions at capture time are **UNVERIFIED / undocumented**.

---

## 4. Class Distribution & Filtering for v1

The downloaded archive (`Original Images.zip`) contains 1,701 verified original RGB photographs across 8 folders. For project v1, only the 4 classes aligned with decision D-14 are included.

### 4.1 Target Classes for v1 (909 Original Images)

| Class Index | Target Class Name | Original Image Count | 100-Image Rule Threshold | Status in v1 |
|---|---|---|---|---|
| 0 | `Bacterial Leaf Blight` | 180 | ✅ Passed (180 $\ge$ 100) | Included |
| 1 | `Brown Spot` | 267 | ✅ Passed (267 $\ge$ 100) | Included |
| 2 | `Leaf Blast` | 305 | ✅ Passed (305 $\ge$ 100) | Included |
| 3 | `Healthy Rice Leaf` | 157 | ✅ Passed (157 $\ge$ 100) | Included (Smallest class) |
| **Total Target Originals** | | **909** | **All classes $\ge$ 100** | |

### 4.2 Excluded Non-Target Classes (792 Original Images)
The remaining 4 classes in the archive are outside the project scope and are excluded from all v1 training, validation, and test sets:
* `Leaf scald`: 189 images
* `Narrow Brown Leaf Spot`: 117 images
* `Rice Hispa`: 215 images
* `Sheath Blight`: 271 images
* *Total Excluded Originals:* 792 images ($909 + 792 = 1,701$ total originals).

### 4.3 Augmented Images (5,188 Images - Excluded)
* The authors published 5,188 pre-augmented images in a separate archive (`Augmented Images.zip`).
* **Handling:** Quarantined in `data/raw/public/hasan_augmented/`. These images are **strictly excluded** from data splits to eliminate artificial replication across train, validation, and test partitions. Training augmentation is performed on-the-fly per Section 8.2.

---

## 5. Technical Specifications

* **Image Format:** JPEG (`.jpg`), RGB color space.
* **Dimensions:** Variable resolutions (smartphone native, typically ~1920x1080 to ~4000x3000; standardized to 224x224 during preprocessing).
* **Archive Checksums:**
  * `Original Images.zip`: 1,664,385,692 bytes, SHA-256: `eb1e804ae414250d7a333a1c3820c49a520c2f09e2e6a38f280e90f58a4f62fb`
  * `Augmented Images.zip`: 2,016,076,446 bytes, SHA-256: `0a1536f49bd78c63b53ab1538d862472f40e6c3970a88e83da80d3b939b1fda4`

---

## 6. Known Limitations & Bias Considerations

1. **Absence of Session and Plot Metadata:** No metadata tables exist in the archive. There are no farm IDs, plot IDs, or capture timestamps.
2. **Impossibility of Metadata Field-Level Splitting:** Because images lack plot/session IDs, splitting strictly by farm or field cannot be done via metadata alone. Perceptual hash deduplication (`T-014`) is required to detect near-duplicate shots of the same leaf.
3. **Healthy Class Margin:** `Healthy Rice Leaf` has 157 images, which is the narrowest margin above the $\ge 100$ image threshold. Near-duplicate removal in T-014 must be verified to ensure the count remains $\ge 100$.
4. **Third-Party Rights Notice:** Covered by standard CC BY 4.0 terms, users should be cognizant of the generic third-party clause.
5. **Geographical Domain Concentration:** Sourced exclusively from Sirajganj and Pabna, Bangladesh. Performance on field samples from other Bangladeshi divisions (e.g., Barishal, Sylhet, Rangpur) will be evaluated in Milestone M4 (`test_field`) to quantify the regional domain gap.

---

## 7. Processing & Derivative Artifacts (Decision D-24)

Under decision **D-24**, all 1,701 original images in `data/raw/public/hasan_staging/Original Images/` are transposed to their upright EXIF orientation (`ImageOps.exif_transpose`) and saved to `data/processed/hasan_upright/`:
* **Orientation Transformation:** PIL `ImageOps.exif_transpose` (transposes orientation tag 6 images $90^\circ$ clockwise into native upright portrait rasters and strips the EXIF orientation tag).
* **JPEG Export Parameters:** `quality=95`, `subsampling=0` (4:4:4 chroma subsampling, preventing color subsampling degradation on disease lesion borders).
* **Target Classes Scope:** 907 active images assigned via `split_manifest.csv` (excluding cross-class duplicate `group_035`). Total file count: 1,701 images across all 8 classes.

