# UI Specification: Rice Leaf Disease Detection Mobile Application

## 1. Overview and Architectural Scope

This specification defines the visual hierarchy, layout geometry, interactive behavior, color roles, and accessibility contracts for the Android mobile application (`com.m2hsoftdev.ricedisease`).

### Key Architectural Guidelines
- **Shell Structure**: The application uses a bottom navigation shell containing three top-level destinations: **Scan**, **History**, and **About**. **Splash** and **Onboarding** sit outside this shell. **Result** is pushed onto the navigation stack from Scan with a back navigation arrow.
- **Wording Discipline**: In strict compliance with project safety rules, the application never uses the words *"diagnosis"* or *"cure"*. Identified conditions are referred to exclusively as *"likely condition"* (when top confidence $\ge 60\%$) or *"possible condition"* (when top confidence $< 60\%$).
- **D-11 Compliance**: In the uncertain state (top confidence $< 60\%$), no treatment advice or field advisory text is rendered.
- **Color Roles**: Elements are specified using Material Design 3 semantic color roles (`primary`, `onPrimary`, `surface`, `surfaceVariant`, `onSurface`, `errorContainer`, `onErrorContainer`, `outline`, etc.), not hardcoded hex values.
- **Accessibility & Motion**: Minimum touch targets are 48×48 dp. All typography supports dynamic OS font scaling. When system reduce-motion is enabled, transitions and animated progress indicators snap to static states.

---

## 2. Global Components

### 2.1 Bottom NavigationBar
Mounted permanently at the bottom of the screen within the application shell.

- **Region & Geometry**: Bottom of screen; full width (412 dp), height 80 dp.
- **Element Type**: Material 3 NavigationBar (`nav item` container with pill selection indicators).
- **Z-Index**: Elevated over page content (`elevation: 3 dp`).

#### Navigation Items (Left to Right):
1. **Scan Nav Item**:
   - **Type**: `nav item`
   - **Icon**: `Icons.camera_alt_outlined` (inactive), `Icons.camera_alt` (active)
   - **Label English**: `"Scan"` [NEW]
   - **Label Bangla**: `"স্ক্যান"` [NEW]
   - **Color Role**: Active indicator: `primaryContainer`; Active icon/label: `onPrimaryContainer`; Inactive: `onSurfaceVariant`.
   - **Behavior**: Tapping switches active shell tab to Scan screen. Tab transition: 200 ms cross-fade (instant snap if reduce-motion is on).
2. **History Nav Item**:
   - **Type**: `nav item`
   - **Icon**: `Icons.history_outlined` (inactive), `Icons.history` (active)
   - **Label English**: `"History"` (`historyTitle` / [NEW])
   - **Label Bangla**: `"হিস্ট্রি"` (`historyTitle` / [NEW])
   - **Color Role**: Active indicator: `primaryContainer`; Active icon/label: `onPrimaryContainer`; Inactive: `onSurfaceVariant`.
   - **Behavior**: Tapping switches active shell tab to History screen.
3. **About Nav Item**:
   - **Type**: `nav item`
   - **Icon**: `Icons.info_outline` (inactive), `Icons.info` (active)
   - **Label English**: `"About"` (`aboutTitle` / [NEW])
   - **Label Bangla**: `"সম্পর্কে"` (`aboutTitle` / [NEW])
   - **Color Role**: Active indicator: `primaryContainer`; Active icon/label: `onPrimaryContainer`; Inactive: `onSurfaceVariant`.
   - **Behavior**: Tapping switches active shell tab to About screen.

---

## 3. Screen Specifications

### 3.1 Splash Screen (Outside Shell)
Displayed on cold start while initial preferences and assets are verified.

