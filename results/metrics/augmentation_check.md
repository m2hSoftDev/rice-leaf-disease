# T-031: Augmentation Pipeline Visual Inspection Report

## Pipeline Contract Verification
- **Augmentation Components (Section 8.2)**:
  - Random Rotation: $\pm 30^\circ$ (`tf.keras.layers.RandomRotation(30.0 / 360.0)`)
  - Random Flip: Horizontal and Vertical (`tf.keras.layers.RandomFlip("horizontal_and_vertical")`)
  - Random Zoom: $0.8$ to $1.2$ (`tf.keras.layers.RandomZoom((-0.2, 0.2))`)
  - Random Brightness: $\pm 20\%$ (`tf.keras.layers.RandomBrightness(0.2, value_range=(0.0, 255.0))`)
  - Random Contrast: $\pm 20\%$ (`tf.keras.layers.RandomContrast(0.2)`)
- **Execution Scope**:
  - Training Set: Augmentation is executed strictly in-memory during batch generation (`is_train=True`).
  - Validation Set: ZERO augmentation applied (`is_train=False`). Images pass only resizing and `mobilenet_v2.preprocess_input`.
  - Test Set: ZERO augmentation applied (`is_train=False`). Images pass only resizing and `mobilenet_v2.preprocess_input`.
- **Storage Verification**:
  - No augmented image files are written into dataset folders or git-tracked paths.
  - Verification figures are saved strictly to `results/figures/augmentation_check/` which is ignored by `.gitignore` (`results/figures/*`).

## Visual Inspection Findings

### 1. Brown Spot vs Leaf Blast Morphology Check
- **Brown Spot Observations**:
  - Lesions remain characteristically circular to oval-shaped with dark reddish-brown margins.
  - Zoom range (0.8x to 1.2x) magnifies or demagnifies individual spots without morphing their circular curvature into elongate blast spindles.
  - Rotation ($\pm 30^\circ$) alters the leaf angle naturally without distorting spot geometry.
  - Contrast and brightness jitter ($\pm 20\%$) simulate realistic variations in midday sunlight and cloud shadow without altering the distinctive darker necrotic halo around the lesions.
  - **Conclusion**: None of the 8 sampled Brown Spot augmentations alter the apparent disease into Leaf Blast.

### 2. Leaf Blast Observations
- **Morphology**:
  - Lesions maintain their acute, diamond/spindle-shaped contours oriented along the longitudinal leaf veins, with distinct grey centers.
  - Horizontal/vertical flipping preserves the axial geometry relative to the leaf blade.
  - Zoom-in retains the tapered ends characteristic of *Magnaporthe oryzae* lesions.
  - **Conclusion**: The spindle shape remains distinct from the circular lesions of Brown Spot across all 8 examined samples.

### 3. Bacterial Leaf Blight Observations
- **Morphology**:
  - Wavy, longitudinal marginal striping (yellow to grey-white necrosis running down the leaf edge) remains unambiguously recognizable under rotation, flip, and zoom.

### 4. Healthy Rice Leaf Observations
- **Morphology**:
  - Clean, unblemished green leaves remain healthy; contrast and brightness jitter do not create spurious spot artifacts or faux lesions.

## Summary Conclusion
The Section 8.2 augmentation pipeline realistically simulates field variability (camera angles, orientation, sunlight intensity, sensor distance) while rigorously preserving the diagnostic morphological boundaries between all classes.
