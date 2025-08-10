import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/core/theme/theme.dart';
import 'package:c0r_app/features/main/main_tabs_screen.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  Future<void> pumpApp(WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: _TestApp()));
    await tester.pumpAndSettle();
  }

  testWidgets('Navigate between Home, Progress, Settings', (tester) async {
    await pumpApp(tester);
    expect(find.text('Сегодня'), findsOneWidget);
    await tester.tap(find.text('Прогресс'));
    await tester.pumpAndSettle();
    expect(find.text('Прогресс'), findsWidgets);
    await tester.tap(find.text('Настройки'));
    await tester.pumpAndSettle();
    expect(find.text('Настройки'), findsWidgets);
  });

  testWidgets('Capture button exists on Home', (tester) async {
    await pumpApp(tester);
    expect(find.byType(FilledButton), findsWidgets);
  });
}

class _TestApp extends StatelessWidget {
  const _TestApp();
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: buildLightTheme(),
      home: const MainTabsScreen(),
      locale: const Locale('ru'),
      localizationsDelegates: const [
        AppLocalizationsDelegate(),
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
    );
  }
}
