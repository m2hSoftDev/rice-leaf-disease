# TRACKING.md

## Current Status
- Milestone: M6
- Note: Gate 2 met across all 3 seeds (mean test macro F1 0.8609). Gate 3: PASSED for size, accuracy drop, and Keras-to-TFLite parity (20/20). Flutter-side parity is open as T-054b (M6). T-050 to T-054 complete. T-060 and T-061 complete (App skeleton, routes, theme, localization, Bangla font & ARB strings).
- Active task: None
- Last updated: 2026-11-04

## Task Board
| ID | Task | Status | Owner | Notes |
|---|---|---|---|---|
| T-001 | Create GitHub repo | DONE | agent | Pushed to https://github.com/m2hsoftdev/rice-leaf-disease.git on 2026-11-03 (commit 06fe726) |
| T-002 | Python env + TensorFlow check | DONE | agent | Verified TensorFlow 2.21.0 imports successfully in .venv on 2026-11-03 |
| T-003 | Create Flutter project, verify it builds for Android | DONE | agent | Created Flutter project in app/ (package name com.m2hsoftdev.ricedisease, Android-only per D-02); copied and declared assets (model_fp16.tflite, labels.json, preprocess_config.json); pinned Dart/Flutter/dependency versions; flutter build apk --debug succeeded on 2026-11-04 (app-debug.apk 148.1 MB) |
| T-004 | Choose license and write LICENSE file (D-01) | DONE | agent | MIT License chosen per D-01; Copyright (c) 2026 Mehedi Hasan; root LICENSE created on 2026-11-03 |
| T-005 | Write dataset card draft in docs/dataset_card.md | DONE | agent | Draft completed in docs/dataset_card.md with verified Hasan counts, license quote, and UNVERIFIED collection markings |
| T-010 | Download public datasets, record source and license in licenses.md | DONE | agent | Hasan archive downloaded, extracted, verified (1,701 images, SHA-256 verified, CC BY 4.0); data/metadata/licenses.md recorded |
| T-011 | Build field photo collection plan (sites, dates, consent form, photo protocol) | TODO | user | |
| T-012 | Collect field photos (target 300–500, all 5 classes where present) | TODO | agent | |
| T-013 | Get expert labels for field photos; fill field_log.csv | TODO | agent | |
| T-014 | Dedupe public data with perceptual hashing | DONE | agent | pHash analysis complete (Hamming <= 5 across all target classes); 108 duplicate groups found; group_035 excluded per D-17; per D-18 groups are kept in full and split by group; active counts before split: Bacterial Leaf Blight 179, Brown Spot 267, Leaf Blast 304, Healthy 157 (total 907 images across 737 groups) |

| T-015 | Create train/val/test splits (Section 7.3) and save split manifests | DONE | agent | Group-stratified split manifest created with seed 42 in data/metadata/split_manifest.csv; 70/15/15 target achieved (634 train, 135 val, 138 test); zero leakage |
| T-015a | Dataset candidate search | DONE | agent | Completed; source choice recorded in D-15 (Hasan et al. CC BY 4.0 only for v1; 4 classes per D-14) |


