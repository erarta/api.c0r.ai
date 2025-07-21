# Shared Components

Межсервисные компоненты и контракты для всех сервисов c0r.AI.

## 🏗️ Структура

### 📋 Models (`models/`)
Общие Pydantic модели данных, используемые всеми сервисами.

**Содержит:**
- `user.py` - Модели пользователей и профилей
- `nutrition.py` - Модели питания и калорий
- `payment.py` - Модели платежей и транзакций
- `ml.py` - Модели ML запросов и ответов

### 🔧 Utils (`utils/`)
Общие утилиты и хелперы.

**Содержит:**
- `validation.py` - Валидация данных
- `formatting.py` - Форматирование ответов
- `constants.py` - Общие константы
- `exceptions.py` - Кастомные исключения

### 🔐 Auth (`auth/`)
Компоненты аутентификации и авторизации.

**Содержит:**
- `tokens.py` - Генерация и валидация токенов
- `middleware.py` - Middleware для проверки доступа
- `permissions.py` - Управление правами доступа

### 📡 Contracts (`contracts/`)
API контракты между сервисами.

**Содержит:**
- `api_ml.py` - Контракт API ↔ ML сервиса
- `api_pay.py` - Контракт API ↔ Payment сервиса
- `ml_pay.py` - Контракт ML ↔ Payment сервиса

## 🚀 Использование

```python
# Импорт общих моделей
from shared.models.user import UserProfile
from shared.models.nutrition import NutritionData

# Импорт утилит
from shared.utils.validation import validate_telegram_id
from shared.utils.formatting import format_calories

# Импорт контрактов
from shared.contracts.api_ml import MLAnalysisRequest
```

## 📦 Установка

Shared компоненты устанавливаются как зависимость в каждом сервисе:

```bash
# В requirements.txt каждого сервиса
-e ../../../shared
```

## 🔄 Версионирование

Изменения в shared компонентах должны быть обратно совместимыми или сопровождаться обновлением всех зависимых сервисов.