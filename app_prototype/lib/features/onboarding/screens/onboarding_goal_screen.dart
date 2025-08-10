import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/core/ui/components.dart';

class OnboardingGoalScreen extends StatefulWidget {
  const OnboardingGoalScreen({super.key});
  @override
  State<OnboardingGoalScreen> createState() => _OnboardingGoalScreenState();
}

class _OnboardingGoalScreenState extends State<OnboardingGoalScreen> {
  String _goal = 'lose';
  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Цель')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            AppOptionCard<String>(
              value: 'lose',
              groupValue: _goal,
              onSelected: (v) => setState(() => _goal = v),
              title: 'Похудение',
              subtitle: 'Дефицит калорий для снижения веса',
              icon: Icons.trending_down,
            ),
            const SizedBox(height: 12),
            AppOptionCard<String>(
              value: 'maintain',
              groupValue: _goal,
              onSelected: (v) => setState(() => _goal = v),
              title: 'Поддержание',
              subtitle: 'Баланс калорий для стабильного веса',
              icon: Icons.horizontal_rule,
            ),
            const SizedBox(height: 12),
            AppOptionCard<String>(
              value: 'gain',
              groupValue: _goal,
              onSelected: (v) => setState(() => _goal = v),
              title: 'Набор массы',
              subtitle: 'Профицит калорий для набора',
              icon: Icons.trending_up,
            ),
            const Spacer(),
            AppPrimaryButton(text: 'Далее', onPressed: () {}),
          ],
        ),
      ),
    );
  }
}

