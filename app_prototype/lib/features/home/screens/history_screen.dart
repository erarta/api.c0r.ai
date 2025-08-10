import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/history_api.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _loading = true;
  List<Map<String, dynamic>> _items = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = await ApiClient.create();
      final hist = HistoryApi(api);
      final items = await hist.list(limit: 50);
      setState(() => _items = items);
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('history.title'))),
      showLoading: _loading,
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.separated(
          padding: const EdgeInsets.all(16),
          itemBuilder: (_, i) {
            final it = _items[i];
            final kbzhu = it['kbzhu'] as Map<String, dynamic>?;
            final summary = kbzhu != null
                ? 'Ккал:${kbzhu['calories'] ?? 0} • Б:${kbzhu['proteins'] ?? 0} • Ж:${kbzhu['fats'] ?? 0} • У:${kbzhu['carbohydrates'] ?? 0}'
                : '';
            return ListTile(
              leading: const CircleAvatar(child: Icon(Icons.fastfood)),
              title: Text(it['title']?.toString() ?? 'Анализ'),
              subtitle: Text(summary),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            );
          },
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemCount: _items.length,
        ),
      ),
    );
  }
}
