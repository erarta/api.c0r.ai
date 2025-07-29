# Конфигурационная система ML моделей

## Обзор

Новая конфигурационная система обеспечивает гибкое управление SOTA моделями, их параметрами и провайдерами для максимального качества анализа еды и генерации рецептов.

## Архитектура конфигурационной системы

### Структура модулей

```
services/ml/core/models/
├── config/                      # Конфигурация моделей
│   ├── sota_config.py          # SOTA модели и их настройки
│   ├── provider_config.py      # Конфигурация провайдеров
│   ├── task_config.py          # Настройки для разных задач
│   └── environment_config.py   # Переменные окружения
├── providers/                   # Провайдеры AI
│   ├── openai_provider.py      # OpenAI GPT-4o
│   ├── anthropic_provider.py   # Claude 3.5 Sonnet
│   ├── google_provider.py      # Gemini Pro Vision
│   └── base_provider.py        # Базовый класс провайдера
├── managers/                    # Менеджеры моделей
│   ├── model_manager.py        # Основной менеджер
│   ├── fallback_manager.py     # Система fallback
│   └── performance_monitor.py  # Мониторинг производительности
└── utils/
    ├── model_validator.py      # Валидация моделей
    └── cost_calculator.py      # Расчет стоимости
```

## SOTA модели конфигурация

### Основная конфигурация

```python
# services/ml/core/models/config/sota_config.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class ModelTier(Enum):
    """Уровни качества моделей"""
    SOTA = "sota"           # Максимальное качество
    PREMIUM = "premium"     # Высокое качество
    STANDARD = "standard"   # Стандартное качество
    BUDGET = "budget"       # Экономичный вариант

class TaskType(Enum):
    """Типы задач ML"""
    FOOD_ANALYSIS = "food_analysis"
    RECIPE_GENERATION = "recipe_generation"
    NUTRITION_EXPLANATION = "nutrition_explanation"
    MOTIVATION_GENERATION = "motivation_generation"

@dataclass
class ModelConfig:
    """Конфигурация модели"""
    name: str
    provider: str
    tier: ModelTier
    max_tokens: int
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    timeout: int
    retry_attempts: int
    cost_per_1k_tokens: float
    vision_support: bool
    json_mode: bool
    system_prompt_support: bool

# SOTA конфигурация для максимального качества
SOTA_MODEL_CONFIGS = {
    TaskType.FOOD_ANALYSIS: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=2000,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=60,
            retry_attempts=3,
            cost_per_1k_tokens=0.005,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.PREMIUM,
            max_tokens=1500,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=45,
            retry_attempts=3,
            cost_per_1k_tokens=0.00015,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.STANDARD: ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider="anthropic",
            tier=ModelTier.STANDARD,
            max_tokens=1500,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=45,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            vision_support=True,
            json_mode=False,
            system_prompt_support=True
        )
    },
    
    TaskType.RECIPE_GENERATION: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=3000,
            temperature=0.3,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            timeout=90,
            retry_attempts=3,
            cost_per_1k_tokens=0.005,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider="anthropic",
            tier=ModelTier.PREMIUM,
            max_tokens=2500,
            temperature=0.3,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=75,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            vision_support=True,
            json_mode=False,
            system_prompt_support=True
        )
    }
}
```

### Динамическая конфигурация

