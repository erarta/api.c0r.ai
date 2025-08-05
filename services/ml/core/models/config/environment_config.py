"""
Environment Configuration for c0r.AI ML Service
Centralized management of environment variables and settings
"""

import os
from typing import Optional, Dict, Any
from loguru import logger


class EnvironmentConfig:
    """Конфигурация из переменных окружения"""
    
    # Основные настройки
    DEFAULT_TIER = os.getenv("ML_DEFAULT_TIER", "sota")
    FALLBACK_ENABLED = os.getenv("ML_FALLBACK_ENABLED", "true").lower() == "true"
    COST_LIMIT_PER_REQUEST = float(os.getenv("ML_COST_LIMIT_PER_REQUEST", "0.10"))
    COST_LIMIT_PER_HOUR = float(os.getenv("ML_COST_LIMIT_PER_HOUR", "10.0"))
    COST_LIMIT_PER_DAY = float(os.getenv("ML_COST_LIMIT_PER_DAY", "100.0"))
    
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
    HTTP_PROXY = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    
    # Геолокация
    MAXMIND_LICENSE_KEY = os.getenv("MAXMIND_LICENSE_KEY")
    IPSTACK_API_KEY = os.getenv("IPSTACK_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Кэширование
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    LOCATION_CACHE_TTL = int(os.getenv("LOCATION_CACHE_TTL", "86400"))  # 24 часа
    REGIONAL_DATA_CACHE_TTL = int(os.getenv("REGIONAL_DATA_CACHE_TTL", "604800"))  # 7 дней
    IP_GEOLOCATION_CACHE_TTL = int(os.getenv("IP_GEOLOCATION_CACHE_TTL", "3600"))  # 1 час
    
    # Fallback настройки
    DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "RU")
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Europe/Moscow")
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ru")
    
    # Мониторинг и логирование
    ENABLE_MODEL_MONITORING = os.getenv("ML_ENABLE_MONITORING", "true").lower() == "true"
    LOG_MODEL_RESPONSES = os.getenv("ML_LOG_RESPONSES", "false").lower() == "true"
    PERFORMANCE_TRACKING = os.getenv("ML_PERFORMANCE_TRACKING", "true").lower() == "true"
    
    # Circuit Breaker настройки
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("ML_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.getenv("ML_CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60"))
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = int(os.getenv("ML_CIRCUIT_BREAKER_SUCCESS_THRESHOLD", "3"))
    
    # Retry настройки
    DEFAULT_RETRY_ATTEMPTS = int(os.getenv("ML_DEFAULT_RETRY_ATTEMPTS", "3"))
    DEFAULT_RETRY_DELAY = float(os.getenv("ML_DEFAULT_RETRY_DELAY", "1.0"))
    MAX_RETRY_DELAY = float(os.getenv("ML_MAX_RETRY_DELAY", "60.0"))
    
    # Timeout настройки
    DEFAULT_REQUEST_TIMEOUT = int(os.getenv("ML_DEFAULT_REQUEST_TIMEOUT", "60"))
    FOOD_ANALYSIS_TIMEOUT = int(os.getenv("ML_FOOD_ANALYSIS_TIMEOUT", "60"))
    RECIPE_GENERATION_TIMEOUT = int(os.getenv("ML_RECIPE_GENERATION_TIMEOUT", "90"))
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """
        Валидация конфигурации и возврат статуса
        
        Returns:
            Словарь с результатами валидации
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "api_keys_status": {}
        }
        
        # Проверка API ключей
        api_keys = {
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "google": cls.GOOGLE_API_KEY
        }
        
        for provider, key in api_keys.items():
            validation_result["api_keys_status"][provider] = bool(key)
            if not key:
                validation_result["warnings"].append(f"{provider.upper()}_API_KEY not configured")
        
        # Проверка обязательных ключей
        if not cls.OPENAI_API_KEY:
            validation_result["errors"].append("OPENAI_API_KEY is required for primary functionality")
            validation_result["valid"] = False
        
        # Проверка числовых значений
        try:
            if cls.COST_LIMIT_PER_REQUEST <= 0:
                validation_result["errors"].append("ML_COST_LIMIT_PER_REQUEST must be positive")
                validation_result["valid"] = False
        except (ValueError, TypeError):
            validation_result["errors"].append("ML_COST_LIMIT_PER_REQUEST must be a valid number")
            validation_result["valid"] = False
        
        # Проверка timeout значений
        if cls.DEFAULT_REQUEST_TIMEOUT <= 0:
            validation_result["errors"].append("ML_DEFAULT_REQUEST_TIMEOUT must be positive")
            validation_result["valid"] = False
        
        # Проверка retry настроек
        if cls.DEFAULT_RETRY_ATTEMPTS < 0:
            validation_result["errors"].append("ML_DEFAULT_RETRY_ATTEMPTS must be non-negative")
            validation_result["valid"] = False
        
        # Проверка cache TTL
        if cls.LOCATION_CACHE_TTL <= 0:
            validation_result["warnings"].append("LOCATION_CACHE_TTL should be positive for effective caching")
        
        return validation_result
    
    @classmethod
    def get_proxy_config(cls) -> Optional[Dict[str, str]]:
        """
        Получить конфигурацию прокси
        
        Returns:
            Словарь с настройками прокси или None
        """
        if cls.HTTP_PROXY or cls.HTTPS_PROXY:
            return {
                "http://": cls.HTTP_PROXY,
                "https://": cls.HTTPS_PROXY
            }
        return None
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """
        Получить конфигурацию кэширования
        
        Returns:
            Словарь с настройками кэша
        """
        return {
            "redis_url": cls.REDIS_URL,
            "location_ttl": cls.LOCATION_CACHE_TTL,
            "regional_data_ttl": cls.REGIONAL_DATA_CACHE_TTL,
            "ip_geolocation_ttl": cls.IP_GEOLOCATION_CACHE_TTL
        }
    
    @classmethod
    def get_circuit_breaker_config(cls) -> Dict[str, int]:
        """
        Получить конфигурацию Circuit Breaker
        
        Returns:
            Словарь с настройками Circuit Breaker
        """
        return {
            "failure_threshold": cls.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            "recovery_timeout": cls.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            "success_threshold": cls.CIRCUIT_BREAKER_SUCCESS_THRESHOLD
        }
    
    @classmethod
    def get_retry_config(cls) -> Dict[str, Any]:
        """
        Получить конфигурацию повторных попыток
        
        Returns:
            Словарь с настройками retry
        """
        return {
            "max_attempts": cls.DEFAULT_RETRY_ATTEMPTS,
            "base_delay": cls.DEFAULT_RETRY_DELAY,
            "max_delay": cls.MAX_RETRY_DELAY
        }
    
    @classmethod
    def log_configuration_status(cls):
        """Логирование статуса конфигурации"""
        validation = cls.validate_configuration()
        
        if validation["valid"]:
            logger.info("✅ ML Service configuration is valid")
        else:
            logger.error("❌ ML Service configuration has errors:")
            for error in validation["errors"]:
                logger.error(f"  - {error}")
        
        if validation["warnings"]:
            logger.warning("⚠️ ML Service configuration warnings:")
            for warning in validation["warnings"]:
                logger.warning(f"  - {warning}")
        
        # Логируем статус API ключей
        api_status = validation["api_keys_status"]
        logger.info("🔑 API Keys status:")
        for provider, configured in api_status.items():
            status = "✅ Configured" if configured else "❌ Missing"
            logger.info(f"  - {provider.upper()}: {status}")
        
        # Логируем основные настройки
        logger.info("⚙️ Key settings:")
        logger.info(f"  - Default tier: {cls.DEFAULT_TIER}")
        logger.info(f"  - Fallback enabled: {cls.FALLBACK_ENABLED}")
        logger.info(f"  - Cost limit per request: ${cls.COST_LIMIT_PER_REQUEST}")
        logger.info(f"  - Monitoring enabled: {cls.ENABLE_MODEL_MONITORING}")
        logger.info(f"  - Performance tracking: {cls.PERFORMANCE_TRACKING}")


# Валидация конфигурации при импорте
_validation_result = EnvironmentConfig.validate_configuration()
if not _validation_result["valid"]:
    logger.error("❌ Critical configuration errors detected!")
    for error in _validation_result["errors"]:
        logger.error(f"  - {error}")