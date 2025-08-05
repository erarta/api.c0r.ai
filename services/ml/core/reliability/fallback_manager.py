"""
Fallback Manager for c0r.AI ML Service
Manages fallback chains and graceful degradation
"""

from typing import List, Callable, Any, Optional, Dict, Union
from dataclasses import dataclass
from enum import Enum
import time
import asyncio
from loguru import logger

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenException


class FallbackStrategy(Enum):
    """Стратегии fallback"""
    SEQUENTIAL = "sequential"      # Последовательное выполнение
    PARALLEL = "parallel"          # Параллельное выполнение (первый успешный)
    WEIGHTED = "weighted"          # Взвешенный выбор
    CONDITIONAL = "conditional"    # Условный выбор


@dataclass
class FallbackOption:
    """Опция fallback с метаданными"""
    name: str
    func: Callable
    weight: float = 1.0           # Вес для взвешенной стратегии
    condition: Optional[Callable] = None  # Условие для выполнения
    circuit_breaker: Optional[CircuitBreaker] = None
    timeout: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FallbackResult:
    """Результат выполнения fallback"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    executed_option: Optional[str] = None
    execution_time: float = 0.0
    attempts_made: int = 0
    fallback_used: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FallbackManager:
    """
    Менеджер fallback механизмов для обеспечения отказоустойчивости
    
    Поддерживает различные стратегии fallback:
    - Последовательное выполнение (sequential)
    - Параллельное выполнение (parallel)
    - Взвешенный выбор (weighted)
    - Условный выбор (conditional)
    """
    
    def __init__(self, 
                 name: str,
                 strategy: FallbackStrategy = FallbackStrategy.SEQUENTIAL):
        self.name = name
        self.strategy = strategy
        self.options: List[FallbackOption] = []
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "fallback_executions": 0,
            "option_stats": {}
        }
        
        logger.info(f"🔄 FallbackManager '{name}' initialized with strategy: {strategy.value}")
    
    def add_option(self, 
                   name: str,
                   func: Callable,
                   weight: float = 1.0,
                   condition: Optional[Callable] = None,
                   circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
                   timeout: Optional[float] = None,
                   retry_count: int = 0,
                   **metadata) -> 'FallbackManager':
        """
        Добавление опции fallback
        
        Args:
            name: Имя опции
            func: Функция для выполнения
            weight: Вес для взвешенной стратегии
            condition: Условие для выполнения
            circuit_breaker_config: Конфигурация circuit breaker
            timeout: Таймаут выполнения
            retry_count: Количество повторов
            **metadata: Дополнительные метаданные
            
        Returns:
            Self для цепочки вызовов
        """
        # Создаем circuit breaker если нужен
        circuit_breaker = None
        if circuit_breaker_config:
            circuit_breaker = CircuitBreaker(
                f"{self.name}_{name}", 
                circuit_breaker_config
            )
        
        option = FallbackOption(
            name=name,
            func=func,
            weight=weight,
            condition=condition,
            circuit_breaker=circuit_breaker,
            timeout=timeout,
            retry_count=retry_count,
            metadata=metadata
        )
        
        self.options.append(option)
        self.stats["option_stats"][name] = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_execution_time": 0.0
        }
        
        logger.debug(f"➕ Added fallback option '{name}' to '{self.name}'")
        return self
    
    def execute(self, *args, **kwargs) -> FallbackResult:
        """
        Выполнение fallback цепочки
        
        Args:
            *args, **kwargs: Аргументы для передачи в функции
            
        Returns:
            Результат выполнения
        """
        start_time = time.time()
        self.stats["total_executions"] += 1
        
        logger.debug(f"🚀 Executing fallback chain '{self.name}' with strategy {self.strategy.value}")
        
        try:
            if self.strategy == FallbackStrategy.SEQUENTIAL:
                result = self._execute_sequential(*args, **kwargs)
            elif self.strategy == FallbackStrategy.PARALLEL:
                result = self._execute_parallel(*args, **kwargs)
            elif self.strategy == FallbackStrategy.WEIGHTED:
                result = self._execute_weighted(*args, **kwargs)
            elif self.strategy == FallbackStrategy.CONDITIONAL:
                result = self._execute_conditional(*args, **kwargs)
            else:
                raise ValueError(f"Unknown fallback strategy: {self.strategy}")
            
            if result.success:
                self.stats["successful_executions"] += 1
                if result.fallback_used:
                    self.stats["fallback_executions"] += 1
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"❌ Fallback chain '{self.name}' failed completely: {e}")
            return FallbackResult(
                success=False,
                error=e,
                execution_time=time.time() - start_time,
                attempts_made=len(self.options)
            )
    
    def _execute_sequential(self, *args, **kwargs) -> FallbackResult:
        """Последовательное выполнение опций"""
        attempts = 0
        
        for i, option in enumerate(self.options):
            if not self._should_execute_option(option, *args, **kwargs):
                continue
            
            attempts += 1
            result = self._execute_single_option(option, *args, **kwargs)
            
            if result.success:
                return FallbackResult(
                    success=True,
                    result=result.result,
                    executed_option=option.name,
                    attempts_made=attempts,
                    fallback_used=(i > 0),
                    metadata={"strategy": "sequential", "option_index": i}
                )
            
            logger.warning(f"⚠️ Option '{option.name}' failed: {result.error}")
        
        return FallbackResult(
            success=False,
            error=Exception("All sequential options failed"),
            attempts_made=attempts,
            fallback_used=True
        )
    
    def _execute_parallel(self, *args, **kwargs) -> FallbackResult:
        """Параллельное выполнение опций (первый успешный)"""
        import concurrent.futures
        
        executable_options = [
            option for option in self.options 
            if self._should_execute_option(option, *args, **kwargs)
        ]
        
        if not executable_options:
            return FallbackResult(
                success=False,
                error=Exception("No executable options available"),
                attempts_made=0
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(executable_options)) as executor:
            # Запускаем все опции параллельно
            future_to_option = {
                executor.submit(self._execute_single_option, option, *args, **kwargs): option
                for option in executable_options
            }
            
            # Ждем первый успешный результат
            for future in concurrent.futures.as_completed(future_to_option):
                option = future_to_option[future]
                result = future.result()
                
                if result.success:
                    # Отменяем остальные задачи
                    for f in future_to_option:
                        if f != future:
                            f.cancel()
                    
                    return FallbackResult(
                        success=True,
                        result=result.result,
                        executed_option=option.name,
                        attempts_made=len(executable_options),
                        fallback_used=False,  # В параллельном режиме все опции равноправны
                        metadata={"strategy": "parallel", "total_options": len(executable_options)}
                    )
        
        return FallbackResult(
            success=False,
            error=Exception("All parallel options failed"),
            attempts_made=len(executable_options),
            fallback_used=True
        )
    
    def _execute_weighted(self, *args, **kwargs) -> FallbackResult:
        """Взвешенный выбор опции"""
        import random
        
        executable_options = [
            option for option in self.options 
            if self._should_execute_option(option, *args, **kwargs)
        ]
        
        if not executable_options:
            return FallbackResult(
                success=False,
                error=Exception("No executable options available"),
                attempts_made=0
            )
        
        # Выбираем опцию на основе весов
        total_weight = sum(option.weight for option in executable_options)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        selected_option = None
        
        for option in executable_options:
            current_weight += option.weight
            if random_value <= current_weight:
                selected_option = option
                break
        
        if selected_option is None:
            selected_option = executable_options[-1]  # Fallback на последнюю опцию
        
        result = self._execute_single_option(selected_option, *args, **kwargs)
        
        return FallbackResult(
            success=result.success,
            result=result.result,
            error=result.error,
            executed_option=selected_option.name,
            attempts_made=1,
            fallback_used=False,
            metadata={
                "strategy": "weighted", 
                "selected_weight": selected_option.weight,
                "total_weight": total_weight
            }
        )
    
    def _execute_conditional(self, *args, **kwargs) -> FallbackResult:
        """Условный выбор опции"""
        for option in self.options:
            if self._should_execute_option(option, *args, **kwargs):
                result = self._execute_single_option(option, *args, **kwargs)
                
                return FallbackResult(
                    success=result.success,
                    result=result.result,
                    error=result.error,
                    executed_option=option.name,
                    attempts_made=1,
                    fallback_used=False,
                    metadata={"strategy": "conditional", "condition_met": True}
                )
        
        return FallbackResult(
            success=False,
            error=Exception("No conditions met for execution"),
            attempts_made=0,
            fallback_used=True,
            metadata={"strategy": "conditional", "condition_met": False}
        )
    
    def _should_execute_option(self, option: FallbackOption, *args, **kwargs) -> bool:
        """Проверка, должна ли выполняться опция"""
        # Проверяем circuit breaker
        if option.circuit_breaker and option.circuit_breaker.is_open():
            logger.debug(f"🚫 Option '{option.name}' skipped - circuit breaker is open")
            return False
        
        # Проверяем условие
        if option.condition:
            try:
                if not option.condition(*args, **kwargs):
                    logger.debug(f"🚫 Option '{option.name}' skipped - condition not met")
                    return False
            except Exception as e:
                logger.warning(f"⚠️ Condition check failed for '{option.name}': {e}")
                return False
        
        return True
    
    def _execute_single_option(self, option: FallbackOption, *args, **kwargs) -> FallbackResult:
        """Выполнение одной опции с повторами и circuit breaker"""
        start_time = time.time()
        self.stats["option_stats"][option.name]["executions"] += 1
        
        last_error = None
        
        for attempt in range(option.retry_count + 1):
            try:
                if option.circuit_breaker:
                    # Выполняем через circuit breaker
                    result = option.circuit_breaker.call(option.func, *args, **kwargs)
                else:
                    # Прямое выполнение
                    if option.timeout:
                        result = self._execute_with_timeout(option.func, option.timeout, *args, **kwargs)
                    else:
                        result = option.func(*args, **kwargs)
                
                # Успешное выполнение
                execution_time = time.time() - start_time
                self.stats["option_stats"][option.name]["successes"] += 1
                self._update_avg_execution_time(option.name, execution_time)
                
                logger.debug(f"✅ Option '{option.name}' succeeded in {execution_time:.2f}s")
                
                return FallbackResult(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    attempts_made=attempt + 1
                )
                
            except CircuitBreakerOpenException as e:
                # Circuit breaker открыт - не повторяем
                last_error = e
                break
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Option '{option.name}' attempt {attempt + 1} failed: {e}")
                
                if attempt < option.retry_count:
                    # Экспоненциальная задержка между повторами
                    delay = min(2 ** attempt, 10)  # Максимум 10 секунд
                    time.sleep(delay)
        
        # Все попытки неудачны
        execution_time = time.time() - start_time
        self.stats["option_stats"][option.name]["failures"] += 1
        self._update_avg_execution_time(option.name, execution_time)
        
        logger.error(f"❌ Option '{option.name}' failed after {option.retry_count + 1} attempts")
        
        return FallbackResult(
            success=False,
            error=last_error,
            execution_time=execution_time,
            attempts_made=option.retry_count + 1
        )
    
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
    
    def _update_avg_execution_time(self, option_name: str, execution_time: float):
        """Обновление средней времени выполнения"""
        stats = self.stats["option_stats"][option_name]
        total_executions = stats["executions"]
        
        if total_executions == 1:
            stats["avg_execution_time"] = execution_time
        else:
            # Скользящее среднее
            stats["avg_execution_time"] = (
                (stats["avg_execution_time"] * (total_executions - 1) + execution_time) / 
                total_executions
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики fallback manager"""
        success_rate = 0.0
        if self.stats["total_executions"] > 0:
            success_rate = (self.stats["successful_executions"] / self.stats["total_executions"]) * 100
        
        fallback_rate = 0.0
        if self.stats["successful_executions"] > 0:
            fallback_rate = (self.stats["fallback_executions"] / self.stats["successful_executions"]) * 100
        
        return {
            "name": self.name,
            "strategy": self.strategy.value,
            "total_executions": self.stats["total_executions"],
            "successful_executions": self.stats["successful_executions"],
            "fallback_executions": self.stats["fallback_executions"],
            "success_rate": round(success_rate, 2),
            "fallback_rate": round(fallback_rate, 2),
            "options_count": len(self.options),
            "option_stats": self.stats["option_stats"]
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "fallback_executions": 0,
            "option_stats": {name: {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "avg_execution_time": 0.0
            } for name in self.stats["option_stats"]}
        }
        
        logger.info(f"📊 Stats reset for FallbackManager '{self.name}'")
    
    def remove_option(self, name: str) -> bool:
        """Удаление опции"""
        for i, option in enumerate(self.options):
            if option.name == name:
                del self.options[i]
                if name in self.stats["option_stats"]:
                    del self.stats["option_stats"][name]
                
                logger.info(f"🗑️ Removed option '{name}' from FallbackManager '{self.name}'")
                return True
        
        return False
    
    def clear_options(self):
        """Очистка всех опций"""
        self.options.clear()
        self.stats["option_stats"].clear()
        
        logger.info(f"🧹 Cleared all options from FallbackManager '{self.name}'")
    
    def __len__(self) -> int:
        """Количество опций"""
        return len(self.options)
    
    def __bool__(self) -> bool:
        """Проверка наличия опций"""
        return len(self.options) > 0


