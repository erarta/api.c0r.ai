"""
Retry Handler for c0r.AI ML Service
Provides intelligent retry mechanisms with exponential backoff
"""

import time
import random
from typing import Callable, Any, Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
import functools
from loguru import logger


class RetryStrategy(Enum):
    """Стратегии повторов"""
    FIXED_DELAY = "fixed_delay"           # Фиксированная задержка
    EXPONENTIAL_BACKOFF = "exponential"   # Экспоненциальная задержка
    LINEAR_BACKOFF = "linear"             # Линейная задержка
    RANDOM_JITTER = "random_jitter"       # Случайная задержка
    FIBONACCI = "fibonacci"               # Последовательность Фибоначчи


@dataclass
class RetryConfig:
    """Конфигурация retry механизма"""
    max_attempts: int = 3                 # Максимальное количество попыток
    base_delay: float = 1.0              # Базовая задержка (секунды)
    max_delay: float = 60.0              # Максимальная задержка (секунды)
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0      # Множитель для экспоненциального backoff
    jitter: bool = True                  # Добавлять случайный jitter
    jitter_range: float = 0.1            # Диапазон jitter (0.0 - 1.0)
    retryable_exceptions: tuple = (Exception,)  # Исключения для повтора
    stop_on_exceptions: tuple = ()       # Исключения для остановки
    timeout_per_attempt: Optional[float] = None  # Таймаут на попытку


