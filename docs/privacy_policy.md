# Privacy Policy: Rice Leaf Disease Detection

**Last Updated / Effective Date**: November 7, 2026 (Placeholder: `[EFFECTIVE_DATE]`)  
**Application**: Rice Leaf Disease Detection (`com.m2hsoftdev.ricedisease`)  
**Developer**: Mehedi Hasan  
**Contact Email**: `[DEVELOPER_EMAIL]` (Placeholder — to be configured before public release)  
**Hosted URL**: `[PRIVACY_POLICY_URL]` (Placeholder — e.g., `https://m2hsoftdev.github.io/rice-leaf-disease/privacy.html`)

---

## 1. Overview & Core Privacy Guarantee

Rice Leaf Disease Detection is designed from the ground up as a **100% offline, privacy-first agricultural utility**. The application operates entirely on your device without transmitting data over the internet.

* **Zero Data Collection**: We do not collect, transmit, harvest, or store any personal information, device identifiers, or user photos on external servers.
* **Zero Tracking & Analytics**: The application bundles **no third-party tracking, analytics SDKs, advertising libraries, or crash reporting services**.
* **Zero Network Traffic**: The application does not require and does not request internet access permissions (`android.permission.INTERNET` is not included in the application manifest).
* **On-Device Artificial Intelligence**: All machine learning inference (MobileNetV2) runs locally on your mobile device processor via TensorFlow Lite.

---

## 2. Information We Do NOT Collect

We do not collect any of the following categories of data:
- Personal identifiers (name, email address, phone number, physical address).
- Precise or coarse location data.
- Device or network identifiers (IMEI, MAC address, Android ID, IP address).
- Usage telemetry, interaction tracking, or behavioral analytics.
- Advertising or commercial profiling data.
- Financial or payment information.

---

## 3. Device Permissions and How They Are Used

The application requests only the minimum runtime permissions required to perform its core offline agricultural utility:

### 3.1 Camera Permission (`CAMERA`)
* **Purpose**: Allows you to take a photo of a rice leaf displaying disease symptoms for local analysis.
* **Timing**: Requested strictly **just-in-time** when you tap the camera capture button. It is never requested at startup or during onboarding.
* **Data Flow**: Camera frames are processed strictly in temporary device memory. Photos taken are never uploaded or shared outside your device.

### 3.2 Photo Library / Storage Access (`READ_MEDIA_IMAGES` / `READ_EXTERNAL_STORAGE`)
* **Purpose**: Allows you to select an existing rice leaf photo from your device gallery.
* **Timing**: Requested only when you tap the gallery selection button.
* **Data Flow**: Only the specific image you pick is accessed by the application. No other files or folders in your device storage are scanned or read.

---

## 4. Local Data Storage & User Control

* **Application-Private Storage**: Images you capture or select, along with their condition identification results, timestamps, and confidence scores, are stored solely in your device's private application sandbox (`/data/user/0/com.m2hsoftdev.ricedisease/`).
* **User Control**: You can clear all saved scan history and associated local images at any time directly within the application via the **"Clear All"** option on the History screen.
* **Uninstallation**: Uninstalling the application immediately and permanently removes all stored scan records, images, and preferences from your device.

---

## 5. Third-Party Services and External Links

* **No Third-Party SDKs**: The application contains no third-party software development kits (SDKs) that transmit user data.
* **External Links**: The application contains informational links to open-source licenses (such as the MIT License and Creative Commons CC BY 4.0). If you click these links, they open in your external web browser, which is governed by your browser's privacy policy and the visited website's policies.

---

## 6. Children's Privacy

The application does not collect any data from anyone, including children under the age of 13. It is a general agricultural reference tool suitable for all ages.

---

## 7. Changes to This Privacy Policy

If we modify our privacy policy in future versions of the application (e.g., if new features are added in v2), we will update the "Last Updated" date at the top of this document and publish the revised policy at `[PRIVACY_POLICY_URL]`.

---

## 8. Contact Information

If you have questions, concerns, or inquiries regarding this Privacy Policy or the data practices of the application, please contact:

* **Developer**: Mehedi Hasan
* **Email**: `[DEVELOPER_EMAIL]`
* **Project Repository**: https://github.com/m2hSoftDev/rice-leaf-disease
* **Physical Address / Institutional Affiliation**: `[PHYSICAL_ADDRESS_OR_ORGANIZATION]` (Placeholder)
