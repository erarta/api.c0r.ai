"""
c0r.AI ML Service - New Architecture Integration
Main entry point for the enhanced ML service with SOTA models and regional adaptation
"""

from .core.models.managers.model_manager import ModelManager
from .modules.location.detector import UserLocationDetector as LocationDetector
from .core.prompts.base.prompt_builder import PromptBuilder
from .core.reliability.circuit_breaker import CircuitBreaker, circuit_breaker
from .core.reliability.fallback_manager import FallbackManager
from .core.reliability.health_monitor import HealthMonitor

# Main service class
from .service import MLService

__all__ = [
    "MLService",
    "ModelManager",
    "LocationDetector", 
    "PromptBuilder",
    "CircuitBreaker",
    "circuit_breaker",
    "FallbackManager",
    "HealthMonitor"
]

# Version info
__version__ = "2.0.0"
__author__ = "c0r.AI Development Team"
__description__ = "Enhanced ML service with SOTA models, regional adaptation, and reliability features"

# Service instance for backward compatibility
_service_instance = None

def get_ml_service() -> MLService:
    """
    Get singleton ML service instance
    
    Returns:
        MLService: Configured ML service instance
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = MLService()
    
    return _service_instance


# Backward compatibility functions
def analyze_food_image(image_data: bytes, 
                      user_language: str = "ru",
                      user_context: dict = None,
                      user_id: int = None,
                      telegram_user: dict = None) -> dict:
    """
    Backward compatible food analysis function
    
    Args:
        image_data: Image data in bytes
        user_language: User language code
        user_context: User context and preferences
        user_id: User ID for location detection
        telegram_user: Telegram user data
        
    Returns:
        Analysis result dictionary
    """
    service = get_ml_service()
    
    return service.analyze_food(
        image_data=image_data,
        user_language=user_language,
        user_context=user_context or {},
        user_id=user_id,
        telegram_user=telegram_user
    )


def generate_recipes_from_image(image_data: bytes,
                               user_language: str = "ru", 
                               user_context: dict = None,
                               user_id: int = None,
                               telegram_user: dict = None) -> dict:
    """
    Backward compatible recipe generation function
    
    Args:
        image_data: Image data in bytes
        user_language: User language code
        user_context: User context and preferences
        user_id: User ID for location detection
        telegram_user: Telegram user data
        
    Returns:
        Recipe generation result dictionary
    """
    service = get_ml_service()
    
    return service.generate_recipes(
        image_data=image_data,
        user_language=user_language,
        user_context=user_context or {},
        user_id=user_id,
        telegram_user=telegram_user
    )


def get_service_health() -> dict:
    """
    Get ML service health status
    
    Returns:
        Health status dictionary
    """
    service = get_ml_service()
    return service.get_health_status()


# Initialize logging
import logging
from loguru import logger

# Configure loguru to work with existing logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Set up logging integration
logging.basicConfig(handlers=[InterceptHandler()], level=0)