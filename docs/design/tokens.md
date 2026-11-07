# Design Tokens & System Rules: Rice Leaf Disease Detection

This document specifies the core design tokens, color roles, typography scale, spacing grid, radii, elevation levels, touch targets, and motion contracts for the mobile application (`com.m2hsoftdev.ricedisease`).

All visual values derive strictly from Material Design 3 (M3) specifications and accessibility standards (WCAG 2.1 AA and Android Accessibility Guidelines).

---

## 1. Color System (Derived from Green Seed)

All semantic color roles are generated deterministically from a single agricultural green seed:
* **Seed Color**: `#2E7D32` (Material Green 800 — healthy rice canopy green)

No arbitrary hex values are permitted in the application. Every color token maps to a semantic Material 3 role:

| Color Role | Light Theme Value | Dark Theme Value | Derived Relationship / Usage |
|---|---|---|---|
| `primary` | `#236A34` | `#8CD699` | Key brand tone, primary buttons, active icons, shutter fill |
| `onPrimary` | `#FFFFFF` | `#003914` | Text and icons placed on top of `primary` |
| `primaryContainer` | `#A7F3B3` | `#055320` | Navigation selection pills, likely condition card background |
| `onPrimaryContainer` | `#00210A` | `#A7F3B3` | High-contrast text/icons on `primaryContainer` |
| `surface` | `#F8FAF6` | `#111411` | Default screen background, base canvas |
| `onSurface` | `#191C19` | `#E1E3DF` | High-emphasis body text, app bar title, primary headings |
| `surfaceVariant` | `#EEF2EB` | `#2D312C` | Card containers, viewfinder border, text field fills |
| `onSurfaceVariant` | `#424940` | `#C2C8BE` | Secondary text, inactive navigation icons, captions |
| `surfaceContainer` | `#F0F4ED` | `#191C19` | Bottom navigation bar background, dialog surfaces |
| `surfaceTint` | `#236A34` | `#8CD699` | Scrim/elevation overlay applied to App Bar when scrolled |
| `outline` | `#72796F` | `#8C9388` | Viewfinder guide brackets, outlined buttons, subtle borders |
| `outlineVariant` | `#C2C8BE` | `#424940` | Dividers, dashed guidelines, inactive shutter ring |
| `error` | `#BA1A1A` | `#FFB4AB` | Critical warnings, destructive actions, camera error |
| `onError` | `#FFFFFF` | `#690005` | Text/icons placed on top of `error` |
| `errorContainer` | `#FFDAD6` | `#4D0005` | Uncertain result banner background, permission denial banner |
| `onErrorContainer` | `#410002` | `#FFDAD6` | High-contrast warning text and icons on `errorContainer` |
| `tertiary` | `#386567` | `#A0CFD0` | Accent badges, auxiliary informational chips |
| `onTertiary` | `#FFFFFF` | `#043638` | Text on tertiary accent |
| `scrim` | `rgba(0,0,0,0.4)` | `rgba(0,0,0,0.6)` | Gradient overlay over camera preview behind App Bar and controls |

---

## 2. Typography Scale (Material 3 & Dual-Locale)

### 2.1 Font Families
* **English Locale (`en`)**: System default font (`Roboto` on Android / system sans-serif).
* **Bangla Locale (`bn`)**: Embedded **Noto Sans Bengali** (`NotoSansBengali-Regular.ttf`, `NotoSansBengali-Bold.ttf`, OFL 1.1).

### 2.2 Material 3 Type Roles & Scaling Contract
All text elements must support OS-level text scaling up to **200%** without clipping, overlapping, or truncation. Containers must never enforce fixed vertical dimensions when wrapping multiline text.

| M3 Type Role | Size (sp) | Weight | Line Height (dp) | Tracking | Primary Usage |
|---|---|---|---|---|---|
| `displayLarge` | 57 | Regular (400) | 64 | -0.25 | Splash hero metrics |
| `displayMedium` | 45 | Regular (400) | 52 | 0 | Splash headers |
| `headlineLarge` | 32 | Bold (700) | 40 | 0 | Top-level screen hero titles |
| `headlineMedium` | 28 | SemiBold (600) | 36 | 0 | Disease condition name in Result |
| `headlineSmall` | 24 | Medium (500) | 32 | 0 | Dialog titles, section headers |
| `titleLarge` | 22 | Bold (700) | 28 | 0 | App bar title, major card headers |
| `titleMedium` | 16 | SemiBold (600) | 24 | +0.15 | Sub-headers, advisory card titles |
| `titleSmall` | 14 | Medium (500) | 20 | +0.1 | Control panel labels (shutter, gallery) |
| `bodyLarge` | 16 | Regular (400) | 24 | +0.5 | Main body copy, advisory instructions |
| `bodyMedium` | 14 | Regular (400) | 20 | +0.25 | Secondary body, disclaimer strip text |
| `bodySmall` | 12 | Regular (400) | 16 | +0.4 | Captions, metadata timestamps, license notes |
| `labelLarge` | 14 | SemiBold (600) | 20 | +0.1 | Action buttons, analyze button |
| `labelMedium` | 12 | Medium (500) | 16 | +0.5 | Bottom navigation bar labels, tag pills |
| `labelSmall` | 11 | Medium (500) | 16 | +0.5 | Small status chips, confidence indicator |