@dataclass
class RetryResult:
    """Результат выполнения с повторами"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    attempts_made: int = 0
    total_time: float = 0.0
    last_delay: float = 0.0
    retry_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.retry_history is None:
            self.retry_history = []


class RetryHandler:
    """
    Обработчик повторов с различными стратегиями backoff
    
    Поддерживает:
    - Различные стратегии задержек
    - Настраиваемые исключения для повтора
    - Jitter для предотвращения thundering herd
    - Детальная статистика выполнения
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[RetryConfig] = None):
        self.name = name
        self.config = config or RetryConfig()
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_attempts": 0,
            "avg_attempts_per_execution": 0.0,
            "avg_execution_time": 0.0,
            "exception_counts": {}
        }
        
        logger.info(f"🔄 RetryHandler '{name}' initialized with config: {self.config}")
    
    def execute(self, func: Callable, *args, **kwargs) -> RetryResult:
        """
        Выполнение функции с повторами
        
        Args:
            func: Функция для выполнения
            *args, **kwargs: Аргументы функции
            
        Returns:
            Результат выполнения с метаданными
        """
        start_time = time.time()
        self.stats["total_executions"] += 1
        
        retry_history = []
        last_exception = None
        
        logger.debug(f"🚀 Starting retry execution for '{self.name}' (max {self.config.max_attempts} attempts)")
        
        for attempt in range(1, self.config.max_attempts + 1):
            attempt_start = time.time()
            
            try:
                # Выполняем функцию
                if self.config.timeout_per_attempt:
                    result = self._execute_with_timeout(
                        func, self.config.timeout_per_attempt, *args, **kwargs
                    )
                else:
                    result = func(*args, **kwargs)
                
                # Успешное выполнение
                attempt_time = time.time() - attempt_start
                total_time = time.time() - start_time
                
                retry_history.append({
                    "attempt": attempt,
                    "success": True,
                    "execution_time": attempt_time,
                    "error": None
                })
                
                # Обновляем статистику
                self.stats["successful_executions"] += 1
                self.stats["total_attempts"] += attempt
                self._update_avg_stats(attempt, total_time)
                
                logger.debug(f"✅ '{self.name}' succeeded on attempt {attempt} in {total_time:.2f}s")
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts_made=attempt,
                    total_time=total_time,
                    retry_history=retry_history
                )
                
            except Exception as e:
                attempt_time = time.time() - attempt_start
                last_exception = e
                
                retry_history.append({
                    "attempt": attempt,
                    "success": False,
                    "execution_time": attempt_time,
                    "error": str(e),
                    "exception_type": type(e).__name__
                })
                
                # Обновляем статистику исключений
                exception_name = type(e).__name__
                self.stats["exception_counts"][exception_name] = (
                    self.stats["exception_counts"].get(exception_name, 0) + 1
                )
                
                logger.warning(f"⚠️ '{self.name}' attempt {attempt} failed: {e}")
                
                # Проверяем, нужно ли останавливаться
                if self._should_stop_retry(e):
                    logger.error(f"🛑 Stopping retry for '{self.name}' due to non-retryable exception: {e}")
                    break
                
                # Проверяем, можно ли повторить
                if not self._should_retry(e):
                    logger.error(f"🚫 Not retrying '{self.name}' due to exception type: {e}")
                    break
                
                # Если это не последняя попытка, делаем задержку
                if attempt < self.config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.debug(f"⏳ Waiting {delay:.2f}s before retry {attempt + 1}")
                    time.sleep(delay)
        
        # Все попытки неудачны
        total_time = time.time() - start_time
        self.stats["failed_executions"] += 1
        self.stats["total_attempts"] += self.config.max_attempts
        self._update_avg_stats(self.config.max_attempts, total_time)
        
        logger.error(f"❌ '{self.name}' failed after {self.config.max_attempts} attempts")
        
        return RetryResult(
            success=False,
            error=last_exception,
            attempts_made=self.config.max_attempts,
            total_time=total_time,
            retry_history=retry_history
        )
    
    def _should_retry(self, exception: Exception) -> bool:
        """Проверка, нужно ли повторять при данном исключении"""
        return isinstance(exception, self.config.retryable_exceptions)
    
    def _should_stop_retry(self, exception: Exception) -> bool:
        """Проверка, нужно ли остановить повторы при данном исключении"""
        return isinstance(exception, self.config.stop_on_exceptions)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Расчет задержки перед следующей попыткой"""
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
            
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
            
        elif self.config.strategy == RetryStrategy.RANDOM_JITTER:
            delay = random.uniform(0, self.config.base_delay * attempt)
            
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self.config.base_delay * self._fibonacci(attempt)
            
        else:
            delay = self.config.base_delay
        
        # Ограничиваем максимальной задержкой
        delay = min(delay, self.config.max_delay)
        
        # Добавляем jitter если включен
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        """Вычисление числа Фибоначчи"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        
        return b
    
    def _execute_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        """Выполнение функции с таймаутом"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function execution exceeded {timeout} seconds")
        
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)
                return result
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Для Windows - простое выполнение
            return func(*args, **kwargs)
    
    def _update_avg_stats(self, attempts: int, execution_time: float):
        """Обновление средних статистик"""
        total_executions = self.stats["total_executions"]
        
        # Среднее количество попыток
        if total_executions == 1:
            self.stats["avg_attempts_per_execution"] = attempts
        else:
            self.stats["avg_attempts_per_execution"] = (
                (self.stats["avg_attempts_per_execution"] * (total_executions - 1) + attempts) /
                total_executions
            )
        
        # Среднее время выполнения
        if total_executions == 1:
            self.stats["avg_execution_time"] = execution_time
        else:
            self.stats["avg_execution_time"] = (
                (self.stats["avg_execution_time"] * (total_executions - 1) + execution_time) /
                total_executions
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики retry handler"""
        success_rate = 0.0
        if self.stats["total_executions"] > 0:
            success_rate = (self.stats["successful_executions"] / self.stats["total_executions"]) * 100
        
        return {
            "name": self.name,
            "config": {
                "max_attempts": self.config.max_attempts,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "strategy": self.config.strategy.value,
                "backoff_multiplier": self.config.backoff_multiplier,
                "jitter": self.config.jitter
            },
            "stats": {
                "total_executions": self.stats["total_executions"],
                "successful_executions": self.stats["successful_executions"],
                "failed_executions": self.stats["failed_executions"],
                "success_rate": round(success_rate, 2),
                "total_attempts": self.stats["total_attempts"],
                "avg_attempts_per_execution": round(self.stats["avg_attempts_per_execution"], 2),
                "avg_execution_time": round(self.stats["avg_execution_time"], 2),
                "exception_counts": self.stats["exception_counts"]
            }
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_attempts": 0,
            "avg_attempts_per_execution": 0.0,
            "avg_execution_time": 0.0,
            "exception_counts": {}
        }
        
        logger.info(f"📊 Stats reset for RetryHandler '{self.name}'")
    
    def __call__(self, func: Callable) -> Callable:
        """Декоратор для применения retry к функции"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = self.execute(func, *args, **kwargs)
            if result.success:
                return result.result
            else:
                raise result.error
        
        return wrapper


def retry(name: str, 
          config: Optional[RetryConfig] = None) -> Callable:
    """
    Декоратор для применения retry к функции
    
    Args:
        name: Имя retry handler
        config: Конфигурация retry
        
    Returns:
        Декоратор
    """
    def decorator(func: Callable) -> Callable:
        handler = RetryHandler(name, config)
        return handler(func)
    
    return decorator


def retry_with_exponential_backoff(max_attempts: int = 3,
                                 base_delay: float = 1.0,
                                 max_delay: float = 60.0,
                                 backoff_multiplier: float = 2.0,
                                 jitter: bool = True) -> Callable:
    """
    Удобный декоратор для экспоненциального backoff
    
    Args:
        max_attempts: Максимальное количество попыток
        base_delay: Базовая задержка
        max_delay: Максимальная задержка
        backoff_multiplier: Множитель backoff
        jitter: Добавлять jitter
        
    Returns:
        Декоратор
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        backoff_multiplier=backoff_multiplier,
        jitter=jitter
    )
    
    def decorator(func: Callable) -> Callable:
        handler = RetryHandler(func.__name__, config)
        return handler(func)
    
    return decorator


