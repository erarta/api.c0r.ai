import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:c0r_app/features/main/main_tabs_screen.dart';
import 'package:c0r_app/core/theme/theme.dart';
import 'package:c0r_app/core/router/app_router.dart';
import 'package:c0r_app/core/router/routes.dart';
import 'package:c0r_app/core/config/app_config.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.load();
  final dsn = dotenv.maybeGet('SENTRY_DSN');
  if (dsn != null && dsn.isNotEmpty) {
    await SentryFlutter.init((opts) => opts.dsn = dsn, appRunner: () => runApp(const ProviderScope(child: C0RApp())));
  } else {
    runApp(const ProviderScope(child: C0RApp()));
  }
}

class C0RApp extends StatelessWidget {
  const C0RApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'c0r.ai',
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: ThemeMode.system,
      localizationsDelegates: const [
        AppLocalizationsDelegate(),
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      onGenerateTitle: (ctx) => ctx.l10n.t('app.title'),
      initialRoute: AppRoutes.onboardingIntro,
      onGenerateRoute: (settings) {
        if (settings.name == '/main') {
          return MaterialPageRoute(builder: (_) => const MainTabsScreen());
        }
        return onGenerateRoute(settings);
      },
      debugShowCheckedModeBanner: false,
    );
  }
}

