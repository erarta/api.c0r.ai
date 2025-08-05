# Система Fallback и обработки ошибок для ML сервиса

## Обзор

Комплексная система обработки ошибок и fallback механизмов обеспечивает надежность и отказоустойчивость ML сервиса при работе с SOTA моделями для анализа еды и генерации рецептов.

## Архитектура системы обработки ошибок

### Структура модулей

```
services/ml/core/error_handling/
├── fallback/                    # Система fallback
│   ├── fallback_manager.py     # Основной менеджер fallback
│   ├── model_fallback.py       # Fallback между моделями
│   ├── provider_fallback.py    # Fallback между провайдерами
│   └── response_fallback.py    # Fallback ответы
├── error_handlers/              # Обработчики ошибок
│   ├── api_errors.py           # Ошибки API провайдеров
│   ├── parsing_errors.py       # Ошибки парсинга ответов
│   ├── timeout_errors.py       # Ошибки таймаута
│   └── rate_limit_errors.py    # Ошибки лимитов
├── recovery/                    # Система восстановления
│   ├── circuit_breaker.py      # Circuit breaker pattern
│   ├── retry_manager.py        # Управление повторными попытками
│   └── health_checker.py       # Проверка здоровья сервисов
└── monitoring/
    ├── error_tracker.py        # Отслеживание ошибок
    └── alert_system.py         # Система уведомлений
```

## Типы ошибок и их обработка

### Классификация ошибок

```python
# services/ml/core/error_handling/error_types.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import traceback

class ErrorSeverity(Enum):
    """Уровни критичности ошибок"""
    LOW = "low"           # Незначительные ошибки
    MEDIUM = "medium"     # Средние ошибки
    HIGH = "high"         # Критические ошибки
    CRITICAL = "critical" # Критические системные ошибки

class ErrorCategory(Enum):
    """Категории ошибок"""
    API_ERROR = "api_error"                 # Ошибки API провайдеров
    PARSING_ERROR = "parsing_error"         # Ошибки парсинга ответов
    TIMEOUT_ERROR = "timeout_error"         # Ошибки таймаута
    RATE_LIMIT_ERROR = "rate_limit_error"   # Превышение лимитов
    AUTHENTICATION_ERROR = "auth_error"     # Ошибки аутентификации
    QUOTA_EXCEEDED = "quota_exceeded"       # Превышение квот
    MODEL_ERROR = "model_error"             # Ошибки модели
    NETWORK_ERROR = "network_error"         # Сетевые ошибки
    VALIDATION_ERROR = "validation_error"   # Ошибки валидации
    SYSTEM_ERROR = "system_error"           # Системные ошибки

@dataclass
class MLError:
    """Базовый класс для ML ошибок"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    provider: str
    model: str
    task_type: str
    timestamp: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    recoverable: bool = True
    retry_after: Optional[int] = None

class MLErrorHandler:
    """Базовый обработчик ML ошибок"""
    
    def __init__(self):
        self.error_registry = {}
        self.fallback_manager = FallbackManager()
        self.error_tracker = ErrorTracker()
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> MLError:
        """Обработка ошибки с классификацией"""
        ml_error = self._classify_error(error, context)
        
        # Логирование ошибки
        self.error_tracker.log_error(ml_error)
        
        # Определение стратегии восстановления
        recovery_strategy = self._get_recovery_strategy(ml_error)
        
        return ml_error
    
    def _classify_error(self, error: Exception, context: Dict[str, Any]) -> MLError:
        """Классификация ошибки"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Определяем категорию и серьезность
        if "timeout" in error_message.lower():
            category = ErrorCategory.TIMEOUT_ERROR
            severity = ErrorSeverity.MEDIUM
            recoverable = True
            retry_after = 30
        elif "rate limit" in error_message.lower():
            category = ErrorCategory.RATE_LIMIT_ERROR
            severity = ErrorSeverity.HIGH
            recoverable = True
            retry_after = 60
        elif "authentication" in error_message.lower():
            category = ErrorCategory.AUTHENTICATION_ERROR
            severity = ErrorSeverity.CRITICAL
            recoverable = False
        elif "quota" in error_message.lower():
            category = ErrorCategory.QUOTA_EXCEEDED
            severity = ErrorSeverity.HIGH
            recoverable = True
            retry_after = 3600
        else:
            category = ErrorCategory.API_ERROR
            severity = ErrorSeverity.MEDIUM
            recoverable = True
            retry_after = 10
        
        return MLError(
            category=category,
            severity=severity,
            message=error_message,
            provider=context.get('provider', 'unknown'),
            model=context.get('model', 'unknown'),
            task_type=context.get('task_type', 'unknown'),
            timestamp=datetime.now().isoformat(),
            user_id=context.get('user_id'),
            request_id=context.get('request_id'),
            traceback=traceback.format_exc(),
            context=context,
            recoverable=recoverable,
            retry_after=retry_after
        )
```

