# UI Design Review Checklist: Rice Leaf Disease Detection

This checklist provides a structured yes/no evaluation framework for verifying the proposed UI design across all screens, states, safety rules, and accessibility guidelines prior to implementation approval.

---

## 1. Safety & Medical Language Compliance (Section 6, D-11)

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| S-01 | Are the prohibited terms **"diagnosis"** and **"cure"** completely absent from all user-facing copy in both English and Bangla? | [ ] | Strict policy: Only "possible condition" or "likely condition" are permitted. |
| S-02 | In the **Result: Uncertain State** ($< 60\%$ confidence), is the field advisory / treatment section **completely absent**? | [ ] | Mandatory per **Rule D-11**. No spray, fertilizer, or cultural treatment advice may be shown. |
| S-03 | In the **Result: Uncertain State**, is the top prediction explicitly labeled as an unconfirmed weak guess (e.g., *"Possible condition: Brown Spot (52.0%)"*)? | [ ] | D-11 & Section 9.2: Weak guess only. |
| S-04 | Is the official legal disclaimer (F-08) visible on **Scan**, **Result Confident** (light & dark, EN & BN), and **Result Uncertain** (light & dark, EN & BN) in a compact card? | [ ] | F-08 requirement: Permanent visible advisory notice across all scan and result states. |
| S-05 | Does the disclaimer clearly state that the tool is advisory only and does not replace professional agricultural extension advice? | [ ] | `disclaimerText` verbatim quote from `app_en.arb` / `app_bn.arb`. |
| S-06 | Is **"Upazila Agriculture Office (DAE)"** used instead of **"sub-assistant agriculture officer"** across all screens, advisories, and recommended next steps? | [ ] | Institutional designation per Department of Agricultural Extension (DAE) hierarchy. |

---

## 2. Navigation Shell & Tab Structure (Section 9.1)

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| N-01 | Is the Bottom NavigationBar fixed at the bottom with exactly three destinations in order: **Scan**, **History**, **About**? | [ ] | M3 NavigationBar shell pattern. |
| N-02 | Are **Splash** and **Onboarding** positioned outside the shell (no bottom navigation bar visible)? | [ ] | Full-screen standalone entry flow. |
| N-03 | Does the active tab display an M3 pill indicator using the `primaryContainer` color role? | [ ] | Material 3 tonal elevation contract. |
| N-04 | Does the **Result** screen include a clear top app bar back arrow to pop back to Scan? | [ ] | Navigation stack requirement. |
| N-05 | Is the tab switching transition smooth (200 ms cross-fade), and does it snap immediately when reduce-motion is enabled? | [ ] | Accessibility motion contract. |

---

## 3. Screen-by-Screen Review

### 3.1 Splash Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| SP-01 | Does the splash screen display the app logo, full title, and offline descriptor? | [ ] | Branding contract. |
| SP-02 | Is the loading progress indicator indeterminate and responsive? | [ ] | Circular indicator or 3-dot static fallback. |
| SP-03 | Does the screen automatically navigate to Onboarding on first launch and Scan on subsequent launches? | [ ] | `onboarding_done` shared preference flag. |

### 3.2 Onboarding Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| ON-01 | Is the Language Toggle button prominently accessible in the top app bar? | [ ] | Enables farmer to switch to Bangla immediately. |
| ON-02 | Is the Advisory Notice card rendered with high prominence? | [ ] | F-08 visible notice on first run. |
| ON-03 | Are clear photo capture guidelines provided (natural light, centered leaf, sharp focus)? | [ ] | Ensures input quality for mobile classifier. |
| ON-04 | Does the "Get Started" button have a minimum height of at least 48 dp? | [ ] | Touch target accessibility. |

### 3.3 Scan Screen (Home Tab)
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| SC-01 | Is the viewfinder placeholder clearly indicated with a dashed boundary and centering instruction? | [ ] | Guides user to frame diseased rice leaf. |
| SC-02 | Are both "Take Photo" (primary filled button) and "Choose from Gallery" (outlined button) easily distinguishable? | [ ] | F-01 (camera) and F-02 (gallery picker). |
| SC-03 | Is the language switch button operational in the top app bar? | [ ] | Immediate locale toggle without restart. |
| SC-04 | Is the permanent Advisory Notice card visible without requiring vertical scrolling on standard screens? | [ ] | F-08 requirement. |

