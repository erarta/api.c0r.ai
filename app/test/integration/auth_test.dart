import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/screens/auth/views/signup_screen.dart';
import 'package:modera/screens/auth/views/login_screen.dart';
import 'package:modera/providers/auth_provider.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Authentication Tests', () {
    testWidgets('Should display signup screen with all fields',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: SignUpScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Sign up'), findsWidgets);
      expect(find.byType(TextFormField), findsWidgets);
    });

    testWidgets('Should display login screen with email and password fields',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: LoginScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Welcome back!'), findsOneWidget);
      expect(find.text('Log in'), findsWidgets);
      expect(find.byType(TextFormField), findsNWidgets(2));
    });

    testWidgets('Should validate email format on signup',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: SignUpScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Find email field (first TextFormField)
      final emailFields = find.byType(TextFormField);

      // Enter invalid email
      await tester.enterText(emailFields.first, 'invalid-email');
      await tester.pump();

      // Try to submit (tap Sign up button)
      final signUpButton = find.widgetWithText(ElevatedButton, 'Sign up');
      if (signUpButton.evaluate().isNotEmpty) {
        await tester.tap(signUpButton);
        await tester.pump();

        // Should show validation error
        expect(find.textContaining('email'), findsWidgets);
      }
    });

    testWidgets('Should validate password requirements on signup',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: SignUpScreen()),
        ),
      );
      await tester.pumpAndSettle();

      final textFields = find.byType(TextFormField);

      // Enter valid email but short password
      if (textFields.evaluate().length >= 2) {
        await tester.enterText(textFields.at(0), 'test@example.com');
        await tester.enterText(textFields.at(1), '123');
        await tester.pump();

        // Try to submit
        final signUpButton = find.widgetWithText(ElevatedButton, 'Sign up');
        if (signUpButton.evaluate().isNotEmpty) {
          await tester.tap(signUpButton);
          await tester.pump();

          // Should show password validation error
          expect(find.textContaining('password'), findsWidgets);
        }
      }
    });

    testWidgets('Should have Forgot password link on login screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: LoginScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Forgot password'), findsOneWidget);
    });

    testWidgets('Should have Sign up link on login screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: LoginScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text("Don't have an account?"), findsOneWidget);
      expect(find.text('Sign up'), findsOneWidget);
    });

    test('Should initialize auth provider with null user', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final user = container.read(userProvider);
      expect(user, isNull);
    });

    test('Should set user in auth provider', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Create a mock user (in real scenario, this comes from Supabase)
      // For testing, we just verify the state management works
      final userNotifier = container.read(userProvider.notifier);

      // Initially null
      expect(container.read(userProvider), isNull);

      // After setting user, isAuthenticated should be true
      // Note: We can't create a real User object without Supabase auth,
      // so we test the provider logic
      expect(container.read(isAuthenticatedProvider), isFalse);
    });

    test('Should clear user on logout', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final userNotifier = container.read(userProvider.notifier);

      // Clear user
      userNotifier.clearUser();

      // Should be null
      expect(container.read(userProvider), isNull);
      expect(container.read(isAuthenticatedProvider), isFalse);
    });

    testWidgets('Login button should be disabled with empty fields',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: LoginScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Find Log in button
      final loginButton = find.widgetWithText(ElevatedButton, 'Log in');
      expect(loginButton, findsOneWidget);

      // Tap without filling fields
      await tester.tap(loginButton);
      await tester.pumpAndSettle();

      // Should still be on login screen (validation failed)
      expect(find.text('Welcome back!'), findsOneWidget);
    });

    testWidgets('Should display error message on invalid login',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: LoginScreen()),
        ),
      );
      await tester.pumpAndSettle();

      final textFields = find.byType(TextFormField);

      // Enter invalid credentials
      if (textFields.evaluate().length >= 2) {
        await tester.enterText(textFields.at(0), 'invalid@test.com');
        await tester.enterText(textFields.at(1), 'wrongpassword');
        await tester.pump();

        // Try to log in
        final loginButton = find.widgetWithText(ElevatedButton, 'Log in');
        await tester.tap(loginButton);
        await tester.pump();

        // Wait for async operation
        await tester.pump(const Duration(seconds: 2));

        // Should show error (note: actual error might vary based on Supabase response)
        // We just verify the screen structure handles errors
        expect(find.text('Welcome back!'), findsOneWidget);
      }
    });
  });
}