```python
# services/ml/core/models/config/environment_config.py

import os
from typing import Optional

class EnvironmentConfig:
    """Конфигурация из переменных окружения"""
    
    # Основные настройки
    DEFAULT_TIER = os.getenv("ML_DEFAULT_TIER", "sota")
    FALLBACK_ENABLED = os.getenv("ML_FALLBACK_ENABLED", "true").lower() == "true"
    COST_LIMIT_PER_REQUEST = float(os.getenv("ML_COST_LIMIT_PER_REQUEST", "0.10"))
    
    # Модели для анализа еды
    FOOD_ANALYSIS_PRIMARY_MODEL = os.getenv("ML_FOOD_ANALYSIS_MODEL", "gpt-4o")
    FOOD_ANALYSIS_FALLBACK_MODEL = os.getenv("ML_FOOD_ANALYSIS_FALLBACK", "gpt-4o-mini")
    FOOD_ANALYSIS_MAX_TOKENS = int(os.getenv("ML_FOOD_ANALYSIS_MAX_TOKENS", "2000"))
    FOOD_ANALYSIS_TEMPERATURE = float(os.getenv("ML_FOOD_ANALYSIS_TEMPERATURE", "0.1"))
    
    # Модели для генерации рецептов
    RECIPE_GENERATION_PRIMARY_MODEL = os.getenv("ML_RECIPE_GENERATION_MODEL", "gpt-4o")
    RECIPE_GENERATION_FALLBACK_MODEL = os.getenv("ML_RECIPE_GENERATION_FALLBACK", "claude-3-5-sonnet-20241022")
    RECIPE_GENERATION_MAX_TOKENS = int(os.getenv("ML_RECIPE_GENERATION_MAX_TOKENS", "3000"))
    RECIPE_GENERATION_TEMPERATURE = float(os.getenv("ML_RECIPE_GENERATION_TEMPERATURE", "0.3"))
    
    # API ключи
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Прокси настройки
    HTTP_PROXY = os.getenv("HTTP_PROXY")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY")
    
    # Мониторинг и логирование
    ENABLE_MODEL_MONITORING = os.getenv("ML_ENABLE_MONITORING", "true").lower() == "true"
    LOG_MODEL_RESPONSES = os.getenv("ML_LOG_RESPONSES", "false").lower() == "true"
    PERFORMANCE_TRACKING = os.getenv("ML_PERFORMANCE_TRACKING", "true").lower() == "true"
```

## Провайдеры AI

### Базовый провайдер

```python
# services/ml/core/models/providers/base_provider.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
from dataclasses import dataclass

@dataclass
class ModelResponse:
    """Ответ от модели"""
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    response_time: float
    success: bool
    error_message: Optional[str] = None

class BaseAIProvider(ABC):
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Инициализация клиента провайдера"""
        pass
    
    @abstractmethod
    async def generate_response(self, 
                              prompt: str,
                              image_data: Optional[bytes] = None,
                              system_prompt: Optional[str] = None) -> ModelResponse:
        """Генерация ответа от модели"""
        pass
    
    @abstractmethod
    def validate_response(self, response: str) -> bool:
        """Валидация ответа модели"""
        pass
    
    async def generate_with_retry(self, 
                                prompt: str,
                                image_data: Optional[bytes] = None,
                                system_prompt: Optional[str] = None) -> ModelResponse:
        """Генерация с повторными попытками"""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = await self.generate_response(prompt, image_data, system_prompt)
                if response.success:
                    return response
                last_error = response.error_message
            except Exception as e:
                last_error = str(e)
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return ModelResponse(
            content="",
            model_used=self.config.name,
            provider=self.config.provider,
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            success=False,
            error_message=f"Failed after {self.config.retry_attempts} attempts: {last_error}"
        )
```

### OpenAI провайдер

```python
# services/ml/core/models/providers/openai_provider.py

import openai
import base64
import json
from typing import Optional
import httpx

class OpenAIProvider(BaseAIProvider):
    """Провайдер для OpenAI GPT-4o"""
    
    def _initialize_client(self):
        """Инициализация OpenAI клиента"""
        api_key = EnvironmentConfig.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not provided")
        
        # Настройка прокси если необходимо
        http_client = None
        if EnvironmentConfig.HTTP_PROXY or EnvironmentConfig.HTTPS_PROXY:
            http_client = httpx.Client(
                proxies={
                    "http://": EnvironmentConfig.HTTP_PROXY,
                    "https://": EnvironmentConfig.HTTPS_PROXY
                }
            )
        
        self.client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
    
    async def generate_response(self, 
                              prompt: str,
                              image_data: Optional[bytes] = None,
                              system_prompt: Optional[str] = None) -> ModelResponse:
        """Генерация ответа через OpenAI API"""
        start_time = time.time()
        
        try:
            messages = []
            
            # Системный промпт
            if system_prompt and self.config.system_prompt_support:
                messages.append({"role": "system", "content": system_prompt})
            
            # Пользовательский промпт с изображением
            user_content = [{"type": "text", "text": prompt}]
            
            if image_data and self.config.vision_support:
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high"
                    }
                })
            
            messages.append({"role": "user", "content": user_content})
            
            # Параметры запроса
            request_params = {
                "model": self.config.name,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty,
                "timeout": self.config.timeout
            }
            
            # JSON режим если поддерживается
            if self.config.json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            # Выполнение запроса
            response = await self.client.chat.completions.create(**request_params)
            
            # Обработка ответа
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = tokens_used * self.config.cost_per_1k_tokens / 1000
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=content,
                model_used=self.config.name,
                provider=self.config.provider,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ModelResponse(
                content="",
                model_used=self.config.name,
                provider=self.config.provider,
                tokens_used=0,
                cost=0.0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    def validate_response(self, response: str) -> bool:
        """Валидация ответа OpenAI"""
        if not response or len(response.strip()) == 0:
            return False
        
        # Если ожидается JSON, проверяем парсинг
        if self.config.json_mode:
            try:
                json.loads(response)
                return True
            except json.JSONDecodeError:
                return False
        
        return True
```

