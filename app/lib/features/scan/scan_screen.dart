import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:ricedisease/app/providers.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/features/scan/session_scan_record.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/services/camera_capture_service.dart';
import 'package:ricedisease/services/inference_service.dart';
import 'package:ricedisease/services/preprocess_service.dart';
import 'package:ricedisease/widgets/disclaimer_card.dart';

/// Distinct states for the capture page.
enum CaptureState {
  idle,
  permissionDenied,
  photoSelected,
  analyzing,
}

/// Capture page (Scan) adhering to Material 3 full-bleed layout,
/// docs/design/ui_spec.md Section 4.3, and Decision D-30 live camera capture.
class ScanScreen extends ConsumerStatefulWidget {
  final CaptureState initialState;
  final PreprocessService? preprocessService;
  final InferenceService? inferenceService;
  final CameraCaptureService? cameraCaptureService;

  const ScanScreen({
    super.key,
    this.initialState = CaptureState.idle,
    this.preprocessService,
    this.inferenceService,
    this.cameraCaptureService,
  });

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  late CaptureState _currentState;
  CameraCaptureService? _internalCameraService;
  Uint8List? _capturedBytes;
  String? _capturedPath;

  CameraCaptureService get _cameraService =>
      widget.cameraCaptureService ??
      (_internalCameraService ??= CameraCaptureService());

  PreprocessService get _preprocessService =>
      widget.preprocessService ?? ref.read(preprocessServiceProvider);

  InferenceService get _inferenceService =>
      widget.inferenceService ?? ref.read(inferenceServiceProvider);

  @override
  void initState() {
    super.initState();
    _currentState = widget.initialState;
  }

  @override
  void dispose() {
    _internalCameraService?.dispose();
    super.dispose();
  }

