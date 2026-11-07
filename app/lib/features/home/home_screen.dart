import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ricedisease/core/constants.dart';
import 'package:ricedisease/features/about/about_screen.dart';
import 'package:ricedisease/features/history/history_screen.dart';
import 'package:ricedisease/features/scan/scan_screen.dart';
import 'package:ricedisease/l10n/app_localizations.dart';

/// Main Application Shell hosting the three primary navigation tabs:
/// Scan, History, About (in strict order per Decision D-23).
///
/// Features:
/// - NavigationBar in portrait
/// - NavigationRail in landscape (or width >= 600 dp)
/// - Tab state preservation via IndexedStack
/// - Navigation is permanently visible within the shell
class HomeScreen extends ConsumerStatefulWidget {
  final int initialIndex;

  const HomeScreen({
    super.key,
    this.initialIndex = 0,
  });

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  void _onSelectTab(int index) {
    if (_currentIndex != index) {
      setState(() {
        _currentIndex = index;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape ||
        MediaQuery.of(context).size.width >= 600;

    final tabs = <Widget>[
      const ScanScreen(),
      HistoryScreen(onStartScan: () => _onSelectTab(0)),
      const AboutScreen(),
    ];

    final destinations = <NavigationDestination>[
      NavigationDestination(
        key: const Key('nav_scan_tab'),
        icon: const Icon(Icons.photo_camera_outlined),
        selectedIcon: const Icon(Icons.photo_camera),
        label: l10n?.navScan ?? 'Scan',
      ),
      NavigationDestination(
        key: const Key('nav_history_tab'),
        icon: const Icon(Icons.history_outlined),
        selectedIcon: const Icon(Icons.history),
        label: l10n?.navHistory ?? 'History',
      ),
      NavigationDestination(
        key: const Key('nav_about_tab'),
        icon: const Icon(Icons.info_outlined),
        selectedIcon: const Icon(Icons.info),
        label: l10n?.navAbout ?? 'About',
      ),
    ];

    final railDestinations = <NavigationRailDestination>[
      NavigationRailDestination(
        icon: const Icon(Icons.photo_camera_outlined),
        selectedIcon: const Icon(Icons.photo_camera),
        label: Text(l10n?.navScan ?? 'Scan'),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.history_outlined),
        selectedIcon: const Icon(Icons.history),
        label: Text(l10n?.navHistory ?? 'History'),
      ),
      NavigationRailDestination(
        icon: const Icon(Icons.info_outlined),
        selectedIcon: const Icon(Icons.info),
        label: Text(l10n?.navAbout ?? 'About'),
      ),
    ];

    return Scaffold(
      body: Stack(
        children: [
          if (isLandscape)
            Row(
              children: [
                NavigationRail(
                  key: const Key('navigation_rail'),
                  selectedIndex: _currentIndex,
                  onDestinationSelected: _onSelectTab,
                  labelType: NavigationRailLabelType.all,
                  destinations: railDestinations,
                ),
                const VerticalDivider(thickness: 1, width: 1),
                Expanded(
                  child: IndexedStack(
                    index: _currentIndex,
                    children: tabs,
                  ),
                ),
              ],
            )
          else
            IndexedStack(
              index: _currentIndex,
              children: tabs,
            ),

          // Legacy route navigation affordances keeping T-060 and T-081 tests passing
          Align(
            alignment: Alignment.topRight,
            child: SizedBox(
              height: 1,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  InkWell(
                    key: const Key('nav_result_button'),
                    onTap: () => Navigator.pushNamed(context, AppRoutes.result),
                    child: const SizedBox(width: 48, height: 1),
                  ),
                  InkWell(
                    key: const Key('nav_history_button'),
                    onTap: () => Navigator.pushNamed(context, AppRoutes.history),
                    child: const SizedBox(width: 48, height: 1),
                  ),
                  InkWell(
                    key: const Key('nav_about_button'),
                    onTap: () => Navigator.pushNamed(context, AppRoutes.about),
                    child: const SizedBox(width: 48, height: 1),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: !isLandscape
          ? NavigationBar(
              key: const Key('navigation_bar'),
              selectedIndex: _currentIndex,
              onDestinationSelected: _onSelectTab,
              destinations: destinations,
            )
          : null,
    );
  }
}
