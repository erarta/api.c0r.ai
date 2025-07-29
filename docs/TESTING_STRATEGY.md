# Стратегия тестирования новой архитектуры ML сервиса

## Обзор

Комплексная стратегия тестирования обеспечивает качество и надежность новой архитектуры ML сервиса с SOTA моделями, региональной адаптацией и системой fallback.

## Архитектура тестирования

### Структура тестов

```
tests/
├── unit/                        # Unit тесты
│   ├── test_location_detector.py
│   ├── test_prompt_builder.py
│   ├── test_model_manager.py
│   ├── test_fallback_manager.py
│   └── test_error_handling.py
├── integration/                 # Integration тесты
│   ├── test_ml_service_integration.py
│   ├── test_provider_integration.py
│   ├── test_regional_adaptation.py
│   └── test_recipe_generation.py
├── e2e/                        # End-to-end тесты
│   ├── test_food_analysis_flow.py
│   ├── test_recipe_generation_flow.py
│   └── test_error_scenarios.py
├── performance/                # Performance тесты
│   ├── test_response_times.py
│   ├── test_concurrent_requests.py
│   └── test_cost_optimization.py
├── fixtures/                   # Тестовые данные
│   ├── images/                 # Тестовые изображения еды
│   ├── prompts/               # Тестовые промпты
│   └── responses/             # Ожидаемые ответы
└── utils/
    ├── test_helpers.py        # Вспомогательные функции
    ├── mock_providers.py      # Mock провайдеры
    └── data_generators.py     # Генераторы тестовых данных
```

## Unit тесты

### Тестирование Location Detector

```python
# tests/unit/test_location_detector.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.ml.modules.location.detector import UserLocationDetector, LocationInfo
from services.ml.modules.location.models import RegionalContext

class TestUserLocationDetector:
    """Тесты модуля определения локации пользователя"""
    
    @pytest.fixture
    def location_detector(self):
        return UserLocationDetector()
    
    @pytest.fixture
    def mock_telegram_response(self):
        return LocationInfo(
            country_code="RU",
            country_name="Russia",
            region="Moscow",
            city="Moscow",
            timezone="Europe/Moscow",
            latitude=55.7558,
            longitude=37.6176,
            confidence=0.95,
            detection_method="telegram_api"
        )
    
    @pytest.mark.asyncio
    async def test_detect_user_location_telegram_success(self, location_detector, mock_telegram_response):
        """Тест успешного определения локации через Telegram API"""
        
        with patch.object(location_detector.telegram_provider, 'get_location', 
                         return_value=mock_telegram_response):
            
            result = await location_detector.detect_user_location(
                telegram_user_id="123456789",
                user_language="ru"
            )
            
            assert result.country_code == "RU"
            assert result.detection_method == "telegram_api"
            assert result.confidence >= 0.9
    
    @pytest.mark.asyncio
    async def test_detect_user_location_fallback_to_ip(self, location_detector):
        """Тест fallback на IP геолокацию при недоступности Telegram API"""
        
        # Mock неудачного Telegram запроса
        with patch.object(location_detector.telegram_provider, 'get_location', 
                         return_value=None):
            
            # Mock успешного IP запроса
            ip_response = LocationInfo(
                country_code="RU",
                country_name="Russia",
                region="Unknown",
                city=None,
                timezone=None,
                latitude=None,
                longitude=None,
                confidence=0.7,
                detection_method="ip_geolocation"
            )
            
            with patch.object(location_detector.ip_provider, 'get_location',
                             return_value=ip_response):
                
                result = await location_detector.detect_user_location(
                    telegram_user_id="123456789",
                    user_language="ru",
                    ip_address="95.108.213.123"
                )
                
                assert result.country_code == "RU"
                assert result.detection_method == "ip_geolocation"
                assert result.confidence == 0.7
    
    def test_get_regional_cuisine_context_russia(self, location_detector):
        """Тест получения регионального контекста для России"""
        
        location = LocationInfo(
            country_code="RU",
            country_name="Russia",
            region="Moscow",
            city="Moscow",
            timezone="Europe/Moscow",
            latitude=55.7558,
            longitude=37.6176,
            confidence=0.95,
            detection_method="telegram_api"
        )
        
        context = location_detector.get_regional_cuisine_context(location)
        
        assert "русская" in context.cuisine_types
        assert "гречка" in context.common_products
        assert context.measurement_units == "metric"
        assert "тушение" in context.cooking_methods
    
    def test_get_regional_cuisine_context_usa(self, location_detector):
        """Тест получения регионального контекста для США"""
        
        location = LocationInfo(
            country_code="US",
            country_name="United States",
            region="California",
            city="San Francisco",
            timezone="America/Los_Angeles",
            latitude=37.7749,
            longitude=-122.4194,
            confidence=0.8,
            detection_method="ip_geolocation"
        )
        
        context = location_detector.get_regional_cuisine_context(location)
        
        assert "американская" in context.cuisine_types
        assert "beef" in context.common_products
        assert context.measurement_units == "imperial"
        assert "grilling" in context.cooking_methods
```

