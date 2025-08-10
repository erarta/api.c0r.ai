import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/core/pickers/ruler_picker.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/weight_logs_api.dart';

class WeightUpdateScreen extends StatefulWidget {
  const WeightUpdateScreen({super.key});

  @override
  State<WeightUpdateScreen> createState() => _WeightUpdateScreenState();
}

class _WeightUpdateScreenState extends State<WeightUpdateScreen> {
  double _weight = 70.0;
  bool _loading = false;

  Future<void> _save() async {
    setState(() => _loading = true);
    try {
      final api = await ApiClient.create();
      final wl = WeightLogsApi(api);
      final now = DateTime.now();
      final date = '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
      await wl.add(date: date, weightKg: _weight);
      if (!mounted) return;
      Navigator.of(context).pop();
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Обновить вес')),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const SizedBox(height: 24),
            RulerPicker(
              value: _weight,
              min: 30,
              max: 200,
              step: 0.1,
              majorTickEvery: 1,
              labelBuilder: (v) => '${v.toStringAsFixed(1)} кг',
              onChanged: (v) => setState(() => _weight = v),
            ),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _save,
                child: const Text('Сохранить'),
              ),
            )
          ],
        ),
      ),
    );
  }
}
