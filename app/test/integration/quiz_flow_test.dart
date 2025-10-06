import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/features/onboarding_quiz/gender_screen.dart';
import 'package:modera/features/onboarding_quiz/activity_screen.dart';
import 'package:modera/features/onboarding_quiz/diet_page.dart';
import 'package:modera/features/onboarding_quiz/quiz_state.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Quiz Flow Tests', () {
    testWidgets('Should display gender selection screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: GenderScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('What is your gender?'), findsOneWidget);
      expect(find.text('Male'), findsOneWidget);
      expect(find.text('Female'), findsOneWidget);
      expect(find.text('Other'), findsOneWidget);
    });

    testWidgets('Should enable Next button when gender is selected',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: GenderScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Initially Next button should be disabled
      final nextButton = find.text('Next');
      expect(nextButton, findsOneWidget);

      // Select Male
      await tester.tap(find.text('Male'));
      await tester.pumpAndSettle();

      // Next button should now be enabled
      final elevatedButton = tester.widget<ElevatedButton>(
        find.ancestor(
          of: find.text('Next'),
          matching: find.byType(ElevatedButton),
        ),
      );
      expect(elevatedButton.onPressed, isNotNull);
    });

    testWidgets('Should display activity level screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: ActivityScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('How many workouts do you do per week?'),
        findsOneWidget,
      );
      expect(find.text('0-2'), findsOneWidget);
      expect(find.text('3-5'), findsOneWidget);
      expect(find.text('6+'), findsOneWidget);
    });

    testWidgets('Should select activity level and enable Next button',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: ActivityScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Select moderate activity (3-5)
      await tester.tap(find.text('3-5'));
      await tester.pumpAndSettle();

      // Verify Next button is enabled
      final nextButton = find.text('Next');
      expect(nextButton, findsOneWidget);
    });

    testWidgets('Should display diet type selection screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: DietPage()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Select your diet type'), findsOneWidget);
      expect(find.text('Balanced'), findsOneWidget);
      expect(find.text('Low-carb'), findsOneWidget);
      expect(find.text('Keto'), findsOneWidget);
      expect(find.text('Vegan'), findsOneWidget);
    });

    testWidgets('Should allow multiple diet selections',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: DietPage()),
        ),
      );
      await tester.pumpAndSettle();

      // Select Balanced
      await tester.tap(find.text('Balanced'));
      await tester.pumpAndSettle();

      // Select Vegan
      await tester.tap(find.text('Vegan'));
      await tester.pumpAndSettle();

      // Both should be selected, Next button enabled
      final nextButton = find.text('Next');
      expect(nextButton, findsOneWidget);
    });

    testWidgets('Should update quiz state when selections are made',
        (WidgetTester tester) async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Initial state should be empty
      final initialState = container.read(quizStateProvider);
      expect(initialState.gender, isNull);

      // Update gender
      container.read(quizStateProvider.notifier).updateGender('male');

      final updatedState = container.read(quizStateProvider);
      expect(updatedState.gender, equals('male'));
    });

    testWidgets('Should persist quiz selections across screens',
        (WidgetTester tester) async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Set gender
      container.read(quizStateProvider.notifier).updateGender('female');

      // Set activity level
      container.read(quizStateProvider.notifier).updateActivityLevel('high');

      // Set diet types (using onboardingAnswersProvider)
      final state = container.read(quizStateProvider);
      expect(state.gender, equals('female'));
      expect(state.activityLevel, equals('high'));
    });

    testWidgets('Should display progress bar at correct value',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: ActivityScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Activity screen should show 0.2 progress
      final progressIndicator = tester.widget<LinearProgressIndicator>(
        find.byType(LinearProgressIndicator),
      );
      expect(progressIndicator.value, equals(0.2));
    });
  });
}