### Тестирование Prompt Builder

```python
# tests/unit/test_prompt_builder.py

import pytest
from services.ml.core.prompts.base.prompt_builder import PromptBuilder
from services.ml.modules.location.models import RegionalContext

class TestPromptBuilder:
    """Тесты конструктора промптов"""
    
    @pytest.fixture
    def prompt_builder(self):
        return PromptBuilder()
    
    @pytest.fixture
    def russian_regional_context(self):
        return RegionalContext(
            cuisine_types=["русская", "советская"],
            common_products=["гречка", "картофель", "морковь"],
            seasonal_products={"winter": ["квашеная капуста", "соленые огурцы"]},
            cooking_methods=["варка", "тушение", "жарка"],
            measurement_units="metric",
            dietary_preferences=["без ограничений"],
            food_culture_notes="Традиционная русская кухня"
        )
    
    @pytest.fixture
    def user_profile(self):
        return {
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "goal": "lose_weight",
            "daily_calories_target": 1800
        }
    
    def test_build_food_analysis_prompt_russian(self, prompt_builder, russian_regional_context, user_profile):
        """Тест создания промпта для анализа еды на русском языке"""
        
        prompt = prompt_builder.build_food_analysis_prompt(
            user_language="ru",
            regional_context=russian_regional_context,
            user_profile=user_profile,
            motivation_level="standard"
        )
        
        # Проверяем наличие ключевых элементов
        assert "русская" in prompt.lower()
        assert "гречка" in prompt.lower()
        assert "граммах" in prompt.lower()
        assert "мотивационное" in prompt.lower()
        assert "польза" in prompt.lower()
        assert "json" in prompt.lower()
    
    def test_build_recipe_generation_prompt_three_recipes(self, prompt_builder, russian_regional_context, user_profile):
        """Тест создания промпта для генерации трех рецептов"""
        
        prompt = prompt_builder.build_recipe_generation_prompt(
            user_language="ru",
            regional_context=russian_regional_context,
            user_profile=user_profile,
            recipe_count=3
        )
        
        # Проверяем наличие требований к трем рецептам
        assert "ТРИ" in prompt.upper()
        assert "ПЕРСОНАЛЬНЫЙ" in prompt.upper()
        assert "ТРАДИЦИОННЫЙ" in prompt.upper()
        assert "КРЕАТИВНЫЙ" in prompt.upper()
        assert "rank" in prompt.lower()
        assert "suitability_score" in prompt.lower()
    
    def test_prompt_adaptation_for_dietary_restrictions(self, prompt_builder, russian_regional_context):
        """Тест адаптации промпта под диетические ограничения"""
        
        vegan_profile = {
            "dietary_preferences": ["vegan"],
            "allergies": ["gluten", "dairy"],
            "goal": "maintain_weight"
        }
        
        prompt = prompt_builder.build_recipe_generation_prompt(
            user_language="en",
            regional_context=russian_regional_context,
            user_profile=vegan_profile,
            recipe_count=3
        )
        
        assert "vegan" in prompt.lower()
        assert "gluten" in prompt.lower()
        assert "dairy" in prompt.lower()
        assert "avoid" in prompt.lower()
```

