import 'dart:convert';
import 'dart:io';
import 'dart:isolate';
import 'dart:typed_data';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

import 'preprocess_service.dart';

/// Result data model returned by [InferenceService].
///
/// Encapsulates model predictions, confidence scores, localized display names,
/// and low-confidence uncertain state handling under rule D-11.
class InferenceResult {
  /// Zero-based output class index corresponding to model output tensor [0..3].
  final int classIndex;

  /// Canonical label string from labels.json (e.g. 'healthy', 'leaf_blast').
  final String label;

  /// English display name from labels.json.
  final String displayNameEn;

  /// Bangla display name from labels.json.
  final String displayNameBn;

  /// Confidence score of winning class in [0.0, 1.0].
  final double confidence;

  /// Softmax probabilities for all 4 classes ordered by model index (0..3).
  final List<double> allConfidences;

  /// True if top confidence is below 60% (0.60) per rule D-11.
  final bool isUncertain;

  /// Localized advisory text in English. Null when [isUncertain] is true (D-11).
  final String? advisoryEn;

  /// Localized advisory text in Bangla. Null when [isUncertain] is true (D-11).
  final String? advisoryBn;

  const InferenceResult({
    required this.classIndex,
    required this.label,
    required this.displayNameEn,
    required this.displayNameBn,
    required this.confidence,
    required this.allConfidences,
    required this.isUncertain,
    this.advisoryEn,
    this.advisoryBn,
  });

  @override
  String toString() {
    return 'InferenceResult(label: $label, index: $classIndex, '
        'confidence: ${(confidence * 100).toStringAsFixed(2)}%, uncertain: $isUncertain)';
  }
}

/// On-device TFLite inference service for rice leaf disease detection.
///
/// Specifications:
/// - Loads `model_fp16.tflite` (canonical Seed 43 export) and `labels.json`.
/// - Strictly maps output indices via `labels.json` per D-22:
///     0 -> bacterial_leaf_blight
///     1 -> brown_spot
///     2 -> healthy
///     3 -> leaf_blast
/// - Runs inference in a background isolate to keep UI responsive (Section 9.2).
/// - Enforces D-11 low-confidence rule: if top confidence < 60%, returns uncertain state
///   with no advisory text.
class InferenceService {
  static const String defaultModelPath = 'assets/model_fp16.tflite';
  static const String defaultLabelsPath = 'assets/labels.json';

  /// D-11 threshold: predictions strictly below 60% are flagged as uncertain
  static const double confidenceThreshold = 0.60;

  /// Standard field advisory texts per Section 6 (English)
  static const Map<String, String> defaultAdvisoriesEn = {
    'bacterial_leaf_blight':
        'Avoid excessive nitrogen fertilizer; ensure proper field drainage; consult an agricultural extension officer.',
    'brown_spot':
        'Apply balanced fertilizer (NPK); use certified disease-free seeds; consult an agricultural extension officer.',
    'healthy':
        'No disease symptoms detected; keep monitoring crop regularly.',
    'leaf_blast':
        'Monitor humidity; use resistant varieties; reduce excessive nitrogen; consult an agricultural extension officer.',
  };

  /// Standard field advisory texts per Section 6 (Bangla)
  static const Map<String, String> defaultAdvisoriesBn = {
    'bacterial_leaf_blight':
        'অতিরিক্ত নাইট্রোজেন সার পরিহার করুন; জমিতে পরিমিত পানি নিষ্কাশন নিশ্চিত করুন; কৃষি কর্মকর্তার পরামর্শ নিন।',
    'brown_spot':
        'সুষম সার (এনপিকে) ব্যবহার করুন; রোগমুক্ত শোধিত বীজ ব্যবহার করুন; কৃষি কর্মকর্তার পরামর্শ নিন।',
    'healthy':
        'কোনো রোগের লক্ষণ দেখা যায়নি; নিয়মিত পর্যবেক্ষণ চালিয়ে যান।',
    'leaf_blast':
        'আর্দ্রতা পর্যবেক্ষণ করুন; প্রতিরোধী জাত ব্যবহার করুন; অতিরিক্ত নাইট্রোজেন কমান; কৃষি কর্মকর্তার পরামর্শ নিন।',
  };

  Uint8List? _modelBytes;
  Map<int, String>? _indexToLabel;
  Map<int, String>? _indexToDisplayNameEn;
  Map<int, String>? _indexToDisplayNameBn;
  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;
  Map<int, String>? get indexToLabel =>
      _indexToLabel == null ? null : Map.unmodifiable(_indexToLabel!);
  Map<int, String>? get indexToDisplayNameEn =>
      _indexToDisplayNameEn == null ? null : Map.unmodifiable(_indexToDisplayNameEn!);
  Map<int, String>? get indexToDisplayNameBn =>
      _indexToDisplayNameBn == null ? null : Map.unmodifiable(_indexToDisplayNameBn!);

  InferenceService({
    Uint8List? modelBytes,
    String? labelsJsonString,
  }) {
    if (modelBytes != null && labelsJsonString != null) {
      _initFromData(modelBytes, labelsJsonString);
    }
  }

