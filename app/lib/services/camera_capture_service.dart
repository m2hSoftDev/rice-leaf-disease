import 'dart:async';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

/// Result of a successful camera photo capture.
class CameraCaptureResult {
  final Uint8List bytes;
  final String path;

  const CameraCaptureResult({
    required this.bytes,
    required this.path,
  });
}

/// Base typed exception for camera-related operations.
abstract class CameraServiceException implements Exception {
  final String message;
  final String messageBn;

  const CameraServiceException(this.message, this.messageBn);

  String getLocalizedMessage(bool isBn) => isBn ? messageBn : message;

  @override
  String toString() => message;
}

/// Thrown when no camera hardware is detected on the device.
class NoCameraException extends CameraServiceException {
  const NoCameraException([
    String message = 'No suitable camera found on this device.',
    String messageBn = 'এই ডিভাইসে কোনো ক্যামেরা খুঁজে পাওয়া যায়নি।',
  ]) : super(message, messageBn);
}

/// Thrown when camera permission has been denied by the user or system policy.
class CameraPermissionDeniedException extends CameraServiceException {
  const CameraPermissionDeniedException([
    String message = 'Camera permission was denied. Please grant permission in settings.',
    String messageBn = 'ক্যামেরা ব্যবহারের অনুমতি দেওয়া হয়নি। অনুগ্রহ করে সেটিংসে গিয়ে অনুমতি দিন।',
  ]) : super(message, messageBn);
}

/// Thrown when the camera fails to initialize.
class CameraInitializationException extends CameraServiceException {
  const CameraInitializationException([
    String message = 'Failed to initialize camera.',
    String messageBn = 'ক্যামেরা চালু করতে ব্যর্থ হয়েছে।',
  ]) : super(message, messageBn);
}

/// Thrown when photo capture fails.
class CameraCaptureException extends CameraServiceException {
  const CameraCaptureException([
    String message = 'Failed to capture photo.',
    String messageBn = 'ছবি তুলতে ব্যর্থ হয়েছে।',
  ]) : super(message, messageBn);
}

/// Permission statuses for camera access.
enum CameraPermissionStatus {
  notGranted,
  granted,
  permanentlyDenied,
}

typedef PermissionStatusChecker = Future<CameraPermissionStatus> Function();
typedef CameraListProvider = Future<List<CameraDescription>> Function();
typedef CameraControllerFactory = CameraController Function(
  CameraDescription description,
  ResolutionPreset resolutionPreset, {
  bool enableAudio,
});

/// Service managing camera lifecycle, initialization, and photo capture.
/// Adheres to Section 9.5 (just-in-time permissions) and ResolutionPreset.high.
class CameraCaptureService with WidgetsBindingObserver {
  final CameraListProvider _cameraListProvider;
  final CameraControllerFactory _controllerFactory;
  final PermissionStatusChecker? _permissionChecker;

  CameraController? _controller;
  bool _isInitialized = false;
  bool _wasActive = false;
  bool _observerRegistered = false;

  CameraCaptureService({
    CameraListProvider? cameraListProvider,
    CameraControllerFactory? controllerFactory,
    PermissionStatusChecker? permissionChecker,
  })  : _cameraListProvider = cameraListProvider ?? availableCameras,
        _controllerFactory = controllerFactory ??
            ((description, preset, {enableAudio = false}) => CameraController(
                  description,
                  preset,
                  enableAudio: enableAudio,
                )),
        _permissionChecker = permissionChecker;

  CameraController? get controller => _controller;

  bool get isInitialized =>
      _isInitialized &&
      _controller != null &&
      _controller!.value.isInitialized;

