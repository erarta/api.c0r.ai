import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';
import 'quiz_state.dart';

class AgeScreen extends ConsumerStatefulWidget {
  const AgeScreen({super.key});

  @override
  ConsumerState<AgeScreen> createState() => _AgeScreenState();
}

class _AgeScreenState extends ConsumerState<AgeScreen> {
  late DateTime _selectedDob;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _selectedDob = DateTime(now.year - 25, now.month, now.day);
  }

  int _calculateAge(DateTime dob) {
    final now = DateTime.now();
    int age = now.year - dob.year;
    if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) {
      age--;
    }
    return age;
  }

  @override
  Widget build(BuildContext context) {
    final age = _calculateAge(_selectedDob);
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return Stack(
              children: [
                // Header
                Positioned(
                  left: defaultPadding,
                  right: defaultPadding,
                  top: defaultPadding * 1.5,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('How old are you?', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: defaultPadding / 2),
                      Text('Select your date of birth below.'),
                    ],
                  ),
                ),
                // EXACT center age text
                Align(
                  alignment: const Alignment(0, -0.12),
                  child: Text(
                    '$age years',
                    textAlign: TextAlign.center,
                    style: Theme.of(context)
                        .textTheme
                        .displaySmall
                        ?.copyWith(fontSize: 56, fontWeight: FontWeight.w600),
                  ),
                ),
                // iOS picker just above button
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 120,
                  child: SizedBox(
                    height: 220,
                    child: CupertinoDatePicker(
                      mode: CupertinoDatePickerMode.date,
                      initialDateTime: _selectedDob,
                      maximumDate: DateTime.now(),
                      minimumYear: 1900,
                      onDateTimeChanged: (d) {
                        setState(() => _selectedDob = d);
                      },
                    ),
                  ),
                ),
                Positioned(
                  left: defaultPadding,
                  right: defaultPadding,
                  bottom: defaultPadding,
                  child: ElevatedButton(
                    onPressed: () {
                      ref.read(onboardingAnswersProvider.notifier).setAgeYears(age);
                      // Go to auth before profile details
                      Navigator.pushNamed(context, signUpScreenRoute);
                    },
                    child: const Text('Next'),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}


