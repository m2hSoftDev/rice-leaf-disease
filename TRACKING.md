# TRACKING.md

## Current Status
- Milestone: M0
- Active task: none
- Last updated: 2026-11-02

## Task Board
| ID | Task | Status | Owner | Notes |
|---|---|---|---|---|
| T-001 | Create GitHub repo | IN_PROGRESS | agent | Local folder structure, .gitignore, and git init complete; remote GitHub repo setup pending user action |
| T-002 | Python env + TensorFlow check | BLOCKED | agent | TF 2.21.0 & deps installed in .venv; import blocked by missing MSVC++ 2015-2022 x64 Redistributable (msvcp140.dll) |
| T-003 | Create Flutter project, verify it builds for Android | TODO | agent | |
| T-004 | Choose license and write LICENSE file (D-01) | TODO | agent | |
| T-005 | Write dataset card draft in docs/dataset_card.md | TODO | agent | |
| T-010 | Download public datasets, record source and license in licenses.md | TODO | agent | |
| T-011 | Build field photo collection plan (sites, dates, consent form, photo protocol) | TODO | agent | |
| T-012 | Collect field photos (target 300–500, all 5 classes where present) | TODO | agent | |
| T-013 | Get expert labels for field photos; fill field_log.csv | TODO | agent | |
| T-014 | Dedupe public data with perceptual hashing | TODO | agent | |
| T-015 | Create train/val/test splits (Section 7.3) and save split manifests | TODO | agent | |
| T-015a | Dataset candidate search | UNVERIFIED | agent | Search Kaggle/Mendeley; save details to docs/dataset_candidates.md; no downloads until approved |
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
- D-01: MIT license (YYYY-MM-DD)
- D-08: State management is Riverpod (2026-11-02)
- D-09: Local storage for scan history is sqflite (2026-11-02)
- D-10: On-device Grad-CAM is out of scope for v1. Grad-CAM runs only in the Python evaluation notebook for test_field errors. The app shows no heatmaps in v1. Precomputed demo heatmaps are not allowed (2026-11-02)
- D-11: Low-confidence behavior (top confidence < 60%): show an "Uncertain" banner with the confidence score and the text "Please consult an agricultural expert." Hide the advisory section. The top class name may appear in the banner as a weak guess, but no treatment advice is shown for it (2026-11-02)
- D-12: Milestones M2 and M3 use public data only and may run in parallel with field collection. Replace Gate 1 with Gate 1a (public splits and dataset cards, end of M1) and Gate 1b (field photos collected and expert-labeled, required before M4) (2026-11-02)
- D-13: The primary cross-platform entry point is `python -m scripts.reproduce_all`. Do not create a bash script. Add a PowerShell wrapper only if I ask for one (2026-11-02)

## Blockers and Questions
- T-002: TensorFlow import requires Microsoft Visual C++ 2015-2022 Redistributable (x64) installed on Windows (missing msvcp140.dll / msvcp140_1.dll). User must run official installer with admin elevation.
- T-001: GitHub remote creation requires user action (GitHub CLI not installed/authenticated).
- T-015a: No single public dataset provides all 5 classes with >= 100 images. User decision needed on composite approach.

## Daily Log
- 2026-11-02: Recorded decisions D-08 to D-13; updated PROJECT_SCOPE.md to reflect decisions D-08 through D-13; added task T-015a to task board.
- 2026-11-02: Executed T-015a (dataset search saved to docs/dataset_candidates.md); executed T-001 locally (created Section 12 directory structure, .gitignore, .gitkeep files, git init); created requirements.txt with pinned versions and installed dependencies in .venv; T-002 marked BLOCKED due to missing MSVC++ Redistributable (msvcp140.dll).