### 3.4 Result Screen: Confident State ($\ge 60\%$)
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| RC-01 | Does the screen display a clean preview of the captured/selected leaf photo? | [ ] | Visual confirmation for user. |
| RC-02 | Is the condition prominently displayed as "Likely Condition" (or "সম্ভাব্য রোগ / লক্ষণ")? | [ ] | Safety wording requirement. |
| RC-03 | Does the confidence bar display the exact numerical percentage alongside the "Likely" tag? | [ ] | F-04 confidence display. |
| RC-04 | Does the Field Advisory card contain actionable cultural/management notes and prompt expert consultation? | [ ] | F-06 non-prescriptive advisory. |
| RC-05 | Is the compact disclaimer card (F-08) visible below the field advisory card? | [ ] | Permanent advisory notice requirement. |
| RC-06 | Is there a primary action button to "Scan Another Leaf"? | [ ] | Quick return to scanning loop. |

### 3.5 Result Screen: Uncertain State ($< 60\%$)
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| RU-01 | Does the screen render an high-visibility warning container using `errorContainer` and `onErrorContainer`? | [ ] | F-05 / D-11 low-confidence warning banner. |
| RU-02 | Is the title "Uncertain Result" ("অনিশ্চিত ফলাফল") with warning icon clearly visible? | [ ] | D-11 clear banner. |
| RU-03 | Is the weak guess framed conservatively (e.g., *"Possible condition: Brown Spot (52.0%)"* / *"সম্ভাব্য লক্ষণ: বাদামি দাগ রোগ (৫২.০%)"*)? | [ ] | Weak guess presentation. |
| RU-04 | Is the Field Advisory / Treatment card **completely hidden**? | [ ] | **Rule D-11 zero treatment advice policy.** |
| RU-05 | Does the screen provide an expert consultation next step card directing the user to their **Upazila Agriculture Office (DAE)**? | [ ] | Institutional extension guidance. |
| RU-06 | Is the compact disclaimer card (F-08) visible below the recommended next step card? | [ ] | Permanent advisory notice requirement. |
| RU-07 | Is there a prominent button to "Retake Photo in Better Light"? | [ ] | Helps resolve poor photo quality. |

### 3.6 History Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| HI-01 | Does the empty state display a friendly illustration, title, description, and "Start First Scan" call to action? | [ ] | F-09 empty state handling. |
| HI-02 | In the populated list, does each scan card display a thumbnail, condition name, timestamp, and confidence %? | [ ] | F-09 list format. |
| HI-03 | Are uncertain scans visually distinguished in the history list (e.g. error icon / muted color)? | [ ] | Distinguishes uncertain records from confident ones. |
| HI-04 | Is there a bulk "Clear All" or individual swipe-to-delete action? | [ ] | History management. |

### 3.7 About Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| AB-01 | Does the top card state the app name, version (1.0.0), and final-year project attribution? | [ ] | Academic attribution. |
| AB-02 | Is the MIT License (D-01) and Noto Sans Bengali OFL 1.1 license explicitly noted? | [ ] | Software licensing compliance. |
| AB-03 | Is dataset credit **excluded** from the About screen and kept only in `README.md` and `docs/dataset_card.md`? | [ ] | Dataset attribution policy compliance. |
| AB-04 | Is the full Advisory Notice disclaimer displayed? | [ ] | Section 15 legal notice. |

---

## 4. Typography, Localization & Accessibility

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| LA-01 | Are the Bangla disease condition names and UI labels readable and rendered with proper conjuncts (যুক্তাক্ষর) using Noto Sans Bengali? | [ ] | Verified in T-061 font embedding; proper conjunct rendering. |
| LA-02 | Does every interactive touch target satisfy the minimum 48×48 dp dimension? | [ ] | Android Accessibility standard. |
| LA-03 | Does the UI maintain WCAG AA contrast ratio (at least 4.5:1 for normal text, 3:1 for large text) across both Light and Dark themes? | [ ] | Material 3 tonal contrast check. |
| LA-04 | Does the layout adapt gracefully when OS system text scaling (up to 1.3×) is active without clipping text? | [ ] | Accessibility text scaling test. |
| LA-05 | When "Reduce Motion" is enabled in system settings, are all animations disabled or replaced with instant transitions? | [ ] | Reduce-motion accessibility contract. |
