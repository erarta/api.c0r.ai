"""
Health Monitor for c0r.AI ML Service
Monitors system health and provides health checks
"""

import time
import threading
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger


class HealthStatus(Enum):
    """Статусы здоровья компонентов"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Результат проверки здоровья"""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    error: Optional[Exception] = None


@dataclass
class HealthCheckConfig:
    """Конфигурация проверки здоровья"""
    name: str
    check_function: Callable[[], HealthCheckResult]
    interval: int = 60                    # Интервал проверки в секундах
    timeout: float = 10.0                 # Таймаут проверки
    enabled: bool = True                  # Включена ли проверка
    critical: bool = False                # Критическая ли проверка
    retry_count: int = 2                  # Количество повторов при ошибке
    tags: List[str] = field(default_factory=list)  # Теги для группировки


class HealthMonitor:
    """
    Монитор здоровья системы
    
    Выполняет периодические проверки здоровья компонентов системы
    и предоставляет агрегированную информацию о состоянии
    """
    
    def __init__(self, name: str = "system"):
        self.name = name
        self.checks: Dict[str, HealthCheckConfig] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.history: Dict[str, List[HealthCheckResult]] = {}
        self.max_history_size = 100
        
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # Статистика
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "avg_response_time": 0.0,
            "uptime_start": datetime.now()
        }
        
        logger.info(f"🏥 HealthMonitor '{name}' initialized")
    
    def add_check(self, config: HealthCheckConfig) -> 'HealthMonitor':
        """
        Добавление проверки здоровья
        
        Args:
            config: Конфигурация проверки
            
        Returns:
            Self для цепочки вызовов
        """
        with self._lock:
            self.checks[config.name] = config
            self.history[config.name] = []
            
            logger.info(f"➕ Added health check '{config.name}' with interval {config.interval}s")
            
        return self
    
    def remove_check(self, name: str) -> bool:
        """Удаление проверки здоровья"""
        with self._lock:
            if name in self.checks:
                del self.checks[name]
                if name in self.results:
                    del self.results[name]
                if name in self.history:
                    del self.history[name]
                
                logger.info(f"🗑️ Removed health check '{name}'")
                return True
            
            return False
    
    def run_check(self, name: str) -> Optional[HealthCheckResult]:
        """
        Выполнение одной проверки здоровья
        
        Args:
            name: Имя проверки
            
        Returns:
            Результат проверки или None если проверка не найдена
        """
        with self._lock:
            if name not in self.checks:
                logger.warning(f"⚠️ Health check '{name}' not found")
                return None
            
            config = self.checks[name]
            
            if not config.enabled:
                logger.debug(f"⏸️ Health check '{name}' is disabled")
                return None
        
        return self._execute_check(config)
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Выполнение всех проверок здоровья"""
        results = {}
        
        with self._lock:
            enabled_checks = {name: config for name, config in self.checks.items() 
                            if config.enabled}
        
        for name, config in enabled_checks.items():
            result = self._execute_check(config)
            if result:
                results[name] = result
        
        logger.debug(f"🔍 Executed {len(results)} health checks")
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Получение общего статуса здоровья системы"""
        with self._lock:
            if not self.results:
                return HealthStatus.UNKNOWN
            
            # Проверяем критические компоненты
            critical_checks = [name for name, config in self.checks.items() 
                             if config.critical and config.enabled]
            
            for check_name in critical_checks:
                if check_name in self.results:
                    result = self.results[check_name]
                    if result.status == HealthStatus.UNHEALTHY:
                        return HealthStatus.UNHEALTHY
            
            # Проверяем все компоненты
            statuses = [result.status for result in self.results.values()]
            
            if all(status == HealthStatus.HEALTHY for status in statuses):
                return HealthStatus.HEALTHY
            elif any(status == HealthStatus.UNHEALTHY for status in statuses):
                return HealthStatus.DEGRADED
            elif any(status == HealthStatus.DEGRADED for status in statuses):
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.UNKNOWN
    
    def get_health_report(self) -> Dict[str, Any]:
        """Получение полного отчета о здоровье"""
        with self._lock:
            overall_status = self.get_overall_status()
            
            # Группировка по статусам
            status_counts = {status.value: 0 for status in HealthStatus}
            for result in self.results.values():
                status_counts[result.status.value] += 1
            
            # Критические проблемы
            critical_issues = []
            for name, config in self.checks.items():
                if config.critical and name in self.results:
                    result = self.results[name]
                    if result.status != HealthStatus.HEALTHY:
                        critical_issues.append({
                            "name": name,
                            "status": result.status.value,
                            "message": result.message,
                            "timestamp": result.timestamp.isoformat()
                        })
            
            # Статистика производительности
            avg_response_time = 0.0
            if self.results:
                avg_response_time = sum(r.response_time for r in self.results.values()) / len(self.results)
            
            uptime = datetime.now() - self.stats["uptime_start"]
            
            return {
                "monitor_name": self.name,
                "overall_status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": int(uptime.total_seconds()),
                "checks": {
                    "total": len(self.checks),
                    "enabled": len([c for c in self.checks.values() if c.enabled]),
                    "critical": len([c for c in self.checks.values() if c.critical])
                },
                "status_distribution": status_counts,
                "critical_issues": critical_issues,
                "performance": {
                    "avg_response_time": round(avg_response_time, 3),
                    "total_checks_executed": self.stats["total_checks"],
                    "success_rate": self._calculate_success_rate()
                },
                "individual_checks": {
                    name: {
                        "status": result.status.value,
                        "message": result.message,
                        "response_time": result.response_time,
                        "timestamp": result.timestamp.isoformat(),
                        "details": result.details
                    }
                    for name, result in self.results.items()
                }
            }
    
    def start_monitoring(self, check_interval: int = 30):
        """
        Запуск фонового мониторинга
        
        Args:
            check_interval: Интервал между циклами проверок (секунды)
        """
        if self._running:
            logger.warning("⚠️ Health monitoring is already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True,
            name=f"HealthMonitor-{self.name}"
        )
        self._monitor_thread.start()
        
        logger.info(f"🚀 Started health monitoring with {check_interval}s interval")
    
    def stop_monitoring(self):
        """Остановка фонового мониторинга"""
        if not self._running:
            logger.warning("⚠️ Health monitoring is not running")
            return
        
        self._running = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("🛑 Stopped health monitoring")
    
    def _execute_check(self, config: HealthCheckConfig) -> Optional[HealthCheckResult]:
        """Выполнение одной проверки с повторами"""
        last_error = None
        
        for attempt in range(config.retry_count + 1):
            try:
                start_time = time.time()
                
                # Выполняем проверку с таймаутом
                result = self._execute_with_timeout(
                    config.check_function, 
                    config.timeout
                )
                
                response_time = time.time() - start_time
                result.response_time = response_time
                
                # Сохраняем результат
                with self._lock:
                    self.results[config.name] = result
                    self._add_to_history(config.name, result)
                    self._update_stats(True, response_time)
                
                if result.status == HealthStatus.HEALTHY:
                    logger.debug(f"✅ Health check '{config.name}' passed in {response_time:.3f}s")
                else:
                    logger.warning(f"⚠️ Health check '{config.name}' status: {result.status.value}")
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"❌ Health check '{config.name}' attempt {attempt + 1} failed: {e}")
                
                if attempt < config.retry_count:
                    time.sleep(1)  # Короткая задержка между повторами
        
        # Все попытки неудачны
        error_result = HealthCheckResult(
            name=config.name,
            status=HealthStatus.UNHEALTHY,
            message=f"Check failed after {config.retry_count + 1} attempts: {last_error}",
            error=last_error,
            response_time=config.timeout
        )
        
        with self._lock:
            self.results[config.name] = error_result
            self._add_to_history(config.name, error_result)
            self._update_stats(False, config.timeout)
        
        return error_result
    
    def _execute_with_timeout(self, func: Callable, timeout: float) -> HealthCheckResult:
        """Выполнение функции с таймаутом"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Health check exceeded {timeout} seconds")
        
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
            
            try:
                result = func()
                signal.alarm(0)
                return result
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Для Windows - простое выполнение
            return func()
    
    def _monitoring_loop(self, check_interval: int):
        """Основной цикл мониторинга"""
        logger.info(f"🔄 Health monitoring loop started")
        
        while self._running:
            try:
                # Определяем какие проверки нужно выполнить
                checks_to_run = []
                current_time = time.time()
                
                with self._lock:
                    for name, config in self.checks.items():
                        if not config.enabled:
                            continue
                        
                        # Проверяем, пора ли выполнять проверку
                        last_result = self.results.get(name)
                        if (last_result is None or 
                            (current_time - last_result.timestamp.timestamp()) >= config.interval):
                            checks_to_run.append(config)
                
                # Выполняем проверки
                for config in checks_to_run:
                    if not self._running:
                        break
                    
                    self._execute_check(config)
                
                # Ждем до следующего цикла
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in health monitoring loop: {e}")
                time.sleep(check_interval)
        
        logger.info("🏁 Health monitoring loop stopped")
    
    def _add_to_history(self, check_name: str, result: HealthCheckResult):
        """Добавление результата в историю"""
        if check_name not in self.history:
            self.history[check_name] = []
        
        self.history[check_name].append(result)
        
        # Ограничиваем размер истории
        if len(self.history[check_name]) > self.max_history_size:
            self.history[check_name] = self.history[check_name][-self.max_history_size:]
    
    def _update_stats(self, success: bool, response_time: float):
        """Обновление статистики"""
        self.stats["total_checks"] += 1
        
        if success:
            self.stats["successful_checks"] += 1
        else:
            self.stats["failed_checks"] += 1
        
        # Обновляем среднее время ответа
        total_checks = self.stats["total_checks"]
        if total_checks == 1:
            self.stats["avg_response_time"] = response_time
        else:
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (total_checks - 1) + response_time) /
                total_checks
            )
    
    def _calculate_success_rate(self) -> float:
        """Расчет процента успешных проверок"""
        if self.stats["total_checks"] == 0:
            return 0.0
        
        return (self.stats["successful_checks"] / self.stats["total_checks"]) * 100
    
    def get_check_history(self, check_name: str, limit: int = 10) -> List[HealthCheckResult]:
        """Получение истории проверки"""
        with self._lock:
            history = self.history.get(check_name, [])
            return history[-limit:] if limit > 0 else history
    
    def enable_check(self, name: str) -> bool:
        """Включение проверки"""
        with self._lock:
            if name in self.checks:
                self.checks[name].enabled = True
                logger.info(f"✅ Enabled health check '{name}'")
                return True
            return False
    
    def disable_check(self, name: str) -> bool:
        """Отключение проверки"""
        with self._lock:
            if name in self.checks:
                self.checks[name].enabled = False
                logger.info(f"⏸️ Disabled health check '{name}'")
                return True
            return False
    
    def reset_stats(self):
        """Сброс статистики"""
        with self._lock:
            self.stats = {
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0,
                "avg_response_time": 0.0,
                "uptime_start": datetime.now()
            }
            
            logger.info(f"📊 Stats reset for HealthMonitor '{self.name}'")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()


# Предопределенные проверки здоровья

def create_database_health_check(connection_func: Callable) -> Callable[[], HealthCheckResult]:
    """Создание проверки здоровья базы данных"""
    def check() -> HealthCheckResult:
        try:
            start_time = time.time()
            connection_func()
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={"response_time": response_time}
            )
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {e}",
                error=e
            )
    
    return check


def create_api_health_check(url: str, timeout: float = 5.0) -> Callable[[], HealthCheckResult]:
    """Создание проверки здоровья API"""
    def check() -> HealthCheckResult:
        try:
            import requests
            
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthCheckResult(
                    name="api",
                    status=HealthStatus.HEALTHY,
                    message=f"API endpoint {url} is healthy",
                    details={
                        "status_code": response.status_code,
                        "response_time": response_time
                    }
                )
            else:
                return HealthCheckResult(
                    name="api",
                    status=HealthStatus.DEGRADED,
                    message=f"API endpoint returned status {response.status_code}",
                    details={
                        "status_code": response.status_code,
                        "response_time": response_time
                    }
                )
                
        except Exception as e:
            return HealthCheckResult(
                name="api",
                status=HealthStatus.UNHEALTHY,
                message=f"API endpoint {url} is unreachable: {e}",
                error=e
            )
    
    return check


def create_memory_health_check(threshold_percent: float = 80.0) -> Callable[[], HealthCheckResult]:
    """Создание проверки использования памяти"""
    def check() -> HealthCheckResult:
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent < threshold_percent:
                status = HealthStatus.HEALTHY
                message = f"Memory usage is normal: {usage_percent:.1f}%"
            elif usage_percent < 90.0:
                status = HealthStatus.DEGRADED
                message = f"Memory usage is high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage is critical: {usage_percent:.1f}%"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "available_gb": round(memory.available / (1024**3), 2),
                    "total_gb": round(memory.total / (1024**3), 2)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check memory usage: {e}",
                error=e
            )
    
    return check


# Глобальный монитор здоровья
global_health_monitor = HealthMonitor("global")