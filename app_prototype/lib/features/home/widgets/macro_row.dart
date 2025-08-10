import 'package:flutter/material.dart';
import 'package:c0r_app/core/ui/components.dart';
import 'package:c0r_app/core/theme/theme.dart';

class MacroRow extends StatelessWidget {
  final double calories;
  final double proteins;
  final double fats;
  final double carbohydrates;
  final double? caloriesTarget;
  final double? proteinsTarget;
  final double? fatsTarget;
  final double? carbsTarget;

  const MacroRow({
    super.key,
    required this.calories,
    required this.proteins,
    required this.fats,
    required this.carbohydrates,
    this.caloriesTarget,
    this.proteinsTarget,
    this.fatsTarget,
    this.carbsTarget,
  });

  @override
  Widget build(BuildContext context) {
    final nutrition = Theme.of(context).extension<NutritionColors>()!;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppLabeledProgress(label: 'Калории', value: calories, target: caloriesTarget, color: nutrition.calories),
          const SizedBox(height: 10),
          AppLabeledProgress(label: 'Белки', value: proteins, target: proteinsTarget, color: nutrition.proteins),
          const SizedBox(height: 10),
          AppLabeledProgress(label: 'Жиры', value: fats, target: fatsTarget, color: nutrition.fats),
          const SizedBox(height: 10),
          AppLabeledProgress(label: 'Углеводы', value: carbohydrates, target: carbsTarget, color: nutrition.carbs),
        ],
      ),
    );
  }
}
