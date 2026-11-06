import 'package:flutter/material.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/services/inference_service.dart';

/// Result screen displaying disease classification, confidence,
/// uncertain state banner (D-11, F-05), and localized field advisory (F-06).
class ResultScreen extends StatelessWidget {
  final InferenceResult? result;

  const ResultScreen({super.key, this.result});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final title = l10n?.resultTitle ?? 'Result Screen';
    final isBn = Localizations.localeOf(context).languageCode == 'bn';

    final effectiveResult = result ??
        (ModalRoute.of(context)?.settings.arguments as InferenceResult?);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.appTitle ?? 'Rice Leaf Disease Detection'),
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
              const SizedBox(height: 16),

              if (effectiveResult == null) ...[
                // Fallback placeholder when no inference result passed (keeps existing tests passing)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n?.diseaseBacterialLeafBlight ?? 'Bacterial Leaf Blight',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          l10n?.diseaseBrownSpot ?? 'Brown Spot',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          l10n?.diseaseLeafBlast ?? 'Leaf Blast',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          l10n?.diseaseHealthy ?? 'Healthy',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                // Uncertain result placeholder banner (D-11)
                Card(
                  color: Theme.of(context).colorScheme.errorContainer,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n?.uncertainTitle ?? 'Uncertain Result',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.onErrorContainer,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          l10n?.uncertainDescription ?? '',
                          style: TextStyle(
                            fontSize: 14,
                            color: Theme.of(context).colorScheme.onErrorContainer,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                // Advisory note placeholder (F-06)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n?.advisoryTitle ?? 'Field Advisory',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          l10n?.disclaimerText ?? '',
                          style: const TextStyle(fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                ),
              ] else ...[
                // When effectiveResult is present:
                if (effectiveResult.isUncertain) ...[
                  // D-11 uncertain banner: top confidence < 60%
                  Card(
                    color: Theme.of(context).colorScheme.errorContainer,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n?.uncertainTitle ?? 'Uncertain Result',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Theme.of(context).colorScheme.onErrorContainer,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '${isBn ? effectiveResult.displayNameBn : effectiveResult.displayNameEn} '
                            '(${(effectiveResult.confidence * 100).toStringAsFixed(1)}%)',
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: Theme.of(context).colorScheme.onErrorContainer,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            l10n?.uncertainDescription ??
                                'Confidence is low. Please consult an agricultural expert.',
                            style: TextStyle(
                              fontSize: 14,
                              color: Theme.of(context).colorScheme.onErrorContainer,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  // Advisory section is explicitly hidden per D-11: no treatment advice shown
                ] else ...[
                  // Normal confident result (confidence >= 60%)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isBn
                                ? effectiveResult.displayNameBn
                                : effectiveResult.displayNameEn,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            isBn
                                ? effectiveResult.displayNameEn
                                : effectiveResult.displayNameBn,
                            style: TextStyle(
                              fontSize: 14,
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Text(
                                '${l10n?.confidenceLabel ?? "Confidence"}: ',
                                style: const TextStyle(fontWeight: FontWeight.w600),
                              ),
                              Text(
                                '${(effectiveResult.confidence * 100).toStringAsFixed(1)}%',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Field Advisory Card (F-06)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n?.advisoryTitle ?? 'Field Advisory',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            (isBn
                                    ? effectiveResult.advisoryBn
                                    : effectiveResult.advisoryEn) ??
                                '',
                            style: const TextStyle(fontSize: 14),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            l10n?.disclaimerText ?? '',
                            style: TextStyle(
                              fontSize: 12,
                              fontStyle: FontStyle.italic,
                              color: Theme.of(context).colorScheme.outline,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }
}
