import 'package:flutter/material.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/l10n/app_localizations.dart';
import 'package:ricedisease/widgets/disclaimer_card.dart';

/// About screen adhering strictly to docs/design/ui_spec.md Section 4.7
/// and Decision D-29 (dataset credit appears only here and documentation).
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final isBn = Localizations.localeOf(context).languageCode == 'bn';
    final canPop = ModalRoute.of(context)?.canPop ?? false;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.aboutTitle ?? 'About Screen'),
        scrolledUnderElevation: 2,
        leading: canPop ? const BackButton() : null,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spaceMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. App Identity Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.spaceMd),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: theme.colorScheme.primaryContainer,
                          ),
                          child: Icon(
                            Icons.energy_savings_leaf,
                            color: theme.colorScheme.onPrimaryContainer,
                            size: 28,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                l10n?.appTitle ?? 'Rice Leaf Disease Detection',
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${l10n?.versionLabel ?? "Version"}: 1.0.0 (Build 1)',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      l10n?.developerCredit ??
                          'Academic final-year project by Mehedi Hasan.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontStyle: FontStyle.italic,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppTheme.spaceMd),

            // 2. Software & Font Licenses Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.spaceMd),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.verified_outlined,
                          size: 20,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          l10n?.licenseTitle ?? 'License',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n?.licenseText ??
                          'Released under the MIT License. Embedded font Noto Sans Bengali licensed under SIL Open Font License 1.1.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppTheme.spaceMd),

            // 3. Dataset Credit Card (Decision D-29)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.spaceMd),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.menu_book_outlined,
                          size: 20,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          l10n?.datasetCreditTitle ?? 'Dataset Credit',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n?.datasetCreditText ??
                          (isBn
                              ? 'ধানের পাতার ছবি: হাসান, এম. প্রমুখ (২০২৩), মেন্ডেলে ডেটা, DOI 10.17632/hx6f852hw4.2, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) লাইসেন্সের অধীন। পরিবর্তন: EXIF ডেটা অনুযায়ী ছবির ওরিয়েন্টেশন সংশোধন করা হয়েছে এবং প্রশিক্ষণের জন্য পুনরায় এনকোড করা হয়েছে।'
                              : 'Rice leaf images: Hasan, M. et al. (2023), Mendeley Data, DOI 10.17632/hx6f852hw4.2, licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: images were re-oriented according to EXIF data and re-encoded for training.'),
                      key: const Key('dataset_credit_text'),
                      style: theme.textTheme.bodySmall?.copyWith(
                        height: 1.5,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppTheme.spaceMd),

            // 4. In-App Privacy Policy Row (T-081)
            Card(
              child: ListTile(
                key: const Key('privacy_policy_row'),
                leading: Icon(
                  Icons.privacy_tip_outlined,
                  color: theme.colorScheme.primary,
                ),
                title: Text(
                  l10n?.privacyPolicyTitle ?? 'Privacy Policy',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                subtitle: Text(
                  l10n?.privacyPolicySubtitle ??
                      '100% offline. Zero personal data or photos collected or shared.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.of(context).pushNamed(AppRoutes.privacy);
                },
              ),
            ),
            const SizedBox(height: AppTheme.spaceMd),

            // 5. Official Advisory Disclaimer Card (F-08)
            const DisclaimerCard(isCompact: false),
            const SizedBox(height: AppTheme.spaceLg),
          ],
        ),
      ),
    );
  }
}
