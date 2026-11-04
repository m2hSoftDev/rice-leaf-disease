import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/app/router.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/core/locale_provider.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Root application widget configuring Material 3 theme, localization, and routes.
class RiceDiseaseApp extends ConsumerWidget {
  const RiceDiseaseApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentLocale = ref.watch(localeProvider);

    return MaterialApp(
      title: 'Rice Leaf Disease Detection',
      theme: AppTheme.getTheme(currentLocale),
      locale: currentLocale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      initialRoute: AppRoutes.splash,
      onGenerateRoute: AppRouter.onGenerateRoute,
    );
  }
}
