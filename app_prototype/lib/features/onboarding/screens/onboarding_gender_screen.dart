import 'package:flutter/material.dart';
import 'package:c0r_app/core/ui/components.dart';

class OnboardingGenderScreen extends StatefulWidget {
  const OnboardingGenderScreen({super.key});
  @override
  State<OnboardingGenderScreen> createState() => _OnboardingGenderScreenState();
}

class _OnboardingGenderScreenState extends State<OnboardingGenderScreen> {
  String _gender = 'male';
  @override
  Widget build(BuildContext context) {
    return AppScreen(
      title: 'Пол',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          AppOptionCard<String>(
            value: 'male',
            groupValue: _gender,
            onSelected: (v) => setState(() => _gender = v),
            title: 'Мужской',
            icon: Icons.male,
          ),
          const SizedBox(height: 12),
          AppOptionCard<String>(
            value: 'female',
            groupValue: _gender,
            onSelected: (v) => setState(() => _gender = v),
            title: 'Женский',
            icon: Icons.female,
          ),
          const Spacer(),
          AppPrimaryButton(text: 'Далее', onPressed: () {}),
        ],
      ),
    );
  }
}

