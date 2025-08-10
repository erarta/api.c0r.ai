import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/features/progress/screens/weight_update_screen.dart';
import 'package:c0r_app/features/progress/screens/adjust_goals_screen.dart';
import 'package:c0r_app/features/progress/screens/bmi_screen.dart';
import 'package:c0r_app/features/progress/screens/refer_friend_screen.dart';
import 'package:c0r_app/features/progress/screens/change_goal_screen.dart';

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Прогресс')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Аналитика', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  Container(height: 180, color: Theme.of(context).colorScheme.surfaceContainerHighest),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          ListTile(
            title: const Text('Обновить вес'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const WeightUpdateScreen()),
            ),
          ),
          ListTile(
            title: const Text('Настроить цели'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const AdjustGoalsScreen()),
            ),
          ),
          ListTile(
            title: const Text('BMI'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const BmiScreen()),
            ),
          ),
          ListTile(
            title: const Text('Поменять цель'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ChangeGoalScreen()),
            ),
          ),
          ListTile(
            title: const Text('Пригласить друга'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ReferFriendScreen()),
            ),
          ),
        ],
      ),
    );
  }
}