def retry_on_exceptions(*exceptions: type,
                       max_attempts: int = 3,
                       base_delay: float = 1.0) -> Callable:
    """
    Декоратор для retry только на определенных исключениях
    
    Args:
        *exceptions: Типы исключений для retry
        max_attempts: Максимальное количество попыток
        base_delay: Базовая задержка
        
    Returns:
        Декоратор
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        retryable_exceptions=exceptions
    )
    
    def decorator(func: Callable) -> Callable:
        handler = RetryHandler(func.__name__, config)
        return handler(func)
    
    return decorator


class RetryHandlerRegistry:
    """Реестр retry handler'ов"""
    
    def __init__(self):
        self._handlers: Dict[str, RetryHandler] = {}
        
        logger.info("📋 RetryHandlerRegistry initialized")
    
    def create(self, 
               name: str, 
               config: Optional[RetryConfig] = None) -> RetryHandler:
        """Создание нового retry handler"""
        if name in self._handlers:
            logger.warning(f"⚠️ RetryHandler '{name}' already exists, returning existing")
            return self._handlers[name]
        
        handler = RetryHandler(name, config)
        self._handlers[name] = handler
        
        logger.info(f"🆕 Created RetryHandler '{name}'")
        return handler
    
    def get(self, name: str) -> Optional[RetryHandler]:
        """Получение retry handler по имени"""
        return self._handlers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики всех retry handler'ов"""
        return {name: handler.get_stats() 
               for name, handler in self._handlers.items()}
    
    def remove(self, name: str) -> bool:
        """Удаление retry handler"""
        if name in self._handlers:
            del self._handlers[name]
            logger.info(f"🗑️ Removed RetryHandler '{name}'")
            return True
        return False
    
    def list_names(self) -> List[str]:
        """Список имен всех retry handler'ов"""
        return list(self._handlers.keys())


# Глобальный реестр retry handler'ов
retry_registry = RetryHandlerRegistry()