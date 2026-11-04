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
  String get disclaimerText =>
      'This tool is advisory only and does not replace professional agricultural advice.';
}
