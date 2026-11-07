# Google Play Console: Data Safety Form Answers

**Application**: Rice Leaf Disease Detection  
**Package Name**: `com.m2hsoftdev.ricedisease`  
**Developer**: Mehedi Hasan  
**Target Release**: v1.0.0 (M7 Release, Task T-082)  
**Status**: DRAFT / READY FOR CONSOLE ENTRY  
**Open Placeholders**: `[DEVELOPER_EMAIL]`, `[PRIVACY_POLICY_URL]`

This document provides the exact questionnaire responses required by the Google Play Console **Data safety** declaration section.

---

## 1. Overview Questions

| Questionnaire Prompt | Google Play Console Answer | Technical Verification / Fact-Check |
|---|---|---|
| **Does your app collect or share any of the required user data types?** | **No** | Verified: Zero network calls. `android.permission.INTERNET` is omitted from `AndroidManifest.xml`. No analytics, ads, or tracking SDKs in `pubspec.yaml`. |
| **Is all of the user data collected by your app encrypted in transit?** | **N/A** (disabled because no data is collected or transmitted) | The app does not transmit data over the network. |
| **Do you provide a way for users to request that their data is deleted?** | **Yes** | Users can wipe all saved scan history and photos locally via the "Clear All" button in the History tab. Uninstalling the app completely purges the app-private directory. |
| **Is your app's data safety form compliant with the Google Play Families policy?** | **Yes** | No personal data is collected or shared; target audience includes general users and families. |

---

## 2. Specific Data Type Inquiries

| Data Category | Data Type | Collected? | Shared? | Purpose / Details |
|---|---|---|---|---|
| **Location** | Approximate location | **No** | **No** | Not accessed or requested. |
| | Precise location | **No** | **No** | Not accessed or requested. |
| **Personal Info** | Name, Email, Phone, Address, ID | **No** | **No** | Not collected. No account creation exists. |
| **Financial Info** | Credit card, bank account, purchase history | **No** | **No** | No purchases or financial transactions. |
| **Health and Fitness**| Health info, fitness info | **No** | **No** | Not collected. |
| **Messages** | Emails, SMS/MMS | **No** | **No** | Not accessed. |
| **Photos and Videos**| Photos | **No (Not collected/shared)** | **No** | Leaf photos captured or selected remain **strictly on the user's local device**. They are never uploaded or transmitted to any server. |
| **Audio Files** | Voice/sound recordings | **No** | **No** | Not accessed. |
| **Files and Docs** | Files and documents | **No** | **No** | Not collected or transmitted. |
| **Calendar** | Calendar events | **No** | **No** | Not accessed. |
| **Contacts** | Contact book | **No** | **No** | Not accessed. |
| **App Activity** | Page views, interactions, search history | **No** | **No** | Zero analytics SDKs. No telemetry collected. |
| **Web Browsing** | Browsing history | **No** | **No** | Not collected. |
| **App Info and Performance** | Crash logs, diagnostics, performance metrics | **No** | **No** | No crash-reporting SDK (Crashlytics, Sentry, etc.) installed. |
| **Device or Other IDs** | Device ID, advertising ID, Android ID | **No** | **No** | Not collected or accessed. |

---

## 3. Runtime Device Permissions Declared

The application declares the following permissions in Android:

1. `android.permission.CAMERA`:
   - **Declared for**: Taking photos of diseased leaves for on-device analysis.
   - **Play Store Justification**: Core app functionality (leaf disease classification).
   - **Data Handling**: Frames processed locally in device RAM via TensorFlow Lite; zero frames transmitted.
2. `android.permission.READ_MEDIA_IMAGES` / `android.permission.READ_EXTERNAL_STORAGE`:
   - **Declared for**: Selecting a photo from the local device gallery.
   - **Play Store Justification**: Core app functionality (analyzing previously taken leaf photo).
   - **Data Handling**: User explicitly picks the image; image is copied to app-private cache for local model inference; zero bytes transmitted.

---

## 4. Privacy Policy URL for Play Console Store Listing

* **Field in Play Console**: App content -> Privacy policy -> URL
* **Target URL**: `[PRIVACY_POLICY_URL]` (e.g., `https://m2hsoftdev.github.io/rice-leaf-disease/privacy.html`)
* **Verification Status**: Pending public GitHub Pages publication before production track submission (Gate 5).
