import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ricedisease/app/app.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';

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
}
