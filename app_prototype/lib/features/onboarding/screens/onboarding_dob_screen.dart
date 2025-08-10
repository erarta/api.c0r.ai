import 'package:flutter/material.dart';
import 'package:c0r_app/core/pickers/app_date_picker.dart';
import 'package:c0r_app/core/ui/components.dart';

class OnboardingDobScreen extends StatefulWidget {
  const OnboardingDobScreen({super.key});
  @override
  State<OnboardingDobScreen> createState() => _OnboardingDobScreenState();
}

class _OnboardingDobScreenState extends State<OnboardingDobScreen> {
  DateTime? _dob;
  @override
  Widget build(BuildContext context) {
    return AppScreen(
      title: 'Дата рождения',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppSubtitle(_dob == null ? 'Выбери дату' : _dob!.toLocal().toString().split(' ')[0]),
          const SizedBox(height: 16),
          AppPrimaryButton(
            text: 'Открыть выбор даты',
            onPressed: () async {
              final now = DateTime.now();
              final picked = await AppDatePicker.show(
                context,
                initialDate: DateTime(now.year - 25, now.month, now.day),
                firstDate: DateTime(now.year - 120),
                lastDate: DateTime(now.year - 12),
              );
              if (picked != null) setState(() => _dob = picked);
            },
          ),
          const Spacer(),
          AppPrimaryButton(text: 'Далее', onPressed: _dob != null ? () {} : null),
        ],
      ),
    );
  }
}

