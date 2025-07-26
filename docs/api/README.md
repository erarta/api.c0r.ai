# 🌐 API Документация c0r.AI

Техническая документация по API endpoints и интеграции.

## 📋 Обзор API

c0r.AI предоставляет RESTful API для анализа изображений еды, управления пользователями и обработки платежей.

### Базовые URL:
- **API Service**: `https://api.c0r.ai`
- **ML Service**: `https://ml.c0r.ai`
- **Payment Service**: `https://pay.c0r.ai`

## 🔐 Аутентификация

Все API endpoints требуют аутентификации через внутренние токены или Supabase JWT.

### Типы аутентификации:
- **Internal Auth** - Для межсервисного взаимодействия
- **User Auth** - Для пользовательских запросов
- **Service Role** - Для административных операций

Подробнее: **[Аутентификация](authentication.md)**

## 📊 Endpoints

### 🔍 Анализ изображений
```http
POST /v1/analyze
Content-Type: multipart/form-data

# Анализ фотографии еды
# Возвращает КБЖУ и детализацию продуктов
```

### 👤 Управление пользователями
```http
GET /users/{user_id}
POST /users
PUT /users/{user_id}
DELETE /users/{user_id}

# CRUD операции с профилями пользователей
```

### 💳 Платежи
```http
POST /payments/invoice
POST /payments/webhook/yookassa
GET /payments/status/{payment_id}

# Создание счетов и обработка платежей
```

### 🍳 Рецепты
```http
POST /recipes/generate
GET /recipes/{recipe_id}
GET /users/{user_id}/recipes

# Генерация и управление рецептами
```

Полный список: **[Endpoints](endpoints.md)**

## ⚡ Rate Limits

API имеет ограничения на количество запросов для предотвращения злоупотреблений:

- **Анализ изображений**: 10 запросов/минуту на пользователя
- **Генерация рецептов**: 5 запросов/минуту на пользователя
- **Общие запросы**: 100 запросов/минуту на IP

Подробнее: **[Rate Limits](rate-limits.md)**

## 📝 Примеры использования

### Анализ изображения
```python
import requests

# Загрузка и анализ фотографии
with open('food_photo.jpg', 'rb') as f:
    response = requests.post(
        'https://api.c0r.ai/v1/analyze',
        files={'photo': f},
        data={
            'telegram_user_id': '123456789',
            'user_language': 'ru'
        },
        headers={'Authorization': 'Bearer your_token'}
    )

result = response.json()
print(f"Калории: {result['kbzhu']['calories']}")
```

### Создание платежа
```python
import requests

# Создание счета для оплаты
response = requests.post(
    'https://pay.c0r.ai/invoice',
    json={
        'user_id': '123456789',
        'plan_id': 'premium',
        'amount': 299.0,
        'description': 'Premium подписка на месяц'
    },
    headers={'Authorization': 'Bearer your_token'}
)

invoice = response.json()
print(f"Ссылка для оплаты: {invoice['payment_url']}")
```

Больше примеров: **[Examples](examples.md)**

## 🔧 SDK и библиотеки

### Python SDK
```bash
pip install c0r-ai-sdk
```

```python
from c0r_ai import Client

client = Client(api_key='your_api_key')
result = client.analyze_image('path/to/image.jpg')
```

### JavaScript SDK
```bash
npm install @c0r-ai/sdk
```

```javascript
import { C0rAI } from '@c0r-ai/sdk';

const client = new C0rAI({ apiKey: 'your_api_key' });
const result = await client.analyzeImage(imageFile);
```

## 📊 Мониторинг и статус

### Health Checks
- **API Service**: `GET /health`
- **ML Service**: `GET /health`
- **Payment Service**: `GET /health`

### Статус сервисов
Проверить текущий статус всех сервисов можно на странице статуса.

## 🚨 Коды ошибок

### HTTP Status Codes
- `200` - Успешный запрос
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

### Формат ошибок
```json
{
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Uploaded file is not a valid image",
    "details": {
      "allowed_formats": ["jpg", "jpeg", "png", "webp"]
    }
  }
}
```

## 📞 Поддержка API

При проблемах с API:

1. Проверьте [примеры использования](examples.md)
2. Изучите [коды ошибок](#-коды-ошибок)
3. Проверьте [статус сервисов](#-мониторинг-и-статус)
4. Создайте Issue с тегом `api`

---

**API Version**: v1  
**Последнее обновление**: 2025-01-26  
**Статус**: Стабильная версия ✅