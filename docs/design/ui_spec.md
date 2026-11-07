# UI Specification: Rice Leaf Disease Detection Mobile Application

## 1. Overview and Architectural Scope

This specification defines the visual hierarchy, layout geometry, interactive behavior, color roles, performance contracts, security rules, and accessibility standards for the Android mobile application (`com.m2hsoftdev.ricedisease`).

### Key Architectural Guidelines
- **Shell Structure**: The application uses a bottom navigation shell containing three top-level destinations in strict order: **Scan**, **History**, and **About** (Decision D-23). **Splash** and **Onboarding** sit outside this shell. **Result** is pushed onto the navigation stack from Scan with a back navigation arrow.
- **Wording Discipline**: In strict compliance with project safety rules, the application never uses the words *"diagnosis"* or *"cure"*. Identified conditions are referred to exclusively as *"likely condition"* (when top confidence $\ge 60\%$) or *"possible condition"* (when top confidence $< 60\%$).
- **D-11 Compliance**: In the uncertain state (top confidence $< 60\%$), no treatment advice or field advisory text is rendered.
- **D-29 Compliance**: Dataset credit appears on About, README, dataset card, and store listing only. It does not appear on Scan, Result, History, splash, onboarding, or navigation.
- **Design Tokens**: All elements use semantic Material Design 3 tokens defined in `docs/design/tokens.md`. No raw hex codes are permitted in UI specifications.

---

## 2. Performance, Scalability, and Security Architecture

### 2.1 Performance & Hardware Budget
The application must execute reliably in rural field conditions on low-cost Android hardware:
* **Target Hardware**: Functional and responsive on low-end Android devices with **2 GB to 3 GB RAM** (e.g. Android 8.0+ / API 26+).
* **Zero Animated Backgrounds**: Live views must not employ particle animations, video backgrounds, or continuous raster redraw loops.
* **Camera Preview Optimization**: The live camera feed must run with **no live blur or heavy backdrop-filter effects**. Shaders and visual filters are prohibited on the live preview.
* **Image Downscaling Budget**: No image larger than **1600 px** along its longest edge may be displayed or kept in memory. The camera stream and gallery pickers downsample previews immediately.
* **Lazy History Rendering**: The History screen must implement a lazy-loading list (`ListView.builder`) with cached, downscaled 56×56 dp thumbnails to maintain 60 fps scrolling.
* **Responsive Inference Contract**: Model execution runs in a background isolate (`Isolate.run`). The UI must immediately display an active **Analyzing Progress State**, never freezing the screen or blocking input threads.

### 2.2 Scalability, Breakpoints & Modular Components
The application scales seamlessly across mobile form factors and orientations:
* **Breakpoint Grid**:
  * **Compact (Portrait Phones, width < 600 dp)**: Standard single-column layout (e.g. 412×892 dp). Full-bleed capture preview with bottom control panel.
  * **Medium / Landscape (Phone Landscape, height < 480 dp / width 600–840 dp)**: Horizontal division (e.g. 892×412 dp). Viewfinder occupies the left/center; camera controls (shutter, gallery, help) dock vertically on the right column. Shutter, gallery, and disclaimer remain 100% visible without scrolling.
  * **Expanded (Small Tablets, width $\ge$ 600 dp)**: Centered container capped at 640 dp maximum content width to prevent awkward horizontal stretching.
* **Reusable UI Components**:
  * `PrimaryAppBar`: Top app bar supporting transparent scrim over camera and tonal surface tint on scroll.
  * `PrimaryButton`: 48 dp minimum touch target filled button with consistent ripple.
  * `ConfidenceBar`: Horizontal progress indicator with accessible text percentage.
  * `DisclaimerCard`: Standardized collapsible advisory notice (F-08).
  * `ResultBanner`: Standardized M3 banner (`primaryContainer` for confident, `errorContainer` for uncertain).
* **Flexible Text Wrapping**: Containers and cards must never use hardcoded fixed heights. Multiline localized strings must expand dynamically to support system text scaling up to **200%** without text truncation or clipping.