### Тестирование Model Manager

```python
# tests/unit/test_model_manager.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.ml.core.models.managers.model_manager import ModelManager
from services.ml.core.models.config.sota_config import TaskType, ModelTier

class TestModelManager:
    """Тесты менеджера моделей"""
    
    @pytest.fixture
    def model_manager(self):
        return ModelManager()
    
    @pytest.fixture
    def mock_image_data(self):
        return b"fake_image_data"
    
    @pytest.fixture
    def mock_regional_context(self):
        return {
            "cuisine_types": ["русская"],
            "common_products": ["гречка", "картофель"],
            "measurement_units": "metric"
        }
    
    @pytest.fixture
    def mock_user_profile(self):
        return {
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "goal": "lose_weight",
            "language": "ru"
        }
    
    @pytest.mark.asyncio
    async def test_generate_food_analysis_success(self, model_manager, mock_image_data, mock_regional_context, mock_user_profile):
        """Тест успешной генерации анализа еды"""
        
        expected_response = {
            "content": '{"food_items": [{"name": "гречка", "calories": 100}], "total_nutrition": {"calories": 100}}',
            "model_used": "gpt-4o",
            "provider": "openai",
            "tokens_used": 150,
            "cost": 0.0075,
            "response_time": 2.5,
            "success": True
        }
        
        with patch.object(model_manager.providers["food_analysis_sota_openai"], 
                         'generate_with_retry', return_value=expected_response):
            
            result = await model_manager.generate_food_analysis(
                image_data=mock_image_data,
                user_language="ru",
                regional_context=mock_regional_context,
                user_profile=mock_user_profile,
                tier=ModelTier.SOTA
            )
            
            assert result["success"] is True
            assert result["model_used"] == "gpt-4o"
            assert "гречка" in result["content"]
    
    @pytest.mark.asyncio
    async def test_generate_food_analysis_fallback(self, model_manager, mock_image_data, mock_regional_context, mock_user_profile):
        """Тест fallback при недоступности основной модели"""
        
        # Mock неудачи основной модели
        with patch.object(model_manager.providers["food_analysis_sota_openai"], 
                         'generate_with_retry', side_effect=Exception("API Error")):
            
            # Mock успешного fallback
            fallback_response = {
                "content": '{"food_items": [{"name": "гречка", "calories": 100}]}',
                "model_used": "gpt-4o-mini",
                "provider": "openai",
                "success": True
            }
            
            with patch.object(model_manager.fallback_manager, 'get_fallback_response',
                             return_value=fallback_response):
                
                result = await model_manager.generate_food_analysis(
                    image_data=mock_image_data,
                    user_language="ru",
                    regional_context=mock_regional_context,
                    user_profile=mock_user_profile,
                    tier=ModelTier.SOTA
                )
                
                assert result["success"] is True
                assert result["model_used"] == "gpt-4o-mini"
```

## Integration тесты

### Тестирование интеграции ML сервиса

