import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class LanguageScreen extends StatefulWidget {
  const LanguageScreen({super.key});
  @override
  State<LanguageScreen> createState() => _LanguageScreenState();
}

class _LanguageScreenState extends State<LanguageScreen> {
  String _lang = 'ru';

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Язык')),
      body: Column(
        children: [
          RadioListTile(title: const Text('Русский'), value: 'ru', groupValue: _lang, onChanged: (v) => setState(() => _lang = v as String)),
          RadioListTile(title: const Text('English'), value: 'en', groupValue: _lang, onChanged: (v) => setState(() => _lang = v as String)),
          const Spacer(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton(onPressed: () {}, child: const Text('Сохранить')),
            ),
          )
        ],
      ),
    );
  }
}