- **Layout Structure**: Centered single column, vertical layout.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top / Center | `image` (App Logo) | 120×120 dp | None (Semantic icon of rice stalk / leaf) | `primary` | Static vector logo. VoiceOver/TalkBack label: "Rice Leaf Disease Detection Logo". |
| 2 | Center | `text` (Title) | Full width, ~32 dp height | `"Rice Leaf Disease Detection"` (`appTitle`) / `"ধানের পাতার রোগ শনাক্তকরণ"` (`appTitle`) | `onSurface` | `headlineMedium`, bold (700). |
| 3 | Center | `text` (Subtitle) | Full width, ~24 dp height | `"Offline Agricultural Field Tool"` [NEW] / `"অফলাইন কৃষি সহায়ক টুল"` [NEW] | `onSurfaceVariant` | `bodyMedium`. |
| 4 | Bottom (80 dp above edge) | `bar` (Progress Indicator) | 36×36 dp | None | `primary` | Indeterminate circular progress indicator. If reduce-motion is on, renders static 3-dot graphic. Automatically redirects after 1.2 s to Onboarding (first launch) or Scan (subsequent). |

---

### 3.2 Onboarding Screen (Outside Shell)
Shown only on first launch (`onboarding_done = false`) per requirement F-08 and Section 9.1.

- **Layout Structure**: Vertical scrollable column with pinned bottom action bar.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Welcome"` [NEW] / `"স্বাগতম"` [NEW] | `surface` (bg), `onSurface` (text) | Displays app title. Trailing: Language toggle button. |
| 2 | Top right in App Bar | `button` (TextButton) | ~110×40 dp | `"বাংলায় দেখুন"` (`switchToBangla`) / `"View in English"` (`switchToEnglish`) | `primary` | Tapping toggles app locale immediately without restart. |
| 3 | Upper Body | `image` (Hero Graphic) | Full width, 180 dp height | Vector illustration of rice field and phone scanner | `surfaceVariant` (bg), `primary` (accent) | Decorative visual header. |
| 4 | Middle Body | `card` (Advisory Disclaimer) | Full width, ~160 dp height | Header: `"Advisory Notice"` (`disclaimerTitle`) / `"জরুরি সতর্কবার্তা"` (`disclaimerTitle`). Body: `"This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action."` (`disclaimerText`) / `app_bn.arb` | Card: `surfaceVariant`; Header: `onSurfaceVariant` (bold); Body: `onSurfaceVariant` | High-contrast notice card. TalkBack reads notice in full. |
| 5 | Lower Body | `card` (Usage Guide) | Full width, ~120 dp height | Header: `"Photo Guidelines"` [NEW] / `"ছবি তোলার নিয়মাবলী"` [NEW]. Bullet 1: `"Take photo in good natural daylight"` [NEW] / `"দিনের আলোতে পরিষ্কার ছবি তুলুন"` [NEW]. Bullet 2: `"Focus clearly on diseased leaf area"` [NEW] / `"আক্রান্ত অংশের দিকে ক্যামেরা ফোকাস করুন"` [NEW]. | `surfaceVariant` | Instructional card ensuring quality input. |
| 6 | Bottom Pinned | `button` (FilledButton) | Full width, 56 dp height | `"Get Started"` (`getStarted`) / `"শুরু করুন"` (`getStarted`) | `primary` (bg), `onPrimary` (text) | Sets `onboarding_done = true` in `SharedPreferences` and navigates to Scan screen. 48 dp minimum touch target. |

---

### 3.3 Scan Screen (Inside Shell: Tab 1)
The primary operational screen allowing farmers and extension officers to capture or select a rice leaf photo.

