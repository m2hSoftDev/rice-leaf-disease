import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ricedisease/app/app.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/features/about/about_screen.dart';
import 'package:ricedisease/features/history/history_screen.dart';
import 'package:ricedisease/features/home/home_screen.dart';
import 'package:ricedisease/features/result/result_screen.dart';
import 'package:ricedisease/features/scan/scan_screen.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/services/inference_service.dart';

Widget createTestAppWithPrefs({
  required SharedPreferences prefs,
  Widget? home,
}) {
  return ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(prefs),
    ],
    child: home != null
        ? MaterialApp(
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: home,
          )
        : const RiceDiseaseApp(),
  );
}

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  group('T-060b Part A: Approved Visual Design Verification Tests', () {
    // 1. Three tabs render and switch
    testWidgets('Three tabs render in navigation shell and switch state (D-23)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      // Portrait phone dimensions (412x892)
      tester.view.physicalSize = const Size(412, 892);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(createTestAppWithPrefs(prefs: prefs));
      await tester.pumpAndSettle();

      // Confirm NavigationBar is present
      expect(find.byType(NavigationBar), findsOneWidget);
      expect(find.byType(NavigationRail), findsNothing);

      // Confirm 3 tabs in strict D-23 order
      expect(find.byKey(const Key('nav_scan_tab')), findsOneWidget);
      expect(find.byKey(const Key('nav_history_tab')), findsOneWidget);
      expect(find.byKey(const Key('nav_about_tab')), findsOneWidget);

      // Tab 0 (Scan) is active initially
      expect(find.byKey(const Key('take_photo_button')), findsOneWidget);
      expect(find.byKey(const Key('choose_gallery_button')), findsOneWidget);

      // Switch to Tab 1 (History)
      await tester.tap(find.byKey(const Key('nav_history_tab')));
      await tester.pumpAndSettle();
      expect(find.text('No past scans yet.'), findsOneWidget);
      expect(find.byKey(const Key('start_first_scan_button')), findsOneWidget);

      // Switch to Tab 2 (About)
      await tester.tap(find.byKey(const Key('nav_about_tab')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('privacy_policy_row')), findsOneWidget);
      expect(find.byKey(const Key('dataset_credit_text')), findsOneWidget);

      // Switch back to Tab 0 (Scan)
      await tester.tap(find.byKey(const Key('nav_scan_tab')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('take_photo_button')), findsOneWidget);
    });

    // 2. NavigationRail appears in landscape
    testWidgets('NavigationRail appears in landscape (width >= 600 dp)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      // Set landscape viewport (892x412)
      tester.view.physicalSize = const Size(892, 412);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(createTestAppWithPrefs(prefs: prefs));
      await tester.pumpAndSettle();

      // NavigationRail is present, NavigationBar is absent
      expect(find.byType(NavigationRail), findsOneWidget);
      expect(find.byType(NavigationBar), findsNothing);
    });

    // 3. Uncertain state hides advisory
    testWidgets('Uncertain state (<60%) hides advisory section completely per D-11',
        (WidgetTester tester) async {
      const uncertainResult = InferenceResult(
        classIndex: 1,
        label: 'brown_spot',
        displayNameEn: 'Brown Spot',
        displayNameBn: 'বাদামি দাগ রোগ',
        confidence: 0.52,
        allConfidences: [0.20, 0.52, 0.15, 0.13],
        isUncertain: true,
        advisoryEn: null,
        advisoryBn: null,
      );

      await tester.pumpWidget(
        const MaterialApp(
          locale: Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: ResultScreen(result: uncertainResult),
        ),
      );
      await tester.pumpAndSettle();

      // Uncertain banner with weak guess and next step is rendered
      expect(find.text('Uncertain Result'), findsOneWidget);
      expect(find.textContaining('Possible condition: Brown Spot (52.0%)'), findsOneWidget);
      expect(find.textContaining('Upazila Agriculture Office (DAE)'), findsOneWidget);

      // Advisory section must be completely absent per D-11
      expect(find.text('Field Advisory'), findsNothing);
    });

    // 4. Advisory shows at 60% or higher
    testWidgets('Advisory section shows when confidence is 60% or higher',
        (WidgetTester tester) async {
      const confidentResult = InferenceResult(
        classIndex: 2,
        label: 'healthy',
        displayNameEn: 'Healthy',
        displayNameBn: 'সুস্থ পাতা',
        confidence: 0.85,
        allConfidences: [0.05, 0.05, 0.85, 0.05],
        isUncertain: false,
        advisoryEn: 'No disease symptoms detected; keep monitoring crop regularly.',
        advisoryBn: 'কোনো রোগের লক্ষণ দেখা যায়নি; নিয়মিত পর্যবেক্ষণ চালিয়ে যান।',
      );

      await tester.pumpWidget(
        const MaterialApp(
          locale: Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: ResultScreen(result: confidentResult),
        ),
      );
      await tester.pumpAndSettle();

      // Confident condition and advisory are rendered
      expect(find.text('Likely Condition'), findsOneWidget);
      expect(find.text('Healthy'), findsOneWidget);
      expect(find.text('Field Advisory'), findsOneWidget);
      expect(find.textContaining('No disease symptoms detected'), findsOneWidget);

      // Uncertain banner is absent
      expect(find.text('Uncertain Result'), findsNothing);
    });

    // 5. Reduce-motion sets durations to zero
    testWidgets('Reduce-motion sets motion durations to zero',
        (WidgetTester tester) async {
      late Duration normalDuration;
      late Duration reducedDuration;

      // Normal motion enabled
      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(disableAnimations: false),
          child: Builder(
            builder: (context) {
              normalDuration = AppTheme.motionDuration(
                context,
                AppTheme.motionStandard,
              );
              return const SizedBox();
            },
          ),
        ),
      );
      expect(normalDuration, equals(const Duration(milliseconds: 300)));

      // Reduce motion active (system accessibility setting)
      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(disableAnimations: true),
          child: Builder(
            builder: (context) {
              reducedDuration = AppTheme.motionDuration(
                context,
                AppTheme.motionStandard,
              );
              return const SizedBox();
            },
          ),
        ),
      );
      expect(reducedDuration, equals(Duration.zero));
    });

    // 6. Permission-denied state still shows gallery button
    testWidgets('Camera permission-denied state still shows active gallery button',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      await tester.pumpWidget(
        createTestAppWithPrefs(
          prefs: prefs,
          home: const ScanScreen(initialState: CaptureState.permissionDenied),
        ),
      );
      await tester.pumpAndSettle();

      // Permission explanation is visible
      expect(find.text('Camera Access Needed'), findsOneWidget);
      expect(find.text('Open Settings'), findsOneWidget);

      // Gallery button remains available and tappable
      final galleryButtonFinder = find.byKey(const Key('choose_gallery_button'));
      expect(galleryButtonFinder, findsOneWidget);
      await tester.tap(galleryButtonFinder);
      await tester.pumpAndSettle();

      // State transitions to photo selected
      expect(find.text('Photo Selected'), findsOneWidget);
    });

    // 7. About shows dataset credit and no other screen does (D-29)
    testWidgets('About screen displays dataset credit (D-29) and no other screen does',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      const confidentResult = InferenceResult(
        classIndex: 2,
        label: 'healthy',
        displayNameEn: 'Healthy',
        displayNameBn: 'সুস্থ পাতা',
        confidence: 0.85,
        allConfidences: [0.05, 0.05, 0.85, 0.05],
        isUncertain: false,
        advisoryEn: 'No symptoms',
        advisoryBn: 'লক্ষণ নেই',
      );

      // 1. About Screen: MUST show dataset credit
      await tester.pumpWidget(
        createTestAppWithPrefs(
          prefs: prefs,
          home: const AboutScreen(),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('dataset_credit_text')), findsOneWidget);
      expect(find.textContaining('Hasan, M. et al.'), findsOneWidget);
      expect(find.textContaining('CC BY 4.0'), findsOneWidget);

      // 2. Scan Screen: MUST NOT show dataset credit
      await tester.pumpWidget(
        createTestAppWithPrefs(
          prefs: prefs,
          home: const ScanScreen(),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('dataset_credit_text')), findsNothing);
      expect(find.textContaining('Hasan, M. et al.'), findsNothing);

      // 3. History Screen: MUST NOT show dataset credit
      await tester.pumpWidget(
        createTestAppWithPrefs(
          prefs: prefs,
          home: const HistoryScreen(),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('dataset_credit_text')), findsNothing);
      expect(find.textContaining('Hasan, M. et al.'), findsNothing);

      // 4. Result Screen: MUST NOT show dataset credit
      await tester.pumpWidget(
        createTestAppWithPrefs(
          prefs: prefs,
          home: const ResultScreen(result: confidentResult),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('dataset_credit_text')), findsNothing);
      expect(find.textContaining('Hasan, M. et al.'), findsNothing);
    });
  });
}
