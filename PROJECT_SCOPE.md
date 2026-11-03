# PROJECT_SCOPE.md: Rice Leaf Disease Detection (Bangladesh)

## 0. Agent Instructions (read first)
- Read this file and TRACKING.md before any action.
- Work only on the task the user selects. Do not start unrelated tasks.
- Never change a locked decision (Section 17) without writing a DECISION entry in TRACKING.md and asking the user.
- After finishing a task, update its status in TRACKING.md and add a log line with the date.
- Do not invent dataset facts, licenses, or results. If a fact is unknown, mark it UNVERIFIED and ask.
- Keep all code reproducible: fixed random seeds, pinned versions in requirements.txt.

---

## 1. Project Summary
An offline-first mobile app (Android, Flutter) that identifies common rice leaf diseases from a phone photo and returns the disease name in English and Bangla, a confidence score, and a short advisory note. The classifier is a CNN trained in Python (TensorFlow/Keras), exported to TensorFlow Lite, and run on the device.

This is also a final-year project. Results must be reported honestly, including the gap between public-dataset and field-photo performance.

## 2. Goals
- G1: Classify 5 rice leaf conditions from a single photo with macro F1 of at least 0.80 on the held-out public test set.
- G2: Run inference fully offline on a low-end Android phone (2–3 GB RAM) in under 1 second per image.
- G3: Keep the mobile model under 5 MB.
- G4: Publish the code, notebooks, and dataset card on GitHub under an open-source license.
- G5: Publish the app on Google Play (testing track first).
- G6: Measure and report the accuracy drop between public and field images.

## 3. Non-Goals (out of scope)
- Pest identification, nutrient deficiency, or any non-visual diagnosis.
- Disease classes beyond the 5 listed in Section 6.
- Cloud backend, user accounts, or payments in v1.
- Medical or official agricultural advice. The app is advisory only.
- iOS release in v1 (Android only).

## 4. Target Users
- Primary: Smallholder rice farmers with a basic Android phone and intermittent internet.
- Secondary: Upazila agriculture extension officers who help farmers identify problems.
- Language: Bangla first, English second.

---

## 5. Feature List

Priority: M = Must (MVP), S = Should, C = Could.

| ID | Feature | Priority | Acceptance Criteria |
|---|---|---|---|
| F-01 | Capture photo with camera | M | Opens camera, returns image in under 2 s |
| F-02 | Pick photo from gallery | M | Selects JPG/PNG up to 10 MB |
| F-03 | Run on-device classification | M | Returns label and confidence with no network |
| F-04 | Show result card | M | Shows disease name (Bangla + English), confidence %, and advisory note |
| F-05 | Low-confidence warning | M | If top confidence < 60%, show "Uncertain" banner with confidence % and "Please consult an agricultural expert." Advisory section hidden; top class name may appear as weak guess, but no treatment advice is shown (D-11) |
| F-06 | Advisory text per disease | M | Loaded from local JSON; Bangla and English |
| F-07 | Bangla UI and fonts | M | All UI strings localized; Bangla renders correctly on Android 8+ |
| F-08 | Visible disclaimer | M | Shown on the result screen and on first launch |
| F-09 | Scan history (local) | S | Last 50 results saved in local storage with thumbnail and timestamp |
| F-10 | Explain-my-result view | C | Out of scope for v1 (D-10); Grad-CAM runs in Python evaluation only |
| F-11 | Language toggle | S | Switch between Bangla and English without restarting |
| F-12 | Share result as image | C | Creates a PNG card for WhatsApp sharing |
| F-13 | Field feedback button | C | "Was this correct?" saves locally, exportable as CSV |
| F-14 | About and credits screen | S | Lists dataset sources, licenses, researcher name, and version |

---

## 6. Classes (Labels)

| Index | Folder name | English | Bangla | Advisory focus |
|---|---|---|---|---|
| 0 | bacterial_leaf_blight | Bacterial Leaf Blight | ব্যাকটেরিয়াল পাতা ঝলসানো | Avoid excess nitrogen; drainage; consult expert |
| 1 | brown_spot | Brown Spot | বাদামি দাগ রোগ | Balanced fertilizer; seed treatment; consult expert |
| 2 | leaf_blast | Leaf Blast | পাতা ব্লাস্ট | Monitor humidity; resistant varieties; consult expert |
| 3 | healthy | Healthy | সুস্থ পাতা | No action needed; keep monitoring |
| [deferred] | leaf_smut | Leaf Smut | পাতার স্মাট | Deferred to v2 (D-14) |