## Менеджер моделей

### Основной менеджер

```python
# services/ml/core/models/managers/model_manager.py

from typing import Dict, Optional, List
import asyncio
from enum import Enum

class ModelManager:
    """Основной менеджер ML моделей"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.fallback_manager = FallbackManager()
        self.performance_monitor = PerformanceMonitor()
        self.cost_calculator = CostCalculator()
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Инициализация всех доступных провайдеров"""
        # OpenAI провайдеры
        if EnvironmentConfig.OPENAI_API_KEY:
            for task_type in TaskType:
                for tier in ModelTier:
                    if tier in SOTA_MODEL_CONFIGS.get(task_type, {}):
                        config = SOTA_MODEL_CONFIGS[task_type][tier]
                        if config.provider == "openai":
                            provider_key = f"{task_type.value}_{tier.value}_openai"
                            self.providers[provider_key] = OpenAIProvider(config)
        
        # Anthropic провайдеры
        if EnvironmentConfig.ANTHROPIC_API_KEY:
            # Аналогично для Anthropic
            pass
    
    async def generate_food_analysis(self,
                                   image_data: bytes,
                                   user_language: str,
                                   regional_context: dict,
                                   user_profile: dict,
                                   tier: ModelTier = ModelTier.SOTA) -> ModelResponse:
        """Генерация анализа еды"""
        
        # Получаем конфигурацию модели
        config = SOTA_MODEL_CONFIGS[TaskType.FOOD_ANALYSIS][tier]
        provider_key = f"{TaskType.FOOD_ANALYSIS.value}_{tier.value}_{config.provider}"
        
        if provider_key not in self.providers:
            # Fallback на доступную модель
            return await self.fallback_manager.get_fallback_response(
                TaskType.FOOD_ANALYSIS, image_data, user_language, regional_context
            )
        
        provider = self.providers[provider_key]
        
        # Создаем промпт
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_food_analysis_prompt(
            user_language, regional_context, user_profile
        )
        
        # Генерируем ответ
        response = await provider.generate_with_retry(prompt, image_data)
        
        # Мониторинг производительности
        if EnvironmentConfig.ENABLE_MODEL_MONITORING:
            await self.performance_monitor.log_request(
                task_type=TaskType.FOOD_ANALYSIS,
                model_used=response.model_used,
                response_time=response.response_time,
                tokens_used=response.tokens_used,
                cost=response.cost,
                success=response.success
            )
        
        return response
    
    async def generate_triple_recipes(self,
                                    image_url: str,
                                    user_context: dict,
                                    regional_context: dict,
                                    tier: ModelTier = ModelTier.SOTA) -> ModelResponse:
        """Генерация трех рецептов"""
        
        config = SOTA_MODEL_CONFIGS[TaskType.RECIPE_GENERATION][tier]
        provider_key = f"{TaskType.RECIPE_GENERATION.value}_{tier.value}_{config.provider}"
        
        if provider_key not in self.providers:
            return await self.fallback_manager.get_fallback_response(
                TaskType.RECIPE_GENERATION, image_url, user_context, regional_context
            )
        
        provider = self.providers[provider_key]
        
        # Создаем промпт для тройной генерации
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_recipe_generation_prompt(
            user_context.get('language', 'en'),
            regional_context,
            user_context,
            recipe_count=3
        )
        
        # Генерируем ответ
        response = await provider.generate_with_retry(prompt, image_url)
        
        # Мониторинг
        if EnvironmentConfig.ENABLE_MODEL_MONITORING:
            await self.performance_monitor.log_request(
                task_type=TaskType.RECIPE_GENERATION,
                model_used=response.model_used,
                response_time=response.response_time,
                tokens_used=response.tokens_used,
                cost=response.cost,
                success=response.success
            )
        
        return response
```

