"""
Enhanced Prompt Builder for c0r.AI ML Service
Main prompt construction system with regional adaptation and motivation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from ...models.config.sota_config import TaskType, ModelTier
# Location models removed - using language-based region detection instead
from ..motivation.praise_system import MotivationSystem
from ..utils.plate_weight_estimator import PlateWeightEstimator


# Simple stubs for removed location models
class RegionalContext:
    """Simple stub for RegionalContext"""
    def __init__(self, region_code: str = "INTL"):
        self.region_code = region_code
        self.common_products = []
        self.cooking_methods = []
        self.measurement_units = "metric"


class LocationInfo:
    """Simple stub for LocationInfo"""
    def __init__(self, country_code: str = "INTL"):
        self.country_code = country_code


class PromptBuilder:
    """Конструктор промптов с поддержкой региональной адаптации"""
    
    def __init__(self):
        self.motivation_system = MotivationSystem()
        self.weight_estimator = PlateWeightEstimator()
        
        # Кэш промптов для оптимизации
        self.prompt_cache: Dict[str, str] = {}
        
        logger.info("🎯 PromptBuilder initialized")
    
    def build_food_analysis_prompt(self, 
                                 user_language: str,
                                 regional_context: RegionalContext,
                                 user_profile: Dict[str, Any],
                                 motivation_level: str = "standard") -> str:
        """
        Создает улучшенный промпт для анализа еды
        
        Args:
            user_language: Язык пользователя
            regional_context: Региональный контекст кухни
            user_profile: Профиль пользователя
            motivation_level: Уровень мотивации
            
        Returns:
            Готовый промпт для анализа еды
        """
        logger.debug(f"🍽️ Building food analysis prompt for {regional_context.region_code} in {user_language}")
        
        # Генерируем мотивационное приветствие
        motivation_greeting = self.motivation_system.get_motivation_greeting(
            user_language, motivation_level, user_profile.get('analysis_count', 0)
        )
        
        # Получаем региональные особенности
        regional_products = ", ".join(regional_context.common_products[:10])  # Топ-10 продуктов
        seasonal_products = self._get_current_seasonal_products(regional_context)
        cooking_methods = ", ".join(regional_context.cooking_methods[:5])  # Топ-5 методов
        
        # Создаем контекст для оценки веса
        portion_context = self.weight_estimator.get_portion_context(regional_context.region_code)
        
        # Генерируем поощрительное сообщение
        encouragement = self.motivation_system.get_encouragement_message(
            user_language, "healthy_choice"
        )
        
        if user_language == "ru":
            return self._build_russian_food_analysis_prompt(
                motivation_greeting=motivation_greeting,
                regional_products=regional_products,
                seasonal_products=seasonal_products,
                cooking_methods=cooking_methods,
                portion_context=portion_context,
                measurement_units=regional_context.measurement_units,
                encouragement=encouragement,
                regional_context=regional_context
            )
        else:
            return self._build_english_food_analysis_prompt(
                motivation_greeting=motivation_greeting,
                regional_products=regional_products,
                seasonal_products=seasonal_products,
                cooking_methods=cooking_methods,
                portion_context=portion_context,
                measurement_units=regional_context.measurement_units,
                encouragement=encouragement,
                regional_context=regional_context
            )
    
    def build_recipe_generation_prompt(self,
                                     user_language: str,
                                     regional_context: RegionalContext,
                                     user_profile: Dict[str, Any],
                                     recipe_count: int = 3) -> str:
        """
        Создает промпт для генерации множественных рецептов
        
        Args:
            user_language: Язык пользователя
            regional_context: Региональный контекст
            user_profile: Профиль пользователя
            recipe_count: Количество рецептов для генерации
            
        Returns:
            Готовый промпт для генерации рецептов
        """
        logger.debug(f"👨‍🍳 Building recipe generation prompt for {recipe_count} recipes")
        
        # Мотивационное приветствие
        motivation_greeting = self.motivation_system.get_cooking_motivation(
            user_language, user_profile.get('cooking_level', 'beginner')
        )
        
        # Контекст пользователя
        user_context_str = self._build_user_context_string(user_profile, user_language)
        
        # Региональные особенности
        regional_cuisine = ", ".join(regional_context.cuisine_types)
        available_products = ", ".join(regional_context.common_products[:15])
        
        if user_language == "ru":
            return self._build_russian_recipe_prompt(
                motivation_greeting=motivation_greeting,
                regional_cuisine=regional_cuisine,
                available_products=available_products,
                user_context=user_context_str,
                regional_context=regional_context,
                recipe_count=recipe_count
            )
        else:
            return self._build_english_recipe_prompt(
                motivation_greeting=motivation_greeting,
                regional_cuisine=regional_cuisine,
                available_products=available_products,
                user_context=user_context_str,
                regional_context=regional_context,
                recipe_count=recipe_count
            )
    
    def _build_russian_food_analysis_prompt(self, **kwargs) -> str:
        """Создание русского промпта для анализа еды"""
        return f"""
{kwargs['motivation_greeting']}

