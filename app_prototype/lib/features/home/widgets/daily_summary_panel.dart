import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:c0r_app/features/home/state/daily_provider.dart';
import 'package:c0r_app/features/home/widgets/macro_row.dart';

class DailySummaryPanel extends ConsumerWidget {
  const DailySummaryPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dailySummaryProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Text('Ошибка: $e'),
      data: (d) => MacroRow(
        calories: d.total.calories,
        proteins: d.total.proteins,
        fats: d.total.fats,
        carbohydrates: d.total.carbohydrates,
        caloriesTarget: 2000,
        proteinsTarget: 120,
        fatsTarget: 70,
        carbsTarget: 250,
      ),
    );
  }
}