### Система Fallback

```python
# services/ml/core/models/managers/fallback_manager.py

class FallbackManager:
    """Менеджер fallback стратегий"""
    
    def __init__(self):
        self.fallback_chains = self._build_fallback_chains()
    
    def _build_fallback_chains(self) -> Dict[TaskType, List[ModelTier]]:
        """Строит цепочки fallback для каждого типа задач"""
        return {
            TaskType.FOOD_ANALYSIS: [
                ModelTier.SOTA,      # gpt-4o
                ModelTier.PREMIUM,   # gpt-4o-mini
                ModelTier.STANDARD   # claude-3-5-sonnet
            ],
            TaskType.RECIPE_GENERATION: [
                ModelTier.SOTA,      # gpt-4o
                ModelTier.PREMIUM,   # claude-3-5-sonnet
                ModelTier.STANDARD   # gpt-4o-mini
            ]
        }
    
    async def get_fallback_response(self,
                                  task_type: TaskType,
                                  *args, **kwargs) -> ModelResponse:
        """Получает ответ используя fallback цепочку"""
        
        fallback_chain = self.fallback_chains.get(task_type, [])
        last_error = None
        
        for tier in fallback_chain:
            try:
                config = SOTA_MODEL_CONFIGS[task_type][tier]
                provider_key = f"{task_type.value}_{tier.value}_{config.provider}"
                
                if provider_key in self.providers:
                    provider = self.providers[provider_key]
                    response = await provider.generate_with_retry(*args, **kwargs)
                    
                    if response.success:
                        return response
                    
                    last_error = response.error_message
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        # Если все fallback не сработали
        return ModelResponse(
            content="",
            model_used="fallback_failed",
            provider="none",
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            success=False,
            error_message=f"All fallback options failed: {last_error}"
        )
```

## Мониторинг производительности

### Performance Monitor

