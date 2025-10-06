import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'quiz_common.dart';
import 'quiz_state.dart';

class DietPage extends ConsumerWidget {
  const DietPage({super.key});

  static const items = <String>[
    'Balanced', 'Low-carb', 'Keto', 'Vegan', 'Vegetarian', 'Paleo', 'Mediterranean', 'DASH'
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(onboardingAnswersProvider).dietTypes.toSet();
    return MultiSelectListPage(
      title: 'Select your diet type',
      subtitle: 'Choose one or more that fit you best.',
      items: items,
      initialSelected: selected,
      onChanged: (s) => ref.read(onboardingAnswersProvider.notifier).setDiet(s.toList()),
      onNext: () => Navigator.of(context).pushNamed('/quiz/tastes'),
    );
  }
}


