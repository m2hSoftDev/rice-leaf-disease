# TRACKING.md

## Current Status
- Milestone: M0
- Active task: None (T-002 DONE)
- Last updated: 2026-11-03

## Task Board
| ID | Task | Status | Owner | Notes |
|---|---|---|---|---|
| T-001 | Create GitHub repo | DONE | agent | Pushed to https://github.com/m2hsoftdev/rice-leaf-disease.git on 2026-11-03 (commit 06fe726) |
| T-002 | Python env + TensorFlow check | DONE | agent | Verified TensorFlow 2.21.0 imports successfully in .venv on 2026-11-03 |
| T-003 | Create Flutter project, verify it builds for Android | TODO | agent | |
| T-004 | Choose license and write LICENSE file (D-01) | DONE | agent | MIT License chosen per D-01; Copyright (c) 2026 Mehedi Hasan; root LICENSE created on 2026-11-03 |
| T-005 | Write dataset card draft in docs/dataset_card.md | DONE | agent | Draft completed in docs/dataset_card.md with verified Hasan counts, license quote, and UNVERIFIED collection markings |
| T-010 | Download public datasets, record source and license in licenses.md | DONE | agent | Hasan archive downloaded, extracted, verified (1,701 images, SHA-256 verified, CC BY 4.0); data/metadata/licenses.md recorded |
| T-011 | Build field photo collection plan (sites, dates, consent form, photo protocol) | TODO | agent | |
| T-012 | Collect field photos (target 300–500, all 5 classes where present) | TODO | agent | |
| T-013 | Get expert labels for field photos; fill field_log.csv | TODO | agent | |
| T-014 | Dedupe public data with perceptual hashing | DONE | agent | pHash analysis complete (Hamming <= 5 across all target classes); 108 duplicate groups found; group_035 excluded per D-17; per D-18 groups are kept in full and split by group; active counts before split: Bacterial Leaf Blight 179, Brown Spot 267, Leaf Blast 304, Healthy 157 (total 907 images across 737 groups) |

| T-015 | Create train/val/test splits (Section 7.3) and save split manifests | DONE | agent | Group-stratified split manifest created with seed 42 in data/metadata/split_manifest.csv; 70/15/15 target achieved (634 train, 135 val, 138 test); zero leakage |
| T-015a | Dataset candidate search | DONE | agent | Completed; source choice recorded in D-15 (Hasan et al. CC BY 4.0 only for v1; 4 classes per D-14) |


| T-020 | Class distribution report and sample grid | TODO | agent | |
| T-021 | B0 majority baseline metrics | TODO | agent | |
| T-022 | B1 small CNN from scratch | TODO | agent | |
| T-023 | B2 frozen MobileNetV2 (Stage 1) | TODO | agent | |
| T-024 | Log results in results/metrics/baselines.csv | TODO | agent | |
| T-030 | Stage 1 and Stage 2 training of M1 with train_config.yaml | TODO | agent | |
| T-031 | Augmentation pipeline with visual check | TODO | agent | |
| T-032 | Evaluate on test_public (macro F1 target >= 0.80) | TODO | agent | |
| T-033 | Three-seed repeat, mean and std | TODO | agent | |
| T-034 | Optional EfficientNet-B0 comparison | TODO | agent | |
| T-040 | Evaluate on test_field; compute gap vs test_public | TODO | agent | |
| T-041 | Grad-CAM on all test_field errors; manual lesion check on 30 samples | TODO | agent | |
| T-042 | Failure analysis grouping and report | TODO | agent | |
| T-043 | Confusion matrices and per-class tables for report | TODO | agent | |
| T-050 | Export float16 TFLite | TODO | agent | |
| T-051 | Try int8 quantization with representative data | TODO | agent | |
| T-052 | Re-evaluate TFLite on both test sets; record accuracy drop | TODO | agent | |
| T-053 | Write labels.json and preprocess_config.json | TODO | agent | |
| T-054 | Verify parity: Python TFLite output vs Flutter output on 20 test images (must match top-1) | TODO | agent | |
| T-060 | App skeleton: routes, theme, localization setup | TODO | agent | |
| T-061 | Bangla font and strings (ARB files) | TODO | agent | |
| T-062 | Image picker and preprocessing service | TODO | agent | |
| T-063 | TFLite inference service in an isolate | TODO | agent | |
| T-064 | Result screen with confidence and uncertain state (F-05) | TODO | agent | |
| T-065 | Advisory JSON loader (Bangla and English) | TODO | agent | |
| T-066 | Onboarding and disclaimer (F-08) | TODO | agent | |
| T-067 | History with local DB (F-09) | TODO | agent | |
| T-069 | About screen with credits and licenses (F-14) | TODO | agent | |
| T-070 | Unit tests for preprocessing and label mapping | TODO | agent | |
| T-071 | Widget test for result screen | TODO | agent | |
| T-072 | Performance test on low-end device; record latency, RAM, app size | TODO | agent | |
| T-080 | Google Play developer account and identity verification | TODO | agent | |
| T-081 | Privacy policy page (GitHub Pages or similar) | TODO | agent | |
| T-082 | Data Safety form answers (no data collected or shared in v1; confirm in console) | TODO | agent | |
| T-083 | Store listing: icon, screenshots, short and full description (English and Bangla) | TODO | agent | |
| T-084 | Upload to internal or closed testing track; confirm current Play requirements in console | TODO | agent | |
| T-085 | Collect tester feedback; fix critical issues | TODO | agent | |
| T-086 | Production release (after Play requirements are met) | TODO | agent | |
| T-090 | README with setup, data download, reproduce command, results, limitations | TODO | agent | |
| T-091 | docs/limitations.md and docs/ethics.md | TODO | agent | |
| T-092 | Final report (see Section 14) | TODO | agent | |
| T-093 | Demo video (3 minutes, screen recording of the app on a phone) | TODO | agent | |
| T-094 | Presentation slides and live demo rehearsal | TODO | agent | |