---

## 3. Spacing Grid & Layout Geometry

The spatial system follows an **8-point grid**, with a **4-point micro-grid** for fine alignment:

| Token | Dimension (dp) | Usage |
|---|---|---|
| `space-xxs` | 4 | Fine inner padding, tag border offsets |
| `space-xs` | 8 | Gap between icon and text, list item spacing |
| `space-sm` | 12 | Compact card padding, chip horizontal inset |
| `space-md` | 16 | Standard screen margin, card inner padding |
| `space-lg` | 20 | Card stack vertical separation, header bottom margin |
| `space-xl` | 24 | Control panel vertical padding, dialog margins |
| `space-2xl` | 32 | Hero element separation, empty state spacing |
| `space-3xl` | 40 | Splash icon top margin |
| `space-4xl` | 48 | Minimum interactive touch target boundary |
| `space-shutter`| 72 | Diameter of central camera capture shutter |

---

## 4. Corner Radii & Elevation Levels

### 4.1 Corner Radii
* **Cards & Containers**: `16 dp` to `20 dp` (standard M3 card curvature).
* **Buttons (Filled / Outlined)**: `12 dp` to `16 dp`.
* **Chips & Badges**: `8 dp`.
* **Selection Pills & Navigation Indicators**: Full pill (`9999 dp` / `16 dp` half-height).
* **Shutter Button**: Full circle (`50%` / `36 dp` radius for 72 dp button).
* **Control Buttons (Gallery / Help)**: Circular pill (`50%` / `28 dp` radius for 56 dp button).

### 4.2 Elevation Levels (Material 3 Tonal Elevation)
In Material 3, elevation is rendered via tonal color surface shifts (`surfaceTint`), not heavy drop shadows:
* **Level 0 (0 dp)**: Full-bleed camera preview, flat canvas.
* **Level 1 (1 dp)**: Cards resting on surface (`surfaceContainerLow`).
* **Level 2 (3 dp)**: Bottom NavigationBar (`surfaceContainer`), Scrolled App Bar.
* **Level 3 (6 dp)**: Floating control panel over camera preview, Dialogs.
* **Level 4 (8 dp)**: Floating Action Buttons (FAB).
* **Level 5 (12 dp)**: Modal bottom sheets.

---

## 5. Touch Targets & Ergonomics

Strict compliance with Android Accessibility Guidelines:
* **Standard Minimum Touch Target**: **48×48 dp** for all interactive icons, buttons, navigation destinations, and list chevrons.
* **Camera Shutter Button**: **72×72 dp** circular footprint with a `4 dp` outer tactile stroke ring and `80×80 dp` clear touch boundary.
* **Auxiliary Capture Controls (Gallery, Flash/Help)**: **56×56 dp** touch targets placed comfortably within thumb reach.
* **One-Thumb Ergonomics**: On the Capture screen, the Shutter, Gallery picker, and Help toggle sit within the bottom 120 dp of the viewport, well within the natural sweep of either the right or left thumb.

---

## 6. Motion & Animation Contract

All animations adhere to Material 3 motion tokens:
* **Short / Micro-interactions**: `200 ms` (cubic-bezier `0.2, 0.0, 0, 1.0`) — button press state, icon toggle.
* **Standard / Container Expansion**: `300 ms` (cubic-bezier `0.2, 0.0, 0, 1.0`) — disclaimer expand/collapse, dialog appearance.
* **Emphasized / Screen Transitions**: `350 ms` (cubic-bezier `0.05, 0.7, 0.1, 1.0`) — navigation tab cross-fade, photo selection reveal.

### Reduce-Motion Accessibility Contract
When the user has enabled **"Reduce Motion"** or **"Remove Animations"** in Android system accessibility settings:
* All transition durations immediately drop to **`0 ms`** (instant state jump).
* Animated progress bars and loading spinners render as **static, accessible state indicators** (e.g. solid filled progress bar or clear textual indicator).
* Camera shutter squeeze animations are disabled; capture response is indicated solely by an immediate haptic tick and border flash.

