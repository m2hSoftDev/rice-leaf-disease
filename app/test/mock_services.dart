import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:ricedisease/services/inference_service.dart';
import 'package:ricedisease/services/preprocess_service.dart';

/// Mock implementation of [PreprocessService] for widget and integration tests.
class MockPreprocessService extends PreprocessService {
  final Future<XFile?> Function({required ImageSource source})? onPickImage;
  final Float32List Function(Uint8List bytes)? onPreprocess;

  MockPreprocessService({
    this.onPickImage,
    this.onPreprocess,
  });

  @override
  Future<XFile?> pickImage({required ImageSource source}) async {
    if (onPickImage != null) {
      return onPickImage!(source: source);
    }
    return super.pickImage(source: source);
  }

  @override
  Float32List preprocess(
    Uint8List bytes, {
    bool applyExifOrientation = true,
    String? filename,
  }) {
    if (onPreprocess != null) {
      return onPreprocess!(bytes);
    }
    return Float32List(PreprocessService.outputElementCount);
  }
}

/// Mock implementation of [InferenceService] for widget and integration tests.
class MockInferenceService extends InferenceService {
  final Future<InferenceResult> Function(Float32List inputTensor)?
      onRunInference;

  MockInferenceService({this.onRunInference});

  @override
  Future<InferenceResult> runInference(Float32List inputTensor) async {
    if (onRunInference != null) {
      return onRunInference!(inputTensor);
    }
    return super.runInference(inputTensor);
  }
}