Status values: TODO, IN_PROGRESS, BLOCKED, REVIEW, DONE, UNVERIFIED

## Decisions Log
- D-01: MIT license (2026-11-03)
- D-08: State management is Riverpod (2026-11-02)
- D-09: Local storage for scan history is sqflite (2026-11-02)
- D-10: On-device Grad-CAM is out of scope for v1. Grad-CAM runs only in the Python evaluation notebook for test_field errors. The app shows no heatmaps in v1. Precomputed demo heatmaps are not allowed (2026-11-02)
- D-11: Low-confidence behavior (top confidence < 60%): show an "Uncertain" banner with the confidence score and the text "Please consult an agricultural expert." Hide the advisory section. The top class name may appear in the banner as a weak guess, but no treatment advice is shown for it (2026-11-02)
- D-12: Milestones M2 and M3 use public data only and may run in parallel with field collection. Replace Gate 1 with Gate 1a (public splits and dataset cards, end of M1) and Gate 1b (field photos collected and expert-labeled, required before M4) (2026-11-02)
- D-13: The primary cross-platform entry point is `python -m scripts.reproduce_all`. Do not create a bash script. Add a PowerShell wrapper only if I ask for one (2026-11-02)
- D-14: Amend D-07 to four classes for v1 (bacterial_leaf_blight, brown_spot, leaf_blast, healthy). Leaf Smut is deferred to v2 (APPROVED, 2026-11-03)
  - Proposed Amendment: Locked decision D-07 amended from 5 to 4 classes: bacterial_leaf_blight, brown_spot, leaf_blast, healthy.
  - Reason: Section 6 requires >= 100 images per class before training. Public Leaf Smut is limited to 40 images (UCI ID 486), causing severe class imbalance (7:1) and unreliable test metrics. Candidate 1 (Hasan et al.) provides verified counts: Bacterial Leaf Blight 180, Brown Spot 267, Leaf Blast 305, Healthy 157 (original images, before deduplication).
  - Note: Healthy (157) is the smallest class; the 100-image rule must be re-checked after T-014 deduplication.
  - What Remains Open: Leaf Smut deferred to v2. Field campaign (Gate 1b) or institutional partner (BRRI) may supply >= 100 images to expand back to 5 classes under a future DECISION.
