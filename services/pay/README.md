# Payment Service

Сервис обработки платежей и биллинга.

## 🏗️ Компоненты

### 💳 Stripe (`stripe/`)
Интеграция со Stripe для международных платежей.

**Функциональность:**
- Создание платежных интентов
- Обработка webhook'ов
- Управление подписками
- Возвраты и диспуты

### 🏦 YooKassa (`yookassa/`)
Интеграция с YooKassa для платежей в России и СНГ.

**Функциональность:**
- Создание платежей
- Обработка уведомлений
- Поддержка различных методов оплаты
- Фискализация чеков

### 🔗 Shared (`shared/`)
Общие компоненты для всех платежных провайдеров.

**Содержит:**
- Модели платежных данных
- Процессоры транзакций
- Утилиты валидации
- Логирование операций

## 🚀 Развертывание

```bash
# Payment Service
cd services/pay && python main.py

# Docker
docker-compose up payment-service
```

## 🔧 Конфигурация

### Переменные окружения:
- `STRIPE_SECRET_KEY` - Секретный ключ Stripe
- `STRIPE_WEBHOOK_SECRET` - Секрет для webhook'ов Stripe
- `YOOKASSA_SHOP_ID` - ID магазина YooKassa
- `YOOKASSA_SECRET_KEY` - Секретный ключ YooKassa
- `PAYMENT_SERVICE_PORT` - Порт сервиса (по умолчанию 8003)

## 📊 API Endpoints

- `POST /stripe/create-payment` - Создание Stripe платежа
- `POST /stripe/webhook` - Webhook для Stripe
- `POST /yookassa/create-payment` - Создание YooKassa платежа
- `POST /yookassa/webhook` - Webhook для YooKassa
- `GET /health` - Проверка состояния сервиса

## 🔒 Безопасность

- Все webhook'ы проверяются на подлинность
- Секретные ключи хранятся в переменных окружения
- Логирование всех платежных операций
- Валидация всех входящих данных