Note: Amended by D-14 to 4 classes for v1 (dropping leaf_smut). Class list is locked to Hasan et al. dataset (D-15). Confirm each folder has at least 100 images before training. Advisory text must be reviewed by an agricultural expert before release (see Section 15). Low-confidence behavior follows D-11: if top confidence < 60%, hide the advisory section and show no treatment advice.


---

## 7. Data Specification

### 7.1 Sources
- Public: Kaggle and Mendeley Data rice leaf disease datasets. Record the exact dataset name, URL, version, and license for each one. (UNVERIFIED until checked.)
- Field: Images collected by the developer in Bangladeshi rice fields, with farmer consent. Stored separately from public data.

### 7.2 Folder Structure
```
data/
  raw/
    public/<dataset_name>/...
    field/<collection_date>_<location>/<class>/...
  processed/
    train/<class>/...
    val/<class>/...
    test_public/<class>/...
    test_field/<class>/...
  metadata/
    dataset_card.md
    field_log.csv        (image_id, date, location, camera, lighting, consent_ref, expert_label)
    licenses.md
```

### 7.3 Splitting Rules (mandatory)
- Split by source or field session, never randomly across images from the same leaf or plot.
- Target split for public data: 70% train, 15% validation, 15% test.
- Field photos are never used for training in the main experiment. They form test_field only. A separate experiment may use part of them for fine-tuning, reported as a separate result.
- Run a duplicate check (perceptual hash) before splitting. Remove near-duplicates.

### 7.4 Labeling
- Every field image must have an expert-confirmed label. Record the expert's name or role and the date in field_log.csv.
- Images with uncertain labels go to a "review" folder and are excluded from training.

### 7.5 Consent and Ethics
- Get verbal or written consent from each farmer before photographing their field. Record the consent_ref ID.
- Do not photograph people's faces. Crop or discard any image that includes faces.
- Store no personal data (names, phone numbers) in the dataset.

---

## 8. ML Pipeline Specification

### 8.1 Preprocessing Contract (must match training and app)
- Color: RGB
- Resize: 224 × 224, bilinear
- Normalization: tf.keras.applications.mobilenet_v2.preprocess_input (scales to [-1, 1])
- Output: softmax over 5 classes
- This contract is saved as `preprocess_config.json` and copied into the Flutter app assets.

### 8.2 Augmentation (training only)
- Random rotation ±30°, horizontal and vertical flip, zoom 0.8–1.2
- Brightness and contrast jitter ±20%
- Random crop, simulated shadow (optional)
- No augmentation on validation or test data.

### 8.3 Model Training
- Base: MobileNetV2, ImageNet weights, alpha 1.0
- Stage 1: Freeze base, train head (Dense 128, ReLU, Dropout 0.3, Dense 4, softmax). Adam lr 1e-3, up to 20 epochs.
- Stage 2: Unfreeze last 30 layers, Adam lr 1e-5, up to 30 epochs.
- Callbacks: EarlyStopping (patience 5, monitor val_loss), ReduceLROnPlateau, ModelCheckpoint.
- Class imbalance: class weights computed from training set.
- Seed: 42 everywhere.

### 8.4 Baselines (must be reported)
- B0: Majority class predictor.
- B1: Small CNN trained from scratch (3 conv blocks).
- B2: MobileNetV2 frozen base only (Stage 1 only).
- M1: Full fine-tuned MobileNetV2 (the main model).
- Optional comparison: EfficientNet-B0 with the same protocol.

### 8.5 Evaluation Metrics
- Primary: Macro F1 on test_public.
- Secondary: Accuracy, per-class precision and recall, confusion matrix, Cohen's kappa.
- Field: Same metrics on test_field, reported separately, with the public-to-field gap.
- Efficiency: Model size (MB), inference time on the target phone (ms), and peak RAM.
- Statistical: Repeat main experiment 3 times with different seeds, report mean and standard deviation.

### 8.6 Explainability
- Grad-CAM on the last conv layer for every test_field misclassification.
- Manual check of 30 random heatmaps: does the highlight fall on the lesion? Record the result.

### 8.7 Failure Analysis
- Collect all wrong predictions on test_field.
- Group by cause: blur, low light, early symptoms, look-alike classes, background clutter.
- Report counts and examples per group.

### 8.8 Export
- Save Keras model as `model.keras`.
- Convert to TFLite: float16 first; try int8 with a representative dataset from train.
- Re-run test_public and test_field on the TFLite model. Report accuracy drop from Keras to TFLite.
- Output files: `model_fp16.tflite` (or int8), `labels.json`, `preprocess_config.json`.

### 8.9 Acceptance Criteria for the Model
- Macro F1 on test_public >= 0.80.
- TFLite accuracy drop vs Keras <= 2 percentage points.
- Model file <= 5 MB.
- All results reproducible from one command (see Section 12).

