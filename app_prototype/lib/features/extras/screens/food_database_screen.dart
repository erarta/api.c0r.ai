import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class FoodDatabaseScreen extends StatelessWidget {
  const FoodDatabaseScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('База продуктов')),
      body: Column(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: TextField(decoration: InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Поиск')),
          ),
          const Divider(height: 1),
          Expanded(
            child: ListView.separated(
              itemBuilder: (_, i) => ListTile(title: Text('Продукт ${i + 1}'), subtitle: const Text('ккал/Б/Ж/У')),
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemCount: 20,
            ),
          )
        ],
      ),
    );
  }
}
