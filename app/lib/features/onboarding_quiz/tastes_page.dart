import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'quiz_common.dart';
import 'quiz_state.dart';

class TastesPage extends ConsumerWidget {
  const TastesPage({super.key});

  static const items = <String>[
    'Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(onboardingAnswersProvider).tastePreferences.toSet();
    return MultiSelectListPage(
      title: 'Taste preferences',
      subtitle: 'Pick what you typically enjoy.',
      items: items,
      initialSelected: selected,
      onChanged: (s) => ref.read(onboardingAnswersProvider.notifier).setTastes(s.toList()),
      onNext: () => Navigator.of(context).pushNamed('/quiz/allergens'),
    );
  }
}


