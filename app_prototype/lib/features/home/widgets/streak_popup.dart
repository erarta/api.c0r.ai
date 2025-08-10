import 'package:flutter/material.dart';

class StreakPopup extends StatelessWidget {
  final int days;
  final VoidCallback onClose;
  const StreakPopup({super.key, required this.days, required this.onClose});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.local_fire_department, size: 48, color: Colors.orange.shade600),
            const SizedBox(height: 12),
            Text('Серия: $days дней!', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            const Text('Продолжай — ты отлично справляешься!'),
            const SizedBox(height: 16),
            FilledButton(onPressed: onClose, child: const Text('Круто')),
          ],
        ),
      ),
    );
  }
}
