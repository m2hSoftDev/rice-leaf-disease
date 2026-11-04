import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ricedisease/app/app.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/features/home/home_screen.dart';

Widget createTestApp({
  required SharedPreferences prefs,
}) {
  return ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(prefs),
    ],
    child: const RiceDiseaseApp(),
  );
}

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  group('T-060 Route and Navigation Tests', () {
    testWidgets('Splash screen redirects to Onboarding on first launch (onboarding_done=false)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({PrefKeys.onboardingDone: false});
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Onboarding screen is rendered
      expect(find.text('Onboarding Screen'), findsOneWidget);
      expect(find.byKey(const Key('get_started_button')), findsOneWidget);
    });

    testWidgets('Splash screen redirects to Home when onboarding is already complete (onboarding_done=true)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({PrefKeys.onboardingDone: true});
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Home screen is rendered
      expect(find.text('Home Screen'), findsOneWidget);
    });

    testWidgets('Completing onboarding updates SharedPreferences and navigates to Home',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({PrefKeys.onboardingDone: false});
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      expect(find.text('Onboarding Screen'), findsOneWidget);
      await tester.tap(find.byKey(const Key('get_started_button')));
      await tester.pumpAndSettle();

      expect(find.text('Home Screen'), findsOneWidget);
      expect(prefs.getBool(PrefKeys.onboardingDone), isTrue);
    });

    testWidgets('All placeholder screens render correctly via navigation',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({PrefKeys.onboardingDone: true});
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // 1. Home
      expect(find.text('Home Screen'), findsOneWidget);

      // 2. Result
      await tester.tap(find.byKey(const Key('nav_result_button')));
      await tester.pumpAndSettle();
      expect(find.text('Result Screen'), findsOneWidget);
      await tester.pageBack();
      await tester.pumpAndSettle();

      // 3. History
      await tester.tap(find.byKey(const Key('nav_history_button')));
      await tester.pumpAndSettle();
      expect(find.text('History Screen'), findsOneWidget);
      await tester.pageBack();
      await tester.pumpAndSettle();

      // 4. About
      await tester.tap(find.byKey(const Key('nav_about_button')));
      await tester.pumpAndSettle();
      expect(find.text('About Screen'), findsOneWidget);
      await tester.pageBack();
      await tester.pumpAndSettle();

      expect(find.text('Home Screen'), findsOneWidget);
    });
  });

  group('T-060 Localization & Language Toggle Tests', () {
    testWidgets('Language toggle switches locale dynamically between English and Bangla without restart',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Initial state is English
      expect(find.text('Home Screen'), findsOneWidget);
      expect(find.text('বাংলায় দেখুন'), findsOneWidget);

      // Toggle to Bangla
      await tester.tap(find.byKey(const Key('language_toggle_button')));
      await tester.pumpAndSettle();

      // UI updates immediately to Bangla without app restart
      expect(find.text('হোম স্ক্রিন'), findsOneWidget);
      expect(find.text('View in English'), findsOneWidget);
      expect(prefs.getString(PrefKeys.selectedLocale), 'bn');

      // Toggle back to English
      await tester.tap(find.byKey(const Key('language_toggle_button')));
      await tester.pumpAndSettle();

      expect(find.text('Home Screen'), findsOneWidget);
      expect(find.text('বাংলায় দেখুন'), findsOneWidget);
      expect(prefs.getString(PrefKeys.selectedLocale), 'en');
    });
  });

  group('T-061 Font and Localized Strings Tests', () {
    testWidgets('Bangla locale uses NotoSansBengali font and renders Bangla disclaimer',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'bn',
      });
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Home Screen in Bangla
      expect(find.text('হোম স্ক্রিন'), findsOneWidget);

      // Bangla disclaimer is present
      final disclaimerFinder = find.byKey(const Key('disclaimer_text'));
      expect(disclaimerFinder, findsOneWidget);
      final Text disclaimerWidget = tester.widget(disclaimerFinder);
      expect(
        disclaimerWidget.data,
        contains('এই অ্যাপটি কেবল তথ্য ও পরামর্শের জন্য তৈরি'),
      );

      // Theme uses NotoSansBengali font for Bangla
      final BuildContext context = tester.element(find.byType(HomeScreen));
      final theme = Theme.of(context);
      expect(theme.textTheme.bodyMedium?.fontFamily, equals('NotoSansBengali'));
    });

    testWidgets('English locale uses default font (no NotoSansBengali)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Home Screen in English
      expect(find.text('Home Screen'), findsOneWidget);

      // English disclaimer is present
      final disclaimerFinder = find.byKey(const Key('disclaimer_text'));
      expect(disclaimerFinder, findsOneWidget);
      final Text disclaimerWidget = tester.widget(disclaimerFinder);
      expect(
        disclaimerWidget.data,
        contains('This tool is advisory only'),
      );

      // Theme uses default font (not NotoSansBengali) for English
      final BuildContext context = tester.element(find.byType(HomeScreen));
      final theme = Theme.of(context);
      expect(theme.textTheme.bodyMedium?.fontFamily, isNot(equals('NotoSansBengali')));
    });

    testWidgets('Result screen renders all 4 Section 6 Bangla disease names in Bangla locale',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'bn',
      });
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(createTestApp(prefs: prefs));
      await tester.pumpAndSettle();

      // Navigate to Result Screen
      await tester.tap(find.byKey(const Key('nav_result_button')));
      await tester.pumpAndSettle();

      // Confirm all 4 exact Bangla disease names from Section 6
      expect(find.text('ব্যাকটেরিয়াল পাতা ঝলসানো'), findsOneWidget);
      expect(find.text('বাদামি দাগ রোগ'), findsOneWidget);
      expect(find.text('পাতা ব্লাস্ট'), findsOneWidget);
      expect(find.text('সুস্থ পাতা'), findsOneWidget);
    });
  });
}
