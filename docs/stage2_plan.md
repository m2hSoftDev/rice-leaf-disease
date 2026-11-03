# Stage 2 Fine-Tuning Plan (T-030: Main Model M1)

This plan specifies the execution protocol for **T-030: Stage 2 Fine-Tuning of MobileNetV2 (Main Model M1)**, following the project contract defined in `PROJECT_SCOPE.md` (Section 8.3, Section 16) and locked decision `D-19`.

---

## 1. Starting Model & Weight Initialization
- **Base Checkpoint**: The initial weights for Stage 2 fine-tuning will be loaded strictly from `results/checkpoints/b2_best.keras`.
- **Validation Selection Lineage**: This checkpoint was selected from epoch 4 of Baseline B2 training based on the highest validation macro F1 (`0.7670`), adhering strictly to decision **D-19**.
- **Head Architecture**: Retains the 4-class classification head configured under D-14 and Section 8.3:
  - `Dense(128, activation='relu')`
  - `Dropout(0.3, seed=42)`
  - `Dense(4, activation='softmax')`

---

## 2. Unfreezing Depth and Optimization
- **Backbone**: MobileNetV2 (154 layers total).
- **Unfreezing Policy**:
  - The first 124 layers of MobileNetV2 remain frozen (`trainable = False`) to preserve robust, low-level feature representations (edges, corners, general textures).
  - The **last 30 layers** of MobileNetV2 are unfrozen (`layer.trainable = True`), per Section 8.3 specification.
  - `BatchNormalization` layers inside the backbone remain in inference mode (`training=False`) during forward passes to prevent unstable batch statistic updates from small batches.
- **Optimizer & Learning Rate**:
  - Optimizer: `tf.keras.optimizers.Adam(learning_rate=1e-5)`
  - A reduced learning rate of $1 \times 10^{-5}$ prevents catastrophic forgetting of pretrained weights while fine-tuning high-level features for rice leaf disease symptoms.
- **Loss Function**: `sparse_categorical_crossentropy` with balanced class weights computed from the training split.

---

## 3. Training Duration & Stopping Criteria (D-19)
- **Maximum Epochs**: Up to 30 epochs (Section 8.3).
- **Metric for Checkpoint & Early Stopping**: Monitored strictly on **Validation Macro F1** (`val_macro_f1`), per locked decision **D-19**.
- **Patience**: 5 epochs without improvement in `val_macro_f1`.
- **Checkpoint Destination**: `results/checkpoints/m1_best.keras` (git-ignored).
- **Restoration**: The best weights according to validation macro F1 will be restored prior to evaluation.

---

## 4. Dataset, Augmentation, and Preprocessing Contract
- **Data Source**: `data/metadata/split_manifest.csv` only (4 classes, 907 active images).
  - Training set: 634 images (balanced class weights applied).
  - Validation set: 135 images.
  - Held-out test set: 138 images.
- **Exclusions**: Conflicting cross-class duplicate `group_035` and augmented staging images remain strictly excluded.
- **Preprocessing Contract (Section 8.1)**: RGB, 224x224 bilinear resize, normalized via `tf.keras.applications.mobilenet_v2.preprocess_input` (values scaled to $[-1, 1]$).
- **Augmentation Pipeline (Section 8.2)**: Applied to the training split only:
  - Random rotation $\pm 30^\circ$
  - Random horizontal and vertical flip
  - Random zoom $0.8$ to $1.2$
  - Random brightness and contrast jitter $\pm 20\%$
  - No augmentation on validation or test splits.
- **Reproducibility**: Random seed 42 fixed across Python, NumPy, and TensorFlow.

---

## 5. Quality Gate 2 Protocol (Test Macro F1 >= 0.80)
- **Strict Blind Evaluation**: The held-out test split (`test_public`, $N=138$) will be evaluated exactly **once**, after Stage 2 fine-tuning completes and the best validation checkpoint has been restored. The test split is never referenced during training or stopping decisions.
- **Success Criteria**: If Test Macro F1 $\ge 0.80$, Quality Gate 2 is formally satisfied.
- **Contingency / Reporting Protocol**: If Test Macro F1 $< 0.80$:
  - The result will be reported honestly and transparently as **not met**, documenting the exact per-class confusion and gap.
  - **No post-hoc hyperparameter tuning** will be conducted against the test set (preventing test set leakage and overfitting).
  - The analysis will be submitted to the final report as an honest empirical finding per Section 16 and Definition of Done.