## Система Fallback

### Многоуровневый Fallback

```python
# services/ml/core/error_handling/fallback/fallback_manager.py

from typing import List, Dict, Any, Optional, Callable
import asyncio
from datetime import datetime, timedelta

class FallbackStrategy(Enum):
    """Стратегии fallback"""
    MODEL_FALLBACK = "model_fallback"         # Переключение на другую модель
    PROVIDER_FALLBACK = "provider_fallback"   # Переключение на другого провайдера
    CACHED_RESPONSE = "cached_response"       # Использование кэшированного ответа
    SIMPLIFIED_PROMPT = "simplified_prompt"   # Упрощенный промпт
    DEGRADED_SERVICE = "degraded_service"     # Ограниченный сервис
    MANUAL_FALLBACK = "manual_fallback"       # Ручной fallback

@dataclass
class FallbackChain:
    """Цепочка fallback стратегий"""
    task_type: TaskType
    strategies: List[FallbackStrategy]
    max_attempts: int
    timeout_per_attempt: int
    
class FallbackManager:
    """Менеджер fallback стратегий"""
    
    def __init__(self):
        self.fallback_chains = self._build_fallback_chains()
        self.circuit_breaker = CircuitBreaker()
        self.cache_manager = CacheManager()
        self.model_health = ModelHealthChecker()
    
    def _build_fallback_chains(self) -> Dict[TaskType, FallbackChain]:
        """Построение цепочек fallback для каждого типа задач"""
        return {
            TaskType.FOOD_ANALYSIS: FallbackChain(
                task_type=TaskType.FOOD_ANALYSIS,
                strategies=[
                    FallbackStrategy.MODEL_FALLBACK,      # gpt-4o -> gpt-4o-mini
                    FallbackStrategy.PROVIDER_FALLBACK,   # OpenAI -> Anthropic
                    FallbackStrategy.SIMPLIFIED_PROMPT,   # Упрощенный анализ
                    FallbackStrategy.CACHED_RESPONSE,     # Кэшированный ответ
                    FallbackStrategy.DEGRADED_SERVICE     # Базовый анализ
                ],
                max_attempts=5,
                timeout_per_attempt=60
            ),
            TaskType.RECIPE_GENERATION: FallbackChain(
                task_type=TaskType.RECIPE_GENERATION,
                strategies=[
                    FallbackStrategy.MODEL_FALLBACK,      # gpt-4o -> claude-3.5
                    FallbackStrategy.PROVIDER_FALLBACK,   # OpenAI -> Anthropic
                    FallbackStrategy.SIMPLIFIED_PROMPT,   # 1 рецепт вместо 3
                    FallbackStrategy.CACHED_RESPONSE,     # Похожие рецепты
                    FallbackStrategy.MANUAL_FALLBACK      # Предустановленные рецепты
                ],
                max_attempts=5,
                timeout_per_attempt=90
            )
        }
    
    async def execute_with_fallback(self,
                                  task_type: TaskType,
                                  primary_function: Callable,
                                  context: Dict[str, Any]) -> Any:
        """Выполнение задачи с fallback"""
        
        fallback_chain = self.fallback_chains.get(task_type)
        if not fallback_chain:
            raise ValueError(f"No fallback chain defined for {task_type}")
        
        last_error = None
        
        for attempt, strategy in enumerate(fallback_chain.strategies):
            try:
                # Проверяем circuit breaker
                if not self.circuit_breaker.can_execute(strategy):
                    continue
                
                # Выполняем стратегию
                result = await self._execute_strategy(
                    strategy, primary_function, context, attempt
                )
                
                if result:
                    # Успешное выполнение
                    self.circuit_breaker.record_success(strategy)
                    return result
                    
            except Exception as e:
                last_error = e
                self.circuit_breaker.record_failure(strategy)
                
                # Логируем попытку fallback
                logger.warning(f"Fallback attempt {attempt + 1} failed for {strategy}: {e}")
                
                # Ждем перед следующей попыткой
                if attempt < len(fallback_chain.strategies) - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # Все fallback стратегии не сработали
        raise FallbackExhaustedException(
            f"All fallback strategies failed for {task_type}",
            last_error=last_error
        )
    
    async def _execute_strategy(self,
                              strategy: FallbackStrategy,
                              primary_function: Callable,
                              context: Dict[str, Any],
                              attempt: int) -> Any:
        """Выполнение конкретной fallback стратегии"""
        
        if strategy == FallbackStrategy.MODEL_FALLBACK:
            return await self._model_fallback(primary_function, context, attempt)
        
        elif strategy == FallbackStrategy.PROVIDER_FALLBACK:
            return await self._provider_fallback(primary_function, context, attempt)
        
        elif strategy == FallbackStrategy.SIMPLIFIED_PROMPT:
            return await self._simplified_prompt_fallback(primary_function, context)
        
        elif strategy == FallbackStrategy.CACHED_RESPONSE:
            return await self._cached_response_fallback(context)
        
        elif strategy == FallbackStrategy.DEGRADED_SERVICE:
            return await self._degraded_service_fallback(context)
        
        elif strategy == FallbackStrategy.MANUAL_FALLBACK:
            return await self._manual_fallback(context)
        
        else:
            raise ValueError(f"Unknown fallback strategy: {strategy}")
```