Ты - эксперт по питанию, специализирующийся на {kwargs['regional_context'].cuisine_types[0]} кухне. Проанализируй это изображение еды с максимальной точностью.

РЕГИОНАЛЬНЫЙ КОНТЕКСТ ({kwargs['regional_context'].region_code}):
- Типичные продукты региона: {kwargs['regional_products']}
- Сезонные продукты: {kwargs['seasonal_products']}
- Традиционные методы готовки: {kwargs['cooking_methods']}
- Единицы измерения: {kwargs['measurement_units']}
- Особенности кухни: {kwargs['regional_context'].food_culture_notes}

ЗАДАЧА АНАЛИЗА:
1. 🔍 Определи ВСЕ продукты на изображении, уделяя особое внимание региональным продуктам
2. ⚖️ Оцени точный вес каждого продукта в граммах {kwargs['portion_context']}
3. 🧮 Рассчитай детальную пищевую ценность для каждого продукта отдельно
4. 💚 Объясни пользу каждого продукта для здоровья в контексте региональной кухни
5. 🎯 Добавь мотивационное сообщение о важности отслеживания питания

ВАЖНЫЕ ТРЕБОВАНИЯ:
- Используй точные русские названия продуктов
- Учитывай региональные особенности приготовления
- Оценивай вес с учетом стандартных порций в {kwargs['regional_context'].region_code}
- Объясняй пользу продуктов в контексте местных традиций питания

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "motivation_message": "{{персональное поздравление за ведение учета питания}}",
    "regional_analysis": {{
        "detected_cuisine_type": "{{определенный тип кухни}}",
        "regional_match_confidence": {{уверенность соответствия региональной кухне 0-1}},
        "cultural_notes": "{{культурные особенности блюда}}"
    }},
    "food_items": [
        {{
            "name": "{{точное русское название продукта}}",
            "regional_name": "{{местное/традиционное название если отличается}}",
            "weight_grams": {{точный вес в граммах}},
            "weight_confidence": {{уверенность в оценке веса 0-1}},
            "calories": {{калории}},
            "proteins": {{белки в граммах}},
            "fats": {{жиры в граммах}},
            "carbohydrates": {{углеводы в граммах}},
            "fiber": {{клетчатка в граммах}},
            "health_benefits": "{{подробное объяснение пользы этого продукта}}",
            "regional_significance": "{{значение в {kwargs['regional_context'].region_code} кухне}}",
            "seasonal_availability": "{{сезонная доступность в регионе}}",
            "cooking_method_detected": "{{определенный метод приготовления}}"
        }}
    ],
    "total_nutrition": {{
        "calories": {{общие калории}},
        "proteins": {{общие белки}},
        "fats": {{общие жиры}},
        "carbohydrates": {{общие углеводы}},
        "fiber": {{общая клетчатка}},
        "estimated_plate_weight": {{оценка веса всей тарелки в граммах}}
    }},
    "nutritional_analysis": {{
        "overall_healthiness": "{{оценка полезности блюда по 10-балльной шкале}}",
        "dietary_recommendations": "{{персональные рекомендации по питанию}}",
        "regional_nutrition_notes": "{{особенности питательности в контексте {kwargs['regional_context'].region_code} кухни}}",
        "balance_assessment": "{{оценка сбалансированности БЖУ}}"
    }},
    "encouragement": "{kwargs['encouragement']}"
}}

ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ:
- Будь максимально точен в определении веса - это критически важно для подсчета калорий
- Учитывай, что в {kwargs['regional_context'].region_code} кухне есть свои особенности порций
- Объясняй пользу продуктов простым и понятным языком
- Мотивируй пользователя продолжать отслеживать питание
- Все числовые значения должны быть числами, не строками
"""
    
    def _build_english_food_analysis_prompt(self, **kwargs) -> str:
        """Создание английского промпта для анализа еды"""
        return f"""
{kwargs['motivation_greeting']}

