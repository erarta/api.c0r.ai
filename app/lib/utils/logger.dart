import 'package:flutter/foundation.dart';

// Explicitly define LogLevel enum
enum LogLevel { 
  debug, 
  info, 
  warning, 
  error, 
  network 
}

class AppLogger {
  static void log(
    dynamic message, {
    LogLevel level = LogLevel.debug,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    if (kDebugMode) {
      String emoji;
      switch (level) {
        case LogLevel.debug:
          emoji = '🐞';
          break;
        case LogLevel.info:
          emoji = 'ℹ️';
          break;
        case LogLevel.warning:
          emoji = '⚠️';
          break;
        case LogLevel.error:
          emoji = '❌';
          break;
        case LogLevel.network:
          emoji = '🌐';
          break;
      }

      String logMessage = '$emoji ${level.toString().split('.').last.toUpperCase()}: $message';
      
      print(logMessage);
      
      if (error != null) {
        print('Error Details: $error');
      }
      
      if (stackTrace != null) {
        print('Stack Trace: $stackTrace');
      }
    }
  }
} 