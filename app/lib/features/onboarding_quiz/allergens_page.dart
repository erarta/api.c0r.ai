import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'quiz_common.dart';
import 'quiz_state.dart';

class AllergensPage extends ConsumerWidget {
  const AllergensPage({super.key});

  static const items = <String>[
    'Gluten', 'Lactose', 'Peanuts', 'Tree nuts', 'Soy', 'Eggs', 'Fish', 'Shellfish', 'Sesame'
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(onboardingAnswersProvider).allergens.toSet();
    return MultiSelectListPage(
      title: 'Allergens / intolerances',
      subtitle: 'Select any you avoid.',
      items: items,
      initialSelected: selected,
      onChanged: (s) => ref.read(onboardingAnswersProvider.notifier).setAllergens(s.toList()),
      onNext: () => Navigator.of(context).pushNamed('/quiz/cuisines'),
    );
  }
}


