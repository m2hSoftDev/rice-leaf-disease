import 'package:flutter/material.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Result placeholder screen.
class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final title = l10n?.resultTitle ?? 'Result Screen';
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.appTitle ?? 'Rice Leaf Disease Detection'),
      ),
      body: Center(
        child: Text(
          title,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