You are a nutrition expert specializing in {kwargs['regional_context'].cuisine_types[0]} cuisine. Analyze this food image with maximum accuracy.

REGIONAL CONTEXT ({kwargs['regional_context'].region_code}):
- Typical regional products: {kwargs['regional_products']}
- Seasonal products: {kwargs['seasonal_products']}
- Traditional cooking methods: {kwargs['cooking_methods']}
- Measurement units: {kwargs['measurement_units']}
- Cuisine characteristics: {kwargs['regional_context'].food_culture_notes}

ANALYSIS TASK:
1. 🔍 Identify ALL food items in the image, paying special attention to regional products
2. ⚖️ Estimate precise weight of each item in grams {kwargs['portion_context']}
3. 🧮 Calculate detailed nutritional value for each product separately
4. 💚 Explain health benefits of each product in regional cuisine context
5. 🎯 Add motivational message about the importance of nutrition tracking

IMPORTANT REQUIREMENTS:
- Use accurate food names specific to the region
- Consider regional cooking characteristics
- Estimate weights based on standard portions in {kwargs['regional_context'].region_code}
- Explain product benefits in the context of local food traditions

RESPONSE FORMAT (strict JSON):
{{
    "motivation_message": "{{personal congratulations for tracking nutrition}}",
    "regional_analysis": {{
        "detected_cuisine_type": "{{identified cuisine type}}",
        "regional_match_confidence": {{confidence in regional cuisine match 0-1}},
        "cultural_notes": "{{cultural characteristics of the dish}}"
    }},
    "food_items": [
        {{
            "name": "{{precise food name}}",
            "regional_name": "{{local/traditional name if different}}",
            "weight_grams": {{precise weight in grams}},
            "weight_confidence": {{confidence in weight estimation 0-1}},
            "calories": {{calories}},
            "proteins": {{proteins in grams}},
            "fats": {{fats in grams}},
            "carbohydrates": {{carbohydrates in grams}},
            "fiber": {{fiber in grams}},
            "health_benefits": "{{detailed explanation of this product's benefits}}",
            "regional_significance": "{{significance in {kwargs['regional_context'].region_code} cuisine}}",
            "seasonal_availability": "{{seasonal availability in the region}}",
            "cooking_method_detected": "{{identified cooking method}}"
        }}
    ],
    "total_nutrition": {{
        "calories": {{total calories}},
        "proteins": {{total proteins}},
        "fats": {{total fats}},
        "carbohydrates": {{total carbohydrates}},
        "fiber": {{total fiber}},
        "estimated_plate_weight": {{estimated total plate weight in grams}}
    }},
    "nutritional_analysis": {{
        "overall_healthiness": "{{healthiness rating on 10-point scale}}",
        "dietary_recommendations": "{{personalized nutrition recommendations}}",
        "regional_nutrition_notes": "{{nutritional characteristics in {kwargs['regional_context'].region_code} cuisine context}}",
        "balance_assessment": "{{assessment of macronutrient balance}}"
    }},
    "encouragement": "{kwargs['encouragement']}"
}}

