import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_bn.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('bn'),
    Locale('en'),
  ];

  /// The title of the application
  ///
  /// In en, this message translates to:
  /// **'Rice Leaf Disease Detection'**
  String get appTitle;

  /// Title for splash screen
  ///
  /// In en, this message translates to:
  /// **'Splash Screen'**
  String get splashTitle;

  /// Title for onboarding screen
  ///
  /// In en, this message translates to:
  /// **'Onboarding Screen'**
  String get onboardingTitle;

  /// Title for home screen
  ///
  /// In en, this message translates to:
  /// **'Home Screen'**
  String get homeTitle;

  /// Title for result screen
  ///
  /// In en, this message translates to:
  /// **'Result Screen'**
  String get resultTitle;

  /// Title for history screen
  ///
  /// In en, this message translates to:
  /// **'History Screen'**
  String get historyTitle;

  /// Title for about screen
  ///
  /// In en, this message translates to:
  /// **'About Screen'**
  String get aboutTitle;

  /// Current language name
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get languageName;

  /// Button label to switch to Bangla
  ///
  /// In en, this message translates to:
  /// **'বাংলায় দেখুন'**
  String get switchToBangla;

  /// Button label to switch to English
  ///
  /// In en, this message translates to:
  /// **'View in English'**
  String get switchToEnglish;

  /// Button to complete onboarding
  ///
  /// In en, this message translates to:
  /// **'Get Started'**
  String get getStarted;

  /// Button to take a leaf photo
  ///
  /// In en, this message translates to:
  /// **'Take Photo'**
  String get takePhoto;

  /// Button to pick photo from gallery
  ///
  /// In en, this message translates to:
  /// **'Choose from Gallery'**
  String get chooseGallery;

  /// Navigation button to result screen
  ///
  /// In en, this message translates to:
  /// **'Go to Result Screen'**
  String get goToResult;

  /// Navigation button to history screen
  ///
  /// In en, this message translates to:
  /// **'Go to History Screen'**
  String get goToHistory;

  /// Navigation button to about screen
  ///
  /// In en, this message translates to:
  /// **'Go to About Screen'**
  String get goToAbout;

  /// Title for disclaimer
  ///
  /// In en, this message translates to:
  /// **'Advisory Notice'**
  String get disclaimerTitle;

  /// Advisory disclaimer text (F-08)
  ///
  /// In en, this message translates to:
  /// **'This tool is advisory only and provides leaf condition identification from photos. It does not replace professional agricultural advice. Please consult an agricultural extension officer before taking action.'**
  String get disclaimerText;

  /// Banner title when confidence is below 60 percent (D-11)
  ///
  /// In en, this message translates to:
  /// **'Uncertain Result'**
  String get uncertainTitle;

  /// Banner description when confidence is low (D-11)
  ///
  /// In en, this message translates to:
  /// **'Confidence is low. Please consult an agricultural expert for guidance.'**
  String get uncertainDescription;

  /// Prefix for weak guess display when uncertain
  ///
  /// In en, this message translates to:
  /// **'Possible condition:'**
  String get weakGuessPrefix;

  /// Class name for Bacterial Leaf Blight
  ///
  /// In en, this message translates to:
  /// **'Bacterial Leaf Blight'**
  String get diseaseBacterialLeafBlight;

  /// Class name for Brown Spot
  ///
  /// In en, this message translates to:
  /// **'Brown Spot'**
  String get diseaseBrownSpot;

  /// Class name for Leaf Blast
  ///
  /// In en, this message translates to:
  /// **'Leaf Blast'**
  String get diseaseLeafBlast;

  /// Class name for Healthy leaf
  ///
  /// In en, this message translates to:
  /// **'Healthy'**
  String get diseaseHealthy;

  /// Class name for Leaf Smut (deferred to v2)
  ///
  /// In en, this message translates to:
  /// **'Leaf Smut'**
  String get diseaseLeafSmut;

  /// Label for prediction confidence percentage
  ///
  /// In en, this message translates to:
  /// **'Confidence'**
  String get confidenceLabel;

  /// Title for disease advisory note
  ///
  /// In en, this message translates to:
  /// **'Field Advisory'**
  String get advisoryTitle;

  /// Empty state text for history screen
  ///
  /// In en, this message translates to:
  /// **'No past scans yet.'**
  String get historyEmpty;

  /// Description of the application in About screen
  ///
  /// In en, this message translates to:
  /// **'Offline mobile application for identifying rice leaf conditions in Bangladesh. Developed as an academic final-year project.'**
  String get aboutDescription;

  /// Credits title in About screen
  ///
  /// In en, this message translates to:
  /// **'Credits & Sources'**
  String get creditsTitle;

  /// Credits description in About screen
  ///
  /// In en, this message translates to:
  /// **'Model trained on public rice leaf dataset by Hasan et al. (CC BY 4.0). Deployed with TensorFlow Lite.'**
  String get creditsText;

  /// License title in About screen
  ///
  /// In en, this message translates to:
  /// **'License'**
  String get licenseTitle;

  /// License details in About screen
  ///
  /// In en, this message translates to:
  /// **'Released under the MIT License. Embedded font Noto Sans Bengali licensed under SIL Open Font License 1.1.'**
  String get licenseText;

  /// App version label
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get versionLabel;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['bn', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'bn':
      return AppLocalizationsBn();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
