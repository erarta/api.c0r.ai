import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/features/onboarding_quiz/quiz_state.dart';
import 'package:modera/widgets/language_selector.dart';

class ActivityScreen extends ConsumerStatefulWidget {
  const ActivityScreen({super.key});

  @override
  ConsumerState<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends ConsumerState<ActivityScreen> {
  String? _selectedActivity;

  @override
  void initState() {
    super.initState();
    // Auto-select first option for quick testing
    _selectedActivity = 'sedentary';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.arrow_back, color: Colors.black),
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: LinearProgressIndicator(
          value: 0.2,
          backgroundColor: Colors.grey.shade200,
          valueColor: const AlwaysStoppedAnimation<Color>(Colors.black),
        ),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: MediaQuery.of(context).size.height -
                          MediaQuery.of(context).padding.top -
                          MediaQuery.of(context).padding.bottom -
                          kToolbarHeight,
              ),
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              Text(
                'How many workouts do you do per week?',
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'This will be used to calibrate your custom plan.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 60),
              _ActivityOption(
                icon: '🚶',
                title: '0-2',
                subtitle: 'Workouts now and then',
                isSelected: _selectedActivity == 'low',
                onTap: () {
                  setState(() {
                    _selectedActivity = 'low';
                  });
                },
              ),
              const SizedBox(height: 16),
              _ActivityOption(
                icon: '🏃',
                title: '3-5',
                subtitle: 'A few workouts per week',
                isSelected: _selectedActivity == 'moderate',
                onTap: () {
                  setState(() {
                    _selectedActivity = 'moderate';
                  });
                },
              ),
              const SizedBox(height: 16),
              _ActivityOption(
                icon: '💪',
                title: '6+',
                subtitle: 'Dedicated athlete',
                isSelected: _selectedActivity == 'high',
                onTap: () {
                  setState(() {
                    _selectedActivity = 'high';
                  });
                },
              ),
              const SizedBox(height: 60),
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _selectedActivity != null
                      ? () {
                          ref.read(quizStateProvider.notifier).updateActivityLevel(_selectedActivity!);
                          Navigator.pushNamed(context, '/quiz/diet');
                        }
                      : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _selectedActivity != null
                        ? Colors.black
                        : Colors.grey.shade300,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    disabledBackgroundColor: Colors.grey.shade300,
                    disabledForegroundColor: Colors.grey.shade500,
                  ),
                  child: const Text(
                    'Next',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
              ],
            ),
          ),
        ),
      ),
    ),
    );
  }
}

class _ActivityOption extends StatelessWidget {
  final String icon;
  final String title;
  final String subtitle;
  final bool isSelected;
  final VoidCallback onTap;

  const _ActivityOption({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
        decoration: BoxDecoration(
          color: isSelected ? Colors.black : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? Colors.black : Colors.grey.shade300,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: isSelected ? Colors.white.withOpacity(0.1) : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Text(
                  icon,
                  style: const TextStyle(fontSize: 24),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? Colors.white : Colors.black,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 14,
                      color: isSelected ? Colors.white70 : Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}