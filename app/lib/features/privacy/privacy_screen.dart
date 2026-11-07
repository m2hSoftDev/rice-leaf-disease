import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

/// Privacy Policy screen displaying the offline privacy policy (Task T-081).
///
/// Loads policy text directly from bundled asset `assets/privacy/privacy_en.md`.
/// Contains zero network calls and zero external URL launchers.
class PrivacyScreen extends StatefulWidget {
  const PrivacyScreen({super.key});

  @override
  State<PrivacyScreen> createState() => _PrivacyScreenState();
}

class _PrivacyScreenState extends State<PrivacyScreen> {
  String? _content;

  @override
  void initState() {
    super.initState();
    _loadPolicy();
  }

  Future<void> _loadPolicy() async {
    try {
      final text = await rootBundle.loadString('assets/privacy/privacy_en.md', cache: false);
      if (mounted) {
        setState(() {
          _content = text;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _content = 'Unable to load privacy policy. Please contact m2hsoftdev@gmail.com.';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isBangla = Localizations.localeOf(context).languageCode == 'bn';

    return Scaffold(
      appBar: AppBar(
        title: Text(isBangla ? 'গোপনীয়তা নীতি' : 'Privacy Policy'),
      ),
      body: _content == null
          ? const Center(child: Text('Loading...'))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (isBangla) ...[
                    Card(
                      color: Theme.of(context).colorScheme.surfaceVariant,
                      child: const Padding(
                        padding: EdgeInsets.all(12.0),
                        child: Row(
                          children: [
                            Icon(Icons.info_outline, size: 20),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'বাংলা সংস্করণ পর্যালোচনার জন্য প্রক্রিয়াধীন রয়েছে। নিচে ইংরেজি গোপনীয়তা নীতি প্রদর্শিত হলো।',
                                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  SelectableText(
                    _content!,
                    style: const TextStyle(
                      fontSize: 14,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
