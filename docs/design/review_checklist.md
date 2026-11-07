# UI Design Review Checklist: Rice Leaf Disease Detection

This checklist provides a structured yes/no evaluation framework for verifying the proposed UI design across all screens, states, safety rules, security policies, and accessibility guidelines prior to implementation approval.

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

## 2. Navigation Shell & Tab Structure (Section 9.1, D-23)

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| N-01 | Is the bottom navigation order strictly **Scan**, **History**, **About**? | [ ] | Mandatory per Decision **D-23**. |
| N-02 | Are **Splash** and **Onboarding** positioned outside the shell (no bottom navigation bar visible)? | [ ] | Full-screen standalone entry flow. |
| N-03 | Does the active tab display an M3 pill indicator using the `primaryContainer` color role with no badge in v1? | [ ] | Material 3 tonal elevation contract; no badges in v1. |
| N-04 | Does the **Result** screen include a clear top app bar back arrow to pop back to Scan? | [ ] | Navigation stack requirement. |
| N-05 | Is the tab switching transition smooth (200 ms cross-fade), and does it snap immediately when reduce-motion is enabled? | [ ] | Accessibility motion contract. |

---

## 3. Screen-by-Screen Review

### 3.1 Splash Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| SP-01 | Does the splash screen display the app logo, full title, and offline descriptor? | [ ] | Branding contract. |
| SP-02 | Is the loading progress indicator indeterminate and responsive (static fallback on reduce-motion)? | [ ] | Circular indicator or 3-dot static fallback. |
| SP-03 | Does the screen automatically navigate to Onboarding on first launch and Scan on subsequent launches? | [ ] | `onboarding_done` shared preference flag. |

### 3.2 Onboarding Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| ON-01 | Is the Language Toggle button prominently accessible in the top app bar? | [ ] | Enables farmer to switch to Bangla immediately. |
| ON-02 | Is the Advisory Notice card rendered with high prominence? | [ ] | F-08 visible notice on first run. |
| ON-03 | Are clear photo capture guidelines provided (natural light, centered leaf, sharp focus)? | [ ] | Ensures input quality for mobile classifier. |
| ON-04 | Does the "Get Started" button have a minimum height of at least 48 dp? | [ ] | Touch target accessibility. |

### 3.3 Scan Screen (Full-Screen Capture Page)
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| SC-01 | Is the 72 dp shutter button fully visible without scrolling in both portrait (412×892 dp) and landscape (892×412 dp)? | [ ] | Viewport geometry guarantee; zero scrolling required. |
| SC-02 | Is the 56 dp gallery button reachable with one thumb within the bottom control panel? | [ ] | Ergonomic reachability test for left/right thumb. |
| SC-03 | Does the camera permission-denied state provide an "Open Settings" action and still allow gallery photo selection? | [ ] | Graceful degradation; gallery remains fully active. |
| SC-04 | Is the disclaimer visible on the capture page as a compact strip that never covers or overlaps the shutter? | [ ] | F-08 notice strip anchored above control panel. |
| SC-05 | Does the top app bar stay readable over the camera preview in light and dark with a gradient scrim? | [ ] | Contrast and legibility over live video preview. |
| SC-06 | Does the photo selected state show clear "Analyze Leaf" and "Retake / Change" actions? | [ ] | Confirmation step before inference. |
| SC-07 | Does the analyzing state display a responsive progress indicator and disable shutter interactions? | [ ] | Prevents duplicate taps during background isolate execution. |

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
| HI-02 | In the populated list, does each scan card display a thumbnail, condition name, timestamp, and confidence %? | [ ] | F-09 list format using lazy `ListView.builder`. |
| HI-03 | Are uncertain scans visually distinguished in the history list (e.g. error icon / muted color)? | [ ] | Distinguishes uncertain records from confident ones. |
| HI-04 | Is there a bulk "Clear All" action protected behind a modal confirmation dialog? | [ ] | Prevents accidental data deletion. |

### 3.7 About Screen
| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| AB-01 | Does the top card state the app name, version (1.0.0), and final-year project attribution to developer Mehedi Hasan? | [ ] | Academic attribution. |
| AB-02 | Is the MIT License (D-01) and Noto Sans Bengali OFL 1.1 license explicitly noted? | [ ] | Software licensing compliance. |
| AB-03 | Does the About screen show the full dataset credit with DOI, CC BY 4.0 link, and modification statement? | [ ] | Expected: yes (Decision D-29 compliance). |
| AB-03b | Does any other screen (Scan, Result, History, Splash, Onboarding, Bottom Navigation) show dataset credit? | [ ] | Expected: no (D-29: credit appears on About, README, dataset card, and store listing only). |
| AB-04 | Is the full Advisory Notice disclaimer displayed? | [ ] | Section 15 legal notice. |

---

## 4. Typography, Localization & Accessibility

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| LA-01 | Are the Bangla disease condition names and UI labels readable and rendered with proper conjuncts (যুক্তাক্ষর) using Noto Sans Bengali? | [ ] | Verified in T-061 font embedding; proper conjunct rendering. |
| LA-02 | Does every interactive touch target satisfy the minimum 48×48 dp dimension? | [ ] | Android Accessibility standard. |
| LA-03 | Does the UI maintain WCAG AA contrast ratio (at least 4.5:1 for normal text, 3:1 for large text) across both Light and Dark themes? | [ ] | Material 3 tonal contrast check. |
| LA-04 | Does any text clip at 200% font scale in English and Bangla? | [ ] | Expected: no (containers wrap dynamically without fixed heights). |
| LA-05 | When "Reduce Motion" is enabled in system settings, are all animations disabled or replaced with instant transitions? | [ ] | Reduce-motion accessibility contract. |

---

## 5. Security, Privacy & Offline Architecture

| Check Item | Question | Yes / No | Notes / Reference |
|---|---|---|---|
| SEC-01 | Are there any network or analytics references in the design, mockups, or specification? | [ ] | Expected: no (strictly 100% offline, zero network calls, zero tracking). |
| SEC-02 | Are camera and gallery permissions requested exclusively just-in-time upon user tap? | [ ] | No startup or onboarding permission prompts. |
| SEC-03 | Are captured images stored solely in app-private storage, with zero data-sharing screens? | [ ] | Sandbox storage only; user can wipe from History. |
| SEC-04 | Does the user interface strictly avoid displaying raw file paths, device IDs, or model internals? | [ ] | Prevents internal information leakage. |
