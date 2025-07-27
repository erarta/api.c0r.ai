# 🏗️ План разделения API и бота для быстрого ребрендинга

## 📊 Текущее состояние архитектуры

### Существующая структура
```
services/
├── api/                        # API Service
│   ├── bot/                   # Telegram Bot (Python)
│   ├── edge/                  # Edge API (Cloudflare Workers)
│   └── shared/                # Общие компоненты API
├── ml/                        # ML Service
├── pay/                       # Payment Service
└── README.md
```

### Проблемы текущей архитектуры
1. **Тесная связанность**: Bot и API находятся в одном сервисе
2. **Сложность ребрендинга**: Telegram-специфичная логика смешана с бизнес-логикой
3. **Масштабирование**: Сложно добавить другие интерфейсы (Web, Mobile)
4. **Развертывание**: Bot и API развертываются вместе

## 🎯 Целевая архитектура для ребрендинга

### Новая структура сервисов
```
services/
├── core/                      # 🆕 Core Business Logic Service
│   ├── api/                   # REST API endpoints
│   ├── models/                # Business models
│   ├── services/              # Business services
│   └── shared/                # Core utilities
├── interfaces/                # 🆕 User Interface Services
│   ├── telegram-bot/          # Telegram Bot interface
│   ├── web-app/              # Web application interface
│   ├── mobile-api/           # Mobile API interface
│   └── shared/               # Interface utilities
├── ml/                       # ML Service (без изменений)
├── pay/                      # Payment Service (без изменений)
└── infrastructure/           # 🆕 Infrastructure Services
    ├── auth/                 # Authentication service
    ├── notifications/        # Notification service
    └── file-storage/         # File storage service
```

## 🔄 Этапы миграции

### Этап 1: Выделение Core Service
**Цель**: Создать независимый бизнес-логический сервис

#### Действия:
1. **Создать `services/core/`**
   ```
   services/core/
   ├── api/
   │   ├── endpoints/
   │   │   ├── users.py          # User management
   │   │   ├── nutrition.py      # Nutrition analysis
   │   │   ├── recipes.py        # Recipe generation
   │   │   └── analytics.py      # User analytics
   │   ├── middleware/
   │   └── main.py
   ├── models/
   │   ├── user.py
   │   ├── nutrition.py
   │   ├── recipe.py
   │   └── analytics.py
   ├── services/
   │   ├── user_service.py
   │   ├── nutrition_service.py
   │   ├── recipe_service.py
   │   └── analytics_service.py
   └── shared/
       ├── database.py
       ├── auth.py
       └── utils.py
   ```

2. **Перенести бизнес-логику из `services/api/bot/`**
   - Извлечь логику работы с пользователями
   - Извлечь логику анализа питания
   - Извлечь логику генерации рецептов
   - Создать REST API endpoints

3. **Создать API контракты**
   ```python
   # services/core/api/endpoints/nutrition.py
   @app.post("/analyze")
   async def analyze_nutrition(request: NutritionAnalysisRequest):
       """Analyze nutrition from image"""
       pass
   
   @app.get("/users/{user_id}/history")
   async def get_user_history(user_id: str):
       """Get user analysis history"""
       pass
   ```

### Этап 2: Создание Interface Services
**Цель**: Разделить интерфейсы от бизнес-логики

#### Действия:
1. **Создать `services/interfaces/telegram-bot/`**
   ```
   services/interfaces/telegram-bot/
   ├── handlers/
   │   ├── start.py
   │   ├── photo.py
   │   ├── profile.py
   │   └── payments.py
   ├── middleware/
   ├── utils/
   ├── config/
   │   └── brand_config.py      # 🆕 Брендинг конфигурация
   └── main.py
   ```

2. **Создать систему брендинга**
   ```python
   # services/interfaces/telegram-bot/config/brand_config.py
   class BrandConfig:
       name: str = "c0r.AI"
       welcome_message: str = "Welcome to c0r.AI!"
       logo_url: str = "https://..."
       primary_color: str = "#007bff"
       support_contact: str = "@c0r_support"
       
   # Для нового бренда просто меняем конфигурацию
   class NewBrandConfig(BrandConfig):
       name: str = "FoodAnalyzer"
       welcome_message: str = "Welcome to FoodAnalyzer!"
       logo_url: str = "https://newbrand.com/logo.png"
   ```

3. **Интеграция с Core Service**
   ```python
   # services/interfaces/telegram-bot/handlers/photo.py
   async def handle_photo(message):
       # Загрузить фото
       photo_url = await upload_photo(message.photo)
       
       # Вызвать Core Service
       async with httpx.AsyncClient() as client:
           response = await client.post(
               f"{CORE_SERVICE_URL}/analyze",
               json={"photo_url": photo_url, "user_id": message.from_user.id}
           )
       
       # Отформатировать ответ согласно бренду
       result = response.json()
       formatted_message = format_nutrition_result(result, brand_config)
       await message.reply(formatted_message)
   ```

### Этап 3: Создание Infrastructure Services
**Цель**: Выделить инфраструктурные компоненты

