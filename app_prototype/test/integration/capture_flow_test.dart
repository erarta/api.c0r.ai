import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/features/home/screens/capture_screen.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  testWidgets('Capture shows buttons and handles no-image tap gracefully', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      locale: Locale('ru'),
      localizationsDelegates: [
        AppLocalizationsDelegate(),
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      home: CaptureScreen(),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Сделать фото'), findsOneWidget);
    expect(find.text('Анализ'), findsOneWidget);

    await tester.tap(find.text('Анализ'));
    await tester.pump();
  });
}