### Специализированные Fallback стратегии

```python
# services/ml/core/error_handling/fallback/model_fallback.py

class ModelFallbackManager:
    """Менеджер fallback между моделями"""
    
    def __init__(self):
        self.model_hierarchy = self._build_model_hierarchy()
        self.model_health = ModelHealthChecker()
    
    def _build_model_hierarchy(self) -> Dict[TaskType, List[ModelTier]]:
        """Иерархия моделей для fallback"""
        return {
            TaskType.FOOD_ANALYSIS: [
                ModelTier.SOTA,      # gpt-4o (первый выбор)
                ModelTier.PREMIUM,   # gpt-4o-mini (fallback 1)
                ModelTier.STANDARD,  # claude-3.5-sonnet (fallback 2)
                ModelTier.BUDGET     # gemini-pro (fallback 3)
            ],
            TaskType.RECIPE_GENERATION: [
                ModelTier.SOTA,      # gpt-4o (первый выбор)
                ModelTier.PREMIUM,   # claude-3.5-sonnet (fallback 1)
                ModelTier.STANDARD,  # gpt-4o-mini (fallback 2)
                ModelTier.BUDGET     # gemini-pro (fallback 3)
            ]
        }
    
    async def get_next_available_model(self,
                                     task_type: TaskType,
                                     failed_model: str,
                                     context: Dict[str, Any]) -> Optional[ModelConfig]:
        """Получение следующей доступной модели"""
        
        hierarchy = self.model_hierarchy.get(task_type, [])
        failed_tier = self._get_model_tier(failed_model)
        
        # Находим следующие доступные модели
        for tier in hierarchy:
            if tier <= failed_tier:  # Пропускаем уже неудачные
                continue
            
            config = SOTA_MODEL_CONFIGS.get(task_type, {}).get(tier)
            if not config:
                continue
            
            # Проверяем здоровье модели
            if await self.model_health.is_healthy(config.name, config.provider):
                return config
        
        return None
    
    async def execute_model_fallback(self,
                                   task_type: TaskType,
                                   original_function: Callable,
                                   context: Dict[str, Any],
                                   failed_model: str) -> Any:
        """Выполнение fallback на другую модель"""
        
        fallback_config = await self.get_next_available_model(
            task_type, failed_model, context
        )
        
        if not fallback_config:
            raise NoFallbackModelException(f"No fallback model available for {task_type}")
        
        # Обновляем контекст для fallback модели
        fallback_context = context.copy()
        fallback_context['model_config'] = fallback_config
        fallback_context['is_fallback'] = True
        fallback_context['original_model'] = failed_model
        
        # Адаптируем промпт под новую модель
        if 'prompt' in fallback_context:
            fallback_context['prompt'] = self._adapt_prompt_for_model(
                fallback_context['prompt'], fallback_config
            )
        
        # Выполняем с fallback моделью
        return await original_function(**fallback_context)
```

## Circuit Breaker Pattern

### Реализация Circuit Breaker

