import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:c0r_app/features/auth/screens/auth_screen.dart';

void main() {
  Widget buildApp() => const MaterialApp(
        locale: Locale('ru'),
        localizationsDelegates: [
          AppLocalizationsDelegate(),
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: AppLocalizations.supportedLocales,
        home: AuthScreen(),
      );

  testWidgets('Auth screen shows fields and sign-in button', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Пароль'), findsOneWidget);
    expect(find.text('Войти'), findsOneWidget);
  });
}
