"""
Psychological eating profile analyzer.
Identifies emotional and psychological patterns in eating behavior.
"""
from __future__ import annotations

import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..models.nutrition_profile import (
    EatingPersonality, SocialEatingPattern, NutritionTrigger,
    SuccessPattern, OptimizationZone
)


class PsychologicalProfileAnalyzer:
    """Analyzes psychological and emotional eating patterns"""

    # Define trigger keywords that might indicate emotional eating
    STRESS_INDICATORS = ['busy', 'work', 'meeting', 'deadline', 'stress', 'tired']
    SOCIAL_INDICATORS = ['restaurant', 'cafe', 'party', 'dinner', 'friends', 'family']
    COMFORT_FOODS = ['chocolate', 'ice cream', 'pizza', 'cake', 'cookies', 'chips']

    @staticmethod
    def analyze_eating_frequency_by_day(food_logs: List[Dict[str, Any]]) -> Dict[int, float]:
        """Analyze eating frequency by day of week (0=Monday, 6=Sunday)"""
        day_counts = defaultdict(int)
        day_calories = defaultdict(list)

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                day_of_week = dt.weekday()
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

                day_counts[day_of_week] += 1
                day_calories[day_of_week].append(calories)

            except Exception as e:
                logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
                continue

        # Calculate average daily intake
        day_patterns = {}
        for day in range(7):
            avg_frequency = day_counts.get(day, 0)
            avg_calories = statistics.mean(day_calories[day]) if day_calories[day] else 0
            day_patterns[day] = {
                'frequency': avg_frequency,
                'avg_calories': avg_calories
            }

        return day_patterns

    @classmethod
    def detect_eating_personality(cls, food_logs: List[Dict[str, Any]], temporal_consistency: float) -> EatingPersonality:
        """Detect user's eating personality archetype"""

        day_patterns = cls.analyze_eating_frequency_by_day(food_logs)

        # Calculate metrics
        weekday_avg = statistics.mean([day_patterns[i]['avg_calories'] for i in range(5)])
        weekend_avg = statistics.mean([day_patterns[i]['avg_calories'] for i in range(5, 7)])
        weekend_ratio = weekend_avg / weekday_avg if weekday_avg > 0 else 1

        morning_logs = cls._count_logs_in_timeframe(food_logs, 5, 11)
        late_logs = cls._count_logs_in_timeframe(food_logs, 21, 24)
        total_logs = len(food_logs)

        morning_ratio = morning_logs / max(total_logs, 1)
        late_ratio = late_logs / max(total_logs, 1)

        # Social eating indicators
        social_score = cls._calculate_social_eating_score(food_logs)

        # Determine personality
        if morning_ratio > 0.3 and temporal_consistency > 0.7:
            return EatingPersonality.EARLY_BIRD_PLANNER
        elif morning_ratio < 0.1 and late_ratio > 0.2:
            return EatingPersonality.LATE_STARTER_IMPULSIVE
        elif temporal_consistency > 0.8 and abs(weekend_ratio - 1.0) < 0.2:
            return EatingPersonality.STRUCTURED_BALANCED
        elif weekend_ratio > 1.5:
            return EatingPersonality.WEEKEND_WARRIOR
        elif social_score > 0.4:
            return EatingPersonality.SOCIAL_EATER
        elif late_ratio > 0.3 or weekend_ratio > 1.3:
            return EatingPersonality.STRESS_DRIVEN
        elif temporal_consistency < 0.5:
            return EatingPersonality.BUSY_PROFESSIONAL
        else:
            return EatingPersonality.INTUITIVE_GRAZER

    @staticmethod
    def _count_logs_in_timeframe(logs: List[Dict[str, Any]], start_hour: int, end_hour: int) -> int:
        """Count logs within specific hour range"""
        count = 0
        for log in logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if start_hour <= dt.hour < end_hour:
                    count += 1
            except Exception:
                continue

        return count

    @staticmethod
    def _calculate_social_eating_score(logs: List[Dict[str, Any]]) -> float:
        """Calculate how much user eats in social contexts"""
        # This is a simplified implementation
        # In real system, this could use location data, restaurant detection, etc.

        social_indicators = 0
        total_logs = len(logs)

        for log in logs:
            metadata = log.get('metadata', {})
            if metadata:
                # Look for social indicators in metadata
                description = str(metadata).lower()
                if any(indicator in description for indicator in PsychologicalProfileAnalyzer.SOCIAL_INDICATORS):
                    social_indicators += 1

        return social_indicators / max(total_logs, 1)

    @classmethod
    def analyze_social_eating_patterns(cls, food_logs: List[Dict[str, Any]]) -> SocialEatingPattern:
        """Analyze social and contextual eating behaviors"""

        day_patterns = cls.analyze_eating_frequency_by_day(food_logs)

        # Weekend vs weekday indulgence
        weekday_calories = [day_patterns[i]['avg_calories'] for i in range(5)]
        weekend_calories = [day_patterns[i]['avg_calories'] for i in range(5, 7)]

        weekday_avg = statistics.mean(weekday_calories) if weekday_calories else 0
        weekend_avg = statistics.mean(weekend_calories) if weekend_calories else 0

        weekend_indulgence = min(1.0, (weekend_avg - weekday_avg) / max(weekday_avg, 1))
        weekend_indulgence = max(0.0, weekend_indulgence)  # Ensure non-negative

        # Work stress snacking (simplified - based on weekday frequency vs meal times)
        work_hours_logs = cls._count_logs_in_timeframe(food_logs, 9, 17)
        total_logs = len(food_logs)
        work_stress_score = min(1.0, work_hours_logs / max(total_logs, 1) * 2)  # Amplify signal

        # Social eating score
        social_score = cls._calculate_social_eating_score(food_logs)

        # Planning score (based on meal timing consistency)
        meal_times = []
        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    meal_times.append(dt.hour)
                except Exception:
                    continue

        if len(meal_times) > 1:
            time_std = statistics.stdev(meal_times)
            planning_score = max(0.0, 1.0 - (time_std / 12))  # 12 hours std = 0 planning
        else:
            planning_score = 0.5

        return SocialEatingPattern(
            weekend_indulgence_score=weekend_indulgence,
            work_stress_snacking=work_stress_score,
            restaurant_frequency=social_score,
            social_meal_impact=social_score,
            planning_score=planning_score
        )

    @classmethod
    def identify_triggers(cls, food_logs: List[Dict[str, Any]]) -> List[NutritionTrigger]:
        """Identify behavioral triggers from food logs"""
        triggers = []

        # Analyze by day of week
        day_patterns = cls.analyze_eating_frequency_by_day(food_logs)

        # Monday trigger (post-weekend)
        monday_calories = day_patterns.get(0, {}).get('avg_calories', 0)
        sunday_calories = day_patterns.get(6, {}).get('avg_calories', 0)

        if monday_calories > 0 and sunday_calories > 0:
            monday_ratio = monday_calories / sunday_calories
            if monday_ratio > 1.2:
                triggers.append(NutritionTrigger(
                    trigger="monday_compensation",
                    food_response="higher_calorie_intake",
                    probability=min(0.8, (monday_ratio - 1.0) / 0.5)
                ))

        # Friday trigger (pre-weekend)
        friday_calories = day_patterns.get(4, {}).get('avg_calories', 0)
        weekday_avg = statistics.mean([day_patterns[i].get('avg_calories', 0) for i in range(4)])

        if friday_calories > 0 and weekday_avg > 0:
            friday_ratio = friday_calories / weekday_avg
            if friday_ratio > 1.15:
                triggers.append(NutritionTrigger(
                    trigger="friday_celebration",
                    food_response="increased_intake",
                    probability=min(0.7, (friday_ratio - 1.0) / 0.3)
                ))

        # Late night eating trigger
        late_logs = cls._count_logs_in_timeframe(food_logs, 21, 24)
        if late_logs > 0:
            late_probability = min(0.9, late_logs / max(len(food_logs), 1) * 3)
            triggers.append(NutritionTrigger(
                trigger="evening_hunger",
                food_response="late_night_snacking",
                probability=late_probability,
                time_of_day=datetime.strptime("22:00", "%H:%M").time()
            ))

        return triggers

    @classmethod
    def identify_success_patterns(cls, food_logs: List[Dict[str, Any]], user_goal: str = None) -> List[SuccessPattern]:
        """Identify patterns that correlate with user's success"""
        patterns = []

        # Morning eating success
        morning_logs = cls._count_logs_in_timeframe(food_logs, 6, 10)
        total_logs = len(food_logs)

        if morning_logs / max(total_logs, 1) > 0.3:
            patterns.append(SuccessPattern(
                pattern="regular_breakfast",
                outcome="stable_energy_levels",
                correlation=0.8
            ))

        # Consistent timing success
        meal_times = []
        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    meal_times.append(dt.hour)
                except Exception:
                    continue

        if len(meal_times) > 3:
            time_consistency = 1.0 - min(1.0, statistics.stdev(meal_times) / 12)
            if time_consistency > 0.7:
                patterns.append(SuccessPattern(
                    pattern="consistent_meal_timing",
                    outcome="better_appetite_control",
                    correlation=time_consistency
                ))

        # Weekday discipline success
        day_patterns = cls.analyze_eating_frequency_by_day(food_logs)
        weekday_consistency = statistics.stdev([
            day_patterns[i].get('avg_calories', 0) for i in range(5)
        ]) if len([day_patterns[i].get('avg_calories', 0) for i in range(5)]) > 1 else 0

        if weekday_consistency < 200:  # Low standard deviation in weekday calories
            patterns.append(SuccessPattern(
                pattern="weekday_consistency",
                outcome="steady_progress",
                correlation=0.75
            ))

        return patterns

    @classmethod
    def identify_optimization_zones(cls, food_logs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> List[OptimizationZone]:
        """Identify areas for nutrition optimization"""
        zones = []

        # Analyze current nutrition distribution
        total_protein = sum(log.get('kbzhu', {}).get('protein', 0) for log in food_logs if log.get('kbzhu'))
        total_fiber = sum(log.get('kbzhu', {}).get('fiber', 0) for log in food_logs if log.get('kbzhu'))
        total_calories = sum(log.get('kbzhu', {}).get('calories', 0) for log in food_logs if log.get('kbzhu'))

        days_with_data = len(set(
            log.get('timestamp', '')[:10] for log in food_logs if log.get('timestamp')
        ))
        days_with_data = max(days_with_data, 1)

        avg_daily_protein = total_protein / days_with_data
        avg_daily_fiber = total_fiber / days_with_data
        avg_daily_calories = total_calories / days_with_data

        # Protein optimization
        target_weight = user_profile.get('weight_kg', 70) if user_profile else 70
        target_protein = target_weight * 1.2  # 1.2g per kg body weight

        protein_score = min(1.0, avg_daily_protein / target_protein)
        if protein_score < 0.8:
            zones.append(OptimizationZone(
                area="protein_intake",
                difficulty="moderate_effort",
                impact="high",
                current_score=protein_score,
                target_score=0.9
            ))

        # Fiber optimization
        target_fiber = 25  # grams per day
        fiber_score = min(1.0, avg_daily_fiber / target_fiber)
        if fiber_score < 0.6:
            zones.append(OptimizationZone(
                area="fiber_intake",
                difficulty="easy_wins",
                impact="medium",
                current_score=fiber_score,
                target_score=0.8
            ))

        # Meal timing optimization
        late_eating = cls._count_logs_in_timeframe(food_logs, 21, 24) / max(len(food_logs), 1)
        if late_eating > 0.3:
            zones.append(OptimizationZone(
                area="meal_timing",
                difficulty="requires_strategy",
                impact="medium",
                current_score=1.0 - late_eating,
                target_score=0.9
            ))

        # Weekend consistency optimization
        day_patterns = cls.analyze_eating_frequency_by_day(food_logs)
        weekday_avg = statistics.mean([day_patterns[i]['avg_calories'] for i in range(5)])
        weekend_avg = statistics.mean([day_patterns[i]['avg_calories'] for i in range(5, 7)])

        consistency_score = 1.0 - min(1.0, abs(weekend_avg - weekday_avg) / max(weekday_avg, 1))
        if consistency_score < 0.7:
            zones.append(OptimizationZone(
                area="weekend_consistency",
                difficulty="requires_strategy",
                impact="medium",
                current_score=consistency_score,
                target_score=0.8
            ))

        return zones

    @classmethod
    def generate_psychological_insights(cls, personality: EatingPersonality, social_patterns: SocialEatingPattern) -> List[str]:
        """Generate psychological insights based on eating patterns"""
        insights = []

        # Personality-specific insights
        if personality == EatingPersonality.EARLY_BIRD_PLANNER:
            insights.append("Вы дисциплинированы в утренние часы - используйте это для приготовления здоровых обедов и ужинов заранее.")

        elif personality == EatingPersonality.LATE_STARTER_IMPULSIVE:
            insights.append("Вы часто принимаете спонтанные решения о еде. Заготовьте здоровые снеки, чтобы избежать импульсивных выборов.")

        elif personality == EatingPersonality.STRESS_DRIVEN:
            insights.append("Стресс влияет на ваши пищевые привычки. Попробуйте техники релаксации перед едой.")

        elif personality == EatingPersonality.SOCIAL_EATER:
            insights.append("Вы часто едите в социальных ситуациях. Заранее планируйте выбор блюд в ресторанах.")

        elif personality == EatingPersonality.WEEKEND_WARRIOR:
            insights.append("В выходные ваш режим кардинально меняется. Попробуйте найти баланс между отдыхом и здоровыми привычками.")

        # Social pattern insights
        if social_patterns.weekend_indulgence_score > 0.3:
            insights.append("В выходные вы позволяете себе больше - это нормально, но следите за размером порций.")

        if social_patterns.work_stress_snacking > 0.4:
            insights.append("Рабочий стресс провоцирует перекусы. Держите здоровые альтернативы на рабочем месте.")

        if social_patterns.planning_score < 0.5:
            insights.append("Планирование питания поможет вам достичь целей быстрее. Попробуйте готовить на выходных на всю неделю.")

        return insights