"""
Predictive Analytics for Eating Behavior.
Uses machine learning-like approaches to predict user's eating patterns and potential issues.
"""
from __future__ import annotations

import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta, date, time
from typing import Dict, List, Optional, Any, Tuple, NamedTuple

from loguru import logger

from ..models.nutrition_profile import NutritionDNA, EatingPersonality


class PredictionResult(NamedTuple):
    """Structured prediction result"""
    event: str
    probability: float
    confidence: float
    recommended_action: str
    optimal_timing: Optional[time] = None


class BehaviorPredictor:
    """
    Predicts eating behaviors using pattern analysis and temporal modeling.
    """

    # Probability weights for different prediction factors
    ARCHETYPE_WEIGHTS = {
        EatingPersonality.EARLY_BIRD_PLANNER: {'morning_success': 0.8, 'evening_control': 0.7, 'weekend_stability': 0.6},
        EatingPersonality.LATE_STARTER_IMPULSIVE: {'morning_skip': 0.7, 'evening_overeat': 0.6, 'impulse_buy': 0.8},
        EatingPersonality.STRESS_DRIVEN: {'stress_eat': 0.8, 'comfort_food': 0.7, 'emotional_trigger': 0.9},
        EatingPersonality.SOCIAL_EATER: {'restaurant_overeat': 0.7, 'peer_pressure': 0.6, 'social_drinking': 0.5},
        EatingPersonality.WEEKEND_WARRIOR: {'weekend_binge': 0.8, 'monday_crash': 0.7, 'friday_reward': 0.6},
        EatingPersonality.INTUITIVE_GRAZER: {'small_meals': 0.8, 'stable_intake': 0.7, 'low_variety': 0.5},
        EatingPersonality.BUSY_PROFESSIONAL: {'skip_meals': 0.7, 'fast_food': 0.6, 'irregular_timing': 0.8},
        EatingPersonality.STRUCTURED_BALANCED: {'consistent_success': 0.8, 'gradual_improvement': 0.7}
    }

    @classmethod
    def predict_daily_behavior(
        cls,
        nutrition_dna: NutritionDNA,
        target_date: date,
        recent_logs: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None
    ) -> List[PredictionResult]:
        """Predict eating behavior for a specific day"""

        predictions = []
        recent_logs = recent_logs or []
        context = context or {}

        day_of_week = target_date.weekday()
        is_weekend = day_of_week >= 5

        # 1. Time-based predictions
        predictions.extend(cls._predict_temporal_behaviors(nutrition_dna, day_of_week))

        # 2. Archetype-specific predictions
        predictions.extend(cls._predict_archetype_behaviors(nutrition_dna.archetype, day_of_week, is_weekend))

        # 3. Trigger-based predictions
        predictions.extend(cls._predict_trigger_behaviors(nutrition_dna, day_of_week))

        # 4. Pattern-based predictions from recent behavior
        predictions.extend(cls._predict_from_recent_patterns(recent_logs, day_of_week))

        # 5. Context-based predictions (weather, stress, etc.)
        predictions.extend(cls._predict_contextual_behaviors(nutrition_dna, context))

        # Sort by probability and return top predictions
        predictions.sort(key=lambda p: p.probability * p.confidence, reverse=True)
        return predictions[:8]  # Top 8 predictions

    @classmethod
    def _predict_temporal_behaviors(cls, nutrition_dna: NutritionDNA, day_of_week: int) -> List[PredictionResult]:
        """Predict behaviors based on temporal patterns"""

        predictions = []
        temporal = nutrition_dna.temporal_patterns
        energy = nutrition_dna.energy_patterns

        # Late night eating prediction
        if temporal.late_night_eating_frequency > 0.3:
            probability = temporal.late_night_eating_frequency
            # Higher on weekends and Fridays
            if day_of_week in [4, 5, 6]:
                probability *= 1.3

            predictions.append(PredictionResult(
                event="late_night_snacking",
                probability=min(probability, 0.95),
                confidence=0.8,
                recommended_action="Подготовьте здоровые вечерние снеки или травяной чай",
                optimal_timing=time(20, 30)  # Preventive action at 8:30 PM
            ))

        # Breakfast skipping prediction
        if energy.morning_appetite < 0.3 and day_of_week < 5:  # Weekdays
            predictions.append(PredictionResult(
                event="breakfast_skip",
                probability=1.0 - energy.morning_appetite,
                confidence=0.7,
                recommended_action="Приготовьте легкий белковый завтрак или смузи",
                optimal_timing=temporal.preferred_breakfast_time
            ))

        # Weekend routine disruption
        if temporal.weekend_shift_hours > 2 and day_of_week in [5, 6]:
            predictions.append(PredictionResult(
                event="weekend_routine_disruption",
                probability=min(temporal.weekend_shift_hours / 4, 0.9),
                confidence=0.6,
                recommended_action="Запланируйте хотя бы один регулярный прием пищи"
            ))

        # Monday recovery difficulty
        if day_of_week == 0 and temporal.weekend_shift_hours > 1.5:
            predictions.append(PredictionResult(
                event="monday_adjustment_difficulty",
                probability=min(temporal.weekend_shift_hours / 3, 0.8),
                confidence=0.7,
                recommended_action="Установите будильник на завтрак и подготовьте его с вечера"
            ))

        return predictions

    @classmethod
    def _predict_archetype_behaviors(cls, archetype: EatingPersonality, day_of_week: int, is_weekend: bool) -> List[PredictionResult]:
        """Predict behaviors specific to eating personality archetype"""

        predictions = []
        archetype_weights = cls.ARCHETYPE_WEIGHTS.get(archetype, {})

        if archetype == EatingPersonality.STRESS_DRIVEN:
            # Midweek stress eating
            if day_of_week in [1, 2, 3]:
                predictions.append(PredictionResult(
                    event="stress_induced_eating",
                    probability=archetype_weights.get('stress_eat', 0.5) * 1.2,  # Higher midweek
                    confidence=0.8,
                    recommended_action="Подготовьте план борьбы со стрессом: глубокое дыхание, прогулка",
                    optimal_timing=time(15, 0)  # Typical afternoon stress peak
                ))

            # Comfort food craving
            predictions.append(PredictionResult(
                event="comfort_food_craving",
                probability=archetype_weights.get('comfort_food', 0.6),
                confidence=0.7,
                recommended_action="Найдите здоровые альтернативы комфортной еде"
            ))

        elif archetype == EatingPersonality.WEEKEND_WARRIOR:
            if is_weekend:
                predictions.append(PredictionResult(
                    event="weekend_indulgence",
                    probability=archetype_weights.get('weekend_binge', 0.7),
                    confidence=0.8,
                    recommended_action="Планируйте 'читмил' заранее и ограничьте его одним приемом пищи"
                ))

            elif day_of_week == 4:  # Friday
                predictions.append(PredictionResult(
                    event="friday_reward_eating",
                    probability=archetype_weights.get('friday_reward', 0.6),
                    confidence=0.7,
                    recommended_action="Найдите нефудовые способы отметить конец рабочей недели"
                ))

        elif archetype == EatingPersonality.SOCIAL_EATER:
            if is_weekend:
                predictions.append(PredictionResult(
                    event="social_dining_excess",
                    probability=archetype_weights.get('restaurant_overeat', 0.7),
                    confidence=0.6,
                    recommended_action="Изучите меню заранее и выберите здоровые опции"
                ))

        elif archetype == EatingPersonality.BUSY_PROFESSIONAL:
            if not is_weekend:
                predictions.append(PredictionResult(
                    event="meal_skipping",
                    probability=archetype_weights.get('skip_meals', 0.7),
                    confidence=0.8,
                    recommended_action="Поставьте напоминания о приемах пищи на телефон",
                    optimal_timing=time(13, 0)
                ))

        elif archetype == EatingPersonality.LATE_STARTER_IMPULSIVE:
            predictions.append(PredictionResult(
                event="impulse_food_purchase",
                probability=archetype_weights.get('impulse_buy', 0.8),
                confidence=0.7,
                recommended_action="Составьте список покупок заранее и не ходите в магазин голодными"
            ))

        return predictions

    @classmethod
    def _predict_trigger_behaviors(cls, nutrition_dna: NutritionDNA, day_of_week: int) -> List[PredictionResult]:
        """Predict behaviors based on identified triggers"""

        predictions = []

        for trigger in nutrition_dna.triggers:
            if trigger.probability > 0.5:
                trigger_name = trigger.trigger.lower()

                # Day-specific trigger predictions
                if 'monday' in trigger_name and day_of_week == 0:
                    predictions.append(PredictionResult(
                        event=f"trigger_{trigger.trigger}",
                        probability=trigger.probability,
                        confidence=0.8,
                        recommended_action=f"Ожидается {trigger.food_response}. Подготовьте здоровую альтернативу"
                    ))

                elif 'friday' in trigger_name and day_of_week == 4:
                    predictions.append(PredictionResult(
                        event=f"trigger_{trigger.trigger}",
                        probability=trigger.probability,
                        confidence=0.8,
                        recommended_action=f"Пятничный триггер: {trigger.food_response}. Запланируйте активность"
                    ))

                elif 'stress' in trigger_name:
                    # Stress higher midweek
                    stress_multiplier = 1.3 if day_of_week in [1, 2, 3] else 1.0
                    predictions.append(PredictionResult(
                        event="stress_trigger_activation",
                        probability=min(trigger.probability * stress_multiplier, 0.95),
                        confidence=0.7,
                        recommended_action="Стрессовый день. Практикуйте mindful eating"
                    ))

                elif 'evening' in trigger_name:
                    predictions.append(PredictionResult(
                        event="evening_trigger",
                        probability=trigger.probability,
                        confidence=0.8,
                        recommended_action="Вечерний триггер активен. Приготовьте альтернативы заранее",
                        optimal_timing=trigger.time_of_day or time(20, 0)
                    ))

        return predictions

    @classmethod
    def _predict_from_recent_patterns(cls, recent_logs: List[Dict[str, Any]], day_of_week: int) -> List[PredictionResult]:
        """Predict behaviors based on recent eating patterns"""

        predictions = []

        if not recent_logs or len(recent_logs) < 5:
            return predictions

        # Analyze last 7 days patterns
        daily_patterns = defaultdict(list)
        late_eating_days = 0
        total_days = 0

        for log in recent_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                log_day = dt.weekday()
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

                daily_patterns[log_day].append({
                    'hour': dt.hour,
                    'calories': calories,
                    'date': dt.date()
                })

                if dt.hour >= 21:
                    late_eating_days += 1

                total_days = len(set(log['date'] for logs in daily_patterns.values() for log in logs))

            except Exception:
                continue

        # Pattern-based predictions
        if day_of_week in daily_patterns:
            same_day_logs = daily_patterns[day_of_week]

            # Predict similar day patterns
            if len(same_day_logs) >= 2:
                avg_hour = statistics.mean(log['hour'] for log in same_day_logs)
                avg_calories = statistics.mean(log['calories'] for log in same_day_logs if log['calories'] > 0)

                if avg_hour >= 20:  # Late eating pattern on this day
                    predictions.append(PredictionResult(
                        event="same_day_late_eating",
                        probability=0.7,
                        confidence=0.6,
                        recommended_action=f"В этот день недели вы обычно едите поздно (~{avg_hour:.0f}:00). Попробуйте поужинать пораньше"
                    ))

                if avg_calories > 600:  # High calorie pattern
                    predictions.append(PredictionResult(
                        event="same_day_high_intake",
                        probability=0.6,
                        confidence=0.5,
                        recommended_action="В этот день недели порции обычно больше. Ешьте медленнее и прислушивайтесь к сытости"
                    ))

        # Recent trend continuation
        late_eating_trend = late_eating_days / max(total_days, 1)
        if late_eating_trend > 0.4:
            predictions.append(PredictionResult(
                event="late_eating_trend_continuation",
                probability=late_eating_trend,
                confidence=0.7,
                recommended_action="Недавно часто едите поздно. Попробуйте сдвинуть ужин на час раньше"
            ))

        return predictions

    @classmethod
    def _predict_contextual_behaviors(cls, nutrition_dna: NutritionDNA, context: Dict[str, Any]) -> List[PredictionResult]:
        """Predict behaviors based on external context"""

        predictions = []

        # Weather-based predictions
        weather = context.get('weather', '').lower()
        if 'rain' in weather or 'cold' in weather:
            # Cold/rainy weather increases comfort eating
            base_comfort_probability = nutrition_dna.energy_patterns.evening_comfort_eating

            predictions.append(PredictionResult(
                event="weather_comfort_eating",
                probability=min(base_comfort_probability * 1.4, 0.9),
                confidence=0.5,
                recommended_action="Холодная/дождливая погода провоцирует комфортное питание. Приготовьте теплые здоровые напитки"
            ))

        # Work stress context
        work_stress = context.get('work_stress_level', 0)
        if work_stress > 7:  # High stress (scale 1-10)
            stress_eating_prob = nutrition_dna.social_patterns.work_stress_snacking

            predictions.append(PredictionResult(
                event="high_stress_eating",
                probability=min(stress_eating_prob * 1.5, 0.95),
                confidence=0.8,
                recommended_action="Высокий уровень стресса. Делайте паузы перед едой и выбирайте белковые снеки"
            ))

        # Social context
        social_plans = context.get('social_plans', False)
        if social_plans and nutrition_dna.archetype == EatingPersonality.SOCIAL_EATER:
            predictions.append(PredictionResult(
                event="social_eating_excess",
                probability=nutrition_dna.social_patterns.social_meal_impact,
                confidence=0.7,
                recommended_action="Социальные планы сегодня. Поешьте легкий снек заранее, чтобы не переесть"
            ))

        # Travel context
        travel = context.get('travel', False)
        if travel:
            predictions.append(PredictionResult(
                event="travel_disruption",
                probability=0.8,
                confidence=0.6,
                recommended_action="Путешествие нарушает привычный режим. Возьмите здоровые снеки с собой"
            ))

        return predictions

    @classmethod
    def predict_weekly_outcomes(
        cls,
        nutrition_dna: NutritionDNA,
        week_start: date,
        weekly_context: Dict[str, Any] = None
    ) -> Dict[str, List[PredictionResult]]:
        """Predict outcomes for entire week"""

        weekly_predictions = {}
        weekly_context = weekly_context or {}

        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for i, day_name in enumerate(day_names):
            target_date = week_start + timedelta(days=i)
            daily_context = weekly_context.get(day_name, {})

            daily_predictions = cls.predict_daily_behavior(
                nutrition_dna, target_date, context=daily_context
            )

            weekly_predictions[day_name] = daily_predictions

        return weekly_predictions

    @classmethod
    def predict_goal_success_probability(
        cls,
        nutrition_dna: NutritionDNA,
        goal: str,
        timeframe_days: int = 30
    ) -> Tuple[float, List[str]]:
        """Predict probability of achieving nutrition goal"""

        goal = goal.lower()
        success_factors = []
        risk_factors = []

        # Base success probability from goal alignment
        base_probability = nutrition_dna.goal_alignment_score

        # Archetype success modifiers
        archetype_modifiers = {
            EatingPersonality.EARLY_BIRD_PLANNER: 0.8,      # High success rate
            EatingPersonality.STRUCTURED_BALANCED: 0.85,    # Highest success rate
            EatingPersonality.LATE_STARTER_IMPULSIVE: 0.4,  # Lower success rate
            EatingPersonality.STRESS_DRIVEN: 0.5,           # Moderate success rate
            EatingPersonality.SOCIAL_EATER: 0.6,            # Depends on social support
            EatingPersonality.WEEKEND_WARRIOR: 0.5,         # Inconsistent
            EatingPersonality.BUSY_PROFESSIONAL: 0.4,       # Time constraints
            EatingPersonality.INTUITIVE_GRAZER: 0.7         # Good at listening to body
        }

        archetype_modifier = archetype_modifiers.get(nutrition_dna.archetype, 0.6)

        # Goal-specific analysis
        if 'weight loss' in goal or 'похуд' in goal:
            # Weight loss specific factors
            if nutrition_dna.temporal_patterns.meal_timing_consistency > 0.7:
                success_factors.append("Стабильный режим питания")
                base_probability += 0.1

            if nutrition_dna.temporal_patterns.late_night_eating_frequency > 0.4:
                risk_factors.append("Частое позднее питание")
                base_probability -= 0.15

            if nutrition_dna.social_patterns.weekend_indulgence_score > 0.5:
                risk_factors.append("Сильные отклонения в выходные")
                base_probability -= 0.1

        elif 'muscle' in goal or 'мышц' in goal:
            # Muscle gain specific factors
            if nutrition_dna.energy_patterns.morning_appetite > 0.5:
                success_factors.append("Хороший утренний аппетит")
                base_probability += 0.1

            if nutrition_dna.consistency_score > 0.8:
                success_factors.append("Высокая последовательность питания")
                base_probability += 0.15

        # Consistency factors
        if nutrition_dna.consistency_score > 0.8:
            success_factors.append("Отличная последовательность")
        elif nutrition_dna.consistency_score < 0.4:
            risk_factors.append("Нестабильный режим питания")

        # Success pattern influence
        strong_patterns = [p for p in nutrition_dna.success_patterns if p.correlation > 0.7]
        if strong_patterns:
            success_factors.append(f"Выявлено {len(strong_patterns)} сильных паттернов успеха")
            base_probability += len(strong_patterns) * 0.05

        # Risk from triggers
        high_risk_triggers = [t for t in nutrition_dna.triggers if t.probability > 0.7]
        if high_risk_triggers:
            risk_factors.append(f"{len(high_risk_triggers)} сильных поведенческих триггеров")
            base_probability -= len(high_risk_triggers) * 0.03

        # Combine all factors
        final_probability = base_probability * archetype_modifier

        # Time adjustment - longer timeframes are harder
        if timeframe_days > 60:
            final_probability *= 0.9
        elif timeframe_days < 14:
            final_probability *= 1.1

        # Ensure probability is within bounds
        final_probability = max(0.1, min(final_probability, 0.95))

        return final_probability, success_factors + risk_factors

    @classmethod
    def get_predictive_recommendations(
        cls,
        predictions: List[PredictionResult],
        nutrition_dna: NutritionDNA
    ) -> List[str]:
        """Generate actionable recommendations based on predictions"""

        recommendations = []

        # High probability predictions get priority
        high_prob_predictions = [p for p in predictions if p.probability > 0.7]

        for prediction in high_prob_predictions[:3]:  # Top 3 high probability events
            recommendations.append(prediction.recommended_action)

        # Add archetype-specific general recommendations
        if nutrition_dna.archetype == EatingPersonality.STRESS_DRIVEN:
            recommendations.append("Практикуйте техники управления стрессом перед едой")

        elif nutrition_dna.archetype == EatingPersonality.SOCIAL_EATER:
            recommendations.append("Планируйте социальные приемы пищи заранее")

        elif nutrition_dna.archetype == EatingPersonality.WEEKEND_WARRIOR:
            recommendations.append("Установите одно правило здорового питания для выходных")

        # Add optimization zone recommendations
        easy_wins = [zone for zone in nutrition_dna.optimization_zones if zone.difficulty == "easy_wins"]
        if easy_wins:
            zone = easy_wins[0]
            recommendations.append(f"Легкая победа: улучшите {zone.area}")

        return recommendations[:5]  # Maximum 5 recommendations