---

## 9. Mobile App Specification (Flutter)

### 9.1 Screens
1. Splash: app name, version.
2. Onboarding (first launch only): disclaimer and language choice.
3. Home: two large buttons (Take Photo, Choose from Gallery), language toggle, History button.
4. Result: image preview, disease name, confidence %, advisory note (hidden if top confidence < 60%; see D-11), Share (C), Feedback (C). (Note: heatmaps out of scope for v1 per D-10).
5. History: list of past scans with thumbnails and dates.
6. About: credits, dataset licenses, disclaimer, version.

### 9.2 Core Flow
1. User picks image.
2. App decodes, resizes to 224 × 224, applies preprocessing from preprocess_config.json.
3. Run TFLite interpreter (in an isolate, so the UI does not freeze).
4. Get softmax, take top class and confidence.
5. If top confidence < 60%, show "Uncertain" banner with confidence score and "Please consult an agricultural expert." Top class name may appear in banner as a weak guess, but hide advisory section and show no treatment advice (D-11).
6. If top confidence >= 60%, load advisory from local JSON in the selected language.
7. Save to history (S).

### 9.3 Packages (pin versions in pubspec.yaml)
- flutter_riverpod (state management; D-08)
- tflite_flutter (inference)
- image_picker (camera and gallery)
- image (decode and resize)
- path_provider and sqflite (history; D-09)
- shared_preferences (language, onboarding flag)
- flutter_localizations and intl (Bangla strings)
- Bangla font: Noto Sans Bengali (SIL Open Font License)

### 9.4 Non-Functional Requirements
- Fully offline for core features.
- Inference under 1 s on a 2–3 GB RAM device (measured, not assumed).
- App size under 30 MB including model.
- No crashes on images up to 10 MB.
- Minimum Android version: Android 8.0 (API 26).
- Accessibility: minimum touch target 48 dp, text scalable, high contrast.

### 9.5 Permissions
- Camera (only when user taps Take Photo).
- Storage or photo picker (only when user taps Choose from Gallery).
- No location, contacts, or network permissions in v1.

---

## 10. Architecture

```
[Python: training]                      [Flutter app: deployment]
data -> preprocess -> train -> eval     assets/model_fp16.tflite
                    -> export tflite ->  assets/labels.json
                                        assets/advisory_bn.json
                                        assets/advisory_en.json
                                        UI -> isolate -> tflite -> result
```

Layers in the app: UI (screens), state (Riverpod; D-08), services (inference, storage), data (assets and local DB).

---

## 11. Tech Stack

| Area | Tool | Version |
|---|---|---|
| Language (ML) | Python | 3.10+ |
| Deep learning | TensorFlow / Keras | pinned in requirements.txt |
| Data | NumPy, pandas, Pillow, OpenCV | pinned |
| Plots | Matplotlib, Seaborn | pinned |
| Explainability | tf-keras-vis or manual Grad-CAM | pinned |
| Experiment tracking | CSV logs + TensorBoard | free |
| Dashboard (optional) | Streamlit | pinned |
| Mobile | Flutter (stable channel), Dart | pinned in pubspec.yaml |
| Inference | tflite_flutter | pinned |
| Version control | Git, GitHub | free |
| Notebooks | Jupyter or Google Colab | free tier |

---

## 12. Repository Structure

```
rice-leaf-disease/
  README.md
  LICENSE                     (MIT or Apache 2.0, chosen in D-01)
  PROJECT_SCOPE.md
  TRACKING.md
  requirements.txt
  configs/
    train_config.yaml         (all hyperparameters)
  data/                       (not committed; see README for download)
  notebooks/
    01_explore.ipynb
    02_baselines.ipynb
    03_train_mobilenet.ipynb
    04_evaluate.ipynb
    05_export_tflite.ipynb
  src/
    data/ (split.py, dedupe.py, dataset.py)
    models/ (build.py, train.py)
    eval/ (metrics.py, gradcam.py, failure_analysis.py)
    export/ (to_tflite.py)
  scripts/
    reproduce_all.py          (entry point: python -m scripts.reproduce_all; D-13)
  results/
    metrics/  figures/  failure_cases/
  app/                        (Flutter project)
    assets/ lib/ test/
  docs/
    dataset_card.md  ethics.md  limitations.md  play_store/
```

---

## 13. Milestones and Tasks

Each task has an ID. Use these IDs in TRACKING.md and commit messages.

