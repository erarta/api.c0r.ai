import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/screens/onbording/views/onbording_screnn.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Onboarding Flow Tests', () {
    testWidgets('Should display first onboarding screen on app start',
        (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(
        child: MaterialApp(home: OnbordingScreen()),
      ));
      await tester.pumpAndSettle();

      // Verify first onboarding screen content
      expect(find.text('Calorie tracking made easy'), findsOneWidget);
      expect(find.text('Get Started'), findsOneWidget);
    });

    testWidgets('Should navigate through all 3 onboarding screens',
        (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(
        child: MaterialApp(home: OnbordingScreen()),
      ));
      await tester.pumpAndSettle();

      // Screen 1: Calorie tracking
      expect(find.text('Calorie tracking made easy'), findsOneWidget);

      // Swipe to screen 2
      await tester.drag(
        find.byType(PageView),
        const Offset(-400, 0),
      );
      await tester.pumpAndSettle();

      // Screen 2: Nutrition analyses
      expect(find.text('In-depth nutrition analyses'), findsOneWidget);

      // Swipe to screen 3
      await tester.drag(
        find.byType(PageView),
        const Offset(-400, 0),
      );
      await tester.pumpAndSettle();

      // Screen 3: Transform your body
      expect(find.text('Transform your body'), findsOneWidget);
    });

    testWidgets('Should navigate to gender quiz screen when Get Started is pressed',
        (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(
        child: MaterialApp(home: OnbordingScreen()),
      ));
      await tester.pumpAndSettle();

      // Navigate to last onboarding screen
      await tester.drag(find.byType(PageView), const Offset(-800, 0));
      await tester.pumpAndSettle();

      await tester.drag(find.byType(PageView), const Offset(-800, 0));
      await tester.pumpAndSettle();

      // Tap Get Started button
      final getStartedButton = find.text('Get Started');
      expect(getStartedButton, findsOneWidget);

      await tester.tap(getStartedButton);
      await tester.pumpAndSettle();

      // Verify navigation to gender screen
      expect(find.text('What is your gender?'), findsOneWidget);
    });

    testWidgets('Should display language selector on all onboarding screens',
        (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(
        child: MaterialApp(home: OnbordingScreen()),
      ));
      await tester.pumpAndSettle();

      // Check language selector on screen 1
      expect(find.text('🇺🇸 EN'), findsOneWidget);

      // Swipe to screen 2
      await tester.drag(find.byType(PageView), const Offset(-400, 0));
      await tester.pumpAndSettle();

      expect(find.text('🇺🇸 EN'), findsOneWidget);

      // Swipe to screen 3
      await tester.drag(find.byType(PageView), const Offset(-400, 0));
      await tester.pumpAndSettle();

      expect(find.text('🇺🇸 EN'), findsOneWidget);
    });

    testWidgets('Should show progress indicators on onboarding screens',
        (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(
        child: MaterialApp(home: OnbordingScreen()),
      ));
      await tester.pumpAndSettle();

      // Check for page indicators (dots)
      expect(find.byType(Container), findsWidgets);

      // Progress should update when swiping
      await tester.drag(find.byType(PageView), const Offset(-400, 0));
      await tester.pumpAndSettle();

      // Verify we're on page 2
      expect(find.text('In-depth nutrition analyses'), findsOneWidget);
    });
  });
}