### 2.3 Security, Privacy & Permissions Policy
* **Zero Network Traffic**: The app makes **zero network calls** and bundles **no third-party tracking, analytics, crash-reporting SDKs, or advertising libraries**. The application is 100% offline.
* **Just-In-Time Permissions**: Camera and Gallery permissions are never requested on startup or during onboarding. They are requested exclusively at the exact moment the user taps the Shutter or Gallery button.
* **App-Private Storage**: Captured field photos are stored solely in isolated app-private sandbox storage (`getApplicationDocumentsDirectory()`). Photos are never exported to public shared galleries without explicit user intent and can be deleted individually or wiped completely via "Clear All" in History.
* **No Telemetry / Data Sharing**: Because zero telemetry is collected or transmitted, no privacy consent screens or data-sharing opt-ins are shown.
* **Information Disclosure Prevention**: The user interface is strictly prohibited from displaying raw file system paths (`/data/user/0/...`), device serials, MAC addresses, IMEI, or internal neural network weight shapes.

---

## 3. Global Navigation & Common App Bars

### 3.1 Consistent Top App Bar
All primary destinations within the application shell share a standardized Material 3 Top App Bar (56 dp height):

| Screen | Title Specification | Leading Affordance | Trailing Action | Surface Tint Behavior |
|---|---|---|---|---|
| **Scan (Home)** | App Name: `"Rice Leaf Disease Detection"` (EN) / `"ধানের পাতার রোগ শনাক্তকরণ"` (BN) | None | Language Toggle icon button (`Icons.translate` / text badge) with 48×48 dp target and tooltip (`"Switch to Bangla"` / `"ইংরেজিতে দেখুন"`) | Transparent over camera preview with gradient scrim (`rgba(0,0,0,0.5)` to transparent); applies `surfaceTint` when scrolled |
| **History** | Title: `"History"` (`"হিস্ট্রি"`) | None | Clear-All icon button (`Icons.delete_sweep_outlined`) visible only when history records exist; opens confirmation dialog | Standard M3 flat surface; applies `surfaceTint` upon vertical scroll |
| **About** | Title: `"About"` (`"সম্পর্কে"`) | Back arrow (`Icons.arrow_back`) only if pushed from a nested route; otherwise none | None (clean and unencumbered) | Standard M3 flat surface; applies `surfaceTint` upon vertical scroll |

* **Visual Variants**: Specified across Light and Dark themes, and English and Bangla localizations.

### 3.2 Bottom NavigationBar
Mounted permanently at the bottom of the screen within the application shell (80 dp height, elevation Level 2 / `surfaceContainer`):
* **Order of Destinations**: Strictly **Scan**, **History**, **About** (Decision D-23).
* **Destination Details**:
  1. **Scan**: Icon `Icons.photo_camera_outlined` (inactive) / `Icons.photo_camera` (active); Label `"Scan"` / `"স্ক্যান"`.
  2. **History**: Icon `Icons.history_outlined` (inactive) / `Icons.history` (active); Label `"History"` / `"হিস্ট্রি"`.
  3. **About**: Icon `Icons.info_outlined` (inactive) / `Icons.info` (active); Label `"About"` / `"সম্পর্কে"`.
* **Selection Indicator**: Active destination displays an M3 pill (`primaryContainer` background with `onPrimaryContainer` icon/text). Inactive destinations use `onSurfaceVariant`.
* **Badges**: **No badges in version 1** (no unread badges, dots, or scan counts on navigation icons).

### 3.3 BottomAppBar Architecture Option (Design Evaluation)
* **Evaluated Option**: Replacing the NavigationBar with a `BottomAppBar` featuring a docked center floating capture button, eliminating the dedicated Scan tab.
* **Trade-off Analysis**: A docked center capture button provides immediate single-tap camera access from any tab, but breaks standard Material 3 navigation patterns, occludes content, and creates floating button collision issues in landscape and tablet views.
* **Decision Status**: **NOT IMPLEMENTED**. Decision D-23 locks the three-tab `NavigationBar` (Scan, History, About). Adopting a BottomAppBar would require a formal new Decision to supersede D-23.

---

## 4. Screen Specifications

### 4.1 Splash Screen (Outside Shell)
Displayed on cold launch while validating local storage and configuration.
* **Layout**: Centered vertical column.
* **Elements**: App Logo (120×120 dp), Headline `"Rice Leaf Disease Detection"` (`appTitle`), Subtitle `"Offline Agricultural Field Tool"`, Indeterminate progress indicator (36×36 dp; static 3-dot fallback under reduce-motion).
* **Navigation**: Automatically routes to Onboarding (first run) or Scan (subsequent launches) after 1.2 s.