  /// Just-in-time camera initialization (Section 9.5).
  /// Not called on startup; only invoked when user interacts with shutter or viewfinder.
  Future<void> _initializeCamera() async {
    try {
      await _cameraService.initialize();
      if (!mounted) return;
      setState(() {});
    } on CameraPermissionDeniedException {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.permissionDenied;
      });
    } on CameraServiceException catch (e) {
      if (!mounted) return;
      final isBn = Localizations.localeOf(context).languageCode == 'bn';
      _showErrorSnackBar(e.getLocalizedMessage(isBn));
    } catch (e) {
      if (!mounted) return;
      _showErrorSnackBar(e.toString());
    }
  }

  /// Shutter tap handler.
  /// If camera is not yet initialized, initializes it (just-in-time permission).
  /// If camera is ready, captures raw photo and displays photo-selected state.
  Future<void> _onShutterTap() async {
    if (_currentState == CaptureState.permissionDenied ||
        _currentState == CaptureState.analyzing) {
      return;
    }

    if (!_cameraService.isInitialized) {
      await _initializeCamera();
      return;
    }

    try {
      final capture = await _cameraService.takePicture();
      if (!mounted) return;
      setState(() {
        _capturedBytes = capture.bytes;
        _capturedPath = capture.path;
        _currentState = CaptureState.photoSelected;
      });
    } on CameraServiceException catch (e) {
      if (!mounted) return;
      final isBn = Localizations.localeOf(context).languageCode == 'bn';
      _showErrorSnackBar(e.getLocalizedMessage(isBn));
    } catch (e) {
      if (!mounted) return;
      _showErrorSnackBar(e.toString());
    }
  }

  /// Tapping the preview placeholder area initializes camera just-in-time.
  void _onPreviewTap() {
    if (!_cameraService.isInitialized && _currentState == CaptureState.idle) {
      _initializeCamera();
    }
  }

  /// Gallery photo picker flow.
  Future<void> _onGalleryTap() async {
    if (_currentState == CaptureState.analyzing) {
      return;
    }

    try {
      final xFile =
          await _preprocessService.pickImage(source: ImageSource.gallery);
      if (xFile == null) {
        return;
      }

      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.analyzing;
      });

      final bytes = await xFile.readAsBytes();
      final inputTensor = _preprocessService.preprocess(bytes);
      final result = await _inferenceService.runInference(inputTensor);

      final record = SessionScanRecord.create(
        filename: xFile.name,
        bytes: bytes,
        result: result,
      );
      SessionScanStore.addRecord(record);

      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });

      Navigator.of(context).pushNamed(
        AppRoutes.result,
        arguments: result,
      );
    } on ImageTooLargeException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } on InvalidImageFormatException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } on ImageDecodeException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    }
  }

  /// Analyze button tapped from Photo Selected state.
  /// Runs preprocessing and inference on the captured bytes,
  /// creates session record, and opens ResultScreen.
  Future<void> _onAnalyzeTap() async {
    if (_capturedBytes == null) {
      setState(() {
        _currentState = CaptureState.idle;
      });
      return;
    }

    final bytes = _capturedBytes!;
    final path = _capturedPath;

    setState(() {
      _currentState = CaptureState.analyzing;
    });

    try {
      final inputTensor = _preprocessService.preprocess(bytes);
      final result = await _inferenceService.runInference(inputTensor);

      final filename = (path != null && path.isNotEmpty)
          ? path.split(RegExp(r'[/\\]')).last
          : 'camera_capture.jpg';

      final record = SessionScanRecord.create(
        filename: filename,
        bytes: bytes,
        result: result,
      );
      SessionScanStore.addRecord(record);

      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
        _capturedBytes = null;
        _capturedPath = null;
      });

      Navigator.of(context).pushNamed(
        AppRoutes.result,
        arguments: result,
      );
    } on ImageTooLargeException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } on InvalidImageFormatException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } on ImageDecodeException catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _currentState = CaptureState.idle;
      });
      _showErrorSnackBar(_getLocalizedErrorMessage(e));
    }
  }

  /// Retake button: discards captured photo and returns to live preview.
  void _onRetakeTap() {
    setState(() {
      _capturedBytes = null;
      _capturedPath = null;
      _currentState = CaptureState.idle;
    });
  }

  String _getLocalizedErrorMessage(Object error) {
    final isBn = Localizations.localeOf(context).languageCode == 'bn';
    if (error is ImageTooLargeException) {
      return isBn
          ? 'ছবির সাইজ ১০ মেগাবাইটের বেশি। অনুগ্রহ করে ১০ মেগাবাইটের কম সাইজের ছবি নির্বাচন করুন।'
          : error.message;
    }
    if (error is InvalidImageFormatException) {
      return isBn
          ? 'অসমর্থিত ফাইল ফরম্যাট। শুধুমাত্র JPG এবং PNG ছবি সমর্থিত।'
          : error.message;
    }
    if (error is ImageDecodeException) {
      return isBn
          ? 'ছবি ডিকোড করতে ব্যর্থ হয়েছে। অনুগ্রহ করে পরিষ্কার ছবি নির্বাচন করুন।'
          : error.message;
    }
    return isBn
        ? 'ছবি প্রক্রিয়া করতে ত্রুটি হয়েছে: ${error.toString()}'
        : 'Error processing image: ${error.toString()}';
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          message,
          key: const Key('scan_error_snackbar_text'),
        ),
        backgroundColor: Theme.of(context).colorScheme.error,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _onHelpTap() {
    final l10n = AppLocalizations.of(context);
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n?.helpLabel ?? 'Help'),
        content: Text(
          l10n?.viewfinderInstruction ??
              'Position diseased rice leaf in center under natural daylight for best accuracy.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(l10n?.cancel ?? 'Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Preview Area: Frozen photo, CameraPreview, or Placeholder
          _buildPreviewContent(theme),

          // 2. Viewfinder with corner brackets and guidance instruction
          if (_currentState != CaptureState.permissionDenied)
            Align(
              alignment: isLandscape
                  ? const Alignment(-0.3, 0)
                  : const Alignment(0, -0.1),
              child: _buildViewfinder(theme, l10n),
            ),

          // 3. Permission Denied Overlay State
          if (_currentState == CaptureState.permissionDenied)
            Center(
              child: _buildPermissionDeniedCard(theme, l10n),
            ),

          // 4. Analyzing Overlay State
          if (_currentState == CaptureState.analyzing)
            Container(
              color: Colors.black54,
              child: Center(
                child: _buildAnalyzingIndicator(theme, l10n),
              ),
            ),

          // 5. Photo Selected Action Card Overlay
          if (_currentState == CaptureState.photoSelected)
            Align(
              alignment: isLandscape
                  ? const Alignment(-0.3, 0.7)
                  : const Alignment(0, 0.45),
              child: _buildPhotoSelectedCard(theme, l10n),
            ),

          // 6. Top App Bar with gradient scrim
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: _buildTopScrimAppBar(theme, l10n),
          ),

          // 7. Bottom Controls & Disclaimer (Portrait vs Landscape Docking)
          if (!isLandscape)
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: SafeArea(
                top: false,
                child: _buildPortraitControls(theme, l10n),
              ),
            )
          else ...[
            Positioned(
              bottom: 12,
              left: 16,
              right: 160,
              child: const SafeArea(
                child: DisclaimerCard(isCompact: true),
              ),
            ),
            Positioned(
              top: 56,
              bottom: 0,
              right: 0,
              child: SafeArea(
                left: false,
                child: _buildLandscapeControls(theme, l10n),
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Builds preview content: frozen photo in photoSelected state,
  /// live CameraPreview when controller is ready, or interactive placeholder.
  Widget _buildPreviewContent(ThemeData theme) {
    if (_currentState == CaptureState.photoSelected && _capturedBytes != null) {
      return Image.memory(
        _capturedBytes!,
        key: const Key('frozen_captured_photo'),
        fit: BoxFit.cover,
        width: double.infinity,
        height: double.infinity,
        errorBuilder: (context, error, stackTrace) =>
            _buildPreviewPlaceholder(theme),
      );
    }

    if (_cameraService.isInitialized && _cameraService.controller != null) {
      return CameraPreview(
        _cameraService.controller!,
        key: const Key('camera_live_preview'),
      );
    }

    return GestureDetector(
      key: const Key('preview_placeholder_detector'),
      onTap: _onPreviewTap,
      child: _buildPreviewPlaceholder(theme),
    );
  }

  /// Full-bleed preview placeholder (Section 2.1 zero animated backgrounds).
  Widget _buildPreviewPlaceholder(ThemeData theme) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        gradient: RadialGradient(
          center: Alignment.center,
          radius: 1.2,
          colors: [
            Colors.green.shade900.withOpacity(0.35),
            Colors.black,
          ],
        ),
      ),
      child: Center(
        child: Opacity(
          opacity: 0.15,
          child: Icon(
            Icons.energy_savings_leaf,
            size: 220,
            color: theme.colorScheme.primary,
          ),
        ),
      ),
    );
  }

  /// Top App Bar with gradient scrim over preview.
  Widget _buildTopScrimAppBar(ThemeData theme, AppLocalizations? l10n) {
    final currentLocale = ref.watch(localeProvider);
    final toggleTooltip = currentLocale.languageCode == 'en'
        ? (l10n?.switchToBangla ?? 'বাংলায় দেখুন')
        : (l10n?.switchToEnglish ?? 'View in English');

    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xCC000000),
            Colors.transparent,
          ],
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      l10n?.appTitle ?? 'Rice Leaf Disease Detection',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      l10n?.homeTitle ?? 'Home Screen',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
              // Language toggle button (48 dp minimum touch target)
              Semantics(
                button: true,
                label: toggleTooltip,
                child: Tooltip(
                  message: toggleTooltip,
                  child: Material(
                    color: Colors.white.withOpacity(0.15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                      side: const BorderSide(color: Colors.white30, width: 1),
                    ),
                    child: InkWell(
                      key: const Key('language_toggle_button'),
                      borderRadius: BorderRadius.circular(24),
                      onTap: () {
                        ref.read(localeProvider.notifier).toggleLocale();
                      },
                      child: Container(
                        height: 48,
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        alignment: Alignment.center,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.translate,
                              size: 18,
                              color: Colors.white,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              currentLocale.languageCode == 'en'
                                  ? (l10n?.switchToBangla ?? 'বাংলায় দেখুন')
                                  : (l10n?.switchToEnglish ?? 'View in English'),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 260x260 dp centered viewfinder frame with corner brackets and guidance chip.
  Widget _buildViewfinder(ThemeData theme, AppLocalizations? l10n) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 260,
          height: 260,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.white.withOpacity(0.6),
              width: 2,
            ),
          ),
          child: Stack(
            children: [
              // Top-left corner
              Align(
                alignment: Alignment.topLeft,
                child: Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    border: Border(
                      top: BorderSide(color: Colors.white, width: 4),
                      left: BorderSide(color: Colors.white, width: 4),
                    ),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(16),
                    ),
                  ),
                ),
              ),
              // Top-right corner
              Align(
                alignment: Alignment.topRight,
                child: Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    border: Border(
                      top: BorderSide(color: Colors.white, width: 4),
                      right: BorderSide(color: Colors.white, width: 4),
                    ),
                    borderRadius: BorderRadius.only(
                      topRight: Radius.circular(16),
                    ),
                  ),
                ),
              ),
              // Bottom-left corner
              Align(
                alignment: Alignment.bottomLeft,
                child: Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: Colors.white, width: 4),
                      left: BorderSide(color: Colors.white, width: 4),
                    ),
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(16),
                    ),
                  ),
                ),
              ),
              // Bottom-right corner
              Align(
                alignment: Alignment.bottomRight,
                child: Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: Colors.white, width: 4),
                      right: BorderSide(color: Colors.white, width: 4),
                    ),
                    borderRadius: BorderRadius.only(
                      bottomRight: Radius.circular(16),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        // Guidance chip
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.65),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white24),
          ),
          child: Text(
            l10n?.viewfinderInstruction ??
                'Position diseased rice leaf in center',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }

  /// Permission denied dialog card.
  Widget _buildPermissionDeniedCard(ThemeData theme, AppLocalizations? l10n) {
    return Card(
      color: theme.colorScheme.surface,
      margin: const EdgeInsets.all(24),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusCard),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.no_photography_outlined,
              size: 56,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              l10n?.permissionDeniedTitle ?? 'Camera Access Needed',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              l10n?.permissionDeniedMessage ??
                  'Camera permission is required to capture photos directly. You can still select photos from your gallery.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              key: const Key('open_settings_button'),
              onPressed: () {},
              icon: const Icon(Icons.settings),
              label: Text(l10n?.openSettings ?? 'Open Settings'),
            ),
          ],
        ),
      ),
    );
  }

  /// Photo Selected Confirmation Card with Analyze and Retake actions.
  Widget _buildPhotoSelectedCard(ThemeData theme, AppLocalizations? l10n) {
    return Card(
      color: theme.colorScheme.surface,
      margin: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusCard),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              l10n?.photoSelectedTitle ?? 'Photo Selected',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton(
                  key: const Key('scan_retake_button'),
                  onPressed: _onRetakeTap,
                  child: Text(l10n?.retakeChange ?? 'Retake / Change'),
                ),
                const SizedBox(width: 12),
                FilledButton(
                  key: const Key('scan_analyze_button'),
                  onPressed: _onAnalyzeTap,
                  child: Text(l10n?.analyzeLeaf ?? 'Analyze Leaf'),
                ),
              ],
            ),
            // Step 6: Debug information displayed exclusively behind kDebugMode (omitted in release)
            if (kDebugMode && _capturedBytes != null) ...[
              const SizedBox(height: 12),
              const Divider(),
              Text(
                'Debug: ${_capturedPath?.split(RegExp(r"[/\\]")).last ?? "photo.jpg"} (${_capturedBytes!.lengthInBytes} B)',
                key: const Key('debug_photo_info'),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              Text(
                'SHA-256: ${computeSha256(_capturedBytes!)}',
                key: const Key('debug_photo_sha256'),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontFamily: 'monospace',
                  fontSize: 10,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// Analyzing progress state
  Widget _buildAnalyzingIndicator(ThemeData theme, AppLocalizations? l10n) {
    return Card(
      color: theme.colorScheme.surface,
      margin: const EdgeInsets.all(24),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusCard),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(
                theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              l10n?.analyzingTitle ?? 'Analyzing Rice Leaf...',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              l10n?.analyzingSubtitle ??
                  'Running on-device AI model (MobileNetV2)...',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  /// Bottom control panel in portrait layout.
  Widget _buildPortraitControls(ThemeData theme, AppLocalizations? l10n) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Compact expandable disclaimer strip (F-08)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: const DisclaimerCard(isCompact: true),
        ),
        const SizedBox(height: 8),

        // Controls bar: Gallery (56 dp), Shutter (72 dp), Help (56 dp)
        Padding(
          padding: const EdgeInsets.only(left: 24, right: 24, bottom: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Gallery button (56 dp)
              _buildControlButton(
                key: const Key('choose_gallery_button'),
                icon: Icons.photo_library,
                label: l10n?.galleryLabel ?? 'Gallery',
                size: AppTheme.controlButtonDiameter,
                onTap: _onGalleryTap,
                theme: theme,
                isHighlighted: _currentState == CaptureState.permissionDenied,
              ),

              // 72 dp central Shutter button
              _buildShutterButton(theme, l10n),

              // Help button (56 dp)
              _buildControlButton(
                key: const Key('help_button'),
                icon: Icons.help_outline,
                label: l10n?.helpLabel ?? 'Help',
                size: AppTheme.controlButtonDiameter,
                onTap: _onHelpTap,
                theme: theme,
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Bottom/Side control panel docked in landscape layout.
  Widget _buildLandscapeControls(ThemeData theme, AppLocalizations? l10n) {
    return Container(
      width: 140,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      color: Colors.black45,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildControlButton(
            key: const Key('choose_gallery_button'),
            icon: Icons.photo_library,
            label: l10n?.galleryLabel ?? 'Gallery',
            size: AppTheme.controlButtonDiameter,
            onTap: _onGalleryTap,
            theme: theme,
            isHighlighted: _currentState == CaptureState.permissionDenied,
          ),
          _buildShutterButton(theme, l10n),
          _buildControlButton(
            key: const Key('help_button'),
            icon: Icons.help_outline,
            label: l10n?.helpLabel ?? 'Help',
            size: AppTheme.controlButtonDiameter,
            onTap: _onHelpTap,
            theme: theme,
          ),
        ],
      ),
    );
  }

  /// Circular 72 dp Shutter Button with accessible label.
  Widget _buildShutterButton(ThemeData theme, AppLocalizations? l10n) {
    final isDisabled = _currentState == CaptureState.permissionDenied ||
        _currentState == CaptureState.analyzing;

    return Semantics(
      button: true,
      enabled: !isDisabled,
      label: l10n?.shutterSemantics ?? 'Capture leaf photo',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Opacity(
            opacity: isDisabled ? 0.38 : 1.0,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                key: const Key('take_photo_button'),
                onTap: isDisabled ? null : _onShutterTap,
                customBorder: const CircleBorder(),
                child: Container(
                  width: AppTheme.shutterDiameter,
                  height: AppTheme.shutterDiameter,
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 4),
                  ),
                  child: Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: theme.colorScheme.primary,
                    ),
                    child: const Icon(
                      Icons.camera_alt,
                      color: Colors.white,
                      size: 32,
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            l10n?.shutterLabel ?? 'Capture',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// Circular 56 dp auxiliary control button (Gallery / Help).
  Widget _buildControlButton({
    required Key key,
    required IconData icon,
    required String label,
    required double size,
    required VoidCallback onTap,
    required ThemeData theme,
    bool isHighlighted = false,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Material(
          color: isHighlighted
              ? theme.colorScheme.primaryContainer
              : Colors.white.withOpacity(0.2),
          shape: const CircleBorder(),
          child: InkWell(
            key: key,
            onTap: onTap,
            customBorder: const CircleBorder(),
            child: Container(
              width: size,
              height: size,
              alignment: Alignment.center,
              child: Icon(
                icon,
                color: isHighlighted
                    ? theme.colorScheme.onPrimaryContainer
                    : Colors.white,
                size: 26,
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: TextStyle(
            color: isHighlighted
                ? theme.colorScheme.primaryContainer
                : Colors.white,
            fontSize: 12,
            fontWeight: isHighlighted ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }
}
