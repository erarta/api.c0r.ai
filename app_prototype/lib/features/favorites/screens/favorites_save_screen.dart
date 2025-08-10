import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/favorites_api.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class FavoritesSaveScreen extends StatefulWidget {
  const FavoritesSaveScreen({super.key});
  @override
  State<FavoritesSaveScreen> createState() => _FavoritesSaveScreenState();
}

class _FavoritesSaveScreenState extends State<FavoritesSaveScreen> {
  final _name = TextEditingController();
  bool _loading = false;

  Future<void> _save() async {
    setState(() => _loading = true);
    try {
      final api = await ApiClient.create();
      final fav = FavoritesApi(api);
      await fav.save(name: _name.text.trim(), itemsJson: {'summary': 'custom'});
      if (!mounted) return;
      Navigator.of(context).pop();
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('favorites.save_title'))),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _name, decoration: InputDecoration(labelText: l10n.t('favorites.name_label'))),
            const SizedBox(height: 16),
            SizedBox(width: double.infinity, child: FilledButton(onPressed: _save, child: Text(l10n.t('favorites.add')))),
          ],
        ),
      ),
    );
  }
}