### 4.2 Onboarding Screen (Outside Shell)
Shown only on first launch (`onboarding_done = false`) per requirement F-08.
* **Layout**: Scrollable vertical column with pinned bottom action button.
* **Elements**: Top bar with language toggle, Hero illustration (rice field scanner), Advisory Disclaimer card (F-08 notice), Photo capture guidelines card (lighting, focus, framing), and 56 dp primary button `"Get Started"` (`"শুরু করুন"`).

### 4.3 Scan Screen: Full-Screen Capture Page (Inside Shell: Tab 1)
The primary operational interface. Uses a **full-bleed viewport layout** instead of a small card:

```
┌─────────────────────────────────────────────────────────────┐
│ [App Title: Rice Leaf Disease Detection]   [Language Toggle]│ ◄── Top App Bar with gradient scrim
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌───────────────────┐                    │
│                    │ ┌               ┐ │                    │
│                    │   [Viewfinder]    │ │ ◄── Centered viewfinder frame
│                    │ └               ┘ │       with corner brackets
│                    └───────────────────┘                    │
│              [Position diseased rice leaf in center]        │ ◄── Guidance chip
│                                                             │
├─────────────────────────────────────────────────────────────┤
│   [ ⚠️ Advisory notice: Not formal advice. Tap details ]    │ ◄── Compact expandable disclaimer strip
├─────────────────────────────────────────────────────────────┤
│        [Gallery]            (( Shutter ))           [Flash] │ ◄── Bottom control panel
│         (56 dp)                (72 dp)              (56 dp) │     (inside SafeArea, above Nav)
├─────────────────────────────────────────────────────────────┤
│       [  Scan (Active)  |  History  |  About  ]             │ ◄── Fixed M3 NavigationBar
└─────────────────────────────────────────────────────────────┘
```

#### Detailed Element Geometry:
1. **Top Scrim & App Bar**: Semi-transparent top bar (`linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%)`). App title on left in white (`#FFFFFF`) with subtle shadow; 48×48 dp language toggle button on right with localized tooltip.
2. **Camera Preview Area**: Full-bleed camera feed (aspect ratio 4:3 or native sensor filled). Center features a 260×260 dp viewfinder frame with rounded corner-bracket guides (`border: 2px dashed rgba(255,255,255,0.7); border-radius: 16px;`). A semi-transparent guidance chip (`"Position diseased rice leaf in center"` / `"পাতার আক্রান্ত অংশটি ফ্রেমের মাঝে রাখুন"`) floats below the frame.
3. **Compact Disclaimer Strip (F-08)**: Positioned above the control panel:
   * A compact one-line strip: `"⚠️ Advisory notice: Not formal diagnosis or extension advice. Tap for details."` (EN) / `"⚠️ জরুরি সতর্কবার্তা: এটি কোনো চূড়ান্ত সিদ্ধান্ত নয়। বিস্তারিত দেখতে ট্যাপ করুন।"` (BN).
   * Tap expands the full advisory card in a modal bottom sheet without obstructing the shutter.
   * **Rule**: Must never overlap or cover the shutter button.
4. **Bottom Control Panel**:
   * **Gallery Picker Button (Left)**: Circular 56×56 dp touch target (`Icons.photo_library`) with label `"Gallery"` / `"গ্যালারি"` underneath. Placed within immediate reach of left thumb.
   * **Camera Shutter Button (Center)**: **72×72 dp circular shutter** inside an 84×84 dp white tactile ring with an 80×80 dp minimum touch target. Filled with solid white (or `primaryContainer` in dark mode). Label `"Capture"` / `"ছবি তুলুন"` underneath. Accessible label: `"Capture leaf photo"`.
   * **Flash / Help Button (Right)**: Circular 56×56 dp touch target (`Icons.flash_auto` or `Icons.help_outline`) with label `"Flash"` / `"Help"` underneath. Placed within reach of right thumb.
5. **Landscape Viewport Geometry (892×412 dp)**:
   * Viewfinder remains centered in left/middle preview area.
   * Controls dock vertically on the right: Gallery (top), 72 dp Shutter (center), Help (bottom).
   * Disclaimer strip remains visible along the bottom edge of the preview.
   * **Verification**: In both 412×892 portrait and 892×412 landscape viewports, the shutter, gallery button, and disclaimer are **100% visible without scrolling**.

