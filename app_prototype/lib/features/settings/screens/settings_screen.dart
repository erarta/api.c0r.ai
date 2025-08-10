import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/features/settings/screens/language_screen.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('settings.title'))),
      body: ListView(
        children: [
          ListTile(
            title: Text(l10n.t('settings.language')),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const LanguageScreen()),
            ),
          ),
          ListTile(
            title: Text(l10n.t('settings.delete_account')),
            trailing: const Icon(Icons.delete_outline, color: Colors.redAccent),
            onTap: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (_) => AlertDialog(
                  title: Text(l10n.t('settings.delete_confirm')),
                  content: Text(l10n.t('settings.delete_confirm_desc')),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.t('settings.cancel'))),
                    FilledButton(onPressed: () => Navigator.pop(context, true), child: Text(l10n.t('settings.delete'))),
                  ],
                ),
              );
              if (ok == true) {
                // TODO: call delete API
              }
            },
          ),
        ],
      ),
    );
  }
}
