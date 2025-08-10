import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class MultiAddEntriesScreen extends StatelessWidget {
  const MultiAddEntriesScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Добавить несколько')),
      body: ListView.builder(
        itemCount: 5,
        itemBuilder: (_, i) => ListTile(
          leading: const Icon(Icons.add_circle_outline),
          title: Text('Продукт #${i + 1}'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {},
        ),
      ),
    );
  }
}