#### Capture Page States:
* **State 1: Capture Idle**: Live preview active, guidance chip visible, 72 dp shutter enabled, gallery button active, disclaimer strip visible.
* **State 2: Camera Permission Denied**: Camera feed darkened; centered M3 dialog with camera-off icon (`Icons.no_photography`), explanation that permission is required to shoot photos, primary button `"Open Settings"`, and prominent note that `"You can still select photos from your gallery"`. The Gallery button remains fully functional and highlighted; shutter button is disabled (`opacity: 0.38`).
* **State 3: Photo Selected**: Captured or gallery photo frozen in viewfinder. Overlay panel presents `"Photo Selected"` title with two clear buttons: `"Analyze Leaf"` (filled primary button, 50 dp) and `"Retake / Change"` (outlined button, 50 dp).
* **State 4: Analyzing**: Inference isolate running. Viewfinder is subtly dimmed; center displays an indeterminate circular progress indicator with title `"Analyzing Rice Leaf..."` (`"পাতা বিশ্লেষণ করা হচ্ছে..."`) and subtitle `"Running on-device neural network (MobileNetV2)..."`. Shutter and controls are disabled (`pointer-events: none`).

---

### 4.4 Result Screen: Confident State ($\ge 60\%$ Confidence)
Pushed from Scan when top prediction confidence is $\ge 60\%$.
* **Layout**: Top app bar with back navigation arrow (`Icons.arrow_back`), scrollable content column.
* **Elements**:
  1. Top App Bar: Title `"Scan Result"` / `"ফলাফল"`.
  2. Photo Preview: Captured leaf photo (200 dp height, 12 dp rounded corners).
  3. Likely Condition Card: `primaryContainer` background; Header `"Likely Condition"` / `"সম্ভাব্য রোগ / লক্ষণ"`; Title: Disease Name (e.g. `"Brown Spot"` / `"বাদামি দাগ রোগ"`); Subtitle in alternate language.
  4. Confidence Bar: Horizontal progress bar indicating exact confidence percentage (e.g. `87.4% (Likely)`).
  5. Field Advisory Card: Agronomic management practices from local verified repository; footnote directing user to consult Upazila Agriculture Office (DAE). (Prohibited words "diagnosis" and "cure" strictly omitted).
  6. Compact Disclaimer Card (F-08): Permanent advisory notice.
  7. Outlined Button: `"Scan Another Leaf"` / `"আরেকটি পাতা পরীক্ষা করুন"`.

---

### 4.5 Result Screen: Uncertain State ($< 60\%$ Confidence, D-11)
Pushed from Scan when top prediction confidence is $< 60\%$.
* **Layout**: Top app bar with back navigation arrow, scrollable content column.
* **Elements**:
  1. Top App Bar: Title `"Scan Result"` / `"ফলাফল"`.
  2. Photo Preview: Captured leaf photo (200 dp height).
  3. Uncertain Warning Banner: `errorContainer` container; Warning icon (`Icons.warning_amber_rounded`); Title `"Uncertain Result"` (`"অনিশ্চিত ফলাফল"`); Body text advising user that confidence is low.
  4. Weak Guess Pill: Top class displayed strictly as an unconfirmed weak guess (e.g. `"Possible condition: Brown Spot (52.0%)"`).
  5. **D-11 Enforcement**: Field advisory / treatment section is **completely absent**. Zero chemical, spray, or cultural treatment advice is shown.
  6. Recommended Next Steps Card: Prominently directs farmer: `"Take this leaf sample to your nearest Upazila Agriculture Office (DAE) for expert evaluation."`
  7. Compact Disclaimer Card (F-08): Permanent advisory notice.
  8. Filled Primary Button: `"Retake Photo in Better Light"` (`"ভালো আলোতে পুনরায় ছবি তুলুন"`).
  9. Outlined Button: `"Back to Scan"` (`"স্ক্যানে ফিরে যান"`).

---

### 4.6 History Screen (Inside Shell: Tab 2)
* **Empty State**: Centered illustration, title `"No past scans yet."`, description explaining offline local storage, and filled button `"Start First Scan"`.
* **Populated List**: Lazy-loading list (`ListView.builder`) of scan cards. Each card displays a 56×56 dp thumbnail, condition name, timestamp, and confidence %. Uncertain scans display a warning indicator. Top app bar features Clear-All action icon with a confirmation modal dialog (`"Clear all past scans?"`).

---

