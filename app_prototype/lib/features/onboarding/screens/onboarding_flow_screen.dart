import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/profiles_api.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_gender_screen.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_activity_screen.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_weight_screen.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_dob_screen.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_goal_screen.dart';
import 'package:c0r_app/core/logging/logger.dart';

final onboardingStateProvider = StateProvider<Map<String, dynamic>>((ref) => {});

class OnboardingFlowScreen extends ConsumerStatefulWidget {
  const OnboardingFlowScreen({super.key});
  @override
  ConsumerState<OnboardingFlowScreen> createState() => _OnboardingFlowScreenState();
}

class _OnboardingFlowScreenState extends ConsumerState<OnboardingFlowScreen> {
  int step = 0;
  late final pages = [
    const OnboardingGenderScreen(),
    const OnboardingActivityScreen(),
    const OnboardingWeightScreen(),
    const OnboardingDobScreen(),
    const OnboardingGoalScreen(),
  ];

  Future<void> _finish() async {
    final data = ref.read(onboardingStateProvider);
    AppLogger.info('Onboarding finish pressed', context: {'step': step, 'payload': data});
    try {
      final api = await ApiClient.create();
      final profiles = ProfilesApi(api);
      await profiles.saveProfile(data);
      if (!mounted) return;
      Navigator.of(context).pushReplacementNamed('/main');
    } catch (e, st) {
      AppLogger.error('Onboarding finish failed', e, st, context: {'payload': data});
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Не удалось сохранить профиль. Попробуйте позже.')));
    }
  }

  void _next() {
    if (step < pages.length - 1) {
      setState(() => step++);
      AppLogger.info('Onboarding next', context: {'step': step});
    } else {
      _finish();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      body: SafeArea(child: pages[step]),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: FilledButton(onPressed: _next, child: Text(step == pages.length - 1 ? 'Начать' : 'Далее')),
        ),
      ),
    );
  }
}