class FallbackManagerRegistry:
    """Реестр fallback manager'ов"""
    
    def __init__(self):
        self._managers: Dict[str, FallbackManager] = {}
        
        logger.info("📋 FallbackManagerRegistry initialized")
    
    def create(self, 
               name: str, 
               strategy: FallbackStrategy = FallbackStrategy.SEQUENTIAL) -> FallbackManager:
        """Создание нового fallback manager"""
        if name in self._managers:
            logger.warning(f"⚠️ FallbackManager '{name}' already exists, returning existing")
            return self._managers[name]
        
        manager = FallbackManager(name, strategy)
        self._managers[name] = manager
        
        logger.info(f"🆕 Created FallbackManager '{name}' with strategy {strategy.value}")
        return manager
    
    def get(self, name: str) -> Optional[FallbackManager]:
        """Получение fallback manager по имени"""
        return self._managers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики всех fallback manager'ов"""
        return {name: manager.get_stats() 
               for name, manager in self._managers.items()}
    
    def remove(self, name: str) -> bool:
        """Удаление fallback manager"""
        if name in self._managers:
            del self._managers[name]
            logger.info(f"🗑️ Removed FallbackManager '{name}'")
            return True
        return False
    
    def list_names(self) -> List[str]:
        """Список имен всех fallback manager'ов"""
        return list(self._managers.keys())


# Глобальный реестр fallback manager'ов
fallback_registry = FallbackManagerRegistry()