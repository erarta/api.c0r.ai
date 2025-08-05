"""
Circuit Breaker Pattern Implementation for c0r.AI ML Service
Prevents cascading failures and provides automatic recovery
"""

import time
import threading
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass
from loguru import logger


class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Блокировка запросов
    HALF_OPEN = "half_open"  # Тестирование восстановления


@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker"""
    failure_threshold: int = 5          # Количество ошибок для открытия
    recovery_timeout: int = 60          # Время до попытки восстановления (сек)
    success_threshold: int = 3          # Успешных запросов для закрытия
    timeout: float = 30.0               # Таймаут запроса (сек)
    expected_exception: tuple = (Exception,)  # Ожидаемые исключения


@dataclass
class CircuitBreakerStats:
    """Статистика Circuit Breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0


class CircuitBreaker:
    """
    Circuit Breaker для защиты от каскадных сбоев
    
    Реализует паттерн Circuit Breaker с тремя состояниями:
    - CLOSED: нормальная работа
    - OPEN: блокировка запросов при превышении лимита ошибок
    - HALF_OPEN: тестирование восстановления сервиса
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self.state = CircuitState.CLOSED
        self._lock = threading.RLock()
        
        logger.info(f"🔌 CircuitBreaker '{name}' initialized with config: {self.config}")
    
    def __call__(self, func: Callable) -> Callable:
        """Декоратор для защиты функции Circuit Breaker"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнение функции с защитой Circuit Breaker
        
        Args:
            func: Функция для выполнения
            *args, **kwargs: Аргументы функции
            
        Returns:
            Результат выполнения функции
            
        Raises:
            CircuitBreakerOpenException: Если circuit breaker открыт
            TimeoutError: Если превышен таймаут
        """
        with self._lock:
            self.stats.total_requests += 1
            
            # Проверяем состояние circuit breaker
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._move_to_half_open()
                else:
                    logger.warning(f"🚫 CircuitBreaker '{self.name}' is OPEN, rejecting request")
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker '{self.name}' is open"
                    )
            
            try:
                # Выполняем функцию с таймаутом
                start_time = time.time()
                result = self._execute_with_timeout(func, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Регистрируем успех
                self._on_success(execution_time)
                
                return result
                
            except self.config.expected_exception as e:
                # Регистрируем ошибку
                self._on_failure(e)
                raise
            except Exception as e:
                # Неожиданная ошибка - также считаем как сбой
                logger.error(f"❌ Unexpected error in CircuitBreaker '{self.name}': {e}")
                self._on_failure(e)
                raise
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнение функции с таймаутом"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function execution exceeded {self.config.timeout} seconds")
        
        # Устанавливаем таймаут только для Unix-систем
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.config.timeout))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Отменяем таймаут
                return result
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Для Windows - простое выполнение без таймаута
            return func(*args, **kwargs)
    
    def _on_success(self, execution_time: float):
        """Обработка успешного выполнения"""
        self.stats.successful_requests += 1
        self.stats.consecutive_successes += 1
        self.stats.consecutive_failures = 0
        self.stats.last_success_time = time.time()
        
        logger.debug(f"✅ CircuitBreaker '{self.name}' success in {execution_time:.2f}s")
        
        # Если в состоянии HALF_OPEN и достигли порога успехов
        if (self.state == CircuitState.HALF_OPEN and 
            self.stats.consecutive_successes >= self.config.success_threshold):
            self._move_to_closed()
    
    def _on_failure(self, exception: Exception):
        """Обработка неудачного выполнения"""
        self.stats.failed_requests += 1
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        self.stats.last_failure_time = time.time()
        
        logger.warning(f"❌ CircuitBreaker '{self.name}' failure: {exception}")
        
        # Если превысили порог ошибок, открываем circuit breaker
        if (self.state == CircuitState.CLOSED and 
            self.stats.consecutive_failures >= self.config.failure_threshold):
            self._move_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            # В состоянии HALF_OPEN любая ошибка возвращает в OPEN
            self._move_to_open()
    
    def _should_attempt_reset(self) -> bool:
        """Проверка, можно ли попытаться восстановить соединение"""
        if self.stats.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.stats.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _move_to_closed(self):
        """Переход в состояние CLOSED"""
        previous_state = self.state
        self.state = CircuitState.CLOSED
        self.stats.consecutive_failures = 0
        self.stats.state_changes += 1
        
        logger.info(f"🟢 CircuitBreaker '{self.name}' moved from {previous_state.value} to CLOSED")
    
    def _move_to_open(self):
        """Переход в состояние OPEN"""
        previous_state = self.state
        self.state = CircuitState.OPEN
        self.stats.consecutive_successes = 0
        self.stats.state_changes += 1
        
        logger.warning(f"🔴 CircuitBreaker '{self.name}' moved from {previous_state.value} to OPEN")
    
    def _move_to_half_open(self):
        """Переход в состояние HALF_OPEN"""
        previous_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.stats.consecutive_successes = 0
        self.stats.state_changes += 1
        
        logger.info(f"🟡 CircuitBreaker '{self.name}' moved from {previous_state.value} to HALF_OPEN")
    
    def reset(self):
        """Принудительный сброс circuit breaker в состояние CLOSED"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.stats.consecutive_failures = 0
            self.stats.consecutive_successes = 0
            self.stats.state_changes += 1
            
            logger.info(f"🔄 CircuitBreaker '{self.name}' manually reset to CLOSED")
    
    def force_open(self):
        """Принудительное открытие circuit breaker"""
        with self._lock:
            self._move_to_open()
            logger.warning(f"⚠️ CircuitBreaker '{self.name}' manually forced to OPEN")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики circuit breaker"""
        with self._lock:
            success_rate = 0.0
            if self.stats.total_requests > 0:
                success_rate = (self.stats.successful_requests / self.stats.total_requests) * 100
            
            return {
                "name": self.name,
                "state": self.state.value,
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "success_rate": round(success_rate, 2),
                "consecutive_failures": self.stats.consecutive_failures,
                "consecutive_successes": self.stats.consecutive_successes,
                "state_changes": self.stats.state_changes,
                "last_failure_time": self.stats.last_failure_time,
                "last_success_time": self.stats.last_success_time,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout": self.config.timeout
                }
            }
    
    def is_closed(self) -> bool:
        """Проверка, закрыт ли circuit breaker"""
        return self.state == CircuitState.CLOSED
    
    def is_open(self) -> bool:
        """Проверка, открыт ли circuit breaker"""
        return self.state == CircuitState.OPEN
    
    def is_half_open(self) -> bool:
        """Проверка, в состоянии ли half-open circuit breaker"""
        return self.state == CircuitState.HALF_OPEN


class CircuitBreakerOpenException(Exception):
    """Исключение, возникающее когда circuit breaker открыт"""
    pass


class CircuitBreakerRegistry:
    """Реестр circuit breaker'ов для централизованного управления"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        
        logger.info("📋 CircuitBreakerRegistry initialized")
    
    def get_or_create(self, 
                     name: str, 
                     config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Получение существующего или создание нового circuit breaker
        
        Args:
            name: Имя circuit breaker
            config: Конфигурация (используется только при создании)
            
        Returns:
            Circuit breaker
        """
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
                logger.info(f"🆕 Created new CircuitBreaker: {name}")
            
            return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Получение circuit breaker по имени"""
        return self._breakers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики всех circuit breaker'ов"""
        with self._lock:
            return {name: breaker.get_stats() 
                   for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """Сброс всех circuit breaker'ов"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            
            logger.info("🔄 All circuit breakers reset")
    
    def remove(self, name: str) -> bool:
        """Удаление circuit breaker из реестра"""
        with self._lock:
            if name in self._breakers:
                del self._breakers[name]
                logger.info(f"🗑️ Removed CircuitBreaker: {name}")
                return True
            return False
    
    def list_names(self) -> list[str]:
        """Получение списка имен всех circuit breaker'ов"""
        return list(self._breakers.keys())


# Глобальный реестр circuit breaker'ов
circuit_breaker_registry = CircuitBreakerRegistry()


def circuit_breaker(name: str, 
                   config: Optional[CircuitBreakerConfig] = None) -> Callable:
    """
    Декоратор для применения circuit breaker к функции
    
    Args:
        name: Имя circuit breaker
        config: Конфигурация circuit breaker
        
    Returns:
        Декоратор
    """
    def decorator(func: Callable) -> Callable:
        breaker = circuit_breaker_registry.get_or_create(name, config)
        return breaker(func)
    
    return decorator