```python
# tests/integration/test_ml_service_integration.py

import pytest
import asyncio
from fastapi.testclient import TestClient
from services.ml.main import app
from tests.utils.test_helpers import create_test_image, mock_openai_response

class TestMLServiceIntegration:
    """Integration тесты ML сервиса"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_image(self):
        return create_test_image("russian_buckwheat_meal.jpg")
    
    @pytest.mark.asyncio
    async def test_food_analysis_endpoint_integration(self, client, test_image):
        """Тест интеграции endpoint анализа еды"""
        
        with mock_openai_response({
            "food_items": [
                {
                    "name": "гречневая каша",
                    "weight_grams": 150,
                    "calories": 165,
                    "health_benefits": "Богата белком и клетчаткой"
                }
            ],
            "total_nutrition": {
                "calories": 165,
                "proteins": 6.0,
                "fats": 1.2,
                "carbohydrates": 30.0
            },
            "motivation_message": "Отличный выбор! Гречка - это суперфуд!"
        }):
            
            response = client.post(
                "/api/v1/analyze",
                files={"photo": ("test.jpg", test_image, "image/jpeg")},
                data={
                    "telegram_user_id": "123456789",
                    "provider": "openai",
                    "user_language": "ru"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "food_items" in data
            assert "total_nutrition" in data
            assert "motivation_message" in data
            assert data["food_items"][0]["name"] == "гречневая каша"
    
    @pytest.mark.asyncio
    async def test_recipe_generation_endpoint_integration(self, client):
        """Тест интеграции endpoint генерации рецептов"""
        
        user_context = {
            "language": "ru",
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "goal": "lose_weight",
            "has_profile": True
        }
        
        with mock_openai_response({
            "recipes": [
                {
                    "rank": 1,
                    "type": "personal",
                    "suitability_score": 95,
                    "name": "Гречневая каша с овощами",
                    "description": "Идеальный рецепт для похудения"
                },
                {
                    "rank": 2,
                    "type": "traditional",
                    "suitability_score": 85,
                    "name": "Традиционная гречка"
                },
                {
                    "rank": 3,
                    "type": "creative",
                    "suitability_score": 75,
                    "name": "Гречневый салат"
                }
            ]
        }):
            
            response = client.post(
                "/api/v1/generate-recipe",
                data={
                    "image_url": "https://example.com/food.jpg",
                    "telegram_user_id": "123456789",
                    "user_context": json.dumps(user_context)
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "recipes" in data
            assert len(data["recipes"]) == 3
            assert data["recipes"][0]["rank"] == 1
            assert data["recipes"][0]["suitability_score"] >= data["recipes"][1]["suitability_score"]
```

### Тестирование региональной адаптации

```python
# tests/integration/test_regional_adaptation.py

import pytest
from services.ml.modules.location.detector import UserLocationDetector
from services.ml.core.prompts.base.prompt_builder import PromptBuilder

class TestRegionalAdaptation:
    """Тесты региональной адаптации"""
    
    @pytest.fixture
    def location_detector(self):
        return UserLocationDetector()
    
    @pytest.fixture
    def prompt_builder(self):
        return PromptBuilder()
    
    @pytest.mark.asyncio
    async def test_russian_regional_adaptation(self, location_detector, prompt_builder):
        """Тест адаптации под российский регион"""
        
        # Определяем российскую локацию
        with patch.object(location_detector.ip_provider, 'get_location') as mock_ip:
            mock_ip.return_value = LocationInfo(
                country_code="RU",
                country_name="Russia",
                region="Moscow",
                detection_method="ip_geolocation",
                confidence=0.8
            )
            
            location = await location_detector.detect_user_location(
                telegram_user_id="123456789",
                user_language="ru",
                ip_address="95.108.213.123"
            )
            
            # Получаем региональный контекст
            regional_context = location_detector.get_regional_cuisine_context(location)
            
            # Создаем адаптированный промпт
            prompt = prompt_builder.build_food_analysis_prompt(
                user_language="ru",
                regional_context=regional_context,
                user_profile={"goal": "lose_weight"}
            )
            
            # Проверяем адаптацию
            assert "русская" in prompt.lower()
            assert "гречка" in prompt.lower()
            assert "граммах" in prompt.lower()
            assert "тушение" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_american_regional_adaptation(self, location_detector, prompt_builder):
        """Тест адаптации под американский регион"""
        
        with patch.object(location_detector.ip_provider, 'get_location') as mock_ip:
            mock_ip.return_value = LocationInfo(
                country_code="US",
                country_name="United States",
                region="California",
                detection_method="ip_geolocation",
                confidence=0.8
            )
            
            location = await location_detector.detect_user_location(
                telegram_user_id="123456789",
                user_language="en",
                ip_address="192.168.1.1"
            )
            
            regional_context = location_detector.get_regional_cuisine_context(location)
            
            prompt = prompt_builder.build_food_analysis_prompt(
                user_language="en",
                regional_context=regional_context,
                user_profile={"goal": "gain_weight"}
            )
            
            # Проверяем адаптацию
            assert "american" in prompt.lower()
            assert "beef" in prompt.lower()
            assert "grilling" in prompt.lower()
            assert "imperial" in prompt.lower() or "ounces" in prompt.lower()
```

