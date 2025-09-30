"""
Temporal eating patterns analyzer.
Analyzes when users eat and identifies time-based patterns and insights.
"""
from __future__ import annotations

import statistics
from collections import defaultdict, Counter
from datetime import datetime, time, timedelta, date
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..models.nutrition_profile import TemporalPattern, EnergyPattern


class TemporalPatternsAnalyzer:
    """Analyzes user's eating patterns across time dimensions"""

    @staticmethod
    def extract_meal_times(food_logs: List[Dict[str, Any]]) -> Dict[str, List[time]]:
        """Extract meal times by type from food logs"""
        meal_times = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                meal_time = dt.time()

                # Classify meal type based on time
                hour = dt.hour
                if 5 <= hour < 11:
                    meal_times['breakfast'].append(meal_time)
                elif 11 <= hour < 16:
                    meal_times['lunch'].append(meal_time)
                elif 18 <= hour < 23:
                    meal_times['dinner'].append(meal_time)
                else:
                    meal_times['snack'].append(meal_time)

            except Exception as e:
                logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
                continue

        return meal_times

    @staticmethod
    def calculate_average_time(times: List[time]) -> Optional[time]:
        """Calculate average time from list of time objects"""
        if not times:
            return None

        # Convert times to minutes since midnight
        minutes = []
        for t in times:
            total_minutes = t.hour * 60 + t.minute
            minutes.append(total_minutes)

        avg_minutes = int(statistics.mean(minutes))
        hours = avg_minutes // 60
        mins = avg_minutes % 60

        return time(hours % 24, mins)

    @staticmethod
    def calculate_time_consistency(times: List[time]) -> float:
        """Calculate consistency score (0-1) for meal times"""
        if len(times) < 2:
            return 1.0

        # Convert to minutes and calculate standard deviation
        minutes = [t.hour * 60 + t.minute for t in times]

        try:
            std_dev = statistics.stdev(minutes)
            # Normalize to 0-1 scale (4 hours std = 0 consistency)
            consistency = max(0, 1 - (std_dev / 240))  # 240 minutes = 4 hours
            return consistency
        except statistics.StatisticsError:
            return 1.0

    @staticmethod
    def analyze_weekend_vs_weekday(food_logs: List[Dict[str, Any]]) -> Tuple[float, Dict[str, float]]:
        """Analyze differences between weekend and weekday eating"""
        weekday_times = []
        weekend_times = []
        weekday_calories = []
        weekend_calories = []

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

                if dt.weekday() < 5:  # Monday = 0, Sunday = 6
                    weekday_times.append(dt.hour)
                    weekday_calories.append(calories)
                else:
                    weekend_times.append(dt.hour)
                    weekend_calories.append(calories)

            except Exception as e:
                logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
                continue

        # Calculate shift in meal times
        weekday_avg_hour = statistics.mean(weekday_times) if weekday_times else 12
        weekend_avg_hour = statistics.mean(weekend_times) if weekend_times else 12
        time_shift = abs(weekend_avg_hour - weekday_avg_hour)

        # Calculate calorie difference
        weekday_avg_cal = statistics.mean(weekday_calories) if weekday_calories else 0
        weekend_avg_cal = statistics.mean(weekend_calories) if weekend_calories else 0
        calorie_ratio = weekend_avg_cal / weekday_avg_cal if weekday_avg_cal > 0 else 1

        return time_shift, {
            'weekday_avg_hour': weekday_avg_hour,
            'weekend_avg_hour': weekend_avg_hour,
            'weekday_avg_calories': weekday_avg_cal,
            'weekend_avg_calories': weekend_avg_cal,
            'calorie_ratio': calorie_ratio
        }

    @classmethod
    def analyze_temporal_patterns(cls, food_logs: List[Dict[str, Any]]) -> TemporalPattern:
        """Generate complete temporal pattern analysis"""

        # Extract meal times
        meal_times = cls.extract_meal_times(food_logs)

        # Calculate preferred meal times
        preferred_breakfast = cls.calculate_average_time(meal_times['breakfast']) or time(8, 0)
        preferred_lunch = cls.calculate_average_time(meal_times['lunch']) or time(13, 0)
        preferred_dinner = cls.calculate_average_time(meal_times['dinner']) or time(19, 0)

        # Calculate consistency
        breakfast_consistency = cls.calculate_time_consistency(meal_times['breakfast'])
        lunch_consistency = cls.calculate_time_consistency(meal_times['lunch'])
        dinner_consistency = cls.calculate_time_consistency(meal_times['dinner'])

        overall_consistency = statistics.mean([
            breakfast_consistency, lunch_consistency, dinner_consistency
        ])

        # Weekend shift analysis
        weekend_shift, _ = cls.analyze_weekend_vs_weekday(food_logs)

        # Late night eating analysis
        late_night_count = 0
        total_logs = len(food_logs)

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if dt.hour >= 21:
                        late_night_count += 1
                except Exception:
                    continue

        late_night_frequency = late_night_count / max(total_logs, 1)

        return TemporalPattern(
            preferred_breakfast_time=preferred_breakfast,
            preferred_lunch_time=preferred_lunch,
            preferred_dinner_time=preferred_dinner,
            meal_timing_consistency=overall_consistency,
            weekend_shift_hours=weekend_shift,
            late_night_eating_frequency=late_night_frequency
        )

    @classmethod
    def analyze_energy_patterns(cls, food_logs: List[Dict[str, Any]]) -> EnergyPattern:
        """Analyze energy and appetite patterns throughout the day"""

        hourly_intake = defaultdict(list)

        # Group food by hour
        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0
                hourly_intake[dt.hour].append(calories)
            except Exception:
                continue

        # Calculate average intake by hour
        hourly_averages = {}
        for hour in range(24):
            if hour in hourly_intake:
                hourly_averages[hour] = statistics.mean(hourly_intake[hour])
            else:
                hourly_averages[hour] = 0

        # Find patterns
        morning_calories = sum(hourly_averages.get(h, 0) for h in range(6, 12))
        afternoon_calories = sum(hourly_averages.get(h, 0) for h in range(12, 18))
        evening_calories = sum(hourly_averages.get(h, 0) for h in range(18, 22))

        total_calories = morning_calories + afternoon_calories + evening_calories
        if total_calories == 0:
            total_calories = 1  # Avoid division by zero

        # Normalize to 0-1 scale
        morning_appetite = morning_calories / total_calories
        afternoon_hunger = afternoon_calories / total_calories
        evening_comfort = evening_calories / total_calories

        # Find peak times
        peak_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        lowest_hour = min(hourly_averages.keys(), key=lambda h: hourly_averages[h])

        return EnergyPattern(
            morning_appetite=min(morning_appetite, 1.0),
            afternoon_hunger=min(afternoon_hunger, 1.0),
            evening_comfort_eating=min(evening_comfort, 1.0),
            peak_hunger_time=time(peak_hour, 0),
            lowest_energy_time=time(lowest_hour, 0)
        )

    @classmethod
    def generate_temporal_insights(cls, patterns: TemporalPattern) -> List[str]:
        """Generate human-readable insights from temporal patterns"""
        insights = []

        # Breakfast timing insights
        breakfast_hour = patterns.preferred_breakfast_time.hour
        if breakfast_hour < 7:
            insights.append("Вы предпочитаете ранний завтрак - это отличная привычка для метаболизма!")
        elif breakfast_hour > 10:
            insights.append("Вы поздно завтракаете. Попробуйте сдвинуть завтрак пораньше для лучшего контроля аппетита в течение дня.")

        # Consistency insights
        if patterns.meal_timing_consistency > 0.8:
            insights.append("У вас очень стабильный режим питания - это способствует хорошему пищеварению.")
        elif patterns.meal_timing_consistency < 0.5:
            insights.append("Режим питания довольно хаотичный. Стабильные время приёмов пищи помогут улучшить результаты.")

        # Weekend patterns
        if patterns.weekend_shift_hours > 2:
            insights.append(f"В выходные ваш режим сдвигается на {patterns.weekend_shift_hours:.1f} часов. Это может влиять на энергию в понедельник.")

        # Late night eating
        if patterns.late_night_eating_frequency > 0.3:
            insights.append("Часто едите поздно вечером. Попробуйте завершать приёмы пищи за 3 часа до сна.")

        return insights

    @classmethod
    def get_day_specific_recommendations(cls, patterns: TemporalPattern, day_of_week: int) -> str:
        """Get day-specific recommendations based on patterns"""

        day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        day_name = day_names[day_of_week]

        if day_of_week == 0:  # Monday
            if patterns.weekend_shift_hours > 1:
                return f"{day_name}: После выходных восстанавливаем режим. Завтрак в {patterns.preferred_breakfast_time.strftime('%H:%M')} поможет настроиться на рабочую неделю."
            else:
                return f"{day_name}: Начинаем неделю с правильного завтрака. Ваше обычное время - {patterns.preferred_breakfast_time.strftime('%H:%M')}."

        elif day_of_week == 4:  # Friday
            return f"{day_name}: День часто проходит в предвкушении выходных. Помните о балансе - не переедайте вечером."

        elif day_of_week in [5, 6]:  # Weekend
            if patterns.weekend_shift_hours > 1:
                return f"{day_name}: Выходной день. Можно немного сдвинуть режим, но не забывайте о регулярности питания."
            else:
                return f"{day_name}: Отличная возможность готовить более сложные и полезные блюда."

        else:  # Tuesday-Thursday
            if patterns.meal_timing_consistency > 0.7:
                return f"{day_name}: Середина недели - поддерживаем стабильный ритм питания."
            else:
                return f"{day_name}: Хороший день для упорядочивания режима питания."

        return f"{day_name}: Следуйте привычному режиму питания."