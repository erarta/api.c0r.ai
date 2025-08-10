import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/widgets.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

void main() {
  test('AppLocalizations returns correct strings', () {
    final en = AppLocalizations(const Locale('en'));
    final ru = AppLocalizations(const Locale('ru'));

    expect(en.t('home.today'), 'Today');
    expect(ru.t('home.today'), 'Сегодня');

    expect(en.t('auth.sign_in'), isNotEmpty);
    expect(ru.t('auth.sign_in'), isNotEmpty);
  });
}
