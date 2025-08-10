import "package:flutter/material.dart";
import 'package:c0r_app/core/ui/components.dart';
import 'package:c0r_app/core/pickers/ruler_picker.dart';

class OnboardingWeightScreen extends StatefulWidget {
  const OnboardingWeightScreen({super.key});
  @override
  State<OnboardingWeightScreen> createState() => _OnboardingWeightScreenState();
}

class _OnboardingWeightScreenState extends State<OnboardingWeightScreen> {
  double _weight = 70.0;
  @override
  Widget build(BuildContext context) {
    return AppScreen(
      title: 'Твой вес',
      child: Column(
        children: [
          const SizedBox(height: 8),
          Text("${_weight.toStringAsFixed(1)} кг", style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 16),
          RulerPicker(
            value: _weight,
            min: 30,
            max: 200,
            step: 0.1,
            majorTickEvery: 1,
            labelBuilder: (v) => "${v.toStringAsFixed(1)} кг",
            onChanged: (v) => setState(() => _weight = v),
          ),
          const Spacer(),
          AppPrimaryButton(text: 'Далее', onPressed: () {}),
        ],
      ),
    );
  }
}