## End-to-End тесты

### Тестирование полного flow анализа еды

```python
# tests/e2e/test_food_analysis_flow.py

import pytest
from tests.utils.test_helpers import create_test_user, upload_test_image

class TestFoodAnalysisFlow:
    """E2E тесты полного flow анализа еды"""
    
    @pytest.mark.asyncio
    async def test_complete_food_analysis_flow_russian_user(self):
        """Тест полного flow для российского пользователя"""
        
        # 1. Создаем тестового пользователя
        user = await create_test_user(
            telegram_id="123456789",
            language="ru",
            location="Moscow, Russia"
        )
        
        # 2. Загружаем изображение еды
        image_data = create_test_image("russian_borscht.jpg")
        
        # 3. Выполняем анализ
        with mock_all_providers():
            result = await analyze_food_complete_flow(
                user_id=user.id,
                image_data=image_data,
                expected_regional_context="russian"
            )
        
        # 4. Проверяем результат
        assert result["success"] is True
        assert "борщ" in result["content"].lower()
        assert "мотивационное" in result["content"].lower()
        assert "польза" in result["content"].lower()
        assert result["regional_adaptation"] == "russian"
        
        # 5. Проверяем сохранение в базе данных
        analysis_log = await get_analysis_log(user.id)
        assert analysis_log is not None
        assert analysis_log.model_used in ["gpt-4o", "gpt-4o-mini"]
    
    @pytest.mark.asyncio
    async def test_complete_recipe_generation_flow_with_ranking(self):
        """Тест полного flow генерации рецептов с ранжированием"""
        
        user = await create_test_user(
            telegram_id="987654321",
            language="ru",
            dietary_preferences=["vegetarian"],
            allergies=["nuts"],
            goal="lose_weight"
        )
        
        image_url = "https://example.com/vegetables.jpg"
        
        with mock_all_providers():
            result = await generate_recipes_complete_flow(
                user_id=user.id,
                image_url=image_url,
                expected_recipe_count=3
            )
        
        # Проверяем результат
        assert result["success"] is True
        assert len(result["recipes"]) == 3
        
        # Проверяем ранжирование
        recipes = result["recipes"]
        assert recipes[0]["rank"] == 1
        assert recipes[1]["rank"] == 2
        assert recipes[2]["rank"] == 3
        
        # Проверяем убывание suitability_score
        assert recipes[0]["suitability_score"] >= recipes[1]["suitability_score"]
        assert recipes[1]["suitability_score"] >= recipes[2]["suitability_score"]
        
        # Проверяем типы рецептов
        recipe_types = [r["type"] for r in recipes]
        assert "personal" in recipe_types
        assert "traditional" in recipe_types
        assert "creative" in recipe_types
```

## Performance тесты

### Тестирование производительности

