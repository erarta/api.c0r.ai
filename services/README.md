# Services Architecture

Новая модульная архитектура c0r.AI с четким разделением ответственности между сервисами.

## 🏗️ Структура сервисов

### 📡 API Service (`services/api/`)
Обрабатывает все API запросы и взаимодействие с пользователями.

- **`bot/`** - Telegram Bot (Python)
- **`edge/`** - Edge API на Cloudflare Workers (TypeScript)
- **`shared/`** - Общие компоненты API

### 🤖 ML Service (`services/ml/`)
Обрабатывает все ML/AI операции и анализ данных.

- **`openai/`** - OpenAI интеграция
- **`gemini/`** - Google Gemini интеграция
- **`shared/`** - Общие ML компоненты

### 💳 Payment Service (`services/pay/`)
Обрабатывает все платежные операции и биллинг.

- **`stripe/`** - Stripe интеграция
- **`yookassa/`** - YooKassa интеграция
- **`shared/`** - Общие платежные компоненты

## 🔗 Межсервисное взаимодействие

Сервисы взаимодействуют через:
- HTTP API endpoints
- Общие модели данных в `/shared`
- Централизованную конфигурацию в `/common`

## 🚀 Развертывание

Каждый сервис может развертываться независимо:
```bash
# API Service
cd services/api && docker-compose up

# ML Service  
cd services/ml && docker-compose up

# Payment Service
cd services/pay && docker-compose up
```

## 📝 Миграция

Эта структура заменяет старую организацию:
- `api.c0r.ai/` → `services/api/bot/`
- `Cloudflare_Worker/` → `services/api/edge/`
- `ml.c0r.ai/` → `services/ml/`
- `pay.c0r.ai/` → `services/pay/`
- `Payments/` → удалено (дублирование)