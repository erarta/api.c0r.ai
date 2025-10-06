import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'quiz_common.dart';
import 'quiz_state.dart';

class CuisinesPage extends ConsumerWidget {
  const CuisinesPage({super.key});

  static const items = <String>[
    'Italian', 'Japanese', 'Chinese', 'Indian', 'Thai', 'Mexican', 'Mediterranean', 'French', 'American'
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(onboardingAnswersProvider).cuisines.toSet();
    return MultiSelectListPage(
      title: 'Favorite cuisines',
      subtitle: 'Choose what you like to eat.',
      items: items,
      initialSelected: selected,
      onChanged: (s) => ref.read(onboardingAnswersProvider.notifier).setCuisines(s.toList()),
      onNext: () => Navigator.of(context).pushNamed('/quiz/dislikes'),
    );
  }
}


