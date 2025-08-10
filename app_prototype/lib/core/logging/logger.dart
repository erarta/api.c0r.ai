import 'dart:developer' as dev;
import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

class AppLogger {
  static void info(String message, {Map<String, Object?> context = const {}}) {
    if (!kReleaseMode) dev.log(message, name: 'INFO', error: context.isEmpty ? null : context);
    Sentry.addBreadcrumb(Breadcrumb(message: message, data: context, level: SentryLevel.info));
  }

  static void warn(String message, {Map<String, Object?> context = const {}}) {
    if (!kReleaseMode) dev.log(message, name: 'WARN', error: context.isEmpty ? null : context);
    Sentry.addBreadcrumb(Breadcrumb(message: message, data: context, level: SentryLevel.warning));
  }

  static void error(String message, Object error, StackTrace stack, {Map<String, Object?> context = const {}}) {
    if (!kReleaseMode) dev.log(message, name: 'ERROR', error: error, stackTrace: stack);
    Sentry.captureException(error, stackTrace: stack, withScope: (scope) {
      scope.addBreadcrumb(Breadcrumb(message: message, data: context, level: SentryLevel.error));
    });
  }
}
