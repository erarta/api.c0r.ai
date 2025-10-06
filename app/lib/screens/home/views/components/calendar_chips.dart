import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../constants.dart';
import '../../../../state/recent_analyses.dart';

class CalendarChips extends ConsumerWidget {
  const CalendarChips({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedDate = ref.watch(selectedDateProvider);
    final days = _buildDays();

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          const SizedBox(width: defaultPadding),
          ...days.map((d) {
            final isActive = _isSameDate(d, selectedDate);
            return Padding(
              padding: const EdgeInsets.only(right: defaultPadding / 2),
              child: _Chip(
                label: _formatLabel(d),
                isActive: isActive,
                onTap: () => ref.read(selectedDateProvider.notifier).state = d,
              ),
            );
          }),
          const SizedBox(width: defaultPadding),
        ],
      ),
    );
  }

  List<DateTime> _buildDays() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    return List.generate(14, (i) => today.subtract(Duration(days: i))).reversed.toList();
  }

  bool _isSameDate(DateTime a, DateTime b) => a.year == b.year && a.month == b.month && a.day == b.day;

  String _formatLabel(DateTime d) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    if (_isSameDate(d, today)) return "Today";
    final wd = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][d.weekday - 1];
    return "$wd ${d.day}";
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.isActive, required this.onTap});
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: const BorderRadius.all(Radius.circular(30)),
      child: Container(
        height: 36,
        padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
        decoration: BoxDecoration(
          color: isActive ? primaryColor : Colors.transparent,
          border: Border.all(color: isActive ? Colors.transparent : Theme.of(context).dividerColor),
          borderRadius: const BorderRadius.all(Radius.circular(30)),
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: isActive ? Colors.white : Theme.of(context).textTheme.bodyLarge!.color,
          ),
        ),
      ),
    );
  }
}