  /// Checks whether camera permission is currently granted, not granted,
  /// or permanently denied.
  Future<CameraPermissionStatus> checkPermissionStatus() async {
    if (_permissionChecker != null) {
      return _permissionChecker!();
    }
    try {
      const channel =
          MethodChannel('com.m2hsoftdev.ricedisease/camera_permission');
      final status =
          await channel.invokeMethod<String>('checkCameraPermission');
      if (status == 'granted') {
        return CameraPermissionStatus.granted;
      } else if (status == 'permanentlyDenied') {
        return CameraPermissionStatus.permanentlyDenied;
      }
      return CameraPermissionStatus.notGranted;
    } catch (_) {
      // In non-Android or unit test environments without platform channel:
      if (isInitialized) {
        return CameraPermissionStatus.granted;
      }
      return CameraPermissionStatus.notGranted;
    }
  }

  /// Opens application settings on Android so the user can grant permission.
  Future<void> openAppSettings() async {
    try {
      const channel =
          MethodChannel('com.m2hsoftdev.ricedisease/camera_permission');
      await channel.invokeMethod<void>('openAppSettings');
    } catch (_) {
      // Ignore if unavailable
    }
  }

  /// Initializes the back camera using [ResolutionPreset.high] (1080p target).
  /// Registers [WidgetsBindingObserver] for app background/resume lifecycle handling.
  Future<void> initialize() async {
    _registerObserver();
    try {
      final cameras = await _cameraListProvider();
      if (cameras.isEmpty) {
        throw const NoCameraException();
      }

      // Select back-facing camera if available; otherwise first available
      final camera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      final ctrl = _controllerFactory(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
      );

      _controller = ctrl;
      await ctrl.initialize();
      _isInitialized = true;
      _wasActive = true;
    } on CameraException catch (e) {
      _controller?.dispose();
      _controller = null;
      _isInitialized = false;
      if (e.code == 'CameraAccessDenied' ||
          e.code == 'CameraAccessDeniedWithoutPrompt' ||
          e.code == 'CameraAccessRestricted') {
        throw const CameraPermissionDeniedException();
      }
      throw CameraInitializationException(
        e.description ?? 'Camera initialization failed (${e.code}).',
      );
    } catch (e) {
      _controller?.dispose();
      _controller = null;
      _isInitialized = false;
      if (e is CameraServiceException) rethrow;
      throw CameraInitializationException(
        'Failed to initialize camera: ${e.toString()}',
      );
    }
  }

  /// Captures a photo and returns raw unmodified bytes and file path.
  /// Does NOT re-encode, crop, or resize the bytes.
  Future<CameraCaptureResult> takePicture() async {
    if (!isInitialized || _controller == null) {
      throw const CameraCaptureException('Camera is not initialized.');
    }

    try {
      final xFile = await _controller!.takePicture();
      final bytes = await xFile.readAsBytes();
      return CameraCaptureResult(
        bytes: bytes,
        path: xFile.path,
      );
    } on CameraException catch (e) {
      throw CameraCaptureException(
        e.description ?? 'Capture failed (${e.code}).',
      );
    } catch (e) {
      if (e is CameraServiceException) rethrow;
      throw CameraCaptureException(
        'Failed to capture photo: ${e.toString()}',
      );
    }
  }

  void _registerObserver() {
    if (!_observerRegistered) {
      WidgetsBinding.instance.addObserver(this);
      _observerRegistered = true;
    }
  }

  void _unregisterObserver() {
    if (_observerRegistered) {
      WidgetsBinding.instance.removeObserver(this);
      _observerRegistered = false;
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_controller == null || !_isInitialized) {
      return;
    }

    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused) {
      _controller?.dispose();
      _controller = null;
      _isInitialized = false;
    } else if (state == AppLifecycleState.resumed) {
      if (_wasActive) {
        initialize().ignore();
      }
    }
  }

  /// Disposes camera controller and unregisters lifecycle observer.
  Future<void> dispose() async {
    _unregisterObserver();
    _wasActive = false;
    _isInitialized = false;
    final ctrl = _controller;
    _controller = null;
    await ctrl?.dispose();
  }
}
