"""
OpenAI Provider for c0r.AI ML Service
Implementation of OpenAI GPT-4o and GPT-4o-mini models
"""

import openai
import base64
import json
import time
from typing import Optional, Dict, Any
import httpx
from loguru import logger

from .base_provider import BaseAIProvider, ModelResponse, ProviderError, ProviderTimeoutError, ProviderRateLimitError, ProviderAuthenticationError, ProviderQuotaExceededError
from ..config.environment_config import EnvironmentConfig


class OpenAIProvider(BaseAIProvider):
    """Провайдер для OpenAI GPT-4o и GPT-4o-mini"""
    
    def _initialize_client(self):
        """Инициализация OpenAI клиента"""
        api_key = EnvironmentConfig.OPENAI_API_KEY
        if not api_key:
            raise ProviderAuthenticationError("OPENAI_API_KEY not provided")
        
        # Настройка прокси если необходимо
        http_client = None
        proxy_config = EnvironmentConfig.get_proxy_config()
        
        if proxy_config:
            logger.info(f"🌐 Using proxy for OpenAI: {proxy_config}")
            http_client = httpx.Client(proxies=proxy_config)
        
        try:
            self.client = openai.OpenAI(
                api_key=api_key,
                http_client=http_client,
                timeout=self.config.timeout
            )
            logger.info(f"✅ OpenAI client initialized for {self.model_name}")
        except Exception as e:
            raise ProviderError(f"Failed to initialize OpenAI client: {e}")
    
    async def generate_response(self, 
                              prompt: str,
                              image_data: Optional[bytes] = None,
                              system_prompt: Optional[str] = None,
                              **kwargs) -> ModelResponse:
        """Генерация ответа через OpenAI API"""
        start_time = time.time()
        
        try:
            messages = self._prepare_openai_messages(prompt, image_data, system_prompt)
            
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
            
            # Дополнительные параметры из kwargs
            request_params.update(kwargs)
            
            logger.debug(f"🚀 OpenAI request: {self.model_name}, tokens_limit: {self.config.max_tokens}")
            
            # Выполнение запроса
            response = await self._make_openai_request(request_params)
            
            # Обработка ответа
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else self._count_tokens_estimate(content)
            cost = self.calculate_cost(tokens_used)
            response_time = time.time() - start_time
            
            # Валидация ответа
            if not self.validate_response(content):
                logger.warning(f"⚠️ Response validation failed for {self.model_name}")
                return ModelResponse(
                    content=content,
                    model_used=self.config.name,
                    provider=self.config.provider,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    success=False,
                    error_message="Response validation failed"
                )
            
            logger.info(f"✅ OpenAI response: {self.model_name}, tokens: {tokens_used}, cost: ${cost:.4f}, time: {response_time:.2f}s")
            
            return ModelResponse(
                content=content,
                model_used=self.config.name,
                provider=self.config.provider,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                success=True,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = self._handle_openai_error(e)
            
            logger.error(f"❌ OpenAI error: {error_message}")
            
            return ModelResponse(
                content="",
                model_used=self.config.name,
                provider=self.config.provider,
                tokens_used=0,
                cost=0.0,
                response_time=response_time,
                success=False,
                error_message=error_message
            )
    
    def _prepare_openai_messages(self, 
                                prompt: str,
                                image_data: Optional[bytes] = None,
                                system_prompt: Optional[str] = None) -> list:
        """Подготовка сообщений для OpenAI API"""
        messages = []
        
        # Системный промпт
        if system_prompt and self.config.system_prompt_support:
            messages.append({"role": "system", "content": system_prompt})
        
        # Пользовательский промпт с изображением
        if image_data and self.config.vision_support:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high"  # Высокое качество для лучшего анализа
                    }
                }
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            # Только текст
            messages.append({"role": "user", "content": prompt})
        
        return messages
    
    async def _make_openai_request(self, request_params: Dict[str, Any]):
        """Выполнение запроса к OpenAI API в отдельном потоке, чтобы не блокировать event loop."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, lambda: self.client.chat.completions.create(**request_params)
            )
            return response
        except openai.RateLimitError as e:
            raise ProviderRateLimitError(f"OpenAI rate limit exceeded: {e}")
        except openai.AuthenticationError as e:
            raise ProviderAuthenticationError(f"OpenAI authentication failed: {e}")
        except openai.APITimeoutError as e:
            raise ProviderTimeoutError(f"OpenAI request timeout: {e}")
        except openai.BadRequestError as e:
            if "quota" in str(e).lower():
                raise ProviderQuotaExceededError(f"OpenAI quota exceeded: {e}")
            raise ProviderError(f"OpenAI bad request: {e}")
        except Exception as e:
            raise ProviderError(f"OpenAI API error: {e}")
    
    def _handle_openai_error(self, error: Exception) -> str:
        """Обработка ошибок OpenAI"""
        if isinstance(error, openai.RateLimitError):
            return f"Rate limit exceeded: {error}"
        elif isinstance(error, openai.AuthenticationError):
            return f"Authentication failed: {error}"
        elif isinstance(error, openai.APITimeoutError):
            return f"Request timeout: {error}"
        elif isinstance(error, openai.BadRequestError):
            if "quota" in str(error).lower():
                return f"Quota exceeded: {error}"
            return f"Bad request: {error}"
        elif isinstance(error, openai.APIConnectionError):
            return f"Connection error: {error}"
        elif isinstance(error, openai.InternalServerError):
            return f"OpenAI internal server error: {error}"
        else:
            return f"Unexpected error: {error}"
    
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
                logger.warning(f"⚠️ JSON validation failed for response: {response[:100]}...")
                return False
        
        return True
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Извлечение JSON из ответа с улучшенной обработкой"""
        try:
            # Очистка ответа
            content = response.strip()
            
            # Удаление markdown блоков
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            # Поиск JSON в тексте
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            return json.loads(content)
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to extract JSON from response: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья OpenAI провайдера"""
        try:
            start_time = time.time()
            
            # Простой тестовый запрос
            test_response = await self.generate_response(
                prompt="Hello, this is a health check. Please respond with 'OK'.",
                image_data=None,
                system_prompt=None
            )
            
            response_time = time.time() - start_time
            
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "healthy": test_response.success,
                "response_time": response_time,
                "tokens_used": test_response.tokens_used,
                "cost": test_response.cost,
                "error": test_response.error_message if not test_response.success else None,
                "response_content": test_response.content[:50] if test_response.success else None
            }
            
        except Exception as e:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "healthy": False,
                "response_time": 0.0,
                "tokens_used": 0,
                "cost": 0.0,
                "error": str(e)
            }
    
    def get_model_capabilities(self) -> Dict[str, Any]:
        """Получение возможностей модели"""
        return {
            "vision_support": self.config.vision_support,
            "json_mode": self.config.json_mode,
            "system_prompt_support": self.config.system_prompt_support,
            "max_tokens": self.config.max_tokens,
            "supports_streaming": True,  # OpenAI поддерживает streaming
            "supports_function_calling": self.model_name in ["gpt-4o", "gpt-4o-mini"],
            "context_window": 128000 if "gpt-4o" in self.model_name else 4096
        }