ADDITIONAL INSTRUCTIONS:
- Be maximally accurate in weight estimation - this is critical for calorie counting
- Consider that {kwargs['regional_context'].region_code} cuisine has its own portion characteristics
- Explain product benefits in simple and understandable language
- Motivate the user to continue tracking nutrition
- All numeric values must be numbers, not strings
"""
    
    def _build_russian_recipe_prompt(self, **kwargs) -> str:
        """Создание русского промпта для генерации рецептов"""
        return f"""
{kwargs['motivation_greeting']}

Ты - шеф-повар и эксперт по {kwargs['regional_cuisine']} кухне. Проанализируй изображение и создай ТРИ разных рецепта, ранжированных по соответствию пользователю.

КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:
{kwargs['user_context']}

РЕГИОНАЛЬНЫЙ КОНТЕКСТ ({kwargs['regional_context'].region_code}):
- Типы кухни: {kwargs['regional_cuisine']}
- Доступные продукты: {kwargs['available_products']}
- Методы готовки: {", ".join(kwargs['regional_context'].cooking_methods)}
- Единицы измерения: {kwargs['regional_context'].measurement_units}
- Культурные особенности: {kwargs['regional_context'].food_culture_notes}

ТРЕБОВАНИЯ К РЕЦЕПТАМ:
1. 🎯 ПЕРСОНАЛЬНЫЙ РЕЦЕПТ - максимально подходящий профилю пользователя
2. 🏛️ ТРАДИЦИОННЫЙ РЕЦЕПТ - классический {kwargs['regional_cuisine']} рецепт
3. 🌟 КРЕАТИВНЫЙ РЕЦЕПТ - современная интерпретация или фьюжн

Каждый рецепт должен:
- Использовать ингредиенты с фото
- Быть адаптированным под {kwargs['regional_context'].region_code}
- Учитывать доступность продуктов в регионе
- Соответствовать профилю пользователя

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "motivation_message": "{{поздравление за желание готовить здоровую еду}}",
    "ingredient_analysis": {{
        "recognized_ingredients": [{{список распознанных ингредиентов}}],
        "regional_availability": {{{{ингредиент: "легко найти/сезонный/редкий"}}}},
        "suggested_additions": [{{предложения дополнительных региональных ингредиентов}}]
    }},
    "recipes": [
        {{
            "rank": 1,
            "type": "personal",
            "suitability_score": {{0-100}},
            "name": "{{название рецепта}}",
            "description": "{{почему этот рецепт идеален для пользователя}}",
            "prep_time": "{{время подготовки}}",
            "cook_time": "{{время готовки}}",
            "difficulty": "{{легко/средне/сложно}}",
            "servings": {{количество порций}},
            "ingredients": [
                {{
                    "item": "{{ингредиент}}",
                    "amount": "{{количество в {kwargs['regional_context'].measurement_units}}}",
                    "regional_availability": "{{доступность в {kwargs['regional_context'].region_code}}}",
                    "substitutes": [{{список возможных замен}}]
                }}
            ],
            "instructions": [
                "{{пошаговая инструкция с учетом региональных особенностей}}"
            ],
            "nutrition_per_serving": {{
                "calories": {{калории}},
                "protein": {{белки}},
                "carbs": {{углеводы}},
                "fat": {{жиры}}
            }},
            "health_benefits": "{{польза блюда для здоровья}}",
            "regional_notes": "{{особенности приготовления в {kwargs['regional_context'].region_code}}}",
            "personalization_notes": "{{почему подходит именно этому пользователю}}",
            "cultural_significance": "{{культурное значение блюда в регионе}}"
        }},
        {{
            "rank": 2,
            "type": "traditional",
            "suitability_score": {{0-100}},
            "name": "{{название традиционного рецепта}}",
            "description": "{{описание традиционного блюда}}",
            "cultural_background": "{{историческая справка о блюде}}",
            "traditional_occasions": "{{когда традиционно готовят это блюдо}}"
            // ... остальные поля аналогично первому рецепту
        }},
        {{
            "rank": 3,
            "type": "creative",
            "suitability_score": {{0-100}},
            "name": "{{название креативного рецепта}}",
            "description": "{{описание современной интерпретации}}",
            "innovation_notes": "{{что делает этот рецепт особенным}}",
            "fusion_elements": "{{элементы фьюжн кухни если есть}}"
            // ... остальные поля аналогично первому рецепту
        }}
    ],
    "cooking_tips": [
        "{{советы по готовке для {kwargs['regional_context'].region_code}}}"
    ],
    "regional_wisdom": "{{традиционные секреты {kwargs['regional_cuisine']} кухни}}",
    "encouragement": "{{мотивация к здоровому питанию и готовке}}"
}}

ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ:
- Ранжируй рецепты по убыванию соответствия пользователю
- Учитывай сезонность и доступность ингредиентов
- Включай культурный контекст и традиции
- Предлагай здоровые альтернативы где возможно
- Все числовые значения должны быть числами
"""
    
    def _build_english_recipe_prompt(self, **kwargs) -> str:
        """Создание английского промпта для генерации рецептов"""
        return f"""
{kwargs['motivation_greeting']}

