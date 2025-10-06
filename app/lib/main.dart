import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:app_links/app_links.dart';
import 'package:modera/config/supabase_config.dart';
import 'package:modera/theme/app_theme.dart';
import 'package:modera/route/router.dart' as modera_router;
import 'package:modera/route/route_constants.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: SupabaseConfig.url,
    anonKey: SupabaseConfig.anonKey,
  );
  runApp(const ProviderScope(child: Zer0App()));
}

class Zer0App extends StatefulWidget {
  const Zer0App({super.key});

  @override
  State<Zer0App> createState() => _Zer0AppState();
}

class _Zer0AppState extends State<Zer0App> {
  late final AppLinks _appLinks;

  @override
  void initState() {
    super.initState();
    _appLinks = AppLinks();
    _setupAuthListener();
    _setupDeepLinkListener();
  }

  void _setupAuthListener() {
    Supabase.instance.client.auth.onAuthStateChange.listen((data) {
      final event = data.event;
      if (event == AuthChangeEvent.signedIn) {
        // User has confirmed their email and signed in
        // Navigate to entry point (home screen)
        modera_router.navigatorKey.currentState?.pushNamedAndRemoveUntil(
          entryPointScreenRoute,
          (route) => false,
        );
      }
    });
  }

  void _setupDeepLinkListener() {
    // Handle incoming links when app is already running
    _appLinks.uriLinkStream.listen((Uri? uri) {
      if (uri != null) {
        _handleDeepLink(uri);
      }
    });

    // Handle the initial link when app is opened from a link
    _appLinks.getInitialLink().then((Uri? uri) {
      if (uri != null) {
        _handleDeepLink(uri);
      }
    });
  }

  void _handleDeepLink(Uri uri) {
    // Supabase handles email verification links automatically
    // The link format is: zer0.c0r.ai://login-callback#access_token=...
    // Supabase SDK will process this and trigger auth state change
    debugPrint('Deep link received: $uri');
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: modera_router.navigatorKey,
      title: 'Zer0',
      theme: AppTheme.lightTheme(context),
      darkTheme: AppTheme.darkTheme(context),
      themeMode: ThemeMode.dark,
      initialRoute: onbordingScreenRoute,
      onGenerateRoute: modera_router.generateRoute,
      debugShowCheckedModeBanner: false,
    );
  }
}