- D-15: v1 trains and evaluates on the Hasan et al. (CC BY 4.0) dataset only. Sethy et al. and Ramesh & Vydeki are not used in training or test splits for v1. Sethy may be used later as an external cross-check only, and only after a new DECISION (APPROVED, 2026-11-03)
- D-16: Saputra and Anshul M are excluded because their licenses are Unknown (APPROVED, 2026-11-03)
- D-17: Exclude both instances of the cross-class duplicate group_035 (Bacterial_leaf_Blight (33).jpg and Leaf_blast (289).jpg) from v1. Reason: the same image carries two conflicting labels (APPROVED, 2026-11-03)
- D-18: Near-duplicate groups (pHash Hamming distance <= 5, computed across all target classes) are kept in full. They are not deleted. Each group is assigned to one split only, so near-copies cannot leak between train and test (APPROVED, 2026-11-03)

## Blockers and Questions
- None (T-002 resolved: TensorFlow 2.21.0 imports cleanly in .venv).

## Daily Log
- 2026-11-02: Recorded decisions D-08 to D-13; updated PROJECT_SCOPE.md to reflect decisions D-08 through D-13; added task T-015a to task board.
- 2026-11-02: Executed T-015a (dataset search saved to docs/dataset_candidates.md); executed T-001 locally (created Section 12 directory structure, .gitignore, .gitkeep files, git init); created requirements.txt with pinned versions and installed dependencies in .venv; T-002 marked BLOCKED due to missing MSVC++ Redistributable (msvcp140.dll).
- 2026-11-03: T-001 DONE - Updated .gitignore with strict dataset/model exclusions and pushed to origin (commits b41c399, 06fe726).
- 2026-11-03: T-002 checked - TensorFlow import error persists (msvcp140.dll missing); remains BLOCKED.
- 2026-11-03: T-015a updated docs/dataset_candidates.md with exact folder names, quoted licenses, count mismatch explanations, and leaf_smut options analysis (UNVERIFIED).
- 2026-11-03: Resolved Candidate 3 license (UCI CC BY 4.0 vs Kaggle Unknown), added Sethy confound analysis, Option A PROPOSED decision draft, and Hasan verification checklist to docs/dataset_candidates.md.
- 2026-11-03: Recorded approved decisions D-14 (amend D-07 to 4 classes, drop Leaf Smut for v1), D-15 (single source Hasan et al. CC BY 4.0 for v1), and D-16 (exclude unknown licenses); updated PROJECT_SCOPE.md Sections 6, 15, 17; marked T-015a DONE; completed T-010 (downloaded, extracted, verified Hasan archive, 1,701 originals verified against SHA-256 eb1e804..., created data/metadata/licenses.md).
- 2026-11-03: T-005 DONE - Created dataset card draft in docs/dataset_card.md with verified Hasan counts, CC BY 4.0 license, and UNVERIFIED collection status.
- 2026-11-03: T-014 DONE - Ran perceptual hash deduplication analysis (Hamming <= 5 on 64-bit DCT pHash) across 909 target images; found 108 near-duplicate groups; generated data/metadata/dedup_report.csv; all 4 target classes comfortably pass >= 100 threshold (Healthy: 146).
- 2026-11-03: Recorded approved decision D-17 (exclude cross-class duplicate group_035 due to conflicting labels) in PROJECT_SCOPE.md Section 17 and TRACKING.md.
- 2026-11-03: Recorded approved decision D-18 (keep near-duplicate groups in full and assign each group to one split only) in PROJECT_SCOPE.md Section 17 and TRACKING.md.
- 2026-11-03: Corrected T-014 notes in TRACKING.md: designated 'keep one representative' counts as informational and documented active pre-split counts (907 images across 737 groups, group_035 excluded).
- 2026-11-03: Audited all 412,686 pairwise combinations across all target classes; verified that no cross-class near-duplicates exist beyond group_035.
- 2026-11-03: Spot-checked 10 random duplicate groups (including 3 Brown Spot, 3 Leaf Blast) and generated side-by-side grids in results/figures/dedup_spotcheck/; confirmed 100% true near-duplicates and 0 false positives.
- 2026-11-03: T-004 DONE - Created root LICENSE file under MIT License with copyright holder Mehedi Hasan (D-01).
- 2026-11-03: T-002 DONE - Verified TensorFlow import in .venv (version 2.21.0); MSVC++ Redistributable installed and functional.
- 2026-11-03: T-015 DONE - Generated group-stratified train/val/test split (seed 42) into data/metadata/split_manifest.csv and results/metrics/split_summary.csv; verified zero leakage and exact count matches across all 4 classes.



