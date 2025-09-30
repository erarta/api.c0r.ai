"""
Enhanced Food Plan Generator with all AI improvements.
Integrates Nutrition DNA, predictive analytics, contextual analysis, and adaptive recommendations.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any

from loguru import logger

from ..models.nutrition_profile import NutritionDNA, WeeklyInsight
from ..analyzers.nutrition_dna_generator import NutritionDNAGenerator
from ..engines.personalized_insights import PersonalizedInsightsEngine
from ..engines.contextual_analyzer import ContextualAnalyzer
from ..predictors.behavior_predictor import BehaviorPredictor
from ..recommenders.adaptive_meal_recommender import AdaptiveMealRecommender


class EnhancedFoodPlanGenerator:
    """
    Next-generation food plan generator that creates deeply personalized plans using:
    - Nutrition DNA analysis
    - Behavioral predictions
    - Contextual awareness
    - Adaptive meal recommendations
    - Real-time insights
    """

    def __init__(self):
        self.dna_generator = NutritionDNAGenerator
        self.insights_engine = PersonalizedInsightsEngine
        self.context_analyzer = ContextualAnalyzer
        self.behavior_predictor = BehaviorPredictor
        self.meal_recommender = AdaptiveMealRecommender

    async def generate_enhanced_plan(
        self,
        profile: Dict[str, Any],
        food_history: List[Dict[str, Any]],
        days: int,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive enhanced food plan using all AI capabilities.

        Args:
            profile: User profile data
            food_history: Historical food analysis data
            days: Number of days to generate plan for
            context: Additional context (weather, schedule, etc.)

        Returns:
            Enhanced plan with personalized insights and recommendations
        """

        logger.info(f"Generating enhanced food plan for {days} days with {len(food_history)} historical logs")

        try:
            # 1. Get nutrition preferences from onboarding (if available)
            nutrition_preferences = await self._get_nutrition_preferences(profile.get('user_id'))
            if nutrition_preferences:
                # Merge preferences into profile for enhanced personalization
                profile = await self._merge_nutrition_preferences(profile, nutrition_preferences)
                logger.info("Enhanced profile with nutrition preferences from onboarding")

            # 2. Generate or update Nutrition DNA
            nutrition_dna = await self._get_or_create_nutrition_dna(profile, food_history)

            # 3. Analyze contextual factors
            context_analysis = self.context_analyzer.analyze_context_impact(
                food_history, context.get('context_data', []) if context else []
            )

            # 4. Generate behavioral predictions for the plan period
            start_date = datetime.utcnow().date()
            weekly_predictions = self.behavior_predictor.predict_weekly_outcomes(
                nutrition_dna, start_date, context.get('weekly_context', {}) if context else {}
            )

            # 5. Generate daily meal plans with AI recommendations
            plan_json = {}
            daily_insights = {}

            for day_num in range(1, days + 1):
                target_date = start_date + timedelta(days=day_num - 1)
                day_key = f"day_{day_num}"

                # Generate AI-powered daily plan
                daily_plan = await self._generate_ai_daily_plan(
                    nutrition_dna, target_date, context_analysis,
                    weekly_predictions, context, profile
                )

                plan_json[day_key] = daily_plan

                # Generate daily insights
                daily_insights[day_key] = self.insights_engine.generate_daily_insights(
                    nutrition_dna, target_date, food_history[-7:] if food_history else []
                )

            # 6. Generate weekly insights and recommendations
            weekly_insights = self.insights_engine.generate_weekly_insights(
                nutrition_dna, start_date, food_history[-14:] if food_history else []
            )

            # 7. Create enhanced intro summary
            intro_summary = self._create_enhanced_intro_summary(
                nutrition_dna, context_analysis, weekly_insights, profile, days
            )

            # 8. Generate AI shopping list with smart suggestions
            shopping_list_json = self._generate_smart_shopping_list(plan_json, nutrition_dna)

            # 9. Add personalization metadata
            personalization_data = {
                'nutrition_dna_summary': self.dna_generator.get_dna_summary(nutrition_dna),
                'behavioral_predictions': self._summarize_predictions(weekly_predictions),
                'contextual_insights': context_analysis.get('strongest_influences', []),
                'optimization_opportunities': [
                    zone.area for zone in nutrition_dna.optimization_zones[:3]
                ],
                'success_probability': self.behavior_predictor.predict_goal_success_probability(
                    nutrition_dna, profile.get('goal', 'maintenance'), days
                )[0]
            }

            # 10. Generate adaptive recommendations
            adaptive_suggestions = self.meal_recommender.generate_adaptive_suggestions(
                nutrition_dna, list(plan_json.values())
            )

            return {
                'intro_summary': intro_summary,
                'plan_json': plan_json,
                'shopping_list_json': shopping_list_json,
                'daily_insights': daily_insights,
                'weekly_insights': weekly_insights.dict() if weekly_insights else {},
                'personalization_data': personalization_data,
                'adaptive_suggestions': adaptive_suggestions,
                'confidence': min(nutrition_dna.confidence_score + 0.2, 0.95),  # Boost confidence for enhanced version
                'model_used': 'enhanced_ai_nutrition_system_v1.0',
                'generation_metadata': {
                    'dna_archetype': nutrition_dna.archetype.value,
                    'context_sensitivity': context_analysis.get('context_score', 0.5),
                    'personalization_level': 'maximum',
                    'features_used': [
                        'nutrition_dna', 'behavioral_prediction', 'contextual_analysis',
                        'adaptive_recommendations', 'temporal_patterns', 'psychological_profiling'
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Enhanced food plan generation failed: {e}")
            # Fallback to basic generation
            return await self._generate_fallback_plan(profile, food_history, days)

    async def _get_or_create_nutrition_dna(
        self,
        profile: Dict[str, Any],
        food_history: List[Dict[str, Any]]
    ) -> NutritionDNA:
        """Get existing DNA or generate new one"""

        # In a real implementation, you'd check for existing DNA in database
        # For now, generate fresh DNA
        return self.dna_generator.generate_nutrition_dna(profile, food_history)

    async def _generate_ai_daily_plan(
        self,
        nutrition_dna: NutritionDNA,
        target_date: date,
        context_analysis: Dict[str, Any],
        weekly_predictions: Dict[str, Any],
        context: Dict[str, Any] = None,
        enhanced_profile: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered daily meal plan"""

        day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][target_date.weekday()]
        daily_predictions = weekly_predictions.get(day_name, [])

        # Prepare context for meal recommendations
        meal_context = {
            'is_weekend': target_date.weekday() >= 5,
            'day_of_week': target_date.weekday(),
            'predictions': daily_predictions,
            'weather': context.get('weather') if context else None
        }

        # Generate AI meal recommendations with enhanced preferences
        daily_meals = self.meal_recommender.generate_daily_meal_plan(
            nutrition_dna, target_date, meal_context, None, enhanced_profile
        )

        # Convert to plan format
        daily_plan = {}
        total_calories = 0
        total_protein = 0
        total_fats = 0
        total_carbs = 0

        for meal_type, recommendation in daily_meals.items():
            meal_data = {
                'calories': recommendation.calories,
                'protein': recommendation.protein,
                'fats': recommendation.fats,
                'carbs': recommendation.carbs,
                'text': f"{recommendation.dish_name} — {recommendation.reasoning}",
                'ingredients': recommendation.ingredients,
                'ai_metadata': {
                    'personalization_match': {
                        'energy_level': recommendation.matches_energy_level,
                        'craving_address': recommendation.addresses_typical_craving,
                        'schedule_fit': recommendation.fits_schedule_pattern,
                        'goal_support': recommendation.supports_current_goal
                    },
                    'prep_time': recommendation.prep_time_minutes,
                    'difficulty': recommendation.difficulty_level,
                    'optimal_time': recommendation.recommended_time.strftime('%H:%M')
                }
            }

            daily_plan[meal_type] = meal_data

            total_calories += recommendation.calories
            total_protein += recommendation.protein
            total_fats += recommendation.fats
            total_carbs += recommendation.carbs

        # Add behavioral predictions for the day
        high_risk_predictions = [p for p in daily_predictions if p.probability > 0.6]
        if high_risk_predictions:
            daily_plan['daily_alerts'] = [
                f"⚠️ {pred.event}: {pred.recommended_action}"
                for pred in high_risk_predictions[:2]
            ]

        # Add daily summary with AI insights
        daily_plan['summary'] = {
            'totals': {
                'calories': total_calories,
                'protein': total_protein,
                'fats': total_fats,
                'carbs': total_carbs
            },
            'ai_insights': self._generate_daily_ai_insights(
                nutrition_dna, target_date, daily_predictions
            )
        }

        return daily_plan

    def _generate_daily_ai_insights(
        self,
        nutrition_dna: NutritionDNA,
        target_date: date,
        predictions: List[Any]
    ) -> List[str]:
        """Generate AI insights for specific day"""

        insights = []
        day_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][target_date.weekday()]

        # Archetype-specific daily insight
        archetype_insights = {
            'EARLY_BIRD_PLANNER': f"{day_name} - используйте утреннюю энергию для подготовки здоровых блюд",
            'STRESS_DRIVEN': f"{day_name} может быть стрессовым - заранее подготовьте успокаивающие снеки",
            'SOCIAL_EATER': f"Если сегодня планируются встречи, изучите здоровые варианты заранее",
            'WEEKEND_WARRIOR': f"{'Выходной' if target_date.weekday() >= 5 else 'Рабочий'} день - поддерживайте баланс"
        }

        archetype_key = nutrition_dna.archetype.value
        if archetype_key in archetype_insights:
            insights.append(archetype_insights[archetype_key])

        # Prediction-based insights
        high_prob_predictions = [p for p in predictions if p.probability > 0.7]
        if high_prob_predictions:
            insights.append(f"Высокая вероятность: {high_prob_predictions[0].event}")

        # Temporal insights
        if target_date.weekday() == 0 and nutrition_dna.temporal_patterns.weekend_shift_hours > 1:
            insights.append("Понедельник после выходных - восстанавливаем режим питания")

        return insights[:3]

    def _create_enhanced_intro_summary(
        self,
        nutrition_dna: NutritionDNA,
        context_analysis: Dict[str, Any],
        weekly_insights: WeeklyInsight,
        profile: Dict[str, Any],
        days: int
    ) -> str:
        """Create personalized intro summary with AI insights"""

        summary_parts = []

        # Personalized greeting based on DNA
        archetype_greetings = {
            'EARLY_BIRD_PLANNER': "Как настоящий планировщик, вы получите детальный план с учетом ваших утренних привычек.",
            'STRESS_DRIVEN': "План учитывает ваши стрессовые триггеры и предлагает решения для эмоционального питания.",
            'SOCIAL_EATER': "Социальные ситуации влияют на ваше питание - план включает стратегии для встреч и ресторанов.",
            'WEEKEND_WARRIOR': "План поможет поддержать баланс между активными выходными и здоровым питанием.",
            'BUSY_PROFESSIONAL': "Быстрые, но питательные решения для вашего насыщенного графика.",
            'LATE_STARTER_IMPULSIVE': "Простые решения для спонтанных ситуаций и поздних завтраков.",
            'INTUITIVE_GRAZER': "План поддерживает ваш интуитивный подход с небольшими частыми приемами пищи."
        }

        greeting = archetype_greetings.get(
            nutrition_dna.archetype.value,
            "Персонализированный план питания на основе анализа ваших привычек."
        )
        summary_parts.append(greeting)

        # DNA insights
        summary_parts.append(
            f"Ваш тип питания: {nutrition_dna.archetype.value.replace('_', ' ').title()} "
            f"(точность профиля: {nutrition_dna.confidence_score:.0%})."
        )

        # Context insights
        strong_influences = context_analysis.get('strongest_influences', [])
        if strong_influences:
            top_influence = strong_influences[0]
            summary_parts.append(
                f"Наибольшее влияние на ваше питание оказывает: {top_influence['description'].lower()}."
            )

        # Success prediction
        goal = profile.get('goal', 'поддержание здоровья')
        success_prob, factors = self.behavior_predictor.predict_goal_success_probability(
            nutrition_dna, str(goal), days * 7  # Convert to weeks
        )

        if success_prob > 0.7:
            summary_parts.append(f"Высокие шансы достичь цели '{goal}' ({success_prob:.0%})!")
        elif success_prob > 0.5:
            summary_parts.append(f"Хорошие перспективы для достижения цели '{goal}' при следовании плану.")
        else:
            summary_parts.append(f"План разработан с учетом особенностей для достижения цели '{goal}'.")

        # Weekly focus
        if weekly_insights and weekly_insights.micro_goals:
            focus_goal = weekly_insights.micro_goals[0]
            summary_parts.append(f"Фокус недели: {focus_goal.lower()}.")

        return " ".join(summary_parts)

    def _generate_smart_shopping_list(
        self,
        plan_json: Dict[str, Any],
        nutrition_dna: NutritionDNA
    ) -> Dict[str, Any]:
        """Generate smart shopping list with AI suggestions"""

        # Aggregate all ingredients
        all_ingredients = []
        for day_data in plan_json.values():
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal = day_data.get(meal_type, {})
                ingredients = meal.get('ingredients', [])
                all_ingredients.extend(ingredients)

        # Group by category
        categories = {
            'Белки': ['курица', 'рыба', 'мясо', 'яйца', 'творог', 'йогурт', 'тофу', 'бобы'],
            'Овощи': ['салат', 'огурцы', 'помидоры', 'морковь', 'брокколи', 'шпинат'],
            'Фрукты': ['яблоки', 'бананы', 'ягоды', 'апельсины'],
            'Злаки': ['овсянка', 'рис', 'гречка', 'киноа', 'хлеб'],
            'Молочные': ['молоко', 'сыр', 'йогурт', 'кефир'],
            'Приправы': ['соль', 'перец', 'специи', 'масло']
        }

        categorized_shopping = {cat: [] for cat in categories.keys()}

        for ingredient in all_ingredients:
            ingredient_name = ingredient.get('name', '').lower()
            categorized = False

            for category, keywords in categories.items():
                if any(keyword in ingredient_name for keyword in keywords):
                    categorized_shopping[category].append(ingredient)
                    categorized = True
                    break

            if not categorized:
                categorized_shopping.setdefault('Другое', []).append(ingredient)

        # Add AI suggestions based on DNA
        ai_suggestions = []

        # Optimization zone suggestions
        for zone in nutrition_dna.optimization_zones[:2]:
            if zone.area == 'fiber_intake':
                ai_suggestions.append({
                    'category': 'AI рекомендации',
                    'item': 'Добавьте больше овощей и фруктов для клетчатки',
                    'reasoning': 'Улучшение зоны оптимизации: клетчатка'
                })
            elif zone.area == 'protein_intake':
                ai_suggestions.append({
                    'category': 'AI рекомендации',
                    'item': 'Рассмотрите протеиновые снеки (орехи, семена)',
                    'reasoning': 'Улучшение зоны оптимизации: белок'
                })

        # Archetype-specific suggestions
        archetype_suggestions = {
            'BUSY_PROFESSIONAL': 'Готовые здоровые снеки для быстрых перекусов',
            'STRESS_DRIVEN': 'Травяной чай и темный шоколад для управления стрессом',
            'SOCIAL_EATER': 'Красивая посуда для презентации блюд'
        }

        suggestion = archetype_suggestions.get(nutrition_dna.archetype.value)
        if suggestion:
            ai_suggestions.append({
                'category': 'Персональные рекомендации',
                'item': suggestion,
                'reasoning': f'Для вашего типа: {nutrition_dna.archetype.value.replace("_", " ").title()}'
            })

        return {
            **categorized_shopping,
            'ai_suggestions': ai_suggestions
        }

    def _summarize_predictions(self, weekly_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize behavioral predictions for the week"""

        all_predictions = []
        for day_predictions in weekly_predictions.values():
            all_predictions.extend(day_predictions)

        # Find most common prediction themes
        prediction_themes = Counter()
        for pred in all_predictions:
            if pred.probability > 0.6:
                theme = pred.event.split('_')[0]  # Get first part of event name
                prediction_themes[theme] += 1

        return {
            'total_predictions': len(all_predictions),
            'high_confidence_predictions': len([p for p in all_predictions if p.probability > 0.7]),
            'common_themes': dict(prediction_themes.most_common(3)),
            'risk_days': len([day for day, preds in weekly_predictions.items()
                            if any(p.probability > 0.8 for p in preds)])
        }

    async def _generate_fallback_plan(
        self,
        profile: Dict[str, Any],
        food_history: List[Dict[str, Any]],
        days: int
    ) -> Dict[str, Any]:
        """Generate basic fallback plan if enhanced generation fails"""

        logger.warning("Using fallback plan generation")

        # Simple fallback similar to existing generator
        target_calories = profile.get('daily_calories_target', 2000)
        goal = profile.get('goal', 'maintenance')

        plan_json = {}
        for day_num in range(1, days + 1):
            daily_calories = target_calories + ((-1) ** day_num) * 100  # Slight variation

            plan_json[f"day_{day_num}"] = {
                'breakfast': {
                    'calories': int(daily_calories * 0.25),
                    'protein': int(daily_calories * 0.25 * 0.2 / 4),
                    'fats': int(daily_calories * 0.25 * 0.3 / 9),
                    'carbs': int(daily_calories * 0.25 * 0.5 / 4),
                    'text': 'Сбалансированный завтрак для энергии на день',
                    'ingredients': []
                },
                'lunch': {
                    'calories': int(daily_calories * 0.4),
                    'protein': int(daily_calories * 0.4 * 0.25 / 4),
                    'fats': int(daily_calories * 0.4 * 0.3 / 9),
                    'carbs': int(daily_calories * 0.4 * 0.45 / 4),
                    'text': 'Питательный обед для продуктивного дня',
                    'ingredients': []
                },
                'dinner': {
                    'calories': int(daily_calories * 0.35),
                    'protein': int(daily_calories * 0.35 * 0.3 / 4),
                    'fats': int(daily_calories * 0.35 * 0.25 / 9),
                    'carbs': int(daily_calories * 0.35 * 0.45 / 4),
                    'text': 'Легкий ужин для восстановления',
                    'ingredients': []
                }
            }

        return {
            'intro_summary': f'Базовый план питания на {days} дней для достижения цели: {goal}.',
            'plan_json': plan_json,
            'shopping_list_json': {'Базовые продукты': ['овощи', 'белки', 'злаки']},
            'confidence': 0.3,
            'model_used': 'fallback_generator'
        }

    async def _get_nutrition_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get nutrition preferences from onboarding questionnaire"""

        if not user_id:
            return None

        try:
            # Import here to avoid circular imports
            from ..public.routers.nutrition_onboarding import _get_user_preferences

            preferences = await _get_user_preferences(user_id)
            return preferences.dict() if preferences else None

        except Exception as e:
            logger.warning(f"Failed to get nutrition preferences for user {user_id}: {e}")
            return None

    async def _merge_nutrition_preferences(
        self,
        profile: Dict[str, Any],
        nutrition_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge nutrition preferences from onboarding into profile for enhanced personalization"""

        enhanced_profile = profile.copy()

        # Map onboarding preferences to profile fields
        preference_mapping = {
            'goal': 'goal',
            'daily_calories_target': 'daily_calories_target',
            'activity_level': 'activity_level',
            'dietary_restrictions': 'dietary_preferences',
            'allergies': 'allergies',
            'favorite_foods': 'favorite_foods',
            'disliked_foods': 'disliked_foods',
            'cuisines': 'preferred_cuisines',
            'meal_times': 'meal_times',
            'cooking_skill': 'cooking_skill',
            'cooking_time_available': 'cooking_time_available',
            'work_schedule': 'work_schedule',
            'health_conditions': 'health_conditions',
            'water_intake_goal': 'water_intake_goal',
            'meal_prep_preference': 'meal_prep_preference',
            'snacking_preference': 'snacking_preference',
            'weekend_eating_style': 'weekend_eating_style',
            'stress_eating_tendency': 'stress_eating_tendency',
            'primary_motivation': 'primary_motivation',
            'weight_goal': 'weight_goal',
            'timeline': 'timeline'
        }

        # Apply preference mappings
        for pref_key, profile_key in preference_mapping.items():
            if pref_key in nutrition_preferences and nutrition_preferences[pref_key] is not None:
                enhanced_profile[profile_key] = nutrition_preferences[pref_key]

        # Add composite preference fields for meal recommendations
        enhanced_profile['enhanced_preferences'] = {
            'eating_frequency': nutrition_preferences.get('eating_frequency', '3_meals'),
            'skip_meals': nutrition_preferences.get('skip_meals', []),
            'social_eating_frequency': nutrition_preferences.get('social_eating_frequency', 'sometimes'),
            'accountability_preference': nutrition_preferences.get('accountability_preference', 'progress_tracking'),
            'supplements': nutrition_preferences.get('supplements', [])
        }

        # Add preference flags for meal customization
        enhanced_profile['preference_flags'] = {
            'has_allergies': bool(nutrition_preferences.get('allergies', [])),
            'has_dietary_restrictions': bool(nutrition_preferences.get('dietary_restrictions', [])),
            'has_disliked_foods': bool(nutrition_preferences.get('disliked_foods', [])),
            'prefers_quick_meals': nutrition_preferences.get('cooking_time_available') == 'quick',
            'advanced_cooking_skills': nutrition_preferences.get('cooking_skill') == 'advanced',
            'meal_prep_enthusiast': nutrition_preferences.get('meal_prep_preference') == 'full_prep',
            'stress_sensitive': (nutrition_preferences.get('stress_eating_tendency', 3) >= 4),
            'social_eater': nutrition_preferences.get('social_eating_frequency') in ['often', 'very_often'],
            'weekend_flexible': nutrition_preferences.get('weekend_eating_style') == 'flexible'
        }

        logger.info(f"Enhanced profile with {len(preference_mapping)} preference fields and {len(enhanced_profile['preference_flags'])} preference flags")

        return enhanced_profile