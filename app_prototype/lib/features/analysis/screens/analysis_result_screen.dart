import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class AnalysisResultScreen extends StatelessWidget {
  final double calories;
  final double proteins;
  final double fats;
  final double carbohydrates;
  const AnalysisResultScreen({super.key, required this.calories, required this.proteins, required this.fats, required this.carbohydrates});

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Анализ')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ккал: ${calories.toStringAsFixed(0)}'),
            Text('Белки: ${proteins.toStringAsFixed(1)}'),
            Text('Жиры: ${fats.toStringAsFixed(1)}'),
            Text('Углеводы: ${carbohydrates.toStringAsFixed(1)}'),
            const SizedBox(height: 24),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: () {}, child: const Text('Исправить'))),
              const SizedBox(width: 12),
              Expanded(child: OutlinedButton(onPressed: () {}, child: const Text('Удалить'))),
              const SizedBox(width: 12),
              Expanded(child: FilledButton(onPressed: () { Share.share('Мой анализ: ${calories.toStringAsFixed(0)} ккал'); }, child: const Text('Поделиться'))),
            ])
          ],
        ),
      ),
    );
  }
}