You are a chef and expert in {kwargs['regional_cuisine']} cuisine. Analyze the image and create THREE different recipes, ranked by user suitability.

USER CONTEXT:
{kwargs['user_context']}

REGIONAL CONTEXT ({kwargs['regional_context'].region_code}):
- Cuisine types: {kwargs['regional_cuisine']}
- Available products: {kwargs['available_products']}
- Cooking methods: {", ".join(kwargs['regional_context'].cooking_methods)}
- Measurement units: {kwargs['regional_context'].measurement_units}
- Cultural characteristics: {kwargs['regional_context'].food_culture_notes}

RECIPE REQUIREMENTS:
1. 🎯 PERSONAL RECIPE - maximally suited to user profile
2. 🏛️ TRADITIONAL RECIPE - classic {kwargs['regional_cuisine']} recipe
3. 🌟 CREATIVE RECIPE - modern interpretation or fusion

Each recipe should:
- Use ingredients from the photo
- Be adapted for {kwargs['regional_context'].region_code}
- Consider ingredient availability in the region
- Match the user profile

RESPONSE FORMAT (strict JSON):
{{
    "motivation_message": "{{congratulations for wanting to cook healthy food}}",
    "ingredient_analysis": {{
        "recognized_ingredients": [{{list of recognized ingredients}}],
        "regional_availability": {{{{ingredient: "easily found/seasonal/rare"}}}},
        "suggested_additions": [{{suggestions for additional regional ingredients}}]
    }},
    "recipes": [
        {{
            "rank": 1,
            "type": "personal",
            "suitability_score": {{0-100}},
            "name": "{{recipe name}}",
            "description": "{{why this recipe is perfect for the user}}",
            "prep_time": "{{preparation time}}",
            "cook_time": "{{cooking time}}",
            "difficulty": "{{easy/medium/hard}}",
            "servings": {{number of servings}},
            "ingredients": [
                {{
                    "item": "{{ingredient}}",
                    "amount": "{{amount in {kwargs['regional_context'].measurement_units}}}",
                    "regional_availability": "{{availability in {kwargs['regional_context'].region_code}}}",
                    "substitutes": [{{list of possible substitutions}}]
                }}
            ],
            "instructions": [
                "{{step-by-step instruction considering regional characteristics}}"
            ],
            "nutrition_per_serving": {{
                "calories": {{calories}},
                "protein": {{protein}},
                "carbs": {{carbohydrates}},
                "fat": {{fat}}
            }},
            "health_benefits": "{{health benefits of the dish}}",
            "regional_notes": "{{cooking characteristics in {kwargs['regional_context'].region_code}}}",
            "personalization_notes": "{{why it suits this particular user}}",
            "cultural_significance": "{{cultural significance of the dish in the region}}"
        }},
        {{
            "rank": 2,
            "type": "traditional",
            "suitability_score": {{0-100}},
            "name": "{{traditional recipe name}}",
            "description": "{{traditional dish description}}",
            "cultural_background": "{{historical background of the dish}}",
            "traditional_occasions": "{{when this dish is traditionally prepared}}"
            // ... other fields similar to first recipe
        }},
        {{
            "rank": 3,
            "type": "creative",
            "suitability_score": {{0-100}},
            "name": "{{creative recipe name}}",
            "description": "{{modern interpretation description}}",
            "innovation_notes": "{{what makes this recipe special}}",
            "fusion_elements": "{{fusion cuisine elements if any}}"
            // ... other fields similar to first recipe
        }}
    ],
    "cooking_tips": [
        "{{cooking tips for {kwargs['regional_context'].region_code}}}"
    ],
    "regional_wisdom": "{{traditional secrets of {kwargs['regional_cuisine']} cuisine}}",
    "encouragement": "{{motivation for healthy eating and cooking}}"
}}

