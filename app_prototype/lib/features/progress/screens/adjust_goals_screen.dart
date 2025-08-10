import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class AdjustGoalsScreen extends StatefulWidget {
  const AdjustGoalsScreen({super.key});
  @override
  State<AdjustGoalsScreen> createState() => _AdjustGoalsScreenState();
}

class _AdjustGoalsScreenState extends State<AdjustGoalsScreen> {
  double _calories = 2000;
  double _proteins = 120;
  double _fats = 70;
  double _carbs = 250;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Цели')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _slider('Калории', _calories, 1000, 4000, 50, (v) => setState(() => _calories = v)),
          _slider('Белки', _proteins, 40, 250, 5, (v) => setState(() => _proteins = v)),
          _slider('Жиры', _fats, 20, 200, 5, (v) => setState(() => _fats = v)),
          _slider('Углеводы', _carbs, 80, 400, 10, (v) => setState(() => _carbs = v)),
          const SizedBox(height: 24),
          FilledButton(onPressed: () {}, child: const Text('Сохранить')),
        ],
      ),
    );
  }

  Widget _slider(String label, double value, double min, double max, double step, ValueChanged<double> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [Text(label, style: Theme.of(context).textTheme.titleMedium!), Text(value.toStringAsFixed(0))],
        ),
        Slider(value: value, min: min, max: max, divisions: ((max - min) / step).round(), label: value.toStringAsFixed(0), onChanged: onChanged),
        const SizedBox(height: 8),
      ],
    );
  }
}
