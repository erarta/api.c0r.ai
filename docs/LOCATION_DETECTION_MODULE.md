# Модуль определения локации пользователя

## Обзор

Модуль `UserLocationDetector` предназначен для автоматического определения региона, страны и города пользователя для адаптации анализа еды и рецептов под местную кухню.

## Архитектура модуля

### Структура файлов

```
services/ml/modules/location/
├── detector.py           # Основной класс детектора
├── models.py            # Модели данных
├── providers/           # Провайдеры геолокации
│   ├── telegram.py      # Telegram API
│   ├── ip_geolocation.py # IP геолокация
│   └── timezone.py      # Определение по временной зоне
├── regional_data/       # Региональные данные
│   ├── cuisines.py      # База кухонь по регионам
│   ├── products.py      # Региональные продукты
│   └── languages.py     # Языковые маппинги
└── utils.py            # Утилиты
```

## Основные классы

### LocationInfo

```python
@dataclass
class LocationInfo:
    """Информация о локации пользователя"""
    country_code: str           # ISO код страны (RU, US, DE)
    country_name: str           # Название страны
    region: str                 # Регион/область
    city: Optional[str]         # Город (если доступен)
    timezone: Optional[str]     # Временная зона
    latitude: Optional[float]   # Широта
    longitude: Optional[float]  # Долгота
    confidence: float           # Уверенность в определении (0-1)
    detection_method: str       # Метод определения
```

### RegionalContext

```python
@dataclass
class RegionalContext:
    """Контекст региональной кухни"""
    cuisine_types: List[str]           # Типы кухни (русская, европейская)
    common_products: List[str]         # Распространенные продукты
    seasonal_products: Dict[str, List[str]]  # Сезонные продукты
    cooking_methods: List[str]         # Популярные методы готовки
    measurement_units: str             # Единицы измерения (граммы/унции)
    dietary_preferences: List[str]     # Популярные диеты в регионе
    food_culture_notes: str           # Особенности пищевой культуры
```

### UserLocationDetector

```python
class UserLocationDetector:
    """Основной класс для определения локации пользователя"""
    
    def __init__(self):
        self.telegram_provider = TelegramLocationProvider()
        self.ip_provider = IPGeolocationProvider()
        self.timezone_provider = TimezoneLocationProvider()
        self.regional_data = RegionalDataManager()
    
    async def detect_user_location(self, 
                                 telegram_user_id: str, 
                                 user_language: str,
                                 ip_address: Optional[str] = None,
                                 timezone: Optional[str] = None) -> LocationInfo:
        """
        Определяет локацию пользователя используя несколько методов
        
        Приоритет методов:
        1. Telegram API (если пользователь поделился локацией)
        2. IP геолокация
        3. Определение по временной зоне
        4. Fallback по языку пользователя
        """
        
    def get_regional_cuisine_context(self, location: LocationInfo) -> RegionalContext:
        """Возвращает контекст региональной кухни для локации"""
        
    async def update_user_location_cache(self, 
                                       telegram_user_id: str, 
                                       location: LocationInfo):
        """Кэширует определенную локацию пользователя"""
```

## Провайдеры геолокации

### TelegramLocationProvider

```python
class TelegramLocationProvider:
    """Получение локации через Telegram API"""
    
    async def get_location(self, telegram_user_id: str) -> Optional[LocationInfo]:
        """
        Получает локацию пользователя из Telegram
        - Проверяет последние сообщения с геолокацией
        - Использует Telegram Bot API
        - Возвращает None если локация недоступна
        """
```

### IPGeolocationProvider

```python
class IPGeolocationProvider:
    """Определение локации по IP адресу"""
    
    async def get_location(self, ip_address: str) -> Optional[LocationInfo]:
        """
        Определяет локацию по IP адресу
        - Использует сервисы: MaxMind GeoIP2, IPStack
        - Fallback на бесплатные сервисы
        - Кэширует результаты
        """
```

### TimezoneLocationProvider

```python
class TimezoneLocationProvider:
    """Определение региона по временной зоне"""
    
    def get_location(self, timezone: str) -> Optional[LocationInfo]:
        """
        Определяет вероятную локацию по временной зоне
        - Маппинг timezone -> регион
        - Низкая точность, но быстро
        - Используется как fallback
        """
```

## Региональные данные

### Структура данных по кухням

```python
REGIONAL_CUISINES = {
    "RU": {
        "cuisine_types": ["русская", "советская", "кавказская"],
        "common_products": [
            "гречка", "рис", "картофель", "морковь", "лук", 
            "капуста", "свекла", "огурцы", "помидоры",
            "говядина", "свинина", "курица", "рыба",
            "молоко", "творог", "сметана", "кефир",
            "хлеб", "макароны", "крупы"
        ],
        "seasonal_products": {
            "spring": ["редис", "зеленый лук", "укроп"],
            "summer": ["огурцы", "помидоры", "ягоды", "фрукты"],
            "autumn": ["тыква", "яблоки", "грибы", "капуста"],
            "winter": ["квашеная капуста", "соленые огурцы", "варенье"]
        },
        "cooking_methods": [
            "варка", "жарка", "тушение", "запекание", 
            "засолка", "квашение", "сушка"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["без ограничений", "постная еда"],
        "food_culture_notes": "Традиционная русская кухня с акцентом на сытные блюда, супы, каши и консервацию"
    },
    "US": {
        "cuisine_types": ["американская", "мексиканская", "итальянская"],
        "common_products": [
            "beef", "chicken", "pork", "turkey",
            "potatoes", "corn", "beans", "rice",
            "cheese", "milk", "eggs", "bread",
            "tomatoes", "lettuce", "onions"
        ],
        "seasonal_products": {
            "spring": ["asparagus", "strawberries", "peas"],
            "summer": ["corn", "tomatoes", "berries", "peaches"],
            "autumn": ["pumpkin", "apples", "squash"],
            "winter": ["citrus", "root vegetables", "preserved foods"]
        },
        "cooking_methods": [
            "grilling", "frying", "baking", "roasting", 
            "steaming", "sautéing"
        ],
        "measurement_units": "imperial",
        "dietary_preferences": ["keto", "paleo", "vegan", "gluten-free"],
        "food_culture_notes": "Diverse American cuisine with emphasis on convenience and variety"
    }
}
```

