import 'package:flutter/material.dart';

/// App theme implementation adhering to Material 3, high-contrast accessibility,
/// minimum 48 dp touch target size, and system-scaled typography.
class AppTheme {
  // High-contrast primary colors (contrast ratio >= 7:1 against light surfaces)
  static const Color primary = Color(0xFF134E17);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFFB7F397);
  static const Color onPrimaryContainer = Color(0xFF042100);

  static const Color secondary = Color(0xFF1E3A8A);
  static const Color onSecondary = Color(0xFFFFFFFF);

  static const Color surface = Color(0xFFFFFFFF);
  static const Color onSurface = Color(0xFF111111);
  static const Color surfaceContainerHighest = Color(0xFFE2E7DE);
  static const Color onSurfaceVariant = Color(0xFF1F241E);

  static const Color error = Color(0xFFB00020);
  static const Color onError = Color(0xFFFFFFFF);

  static ThemeData get lightTheme {
    final colorScheme = ColorScheme(
      brightness: Brightness.light,
      primary: primary,
      onPrimary: onPrimary,
      primaryContainer: primaryContainer,
      onPrimaryContainer: onPrimaryContainer,
      secondary: secondary,
      onSecondary: onSecondary,
      surface: surface,
      onSurface: onSurface,
      surfaceContainerHighest: surfaceContainerHighest,
      onSurfaceVariant: onSurfaceVariant,
      error: error,
      onError: onError,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      materialTapTargetSize: MaterialTapTargetSize.padded,
      visualDensity: VisualDensity.standard,
      scaffoldBackgroundColor: surface,
      appBarTheme: const AppBarTheme(
        backgroundColor: primary,
        foregroundColor: onPrimary,
        elevation: 0,
        centerTitle: false,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(48, 48), // Section 9.4 touch target
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          foregroundColor: onPrimary,
          backgroundColor: primary,
          tapTargetSize: MaterialTapTargetSize.padded,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          foregroundColor: primary,
          tapTargetSize: MaterialTapTargetSize.padded,
          side: const BorderSide(color: primary, width: 2),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          foregroundColor: primary,
          tapTargetSize: MaterialTapTargetSize.padded,
        ),
      ),
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          minimumSize: const Size(48, 48),
          tapTargetSize: MaterialTapTargetSize.padded,
        ),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: surfaceContainerHighest, width: 1),
        ),
      ),
    );
  }
}
