"""
Triple Recipe Generation System for c0r.AI ML Service
Generates three ranked recipes based on user preferences and regional context
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from loguru import logger

# Location models removed - using language-based region detection instead

# Simple stub for RegionalContext
class RegionalContext:
    """Simple stub for RegionalContext"""
    def __init__(self, region_code: str = "INTL"):
        self.region_code = region_code
        self.common_products = []
        self.cooking_methods = []
        self.measurement_units = "metric"


class TripleRecipeGenerator:
    """Система генерации трех ранжированных рецептов"""
    
    def __init__(self):
        self.recipe_templates = self._load_recipe_templates()
        self.ranking_weights = self._load_ranking_weights()
        self.difficulty_levels = self._load_difficulty_levels()
        
        logger.info("👨‍🍳 TripleRecipeGenerator initialized")
    
    def generate_recipe_ranking_context(self, 
                                      user_profile: Dict[str, Any],
                                      regional_context: RegionalContext,
                                      recognized_ingredients: List[str]) -> Dict[str, Any]:
        """
        Генерация контекста для ранжирования рецептов
        
        Args:
            user_profile: Профиль пользователя
            regional_context: Региональный контекст
            recognized_ingredients: Распознанные ингредиенты
            
        Returns:
            Контекст для ранжирования рецептов
        """
        logger.debug("🎯 Generating recipe ranking context")
        
        # Анализ пользовательских предпочтений
        user_preferences = self._analyze_user_preferences(user_profile)
        
        # Региональная адаптация
        regional_adaptation = self._get_regional_adaptation(regional_context)
        
        # Анализ доступности ингредиентов
        ingredient_availability = self._analyze_ingredient_availability(
            recognized_ingredients, regional_context
        )
        
        # Определение сложности рецептов
        complexity_preferences = self._determine_complexity_preferences(user_profile)
        
        return {
            "user_preferences": user_preferences,
            "regional_adaptation": regional_adaptation,
            "ingredient_availability": ingredient_availability,
            "complexity_preferences": complexity_preferences,
            "ranking_criteria": self._get_ranking_criteria(user_profile, regional_context)
        }
    
    def calculate_recipe_suitability_score(self, 
                                         recipe_type: str,
                                         user_profile: Dict[str, Any],
                                         regional_context: RegionalContext,
                                         ingredient_match_score: float) -> int:
        """
        Расчет оценки соответствия рецепта пользователю
        
        Args:
            recipe_type: Тип рецепта (personal, traditional, creative)
            user_profile: Профиль пользователя
            regional_context: Региональный контекст
            ingredient_match_score: Оценка соответствия ингредиентов
            
        Returns:
            Оценка от 0 до 100
        """
        logger.debug(f"📊 Calculating suitability score for {recipe_type}")
        
        base_score = 50  # Базовая оценка
        
        # Весовые коэффициенты для разных типов рецептов
        type_weights = {
            "personal": {
                "dietary_match": 0.3,
                "goal_alignment": 0.25,
                "difficulty_match": 0.2,
                "ingredient_availability": 0.15,
                "cultural_preference": 0.1
            },
            "traditional": {
                "cultural_authenticity": 0.35,
                "ingredient_availability": 0.25,
                "dietary_match": 0.2,
                "difficulty_match": 0.1,
                "seasonal_relevance": 0.1
            },
            "creative": {
                "innovation_appeal": 0.3,
                "ingredient_creativity": 0.25,
                "dietary_match": 0.2,
                "difficulty_challenge": 0.15,
                "fusion_interest": 0.1
            }
        }
        
        weights = type_weights.get(recipe_type, type_weights["personal"])
        
        # Расчет компонентов оценки
        dietary_score = self._calculate_dietary_match_score(user_profile)
        goal_score = self._calculate_goal_alignment_score(user_profile, recipe_type)
        difficulty_score = self._calculate_difficulty_match_score(user_profile, recipe_type)
        cultural_score = self._calculate_cultural_preference_score(user_profile, regional_context)
        
        # Специфические оценки для типов рецептов
        if recipe_type == "traditional":
            authenticity_score = self._calculate_authenticity_score(regional_context)
            seasonal_score = self._calculate_seasonal_relevance_score(regional_context)
            
            total_score = (
                base_score +
                (dietary_score * weights["dietary_match"]) +
                (authenticity_score * weights["cultural_authenticity"]) +
                (ingredient_match_score * weights["ingredient_availability"]) +
                (difficulty_score * weights["difficulty_match"]) +
                (seasonal_score * weights["seasonal_relevance"])
            )
        
        elif recipe_type == "creative":
            innovation_score = self._calculate_innovation_appeal_score(user_profile)
            creativity_score = self._calculate_ingredient_creativity_score(user_profile)
            fusion_score = self._calculate_fusion_interest_score(user_profile, regional_context)
            
            total_score = (
                base_score +
                (innovation_score * weights["innovation_appeal"]) +
                (creativity_score * weights["ingredient_creativity"]) +
                (dietary_score * weights["dietary_match"]) +
                (difficulty_score * weights["difficulty_challenge"]) +
                (fusion_score * weights["fusion_interest"])
            )
        
        else:  # personal
            total_score = (
                base_score +
                (dietary_score * weights["dietary_match"]) +
                (goal_score * weights["goal_alignment"]) +
                (difficulty_score * weights["difficulty_match"]) +
                (ingredient_match_score * weights["ingredient_availability"]) +
                (cultural_score * weights["cultural_preference"])
            )
        
        # Нормализация оценки в диапазон 0-100
        final_score = max(0, min(100, int(total_score)))
        
        logger.debug(f"📈 Final suitability score for {recipe_type}: {final_score}")
        
        return final_score
    
    def get_recipe_type_descriptions(self, language: str = "ru") -> Dict[str, Dict[str, str]]:
        """
        Получение описаний типов рецептов
        
        Args:
            language: Язык описаний
            
        Returns:
            Словарь с описаниями типов рецептов
        """
        if language == "ru":
            return {
                "personal": {
                    "title": "Персональный рецепт",
                    "description": "Максимально адаптированный под ваши предпочтения и цели",
                    "focus": "Учитывает диетические ограничения, цели и уровень готовки"
                },
                "traditional": {
                    "title": "Традиционный рецепт",
                    "description": "Классический рецепт региональной кухни",
                    "focus": "Аутентичность, культурные традиции, сезонность"
                },
                "creative": {
                    "title": "Креативный рецепт",
                    "description": "Современная интерпретация или фьюжн",
                    "focus": "Инновации, необычные сочетания, творческий подход"
                }
            }
        else:
            return {
                "personal": {
                    "title": "Personal Recipe",
                    "description": "Maximally adapted to your preferences and goals",
                    "focus": "Considers dietary restrictions, goals and cooking level"
                },
                "traditional": {
                    "title": "Traditional Recipe",
                    "description": "Classic regional cuisine recipe",
                    "focus": "Authenticity, cultural traditions, seasonality"
                },
                "creative": {
                    "title": "Creative Recipe",
                    "description": "Modern interpretation or fusion",
                    "focus": "Innovation, unusual combinations, creative approach"
                }
            }
    
    def get_cooking_tips_for_region(self, 
                                  regional_context: RegionalContext,
                                  language: str = "ru") -> List[str]:
        """
        Получение советов по готовке для региона
        
        Args:
            regional_context: Региональный контекст
            language: Язык советов
            
        Returns:
            Список советов по готовке
        """
        logger.debug(f"💡 Getting cooking tips for {regional_context.region_code}")
        
        region_tips = {
            "RU": {
                "ru": [
                    "Используйте чугунную посуду для лучшего прогрева",
                    "Добавляйте зелень в конце приготовления для сохранения витаминов",
                    "Солите мясо за 30 минут до готовки для лучшего вкуса",
                    "Используйте сметану для смягчения кислых блюд"
                ],
                "en": [
                    "Use cast iron cookware for better heating",
                    "Add herbs at the end of cooking to preserve vitamins",
                    "Salt meat 30 minutes before cooking for better flavor",
                    "Use sour cream to soften acidic dishes"
                ]
            },
            "US": {
                "ru": [
                    "Используйте мерные чашки для точности",
                    "Предварительно разогревайте духовку",
                    "Маринуйте мясо для сочности",
                    "Используйте термометр для мяса"
                ],
                "en": [
                    "Use measuring cups for accuracy",
                    "Preheat the oven beforehand",
                    "Marinate meat for juiciness",
                    "Use a meat thermometer"
                ]
            },
            "IT": {
                "ru": [
                    "Используйте только качественные ингредиенты",
                    "Не переваривайте пасту - al dente лучше всего",
                    "Добавляйте оливковое масло в конце",
                    "Используйте свежие травы"
                ],
                "en": [
                    "Use only quality ingredients",
                    "Don't overcook pasta - al dente is best",
                    "Add olive oil at the end",
                    "Use fresh herbs"
                ]
            }
        }
        
        tips = region_tips.get(regional_context.region_code, {}).get(language, [])
        
        if not tips:
            # Общие советы
            if language == "ru":
                tips = [
                    "Читайте рецепт полностью перед началом",
                    "Подготовьте все ингредиенты заранее",
                    "Не открывайте духовку без необходимости",
                    "Пробуйте блюдо в процессе готовки"
                ]
            else:
                tips = [
                    "Read the recipe completely before starting",
                    "Prepare all ingredients in advance",
                    "Don't open the oven unnecessarily",
                    "Taste the dish while cooking"
                ]
        
        return tips
    
    def _analyze_user_preferences(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ пользовательских предпочтений"""
        
        preferences = {
            "dietary_restrictions": user_profile.get("dietary_preferences", []),
            "allergies": user_profile.get("allergies", []),
            "cooking_level": user_profile.get("cooking_level", "beginner"),
            "goal": user_profile.get("goal", "maintain_weight"),
            "preferred_cuisines": user_profile.get("preferred_cuisines", []),
            "time_constraints": user_profile.get("available_cooking_time", "medium")
        }
        
        return preferences
    
    def _get_regional_adaptation(self, regional_context: RegionalContext) -> Dict[str, Any]:
        """Получение региональной адаптации"""
        
        return {
            "cuisine_types": regional_context.cuisine_types,
            "common_products": regional_context.common_products[:10],
            "cooking_methods": regional_context.cooking_methods[:5],
            "measurement_units": regional_context.measurement_units,
            "cultural_notes": regional_context.food_culture_notes
        }
    
    def _analyze_ingredient_availability(self, 
                                       ingredients: List[str],
                                       regional_context: RegionalContext) -> Dict[str, str]:
        """Анализ доступности ингредиентов"""
        
        availability = {}
        common_products = [p.lower() for p in regional_context.common_products]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            if any(product in ingredient_lower for product in common_products):
                availability[ingredient] = "easily_available"
            elif self._is_seasonal_ingredient(ingredient, regional_context):
                availability[ingredient] = "seasonal"
            else:
                availability[ingredient] = "specialty_store"
        
        return availability
    
    def _determine_complexity_preferences(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Определение предпочтений по сложности"""
        
        cooking_level = user_profile.get("cooking_level", "beginner")
        available_time = user_profile.get("available_cooking_time", "medium")
        
        complexity_map = {
            "beginner": {
                "short": "very_easy",
                "medium": "easy",
                "long": "easy"
            },
            "intermediate": {
                "short": "easy",
                "medium": "medium",
                "long": "medium"
            },
            "advanced": {
                "short": "medium",
                "medium": "medium",
                "long": "hard"
            }
        }
        
        preferred_complexity = complexity_map.get(cooking_level, {}).get(available_time, "easy")
        
        return {
            "preferred_complexity": preferred_complexity,
            "max_prep_time": self._get_max_prep_time(available_time),
            "max_cook_time": self._get_max_cook_time(available_time)
        }
    
    def _get_ranking_criteria(self, 
                            user_profile: Dict[str, Any],
                            regional_context: RegionalContext) -> Dict[str, float]:
        """Получение критериев ранжирования"""
        
        # Базовые критерии
        criteria = {
            "dietary_compatibility": 0.25,
            "ingredient_availability": 0.20,
            "difficulty_match": 0.15,
            "cultural_relevance": 0.15,
            "nutritional_value": 0.15,
            "innovation_factor": 0.10
        }
        
        # Корректировка на основе профиля пользователя
        if user_profile.get("goal") == "lose_weight":
            criteria["nutritional_value"] += 0.1
            criteria["innovation_factor"] -= 0.05
        
        if user_profile.get("cooking_level") == "advanced":
            criteria["innovation_factor"] += 0.1
            criteria["difficulty_match"] -= 0.05
        
        return criteria
    
    def _calculate_dietary_match_score(self, user_profile: Dict[str, Any]) -> float:
        """Расчет соответствия диетическим требованиям"""
        
        dietary_prefs = user_profile.get("dietary_preferences", [])
        allergies = user_profile.get("allergies", [])
        
        # Базовая оценка
        score = 20.0
        
        # Бонус за соответствие диетическим предпочтениям
        if "vegetarian" in dietary_prefs:
            score += 10
        if "healthy" in dietary_prefs:
            score += 8
        if "low_carb" in dietary_prefs:
            score += 6
        
        # Штраф за наличие аллергенов (будет учтено в конкретном рецепте)
        if allergies and len(allergies) > 0:
            score -= 2 * len([a for a in allergies if a != "none"])
        
        return max(0, score)
    
    def _calculate_goal_alignment_score(self, user_profile: Dict[str, Any], recipe_type: str) -> float:
        """Расчет соответствия целям пользователя"""
        
        goal = user_profile.get("goal", "maintain_weight")
        
        goal_scores = {
            "lose_weight": {
                "personal": 25,
                "traditional": 15,
                "creative": 20
            },
            "gain_weight": {
                "personal": 25,
                "traditional": 20,
                "creative": 15
            },
            "maintain_weight": {
                "personal": 20,
                "traditional": 20,
                "creative": 20
            }
        }
        
        return goal_scores.get(goal, {}).get(recipe_type, 15)
    
    def _calculate_difficulty_match_score(self, user_profile: Dict[str, Any], recipe_type: str) -> float:
        """Расчет соответствия уровню сложности"""
        
        cooking_level = user_profile.get("cooking_level", "beginner")
        
        level_scores = {
            "beginner": {
                "personal": 25,
                "traditional": 20,
                "creative": 10
            },
            "intermediate": {
                "personal": 20,
                "traditional": 25,
                "creative": 20
            },
            "advanced": {
                "personal": 15,
                "traditional": 20,
                "creative": 25
            }
        }
        
        return level_scores.get(cooking_level, {}).get(recipe_type, 15)
    
    def _calculate_cultural_preference_score(self, 
                                           user_profile: Dict[str, Any],
                                           regional_context: RegionalContext) -> float:
        """Расчет культурных предпочтений"""
        
        preferred_cuisines = user_profile.get("preferred_cuisines", [])
        regional_cuisines = regional_context.cuisine_types
        
        # Базовая оценка
        score = 10.0
        
        # Бонус за совпадение с предпочитаемыми кухнями
        for cuisine in preferred_cuisines:
            if any(cuisine.lower() in rc.lower() for rc in regional_cuisines):
                score += 8
        
        return score
    
    def _calculate_authenticity_score(self, regional_context: RegionalContext) -> float:
        """Расчет аутентичности для традиционных рецептов"""
        
        # Базовая оценка аутентичности
        base_score = 20.0
        
        # Бонус за богатство культурных традиций
        if len(regional_context.cuisine_types) > 2:
            base_score += 5
        
        if regional_context.food_culture_notes:
            base_score += 5
        
        return base_score
    
    def _calculate_seasonal_relevance_score(self, regional_context: RegionalContext) -> float:
        """Расчет сезонной релевантности"""
        
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
        
        # Оценка на основе количества сезонных продуктов
        return min(20.0, len(seasonal_products) * 2)
    
    def _calculate_innovation_appeal_score(self, user_profile: Dict[str, Any]) -> float:
        """Расчет привлекательности инноваций"""
        
        cooking_level = user_profile.get("cooking_level", "beginner")
        
        innovation_scores = {
            "beginner": 10,
            "intermediate": 20,
            "advanced": 30
        }
        
        return innovation_scores.get(cooking_level, 15)
    
    def _calculate_ingredient_creativity_score(self, user_profile: Dict[str, Any]) -> float:
        """Расчет креативности ингредиентов"""
        
        # Базовая оценка креативности
        base_score = 15.0
        
        # Бонус для продвинутых поваров
        if user_profile.get("cooking_level") == "advanced":
            base_score += 10
        
        return base_score
    
    def _calculate_fusion_interest_score(self, 
                                       user_profile: Dict[str, Any],
                                       regional_context: RegionalContext) -> float:
        """Расчет интереса к фьюжн кухне"""
        
        preferred_cuisines = user_profile.get("preferred_cuisines", [])
        
        # Базовая оценка
        score = 10.0
        
        # Бонус за разнообразие предпочтений
        if len(preferred_cuisines) > 2:
            score += 8
        
        # Бонус за международные предпочтения
        international_cuisines = ["asian", "mediterranean", "mexican", "indian"]
        if any(cuisine in preferred_cuisines for cuisine in international_cuisines):
            score += 5
        
        return score
    
    def _is_seasonal_ingredient(self, ingredient: str, regional_context: RegionalContext) -> bool:
        """Проверка сезонности ингредиента"""
        
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
        
        return any(ingredient.lower() in product.lower() for product in seasonal_products)
    
    def _get_max_prep_time(self, available_time: str) -> str:
        """Получение максимального времени подготовки"""
        
        time_map = {
            "short": "15 минут",
            "medium": "30 минут",
            "long": "60 минут"
        }
        
        return time_map.get(available_time, "30 минут")
    
    def _get_max_cook_time(self, available_time: str) -> str:
        """Получение максимального времени готовки"""
        
        time_map = {
            "short": "30 минут",
            "medium": "60 минут",
            "long": "120 минут"
        }
        
        return time_map.get(available_time, "60 минут")
    
    def _load_recipe_templates(self) -> Dict[str, Dict]:
        """Загрузка шаблонов рецептов"""
        return {
            "personal": {
                "focus": "user_preferences",
                "adaptability": "high",
                "complexity": "variable"
            },
            "traditional": {
                "focus": "authenticity",
                "adaptability": "low",
                "complexity": "medium"
            },
            "creative": {
                "focus": "innovation",
                "adaptability": "high",
                "complexity": "high"
            }
        }
    
    def _load_ranking_weights(self) -> Dict[str, float]:
        """Загрузка весов для ранжирования"""
        return {
            "dietary_match": 0.25,
            "ingredient_availability": 0.20,
            "difficulty_suitability": 0.15,
            "cultural_relevance": 0.15,
            "nutritional_value": 0.15,
            "creativity_factor": 0.10
        }
    
    def _load_difficulty_levels(self) -> Dict[str, Dict]:
        """Загрузка уровней сложности"""
        return {
            "very_easy": {
                "max_prep_time": 10,
                "max_cook_time": 20,
                "max_ingredients": 5,
                "techniques": ["basic"]
            },
            "easy": {
                "max_prep_time": 20,
                "max_cook_time": 40,
                "max_ingredients": 8,
                "techniques": ["basic", "simple"]
            },
            "medium": {
                "max_prep_time": 40,
                "max_cook_time": 80,
                "max_ingredients": 12,
                "techniques": ["basic", "intermediate"]
            },
            "hard": {
                "max_prep_time": 60,
                "max_cook_time": 120,
                "max_ingredients": 15,
                "techniques": ["advanced", "complex"]
            }
        }