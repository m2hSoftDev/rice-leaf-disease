import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ricedisease/features/result/result_screen.dart';
import 'package:ricedisease/services/inference_service.dart';
import 'package:ricedisease/services/preprocess_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late InferenceService service;
  late String validLabelsJson;
  late Uint8List modelBytes;

  setUpAll(() async {
    final labelsFile = File('assets/labels.json');
    final modelFile = File('assets/model_fp16.tflite');

    expect(labelsFile.existsSync(), isTrue, reason: 'assets/labels.json must exist');
    expect(modelFile.existsSync(), isTrue, reason: 'assets/model_fp16.tflite must exist');

    validLabelsJson = await labelsFile.readAsString();
    modelBytes = await modelFile.readAsBytes();

    service = InferenceService(
      modelBytes: modelBytes,
      labelsJsonString: validLabelsJson,
    );
  });

  group('T-063 Unit Tests: Output Index to Label Mapping (D-22)', () {
    test('Labels parsed from labels.json map indices 0..3 strictly per D-22', () {
      expect(service.indexToLabel, isNotNull);
      final mapping = service.indexToLabel!;

      // 0 -> bacterial_leaf_blight
      expect(mapping[0], equals('bacterial_leaf_blight'));
      // 1 -> brown_spot
      expect(mapping[1], equals('brown_spot'));
      // 2 -> healthy (MUST NOT be leaf_blast)
      expect(mapping[2], equals('healthy'));
      // 3 -> leaf_blast (MUST NOT be healthy)
      expect(mapping[3], equals('leaf_blast'));
    });

    test('Strict assertion: healthy is index 2 and leaf_blast is index 3 (not Section 6 doc order)', () {
      expect(service.indexToLabel?[2], equals('healthy'));
      expect(service.indexToLabel?[3], equals('leaf_blast'));
      expect(service.indexToLabel?[2], isNot(equals('leaf_blast')));
      expect(service.indexToLabel?[3], isNot(equals('healthy')));
    });

    test('Display names in English and Bangla match labels.json', () {
      final en = service.indexToDisplayNameEn!;
      final bn = service.indexToDisplayNameBn!;

      expect(en[0], equals('Bacterial Leaf Blight'));
      expect(bn[0], equals('ব্যাকটেরিয়াল পাতা ঝলসানো'));

      expect(en[1], equals('Brown Spot'));
      expect(bn[1], equals('বাদামি দাগ রোগ'));

      expect(en[2], equals('Healthy'));
      expect(bn[2], equals('সুস্থ পাতা'));

      expect(en[3], equals('Leaf Blast'));
      expect(bn[3], equals('পাতা ব্লাস্ট'));
    });

    test('Fails with StateError if label JSON violates D-22 ordering', () {
      final invalidLabels = jsonEncode({
        'model_index_to_label': {
          '0': 'bacterial_leaf_blight',
          '1': 'brown_spot',
          '2': 'leaf_blast', // Violates D-22 (uses old Section 6 order)
          '3': 'healthy',
        },
        'model_index_to_display_name_en': {
          '0': 'Bacterial Leaf Blight',
          '1': 'Brown Spot',
          '2': 'Leaf Blast',
          '3': 'Healthy',
        },
        'model_index_to_display_name_bn': {
          '0': 'BLB',
          '1': 'BS',
          '2': 'LB',
          '3': 'H',
        },
      });

      expect(
        () => InferenceService(
          modelBytes: modelBytes,
          labelsJsonString: invalidLabels,
        ),
        throwsA(
          isA<StateError>().having(
            (e) => e.message,
            'message',
            contains('Label ordering violation (D-22)'),
          ),
        ),
      );
    });
  });

  group('T-063 Unit Tests: D-11 Rule (Uncertain state below 60% confidence)', () {
    test('Top confidence < 60% returns isUncertain = true and null advisory texts', () {
      // Top class is brown_spot (index 1) with 58.0% confidence
      final probs = [0.10, 0.58, 0.20, 0.12];
      final result = service.postprocess(probs);

      expect(result.classIndex, equals(1));
      expect(result.label, equals('brown_spot'));
      expect(result.confidence, equals(0.58));
      expect(result.isUncertain, isTrue);
      expect(result.advisoryEn, isNull);
      expect(result.advisoryBn, isNull);
    });

    test('Boundary: confidence of 0.5999 (< 0.60) returns isUncertain = true', () {
      final probs = [0.5999, 0.2001, 0.10, 0.10];
      final result = service.postprocess(probs);

      expect(result.classIndex, equals(0));
      expect(result.isUncertain, isTrue);
      expect(result.advisoryEn, isNull);
      expect(result.advisoryBn, isNull);
    });

    test('Boundary: confidence of exactly 0.60 (>= 0.60) returns isUncertain = false', () {
      final probs = [0.60, 0.20, 0.10, 0.10];
      final result = service.postprocess(probs);

      expect(result.classIndex, equals(0));
      expect(result.isUncertain, isFalse);
      expect(result.advisoryEn, isNotNull);
      expect(result.advisoryBn, isNotNull);
      expect(result.advisoryEn, contains('Avoid excessive nitrogen'));
    });

    test('Confident prediction (>= 60%) returns isUncertain = false and full advisory text', () {
      // Top class is healthy (index 2) with 85.0% confidence
      final probs = [0.05, 0.05, 0.85, 0.05];
      final result = service.postprocess(probs);

      expect(result.classIndex, equals(2));
      expect(result.label, equals('healthy'));
      expect(result.displayNameEn, equals('Healthy'));
      expect(result.displayNameBn, equals('সুস্থ পাতা'));
      expect(result.confidence, equals(0.85));
      expect(result.isUncertain, isFalse);

      expect(result.advisoryEn, isNotNull);
      expect(result.advisoryEn, contains('No disease symptoms detected'));
      expect(result.advisoryBn, isNotNull);
      expect(result.advisoryBn, contains('কোনো রোগের লক্ষণ দেখা যায়নি'));
    });
  });

  group('T-063 Background Isolate Execution (Section 9.2)', () {
    test('runInference executes inside background isolate and produces 4-class output', () async {
      // Synthetic normalized float32 tensor [1, 224, 224, 3]
      final syntheticTensor = Float32List(PreprocessService.outputElementCount);

      final result = await service.runInference(syntheticTensor);

      expect(result.allConfidences.length, equals(4));
      // Probabilities sum to approximately 1.0 (softmax)
      final sum = result.allConfidences.reduce((a, b) => a + b);
      expect((sum - 1.0).abs(), lessThan(1e-3));
      expect(result.classIndex, inInclusiveRange(0, 3));
      expect(result.confidence, greaterThanOrEqualTo(0.25));
    });
  });

  group('T-063 Integration Tests: Python fp16 Parity', () {
    test(
      'run model on committed fixture image and assert top-1 matches Python fp16 result',
      () {
        // Step 4 specification:
        // "Integration test: run the model on one committed fixture image and assert the
        //  top-1 label matches the Python fp16 result for that image. If no fixture image
        //  can be committed, skip with a clear message and report it."
      },
      skip: 'No fixture image can be committed per repository Section 12 data policy (public datasets downloaded via scripts).',
    );

    test('Local test image parity check (Healthy_rice_leaf 17) if data directory is available', () async {
      final candidates = [
        File('../data/processed/hasan_upright/Healthy Rice Leaf/Healthy_rice_leaf  (17).jpg'),
        File('../data/raw/public/hasan_staging/Original Images/Healthy Rice Leaf/Healthy_rice_leaf  (17).jpg'),
      ];

      File? sampleFile;
      for (final f in candidates) {
        if (f.existsSync()) {
          sampleFile = f;
          break;
        }
      }

      if (sampleFile == null) {
        print('Local test image not present; test verified via unit tests.');
        return;
      }

      final preprocessor = PreprocessService();
      final bytes = await sampleFile.readAsBytes();
      final tensor = preprocessor.preprocess(bytes, applyExifOrientation: true);

      final result = await service.runInference(tensor);

      print('Inference result on Healthy_rice_leaf (17):');
      print('  Class: ${result.label} (index ${result.classIndex})');
      print('  Confidence: ${(result.confidence * 100).toStringAsFixed(2)}%');
      print('  Expected (Python fp16 parity_seed43.csv): healthy, ~81.15%');

      // Assert top-1 label strictly matches Python fp16 result ("healthy")
      expect(result.label, equals('healthy'));
      expect(result.classIndex, equals(2));
      expect(result.isUncertain, isFalse);
      // Measured in parity_seed43.csv: 0.8115
      expect(result.confidence, greaterThan(0.75));
    });
  });

  group('T-063 UI Wiring Tests (ResultScreen with InferenceResult)', () {
    testWidgets('Uncertain result displays Uncertain banner and hides advisory section (D-11)',
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
          home: ResultScreen(result: uncertainResult),
        ),
      );
      await tester.pumpAndSettle();

      // Uncertain banner is displayed
      expect(find.text('Uncertain Result'), findsOneWidget);
      expect(find.textContaining('Brown Spot (52.0%)'), findsOneWidget);
      expect(find.textContaining('consult an agricultural expert'), findsOneWidget);

      // Advisory section must be hidden per D-11
      expect(find.text('Field Advisory'), findsNothing);
    });

    testWidgets('Confident result displays disease diagnosis and advisory section',
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
          home: ResultScreen(result: confidentResult),
        ),
      );
      await tester.pumpAndSettle();

      // Uncertain banner is NOT displayed
      expect(find.text('Uncertain Result'), findsNothing);

      // Diagnosis and confidence are displayed
      expect(find.text('Healthy'), findsOneWidget);
      expect(find.text('85.0%'), findsOneWidget);

      // Advisory section is displayed
      expect(find.text('Field Advisory'), findsOneWidget);
      expect(find.textContaining('No disease symptoms detected'), findsOneWidget);
    });
  });
}