- **Layout Structure**: Top App Bar, scrollable body with viewfinder placeholder / photo action buttons, and pinned advisory notice.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Rice Leaf Disease Detection"` (`appTitle`) / `"ধানের পাতার রোগ শনাক্তকরণ"` (`appTitle`) | `surface` (bg), `onSurface` (text) | Top app bar. Trailing action: Language toggle button. |
| 2 | Top right in App Bar | `button` (TextButton) | ~110×40 dp | `"বাংলায় দেখুন"` (`switchToBangla`) / `"View in English"` (`switchToEnglish`) | `primary` | Tapping toggles locale between English and Bangla. |
| 3 | Upper Body | `card` (Viewfinder / Guide) | Full width, 240 dp height | Center Icon: `Icons.filter_center_focus`; Text: `"Position diseased rice leaf in center"` [NEW] / `"পাতার আক্রান্ত অংশটি ফ্রেমের মাঝে রাখুন"` [NEW] | `surfaceVariant` (container), `onSurfaceVariant` (icon/text) | Viewfinder boundary guide with dashed corner borders. |
| 4 | Middle Body | `button` (FilledButton.icon) | Full width, 54 dp height | Icon: `Icons.camera_alt`; Label: `"Take Photo"` (`takePhoto`) / `"ছবি তুলুন"` (`takePhoto`) | `primary` (bg), `onPrimary` (text) | Opens device camera (F-01). Triggers inference isolate upon capture. |
| 5 | Middle Body | `button` (OutlinedButton.icon) | Full width, 54 dp height | Icon: `Icons.photo_library`; Label: `"Choose from Gallery"` (`chooseGallery`) / `"গ্যালারি থেকে বাছাই করুন"` (`chooseGallery`) | `outline` (border), `primary` (text/icon) | Opens photo picker for JPG/PNG up to 10 MB (F-02). |
| 6 | Lower Body | `card` (Advisory Banner) | Full width, ~100 dp height | Header: `"Advisory Notice"` (`disclaimerTitle`) / `"জরুরি সতর্কবার্তা"`. Text: `"This tool provides advisory identification only. Consult an agricultural expert."` [NEW] / `"এই অ্যাপটি কেবল পরামর্শমূলক। ব্যবস্থা নেওয়ার আগে কৃষি কর্মকর্তার পরামর্শ নিন।"` [NEW] | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Permanent visible disclaimer on scan screen per requirement F-08. |

---

### 3.4 Result Screen: Confident State ($\ge 60\%$ Confidence)
Rendered when model top prediction has confidence $\ge 60\%$. Displays condition name, confidence %, field advisory note, and compact disclaimer card.

- **Layout Structure**: Top App Bar with back arrow, vertical scrollable content.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Scan Result"` [NEW] / `"ফলাফল"` [NEW]. Leading: Back icon (`Icons.arrow_back`). | `surface` (bg), `onSurface` (text) | Back arrow pops back to Scan screen. |
| 2 | Upper Body | `image` (Captured Photo Preview) | Full width, 200 dp height | Thumbnail of analyzed leaf photo | `surfaceVariant` (border) | Displays image preview with subtle rounded corners (12 dp). |
| 3 | Middle Body | `card` (Likely Condition Card) | Full width, ~140 dp height | Header: `"Likely Condition"` [NEW] / `"সম্ভাব্য রোগ / লক্ষণ"` [NEW]. Title: Disease Name (e.g., `"Brown Spot"` (`diseaseBrownSpot`) / `"বাদামি দাগ রোগ"`). Subtitle: Alternate language name. | Card: `primaryContainer`; Title: `onPrimaryContainer` (bold 22sp); Subtitle: `onPrimaryContainer` (14sp) | High-prominence card identifying the likely condition. |
| 4 | Inside Condition Card | `bar` (Confidence Bar) + `text` | Height 8 dp bar + 20 dp text | `"Confidence: 87.4% (Likely)"` (`confidenceLabel` + [NEW]) / `"নির্ভরযোগ্যতা: ৮৭.৪% (সম্ভাব্য)"` | Progress: `primary`; Track: `surfaceVariant`; Text: `onPrimaryContainer` | Horizontal progress bar showing confidence percentage. If reduce-motion is enabled, renders filled bar without fill animation. |
| 5 | Lower Body | `card` (Field Advisory Card) | Full width, ~160 dp height | Header: `"Field Advisory"` (`advisoryTitle`) / `"মাঠ পর্যায়ের পরামর্শ"`. Body: Recommended agricultural management practices from local JSON. Footer: `"Consult an upazila agricultural extension officer before taking chemical measures."` [NEW] | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Displays non-prescriptive advisory note (F-06). Prohibited terms like "diagnosis" and "cure" strictly omitted. |
| 6 | Lower Body | `card` (Compact Disclaimer Card) | Full width, ~70 dp height | Header: `"Advisory Notice"` (`disclaimerTitle`) / `"জরুরি সতর্কবার্তা"`. Text: `"This tool provides advisory identification only. Consult an agricultural expert before taking action."` [NEW] / `"এই অ্যাপটি কেবল পরামর্শমূলক। ব্যবস্থা নেওয়ার আগে কৃষি কর্মকর্তার পরামর্শ নিন।"` [NEW] | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Compact disclaimer card (F-08) rendered permanently. |
| 7 | Bottom Body | `button` (OutlinedButton) | Full width, 50 dp height | Icon: `Icons.replay`; Label: `"Scan Another Leaf"` [NEW] / `"আরেকটি পাতা পরীক্ষা করুন"` [NEW] | `outline` (border), `primary` (text/icon) | Clears state and returns to Scan screen. |

