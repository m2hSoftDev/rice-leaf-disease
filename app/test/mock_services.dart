import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:ricedisease/services/camera_capture_service.dart';
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

/// Mock implementation of [CameraCaptureService] for widget and integration tests.
class MockCameraCaptureService extends CameraCaptureService {
  final Future<void> Function()? onInitialize;
  final Future<CameraCaptureResult> Function()? onTakePicture;
  final Future<void> Function()? onDispose;
  bool mockIsInitialized;
  CameraController? mockController;

  MockCameraCaptureService({
    this.onInitialize,
    this.onTakePicture,
    this.onDispose,
    this.mockIsInitialized = false,
    this.mockController,
  });

  @override
  bool get isInitialized => mockIsInitialized;

  @override
  CameraController? get controller => mockController;

  @override
  Future<void> initialize() async {
    if (onInitialize != null) {
      await onInitialize!();
      return;
    }
    mockIsInitialized = true;
  }

  @override
  Future<CameraCaptureResult> takePicture() async {
    if (onTakePicture != null) {
      return onTakePicture!();
    }
    return CameraCaptureResult(
      bytes: Uint8List.fromList([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
        0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
        0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
      ]),
      path: '/mock/path/camera_photo.png',
    );
  }

  @override
  Future<void> dispose() async {
    if (onDispose != null) {
      await onDispose!();
    }
    mockIsInitialized = false;
  }
}