| T-020 | Class distribution report and sample grid | DONE | agent | Generated results/metrics/class_distribution.csv, class_distribution.md, and sample grids in results/figures/class_samples/ on 2026-11-03 |
| T-021 | B0 majority baseline metrics | DONE | agent | Majority class is Leaf Blast (213 train); val macro F1=0.1271 (acc=34.07%), test macro F1=0.1230 (acc=32.61%), kappa=0.0000 on 2026-11-03 |
| T-022 | B1 small CNN from scratch | DONE | agent | Trained 3-block small CNN from scratch with Adam lr=1e-3, balanced class weights, and train-only augmentation; 6 epochs run (early stopped at epoch 6, best val_loss 1.3694 at epoch 1); val macro F1=0.1012 (acc=19.26%), test macro F1=0.0669 (acc=13.04%), kappa=-0.0504; results in results/metrics/baseline_b1.csv and baseline_b1.md |
| T-023 | B2 frozen MobileNetV2 (Stage 1) | DONE | agent | MobileNetV2 frozen backbone (ImageNet weights, alpha 1.0) with Dense 128 -> Dropout 0.3 -> Dense 4 head; trained with Adam lr=1e-3, balanced class weights, train augmentation; early stopped at epoch 9 (patience 5 on val macro F1 per D-19, best epoch 4 with val macro F1 0.7670, val acc 76.30%); test macro F1=0.7369 (acc=71.01%), kappa=0.6051; results in results/metrics/baseline_b2.csv and baseline_b2.md |
| T-024 | Log results in results/metrics/baselines.csv | DONE | agent | Aggregated B0, B1, and B2 metrics into results/metrics/baselines.csv on 2026-11-03; verified all values against baseline_b0, baseline_b1, and baseline_b2 source files |
| T-030 | Stage 1 and Stage 2 training of M1 with train_config.yaml | DONE | agent | Stage 2 fine-tuning completed from B2 checkpoint; last 30 layers of MobileNetV2 unfrozen with Adam lr=1e-5 (trainable params: 1,675,204); 26 epochs run (early stopped on val macro F1 per D-19, best epoch 21 with val macro F1=0.8561, val acc=85.19%); test macro F1=0.8534 (acc=83.33%), kappa=0.7730; Gate 2 MET (0.8534 >= 0.80); results in results/metrics/m1.csv and m1.md |
| T-031 | Augmentation pipeline with visual check | DONE | agent | Visual inspection complete across 8 samples per class in results/figures/augmentation_check/; confirmed no disease alteration between Brown Spot and Leaf Blast, zero augmentation on val/test, and no augmented images saved to disk; results in results/metrics/augmentation_check.md |
| T-032 | Evaluate on test_public (macro F1 target >= 0.80) | TODO | agent | |
| T-033 | Three-seed repeat, mean and std | DONE | agent | Evaluated M1 across seeds 42, 43, 44; mean test macro F1=0.8609 ± 0.0132, mean test acc=84.54% ± 2.09%, mean kappa=0.7895; Gate 2 met on all three seeds (0.8534, 0.8532, 0.8761); results in results/metrics/m1_seeds.csv and m1_seeds.md |
| T-034 | Optional EfficientNet-B0 comparison | TODO | agent | |
| T-040 | Evaluate on test_field; compute gap vs test_public | TODO | agent | |
| T-041 | Grad-CAM on all test_field errors; manual lesion check on 30 samples | TODO | agent | |
| T-042 | Failure analysis grouping and report | TODO | agent | |
| T-043 | Confusion matrices and per-class tables for report | TODO | agent | |
| T-050 | Export float16 TFLite | DONE | agent | Exported canonical model (m1_seed44_best.keras) to results/export/model_fp16.tflite; measured size 4.62 MB (4,840,736 bytes), within the <= 5.0 MB budget; test accuracy 86.96%, test macro F1 0.8791 (Gate 3 requires T-054 parity check before passing) |
| T-051 | Try int8 quantization with representative data | DONE | agent | Quantized canonical model using representative dataset (N=200) from training split only to results/export/model_int8.tflite; measured size 2.77 MB (2,903,240 bytes), within <= 5.0 MB budget; test accuracy 86.23%, test macro F1 0.8635 |
| T-052 | Re-evaluate TFLite on both test sets; record accuracy drop | DONE | agent | Evaluated fp16 and int8 models on val (N=135) and test (N=138); measured fp16 accuracy drop vs Keras is +0.00 pp on both val and test (within <= 2.0 pp limit); measured int8 accuracy drop is +0.72 pp on test and +4.44 pp on val; results in results/metrics/export_evaluation.csv and export_evaluation.md |
| T-053 | Write labels.json and preprocess_config.json | DONE | agent | Generated results/export/preprocess_config.json (MobileNetV2 [-1, 1], bilinear, 224x224) and results/export/labels.json with explicit model index mapping (0: BLB, 1: Brown Spot, 2: Healthy, 3: Leaf Blast) and warning against Section 6 index order |
| T-054 | Verify parity: Python TFLite output vs Flutter output on 20 test images (must match top-1) | DONE | agent | Evaluated Keras vs Float16 TFLite parity on 20 stratified test images (seed 42, 5/class); 20/20 (100.0%) top-1 matches; verified labels.json index order (Healthy=2, Leaf Blast=3, not transposed); Gate 3 passed for size, accuracy drop, and Keras-to-TFLite parity; results in results/metrics/parity_check.csv and parity_check.md |
| T-054b | Flutter vs Python TFLite top-1 parity on 20 test images. Run after T-063. Must match on all 20 before Gate 3 is fully closed. | TODO | agent | |
| T-060 | App skeleton: routes, theme, localization setup | DONE | agent | App skeleton complete in app/: Material 3 theme (48 dp touch target, system text scaling), routes (splash, onboarding, home, result, history, about), dynamic locale provider (en/bn toggle with SharedPreferences persistence), l10n ARB files generated; all 5 widget tests passed; flutter build apk --debug succeeded (debug APK size: 153.98 MB / 161,461,355 bytes, measurement only, not release size) |
| T-061 | Bangla font and strings (ARB files) | DONE | agent | Embedded Noto Sans Bengali (Regular 0.1364 MB, Bold 0.1381 MB, OFL 1.1) in app/assets/fonts/; recorded in docs/licenses_third_party.md; expanded app_en.arb and app_bn.arb with exact Section 6 Bangla disease names, disclaimer (F-08), uncertain banner (D-11), and About credits; 8/8 widget tests passed; debug build passed |
| T-062 | Image picker and preprocessing service | DONE | agent | Added image_picker: 1.2.4 and image: 4.12.0; implemented PreprocessService with 10 MB limit (F-02), JPG/PNG validation, EXIF orientation handling, bilinear resize to 224x224, and (x / 127.5) - 1.0 normalization to Float32List [1, 224, 224, 3]; synthetic unit test passed within 1e-3; real-image parity evaluated on 3 test images (observed max diff 0.3644 due to downsampling coordinate mapping and JPEG IDCT; gracefully skips if dataset absent); all 13 tests passed; debug build passed |
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
- D-19: For B2 and M1, the model checkpoint and early stopping are selected by validation macro F1 (not val_loss). B1 used val_loss; this difference is documented and B1 is not re-run (APPROVED, 2026-11-03)
- D-20: The canonical model for export is selected by validation macro F1 under D-19. Seed 44 (val macro F1 0.8669) is the canonical model. Seeds 42 and 43 are reported as repeats. Test scores are not used for selection (APPROVED, 2026-11-04)
- D-21: The deployment model is float16 TFLite (results/export/model_fp16.tflite). Int8 is not used in v1 because its validation accuracy drop (4.44 pp) exceeds the 2 pp limit in Section 8.9 (APPROVED by developer, 2026-11-04)
- D-22: The canonical label order is the alphabetical order used in training, recorded in labels.json (0 bacterial_leaf_blight, 1 brown_spot, 2 healthy, 3 leaf_blast). The index column in Section 6 is documentation only. All inference code must map indices through labels.json (APPROVED by developer, 2026-11-04)

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
- 2026-11-03: T-020 DONE - Generated class distribution report (class_distribution.csv, class_distribution.md) and train sample grids in results/figures/class_samples/; set T-011 owner to user.
- 2026-11-03: T-021 DONE - Evaluated B0 majority class baseline (Leaf Blast) on val and test splits; saved results/metrics/baseline_b0.csv and baseline_b0.md.
- 2026-11-03: T-022 DONE - Trained B1 small CNN from scratch (6 epochs run, early stopped at epoch 6, best val_loss=1.3694 at epoch 1); achieved val macro F1=0.1012 (acc=19.26%) and test macro F1=0.0669 (acc=13.04%); saved metrics to results/metrics/baseline_b1.csv, baseline_b1.md, and confusion matrix figure to results/figures/b1_confusion.png.
- 2026-11-03: Spec update - Section 8.3 updated Dense 5 to Dense 4 to align with 4-class v1 scope under D-14.
- 2026-11-03: T-023 DONE - Trained B2 frozen MobileNetV2 Stage 1 (9 epochs run, early stopped on val macro F1 per D-19, best epoch 4 with val macro F1=0.7670, val acc=76.30%); evaluated on held-out test split: test macro F1=0.7369 (acc=71.01%), kappa=0.6051; saved results to results/metrics/baseline_b2.csv, baseline_b2.md, and results/figures/b2_confusion.png.
- 2026-11-03: T-024 DONE - Built results/metrics/baselines.csv summarizing B0, B1, and B2 metrics; verified all values against source files.
- 2026-11-03: T-030 DONE - Stage 2 fine-tuning of M1 from B2 checkpoint (26 epochs run, early stopped on val macro F1 per D-19, best epoch 21 with val macro F1=0.8561, val acc=85.19%); evaluated on held-out test split: test macro F1=0.8534 (acc=83.33%), kappa=0.7730; Quality Gate 2 MET (0.8534 >= 0.80); Brown Spot to Leaf Blast confusion reduced from 18 to 11; saved results to results/metrics/m1.csv, m1.md, and baselines.csv.
- 2026-11-03: T-031 DONE - Built visual augmentation check grids (8 samples per class) in results/figures/augmentation_check/; confirmed pipeline preserves disease morphology (circular brown spots and spindle blast lesions unaltered); documented findings in results/metrics/augmentation_check.md.
- 2026-11-03: T-033 DONE - Completed 3-seed repeat of M1 (seeds 42, 43, 44); mean test macro F1=0.8609 ± 0.0132, mean test accuracy=84.54% ± 2.09%; Gate 2 holds across all three seeds; Brown Spot -> Leaf Blast errors reduced to 11, 9, 3 (mean 7.67 vs B2's 18); saved results to results/metrics/m1_seeds.csv and m1_seeds.md.
- 2026-11-04: Recorded approved decision D-20 (canonical model selection by validation macro F1 under D-19: seed 44).
- 2026-11-04: T-050 to T-053 DONE - Exported canonical model (m1_seed44_best.keras) to Float16 (4.62 MB) and Int8 (2.77 MB) TFLite models at results/export/; re-evaluated on val and test splits; measured Float16 drop at 0.00 pp on both val and test, Int8 drop at +0.72 pp test and +4.44 pp val; generated preprocess_config.json and labels.json with model output index alignment; saved metrics to results/metrics/export_evaluation.csv and export_evaluation.md (Gate 3 remains open pending T-054 parity check).
- 2026-11-04: Recorded approved decisions D-21 (float16 deployment model, int8 excluded due to 4.44 pp val drop) and D-22 (canonical alphabetical label order via labels.json; Section 6 index doc only).
- 2026-11-04: T-054 DONE - Evaluated Keras vs Float16 TFLite top-1 parity on 20 stratified test images (seed 42); achieved 20/20 (100.0%) matches; verified labels.json indices (Healthy=2, Leaf Blast=3, not transposed); Quality Gate 3 PASSED; saved results to results/metrics/parity_check.csv and parity_check.md.
- 2026-11-04: Corrected Gate 3 status (PASSED for size, accuracy drop, and Keras-to-TFLite parity 20/20; Flutter-side parity open as T-054b in M6); added T-054b to Task Board.
- 2026-11-04: T-003 DONE - Created Flutter Android skeleton in app/ with package name com.m2hsoftdev.ricedisease (D-02); removed counter demo; pinned versions in pubspec.yaml; copied and declared model_fp16.tflite, labels.json, and preprocess_config.json in app/assets/; verified flutter test passed; built debug APK successfully via flutter build apk --debug (build/app/outputs/flutter-apk/app-debug.apk).




- 2026-11-04: T-060 DONE - Implemented Flutter app skeleton, 6 placeholder routes with first-launch splash redirection via shared_preferences, Material 3 high-contrast theme, Riverpod locale toggle provider (en/bn), and l10n setup; all widget tests passed (5/5); debug APK built successfully (153.98 MB measurement).
- 2026-11-04: T-061 DONE - Downloaded Noto Sans Bengali v3.011 (OFL 1.1), embedded Regular/Bold fonts into app/assets/fonts/ with docs/licenses_third_party.md; expanded English and Bangla ARB files with exact Section 6 disease names, disclaimer, and uncertain banner; verified all 23 Bangla glyphs present; all widget tests passed (8/8); debug APK built successfully.
- 2026-11-04: T-062 DONE - Implemented PreprocessService and image picking validation (10 MB limit, JPG/PNG); audited Hasan dataset EXIF orientation (88.8% Orientation 6); built Python parity fixture test/fixtures/preprocess_expected.json; evaluated 3 test images (max diff 0.3644 on sharp lesion boundaries due to downsampling coordinate differences between package:image and TensorFlow, ~0.02 on smooth regions); all 13 Flutter tests passed; debug APK built successfully.