---

### 3.5 Result Screen: Uncertain State ($< 60\%$ Confidence)
Rendered when model top prediction has confidence $< 60\%$ (D-11, F-05). Displays warning banner and weak guess; **strictly omits field advisory / treatment section**; includes next steps directing user to Upazila Agriculture Office (DAE) and compact disclaimer card.

- **Layout Structure**: Top App Bar with back arrow, vertical scrollable content.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Scan Result"` [NEW] / `"ফলাফল"` [NEW]. Leading: Back icon (`Icons.arrow_back`). | `surface` (bg), `onSurface` (text) | Returns to Scan screen. |
| 2 | Upper Body | `image` (Captured Photo Preview) | Full width, 200 dp height | Thumbnail of analyzed leaf photo | `surfaceVariant` (border) | Displays image preview with subtle rounded corners (12 dp). |
| 3 | Middle Body | `banner` / `card` (Uncertain Warning Banner) | Full width, ~180 dp height | Icon: `Icons.warning_amber_rounded` (36 dp). Title: `"Uncertain Result"` (`uncertainTitle`) / `"অনিশ্চিত ফলাফল"`. Body: `"Confidence is low. Please consult an agricultural expert for guidance."` (`uncertainDescription`) / `app_bn.arb`. | Container: `errorContainer`; Title & Icon: `onErrorContainer` (bold 20sp); Body: `onErrorContainer` (14sp) | High-visibility warning container. Informs farmer that AI confidence is below safety threshold (D-11). |
| 4 | Inside Banner | `card` (Weak Guess Pill) | Full width, ~50 dp height | `"Possible condition: Brown Spot (52.0%)"` (`weakGuessPrefix` + [NEW]) / `"সম্ভাব্য লক্ষণ: বাদামি দাগ রোগ (৫২.০%)"` | Container: `surface` (50% opacity); Text: `onErrorContainer` (medium 14sp) | Reports top class strictly as an unconfirmed weak guess. |
| 5 | Hidden Section | **NO ADVISORY CARD** | 0 dp height | None | N/A | **Enforces Rule D-11**: The field advisory section is entirely hidden. No spray, fertilizer, or cultural treatment advice is displayed. |
| 6 | Lower Body | `card` (Next Steps Card) | Full width, ~110 dp height | Header: `"Recommended Next Step"` [NEW] / `"করণীয়"` [NEW]. Text: `"Take this leaf sample to your nearest Upazila Agriculture Office (DAE) for expert evaluation."` [NEW] / `"পাতাটি আপনার নিকটস্থ উপজেলা কৃষি অফিসে (ডিএই) নিয়ে যান এবং কৃষি কর্মকর্তার পরামর্শ গ্রহণ করুন।"` [NEW] | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Directs farmer to Upazila Agriculture Office (DAE). |
| 7 | Lower Body | `card` (Compact Disclaimer Card) | Full width, ~70 dp height | Header: `"Advisory Notice"` (`disclaimerTitle`) / `"জরুরি সতর্কবার্তা"`. Text: `"This tool provides advisory identification only. Consult an agricultural expert before taking action."` [NEW] / `"এই অ্যাপটি কেবল পরামর্শমূলক। ব্যবস্থা নেওয়ার আগে কৃষি কর্মকর্তার পরামর্শ নিন।"` [NEW] | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Compact disclaimer card (F-08) rendered permanently. |
| 8 | Bottom Body | `button` (FilledButton) | Full width, 50 dp height | Icon: `Icons.camera_alt`; Label: `"Retake Photo in Better Light"` [NEW] / `"ভালো আলোতে পুনরায় ছবি তুলুন"` [NEW] | `primary` (bg), `onPrimary` (text) | Encourages retaking photo with better lighting or focus. |
| 9 | Bottom Body | `button` (OutlinedButton) | Full width, 50 dp height | Icon: `Icons.arrow_back`; Label: `"Back to Scan"` [NEW] / `"স্ক্যানে ফিরে যান"` [NEW] | `outline` (border), `primary` (text/icon) | Returns to Scan screen. |

