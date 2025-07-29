"""
Model Manager for c0r.AI ML Service
Central management of all AI models and providers
"""

from typing import Dict, Optional, List, Any
import asyncio
from loguru import logger

from ..config.sota_config import ModelConfig, TaskType, ModelTier, SOTA_MODEL_CONFIGS, get_model_config
from ..config.environment_config import EnvironmentConfig
from ..providers.base_provider import BaseAIProvider, ModelResponse
from ..providers.openai_provider import OpenAIProvider


class ModelManager:
    """Основной менеджер ML моделей"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.initialized = False
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Инициализация всех доступных провайдеров"""
        logger.info("🚀 Initializing ML model providers...")
        
        try:
            # OpenAI провайдеры
            if EnvironmentConfig.OPENAI_API_KEY:
                self._initialize_openai_providers()
            else:
                logger.warning("⚠️ OpenAI API key not found, skipping OpenAI providers")
            
            # TODO: Добавить другие провайдеры (Anthropic, Google)
            # if EnvironmentConfig.ANTHROPIC_API_KEY:
            #     self._initialize_anthropic_providers()
            
            self.initialized = True
            logger.info(f"✅ Model Manager initialized with {len(self.providers)} providers")
            
            # Логируем доступные провайдеры
            for provider_key, provider in self.providers.items():
                logger.info(f"  - {provider_key}: {provider}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Model Manager: {e}")
            raise
    
    def _initialize_openai_providers(self):
        """Инициализация OpenAI провайдеров"""
        logger.info("🔧 Initializing OpenAI providers...")
        
        for task_type in TaskType:
            task_configs = SOTA_MODEL_CONFIGS.get(task_type, {})
            
            for tier, config in task_configs.items():
                if config.provider == "openai":
                    try:
                        provider_key = f"{task_type.value}_{tier.value}_openai"
                        provider = OpenAIProvider(config)
                        self.providers[provider_key] = provider
                        logger.debug(f"  ✅ {provider_key}: {config.name}")
                    except Exception as e:
                        logger.error(f"  ❌ Failed to initialize {provider_key}: {e}")
    
    async def generate_food_analysis(self,
                                   image_data: bytes,
                                   user_language: str,
                                   regional_context: Dict[str, Any],
                                   user_profile: Dict[str, Any],
                                   tier: ModelTier = None) -> ModelResponse:
        """Генерация анализа еды"""
        
        # Определяем tier из конфигурации или используем переданный
        if tier is None:
            tier_name = EnvironmentConfig.DEFAULT_TIER.lower()
            tier = ModelTier(tier_name) if tier_name in [t.value for t in ModelTier] else ModelTier.SOTA
        
        logger.info(f"🍽️ Generating food analysis with tier: {tier.value}")
        
        try:
            # Получаем конфигурацию модели
            config = get_model_config(TaskType.FOOD_ANALYSIS, tier)
            provider_key = f"{TaskType.FOOD_ANALYSIS.value}_{tier.value}_{config.provider}"
            
            if provider_key not in self.providers:
                logger.warning(f"⚠️ Provider {provider_key} not available, trying fallback...")
                return await self._try_fallback_analysis(image_data, user_language, regional_context, user_profile)
            
            provider = self.providers[provider_key]
            
            # Используем PromptBuilder для создания улучшенного промпта
            from ...prompts.base.prompt_builder import PromptBuilder
            from ....modules.location.models import RegionalContext
            
            prompt_builder = PromptBuilder()
            
            # Преобразуем regional_context в объект RegionalContext если нужно
            if regional_context and not isinstance(regional_context, RegionalContext):
                # Создаем базовый региональный контекст если передан dict
                from ....modules.location.models import RegionalContext
                regional_context_obj = RegionalContext(
                    region_code=regional_context.get('region_code', 'RU'),
                    cuisine_types=regional_context.get('cuisine_types', ['русская']),
                    common_products=regional_context.get('common_products', ['картофель', 'капуста', 'морковь']),
                    cooking_methods=regional_context.get('cooking_methods', ['варка', 'жарка', 'тушение']),
                    measurement_units=regional_context.get('measurement_units', 'metric'),
                    food_culture_notes=regional_context.get('food_culture_notes', 'Традиционная русская кухня'),
                    seasonal_products=regional_context.get('seasonal_products', {})
                )
            else:
                regional_context_obj = regional_context
            
            # Создаем улучшенный промпт с мотивацией и региональным контекстом
            prompt = prompt_builder.build_food_analysis_prompt(
                user_language=user_language,
                regional_context=regional_context_obj,
                user_profile=user_profile or {},
                motivation_level="standard"
            )
            
            # Генерируем ответ
            logger.debug(f"🚀 Using provider: {provider}")
            response = await provider.generate_with_retry(prompt, image_data)
            
            # Логируем результат
            if response.success:
                logger.info(f"✅ Food analysis completed: {response.model_used}, tokens: {response.tokens_used}, cost: ${response.cost:.4f}")
            else:
                logger.error(f"❌ Food analysis failed: {response.error_message}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Food analysis error: {e}")
            return ModelResponse(
                content="",
                model_used="error",
                provider="error",
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def generate_triple_recipes(self,
                                    image_data: bytes,
                                    user_language: str,
                                    user_context: Dict[str, Any],
                                    regional_context: Dict[str, Any],
                                    tier: ModelTier = None) -> ModelResponse:
        """Генерация трех рецептов"""
        
        # Определяем tier
        if tier is None:
            tier_name = EnvironmentConfig.DEFAULT_TIER.lower()
            tier = ModelTier(tier_name) if tier_name in [t.value for t in ModelTier] else ModelTier.SOTA
        
        logger.info(f"👨‍🍳 Generating triple recipes with tier: {tier.value}")
        
        try:
            config = get_model_config(TaskType.RECIPE_GENERATION, tier)
            provider_key = f"{TaskType.RECIPE_GENERATION.value}_{tier.value}_{config.provider}"
            
            if provider_key not in self.providers:
                logger.warning(f"⚠️ Provider {provider_key} not available, trying fallback...")
                return await self._try_fallback_recipes(image_data, user_language, user_context, regional_context)
            
            provider = self.providers[provider_key]
            
            # Используем PromptBuilder для создания улучшенного промпта рецептов
            from ...prompts.base.prompt_builder import PromptBuilder
            from ....modules.location.models import RegionalContext
            
            prompt_builder = PromptBuilder()
            
            # Преобразуем regional_context в объект RegionalContext если нужно
            if regional_context and not isinstance(regional_context, RegionalContext):
                from ....modules.location.models import RegionalContext
                regional_context_obj = RegionalContext(
                    region_code=regional_context.get('region_code', 'RU'),
                    cuisine_types=regional_context.get('cuisine_types', ['русская']),
                    common_products=regional_context.get('common_products', ['картофель', 'капуста', 'морковь']),
                    cooking_methods=regional_context.get('cooking_methods', ['варка', 'жарка', 'тушение']),
                    measurement_units=regional_context.get('measurement_units', 'metric'),
                    food_culture_notes=regional_context.get('food_culture_notes', 'Традиционная русская кухня'),
                    seasonal_products=regional_context.get('seasonal_products', {})
                )
            else:
                regional_context_obj = regional_context
            
            # Создаем улучшенный промпт для генерации рецептов
            prompt = prompt_builder.build_recipe_generation_prompt(
                user_language=user_language,
                regional_context=regional_context_obj,
                user_profile=user_context or {},
                recipe_count=3
            )
            
            # Генерируем ответ
            logger.debug(f"🚀 Using provider: {provider}")
            response = await provider.generate_with_retry(prompt, image_data)
            
            # Логируем результат
            if response.success:
                logger.info(f"✅ Recipe generation completed: {response.model_used}, tokens: {response.tokens_used}, cost: ${response.cost:.4f}")
            else:
                logger.error(f"❌ Recipe generation failed: {response.error_message}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Recipe generation error: {e}")
            return ModelResponse(
                content="",
                model_used="error",
                provider="error",
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _try_fallback_analysis(self,
                                   image_data: bytes,
                                   user_language: str,
                                   regional_context: Dict[str, Any],
                                   user_profile: Dict[str, Any]) -> ModelResponse:
        """Попытка fallback для анализа еды"""
        
        # Пробуем доступные провайдеры в порядке приоритета
        fallback_order = [ModelTier.PREMIUM, ModelTier.STANDARD, ModelTier.BUDGET]
        
        for tier in fallback_order:
            try:
                config = get_model_config(TaskType.FOOD_ANALYSIS, tier)
                provider_key = f"{TaskType.FOOD_ANALYSIS.value}_{tier.value}_{config.provider}"
                
                if provider_key in self.providers:
                    logger.info(f"🔄 Trying fallback with {provider_key}")
                    provider = self.providers[provider_key]
                    # Используем PromptBuilder и для fallback
                    from ...prompts.base.prompt_builder import PromptBuilder
                    from ....modules.location.models import RegionalContext
                    
                    prompt_builder = PromptBuilder()
                    
                    # Преобразуем regional_context в объект RegionalContext если нужно
                    if regional_context and not isinstance(regional_context, RegionalContext):
                        from ....modules.location.models import RegionalContext
                        regional_context_obj = RegionalContext(
                            region_code=regional_context.get('region_code', 'RU'),
                            cuisine_types=regional_context.get('cuisine_types', ['русская']),
                            common_products=regional_context.get('common_products', ['картофель', 'капуста', 'морковь']),
                            cooking_methods=regional_context.get('cooking_methods', ['варка', 'жарка', 'тушение']),
                            measurement_units=regional_context.get('measurement_units', 'metric'),
                            food_culture_notes=regional_context.get('food_culture_notes', 'Традиционная русская кухня'),
                            seasonal_products=regional_context.get('seasonal_products', {})
                        )
                    else:
                        regional_context_obj = regional_context
                    
                    prompt = prompt_builder.build_food_analysis_prompt(
                        user_language=user_language,
                        regional_context=regional_context_obj,
                        user_profile=user_profile or {},
                        motivation_level="standard"
                    )
                    response = await provider.generate_with_retry(prompt, image_data)
                    
                    if response.success:
                        logger.info(f"✅ Fallback successful with {provider_key}")
                        return response
                    
            except Exception as e:
                logger.warning(f"⚠️ Fallback attempt failed with {tier.value}: {e}")
                continue
        
        # Все fallback не сработали
        logger.error("❌ All fallback attempts failed")
        return ModelResponse(
            content="",
            model_used="fallback_failed",
            provider="none",
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            success=False,
            error_message="All fallback options failed"
        )
    
    async def _try_fallback_recipes(self,
                                  image_data: bytes,
                                  user_language: str,
                                  user_context: Dict[str, Any],
                                  regional_context: Dict[str, Any]) -> ModelResponse:
        """Попытка fallback для генерации рецептов"""
        
        fallback_order = [ModelTier.PREMIUM, ModelTier.STANDARD, ModelTier.BUDGET]
        
        for tier in fallback_order:
            try:
                config = get_model_config(TaskType.RECIPE_GENERATION, tier)
                provider_key = f"{TaskType.RECIPE_GENERATION.value}_{tier.value}_{config.provider}"
                
                if provider_key in self.providers:
                    logger.info(f"🔄 Trying fallback with {provider_key}")
                    provider = self.providers[provider_key]
                    # Используем PromptBuilder и для fallback рецептов
                    from ...prompts.base.prompt_builder import PromptBuilder
                    from ....modules.location.models import RegionalContext
                    
                    prompt_builder = PromptBuilder()
                    
                    # Преобразуем regional_context в объект RegionalContext если нужно
                    if regional_context and not isinstance(regional_context, RegionalContext):
                        from ....modules.location.models import RegionalContext
                        regional_context_obj = RegionalContext(
                            region_code=regional_context.get('region_code', 'RU'),
                            cuisine_types=regional_context.get('cuisine_types', ['русская']),
                            common_products=regional_context.get('common_products', ['картофель', 'капуста', 'морковь']),
                            cooking_methods=regional_context.get('cooking_methods', ['варка', 'жарка', 'тушение']),
                            measurement_units=regional_context.get('measurement_units', 'metric'),
                            food_culture_notes=regional_context.get('food_culture_notes', 'Традиционная русская кухня'),
                            seasonal_products=regional_context.get('seasonal_products', {})
                        )
                    else:
                        regional_context_obj = regional_context
                    
                    prompt = prompt_builder.build_recipe_generation_prompt(
                        user_language=user_language,
                        regional_context=regional_context_obj,
                        user_profile=user_context or {},
                        recipe_count=3
                    )
                    response = await provider.generate_with_retry(prompt, image_data)
                    
                    if response.success:
                        logger.info(f"✅ Fallback successful with {provider_key}")
                        return response
                    
            except Exception as e:
                logger.warning(f"⚠️ Fallback attempt failed with {tier.value}: {e}")
                continue
        
        logger.error("❌ All recipe fallback attempts failed")
        return ModelResponse(
            content="",
            model_used="fallback_failed",
            provider="none",
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            success=False,
            error_message="All recipe fallback options failed"
        )
    
    def _create_basic_food_analysis_prompt(self, user_language: str, regional_context: Dict[str, Any]) -> str:
        """Создание базового промпта для анализа еды (временная реализация)"""
        
        if user_language == "ru":
            return """
            Проанализируйте это изображение еды и предоставьте подробную информацию о питании.

            ВАЖНО: Отвечайте ТОЛЬКО валидным JSON объектом без дополнительного текста.

            Верните ТОЛЬКО этот JSON объект:
            {
                "food_items": [
                    {
                        "name": "русское название продукта",
                        "weight": "вес в граммах",
                        "calories": число_калорий
                    }
                ],
                "total_nutrition": {
                    "calories": общее_число_калорий,
                    "proteins": граммы_белков,
                    "fats": граммы_жиров,
                    "carbohydrates": граммы_углеводов
                }
            }
            """
        else:
            return """
            Analyze this food image and provide detailed nutritional information.

            IMPORTANT: Respond with ONLY a valid JSON object, no additional text.

            Return ONLY this JSON object:
            {
                "food_items": [
                    {
                        "name": "specific food name",
                        "weight": "weight in grams",
                        "calories": calorie_number
                    }
                ],
                "total_nutrition": {
                    "calories": total_calorie_number,
                    "proteins": protein_grams,
                    "fats": fat_grams,
                    "carbohydrates": carb_grams
                }
            }
            """
    
    def _create_basic_recipe_generation_prompt(self, user_language: str, regional_context: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Создание базового промпта для генерации рецептов (временная реализация)"""
        
        if user_language == "ru":
            return """
            Создайте рецепт на основе предоставленной информации.

            Верните ТОЛЬКО JSON объект:
            {
                "name": "название рецепта",
                "description": "описание блюда",
                "prep_time": "время подготовки",
                "cook_time": "время приготовления",
                "servings": "количество порций",
                "ingredients": ["список ингредиентов"],
                "instructions": ["пошаговые инструкции"],
                "nutrition": {
                    "calories": калории_на_порцию,
                    "protein": белки_в_граммах,
                    "carbs": углеводы_в_граммах,
                    "fat": жиры_в_граммах
                }
            }
            """
        else:
            return """
            Create a recipe based on the provided information.

            Return ONLY a JSON object:
            {
                "name": "recipe name",
                "description": "dish description",
                "prep_time": "preparation time",
                "cook_time": "cooking time",
                "servings": "number of servings",
                "ingredients": ["ingredient list"],
                "instructions": ["step-by-step instructions"],
                "nutrition": {
                    "calories": calories_per_serving,
                    "protein": protein_grams,
                    "carbs": carbs_grams,
                    "fat": fat_grams
                }
            }
            """
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья всех провайдеров"""
        logger.info("🏥 Running health check for all providers...")
        
        health_results = {
            "overall_healthy": True,
            "providers": {},
            "total_providers": len(self.providers),
            "healthy_providers": 0,
            "unhealthy_providers": 0
        }
        
        # Проверяем каждый провайдер
        for provider_key, provider in self.providers.items():
            try:
                provider_health = await provider.health_check()
                health_results["providers"][provider_key] = provider_health
                
                if provider_health["healthy"]:
                    health_results["healthy_providers"] += 1
                else:
                    health_results["unhealthy_providers"] += 1
                    health_results["overall_healthy"] = False
                    
            except Exception as e:
                logger.error(f"❌ Health check failed for {provider_key}: {e}")
                health_results["providers"][provider_key] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_results["unhealthy_providers"] += 1
                health_results["overall_healthy"] = False
        
        logger.info(f"🏥 Health check completed: {health_results['healthy_providers']}/{health_results['total_providers']} providers healthy")
        
        return health_results
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о доступных провайдерах"""
        providers_info = {}
        
        for provider_key, provider in self.providers.items():
            providers_info[provider_key] = provider.get_provider_info()
        
        return providers_info
    
    def is_initialized(self) -> bool:
        """Проверка инициализации менеджера"""
        return self.initialized and len(self.providers) > 0