### M0: Setup (Days 1–3)
- T-001: Create GitHub repo with the structure above.
- T-002: Create Python env, requirements.txt, and verify TensorFlow runs (CPU or Colab GPU).
- T-003: Create Flutter project, verify it builds for Android.
- T-004: Choose license and write LICENSE file (D-01).
- T-005: Write dataset card draft in docs/dataset_card.md.

### M1: Data (Weeks 1–2)
- T-010: Download public datasets, record source and license in licenses.md.
- T-011: Build field photo collection plan (sites, dates, consent form, photo protocol).
- T-012: Collect field photos (target 300–500, all 5 classes where present).
- T-013: Get expert labels for field photos; fill field_log.csv.
- T-014: Dedupe public data with perceptual hashing.
- T-015: Create train/val/test splits (Section 7.3) and save split manifests.

### M2: Baselines (Week 3)
- T-020: Class distribution report and sample grid.
- T-021: B0 majority baseline metrics.
- T-022: B1 small CNN from scratch.
- T-023: B2 frozen MobileNetV2 (Stage 1).
- T-024: Log results in results/metrics/baselines.csv.

### M3: Main Model (Week 4)
- T-030: Stage 1 and Stage 2 training of M1 with train_config.yaml.
- T-031: Augmentation pipeline with visual check.
- T-032: Evaluate on test_public (macro F1 target >= 0.80).
- T-033: Three-seed repeat, mean and std.
- T-034: Optional EfficientNet-B0 comparison.

### M4: Evaluation and Explainability (Week 5)
- T-040: Evaluate on test_field; compute gap vs test_public.
- T-041: Grad-CAM on all test_field errors; manual lesion check on 30 samples.
- T-042: Failure analysis grouping and report.
- T-043: Confusion matrices and per-class tables for report.

### M5: Export (Week 5–6)
- T-050: Export float16 TFLite.
- T-051: Try int8 quantization with representative data.
- T-052: Re-evaluate TFLite on both test sets; record accuracy drop.
- T-053: Write labels.json and preprocess_config.json.
- T-054: Verify parity: Python TFLite output vs Flutter output on 20 test images (must match top-1).

### M6: Flutter App (Weeks 6–8)
- T-060: App skeleton: routes, theme, localization setup.
- T-061: Bangla font and strings (ARB files).
- T-062: Image picker and preprocessing service.
- T-063: TFLite inference service in an isolate.
- T-064: Result screen with confidence and uncertain state (F-05).
- T-065: Advisory JSON loader (Bangla and English).
- T-066: Onboarding and disclaimer (F-08).
- T-067: History with local DB (F-09).
- [T-068 removed]: On-device Grad-CAM/heatmap view is out of scope for v1 (D-10); Grad-CAM runs in Python evaluation only (T-041).
- T-069: About screen with credits and licenses (F-14).
- T-070: Unit tests for preprocessing and label mapping.
- T-071: Widget test for result screen.
- T-072: Performance test on low-end device; record latency, RAM, app size.

### M7: Release (Weeks 8–9)
- T-080: Google Play developer account and identity verification.
- T-081: Privacy policy page (GitHub Pages or similar).
- T-082: Data Safety form answers (no data collected or shared in v1; confirm in console).
- T-083: Store listing: icon, screenshots, short and full description (English and Bangla).
- T-084: Upload to internal or closed testing track; confirm current Play requirements in console.
- T-085: Collect tester feedback; fix critical issues.
- T-086: Production release (after Play requirements are met).

### M8: Documentation and Report (Weeks 9–10)
- T-090: README with setup, data download, reproduce command, results, limitations.
- T-091: docs/limitations.md and docs/ethics.md.
- T-092: Final report (see Section 14).
- T-093: Demo video (3 minutes, screen recording of the app on a phone).
- T-094: Presentation slides and live demo rehearsal.

---

## 14. Report Structure
1. Introduction and problem statement
2. Related work
3. Dataset (public + field) and dataset card
4. Methodology (preprocessing, models, training)
5. Experiments and results (baselines, main model, seeds)
6. Field evaluation and domain gap
7. Explainability and failure analysis
8. Mobile deployment (size, latency, accuracy drop)
9. Limitations and ethical considerations
10. Conclusion and future work

---

