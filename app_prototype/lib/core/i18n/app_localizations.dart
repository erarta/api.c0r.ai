import 'package:flutter/widgets.dart';

class AppLocalizations {
  final Locale locale;
  AppLocalizations(this.locale);

  static const supportedLocales = [Locale('en'), Locale('ru')];

  static const _en = {
    'app.title': 'c0r.ai',
    'home.today': 'Today',
    'home.scan_food': 'Scan food',
    'home.tabs.food': 'Food',
    'home.tabs.health': 'Health',
    'home.recent_analyses': 'Recent analyses',
    'health.coming_soon': 'Health index — soon',
    'progress.title': 'Progress',
    'progress.analytics': 'Analytics',
    'settings.title': 'Settings',
    'settings.language': 'Language',
    'settings.delete_account': 'Delete account',
    'settings.delete_confirm': 'Delete account?',
    'settings.delete_confirm_desc': 'This action is irreversible.',
    'settings.cancel': 'Cancel',
    'settings.delete': 'Delete',
    'auth.title': 'Sign in',
    'auth.sign_in': 'Sign in',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.google_soon': 'Google (soon)',
    'auth.apple_soon': 'Apple (soon)',
    'capture.title': 'Photo',
    'capture.take_photo': 'Take photo',
    'capture.analyze': 'Analyze',
    'capture.result': 'Result',
    'label.title': 'Scan label',
    'history.title': 'History',
    'favorites.title': 'Favorites',
    'favorites.add': 'Add',
    'favorites.save_title': 'Save to favorites',
    'favorites.name_label': 'Name',
    'recipes.title': 'Recipes',
    'weight_update.title': 'Update weight',
    'onboarding.welcome_title': 'Welcome to c0r.ai',
    'onboarding.welcome_subtitle': 'Analyze food, goals, progress. Start?',
    'onboarding.next': 'Next',
    'onboarding.start': 'Start',
    'language.title': 'Language',
    'language.ru': 'Russian',
    'language.en': 'English',
  };

  static const _ru = {
    'app.title': 'c0r.ai',
    'home.today': 'Сегодня',
    'home.scan_food': 'Сфотографировать еду',
    'home.tabs.food': 'Еда',
    'home.tabs.health': 'Здоровье',
    'home.recent_analyses': 'Последние анализы',
    'health.coming_soon': 'Индекс здоровья — скоро',
    'progress.title': 'Прогресс',
    'progress.analytics': 'Аналитика',
    'settings.title': 'Настройки',
    'settings.language': 'Язык',
    'settings.delete_account': 'Удалить аккаунт',
    'settings.delete_confirm': 'Удалить аккаунт?',
    'settings.delete_confirm_desc': 'Это действие необратимо.',
    'settings.cancel': 'Отмена',
    'settings.delete': 'Удалить',
    'auth.title': 'Вход',
    'auth.sign_in': 'Войти',
    'auth.email': 'Email',
    'auth.password': 'Пароль',
    'auth.google_soon': 'Google (скоро)',
    'auth.apple_soon': 'Apple (скоро)',
    'capture.title': 'Фото',
    'capture.take_photo': 'Сделать фото',
    'capture.analyze': 'Анализ',
    'capture.result': 'Результат',
    'label.title': 'Сканировать этикетку',
    'history.title': 'История',
    'favorites.title': 'Избранное',
    'favorites.add': 'Добавить',
    'favorites.save_title': 'Сохранить в избранное',
    'favorites.name_label': 'Название',
    'recipes.title': 'Рецепты',
    'weight_update.title': 'Обновить вес',
    'onboarding.welcome_title': 'Добро пожаловать в c0r.ai',
    'onboarding.welcome_subtitle': 'Анализируй еду, цели, прогресс. Начнём?',
    'onboarding.next': 'Далее',
    'onboarding.start': 'Начать',
    'language.title': 'Язык',
    'language.ru': 'Русский',
    'language.en': 'English',
  };

  static AppLocalizations of(BuildContext context) =>
      Localizations.of<AppLocalizations>(context, AppLocalizations)!;

  String t(String key) {
    final lang = locale.languageCode;
    final map = lang == 'ru' ? _ru : _en;
    return map[key] ?? key;
  }
}

class AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const AppLocalizationsDelegate();
  @override
  bool isSupported(Locale locale) =>
      AppLocalizations.supportedLocales.any((l) => l.languageCode == locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async => AppLocalizations(locale);

  @override
  bool shouldReload(covariant LocalizationsDelegate<AppLocalizations> old) => false;
}

extension L10nContext on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
}
