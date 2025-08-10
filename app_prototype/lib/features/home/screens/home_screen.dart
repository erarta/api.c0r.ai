import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/features/home/screens/capture_screen.dart';
import 'package:c0r_app/features/home/screens/history_screen.dart';
import 'package:c0r_app/features/home/widgets/streak_popup.dart';
import 'package:c0r_app/features/home/screens/label_analyze_screen.dart';
import 'package:c0r_app/features/home/screens/barcode_scanner_screen.dart';
import 'package:c0r_app/features/home/widgets/quick_actions_panel.dart';
import 'package:c0r_app/features/home/widgets/daily_summary_panel.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0; // 0: Food, 1: Health

  void _showStreak() {
    showDialog(context: context, builder: (_) => StreakPopup(days: 3, onClose: () => Navigator.pop(context)));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(
        title: Text(l10n.t('home.today')),
        actions: [
          IconButton(
            icon: const Icon(Icons.center_focus_strong_outlined),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const BarcodeScannerScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const LabelAnalyzeScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.local_fire_department_outlined),
            onPressed: _showStreak,
          ),
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const HistoryScreen()),
            ),
          )
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 0, label: Text('Еда')),
                ButtonSegment(value: 1, label: Text('Здоровье')),
              ],
              selected: {_tab},
              onSelectionChanged: (s) => setState(() => _tab = s.first),
            ),
          ),
        ),
      ),
      body: _tab == 0 ? const _FoodTab() : const _HealthTab(),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: FilledButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const CaptureScreen()),
            ),
            child: Text(l10n.t('home.scan_food')),
          ),
        ),
      ),
    );
  }
}

class _FoodTab extends StatelessWidget {
  const _FoodTab();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: const [
        DailySummaryPanel(),
        SizedBox(height: 12),
        QuickActionsPanel(),
        SizedBox(height: 16),
        ListTile(title: Text('Последние анализы')),
      ],
    );
  }
}

class _HealthTab extends StatelessWidget {
  const _HealthTab();
  @override
  Widget build(BuildContext context) {
    return Center(child: Text('Индекс здоровья — скоро', style: Theme.of(context).textTheme.bodyLarge));
  }
}