---

### 3.6 History Screen (Inside Shell: Tab 2)

#### 3.6.1 Empty State (0 Saved Scans)
- **Layout Structure**: Centered column.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Scan History"` (`historyTitle` / [NEW]) / `"স্ক্যান হিস্ট্রি"` [NEW] | `surface` (bg), `onSurface` (text) | App bar. |
| 2 | Center | `icon` (Empty Graphic) | 80×80 dp | `Icons.history_toggle_off` | `outline` | Large muted history icon. |
| 3 | Center | `text` (Empty Title) | Full width, ~28 dp height | `"No past scans yet."` (`historyEmpty`) / `"এখনো কোনো পূর্ববর্তী তথ্য সংরক্ষিত নেই।"` (`historyEmpty`) | `onSurface` (bold 18sp) | Primary empty state text. |
| 4 | Center | `text` (Empty Description) | Full width, ~40 dp height | `"Leaf scans you perform will appear here offline for future reference."` [NEW] / `"আপনার পূর্ববর্তী সকল স্ক্যান অফলাইনে এখানে সংরক্ষিত থাকবে।"` [NEW] | `onSurfaceVariant` (14sp) | Explanatory text. |
| 5 | Center | `button` (FilledButton) | ~180×48 dp | Icon: `Icons.camera_alt`; Label: `"Start First Scan"` [NEW] / `"প্রথম স্ক্যান শুরু করুন"` [NEW] | `primary` (bg), `onPrimary` (text) | Switches to Scan tab. |

