import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/features/onboarding_quiz/quiz_state.dart';
import 'package:modera/widgets/language_selector.dart';

class GenderScreen extends ConsumerStatefulWidget {
  const GenderScreen({super.key});

  @override
  ConsumerState<GenderScreen> createState() => _GenderScreenState();
}

class _GenderScreenState extends ConsumerState<GenderScreen> {
  String? _selectedGender;

  @override
  void initState() {
    super.initState();
    // Auto-select first option for quick testing
    _selectedGender = 'male';
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
          value: 0.1,
          backgroundColor: Colors.grey.shade200,
          valueColor: const AlwaysStoppedAnimation<Color>(Colors.black),
        ),
        centerTitle: false,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              Text(
                'Choose your Gender',
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
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
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _GenderOption(
                      label: 'Male',
                      isSelected: _selectedGender == 'male',
                      onTap: () {
                        setState(() {
                          _selectedGender = 'male';
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    _GenderOption(
                      label: 'Female',
                      isSelected: _selectedGender == 'female',
                      onTap: () {
                        setState(() {
                          _selectedGender = 'female';
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    _GenderOption(
                      label: 'Other',
                      isSelected: _selectedGender == 'other',
                      onTap: () {
                        setState(() {
                          _selectedGender = 'other';
                        });
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _selectedGender != null
                      ? () {
                          ref.read(quizStateProvider.notifier).updateGender(_selectedGender!);
                          Navigator.pushNamed(context, '/quiz/activity');
                        }
                      : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _selectedGender != null
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
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _GenderOption extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _GenderOption({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: BoxDecoration(
          color: isSelected ? Colors.black : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? Colors.black : Colors.grey.shade300,
            width: 2,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: isSelected ? Colors.white : Colors.black,
            ),
          ),
        ),
      ),
    );
  }
}