```python
# services/ml/core/error_handling/recovery/circuit_breaker.py

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"       # Нормальная работа
    OPEN = "open"          # Блокировка запросов
    HALF_OPEN = "half_open" # Тестирование восстановления

@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker"""
    failure_threshold: int = 5          # Порог неудач для открытия
    recovery_timeout: int = 60          # Время до попытки восстановления
    success_threshold: int = 3          # Успехов для закрытия
    timeout: int = 30                   # Таймаут операции
    
class CircuitBreaker:
    """Circuit Breaker для защиты от каскадных отказов"""
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.circuits: Dict[str, CircuitState] = {}
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, datetime] = {}
        self.lock = asyncio.Lock()
    
    def _get_circuit_key(self, provider: str, model: str) -> str:
        """Генерация ключа для circuit"""
        return f"{provider}:{model}"
    
    async def can_execute(self, provider: str, model: str) -> bool:
        """Проверка возможности выполнения запроса"""
        circuit_key = self._get_circuit_key(provider, model)
        
        async with self.lock:
            state = self.circuits.get(circuit_key, CircuitState.CLOSED)
            
            if state == CircuitState.CLOSED:
                return True
            
            elif state == CircuitState.OPEN:
                # Проверяем, можно ли перейти в HALF_OPEN
                last_failure = self.last_failure_times.get(circuit_key)
                if last_failure and datetime.now() - last_failure > timedelta(seconds=self.config.recovery_timeout):
                    self.circuits[circuit_key] = CircuitState.HALF_OPEN
                    self.success_counts[circuit_key] = 0
                    return True
                return False
            
            elif state == CircuitState.HALF_OPEN:
                return True
            
            return False
    
    async def record_success(self, provider: str, model: str):
        """Запись успешного выполнения"""
        circuit_key = self._get_circuit_key(provider, model)
        
        async with self.lock:
            state = self.circuits.get(circuit_key, CircuitState.CLOSED)
            
            if state == CircuitState.HALF_OPEN:
                self.success_counts[circuit_key] = self.success_counts.get(circuit_key, 0) + 1
                
                if self.success_counts[circuit_key] >= self.config.success_threshold:
                    # Закрываем circuit
                    self.circuits[circuit_key] = CircuitState.CLOSED
                    self.failure_counts[circuit_key] = 0
                    self.success_counts[circuit_key] = 0
                    logger.info(f"Circuit breaker closed for {circuit_key}")
            
            elif state == CircuitState.CLOSED:
                # Сбрасываем счетчик неудач при успехе
                self.failure_counts[circuit_key] = 0
    
    async def record_failure(self, provider: str, model: str):
        """Запись неудачного выполнения"""
        circuit_key = self._get_circuit_key(provider, model)
        
        async with self.lock:
            self.failure_counts[circuit_key] = self.failure_counts.get(circuit_key, 0) + 1
            self.last_failure_times[circuit_key] = datetime.now()
            
            state = self.circuits.get(circuit_key, CircuitState.CLOSED)
            
            if state == CircuitState.HALF_OPEN:
                # Возвращаемся в OPEN состояние
                self.circuits[circuit_key] = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened again for {circuit_key}")
            
            elif self.failure_counts[circuit_key] >= self.config.failure_threshold:
                # Открываем circuit
                self.circuits[circuit_key] = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened for {circuit_key} after {self.failure_counts[circuit_key]} failures")
    
    def get_circuit_status(self) -> Dict[str, Dict[str, Any]]:
        """Получение статуса всех circuits"""
        status = {}
        for circuit_key in self.circuits:
            status[circuit_key] = {
                "state": self.circuits[circuit_key].value,
                "failure_count": self.failure_counts.get(circuit_key, 0),
                "success_count": self.success_counts.get(circuit_key, 0),
                "last_failure": self.last_failure_times.get(circuit_key)
            }
        return status
```

## Система повторных попыток

### Retry Manager