#### Действия:
1. **Создать `services/infrastructure/auth/`**
   - JWT токены
   - Управление сессиями
   - Авторизация между сервисами

2. **Создать `services/infrastructure/notifications/`**
   - Email уведомления
   - Push уведомления
   - SMS уведомления

3. **Создать `services/infrastructure/file-storage/`**
   - Загрузка файлов
   - Обработка изображений
   - CDN интеграция

## 🎨 Система быстрого ребрендинга

### Конфигурационный подход
```python
# config/brands/c0r_ai.py
BRAND_CONFIG = {
    "name": "c0r.AI",
    "domain": "c0r.ai",
    "colors": {
        "primary": "#007bff",
        "secondary": "#6c757d"
    },
    "messages": {
        "welcome": "Welcome to c0r.AI - your AI nutrition assistant!",
        "analysis_complete": "✅ Analysis complete!",
        "error": "❌ Something went wrong"
    },
    "integrations": {
        "telegram_bot_token": "BOT_TOKEN_C0R",
        "support_chat": "@c0r_support"
    }
}

# config/brands/food_analyzer.py
BRAND_CONFIG = {
    "name": "FoodAnalyzer",
    "domain": "foodanalyzer.com",
    "colors": {
        "primary": "#28a745",
        "secondary": "#ffc107"
    },
    "messages": {
        "welcome": "Welcome to FoodAnalyzer - track your nutrition!",
        "analysis_complete": "🍎 Your food analysis is ready!",
        "error": "⚠️ Analysis failed"
    },
    "integrations": {
        "telegram_bot_token": "BOT_TOKEN_FOOD_ANALYZER",
        "support_chat": "@foodanalyzer_help"
    }
}
```

### Шаблонизация интерфейсов
```python
# services/interfaces/telegram-bot/templates/messages.py
class MessageTemplates:
    def __init__(self, brand_config):
        self.config = brand_config
    
    def welcome_message(self, user_name: str) -> str:
        return f"👋 {self.config['messages']['welcome']}\n\nHello, {user_name}!"
    
    def nutrition_result(self, calories: int, proteins: float) -> str:
        return f"""
{self.config['messages']['analysis_complete']}

📊 **Nutrition Analysis**
🔥 Calories: {calories}
🥩 Proteins: {proteins}g

Powered by {self.config['name']}
        """
```

### Docker-compose для мультибрендинга
```yaml
# docker-compose.brands.yml
version: '3.8'
services:
  # c0r.AI brand
  c0r-telegram-bot:
    build: ./services/interfaces/telegram-bot
    environment:
      - BRAND_CONFIG=c0r_ai
      - CORE_SERVICE_URL=http://core-service:8000
    
  # FoodAnalyzer brand
  foodanalyzer-telegram-bot:
    build: ./services/interfaces/telegram-bot
    environment:
      - BRAND_CONFIG=food_analyzer
      - CORE_SERVICE_URL=http://core-service:8000
  
  # Общий Core Service
  core-service:
    build: ./services/core
    ports:
      - "8000:8000"
```

## 🚀 Преимущества новой архитектуры

### Для разработки
1. **Модульность**: Каждый сервис имеет четкую ответственность
2. **Тестируемость**: Легко тестировать бизнес-логику отдельно от интерфейсов
3. **Масштабируемость**: Можно независимо масштабировать каждый компонент

### Для бизнеса
1. **Быстрый ребрендинг**: Новый бренд за несколько часов
2. **Мультиплатформенность**: Легко добавить Web, Mobile интерфейсы
3. **A/B тестирование**: Можно тестировать разные интерфейсы одновременно

### Для эксплуатации
1. **Независимое развертывание**: Каждый сервис развертывается отдельно
2. **Отказоустойчивость**: Сбой одного интерфейса не влияет на другие
3. **Мониторинг**: Четкое разделение метрик по сервисам

## 📋 План реализации

### Неделя 1: Подготовка
- [ ] Создать структуру `services/core/`
- [ ] Определить API контракты между сервисами
- [ ] Создать базовые модели данных

### Неделя 2: Core Service
- [ ] Перенести бизнес-логику в Core Service
- [ ] Создать REST API endpoints
- [ ] Настроить базу данных и миграции

### Неделя 3: Interface Services
- [ ] Создать `services/interfaces/telegram-bot/`
- [ ] Интегрировать с Core Service
- [ ] Создать систему брендинга

### Неделя 4: Infrastructure Services
- [ ] Создать Auth Service
- [ ] Создать File Storage Service
- [ ] Настроить межсервисную аутентификацию

### Неделя 5: Тестирование и документация
- [ ] Написать тесты для всех сервисов
- [ ] Создать документацию по API
- [ ] Подготовить руководство по ребрендингу

## 🎯 Результат

После реализации плана получим:
1. **Модульную архитектуру** с четким разделением ответственности
2. **Систему быстрого ребрендинга** через конфигурационные файлы
3. **Возможность мультиплатформенности** (Telegram, Web, Mobile)
4. **Независимое развертывание** каждого компонента
5. **Готовый шаблон** для создания новых продуктов

Это позволит быстро создавать новые бренды и продукты на базе существующей технологической платформы.