  /// Initializes the service by loading model assets and parsing `labels.json`.
  Future<void> initialize({
    String modelPath = defaultModelPath,
    String labelsPath = defaultLabelsPath,
  }) async {
    if (_isInitialized) return;

    Uint8List modelBytes;
    String labelsJsonString;

    try {
      final byteData = await rootBundle.load(modelPath);
      modelBytes = byteData.buffer.asUint8List();
      labelsJsonString = await rootBundle.loadString(labelsPath);
    } catch (_) {
      // Fallback for tests or non-Flutter host runners where assets are on disk
      final modelFile = File(modelPath);
      final labelsFile = File(labelsPath);
      if (modelFile.existsSync() && labelsFile.existsSync()) {
        modelBytes = await modelFile.readAsBytes();
        labelsJsonString = await labelsFile.readAsString();
      } else {
        rethrow;
      }
    }

    _initFromData(modelBytes, labelsJsonString);
  }

  void _initFromData(Uint8List modelBytes, String labelsJsonString) {
    _modelBytes = modelBytes;
    _parseLabels(labelsJsonString);
    _isInitialized = true;
  }

  /// Parses labels from `labels.json` and strictly enforces D-22 ordering.
  void _parseLabels(String labelsJsonString) {
    final Map<String, dynamic> data =
        jsonDecode(labelsJsonString) as Map<String, dynamic>;

    final Map<String, dynamic> indexToLabelMap =
        data['model_index_to_label'] as Map<String, dynamic>;
    final Map<String, dynamic> indexToEnMap =
        data['model_index_to_display_name_en'] as Map<String, dynamic>;
    final Map<String, dynamic> indexToBnMap =
        data['model_index_to_display_name_bn'] as Map<String, dynamic>;

    _indexToLabel = {};
    _indexToDisplayNameEn = {};
    _indexToDisplayNameBn = {};

    for (final entry in indexToLabelMap.entries) {
      final idx = int.parse(entry.key);
      _indexToLabel![idx] = entry.value as String;
    }
    for (final entry in indexToEnMap.entries) {
      final idx = int.parse(entry.key);
      _indexToDisplayNameEn![idx] = entry.value as String;
    }
    for (final entry in indexToBnMap.entries) {
      final idx = int.parse(entry.key);
      _indexToDisplayNameBn![idx] = entry.value as String;
    }

    // Explicit D-22 contract validation
    if (_indexToLabel![2] != 'healthy' || _indexToLabel![3] != 'leaf_blast') {
      throw StateError(
        'Label ordering violation (D-22): expected index 2="healthy" and index 3="leaf_blast", '
        'got index 2="${_indexToLabel![2]}" and index 3="${_indexToLabel![3]}". '
        'Do NOT use Section 6 table order.',
      );
    }
  }

  /// Runs TFLite inference on a preprocessed input tensor `[1, 224, 224, 3]`.
  ///
  /// Inference executes in a background isolate using [Isolate.run] so the UI
  /// event loop remains completely responsive (Section 9.2).
  Future<InferenceResult> runInference(Float32List inputTensor) async {
    if (!_isInitialized) {
      await initialize();
    }
    if (inputTensor.length != PreprocessService.outputElementCount) {
      throw ArgumentError(
        'Expected inputTensor length of ${PreprocessService.outputElementCount} (1*224*224*3), '
        'got ${inputTensor.length}',
      );
    }

    final modelBytes = _modelBytes!;

    // Execute TFLite interpreter inside background isolate
    final List<double> probabilities = await Isolate.run(() {
      final interpreter = Interpreter.fromBuffer(modelBytes);
      final outputBuffer = Float32List(4).reshape([1, 4]);
      interpreter.run(
        inputTensor.reshape([1, PreprocessService.targetHeight, PreprocessService.targetWidth, 3]),
        outputBuffer,
      );
      interpreter.close();

      final rawList = (outputBuffer as List)[0];
      return (rawList as List).map((e) => (e as num).toDouble()).toList();
    });

    return postprocess(probabilities);
  }

  /// Convenience method that runs preprocessing followed by background inference.
  Future<InferenceResult> runInferenceOnBytes(
    Uint8List imageBytes, {
    PreprocessService? preprocessService,
  }) async {
    final preprocessor = preprocessService ?? PreprocessService();
    final inputTensor = preprocessor.preprocess(imageBytes);
    return runInference(inputTensor);
  }

  /// Maps raw probability vector to [InferenceResult] applying D-11 and D-22 rules.
  InferenceResult postprocess(List<double> probabilities) {
    if (!_isInitialized) {
      throw StateError(
        'InferenceService has not been initialized. Call initialize() first.',
      );
    }
    if (probabilities.length != 4) {
      throw ArgumentError(
        'Expected 4 class probabilities, got ${probabilities.length}',
      );
    }

    int topIndex = 0;
    double topConfidence = probabilities[0];
    for (int i = 1; i < probabilities.length; i++) {
      if (probabilities[i] > topConfidence) {
        topConfidence = probabilities[i];
        topIndex = i;
      }
    }

    final label = _indexToLabel![topIndex]!;
    final displayNameEn = _indexToDisplayNameEn![topIndex]!;
    final displayNameBn = _indexToDisplayNameBn![topIndex]!;

    // D-11 rule: if top confidence < 60% (0.60), flag uncertain and omit advisory text
    final isUncertain = topConfidence < confidenceThreshold;

    return InferenceResult(
      classIndex: topIndex,
      label: label,
      displayNameEn: displayNameEn,
      displayNameBn: displayNameBn,
      confidence: topConfidence,
      allConfidences: List<double>.unmodifiable(probabilities),
      isUncertain: isUncertain,
      advisoryEn: isUncertain ? null : defaultAdvisoriesEn[label],
      advisoryBn: isUncertain ? null : defaultAdvisoriesBn[label],
    );
  }
}

/// Riverpod provider for [InferenceService].
final inferenceServiceProvider = Provider<InferenceService>((ref) {
  return InferenceService();
});
