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
}
