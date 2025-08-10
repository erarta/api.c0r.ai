import "package:flutter/material.dart";
import 'package:c0r_app/features/auth/screens/auth_screen.dart';

class OnboardingIntroScreen extends StatelessWidget {
  const OnboardingIntroScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Spacer(),
            Text("Добро пожаловать в c0r.ai", style: Theme.of(context).textTheme.displayLarge),
            const SizedBox(height: 16),
            Text("Анализируй еду, цели, прогресс. Начнём?", style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const AuthScreen()),
                ),
                child: const Text("Войти"),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

