import 'package:flutter/material.dart';
import 'package:c0r_app/core/router/routes.dart';
import 'package:c0r_app/features/onboarding/screens/onboarding_flow_screen.dart';
import 'package:c0r_app/features/home/screens/home_screen.dart';
import 'package:c0r_app/features/progress/screens/progress_screen.dart';
import 'package:c0r_app/features/settings/screens/settings_screen.dart';

Route<dynamic> onGenerateRoute(RouteSettings settings) {
  switch (settings.name) {
    case AppRoutes.onboardingIntro:
      return MaterialPageRoute(builder: (_) => const OnboardingFlowScreen());
    case AppRoutes.home:
      return MaterialPageRoute(builder: (_) => const HomeScreen());
    case AppRoutes.progress:
      return MaterialPageRoute(builder: (_) => const ProgressScreen());
    case AppRoutes.settings:
      return MaterialPageRoute(builder: (_) => const SettingsScreen());
    default:
      return MaterialPageRoute(
        builder: (_) => const Scaffold(
          body: Center(child: Text('Route not found')),
        ),
      );
  }
}
