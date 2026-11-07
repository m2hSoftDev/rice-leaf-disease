// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Rice Leaf Disease Detection';

  @override
  String get splashTitle => 'Splash Screen';

  @override
  String get onboardingTitle => 'Onboarding Screen';

  @override
  String get homeTitle => 'Home Screen';

  @override
  String get resultTitle => 'Result Screen';

  @override
  String get historyTitle => 'History Screen';

  @override
  String get aboutTitle => 'About Screen';

  @override
  String get languageName => 'English';

  @override
  String get switchToBangla => 'বাংলায় দেখুন';

  @override
  String get switchToEnglish => 'View in English';

  @override
  String get getStarted => 'Get Started';

  @override
  String get takePhoto => 'Take Photo';

  @override
  String get chooseGallery => 'Choose from Gallery';

  @override
  String get goToResult => 'Go to Result Screen';

  @override
  String get goToHistory => 'Go to History Screen';

  @override
  String get goToAbout => 'Go to About Screen';

  @override
  String get disclaimerTitle => 'Advisory Notice';

  @override
  String get disclaimerText =>
      'This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.';

  @override
  String get uncertainTitle => 'Uncertain Result';

  @override
  String get uncertainDescription =>
      'Confidence is low. Please consult an agricultural expert for guidance.';

  @override
  String get weakGuessPrefix => 'Possible condition:';

  @override
  String get diseaseBacterialLeafBlight => 'Bacterial Leaf Blight';

  @override
  String get diseaseBrownSpot => 'Brown Spot';

  @override
  String get diseaseLeafBlast => 'Leaf Blast';

  @override
  String get diseaseHealthy => 'Healthy';

  @override
  String get diseaseLeafSmut => 'Leaf Smut';

  @override
  String get confidenceLabel => 'Confidence';

  @override
  String get advisoryTitle => 'Field Advisory';

  @override
  String get historyEmpty => 'No past scans yet.';

  @override
  String get aboutDescription =>
      'Offline mobile application for identifying rice leaf conditions in Bangladesh. Developed as an academic final-year project.';

  @override
  String get creditsTitle => 'Credits & Sources';

  @override
  String get creditsText =>
      'Model trained on public rice leaf dataset by Hasan et al. (CC BY 4.0). Deployed with TensorFlow Lite.';

  @override
  String get licenseTitle => 'License';

  @override
  String get licenseText =>
      'Released under the MIT License. Embedded font Noto Sans Bengali licensed under SIL Open Font License 1.1.';

  @override
  String get versionLabel => 'Version';

  @override
  String get navScan => 'Scan';

  @override
  String get navHistory => 'History';

  @override
  String get navAbout => 'About';

  @override
  String get viewfinderInstruction => 'Position diseased rice leaf in center';

  @override
  String get shutterLabel => 'Capture';

  @override
  String get shutterSemantics => 'Capture leaf photo';

  @override
  String get galleryLabel => 'Gallery';

  @override
  String get helpLabel => 'Help';

  @override
  String get disclaimerStrip =>
      '⚠️ Advisory notice: Advisory tool only; not extension advice. Tap for details.';

  @override
  String get permissionDeniedTitle => 'Camera Access Needed';

  @override
  String get permissionDeniedMessage =>
      'Camera permission is required to capture photos directly. You can still select photos from your gallery.';

  @override
  String get openSettings => 'Open Settings';

  @override
  String get photoSelectedTitle => 'Photo Selected';

  @override
  String get analyzeLeaf => 'Analyze Leaf';

  @override
  String get retakeChange => 'Retake / Change';

  @override
  String get analyzingTitle => 'Analyzing Rice Leaf...';

  @override
  String get analyzingSubtitle => 'Running on-device AI model (MobileNetV2)...';

  @override
  String get scanResultTitle => 'Scan Result';

  @override
  String get likelyCondition => 'Likely Condition';

  @override
  String get likelyTag => 'Likely';

  @override
  String get scanAnother => 'Scan Another Leaf';

  @override
  String get retakeBetterLight => 'Retake Photo in Better Light';

  @override
  String get backToScan => 'Back to Scan';

  @override
  String get extensionOfficeAdvisory =>
      'For official identification and management advice, consult your local Upazila Agriculture Office (DAE).';

  @override
  String get nextStepsTitle => 'Recommended Next Steps';

  @override
  String get nextStepsText =>
      'Take this leaf sample to your nearest Upazila Agriculture Office (DAE) for expert evaluation.';

  @override
  String get startFirstScan => 'Start First Scan';

  @override
  String get historyEmptyDesc =>
      'Scans are stored offline on this device so you can track conditions over time.';

  @override
  String get clearAll => 'Clear All';

  @override
  String get clearAllConfirmTitle => 'Clear all past scans?';

  @override
  String get clearAllConfirmMessage =>
      'This will delete all saved scan history on this device. This action cannot be undone.';

  @override
  String get cancel => 'Cancel';

  @override
  String get delete => 'Delete';

  @override
  String get aboutAndCredits => 'About & Credits';

  @override
  String get developerCredit => 'Academic final-year project by Mehedi Hasan.';

  @override
  String get datasetCreditTitle => 'Dataset Credit';

  @override
  String get datasetCreditText =>
      'Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: images were re-oriented according to EXIF data and re-encoded for training.';

  @override
  String get privacyPolicyTitle => 'Privacy Policy';

  @override
  String get privacyPolicySubtitle =>
      '100% offline. Zero personal data or photos collected or shared.';
}
