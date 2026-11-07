import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ricedisease/app/app.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/features/privacy/privacy_screen.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

Widget createTestAppWithPrefs(SharedPreferences prefs) {
  return ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(prefs),
    ],
    child: RiceDiseaseApp(key: UniqueKey()),
  );
}

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  group('T-081 Privacy Policy Parity and Screen Tests', () {
    test('app/assets/privacy/privacy_en.md matches docs/privacy_policy.md exactly', () {
      final assetFile = File('assets/privacy/privacy_en.md');
      final docFile = File('../docs/privacy_policy.md');

      expect(assetFile.existsSync(), isTrue,
          reason: 'assets/privacy/privacy_en.md must exist in app/assets');
      expect(docFile.existsSync(), isTrue,
          reason: 'docs/privacy_policy.md must exist in docs/');

      // Normalize CRLF to LF for cross-platform byte comparison
      final assetContent = assetFile.readAsStringSync().replaceAll('\r\n', '\n');
      final docContent = docFile.readAsStringSync().replaceAll('\r\n', '\n');

      expect(assetContent, equals(docContent),
          reason: 'In-app privacy text must be identical to canonical docs/privacy_policy.md');
    });

    testWidgets('Privacy screen opens from About row and displays contact email and address',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(PrefKeys.onboardingDone, true);
      await prefs.setString(PrefKeys.selectedLocale, 'en');

      await tester.pumpWidget(createTestAppWithPrefs(prefs));
      await tester.pumpAndSettle();

      // Navigate to About screen
      await tester.tap(find.byKey(const Key('nav_about_button')));
      await tester.pumpAndSettle();

      // Find and tap the Privacy Policy row
      final privacyRowFinder = find.byKey(const Key('privacy_policy_row'));
      expect(privacyRowFinder, findsOneWidget);

      await tester.ensureVisible(privacyRowFinder);
      await tester.pumpAndSettle();

      await tester.tap(privacyRowFinder);
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Confirm PrivacyScreen is displayed
      expect(find.byType(PrivacyScreen), findsOneWidget);
      expect(find.text('Privacy Policy'), findsOneWidget);

      // Verify contact email, date, and address appear in the policy text
      expect(find.textContaining('m2hsoftdev@gmail.com'), findsOneWidget);
      expect(find.textContaining('Sylhet, Bangladesh'), findsOneWidget);
      expect(find.textContaining('2026-11-07'), findsOneWidget);

      // Verify no open placeholders remain
      expect(find.textContaining('[DEVELOPER_EMAIL]'), findsNothing);
      expect(find.textContaining('[EFFECTIVE_DATE]'), findsNothing);
      expect(find.textContaining('[PHYSICAL_ADDRESS_OR_ORGANIZATION]'), findsNothing);
    });

    testWidgets('Bangla locale shows pending translation notice and English policy with contact email',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'bn',
      });
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(PrefKeys.onboardingDone, true);
      await prefs.setString(PrefKeys.selectedLocale, 'bn');

      await tester.pumpWidget(createTestAppWithPrefs(prefs));
      await tester.pumpAndSettle();

      // Navigate to About screen
      await tester.tap(find.byKey(const Key('nav_about_button')));
      await tester.pumpAndSettle();

      // Find and tap the Privacy Policy row
      final privacyRowFinder = find.byKey(const Key('privacy_policy_row'));
      expect(privacyRowFinder, findsOneWidget);

      await tester.ensureVisible(privacyRowFinder);
      await tester.pumpAndSettle();

      await tester.tap(privacyRowFinder);
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Confirm PrivacyScreen in Bangla
      expect(find.byType(PrivacyScreen), findsOneWidget);
      expect(find.text('গোপনীয়তা নীতি'), findsOneWidget);

      // Notice card is displayed in Bangla
      expect(
        find.textContaining('বাংলা সংস্করণ পর্যালোচনার জন্য প্রক্রিয়াধীন রয়েছে'),
        findsOneWidget,
      );

      // English content remains accessible and displays contact email
      expect(find.textContaining('m2hsoftdev@gmail.com'), findsOneWidget);
      expect(find.textContaining('Sylhet, Bangladesh'), findsOneWidget);
    });
  });
}
