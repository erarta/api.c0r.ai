# Nutrition Insights Error Protection

## Проблема
Ошибка "can't parse entities: Can't find end of the entity starting at byte offset 275" возникала из-за несбалансированных маркеров `**` в русском переводе для `nutrition_no_profile`.

## Решение

### 1. Исправление переводов
- **Файл**: `i18n/ru.py`
- **Проблема**: Несбалансированные маркеры `**` в строке `nutrition_no_profile`
- **Решение**: Добавлен закрывающий маркер `**` для правильного баланса

### 2. Добавление недостающих переводов
- **Файл**: `i18n/ru.py` и `i18n/en.py`
- **Добавлено**: Переводы для всех пунктов меню nutrition insights
- **Результат**: Полная локализация интерфейса

### 3. Улучшение функции санитизации
- **Файл**: `api.c0r.ai/app/handlers/nutrition.py`
- **Функция**: `sanitize_markdown_text()`
- **Улучшения**:
  - Проверка баланса маркеров `**`
  - Обработка тройных и четверных звездочек
  - Удаление паттернов missing translation
  - Исправление пустых bold паттернов

### 4. Комплексное тестирование

#### Тесты для случаев с ненастроенным профилем:
- `test_nutrition_insights_with_none_profile` - критический сценарий с `None` профилем
- `test_nutrition_insights_with_empty_profile` - пустой профиль
- `test_nutrition_insights_with_partial_profile` - частично заполненный профиль
- `test_nutrition_insights_callback_with_none_profile` - callback с `None` профилем
- `test_nutrition_insights_callback_exception_handling` - обработка исключений

#### Тесты для санитизации Markdown:
- `test_sanitize_markdown_text_balanced_bold` - сбалансированные маркеры
- `test_sanitize_markdown_text_unbalanced_bold` - несбалансированные маркеры
- `test_sanitize_markdown_text_triple_asterisks` - тройные звездочки
- `test_sanitize_markdown_text_quadruple_asterisks` - четверные звездочки
- `test_sanitize_markdown_text_empty_bold` - пустые bold паттерны
- `test_sanitize_markdown_text_missing_translation` - паттерны missing translation
- `test_sanitize_markdown_text_russian_text` - русский текст
- `test_sanitize_markdown_text_complex_case` - сложный случай (оригинальная ошибка)

#### Тесты для генерации insights:
- `test_generate_insights_complete_profile` - полный профиль
- `test_generate_insights_russian_language` - русский язык

## Защита от будущих ошибок

### 1. Автоматическая санитизация
Все тексты, отправляемые в Telegram с `parse_mode="Markdown"`, проходят через `sanitize_markdown_text()`.

### 2. Валидация переводов
Тесты проверяют баланс маркеров `**` во всех переводах.

### 3. Обработка исключений
Все функции nutrition insights имеют try-catch блоки с graceful fallback.

### 4. Проверка профиля
Перед генерацией insights проверяется полнота профиля пользователя.

## Результат
- ✅ Ошибка Markdown parsing полностью устранена
- ✅ Все 131 тест проходит успешно
- ✅ Добавлена защита от подобных ошибок в будущем
- ✅ Полная локализация интерфейса
- ✅ Graceful handling всех edge cases

## Мониторинг
Для предотвращения подобных ошибок в будущем:
1. Все новые переводы должны проходить тесты на баланс маркеров
2. Функция `sanitize_markdown_text()` применяется ко всем Markdown текстам
3. Тесты автоматически проверяют критические сценарии
4. Логирование ошибок помогает быстро выявлять проблемы 