```python
# services/ml/core/models/managers/performance_monitor.py

from dataclasses import dataclass
from typing import Dict, List
import asyncio
import json
from datetime import datetime, timedelta

@dataclass
class ModelMetrics:
    """Метрики производительности модели"""
    model_name: str
    provider: str
    task_type: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    avg_tokens_per_request: float
    total_cost: float
    success_rate: float
    last_updated: datetime

class PerformanceMonitor:
    """Мониторинг производительности моделей"""
    
    def __init__(self):
        self.metrics: Dict[str, ModelMetrics] = {}
        self.request_history: List[Dict] = []
        self.max_history_size = 10000
    
    async def log_request(self,
                        task_type: TaskType,
                        model_used: str,
                        response_time: float,
                        tokens_used: int,
                        cost: float,
                        success: bool,
                        provider: str = "unknown"):
        """Логирование запроса к модели"""
        
        # Создаем ключ метрики
        metric_key = f"{task_type.value}_{model_used}_{provider}"
        
        # Обновляем метрики
        if metric_key not in self.metrics:
            self.metrics[metric_key] = ModelMetrics(
                model_name=model_used,
                provider=provider,
                task_type=task_type.value,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.0,
                avg_tokens_per_request=0.0,
                total_cost=0.0,
                success_rate=0.0,
                last_updated=datetime.now()
            )
        
        metrics = self.metrics[metric_key]
        
        # Обновляем счетчики
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Обновляем средние значения
        metrics.avg_response_time = (
            (metrics.avg_response_time * (metrics.total_requests - 1) + response_time) 
            / metrics.total_requests
        )
        
        metrics.avg_tokens_per_request = (
            (metrics.avg_tokens_per_request * (metrics.total_requests - 1) + tokens_used)
            / metrics.total_requests
        )
        
        metrics.total_cost += cost
        metrics.success_rate = metrics.successful_requests / metrics.total_requests
        metrics.last_updated = datetime.now()
        
        # Добавляем в историю
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type.value,
            "model": model_used,
            "provider": provider,
            "response_time": response_time,
            "tokens_used": tokens_used,
            "cost": cost,
            "success": success
        })
        
        # Ограничиваем размер истории
        if len(self.request_history) > self.max_history_size:
            self.request_history = self.request_history[-self.max_history_size:]
    
    def get_model_metrics(self, task_type: Optional[TaskType] = None) -> Dict[str, ModelMetrics]:
        """Получение метрик моделей"""
        if task_type:
            return {k: v for k, v in self.metrics.items() 
                   if v.task_type == task_type.value}
        return self.metrics
    
    def get_performance_report(self, hours: int = 24) -> Dict:
        """Генерация отчета о производительности"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_requests = [
            req for req in self.request_history 
            if datetime.fromisoformat(req["timestamp"]) > cutoff_time
        ]
        
        if not recent_requests:
            return {"message": "No recent requests found"}
        
        # Агрегированная статистика
        total_requests = len(recent_requests)
        successful_requests = sum(1 for req in recent_requests if req["success"])
        total_cost = sum(req["cost"] for req in recent_requests)
        avg_response_time = sum(req["response_time"] for req in recent_requests) / total_requests
        
        # Статистика по моделям
        model_stats = {}
        for req in recent_requests:
            model = req["model"]
            if model not in model_stats:
                model_stats[model] = {
                    "requests": 0,
                    "successes": 0,
                    "total_cost": 0.0,
                    "avg_response_time": 0.0
                }
            
            stats = model_stats[model]
            stats["requests"] += 1
            if req["success"]:
                stats["successes"] += 1
            stats["total_cost"] += req["cost"]
            stats["avg_response_time"] = (
                (stats["avg_response_time"] * (stats["requests"] - 1) + req["response_time"])
                / stats["requests"]
            )
        
        # Добавляем success rate
        for model, stats in model_stats.items():
            stats["success_rate"] = stats["successes"] / stats["requests"]
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests,
            "total_cost": round(total_cost, 4),
            "avg_response_time": round(avg_response_time, 2),
            "model_statistics": model_stats
        }
```

## Калькулятор стоимости

```python
# services/ml/core/models/utils/cost_calculator.py

class CostCalculator:
    """Калькулятор стоимости использования моделей"""
    
    def __init__(self):
        self.cost_limits = {
            "per_request": EnvironmentConfig.COST_LIMIT_PER_REQUEST,
            "per_hour": float(os.getenv("ML_COST_LIMIT_PER_HOUR", "10.0")),
            "per_day": float(os.getenv("ML_COST_LIMIT_PER_DAY", "100.0"))
        }
        self.current_costs = {
            "hour": 0.0,
            "day": 0.0
        }
    
    def calculate_request_cost(self, 
                             model_config: ModelConfig,
                             estimated_tokens: int) -> float:
        """Расчет стоимости запроса"""
        return (estimated_tokens * model_config.cost_per_1k_tokens) / 1000
    
    def can_afford_request(self,
                         model_config: ModelConfig,
                         estimated_tokens: int) -> bool:
        """Проверка возможности выполнения запроса по стоимости"""
        request_cost = self.calculate_request_cost(model_config, estimated_tokens)
        
        # Проверяем лимиты
        if request_cost > self.cost_limits["per_request"]:
            return False
        
        if self.current_costs["hour"] + request_cost > self.cost_limits["per_hour"]:
            return False
        
        if self.current_costs["day"] + request_cost > self.cost_limits["per_day"]:
            return False
        
        return True
    
    def suggest_cheaper_alternative(self,
                                  task_type: TaskType,
                                  current_tier: ModelTier) -> Optional[ModelTier]:
        """Предлагает более дешевую альтернативу"""
        tier_order = [ModelTier.BUDGET, ModelTier.STANDARD, ModelTier.PREMIUM, ModelTier.SOTA]
        current_index = tier_order.index(current_tier)
        
        # Ищем более дешевую доступную модель
        for i in range(current_index):