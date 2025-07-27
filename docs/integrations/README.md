# 🔌 Интеграции c0r.AI

Документация по интеграции с внешними сервисами и API.

## 📱 Telegram

Интеграция с Telegram Bot API для взаимодействия с пользователями:

- **[Настройка платежей](telegram/payments-setup.md)** - Подключение платежных систем к Telegram боту
- **[Сценарии тестирования](telegram/test-scenarios.md)** - Тестовые сценарии для проверки функциональности бота

### Основные возможности:
- ✅ Обработка команд и сообщений
- ✅ Загрузка и анализ фотографий
- ✅ Интеграция с платежными системами
- ✅ Многоязычная поддержка
- ✅ Inline клавиатуры и меню

## 💳 Платежные системы

Интеграция с платежными провайдерами для монетизации:

- **[Настройка YooKassa](payments/yookassa-setup.md)** - Подключение YooKassa для платежей в России и СНГ
- **[YooKassa Webhooks](payments/yookassa-webhooks.md)** - Настройка уведомлений о платежах
- **[Получение ключей YooKassa](payments/get-yookassa-keys.md)** - Управление API ключами и настройками

### Поддерживаемые провайдеры:
- ✅ **YooKassa** - Основной провайдер для России и СНГ
- 🔄 **Stripe** - Международные платежи (в разработке)
- 🔄 **Telegram Payments** - Встроенные платежи Telegram (планируется)

## 🤖 AI/ML Сервисы

Интеграция с сервисами машинного обучения:

### OpenAI
- **Vision API** - Анализ изображений еды
- **GPT API** - Генерация рецептов и рекомендаций
- **Embeddings** - Семантический поиск по рецептам

### Google Gemini
- **Multimodal API** - Альтернативный анализ изображений
- **Text Generation** - Дополнительная генерация контента

## 🗄️ База данных

Интеграция с Supabase PostgreSQL:

### Основные таблицы:
- `users` - Профили пользователей
- `scans` - История анализов
- `payments` - Платежные транзакции
- `recipes` - Сгенерированные рецепты
- `schema_migrations` - Отслеживание миграций

### Возможности:
- ✅ Row Level Security (RLS)
- ✅ Real-time subscriptions
- ✅ Автоматические бэкапы
- ✅ Масштабирование

## ☁️ Облачные сервисы

### Cloudflare
- **Workers** - Edge API для обработки запросов
- **R2 Storage** - Хранение изображений
- **CDN** - Кэширование и ускорение

### Supabase
- **Database** - PostgreSQL с расширениями
- **Auth** - Аутентификация пользователей
- **Storage** - Файловое хранилище
- **Edge Functions** - Serverless функции

## 📊 Мониторинг и аналитика

### Health Checks
- Автоматическая проверка состояния сервисов
- Мониторинг доступности API
- Алерты при сбоях

### Логирование
- Структурированные логи через Loguru
- Централизованный сбор логов
- Анализ производительности

## 🔧 Настройка интеграций

### Переменные окружения
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_SERVICE_BOT_TOKEN=your_service_bot_token

# Платежи
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# AI/ML
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# База данных
DATABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

### Проверка интеграций
```bash
# Проверка health endpoints
curl https://api.c0r.ai/health
curl https://ml.c0r.ai/health
curl https://pay.c0r.ai/health

# Тестирование платежей
python tests/integration/test_payments.py

# Проверка Telegram бота
python tests/integration/test_telegram_bot.py
```

## 🚨 Устранение неполадок

### Частые проблемы:
1. **Ошибки аутентификации** - Проверьте API ключи
2. **Таймауты запросов** - Увеличьте timeout в настройках
3. **Ошибки webhook'ов** - Проверьте подписи и URL
4. **Проблемы с базой данных** - Проверьте подключение и RLS политики

### Логи и диагностика:
```bash
# Просмотр логов сервисов
docker-compose logs -f api
docker-compose logs -f ml-service
docker-compose logs -f payment-service

# Проверка состояния базы данных
psql $DATABASE_URL -c "SELECT version();"
```

## 📞 Поддержка

При проблемах с интеграциями:

1. Проверьте [руководство по устранению неполадок](../guides/troubleshooting.md)
2. Изучите логи сервисов
3. Проверьте статус внешних сервисов
4. Создайте Issue с тегом `integration`

---

**Последнее обновление**: 2025-01-26  
**Статус**: Активные интеграции ✅