## Алгоритм определения локации

### Пошаговый процесс

1. **Проверка кэша**
   - Проверяем сохраненную локацию пользователя
   - Если данные свежие (< 24 часа), используем их

2. **Telegram API**
   - Запрашиваем последние сообщения с геолокацией
   - Если найдена - используем с высоким приоритетом

3. **IP геолокация**
   - Определяем IP адрес пользователя
   - Используем MaxMind GeoIP2 или аналоги
   - Точность: страна (95%), город (70%)

4. **Временная зона**
   - Получаем timezone из Telegram
   - Маппим на вероятные регионы
   - Низкая точность, но быстро

5. **Fallback по языку**
   - Если все методы неудачны
   - Используем язык интерфейса как индикатор
   - Самая низкая точность

### Система весов и приоритетов

```python
DETECTION_WEIGHTS = {
    "telegram_location": 1.0,      # Максимальная точность
    "ip_geolocation": 0.8,         # Высокая точность
    "timezone_mapping": 0.4,       # Средняя точность
    "language_fallback": 0.2       # Низкая точность
}
```

## Интеграция с ML сервисом

### Использование в анализе еды

```python
# В функции analyze_food_with_openai
async def analyze_food_with_openai(image_bytes: bytes, 
                                 user_language: str,
                                 telegram_user_id: str) -> dict:
    
    # Определяем локацию пользователя
    location_detector = UserLocationDetector()
    location = await location_detector.detect_user_location(
        telegram_user_id, user_language
    )
    
    # Получаем региональный контекст
    regional_context = location_detector.get_regional_cuisine_context(location)
    
    # Адаптируем промпт под регион
    prompt = create_regional_analysis_prompt(
        user_language, regional_context, location
    )
```

### Использование в генерации рецептов

```python
# В функции generate_recipe_with_openai
async def generate_recipe_with_openai(image_url: str, 
                                    user_context: dict,
                                    telegram_user_id: str) -> dict:
    
    # Получаем региональный контекст
    location_detector = UserLocationDetector()
    location = await location_detector.detect_user_location(
        telegram_user_id, user_context.get('language', 'en')
    )
    
    regional_context = location_detector.get_regional_cuisine_context(location)
    
    # Генерируем рецепты с учетом региона
    recipes = await generate_regional_recipes(
        image_url, user_context, regional_context
    )
```

## Кэширование и производительность

### Стратегия кэширования

```python
CACHE_SETTINGS = {
    "location_cache_ttl": 86400,      # 24 часа
    "regional_data_cache_ttl": 604800, # 7 дней
    "ip_geolocation_cache_ttl": 3600,  # 1 час
}
```

### Оптимизации

1. **Асинхронные запросы** - все API вызовы неблокирующие
2. **Параллельное определение** - несколько методов одновременно
3. **Умное кэширование** - разные TTL для разных типов данных
4. **Fallback цепочка** - быстрое переключение при ошибках

## Конфигурация

### Переменные окружения

```bash
# Telegram Bot API
TELEGRAM_BOT_TOKEN=your_bot_token

# IP Geolocation
MAXMIND_LICENSE_KEY=your_maxmind_key
IPSTACK_API_KEY=your_ipstack_key

# Кэширование
REDIS_URL=redis://localhost:6379
LOCATION_CACHE_TTL=86400

# Fallback настройки
DEFAULT_COUNTRY=RU
DEFAULT_TIMEZONE=Europe/Moscow
```

## Тестирование

### Unit тесты

```python
class TestUserLocationDetector:
    
    async def test_telegram_location_detection(self):
        """Тест определения через Telegram API"""
        
    async def test_ip_geolocation_fallback(self):
        """Тест fallback на IP геолокацию"""
        
    def test_regional_context_mapping(self):
        """Тест маппинга локации на региональный контекст"""
        
    async def test_cache_functionality(self):
        """Тест кэширования локации"""
```

### Integration тесты

```python
class TestLocationIntegration:
    
    async def test_ml_service_integration(self):
        """Тест интеграции с ML сервисом"""
        
    async def test_regional_prompt_adaptation(self):
        """Тест адаптации промптов под регион"""
```

## Мониторинг и метрики

### Ключевые метрики

- **Detection Success Rate** - процент успешных определений
- **Detection Method Distribution** - распределение по методам
- **Regional Coverage** - покрытие по регионам
- **Cache Hit Rate** - эффективность кэширования
- **API Response Time** - время ответа провайдеров

### Логирование

```python
logger.info(f"Location detected for user {user_id}: {location.country_code} "
           f"via {location.detection_method} (confidence: {location.confidence})")
```

## Будущие улучшения

1. **Machine Learning модель** для предсказания локации по поведению
2. **Интеграция с социальными сетями** для дополнительных данных
3. **Crowd-sourced данные** от пользователей
4. **Более детальная региональная сегментация** (города, районы)
5. **Адаптивное обучение** на основе обратной связи пользователей

## Заключение

Модуль определения локации обеспечивает точное и быстрое определение региона пользователя для персонализации анализа еды и генерации рецептов. Многоуровневая система fallback гарантирует работоспособность даже при недоступности основных источников данных.