## 15. Risks and Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Too few field images | High | Start collecting in Week 1; min 60/class; M2/M3 proceed with public data in parallel (Gate 1a); Gate 1b requires field data before M4 (D-12) |
| Insufficient Leaf Smut data in public archives | High | Mitigated by D-14: Leaf Smut deferred to v2, focusing v1 on 4 classes with >= 100 images each from Hasan et al. (D-15) |
| Public dataset license forbids commercial use / unknown licenses | High | Check in T-010; Candidate 1 (Hasan et al.) verified CC BY 4.0 (D-15); unknown license candidates excluded (D-16) |
| Expert unavailable for labeling | High | Agree on labeling protocol early with Upazila Agriculture Office |
| Data leakage (same field in train and test) | High | Split rules in 7.3; automated check in split.py |
| Model too large for app | Medium | Quantization; MobileNetV2 alpha 0.75 as fallback |
| Low-end phone too slow | Medium | Isolate; reduce input size only if retrained and re-evaluated |
| Bangla rendering issues | Medium | Test on 2 real devices; use embedded font |
| Advisory text is wrong or harmful | High | Expert review before release; visible disclaimer |


---

## 16. Quality Gates
- Gate 1a (end of M1): Public data splits and dataset cards complete, no leakage check passed (D-12).
- Gate 1b (before M4): Field photos collected (target 300–500, min 60/class) and expert-labeled in field_log.csv (D-12).
- Gate 2 (end of M3): Macro F1 >= 0.80 on test_public, or a written analysis of why not.
- Gate 3 (end of M5): TFLite parity check passed, size <= 5 MB.
- Gate 4 (end of M6): All Must features working offline on test device.
- Gate 5 (end of M7): Play Store testing track live, privacy policy published.

---

## 17. Locked Decisions
- D-01: License is MIT (change only via DECISION entry).
- D-02: Android only in v1.
- D-03: Offline-first, no backend.
- D-04: TensorFlow/Keras for training, TFLite for deployment.
- D-05: MobileNetV2 is the main model.
- D-06: Field photos are never used for training in the main experiment.
- D-07: Five classes in Section 6 (Amended to four classes for v1 by D-14).
- D-08: State management is Riverpod.
- D-09: Local storage for scan history is sqflite.
- D-10: On-device Grad-CAM is out of scope for v1. Grad-CAM runs only in the Python evaluation notebook for test_field errors. The app shows no heatmaps in v1. Precomputed demo heatmaps are not allowed.
- D-11: Low-confidence behavior (top confidence < 60%): show an "Uncertain" banner with the confidence score and the text "Please consult an agricultural expert." Hide the advisory section. The top class name may appear in the banner as a weak guess, but no treatment advice is shown for it.
- D-12: Milestones M2 and M3 use public data only and may run in parallel with field collection. Replace Gate 1 with Gate 1a (public splits and dataset cards, end of M1) and Gate 1b (field photos collected and expert-labeled, required before M4).
- D-13: The primary cross-platform entry point is `python -m scripts.reproduce_all`. Do not create a bash script. Add a PowerShell wrapper only if requested.
- D-14: Amend D-07 to four classes for v1 (bacterial_leaf_blight, brown_spot, leaf_blast, healthy). Leaf Smut is deferred to v2 (APPROVED, 2026-11-03). Verified original counts before deduplication: Bacterial Leaf Blight 180, Brown Spot 267, Leaf Blast 305, Healthy 157. Note: Healthy (157) is the smallest class; the 100-image rule must be re-checked after T-014 deduplication.

- D-15: v1 trains and evaluates on the Hasan et al. (CC BY 4.0) dataset only. Sethy et al. and Ramesh & Vydeki are not used in training or test splits for v1. Sethy may be used later as an external cross-check only, and only after a new DECISION (APPROVED, 2026-11-03).
- D-16: Saputra and Anshul M are excluded because their licenses are Unknown (APPROVED, 2026-11-03).
- D-17: Exclude both instances of the cross-class duplicate group_035 (Bacterial_leaf_Blight (33).jpg and Leaf_blast (289).jpg) from v1. Reason: the same image carries two conflicting labels (APPROVED, 2026-11-03).
- D-18: Near-duplicate groups (pHash Hamming distance <= 5, computed across all target classes) are kept in full. They are not deleted. Each group is assigned to one split only, so near-copies cannot leak between train and test (APPROVED, 2026-11-03).
- D-19: For B2 and M1, the model checkpoint and early stopping are selected by validation macro F1 (not val_loss). B1 used val_loss; this difference is documented and B1 is not re-run (APPROVED, 2026-11-03).
- D-20: The canonical model for export is selected by validation macro F1 under D-19. Seed 44 (val macro F1 0.8669) is the canonical model. Seeds 42 and 43 are reported as repeats. Test scores are not used for selection (APPROVED, 2026-11-04).



---

## 18. Definition of Done (per task)
- Code runs and is committed with the task ID in the message.
- Tests pass for the changed module.
- Results are saved in results/ with the seed and config used.
- TRACKING.md is updated.
- Any new assumption is recorded as a DECISION or UNVERIFIED item.