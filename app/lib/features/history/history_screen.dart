import 'package:flutter/material.dart';
import 'package:ricedisease/app/theme.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Item model representing a past scan record.
class HistoryItem {
  final String id;
  final String conditionNameEn;
  final String conditionNameBn;
  final double confidence;
  final DateTime timestamp;
  final bool isUncertain;

  const HistoryItem({
    required this.id,
    required this.conditionNameEn,
    required this.conditionNameBn,
    required this.confidence,
    required this.timestamp,
    required this.isUncertain,
  });
}

/// History screen displaying past scans in a lazy list or an empty state (F-09).
class HistoryScreen extends StatefulWidget {
  final VoidCallback? onStartScan;
  final List<HistoryItem>? initialItems;

  const HistoryScreen({
    super.key,
    this.onStartScan,
    this.initialItems,
  });

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late List<HistoryItem> _items;

  @override
  void initState() {
    super.initState();
    _items = widget.initialItems != null
        ? List.from(widget.initialItems!)
        : <HistoryItem>[];
  }

  void _confirmClearAll() {
    final l10n = AppLocalizations.of(context);
    showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n?.clearAllConfirmTitle ?? 'Clear all past scans?'),
        content: Text(
          l10n?.clearAllConfirmMessage ??
              'This will delete all saved scan history on this device. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(l10n?.cancel ?? 'Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
              foregroundColor: Theme.of(context).colorScheme.onError,
            ),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(l10n?.delete ?? 'Delete'),
          ),
        ],
      ),
    ).then((confirmed) {
      if (confirmed == true && mounted) {
        setState(() {
          _items.clear();
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final isBn = Localizations.localeOf(context).languageCode == 'bn';

    final canPop = ModalRoute.of(context)?.canPop ?? false;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.historyTitle ?? 'History Screen'),
        scrolledUnderElevation: 2,
        leading: canPop ? const BackButton() : null,
        actions: [
          if (_items.isNotEmpty)
            IconButton(
              key: const Key('clear_history_button'),
              icon: const Icon(Icons.delete_sweep_outlined),
              tooltip: l10n?.clearAll ?? 'Clear All',
              onPressed: _confirmClearAll,
            ),
        ],
      ),
      body: _items.isEmpty
          ? _buildEmptyState(theme, l10n)
          : _buildPopulatedList(theme, l10n, isBn),
    );
  }

  /// Empty state matching Section 4.6 (HI-01).
  Widget _buildEmptyState(ThemeData theme, AppLocalizations? l10n) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spaceXl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: theme.colorScheme.surfaceVariant,
              ),
              child: Icon(
                Icons.history_toggle_off_outlined,
                size: 48,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              l10n?.historyEmpty ?? 'No past scans yet.',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              l10n?.historyEmptyDesc ??
                  'Scans are stored offline on this device so you can track conditions over time.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),
            FilledButton.icon(
              key: const Key('start_first_scan_button'),
              onPressed: widget.onStartScan,
              icon: const Icon(Icons.photo_camera),
              label: Text(l10n?.startFirstScan ?? 'Start First Scan'),
            ),
          ],
        ),
      ),
    );
  }

  /// Lazy list matching Section 4.6 (HI-02, HI-03).
  Widget _buildPopulatedList(
    ThemeData theme,
    AppLocalizations? l10n,
    bool isBn,
  ) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final item = _items[index];
        final conditionName = isBn ? item.conditionNameBn : item.conditionNameEn;
        final formattedDate =
            '${item.timestamp.year}-${item.timestamp.month.toString().padLeft(2, '0')}-${item.timestamp.day.toString().padLeft(2, '0')} '
            '${item.timestamp.hour.toString().padLeft(2, '0')}:${item.timestamp.minute.toString().padLeft(2, '0')}';

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                // 56x56 dp thumbnail placeholder
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: item.isUncertain
                        ? theme.colorScheme.errorContainer
                        : theme.colorScheme.primaryContainer,
                  ),
                  child: Icon(
                    item.isUncertain
                        ? Icons.warning_amber_rounded
                        : Icons.energy_savings_leaf,
                    color: item.isUncertain
                        ? theme.colorScheme.onErrorContainer
                        : theme.colorScheme.onPrimaryContainer,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        conditionName,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        formattedDate,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  '${(item.confidence * 100).toStringAsFixed(1)}%',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: item.isUncertain
                        ? theme.colorScheme.error
                        : theme.colorScheme.primary,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
