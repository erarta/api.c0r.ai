"""
Base AI Provider for c0r.AI ML Service
Abstract base class for all AI model providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
from dataclasses import dataclass
from loguru import logger

from ..config.sota_config import ModelConfig


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
    metadata: Optional[Dict[str, Any]] = None


class BaseAIProvider(ABC):
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self.provider_name = config.provider
        self.model_name = config.name
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Инициализация клиента провайдера"""
        pass
    
    @abstractmethod
    async def generate_response(self, 
                              prompt: str,
                              image_data: Optional[bytes] = None,
                              system_prompt: Optional[str] = None,
                              **kwargs) -> ModelResponse:
        """Генерация ответа от модели"""
        pass
    
    @abstractmethod
    def validate_response(self, response: str) -> bool:
        """Валидация ответа модели"""
        pass
    
    async def generate_with_retry(self, 
                                prompt: str,
                                image_data: Optional[bytes] = None,
                                system_prompt: Optional[str] = None,
                                **kwargs) -> ModelResponse:
        """Генерация с повторными попытками"""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.config.retry_attempts} for {self.provider_name}:{self.model_name}")
                
                response = await self.generate_response(
                    prompt, image_data, system_prompt, **kwargs
                )
                
                if response.success:
                    if attempt > 0:
                        logger.info(f"✅ {self.provider_name}:{self.model_name} succeeded on attempt {attempt + 1}")
                    return response
                
                last_error = response.error_message
                logger.warning(f"❌ Attempt {attempt + 1} failed: {last_error}")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"❌ Attempt {attempt + 1} exception: {last_error}")
                
                if attempt < self.config.retry_attempts - 1:
                    # Exponential backoff
                    delay = min(2 ** attempt, 30)  # Max 30 seconds
                    logger.debug(f"⏳ Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
        
        # Все попытки исчерпаны
        logger.error(f"❌ All {self.config.retry_attempts} attempts failed for {self.provider_name}:{self.model_name}")
        
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
    
    def calculate_cost(self, tokens_used: int) -> float:
        """Расчет стоимости запроса"""
        return (tokens_used * self.config.cost_per_1k_tokens) / 1000
    
    def _prepare_messages(self, 
                         prompt: str,
                         image_data: Optional[bytes] = None,
                         system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """Подготовка сообщений для API"""
        messages = []
        
        # Системный промпт
        if system_prompt and self.config.system_prompt_support:
            messages.append({"role": "system", "content": system_prompt})
        
        # Пользовательский промпт
        if image_data and self.config.vision_support:
            # Для провайдеров с поддержкой изображений
            user_content = [{"type": "text", "text": prompt}]
            # Конкретная реализация добавления изображения в дочерних классах
            messages.append({"role": "user", "content": user_content})
        else:
            # Только текст
            messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _extract_content_from_response(self, response_data: Any) -> str:
        """Извлечение контента из ответа (переопределяется в дочерних классах)"""
        return str(response_data)
    
    def _count_tokens_estimate(self, text: str) -> int:
        """Приблизительный подсчет токенов (4 символа = 1 токен)"""
        return len(text) // 4
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья провайдера"""
        try:
            # Простой тестовый запрос
            test_response = await self.generate_response(
                prompt="Test health check",
                image_data=None,
                system_prompt=None
            )
            
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "healthy": test_response.success,
                "response_time": test_response.response_time,
                "error": test_response.error_message if not test_response.success else None
            }
            
        except Exception as e:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "healthy": False,
                "response_time": 0.0,
                "error": str(e)
            }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Информация о провайдере"""
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "tier": self.config.tier.value,
            "vision_support": self.config.vision_support,
            "json_mode": self.config.json_mode,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "cost_per_1k_tokens": self.config.cost_per_1k_tokens
        }
    
    def __str__(self) -> str:
        return f"{self.provider_name}:{self.model_name}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(provider='{self.provider_name}', model='{self.model_name}', tier='{self.config.tier.value}')>"


class ProviderError(Exception):
    """Базовая ошибка провайдера"""
    pass


class ProviderTimeoutError(ProviderError):
    """Ошибка таймаута провайдера"""
    pass


class ProviderRateLimitError(ProviderError):
    """Ошибка превышения лимитов провайдера"""
    pass


class ProviderAuthenticationError(ProviderError):
    """Ошибка аутентификации провайдера"""
    pass


class ProviderQuotaExceededError(ProviderError):
    """Ошибка превышения квоты провайдера"""
    pass