### 4.7 About Screen (Inside Shell: Tab 3)
Contains app identification, licenses, dataset attribution, and official legal notice (complies with Decision D-29):
1. Top App Bar: Title `"About & Credits"` / `"অ্যাপ পরিচিতি ও স্বীকৃতি"`.
2. App Identity Card: App name, Version 1.0.0 (Build 1), Developer credit: `"Academic final-year project by Mehedi Hasan."`
3. Software License Card: `"Released under the MIT License (D-01)."`
4. Dataset Credit Card (Decision D-29):
   * Title: `"Dataset credit"` (EN) / `"ডেটাসেট কৃতিত্ব"` [NEW, to be reviewed by a native speaker before release].
   * Body (EN): `"Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: images were re-oriented according to EXIF data and re-encoded for training."`
   * Body (BN): `"ধানের পাতার ছবি: হাসান, এম. প্রমুখ (২০২৩), মেন্ডেলে ডেটা, DOI 10.17632/hx6f852hw4.2, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) লাইসেন্সের অধীন। পরিবর্তন: EXIF ডেটা অনুযায়ী ছবির ওরিয়েন্টেশন সংশোধন করা হয়েছে এবং প্রশিক্ষণের জন্য পুনরায় এনকোড করা হয়েছে।"` [NEW, translation to be reviewed by a native speaker before release]
   * Behavior: Tappable hyperlink opens CC BY 4.0 license page in browser.
5. Font License Card: Embedded font Noto Sans Bengali licensed under SIL Open Font License, Version 1.1 (OFL-1.1).
6. Advisory Disclaimer Card (F-08): Full legal notice.

---

## 5. State & Transition Matrix

