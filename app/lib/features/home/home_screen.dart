import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Home screen containing action buttons, navigation entries, language toggle,
/// and advisory disclaimer (F-08).
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final currentLocale = ref.watch(localeProvider);
    final title = l10n?.homeTitle ?? 'Home Screen';
    final toggleLabel = currentLocale.languageCode == 'en'
        ? (l10n?.switchToBangla ?? 'বাংলায় দেখুন')
        : (l10n?.switchToEnglish ?? 'View in English');

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.appTitle ?? 'Rice Leaf Disease Detection'),
        actions: [
          TextButton(
            key: const Key('language_toggle_button'),
            onPressed: () {
              ref.read(localeProvider.notifier).toggleLocale();
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.onPrimary,
            ),
            child: Text(toggleLabel),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                title,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),
              // Action buttons placeholder (F-01, F-02)
              ElevatedButton.icon(
                key: const Key('take_photo_button'),
                onPressed: () {},
                icon: const Icon(Icons.camera_alt),
                label: Text(l10n?.takePhoto ?? 'Take Photo'),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                key: const Key('choose_gallery_button'),
                onPressed: () {},
                icon: const Icon(Icons.photo_library),
                label: Text(l10n?.chooseGallery ?? 'Choose from Gallery'),
              ),
              const SizedBox(height: 24),
              // Navigation buttons
              ElevatedButton(
                key: const Key('nav_result_button'),
                onPressed: () => Navigator.pushNamed(context, AppRoutes.result),
                child: Text(l10n?.goToResult ?? 'Go to Result Screen'),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                key: const Key('nav_history_button'),
                onPressed: () => Navigator.pushNamed(context, AppRoutes.history),
                child: Text(l10n?.goToHistory ?? 'Go to History Screen'),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                key: const Key('nav_about_button'),
                onPressed: () => Navigator.pushNamed(context, AppRoutes.about),
                child: Text(l10n?.goToAbout ?? 'Go to About Screen'),
              ),
              const SizedBox(height: 28),
              // Visible disclaimer card (F-08)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n?.disclaimerTitle ?? 'Advisory Notice',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        l10n?.disclaimerText ?? '',
                        key: const Key('disclaimer_text'),
                        style: const TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
