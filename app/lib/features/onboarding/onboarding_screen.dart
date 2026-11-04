import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Onboarding screen shown on first launch.
class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final title = l10n?.onboardingTitle ?? 'Onboarding Screen';
    final getStarted = l10n?.getStarted ?? 'Get Started';

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.appTitle ?? 'Rice Leaf Disease Detection'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              key: const Key('get_started_button'),
              onPressed: () async {
                final prefs = ref.read(sharedPreferencesProvider);
                await prefs.setBool(PrefKeys.onboardingDone, true);
                if (context.mounted) {
                  Navigator.pushReplacementNamed(context, AppRoutes.home);
                }
              },
              child: Text(getStarted),
            ),
          ],
        ),
      ),
    );
  }
}
