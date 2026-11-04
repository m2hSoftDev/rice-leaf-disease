import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Home screen containing navigation entries and language toggle.
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
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              key: const Key('nav_result_button'),
              onPressed: () => Navigator.pushNamed(context, AppRoutes.result),
              child: const Text('Go to Result Screen'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('nav_history_button'),
              onPressed: () => Navigator.pushNamed(context, AppRoutes.history),
              child: const Text('Go to History Screen'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('nav_about_button'),
              onPressed: () => Navigator.pushNamed(context, AppRoutes.about),
              child: const Text('Go to About Screen'),
            ),
          ],
        ),
      ),
    );
  }
}
