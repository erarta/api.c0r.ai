"""
Personalized Insights Engine.
Generates context-aware, actionable insights based on user's Nutrition DNA and current behavior.
"""
from __future__ import annotations

import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..models.nutrition_profile import (
    NutritionDNA, EatingPersonality, WeeklyInsight, PersonalizedMealRecommendation
)
from ..analyzers.temporal_patterns import TemporalPatternsAnalyzer
from ..analyzers.psychological_profile import PsychologicalProfileAnalyzer


class PersonalizedInsightsEngine:
    """
    Generates personalized insights, recommendations, and predictions
    based on user's Nutrition DNA and behavioral patterns.
    """

    @classmethod
    def generate_daily_insights(
        cls,
        nutrition_dna: NutritionDNA,
        current_date: date = None,
        recent_logs: List[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate personalized daily insights"""

        if current_date is None:
            current_date = date.today()

        insights = []
        day_of_week = current_date.weekday()
        recent_logs = recent_logs or []

        # Day-specific insights based on archetype
        insights.extend(cls._get_archetype_daily_insights(nutrition_dna.archetype, day_of_week))

        # Temporal pattern insights
        insights.extend(cls._get_temporal_insights(nutrition_dna, day_of_week))

        # Trigger-based insights
        insights.extend(cls._get_trigger_insights(nutrition_dna, day_of_week))

        # Recent behavior insights
        if recent_logs:
            insights.extend(cls._get_recent_behavior_insights(recent_logs, nutrition_dna))

        # Energy pattern insights
        insights.extend(cls._get_energy_pattern_insights(nutrition_dna, day_of_week))

        return insights[:5]  # Return top 5 most relevant insights

    @classmethod
    def _get_archetype_daily_insights(cls, archetype: EatingPersonality, day_of_week: int) -> List[str]:
        """Get archetype-specific insights for the day"""

        day_names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        today = day_names[day_of_week]

        insights_map = {
            EatingPersonality.EARLY_BIRD_PLANNER: {
                0: f"Понедельник - ваш день! Используйте утреннюю энергию для планирования питания на всю неделю.",
                4: f"Пятница - время подготовить здоровые снеки на выходные, чтобы не сбиться с режима.",
                6: f"Воскресенье идеально для meal prep - готовьте основы блюд на предстоящую неделю."
            },
            EatingPersonality.LATE_STARTER_IMPULSIVE: {
                0: f"Понедельник может быть сложным после выходных. Держите простые варианты завтрака под рукой.",
                3: f"Середина недели - хорошее время стабилизировать режим. Попробуйте поужинать на час раньше.",
                5: f"Субботнее утро - отличная возможность попробовать новый здоровый завтрак без спешки."
            },
            EatingPersonality.STRESS_DRIVEN: {
                0: f"Понедельники могут быть стрессовыми. Заранее приготовьте успокаивающий чай и полезные снеки.",
                2: f"Середа недели - пик стресса. Делайте глубокие вдохи перед едой и выбирайте белковые блюда.",
                4: f"Пятница - день расслабления. Но избегайте 'наградной' еды, лучше сходите на прогулку."
            },
            EatingPersonality.SOCIAL_EATER: {
                4: f"Пятничные планы? Изучите меню ресторана заранее и выберите здоровые опции.",
                5: f"Субботние встречи с друзьями - отличный повод попробовать новые здоровые рестораны.",
                6: f"Воскресные семейные обеды - предложите приготовить что-то полезное и вкусное для всех."
            },
            EatingPersonality.WEEKEND_WARRIOR: {
                0: f"Понедельник - восстанавливаемся после выходных. Начните день с белкового завтрака.",
                4: f"Пятница - планируйте выходные так, чтобы включить и активность, и здоровую еду.",
                5: f"Суббота - день экспериментов! Попробуйте приготовить новое здоровое блюдо."
            }
        }

        archetype_insights = insights_map.get(archetype, {})
        insight = archetype_insights.get(day_of_week)

        return [insight] if insight else []

    @classmethod
    def _get_temporal_insights(cls, nutrition_dna: NutritionDNA, day_of_week: int) -> List[str]:
        """Get insights based on temporal eating patterns"""

        insights = []
        patterns = nutrition_dna.temporal_patterns

        # Weekend shift insights
        if day_of_week in [5, 6] and patterns.weekend_shift_hours > 1.5:
            insights.append(
                f"В выходные ваш режим обычно сдвигается на {patterns.weekend_shift_hours:.1f} часов. "
                f"Попробуйте сдвинуть постепенно - сначала завтрак, потом остальные приемы пищи."
            )

        # Monday recovery insight
        if day_of_week == 0 and patterns.weekend_shift_hours > 1:
            insights.append(
                f"Понедельник после выходного сдвига режима. Ваш обычный завтрак в "
                f"{patterns.preferred_breakfast_time.strftime('%H:%M')} поможет вернуться в ритм."
            )

        # Late eating insights
        if patterns.late_night_eating_frequency > 0.3:
            if day_of_week in [4, 5, 6]:  # Weekend approach
                insights.append(
                    "Вы часто едите поздно вечером. В выходные особенно важно не переносить ужин на поздний час."
                )

        # Consistency insights
        if patterns.meal_timing_consistency < 0.5 and day_of_week in [0, 1]:  # Week start
            insights.append(
                "Начало недели - отличное время упорядочить режим питания. "
                "Постарайтесь есть в одно и то же время сегодня и завтра."
            )

        return insights

    @classmethod
    def _get_trigger_insights(cls, nutrition_dna: NutritionDNA, day_of_week: int) -> List[str]:
        """Get insights based on identified triggers"""

        insights = []

        for trigger in nutrition_dna.triggers:
            if trigger.probability > 0.6:  # High probability triggers only
                trigger_name = trigger.trigger.lower()

                # Day-specific trigger insights
                if 'monday' in trigger_name and day_of_week == 0:
                    insights.append(
                        f"Понедельники обычно вызывают у вас {trigger.food_response}. "
                        f"Подготовьте альтернативу заранее - возможно, травяной чай или орехи."
                    )

                elif 'friday' in trigger_name and day_of_week == 4:
                    insights.append(
                        f"Пятницы часто провоцируют {trigger.food_response}. "
                        f"Запланируйте что-то приятное, но полезное на вечер."
                    )

                elif 'stress' in trigger_name and day_of_week in [1, 2, 3]:  # Midweek stress
                    insights.append(
                        f"Середина недели может вызвать стресс и {trigger.food_response}. "
                        f"Попробуйте 5-минутную медитацию перед едой."
                    )

                elif 'evening' in trigger_name:
                    insights.append(
                        f"Вечером у вас часто бывает {trigger.food_response}. "
                        f"Поставьте напоминание выпить стакан воды в {trigger.time_of_day or '21:30'}."
                    )

        return insights

    @classmethod
    def _get_recent_behavior_insights(cls, recent_logs: List[Dict[str, Any]], nutrition_dna: NutritionDNA) -> List[str]:
        """Generate insights based on recent eating behavior"""

        insights = []

        if not recent_logs:
            return insights

        # Analyze last 3 days
        last_3_days = []
        cutoff_date = datetime.now() - timedelta(days=3)

        for log in recent_logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if dt >= cutoff_date:
                        last_3_days.append(log)
                except Exception:
                    continue

        if len(last_3_days) < 3:
            insights.append("Последние дни было мало анализов пищи. Больше данных помогут дать лучшие рекомендации.")
            return insights

        # Check for patterns deviation
        recent_late_eating = sum(1 for log in last_3_days
                               if cls._is_late_eating(log.get('timestamp'))) / len(last_3_days)

        if recent_late_eating > nutrition_dna.temporal_patterns.late_night_eating_frequency + 0.2:
            insights.append(
                "Последние дни вы едите позже обычного. Это может влиять на качество сна и утреннее самочувствие."
            )

        # Check calorie patterns
        recent_calories = [log.get('kbzhu', {}).get('calories', 0) for log in last_3_days if log.get('kbzhu')]
        if recent_calories:
            avg_recent = sum(recent_calories) / len(recent_calories)

            if avg_recent < 300:  # Very low average per meal
                insights.append("Последние дни калорийность приемов пищи была низкой. Убедитесь, что получаете достаточно энергии.")

            elif avg_recent > 800:  # High average per meal
                insights.append("Последние дни порции были довольно большими. Попробуйте есть медленнее и прислушиваться к насыщению.")

        return insights

    @staticmethod
    def _is_late_eating(timestamp_str: Optional[str]) -> bool:
        """Check if eating time is considered late (after 21:00)"""
        if not timestamp_str:
            return False
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.hour >= 21
        except Exception:
            return False

    @classmethod
    def _get_energy_pattern_insights(cls, nutrition_dna: NutritionDNA, day_of_week: int) -> List[str]:
        """Get insights based on energy patterns"""

        insights = []
        energy = nutrition_dna.energy_patterns

        # Morning appetite insights
        if energy.morning_appetite < 0.3 and day_of_week in [0, 1, 2, 3, 4]:  # Weekdays
            insights.append(
                f"Утром у вас обычно низкий аппетит. Попробуйте легкий белковый завтрак в "
                f"{energy.peak_hunger_time.strftime('%H:%M')} - время вашего пика голода."
            )

        # Evening comfort eating
        if energy.evening_comfort_eating > 0.5:
            insights.append(
                "Вечером вы склонны к комфортному питанию. Подготовьте здоровые альтернативы: "
                "ягоды, орехи или травяной чай с медом."
            )

        # Peak hunger timing
        peak_hour = energy.peak_hunger_time.hour
        if day_of_week in [5, 6] and 11 <= peak_hour <= 13:  # Weekend brunch time
            insights.append(
                f"В выходные ваш пик голода приходится на {energy.peak_hunger_time.strftime('%H:%M')}. "
                f"Идеальное время для полноценного бранча!"
            )

        return insights

    @classmethod
    def generate_weekly_insights(
        cls,
        nutrition_dna: NutritionDNA,
        week_start: date,
        week_logs: List[Dict[str, Any]] = None
    ) -> WeeklyInsight:
        """Generate comprehensive weekly insights and recommendations"""

        week_logs = week_logs or []

        # Generate day-specific insights for the week
        day_insights = {}
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for i, day_name in enumerate(day_names):
            daily_insights = cls.generate_daily_insights(nutrition_dna, week_start + timedelta(days=i), week_logs)
            if daily_insights:
                day_insights[day_name] = daily_insights[0]  # Top insight for each day

        # Observe patterns from the week
        observed_patterns = cls._analyze_weekly_patterns(nutrition_dna, week_logs)

        # Generate micro-goals
        micro_goals = cls._generate_micro_goals(nutrition_dna)

        # Predict risk days
        risk_days = cls._predict_risk_days(nutrition_dna)

        # Find opportunity moments
        opportunities = cls._find_opportunity_moments(nutrition_dna)

        return WeeklyInsight(
            week_start=week_start,
            day_insights=day_insights,
            observed_patterns=observed_patterns,
            micro_goals=micro_goals,
            risk_days=risk_days,
            opportunity_moments=opportunities
        )

    @classmethod
    def _analyze_weekly_patterns(cls, nutrition_dna: NutritionDNA, week_logs: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns observed during the week"""

        patterns = []

        # Weekend vs weekday analysis
        if nutrition_dna.social_patterns.weekend_indulgence_score > 0.4:
            patterns.append("Выходные значительно отличаются от будней по питанию")

        # Consistency patterns
        if nutrition_dna.consistency_score > 0.8:
            patterns.append("Очень стабильный режим питания в течение недели")
        elif nutrition_dna.consistency_score < 0.4:
            patterns.append("Режим питания довольно хаотичный, много вариативности")

        # Energy pattern observations
        if nutrition_dna.energy_patterns.evening_comfort_eating > 0.6:
            patterns.append("Склонность к комфортному питанию в вечерние часы")

        # Trigger frequency
        high_prob_triggers = [t for t in nutrition_dna.triggers if t.probability > 0.7]
        if high_prob_triggers:
            patterns.append(f"Сильные поведенческие триггеры: {len(high_prob_triggers)} выявлено")

        return patterns

    @classmethod
    def _generate_micro_goals(cls, nutrition_dna: NutritionDNA) -> List[str]:
        """Generate small, achievable goals for next week"""

        goals = []

        # Based on optimization zones
        for zone in nutrition_dna.optimization_zones:
            if zone.difficulty == "easy_wins":
                if zone.area == "fiber_intake":
                    goals.append("Добавить 1 овощ или фрукт к каждому основному приему пищи")
                elif zone.area == "protein_intake":
                    goals.append("Включить белковый компонент в завтрак 5 дней из 7")

        # Based on archetype
        if nutrition_dna.archetype == EatingPersonality.LATE_STARTER_IMPULSIVE:
            goals.append("Подготовить 3 здоровых снека в начале недели")

        elif nutrition_dna.archetype == EatingPersonality.STRESS_DRIVEN:
            goals.append("Попробовать 3 техники релаксации перед основными приемами пищи")

        elif nutrition_dna.archetype == EatingPersonality.WEEKEND_WARRIOR:
            goals.append("Сохранить один элемент здорового питания на выходных")

        # Temporal improvements
        if nutrition_dna.temporal_patterns.late_night_eating_frequency > 0.4:
            goals.append("Закончить последний прием пищи на 30 минут раньше 3 дня из 7")

        # Consistency improvements
        if nutrition_dna.consistency_score < 0.6:
            goals.append("Есть завтрак в одно и то же время 5 дней подряд")

        return goals[:4]  # Maximum 4 micro-goals

    @classmethod
    def _predict_risk_days(cls, nutrition_dna: NutritionDNA) -> List[str]:
        """Predict days with higher risk of poor food choices"""

        risk_days = []

        # Based on triggers
        for trigger in nutrition_dna.triggers:
            if trigger.probability > 0.6:
                trigger_name = trigger.trigger.lower()
                if 'monday' in trigger_name:
                    risk_days.append("monday - post-weekend adjustment")
                elif 'friday' in trigger_name:
                    risk_days.append("friday - end of week celebration")

        # Based on archetype patterns
        if nutrition_dna.archetype == EatingPersonality.WEEKEND_WARRIOR:
            risk_days.extend(["saturday - freedom mentality", "sunday - preparation anxiety"])

        elif nutrition_dna.archetype == EatingPersonality.STRESS_DRIVEN:
            risk_days.extend(["tuesday - midweek stress", "wednesday - week peak pressure"])

        elif nutrition_dna.archetype == EatingPersonality.SOCIAL_EATER:
            risk_days.extend(["friday - social dinner plans", "saturday - social events"])

        # Based on energy patterns
        if nutrition_dna.energy_patterns.evening_comfort_eating > 0.6:
            risk_days.append("daily evenings after 21:00")

        return list(set(risk_days))  # Remove duplicates

    @classmethod
    def _find_opportunity_moments(cls, nutrition_dna: NutritionDNA) -> List[str]:
        """Find optimal moments for positive changes"""

        opportunities = []

        # Based on success patterns
        for pattern in nutrition_dna.success_patterns:
            if pattern.correlation > 0.7:
                if "breakfast" in pattern.pattern.lower():
                    opportunities.append(f"Morning hours - leverage your {pattern.pattern}")
                elif "consistent" in pattern.pattern.lower():
                    opportunities.append("Midweek - build on your consistency strengths")

        # Based on archetype strengths
        if nutrition_dna.archetype == EatingPersonality.EARLY_BIRD_PLANNER:
            opportunities.append("Sunday evenings - meal prep for the week")
            opportunities.append("Early mornings - make healthy decisions while willpower is high")

        elif nutrition_dna.archetype == EatingPersonality.STRUCTURED_BALANCED:
            opportunities.append("Any day - your consistency allows for gradual improvements")

        elif nutrition_dna.archetype == EatingPersonality.SOCIAL_EATER:
            opportunities.append("Social meals - influence others toward healthy choices")

        # Based on energy patterns
        peak_hour = nutrition_dna.energy_patterns.peak_hunger_time.hour
        if 11 <= peak_hour <= 14:
            opportunities.append(f"Lunch time ({peak_hour}:00) - when you're naturally most hungry")

        # Based on temporal patterns
        if nutrition_dna.temporal_patterns.meal_timing_consistency > 0.7:
            opportunities.append("Regular meal times - your body expects food, perfect for introducing changes")

        return opportunities[:5]  # Top 5 opportunities