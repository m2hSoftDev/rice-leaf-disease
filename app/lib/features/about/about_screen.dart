import 'package:flutter/material.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// About placeholder screen with credits, licenses, and disclaimer (F-14).
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final title = l10n?.aboutTitle ?? 'About Screen';

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.appTitle ?? 'Rice Leaf Disease Detection'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              l10n?.aboutDescription ?? '',
              style: const TextStyle(fontSize: 15),
            ),
            const SizedBox(height: 20),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n?.creditsTitle ?? 'Credits & Sources',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n?.creditsText ?? '',
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n?.licenseTitle ?? 'License',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n?.licenseText ?? '',
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                key: const Key('privacy_policy_row'),
                leading: const Icon(Icons.privacy_tip_outlined),
                title: Text(
                  Localizations.localeOf(context).languageCode == 'bn'
                      ? 'গোপনীয়তা নীতি'
                      : 'Privacy Policy',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  Localizations.localeOf(context).languageCode == 'bn'
                      ? 'সম্পূর্ণ অফলাইন, কোনো ব্যক্তিগত তথ্য সংগ্রহ করা হয় না'
                      : '100% offline, zero data collected or shared',
                  style: const TextStyle(fontSize: 13),
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.of(context).pushNamed(AppRoutes.privacy);
                },
              ),
            ),
            const SizedBox(height: 16),
            Text(
              '${l10n?.versionLabel ?? "Version"}: 1.0.0+1',
              style: const TextStyle(fontSize: 13, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
