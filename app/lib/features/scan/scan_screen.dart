import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/widgets/disclaimer_card.dart';

// TODO(T-063): Wire live camera controller using camera package when camera permissions and lifecycle handling are finalized in M6.

/// Distinct states for the capture page.
enum CaptureState {
  idle,
  permissionDenied,
  photoSelected,
  analyzing,
}

/// Capture page (Scan) adhering to Material 3 full-bleed layout
/// and docs/design/ui_spec.md Section 4.3.
class ScanScreen extends ConsumerStatefulWidget {
  final CaptureState initialState;

  const ScanScreen({
    super.key,
    this.initialState = CaptureState.idle,
  });

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  late CaptureState _currentState;

  @override
  void initState() {
    super.initState();
    _currentState = widget.initialState;
  }

  void _onShutterTap() {
    if (_currentState == CaptureState.permissionDenied ||
        _currentState == CaptureState.analyzing) {
      return;
    }
    // Simulate capturing a photo
    setState(() {
      _currentState = CaptureState.photoSelected;
    });
  }

  void _onGalleryTap() {
    // Gallery picker is always available, even in permission-denied state
    setState(() {
      _currentState = CaptureState.photoSelected;
    });
  }

  void _onAnalyzeTap() {
    setState(() {
      _currentState = CaptureState.analyzing;
    });
    // In production, InferenceService isolate runs here.
    // For navigation flow, navigate to ResultScreen after brief processing.
    Future.delayed(const Duration(milliseconds: 300), () {
      if (mounted) {
        setState(() {
          _currentState = CaptureState.idle;
        });
        Navigator.of(context).pushNamed(AppRoutes.result);
      }
    });
  }

  void _onRetakeTap() {
    setState(() {
      _currentState = CaptureState.idle;
    });
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
          // 1. Full-bleed preview placeholder (static image/viewport, no live camera)
          _buildPreviewPlaceholder(theme),

          // 2. Viewfinder with corner brackets and guidance instruction
          if (_currentState != CaptureState.permissionDenied)
            Align(
              alignment: isLandscape ? const Alignment(-0.3, 0) : const Alignment(0, -0.1),
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
              alignment: isLandscape ? const Alignment(-0.3, 0.7) : const Alignment(0, 0.45),
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
              onPressed: () {},
              icon: const Icon(Icons.settings),
              label: Text(l10n?.openSettings ?? 'Open Settings'),
            ),
          ],
        ),
      ),
    );
  }

  /// Photo Selected Confirmation Card
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
                  onPressed: _onRetakeTap,
                  child: Text(l10n?.retakeChange ?? 'Retake / Change'),
                ),
                const SizedBox(width: 12),
                FilledButton(
                  key: const Key('nav_result_button'),
                  onPressed: _onAnalyzeTap,
                  child: Text(l10n?.analyzeLeaf ?? 'Analyze Leaf'),
                ),
              ],
            ),
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
