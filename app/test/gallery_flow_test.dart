import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ricedisease/app/providers.dart';
import 'package:ricedisease/app/router.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/features/result/result_screen.dart';
import 'package:ricedisease/features/scan/scan_screen.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/services/inference_service.dart';
import 'package:ricedisease/services/preprocess_service.dart';

import 'mock_services.dart';

Widget createGalleryTestApp({
  required SharedPreferences prefs,
  required MockPreprocessService preprocessService,
  required MockInferenceService inferenceService,
  Locale locale = const Locale('en'),
}) {
  return ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(prefs),
      preprocessServiceProvider.overrideWithValue(preprocessService),
      inferenceServiceProvider.overrideWithValue(inferenceService),
    ],
    child: MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      onGenerateRoute: AppRouter.onGenerateRoute,
      home: const ScanScreen(),
    ),
  );
}

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  group('T-060c Gallery Flow and Inference Routing Tests', () {
    testWidgets(
        'Step 1 & 4a: Mocked gallery pick produces ResultScreen with label from mocked inference result and shows analyzing state',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final inferenceCompleter = Completer<InferenceResult>();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async {
          expect(source, equals(ImageSource.gallery));
          return XFile.fromData(
            Uint8List.fromList([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10]),
            name: 'rice_leaf_blast.jpg',
          );
        },
        onPreprocess: (bytes) {
          return Float32List(PreprocessService.outputElementCount);
        },
      );

      final mockInference = MockInferenceService(
        onRunInference: (tensor) => inferenceCompleter.future,
      );

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      // Tap gallery button
      final galleryButtonFinder =
          find.byKey(const Key('choose_gallery_button'));
      expect(galleryButtonFinder, findsOneWidget);
      await tester.tap(galleryButtonFinder);
      await tester.pump();

      // Verify analyzing state is visible while inference runs
      expect(find.text('Analyzing Rice Leaf...'), findsOneWidget);
      expect(
        find.text('Running on-device AI model (MobileNetV2)...'),
        findsOneWidget,
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Complete inference with confident result (>= 60%)
      const confidentResult = InferenceResult(
        classIndex: 3,
        label: 'leaf_blast',
        displayNameEn: 'Leaf Blast',
        displayNameBn: 'পাতা ব্লাস্ট',
        confidence: 0.88,
        allConfidences: [0.04, 0.04, 0.04, 0.88],
        isUncertain: false,
        advisoryEn:
            'Monitor humidity; use resistant varieties; reduce excessive nitrogen; consult an agricultural extension officer.',
        advisoryBn:
            'আর্দ্রতা পর্যবেক্ষণ করুন; প্রতিরোধী জাত ব্যবহার করুন; অতিরিক্ত নাইট্রোজেন কমান; কৃষি কর্মকর্তার পরামর্শ নিন।',
      );
      inferenceCompleter.complete(confidentResult);
      await tester.pumpAndSettle();

      // ResultScreen is opened
      expect(find.byType(ResultScreen), findsOneWidget);

      // Label from mocked inference is displayed
      expect(find.text('Leaf Blast'), findsOneWidget);
      expect(find.text('Likely Condition'), findsOneWidget);

      // Advisory section is visible
      expect(find.text('Field Advisory'), findsOneWidget);
      expect(
        find.textContaining('Monitor humidity; use resistant varieties'),
        findsOneWidget,
      );
      expect(
        find.textContaining('Upazila Agriculture Office (DAE)'),
        findsOneWidget,
      );

      // Uncertain banner must NOT be present
      expect(find.text('Uncertain Result'), findsNothing);
    });

    testWidgets(
        'Step 2 & 4b: Below-60% mocked result hides advisory and shows uncertain banner with weak guess and DAE next step (D-11)',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async => XFile.fromData(
          Uint8List.fromList([0xFF, 0xD8, 0xFF, 0xE0]),
          name: 'uncertain_leaf.jpg',
        ),
        onPreprocess: (_) => Float32List(PreprocessService.outputElementCount),
      );

      // Top confidence 0.45 < 0.60 (D-11)
      const uncertainResult = InferenceResult(
        classIndex: 1,
        label: 'brown_spot',
        displayNameEn: 'Brown Spot',
        displayNameBn: 'বাদামি দাগ রোগ',
        confidence: 0.45,
        allConfidences: [0.25, 0.45, 0.15, 0.15],
        isUncertain: true,
        advisoryEn: null,
        advisoryBn: null,
      );

      final mockInference = MockInferenceService(
        onRunInference: (_) async => uncertainResult,
      );

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('choose_gallery_button')));
      await tester.pumpAndSettle();

      // ResultScreen is opened
      expect(find.byType(ResultScreen), findsOneWidget);

      // Uncertain warning banner is displayed
      expect(find.text('Uncertain Result'), findsOneWidget);
      expect(
        find.textContaining('Possible condition: Brown Spot (45.0%)'),
        findsOneWidget,
      );
      expect(
        find.text('Confidence is low. Please consult an agricultural expert for guidance.'),
        findsOneWidget,
      );

      // Recommended next steps directing to DAE is displayed
      expect(find.text('Recommended Next Steps'), findsOneWidget);
      expect(
        find.textContaining('nearest Upazila Agriculture Office (DAE)'),
        findsOneWidget,
      );

      // Field advisory must be completely HIDDEN (D-11)
      expect(find.text('Field Advisory'), findsNothing);
      expect(
        find.textContaining('Apply balanced fertilizer'),
        findsNothing,
      );
    });

    testWidgets(
        'Step 1 & 4c: Preprocessing error (>10 MB) displays localized message and does not open ResultScreen',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async {
          throw const ImageTooLargeException(
            'Image exceeds the 10 MB limit (12.45 MB). Please select an image under 10 MB.',
          );
        },
      );
      final mockInference = MockInferenceService();

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('choose_gallery_button')));
      await tester.pumpAndSettle();

      // Localized error message is displayed in SnackBar
      expect(
        find.textContaining('Image exceeds the 10 MB limit'),
        findsOneWidget,
      );
      expect(find.byKey(const Key('scan_error_snackbar_text')), findsOneWidget);

      // Result screen was NOT opened
      expect(find.byType(ResultScreen), findsNothing);

      // Scan screen is back in idle state
      expect(find.byKey(const Key('take_photo_button')), findsOneWidget);
      expect(find.text('Position diseased rice leaf in center'), findsOneWidget);
    });

    testWidgets(
        'Step 1 & 4c: Preprocessing error (unsupported format) displays localized message and stays on scan',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async {
          throw const InvalidImageFormatException(
            'Unsupported file format. Only JPG and PNG images are accepted.',
          );
        },
      );
      final mockInference = MockInferenceService();

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('choose_gallery_button')));
      await tester.pumpAndSettle();

      // Format error message is shown
      expect(
        find.textContaining('Unsupported file format. Only JPG and PNG'),
        findsOneWidget,
      );

      // Result screen was NOT opened
      expect(find.byType(ResultScreen), findsNothing);
    });

    testWidgets(
        'Bangla locale: Preprocessing error displays Bangla message and stays on scan',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'bn',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async {
          throw const ImageTooLargeException('Image exceeds the 10 MB limit');
        },
      );
      final mockInference = MockInferenceService();

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
          locale: const Locale('bn'),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('choose_gallery_button')));
      await tester.pumpAndSettle();

      // Localized Bangla error is shown
      expect(
        find.textContaining('ছবির সাইজ ১০ মেগাবাইটের বেশি'),
        findsOneWidget,
      );

      // Result screen was NOT opened
      expect(find.byType(ResultScreen), findsNothing);
    });

    testWidgets(
        'Step 3: Shutter button shows informative notice and does NOT produce a fake result',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService();
      final mockInference = MockInferenceService();

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      // Tap shutter button
      final shutterFinder = find.byKey(const Key('take_photo_button'));
      expect(shutterFinder, findsOneWidget);
      await tester.tap(shutterFinder);
      await tester.pumpAndSettle();

      // Shutter notice is shown explaining camera wire-up is pending T-063 follow-up
      expect(
        find.byKey(const Key('shutter_todo_message')),
        findsOneWidget,
      );
      expect(
        find.textContaining('Camera capture will be available in an upcoming update'),
        findsOneWidget,
      );

      // Result screen was NOT opened with any fake result
      expect(find.byType(ResultScreen), findsNothing);
    });

    testWidgets(
        'User cancels gallery selection: stays on scan in idle state with no errors',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async => null, // User cancelled
      );
      final mockInference = MockInferenceService();

      await tester.pumpWidget(
        createGalleryTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('choose_gallery_button')));
      await tester.pumpAndSettle();

      // Still on scan screen in idle state
      expect(find.byType(ResultScreen), findsNothing);
      expect(find.byKey(const Key('take_photo_button')), findsOneWidget);
      expect(find.byKey(const Key('scan_error_snackbar_text')), findsNothing);
    });
  });
}
