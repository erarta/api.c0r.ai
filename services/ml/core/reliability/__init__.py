"""
Reliability System for c0r.AI ML Service
Provides fallback mechanisms, circuit breakers, and error handling
"""

from .circuit_breaker import CircuitBreaker
from .fallback_manager import FallbackManager
from .retry_handler import RetryHandler
from .health_monitor import HealthMonitor

__all__ = [
    "CircuitBreaker",
    "FallbackManager", 
    "RetryHandler",
    "HealthMonitor"
]

# Version info
__version__ = "1.0.0"
__author__ = "c0r.AI Development Team"
__description__ = "Reliability system with circuit breakers and fallback mechanisms"