```
       [ Cold Launch ]
              │
              ▼
       [ Splash Screen ] ────────(after 1.2s, onboarding_done=false)────► [ Onboarding Screen ]
              │                                                                     │
              │ (after 1.2s, onboarding_done=true)                                  │ (Tap "Get Started")
              ▼                                                                     ▼
     ┌─────────────────────────────────────────────────────────────────────────────────┐
     │                             APPLICATION SHELL (M3)                              │
     │                                                                                 │
     │   [ BottomNavigationBar: Scan (Active) | History (Inactive) | About (Inactive)] │
     │                                                                                 │
     │   [ Tab 1: Scan Screen (Full-Screen Capture Page) ] ◄──┐                        │
     │         ├─ State A: Idle Viewfinder (72 dp Shutter, Gallery, Disclaimer Strip) │
     │         ├─ State B: Camera Permission Denied (Open Settings, Gallery Active)   │
     │         ├─ State C: Photo Selected (Analyze / Retake)                          │
     │         └─ State D: Analyzing (Progress spinner, Isolate inference)            │
     │                         │                                                       │
     │                         │ (Inference Finished)                                  │
     │                         ▼                                                       │
     │             ┌───────────────────────┐                                           │
     │             ▼                       ▼                                           │
     │     [ Result: Confident ]   [ Result: Uncertain ] (D-11)                        │
     │      - Likely condition      - Warning banner                                   │
     │      - Confidence bar        - Weak guess only (no treatment)                   │
     │      - Field advisory        - Upazila Agriculture Office (DAE)                 │
     │      - Disclaimer card       - Disclaimer card                                  │
     │                                                                                 │
     │   [ Tab 2: History Screen ]                                                     │
     │     - State A: Empty State (0 scans)                                            │
     │     - State B: Populated Lazy List (Thumbnails, timestamps, confidence)         │
     │                                                                                 │
     │   [ Tab 3: About Screen ]                                                       │
     │     - Version & Author                                                          │
     │     - MIT Software License                                                      │
     │     - Dataset Credit (Hasan, M. et al., DOI, CC BY 4.0, Changes) (D-29)         │
     │     - Font License (Noto Sans Bengali OFL 1.1)                                  │
     │     - Advisory Disclaimer (F-08)                                                │
     └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Mockups & Wireframes Inventory (Count Reconciliation)

The proposed design includes **standalone Material 3 HTML wireframes** in `docs/design/mockups/` and **rendered PNG screenshots** in `docs/screenshots/design_proposal/`:

| # | Screen / Feature | State & Theme / Locale | Viewport (dp) | HTML Wireframe (`docs/design/mockups/`) | Rendered PNG (`docs/screenshots/design_proposal/`) |
|---|---|---|---|---|---|
| 1 | Splash Screen | Light | 412×892 | `splash_light.html` | `splash_light.png` |
| 2 | Splash Screen | Dark | 412×892 | `splash_dark.html` | `splash_dark.png` |
| 3 | Onboarding Screen | Light (EN/BN toggleable) | 412×892 | `onboarding_light.html` | `onboarding_light.png` |
| 4 | Onboarding Screen | Dark (EN/BN toggleable) | 412×892 | `onboarding_dark.html` | `onboarding_dark.png` |
| 5 | Capture Page: Idle | Light, English | 412×892 | `scan_idle_light_en.html` | `scan_idle_light_en.png` |
| 6 | Capture Page: Idle | Dark, English | 412×892 | `scan_idle_dark_en.html` | `scan_idle_dark_en.png` |
| 7 | Capture Page: Idle | Light, Bangla | 412×892 | `scan_idle_light_bn.html` | `scan_idle_light_bn.png` |
| 8 | Capture Page: Idle | Dark, Bangla | 412×892 | `scan_idle_dark_bn.html` | `scan_idle_dark_bn.png` |
| 9 | Capture Page: Landscape | Light (English) | 892×412 | `scan_landscape_light.html` | `scan_landscape_light.png` |
| 10 | Capture Page: Landscape | Dark (English) | 892×412 | `scan_landscape_dark.html` | `scan_landscape_dark.png` |
| 11 | Capture: Permission Denied | Light | 412×892 | `scan_permission_light.html` | `scan_permission_light.png` |
| 12 | Capture: Permission Denied | Dark | 412×892 | `scan_permission_dark.html` | `scan_permission_dark.png` |
| 13 | Capture: Photo Selected | Light | 412×892 | `scan_selected_light.html` | `scan_selected_light.png` |
| 14 | Capture: Photo Selected | Dark | 412×892 | `scan_selected_dark.html` | `scan_selected_dark.png` |
| 15 | Capture: Analyzing State | Light | 412×892 | `scan_analyzing_light.html` | `scan_analyzing_light.png` |
| 16 | Capture: Analyzing State | Dark | 412×892 | `scan_analyzing_dark.html` | `scan_analyzing_dark.png` |
| 17 | Result: Confident ($\ge 60\%$) | Light, English | 412×892 | `result_confident_light_en.html` | `result_confident_light_en.png` |
| 18 | Result: Confident ($\ge 60\%$) | Dark, English | 412×892 | `result_confident_dark_en.html` | `result_confident_dark_en.png` |
| 19 | Result: Confident ($\ge 60\%$) | Light, Bangla | 412×892 | `result_confident_light_bn.html` | `result_confident_light_bn.png` |
| 20 | Result: Confident ($\ge 60\%$) | Dark, Bangla | 412×892 | `result_confident_dark_bn.html` | `result_confident_dark_bn.png` |
| 21 | Result: Uncertain ($< 60\%$) | Light, English | 412×892 | `result_uncertain_light_en.html` | `result_uncertain_light_en.png` |
| 22 | Result: Uncertain ($< 60\%$) | Dark, English | 412×892 | `result_uncertain_dark_en.html` | `result_uncertain_dark_en.png` |
| 23 | Result: Uncertain ($< 60\%$) | Light, Bangla | 412×892 | `result_uncertain_light_bn.html` | `result_uncertain_light_bn.png` |
| 24 | Result: Uncertain ($< 60\%$) | Dark, Bangla | 412×892 | `result_uncertain_dark_bn.html` | `result_uncertain_dark_bn.png` |
| 25 | History: Empty State | Light | 412×892 | `history_empty_light.html` | `history_empty_light.png` |
| 26 | History: Empty State | Dark | 412×892 | `history_empty_dark.html` | `history_empty_dark.png` |
| 27 | History: Populated List | Light | 412×892 | `history_list_light.html` | `history_list_light.png` |
| 28 | History: Populated List | Dark | 412×892 | `history_list_dark.html` | `history_list_dark.png` |
| 29 | About Screen | Light | 412×892 | `about_light.html` | `about_light.png` |
| 30 | About Screen | Dark | 412×892 | `about_dark.html` | `about_dark.png` |

* **Total Screenshots Directory Size**: Under 2.0 MB budget.
* **Ergonomics & Viewport Guarantee**: In both portrait (412×892 dp) and landscape (892×412 dp), the 72 dp shutter button, 56 dp gallery button, and compact disclaimer are completely visible without scrolling.