```python
# services/ml/core/error_handling/recovery/retry_manager.py

from typing import Callable, Any, Optional
import asyncio
import random
from functools import wraps

class RetryStrategy(Enum):
    """Стратегии повторных попыток"""
    FIXED_DELAY = "fixed_delay"           # Фиксированная задержка
    EXPONENTIAL_BACKOFF = "exponential"   # Экспоненциальная задержка
    LINEAR_BACKOFF = "linear"             # Линейная задержка
    RANDOM_JITTER = "random_jitter"       # Случайная задержка

@dataclass
class RetryConfig:
    """Конфигурация повторных попыток"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0
    retryable_exceptions: List[type] = None

class RetryManager:
    """Менеджер повторных попыток"""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.default_retryable_exceptions = [
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
            # Добавляем специфичные ML ошибки
            RateLimitError,
            TemporaryAPIError
        ]
    
    def retry(self, config: Optional[RetryConfig] = None):
        """Декоратор для повторных попыток"""
        retry_config = config or self.config
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await self.execute_with_retry(func, retry_config, *args, **kwargs)
            return wrapper
        return decorator
    
    async def execute_with_retry(self,
                               func: Callable,
                               config: RetryConfig,
                               *args, **kwargs) -> Any:
        """Выполнение функции с повторными попытками"""
        
        last_exception = None
        
        for attempt in range(config.max_attempts):
            try:
                result = await func(*args, **kwargs)
                
                # Успешное выполнение
                if attempt > 0:
                    logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Проверяем, можно ли повторить
                if not self._is_retryable_exception(e, config):
                    logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                    raise e
                
                # Последняя попытка
                if attempt == config.max_attempts - 1:
                    logger.error(f"All retry attempts failed for {func.__name__}")
                    break
                
                # Рассчитываем задержку
                delay = self._calculate_delay(attempt, config)
                
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s")
                
                await asyncio.sleep(delay)
        
        # Все попытки исчерпаны
        raise RetryExhaustedException(
            f"Function {func.__name__} failed after {config.max_attempts} attempts",
            last_exception=last_exception
        )
    
    def _is_retryable_exception(self, exception: Exception, config: RetryConfig) -> bool:
        """Проверка, можно ли повторить при данной ошибке"""
        retryable_exceptions = config.retryable_exceptions or self.default_retryable_exceptions
        
        return any(isinstance(exception, exc_type) for exc_type in retryable_exceptions)
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Расчет задержки перед повторной попыткой"""
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        
        elif config.strategy == RetryStrategy.RANDOM_JITTER:
            delay = random.uniform(config.base_delay, config.base_delay * 3)
        
        else:
            delay = config.base_delay
        
        # Ограничиваем максимальную задержку
        delay = min(delay, config.max_delay)
        
        # Добавляем jitter для избежания thundering herd
        if config.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
```

## Система мониторинга ошибок

### Error Tracker

```python
# services/ml/core/error_handling/monitoring/error_tracker.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class ErrorTracker:
    """Система отслеживания и анализа ошибок"""
    
    def __init__(self):
        self.error_history: List[MLError] = []
        self.error_stats: Dict[str, int] = {}
        self.alert_system = AlertSystem()
        self.max_history_size = 10000
    
    async def log_error(self, error: MLError):
        """Логирование ошибки"""
        
        # Добавляем в историю
        self.error_history.append(error)
        
        # Ограничиваем размер истории
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
        
        # Обновляем статистику
        error_key = f"{error.category.value}:{error.provider}:{error.model}"
        self.error_stats[error_key] = self.error_stats.get(error_key, 0) + 1
        
        # Проверяем необходимость алертов
        await self._check_alert_conditions(error)
        
        # Логируем в файл/базу данных
        logger.error(f"ML Error: {error.category.value} - {error.message}", extra={
            "provider": error.provider,
            "model": error.model,
            "task_type": error.task_type,
            "severity": error.severity.value,
            "user_id": error.user_id,
            "recoverable": error.recoverable
        })
    
    async def _check_alert_conditions(self, error: MLError):
        """Проверка условий для отправки алертов"""
        
        # Критические ошибки - немедленный алерт
        if error.severity == ErrorSeverity.CRITICAL:
            await self.alert_system.send_critical_alert(error)
        
        # Проверяем частоту ошибок
        recent_errors = self._get_recent_errors(minutes=10)
        error_rate = len([e for e in recent_errors if e.category == error.category])
        
        if error_rate >= 5:  # 5 ошибок за 10 минут
            await self.alert_system.send_high_frequency_alert(error.category, error_rate)
        
        # Проверяем отказы конкретной модели
        model_errors = [e for e in recent_errors 
                       if e.provider == error.provider and e.model == error.model]
        
        if len(model_errors) >= 3:  # 3 ошибки модели за 10 минут
            await self.alert_system.send_model_failure_alert(error.provider, error.model)
    
    def _get_recent_errors(self, minutes: int = 60) -> List[MLError]:
        """Получение недавних ошибок"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [error for error in self.error_history 
                if datetime.fromisoformat(error.timestamp) > cutoff_time]
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Получение статистики ошибок"""
        recent_errors = self._get_recent_errors(minutes=hours * 60)
        
        if not recent_errors:
            return {"message": "No recent errors"}
        
        # Группировка по категориям
        category_stats = {}
        for error in recent_errors:
            category = error.category.value
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "providers": {},
                    "models": {},
                    "severity_distribution": {}
                }
            
            stats = category_stats[category]
            stats["count"] += 1
            stats["providers"][error.provider] = stats["providers"].get(error.provider, 0) + 1
            stats["models"][error.model] = stats["models"].get(error.model, 0) + 1
            stats["severity_distribution"][error.severity.value] = stats["severity_distribution"].get(error.severity.value, 0) + 1
        
        # Топ ошибок
        top_errors = sorted(category_stats
