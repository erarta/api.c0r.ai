# Промпт для реализации новой архитектуры ML сервиса c0r.AI

## Контекст задачи

Ты - опытный разработчик, который должен реализовать новую архитектуру ML сервиса для анализа еды и генерации рецептов на основе детальной документации. Твоя задача - пошагово внедрить все компоненты согласно архитектурному плану.

## Документация для реализации

Используй следующие документы как основу для реализации (все находятся в `docs/`):

### 1. **Основной план**: [`docs/ML_ARCHITECTURE_PLAN.md`](docs/ML_ARCHITECTURE_PLAN.md)
- Общая архитектура системы
- Выбор SOTA моделей (GPT-4o)
- Структура модулей
- Миграционный план по фазам

### 2. **Модуль локации**: [`docs/LOCATION_DETECTION_MODULE.md`](docs/LOCATION_DETECTION_MODULE.md)
- Реализация `services/ml/modules/location/detector.py`
- Провайдеры геолокации (Telegram, IP, timezone)
- База региональных данных
- Интеграция с ML сервисом

### 3. **Система промптов**: [`docs/ENHANCED_PROMPTS_ARCHITECTURE.md`](docs/ENHANCED_PROMPTS_ARCHITECTURE.md)
- Модуль `services/ml/core/prompts/`
- Региональная адаптация промптов
- Мотивационная система
- Генерация 3 ранжированных рецептов
- Точная оценка веса порций

### 4. **Конфигурация моделей**: [`docs/ML_MODEL_CONFIGURATION.md`](docs/ML_MODEL_CONFIGURATION.md)
- Система `services/ml/core/models/`
- SOTA конфигурация с GPT-4o
- Провайдеры AI (OpenAI, Anthropic, Google)
- Мониторинг производительности

### 5. **Обработка ошибок**: [`docs/FALLBACK_ERROR_HANDLING.md`](docs/FALLBACK_ERROR_HANDLING.md)
- Модуль `services/ml/core/error_handling/`
- Система fallback между моделями
- Circuit breaker pattern
- Retry механизмы

### 6. **Тестирование**: [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md)
- Структура тестов `tests/`
- Unit, integration, e2e тесты
- Performance тестирование
- Mock провайдеры

## План реализации по фазам

### Фаза 1: Подготовка инфраструктуры (1-2 недели)

