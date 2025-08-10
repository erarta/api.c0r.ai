import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/recipes_api.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class RecipesListScreen extends StatefulWidget {
  const RecipesListScreen({super.key});
  @override
  State<RecipesListScreen> createState() => _RecipesListScreenState();
}

class _RecipesListScreenState extends State<RecipesListScreen> {
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
      final svc = RecipesApi(api);
      final items = await svc.list(limit: 50);
      setState(() => _items = items);
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('recipes.title'))),
      showLoading: _loading,
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.separated(
          padding: const EdgeInsets.all(16),
          itemBuilder: (_, i) {
            final it = _items[i];
            return ListTile(
              title: Text(it['name']?.toString() ?? l10n.t('favorites.name_label')),
              subtitle: Text((it['items_json']?['summary'] ?? '').toString()),
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
