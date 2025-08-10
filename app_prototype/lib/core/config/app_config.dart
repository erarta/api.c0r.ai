import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static bool _loaded = false;

  static Future<void> load() async {
    if (_loaded) return;
    const file = kReleaseMode ? 'assets/env/.env.prod' : 'assets/env/.env.dev';
    await dotenv.load(fileName: file);
    _loaded = true;
  }
}