**Задачи:**
1. **Создать новую структуру модулей** согласно [`ML_ARCHITECTURE_PLAN.md`](docs/ML_ARCHITECTURE_PLAN.md#новая-архитектура-модулей)
2. **Реализовать базовые конфигурации** из [`ML_MODEL_CONFIGURATION.md`](docs/ML_MODEL_CONFIGURATION.md#sota-модели-конфигурация)
3. **Настроить SOTA модели** с GPT-4o как основной моделью

**Файлы для создания:**
```
services/ml/core/models/config/sota_config.py
services/ml/core/models/providers/base_provider.py
services/ml/core/models/providers/openai_provider.py
services/ml/core/models/managers/model_manager.py
```

**Ключевые требования:**
- Использовать GPT-4o для максимального качества
- Вынести все настройки в переменные окружения
- Реализовать базовый мониторинг производительности

### Фаза 2: Модуль определения локации (1 неделя)

**Задачи:**
1. **Реализовать UserLocationDetector** согласно [`LOCATION_DETECTION_MODULE.md`](docs/LOCATION_DETECTION_MODULE.md#основные-классы)
2. **Создать провайдеры геолокации** (Telegram, IP, timezone)
3. **Добавить базу региональных данных** с кухнями и продуктами

**Файлы для создания:**
```
services/ml/modules/location/detector.py
services/ml/modules/location/models.py
services/ml/modules/location/providers/telegram.py
services/ml/modules/location/providers/ip_geolocation.py
services/ml/modules/location/regional_data/cuisines.py
```

**Ключевые требования:**
- Определение региона НЕ по языку, а по геолокации
- Fallback цепочка: Telegram → IP → timezone → язык
- Кэширование результатов на 24 часа

### Фаза 3: Улучшенная система промптов (2 недели)

**Задачи:**
1. **Создать PromptBuilder** из [`ENHANCED_PROMPTS_ARCHITECTURE.md`](docs/ENHANCED_PROMPTS_ARCHITECTURE.md#базовая-архитектура-промптов)
2. **Реализовать региональную адаптацию** промптов под местную кухню
3. **Добавить мотивационную систему** с поощрениями пользователей
4. **Создать генератор 3 рецептов** с ранжированием по соответствию

**Файлы для создания:**
```
services/ml/core/prompts/base/prompt_builder.py
services/ml/core/prompts/food_analysis/enhanced_analysis.py
services/ml/core/prompts/recipe_generation/triple_recipe_generator.py
services/ml/modules/motivation/praise_system.py
services/ml/utils/plate_weight_estimator.py
```

**Ключевые требования:**
- Промпты должны включать региональный контекст
- Обязательная мотивация и объяснение пользы продуктов
- Генерация 3 типов рецептов: персональный, традиционный, креативный
- Точная оценка веса тарелки в граммах и точное определение калоройности (по отдельным продуктам и общей)

### Фаза 4: Система надежности (1 неделя)

**Задачи:**
1. **Реализовать FallbackManager** из [`FALLBACK_ERROR_HANDLING.md`](docs/FALLBACK_ERROR_HANDLING.md#система-fallback)
2. **Добавить Circuit Breaker** для защиты от каскадных отказов
3. **Создать систему retry** с экспоненциальным backoff
4. **Настроить мониторинг ошибок** и алерты

**Файлы для создания:**
```
services/ml/core/error_handling/fallback/fallback_manager.py
services/ml/core/error_handling/recovery/circuit_breaker.py
services/ml/core/error_handling/recovery/retry_manager.py
services/ml/core/error_handling/monitoring/error_tracker.py
```

**Ключевые требования:**
- Fallback цепочка: GPT-4o → GPT-4o-mini → Claude → Gemini
- Circuit breaker с автоматическим восстановлением
- Логирование всех ошибок с классификацией

### Фаза 5: Тестирование (1 неделя)

**Задачи:**
1. **Создать unit тесты** согласно [`TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md#unit-тесты)
2. **Реализовать integration тесты** для проверки взаимодействия модулей
3. **Добавить e2e тесты** полных пользовательских сценариев
4. **Настроить performance тесты** для оптимизации

**Файлы для создания:**
```
tests/unit/test_location_detector.py
tests/unit/test_prompt_builder.py
tests/integration/test_ml_service_integration.py
tests/e2e/test_food_analysis_flow.py
tests/utils/test_helpers.py
```

**Ключевые требования:**
- Покрытие тестами минимум 85%
- Mock всех внешних API
- Тестирование fallback сценариев
- Performance тесты с лимитами времени ответа

## Технические требования

### Обязательные технологии:
- **Python ≥ 3.10** для всех модулей
- **FastAPI** для API endpoints
- **OpenAI Python SDK** для GPT-4o
- **Pydantic** для валидации данных
- **pytest** для тестирования
- **Redis** для кэширования

### Переменные окружения:
```bash
# SOTA модели
ML_DEFAULT_TIER=sota
ML_FOOD_ANALYSIS_MODEL=gpt-4o
ML_RECIPE_GENERATION_MODEL=gpt-4o

# API ключи
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Геолокация
MAXMIND_LICENSE_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here

# Мониторинг
ML_ENABLE_MONITORING=true
ML_PERFORMANCE_TRACKING=true
```

### Стандарты кода:
- Следовать PEP8 и правилам из `.kilocode/rules/`
- Использовать type hints везде
- Добавлять docstrings для всех публичных методов
- Логировать все важные операции

## Критерии успеха

### Функциональные:
✅ **Региональная адаптация**: Корректное определение региона и адаптация промптов
✅ **3 ранжированных рецепта**: Генерация персонального, традиционного и креативного вариантов
✅ **Мотивационная система**: Поощрения и объяснение пользы продуктов в каждом ответе
✅ **Точность анализа**: Использование GPT-4o для максимального качества
✅ **Надежность**: Работающая система fallback при отказах

### Технические:
✅ **Performance**: Время ответа < 30 секунд для анализа, < 60 секунд для рецептов
✅ **Надежность**: Uptime > 99.5% с учетом fallback
✅ **Тестирование**: Покрытие тестами > 85%
✅ **Мониторинг**: Полное логирование и метрики производительности

## Порядок выполнения

1. **Изучи всю документацию** в указанных файлах
2. **Начни с Фазы 1** - создания базовой инфраструктуры
3. **Реализуй модули поэтапно** согласно плану
4. **Тестируй каждый модуль** перед переходом к следующему
5. **Интегрируй с существующим кодом** в `services/ml/main.py`
6. **Проведи полное тестирование** всей системы

## Важные замечания

⚠️ **Не нарушай существующий API** - новая система должна быть обратно совместимой
⚠️ **Обязательно тестируй fallback** - система должна работать даже при отказе основных моделей  
⚠️ **Следи за стоимостью** - GPT-4o дорогая модель, нужен мониторинг расходов
⚠️ **Логируй все операции** - для отладки и мониторинга производительности

## Результат

После реализации система должна:
- Автоматически определять регион пользователя
- Генерировать региональные промпты с мотивацией
- Создавать 3 ранжированных рецепта для каждого запроса
- Точно оценивать вес порций и калорийность
- Объяснять пользу каждого продукта
- Работать стабильно с системой fallback
- Иметь полное покрытие тестами

Начинай реализацию с изучения документации и создания базовой структуры модулей!