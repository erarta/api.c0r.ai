import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'quiz_common.dart';
import 'quiz_state.dart';

class DislikesPage extends ConsumerWidget {
  const DislikesPage({super.key});

  static const items = <String>[
    'Cilantro', 'Blue cheese', 'Olives', 'Anchovies', 'Mushrooms', 'Liver', 'Brussels sprouts'
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(onboardingAnswersProvider).dislikedIngredients.toSet();
    return MultiSelectListPage(
      title: 'Ingredients you dislike',
      subtitle: 'Pick any you prefer to avoid.',
      items: items,
      initialSelected: selected,
      onChanged: (s) => ref.read(onboardingAnswersProvider.notifier).setDislikes(s.toList()),
      onNext: () => Navigator.of(context).pushNamed('/quiz/weight'),
    );
  }
}