ADDITIONAL INSTRUCTIONS:
- Rank recipes by decreasing user suitability
- Consider seasonality and ingredient availability
- Include cultural context and traditions
- Suggest healthy alternatives where possible
- All numeric values must be numbers
"""
    
    def _get_current_seasonal_products(self, regional_context: RegionalContext) -> str:
        """Получение текущих сезонных продуктов"""
        current_month = datetime.now().month
        
        if current_month in [3, 4, 5]:
            season = "spring"
        elif current_month in [6, 7, 8]:
            season = "summer"
        elif current_month in [9, 10, 11]:
            season = "autumn"
        else:
            season = "winter"
        
        seasonal_products = regional_context.seasonal_products.get(season, [])
        return ", ".join(seasonal_products[:5])  # Топ-5 сезонных продуктов
    
    def _build_user_context_string(self, user_profile: Dict[str, Any], language: str) -> str:
        """Построение строки контекста пользователя"""
        context_parts = []
        
        if user_profile.get('dietary_preferences'):
            dietary_prefs = [pref for pref in user_profile['dietary_preferences'] if pref != 'none']
            if dietary_prefs:
                if language == "ru":
                    context_parts.append(f"Диетические предпочтения: {', '.join(dietary_prefs)}")
                else:
                    context_parts.append(f"Dietary preferences: {', '.join(dietary_prefs)}")
        
        if user_profile.get('allergies'):
            allergies = [allergy for allergy in user_profile['allergies'] if allergy != 'none']
            if allergies:
                if language == "ru":
                    context_parts.append(f"Аллергии (избегать): {', '.join(allergies)}")
                else:
                    context_parts.append(f"Allergies (avoid): {', '.join(allergies)}")
        
        if user_profile.get('goal'):
            goal_map_ru = {
                'lose_weight': 'похудение',
                'maintain_weight': 'поддержание веса',
                'gain_weight': 'набор веса'
            }
            goal_map_en = {
                'lose_weight': 'weight loss',
                'maintain_weight': 'weight maintenance',
                'gain_weight': 'weight gain'
            }
            
            goal_map = goal_map_ru if language == "ru" else goal_map_en
            goal = goal_map.get(user_profile['goal'], user_profile['goal'])
            
            if language == "ru":
                context_parts.append(f"Цель: {goal}")
            else:
                context_parts.append(f"Goal: {goal}")
        
        if user_profile.get('daily_calories_target'):
            if language == "ru":
                context_parts.append(f"Целевая калорийность: {user_profile['daily_calories_target']} ккал/день")
            else:
                context_parts.append(f"Daily calorie target: {user_profile['daily_calories_target']} cal/day")
        
        if user_profile.get('cooking_level'):
            if language == "ru":
                level_map = {'beginner': 'новичок', 'intermediate': 'средний', 'advanced': 'продвинутый'}
                level = level_map.get(user_profile['cooking_level'], user_profile['cooking_level'])
                context_parts.append(f"Уровень готовки: {level}")
            else:
                context_parts.append(f"Cooking level: {user_profile['cooking_level']}")
        
        if language == "ru":
            return "\n".join(context_parts) if context_parts else "Нет специальных требований"
        else:
            return "\n".join(context_parts) if context_parts else "No specific requirements"
    
    def clear_cache(self):
        """Очистка кэша промптов"""
        self.prompt_cache.clear()
        logger.info("🗑️ Prompt cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        return {
            "cache_size": len(self.prompt_cache),
            "cache_keys": list(self.prompt_cache.keys())
        }