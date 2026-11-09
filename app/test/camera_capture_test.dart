import 'dart:convert';
import 'dart:typed_data';

import 'package:camera/camera.dart';
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
import 'package:ricedisease/features/scan/session_scan_record.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/services/camera_capture_service.dart';
import 'package:ricedisease/services/inference_service.dart';
import 'package:ricedisease/services/preprocess_service.dart';

import 'mock_services.dart';

Widget createCameraTestApp({
  required SharedPreferences prefs,
  required MockPreprocessService preprocessService,
  required MockInferenceService inferenceService,
  required MockCameraCaptureService cameraService,
  CaptureState initialState = CaptureState.idle,
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
      home: ScanScreen(
        initialState: initialState,
        preprocessService: preprocessService,
        inferenceService: inferenceService,
        cameraCaptureService: cameraService,
      ),
    ),
  );
}

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  group('T-063 Follow-up Unit Tests: CameraCaptureService', () {
    test('Throws NoCameraException when no cameras are discovered on device', () async {
      final service = CameraCaptureService(
        cameraListProvider: () async => <CameraDescription>[],
      );

      expect(
        () => service.initialize(),
        throwsA(isA<NoCameraException>()),
      );
    });

    test('Maps CameraException CameraAccessDenied to CameraPermissionDeniedException', () async {
      final service = CameraCaptureService(
        cameraListProvider: () async => [
          const CameraDescription(
            name: 'mock_back_camera',
            lensDirection: CameraLensDirection.back,
            sensorOrientation: 90,
          ),
        ],
        controllerFactory: (desc, preset, {enableAudio = false}) {
          throw CameraException('CameraAccessDenied', 'Permission was denied by user');
        },
      );

      expect(
        () => service.initialize(),
        throwsA(isA<CameraPermissionDeniedException>()),
      );
    });

    test('Maps generic CameraException to CameraInitializationException', () async {
      final service = CameraCaptureService(
        cameraListProvider: () async => [
          const CameraDescription(
            name: 'mock_back_camera',
            lensDirection: CameraLensDirection.back,
            sensorOrientation: 90,
          ),
        ],
        controllerFactory: (desc, preset, {enableAudio = false}) {
          throw CameraException('HardwareError', 'Failed to acquire camera service');
        },
      );

      expect(
        () => service.initialize(),
        throwsA(isA<CameraInitializationException>()),
      );
    });

    test('takePicture throws CameraCaptureException when service is uninitialized', () async {
      final service = CameraCaptureService(
        cameraListProvider: () async => <CameraDescription>[],
      );

      expect(
        () => service.takePicture(),
        throwsA(isA<CameraCaptureException>()),
      );
    });

    test('computeSha256 produces exact FIPS 180-4 digests', () {
      final emptyDigest = computeSha256(Uint8List(0));
      expect(emptyDigest, equals('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'));

      final abcDigest = computeSha256(Uint8List.fromList(utf8.encode('abc')));
      expect(abcDigest, equals('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'));
    });

    test('SessionScanRecord.create records filename, byteSize, sha256, and result in memory', () {
      final testBytes = Uint8List.fromList([1, 2, 3, 4, 5]);
      const testResult = InferenceResult(
        classIndex: 2,
        label: 'healthy',
        displayNameEn: 'Healthy',
        displayNameBn: 'সুস্থ পাতা',
        confidence: 0.95,
        allConfidences: [0.01, 0.02, 0.95, 0.02],
        isUncertain: false,
        advisoryEn: 'Plant is healthy.',
        advisoryBn: 'গাছ সুস্থ আছে।',
      );

      final record = SessionScanRecord.create(
        filename: 'leaf_photo.jpg',
        bytes: testBytes,
        result: testResult,
      );

      expect(record.filename, equals('leaf_photo.jpg'));
      expect(record.byteSize, equals(5));
      expect(record.sha256, equals(computeSha256(testBytes)));
      expect(record.result, equals(testResult));

      SessionScanStore.addRecord(record);
      expect(SessionScanStore.records.contains(record), isTrue);
    });
  });

  group('T-063 Follow-up Widget Tests: Live Camera Capture Flow', () {
    testWidgets(
        'With fake camera service: tapping shutter shows photoSelected state, Retake returns to preview',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService();
      final mockInference = MockInferenceService();
      final mockCamera = MockCameraCaptureService(mockIsInitialized: true);

      await tester.pumpWidget(
        createCameraTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
          cameraService: mockCamera,
        ),
      );
      await tester.pumpAndSettle();

      // Tap shutter to take picture
      final shutterFinder = find.byKey(const Key('take_photo_button'));
      expect(shutterFinder, findsOneWidget);
      await tester.tap(shutterFinder);
      await tester.pumpAndSettle();

      // Enters Photo Selected state: Analyze Leaf and Retake buttons are visible
      expect(find.byKey(const Key('scan_analyze_button')), findsOneWidget);
      expect(find.byKey(const Key('scan_retake_button')), findsOneWidget);
      expect(find.byKey(const Key('frozen_captured_photo')), findsOneWidget);

      // ResultScreen is NOT opened automatically
      expect(find.byType(ResultScreen), findsNothing);

      // Tap Retake
      await tester.tap(find.byKey(const Key('scan_retake_button')));
      await tester.pumpAndSettle();

      // Returns to idle preview state: Analyze button is gone, shutter is enabled
      expect(find.byKey(const Key('scan_analyze_button')), findsNothing);
      expect(find.byKey(const Key('take_photo_button')), findsOneWidget);
      expect(find.byKey(const Key('frozen_captured_photo')), findsNothing);
    });

    testWidgets(
        'With fake camera service: tapping shutter then Analyze opens ResultScreen with mocked result',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      const mockResult = InferenceResult(
        classIndex: 1,
        label: 'brown_spot',
        displayNameEn: 'Brown Spot',
        displayNameBn: 'বাদামি দাগ রোগ',
        confidence: 0.88,
        allConfidences: [0.05, 0.88, 0.04, 0.03],
        isUncertain: false,
        advisoryEn: 'Maintain balanced fertilizer application.',
        advisoryBn: 'সুষম সার ব্যবহার করুন।',
      );

      final mockPreprocess = MockPreprocessService(
        onPreprocess: (bytes) => Float32List(PreprocessService.outputElementCount),
      );
      final mockInference = MockInferenceService(
        onRunInference: (tensor) async => mockResult,
      );
      final mockCamera = MockCameraCaptureService(mockIsInitialized: true);

      await tester.pumpWidget(
        createCameraTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
          cameraService: mockCamera,
        ),
      );
      await tester.pumpAndSettle();

      // Tap shutter to take picture
      await tester.tap(find.byKey(const Key('take_photo_button')));
      await tester.pumpAndSettle();

      // Tap Analyze
      await tester.tap(find.byKey(const Key('scan_analyze_button')));
      await tester.pumpAndSettle();

      // ResultScreen opens displaying mocked prediction
      expect(find.byType(ResultScreen), findsOneWidget);
      expect(find.text('Brown Spot'), findsWidgets);
      expect(find.textContaining('88.0%'), findsOneWidget);
    });

    testWidgets(
        'Permission denied state: shows camera-off icon, Open Settings button, and active gallery button',
        (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        PrefKeys.onboardingDone: true,
        PrefKeys.selectedLocale: 'en',
      });
      final prefs = await SharedPreferences.getInstance();

      final mockPreprocess = MockPreprocessService(
        onPickImage: ({required source}) async => XFile.fromData(
          Uint8List.fromList([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
            0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
            0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
          ]),
          name: 'gallery_test.png',
        ),
      );
      final mockInference = MockInferenceService(
        onRunInference: (tensor) async => const InferenceResult(
          classIndex: 2,
          label: 'healthy',
          displayNameEn: 'Healthy',
          displayNameBn: 'সুস্থ পাতা',
          confidence: 0.92,
          allConfidences: [0.02, 0.03, 0.92, 0.03],
          isUncertain: false,
          advisoryEn: 'Healthy plant.',
          advisoryBn: 'সুস্থ পাতা।',
        ),
      );
      final mockCamera = MockCameraCaptureService(mockIsInitialized: false);

      await tester.pumpWidget(
        createCameraTestApp(
          prefs: prefs,
          preprocessService: mockPreprocess,
          inferenceService: mockInference,
          cameraService: mockCamera,
          initialState: CaptureState.permissionDenied,
        ),
      );
      await tester.pumpAndSettle();

      // Permission denied UI elements are visible
      expect(find.byIcon(Icons.no_photography_outlined), findsOneWidget);
      expect(find.byKey(const Key('open_settings_button')), findsOneWidget);
      expect(find.text('Camera Access Needed'), findsOneWidget);

      // Gallery button is present and highlighted
      final galleryFinder = find.byKey(const Key('choose_gallery_button'));
      expect(galleryFinder, findsOneWidget);

      // Tap gallery button: picking photos remains fully functional
      await tester.tap(galleryFinder);
      await tester.pumpAndSettle();

      expect(find.byType(ResultScreen), findsOneWidget);
      expect(find.text('Healthy'), findsWidgets);
    });
  });
}