#### 3.6.2 List Layout (Populated History)
- **Layout Structure**: Vertical scrollable list of Material 3 scan cards.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"Scan History (4)"` [NEW] / `"স্ক্যান হিস্ট্রি (৪)"` [NEW] | `surface` (bg), `onSurface` (text) | App bar. Action button: Clear history icon (`Icons.delete_sweep_outlined`). |
| 2..N | Body List | `card` (History Scan Item) | Full width, 84 dp height per item | Leading: 56×56 dp thumbnail. Title: Condition name (e.g., `"Brown Spot"`). Subtitle: `"Yesterday • 87.4% confidence"` [NEW] / `"গতকাল • ৮৭.৪% নির্ভরযোগ্যতা"`. Trailing: Chevron (`Icons.chevron_right`). | Container: `surfaceVariant`; Title: `onSurfaceVariant` (bold); Subtitle: `onSurfaceVariant` (muted) | Tapping item opens historical Result view. Long press allows deleting individual record. |

---

### 3.7 About Screen (Inside Shell: Tab 3)
Contains app identification, academic credits, third-party licenses, dataset credit, and official disclaimer. Dataset credit appears on About, README, dataset card, and store listing only (Decision D-29).

- **Layout Structure**: Vertical scrollable column.

| Order (Top to Bottom) | Region | Element Type | Dimensions (approx) | Text (English / Bangla) | Color Role | Behavior & Accessibility |
|---|---|---|---|---|---|---|
| 1 | Top | `app bar` | Full width, 56 dp height | Title: `"About & Credits"` (`aboutTitle` / [NEW]) / `"অ্যাপ পরিচিতি ও স্বীকৃতি"` [NEW] | `surface` (bg), `onSurface` (text) | App bar. |
| 2 | Top Body | `card` (App Identity Card) | Full width, ~100 dp height | App Name: `"Rice Leaf Disease Detection"` (`appTitle`). Version: `"Version 1.0.0 (Build 1)"` (`versionLabel` + [NEW]). Researcher: `"Academic final-year project by Mehedi Hasan."` [NEW] | Container: `primaryContainer`; Text: `onPrimaryContainer` | Identifies application and academic project attribution (distinct from dataset authorship). |
| 3 | Middle Body | `card` (Software License) | Full width, ~80 dp height | Header: `"Software License"` (`licenseTitle`). Body: `"Released under the MIT License (D-01)."` (`licenseText`). | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Software open-source license declaration. |
| 4 | Middle Body | `card` (Dataset Credit) | Full width, ~170 dp height | Header: `"Dataset credit"` [NEW] / `"ডেটাসেট কৃতিত্ব"` [NEW, to be reviewed by a native speaker before release]. Body (EN): `"Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: images were re-oriented according to EXIF data and re-encoded for training."` Body (BN): [NEW, translation to be reviewed by a native speaker before release] `"ধানের পাতার ছবি: হাসান, এম. প্রমুখ (২০২৩), মেন্ডেলে ডেটা, DOI 10.17632/hx6f852hw4.2, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) লাইসেন্সের অধীন। পরিবর্তন: EXIF ডেটা অনুযায়ী ছবির ওরিয়েন্টেশন সংশোধন করা হয়েছে এবং প্রশিক্ষণের জন্য পুনরায় এনকোড করা হয়েছে।"` | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Placed after version & MIT rows, before font license. Tappable link opens CC BY 4.0 license page in browser. Complies with D-29. |
| 5 | Middle Body | `card` (Font License) | Full width, ~80 dp height | Header: `"Font License"` [NEW]. Body: `"Embedded font Noto Sans Bengali licensed under SIL Open Font License, Version 1.1 (OFL-1.1)."` (`docs/licenses_third_party.md`). | `surfaceVariant` (bg), `onSurfaceVariant` (text) | Embedded font licensing compliance. |
| 6 | Lower Body | `card` (Advisory Notice) | Full width, ~130 dp height | Header: `"Advisory Disclaimer"` (`disclaimerTitle`). Body: `"This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action."` (`disclaimerText`). | Card: `surfaceVariant`; Text: `onSurfaceVariant` | Mandatory visible legal disclaimer (F-08). |

---

## 4. State & Transition Matrix

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
     │   [ Tab 1: Scan Screen ] ◄──┐                                                   │
     │             │               │                                                   │
     │             │ (Capture/Pick)│ (Back/Retake)                                     │
     │             ▼               │                                                   │
     │     [ Inference Isolate ]   │                                                   │
     │             │               │                                                   │
     │     ┌───────┴───────────────┴────────┐                                          │
     │     ▼                                ▼                                          │
     │ [ Result: Confident ]      [ Result: Uncertain ]                                │
     │  - Likely condition card    - Warning banner (D-11)                             │
     │  - Confidence %             - Weak guess (no treatment)                         │
     │  - Field advisory           - Expert consult advice (DAE)                       │
     │  - Compact disclaimer card  - Compact disclaimer card                           │
     │                                                                                 │
     │   [ Tab 2: History Screen ]                                                     │
     │     - State A: Empty State (0 scans)                                            │
     │     - State B: List Layout (thumbnails, dates, condition, confidence)           │
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

## 5. Mockups & Wireframes Inventory (Count Reconciliation)

The proposed design includes exactly **22 standalone HTML wireframes** and **22 rendered PNG screenshots** covering 8 screens/states across light/dark themes and localizations:

| # | Screen / Feature | Theme & Locale | HTML Wireframe (`docs/design/mockups/`) | Rendered PNG (`docs/screenshots/design_proposal/`) |
|---|---|---|---|---|
| 1 | Splash Screen | Light (Default) | `splash_light.html` | `splash_light.png` |
| 2 | Splash Screen | Dark | `splash_dark.html` | `splash_dark.png` |
| 3 | Onboarding Screen | Light (EN/BN toggleable) | `onboarding_light.html` | `onboarding_light.png` |
| 4 | Onboarding Screen | Dark (EN/BN toggleable) | `onboarding_dark.html` | `onboarding_dark.png` |
| 5 | Scan Screen (Home Tab) | Light, English | `scan_light_en.html` | `scan_light_en.png` |
| 6 | Scan Screen (Home Tab) | Dark, English | `scan_dark_en.html` | `scan_dark_en.png` |
| 7 | Scan Screen (Home Tab) | Light, Bangla | `scan_light_bn.html` | `scan_light_bn.png` |
| 8 | Scan Screen (Home Tab) | Dark, Bangla | `scan_dark_bn.html` | `scan_dark_bn.png` |
| 9 | Result: Confident State ($\ge 60\%$) | Light, English | `result_confident_light_en.html` | `result_confident_light_en.png` |
| 10 | Result: Confident State ($\ge 60\%$) | Dark, English | `result_confident_dark_en.html` | `result_confident_dark_en.png` |
| 11 | Result: Confident State ($\ge 60\%$) | Light, Bangla | `result_confident_light_bn.html` | `result_confident_light_bn.png` |
| 12 | Result: Confident State ($\ge 60\%$) | Dark, Bangla | `result_confident_dark_bn.html` | `result_confident_dark_bn.png` |
| 13 | Result: Uncertain State ($< 60\%$) | Light, English | `result_uncertain_light_en.html` | `result_uncertain_light_en.png` |
| 14 | Result: Uncertain State ($< 60\%$) | Dark, English | `result_uncertain_dark_en.html` | `result_uncertain_dark_en.png` |
| 15 | Result: Uncertain State ($< 60\%$) | Light, Bangla | `result_uncertain_light_bn.html` | `result_uncertain_light_bn.png` |
| 16 | Result: Uncertain State ($< 60\%$) | Dark, Bangla | `result_uncertain_dark_bn.html` | `result_uncertain_dark_bn.png` |
| 17 | History: Empty State | Light | `history_empty_light.html` | `history_empty_light.png` |
| 18 | History: Empty State | Dark | `history_empty_dark.html` | `history_empty_dark.png` |
| 19 | History: List Layout | Light | `history_list_light.html` | `history_list_light.png` |
| 20 | History: List Layout | Dark | `history_list_dark.html` | `history_list_dark.png` |
| 21 | About Screen | Light | `about_light.html` | `about_light.png` |
| 22 | About Screen | Dark | `about_dark.html` | `about_dark.png` |

- **True Counts**: 22 HTML wireframes and 22 PNG screenshots.
- **Folder Size**: `docs/screenshots/design_proposal/` total size is 0.61 MB (well below the 2.0 MB ceiling).