```python
# tests/performance/test_response_times.py

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Performance тесты"""
    
    @pytest.mark.asyncio
    async def test_food_analysis_response_time(self):
        """Тест времени ответа анализа еды"""
        
        image_data = create_test_image("test_meal.jpg")
        
        start_time = time.time()
        
        result = await analyze_food_with_timeout(
            image_data=image_data,
            user_language="ru",
            timeout=30  # 30 секунд максимум
        )
        
        response_time = time.time() - start_time
        
        assert result["success"] is True
        assert response_time < 30  # Должно быть быстрее 30 секунд
        assert response_time < 10  # Желательно быстрее 10 секунд
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """Тест обработки конкурентных запросов"""
        
        async def single_request(request_id):
            image_data = create_test_image(f"test_meal_{request_id}.jpg")
            return await analyze_food_with_timeout(
                image_data=image_data,
                user_language="ru",
                timeout=60
            )
        
        # Запускаем 10 конкурентных запросов
        tasks = [single_request(i) for i in range(10)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Проверяем результаты
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        assert len(successful_results) >= 8  # Минимум 80% успешных запросов
        assert total_time < 120  # Все запросы должны завершиться за 2 минуты
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self):
        """Тест оптимизации стоимости"""
        
        # Тестируем разные уровни моделей
        test_cases = [
            {"tier": "sota", "expected_max_cost": 0.05},
            {"tier": "premium", "expected_max_cost": 0.01},
            {"tier": "standard", "expected_max_cost": 0.005}
        ]
        
        for case in test_cases:
            image_data = create_test_image("cost_test.jpg")
            
            result = await analyze_food_with_cost_tracking(
                image_data=image_data,
                tier=case["tier"]
            )
            
            assert result["success"] is True
            assert result["cost"] <= case["expected_max_cost"]
```

## Тестирование fallback и error handling

### Тестирование сценариев ошибок

```python
# tests/e2e/test_error_scenarios.py

import pytest
from unittest.mock import patch
from services.ml.core.error_handling.fallback.fallback_manager import FallbackManager

class TestErrorScenarios:
    """Тесты сценариев ошибок и fallback"""
    
    @pytest.mark.asyncio
    async def test_openai_api_failure_fallback(self):
        """Тест fallback при отказе OpenAI API"""
        
        image_data = create_test_image("test_meal.jpg")
        
        # Симулируем отказ OpenAI
        with patch('openai.OpenAI.chat.completions.create', 
                  side_effect=Exception("OpenAI API Error")):
            
            # Должен сработать fallback на другую модель
            result = await analyze_food_with_fallback(
                image_data=image_data,
                user_language="ru"
            )
            
            assert result["success"] is True
            assert result["model_used"] != "gpt-4o"  # Использована fallback модель
            assert result["is_fallback"] is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Тест обработки rate limit ошибок"""
        
        # Симулируем rate limit ошибку
        with patch('openai.OpenAI.chat.completions.create',
                  side_effect=RateLimitError("Rate limit exceeded")):
            
            result = await analyze_food_with_retry(
                image_data=create_test_image("test.jpg"),
                max_retries=3
            )
            
            # Должен либо успешно обработать через retry, либо использовать fallback
            assert result["success"] is True or result["error_handled"] is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self):
        """Тест функциональности circuit breaker"""
        
        fallback_manager = FallbackManager()
        
        # Симулируем множественные отказы
        for i in range(6):  # Больше порога для открытия circuit
            with patch('openai.OpenAI.chat.completions.create',
                      side_effect=Exception("API Error")):
                try:
                    await analyze_food_basic(create_test_image(f"test_{i}.jpg"))
                except:
                    pass
        
        # Circuit должен быть открыт
        circuit_status = fallback_manager.circuit_breaker.get_circuit_status()
        assert any(status["state"] == "open" for status in circuit_status.values())
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Тест graceful degradation при отказе всех моделей"""
        
        # Симулируем отказ всех провайдеров
        with patch('openai.OpenAI.chat.completions.create',
                  side_effect=Exception("OpenAI Error")), \
             patch('anthropic.Anthropic.messages.create',
                  side_effect=Exception("Anthropic Error")):
            
            result = await analyze_food_with_full_fallback(
                image_data=create_test_image("test.jpg"),
                user_language="ru"
            )
            
            # Должен вернуть базовый ответ или кэшированный результат
            assert result["success"] is True
            assert result["degraded_service"] is True
            assert "content" in result
```

## Утилиты для тестирования

### Test Helpers

```python
# tests/utils/test_helpers.py

import io
from PIL import Image
import json
from unittest.mock import patch,