import 'package:flutter/material.dart';
import 'package:c0r_app/core/ui/components.dart';

class OnboardingActivityScreen extends StatefulWidget {
  const OnboardingActivityScreen({super.key});
  @override
  State<OnboardingActivityScreen> createState() => _OnboardingActivityScreenState();
}

class _OnboardingActivityScreenState extends State<OnboardingActivityScreen> {
  String _activity = 'moderate';
  @override
  Widget build(BuildContext context) {
    return AppScreen(
      title: 'Активность',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppOptionCard<String>(
            value: 'low',
            groupValue: _activity,
            onSelected: (v) => setState(() => _activity = v),
            title: 'Низкая',
            subtitle: 'Мало движения, сидячая работа',
            icon: Icons.self_improvement_outlined,
          ),
          const SizedBox(height: 12),
          AppOptionCard<String>(
            value: 'moderate',
            groupValue: _activity,
            onSelected: (v) => setState(() => _activity = v),
            title: 'Умеренная',
            subtitle: 'Тренировки 2-3 раза в неделю',
            icon: Icons.directions_walk,
          ),
          const SizedBox(height: 12),
          AppOptionCard<String>(
            value: 'high',
            groupValue: _activity,
            onSelected: (v) => setState(() => _activity = v),
            title: 'Высокая',
            subtitle: 'Ежедневные тренировки',
            icon: Icons.fitness_center,
          ),
          const Spacer(),
          AppPrimaryButton(text: 'Далее', onPressed: () {}),
        ],
      ),
    );
  }
}

