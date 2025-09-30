"""
Contextual Analysis Engine.
Analyzes external factors that influence eating behavior: weather, location, social context, time, etc.
"""
from __future__ import annotations

import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta, date, time
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..models.nutrition_profile import NutritionDNA


class ContextualAnalyzer:
    """
    Analyzes how external context affects eating patterns and provides context-aware insights.
    """

    # Context influence weights - how much different factors affect eating behavior
    CONTEXT_WEIGHTS = {
        'weather': {
            'cold': {'comfort_eating': 1.3, 'warm_foods': 1.5, 'calories': 1.1},
            'hot': {'light_eating': 1.4, 'cold_foods': 1.3, 'hydration': 1.6},
            'rainy': {'comfort_eating': 1.4, 'indoor_cooking': 1.2, 'snacking': 1.2},
            'sunny': {'fresh_foods': 1.2, 'outdoor_eating': 1.3, 'salads': 1.4}
        },
        'time_of_day': {
            'morning': {'light_foods': 1.2, 'caffeine': 1.5, 'quick_prep': 1.3},
            'afternoon': {'energy_foods': 1.4, 'protein': 1.3, 'substantial_meals': 1.2},
            'evening': {'comfort_foods': 1.2, 'relaxing_meals': 1.3, 'lighter_portions': 1.1},
            'late_night': {'snacking': 1.8, 'comfort_foods': 1.6, 'emotional_eating': 1.4}
        },
        'social_context': {
            'alone': {'quick_meals': 1.3, 'simple_prep': 1.4, 'snacking': 1.2},
            'family': {'hearty_meals': 1.3, 'traditional_foods': 1.2, 'sharing': 1.4},
            'friends': {'indulgent_foods': 1.4, 'restaurant_eating': 1.6, 'alcohol': 1.3},
            'work': {'convenient_foods': 1.5, 'desk_eating': 1.3, 'stress_eating': 1.2}
        },
        'location': {
            'home': {'home_cooking': 1.4, 'comfort_foods': 1.2, 'healthy_options': 1.3},
            'office': {'convenience_foods': 1.4, 'snacking': 1.3, 'irregular_timing': 1.2},
            'restaurant': {'indulgence': 1.5, 'larger_portions': 1.3, 'social_pressure': 1.2},
            'travel': {'irregular_eating': 1.6, 'fast_food': 1.4, 'convenience': 1.5}
        }
    }

    @classmethod
    def analyze_context_impact(
        cls,
        food_logs: List[Dict[str, Any]],
        context_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze how different contexts impact eating behavior"""

        context_data = context_data or []

        # Group logs by context factors
        weather_patterns = cls._analyze_weather_impact(food_logs, context_data)
        time_patterns = cls._analyze_time_impact(food_logs)
        social_patterns = cls._analyze_social_impact(food_logs)
        location_patterns = cls._analyze_location_impact(food_logs)

        # Identify strongest context influences
        strong_influences = cls._identify_strong_influences({
            'weather': weather_patterns,
            'time': time_patterns,
            'social': social_patterns,
            'location': location_patterns
        })

        return {
            'weather_impact': weather_patterns,
            'time_impact': time_patterns,
            'social_impact': social_patterns,
            'location_impact': location_patterns,
            'strongest_influences': strong_influences,
            'context_score': cls._calculate_context_sensitivity(food_logs)
        }

    @classmethod
    def _analyze_weather_impact(
        cls,
        food_logs: List[Dict[str, Any]],
        context_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how weather affects eating patterns"""

        weather_eating = defaultdict(list)

        # Create a mapping of dates to weather
        weather_by_date = {}
        for context in context_data:
            context_date = context.get('date')
            weather = context.get('weather', '').lower()
            if context_date and weather:
                weather_by_date[context_date] = weather

        # Group eating by weather conditions
        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                log_date = dt.date().isoformat()

                weather = weather_by_date.get(log_date, 'unknown')
                if weather != 'unknown':
                    calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0
                    hour = dt.hour

                    weather_eating[weather].append({
                        'calories': calories,
                        'hour': hour,
                        'log': log
                    })
            except Exception:
                continue

        # Analyze patterns
        weather_analysis = {}

        for weather_type, eating_data in weather_eating.items():
            if len(eating_data) < 3:  # Need minimum data points
                continue

            calories = [d['calories'] for d in eating_data if d['calories'] > 0]
            hours = [d['hour'] for d in eating_data]

            avg_calories = statistics.mean(calories) if calories else 0
            avg_hour = statistics.mean(hours) if hours else 12

            weather_analysis[weather_type] = {
                'avg_calories_per_meal': avg_calories,
                'avg_eating_hour': avg_hour,
                'meal_count': len(eating_data),
                'calorie_variance': statistics.stdev(calories) if len(calories) > 1 else 0
            }

        return weather_analysis

    @classmethod
    def _analyze_time_impact(cls, food_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how time of day affects eating patterns"""

        time_periods = {
            'early_morning': (5, 8),
            'morning': (8, 12),
            'afternoon': (12, 17),
            'evening': (17, 21),
            'late_night': (21, 24)
        }

        period_eating = defaultdict(list)

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                hour = dt.hour
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

                for period_name, (start_hour, end_hour) in time_periods.items():
                    if start_hour <= hour < end_hour:
                        period_eating[period_name].append({
                            'calories': calories,
                            'hour': hour,
                            'weekday': dt.weekday()
                        })
                        break
            except Exception:
                continue

        # Analyze patterns by time period
        time_analysis = {}

        for period, eating_data in period_eating.items():
            if not eating_data:
                continue

            calories = [d['calories'] for d in eating_data if d['calories'] > 0]

            time_analysis[period] = {
                'frequency': len(eating_data),
                'avg_calories': statistics.mean(calories) if calories else 0,
                'weekday_frequency': len([d for d in eating_data if d['weekday'] < 5]),
                'weekend_frequency': len([d for d in eating_data if d['weekday'] >= 5])
            }

        return time_analysis

    @classmethod
    def _analyze_social_impact(cls, food_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze impact of social context on eating"""

        # This is simplified - in real implementation would use more sophisticated
        # detection of social context from metadata, location data, etc.

        social_indicators = {
            'restaurant': ['restaurant', 'cafe', 'dinner out', 'eating out'],
            'work': ['office', 'work', 'lunch meeting', 'desk'],
            'home_alone': ['home', 'alone', 'quick', 'simple'],
            'social': ['friends', 'party', 'celebration', 'group']
        }

        social_eating = defaultdict(list)

        for log in food_logs:
            metadata = log.get('metadata', {})
            metadata_str = str(metadata).lower() if metadata else ''

            calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

            # Try to classify social context
            context_found = False
            for context, keywords in social_indicators.items():
                if any(keyword in metadata_str for keyword in keywords):
                    social_eating[context].append(calories)
                    context_found = True
                    break

            if not context_found:
                social_eating['unknown'].append(calories)

        # Analyze social patterns
        social_analysis = {}

        for context, calories_list in social_eating.items():
            if len(calories_list) < 2:
                continue

            valid_calories = [c for c in calories_list if c > 0]
            if valid_calories:
                social_analysis[context] = {
                    'frequency': len(calories_list),
                    'avg_calories': statistics.mean(valid_calories),
                    'max_calories': max(valid_calories),
                    'calorie_variance': statistics.stdev(valid_calories) if len(valid_calories) > 1 else 0
                }

        return social_analysis

    @classmethod
    def _analyze_location_impact(cls, food_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how location affects eating patterns"""

        # Simplified location analysis based on metadata keywords
        location_indicators = {
            'home': ['home', 'kitchen', 'house'],
            'work': ['office', 'work', 'workplace'],
            'restaurant': ['restaurant', 'cafe', 'bar'],
            'travel': ['airport', 'hotel', 'trip', 'vacation']
        }

        location_eating = defaultdict(list)

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            metadata = log.get('metadata', {})
            metadata_str = str(metadata).lower() if metadata else ''

            calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                hour = dt.hour
            except Exception:
                hour = 12  # Default

            # Classify location
            for location, keywords in location_indicators.items():
                if any(keyword in metadata_str for keyword in keywords):
                    location_eating[location].append({
                        'calories': calories,
                        'hour': hour
                    })
                    break

        # Analyze location patterns
        location_analysis = {}

        for location, eating_data in location_eating.items():
            if len(eating_data) < 2:
                continue

            calories = [d['calories'] for d in eating_data if d['calories'] > 0]
            hours = [d['hour'] for d in eating_data]

            if calories:
                location_analysis[location] = {
                    'frequency': len(eating_data),
                    'avg_calories': statistics.mean(calories),
                    'avg_hour': statistics.mean(hours),
                    'time_consistency': 1.0 - (statistics.stdev(hours) / 12) if len(hours) > 1 else 1.0
                }

        return location_analysis

    @classmethod
    def _identify_strong_influences(cls, all_patterns: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify which contextual factors have the strongest influence"""

        influences = []

        # Weather influences
        weather_patterns = all_patterns.get('weather', {})
        if len(weather_patterns) >= 2:
            # Compare calorie differences between weather conditions
            weather_calories = {w: data['avg_calories_per_meal'] for w, data in weather_patterns.items()}
            if weather_calories:
                max_cal = max(weather_calories.values())
                min_cal = min(weather_calories.values())
                if max_cal > 0 and (max_cal - min_cal) / max_cal > 0.2:  # 20% difference
                    influences.append({
                        'type': 'weather',
                        'strength': (max_cal - min_cal) / max_cal,
                        'description': f"Погода влияет на калорийность питания до {((max_cal - min_cal) / max_cal * 100):.0f}%"
                    })

        # Time influences
        time_patterns = all_patterns.get('time', {})
        if time_patterns:
            time_frequencies = {t: data['frequency'] for t, data in time_patterns.items()}
            max_freq = max(time_frequencies.values()) if time_frequencies else 0
            min_freq = min(time_frequencies.values()) if time_frequencies else 0

            if max_freq > 0 and (max_freq - min_freq) / max_freq > 0.5:
                influences.append({
                    'type': 'time_preference',
                    'strength': (max_freq - min_freq) / max_freq,
                    'description': f"Сильные временные предпочтения в питании"
                })

        # Social influences
        social_patterns = all_patterns.get('social', {})
        if len(social_patterns) >= 2:
            social_calories = {s: data['avg_calories'] for s, data in social_patterns.items()}
            if social_calories:
                max_social_cal = max(social_calories.values())
                min_social_cal = min(social_calories.values())
                if max_social_cal > 0 and (max_social_cal - min_social_cal) / max_social_cal > 0.3:
                    influences.append({
                        'type': 'social_context',
                        'strength': (max_social_cal - min_social_cal) / max_social_cal,
                        'description': f"Социальный контекст значительно влияет на размер порций"
                    })

        # Sort by strength
        influences.sort(key=lambda x: x['strength'], reverse=True)
        return influences[:3]  # Top 3 influences

    @classmethod
    def _calculate_context_sensitivity(cls, food_logs: List[Dict[str, Any]]) -> float:
        """Calculate how sensitive user is to contextual changes"""

        if len(food_logs) < 10:
            return 0.5  # Not enough data

        # Analyze variance in eating patterns across different times and days
        hourly_eating = defaultdict(list)
        daily_eating = defaultdict(list)

        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                calories = log.get('kbzhu', {}).get('calories', 0) if log.get('kbzhu') else 0

                if calories > 0:
                    hourly_eating[dt.hour].append(calories)
                    daily_eating[dt.weekday()].append(calories)

            except Exception:
                continue

        # Calculate consistency scores
        hourly_consistency = 0
        if len(hourly_eating) > 1:
            hourly_variances = []
            for hour_calories in hourly_eating.values():
                if len(hour_calories) > 1:
                    hourly_variances.append(statistics.stdev(hour_calories))

            if hourly_variances:
                avg_hourly_variance = statistics.mean(hourly_variances)
                hourly_consistency = max(0, 1 - (avg_hourly_variance / 500))  # Normalize

        daily_consistency = 0
        if len(daily_eating) > 1:
            daily_averages = [statistics.mean(day_calories) for day_calories in daily_eating.values() if day_calories]
            if len(daily_averages) > 1:
                daily_variance = statistics.stdev(daily_averages)
                daily_consistency = max(0, 1 - (daily_variance / 300))  # Normalize

        # Overall context sensitivity (lower consistency = higher sensitivity)
        context_sensitivity = 1 - statistics.mean([hourly_consistency, daily_consistency])
        return max(0.1, min(context_sensitivity, 0.9))

    @classmethod
    def get_contextual_recommendations(
        cls,
        context_analysis: Dict[str, Any],
        nutrition_dna: NutritionDNA,
        current_context: Dict[str, Any] = None
    ) -> List[str]:
        """Generate recommendations based on contextual analysis"""

        recommendations = []
        current_context = current_context or {}

        strong_influences = context_analysis.get('strongest_influences', [])

        # Recommendations based on strong influences
        for influence in strong_influences:
            influence_type = influence['type']

            if influence_type == 'weather':
                recommendations.append(
                    "Погода сильно влияет на ваше питание. Планируйте меню с учетом прогноза погоды."
                )
            elif influence_type == 'social_context':
                recommendations.append(
                    "В социальных ситуациях вы едите иначе. Подготавливайтесь к встречам заранее."
                )
            elif influence_type == 'time_preference':
                recommendations.append(
                    "У вас четкие временные предпочтения в еде. Используйте это для планирования режима."
                )

        # Current context recommendations
        current_weather = current_context.get('weather', '').lower()
        if 'cold' in current_weather or 'rain' in current_weather:
            recommendations.append(
                "Холодная/дождливая погода может вызвать желание комфортной еды. "
                "Приготовьте теплые здоровые блюда."
            )
        elif 'hot' in current_weather:
            recommendations.append(
                "Жаркая погода - время для легких блюд и увеличения потребления жидкости."
            )

        # Social context recommendations
        social_situation = current_context.get('social_context')
        if social_situation == 'restaurant':
            recommendations.append(
                "В ресторане легко переесть. Изучите меню заранее и выберите здоровые опции."
            )
        elif social_situation == 'work':
            recommendations.append(
                "Рабочий день может нарушить режим питания. Подготовьте здоровые снеки заранее."
            )

        # Time-based recommendations
        current_time = current_context.get('current_time', datetime.now().time())
        if current_time.hour >= 21:
            recommendations.append(
                "Поздний час - время легких блюд или травяного чая вместо полноценного приема пищи."
            )

        # Context sensitivity recommendations
        context_score = context_analysis.get('context_score', 0.5)
        if context_score > 0.7:
            recommendations.append(
                "Вы очень чувствительны к внешним факторам. Развивайте навыки mindful eating."
            )
        elif context_score < 0.3:
            recommendations.append(
                "У вас стабильные пищевые привычки независимо от контекста - это большое преимущество!"
            )

        return recommendations[:4]  # Maximum 4 recommendations

    @classmethod
    def predict_context_response(
        cls,
        nutrition_dna: NutritionDNA,
        context_analysis: Dict[str, Any],
        predicted_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict how user will respond to specific context"""

        predictions = {}

        # Weather response prediction
        weather = predicted_context.get('weather', '').lower()
        if weather and 'weather' in context_analysis.get('weather_impact', {}):
            weather_patterns = context_analysis['weather_impact']

            if weather in weather_patterns:
                historical_pattern = weather_patterns[weather]
                predictions['expected_calories_change'] = (
                    historical_pattern['avg_calories_per_meal'] /
                    statistics.mean([p['avg_calories_per_meal'] for p in weather_patterns.values()])
                )
                predictions['expected_timing_shift'] = historical_pattern.get('avg_eating_hour', 12) - 12

        # Social context prediction
        social_context = predicted_context.get('social_context')
        if social_context and 'social' in context_analysis.get('social_impact', {}):
            social_patterns = context_analysis['social_impact']

            if social_context in social_patterns:
                historical_social = social_patterns[social_context]
                baseline_calories = statistics.mean([
                    p['avg_calories'] for p in social_patterns.values()
                ])
                predictions['social_calorie_multiplier'] = (
                    historical_social['avg_calories'] / baseline_calories
                )

        # Archetype-specific context predictions
        archetype_responses = {
            'stress_driven': {
                'high_stress': {'overeating_risk': 0.8, 'comfort_food_craving': 0.9},
                'cold_weather': {'comfort_eating': 0.7}
            },
            'social_eater': {
                'social_gathering': {'portion_increase': 1.4, 'indulgence_risk': 0.8},
                'eating_alone': {'undereating_risk': 0.6}
            },
            'busy_professional': {
                'work_stress': {'meal_skipping': 0.7, 'fast_food': 0.8},
                'weekend': {'meal_planning_improvement': 0.6}
            }
        }

        archetype_key = nutrition_dna.archetype.value.lower()
        if archetype_key in archetype_responses:
            archetype_predictions = archetype_responses[archetype_key]

            for context_key, response in archetype_predictions.items():
                if any(context_key in str(v).lower() for v in predicted_context.values()):
                    predictions.update(response)

        return predictions

    @classmethod
    def generate_context_insights(
        cls,
        context_analysis: Dict[str, Any],
        nutrition_dna: NutritionDNA
    ) -> List[str]:
        """Generate insights about how context affects user's eating"""

        insights = []

        # Weather insights
        weather_impact = context_analysis.get('weather_impact', {})
        if len(weather_impact) >= 2:
            weather_calories = {w: data['avg_calories_per_meal'] for w, data in weather_impact.items()}
            max_weather = max(weather_calories.keys(), key=lambda x: weather_calories[x])
            min_weather = min(weather_calories.keys(), key=lambda x: weather_calories[x])

            if weather_calories[max_weather] > weather_calories[min_weather] * 1.2:
                insights.append(
                    f"В {max_weather} погоду вы едите на {((weather_calories[max_weather] / weather_calories[min_weather] - 1) * 100):.0f}% больше, чем в {min_weather}"
                )

        # Time patterns insights
        time_impact = context_analysis.get('time_impact', {})
        if time_impact:
            most_active_period = max(time_impact.keys(), key=lambda x: time_impact[x]['frequency'])
            insights.append(f"Ваше самое активное время для еды: {most_active_period}")

        # Social insights
        social_impact = context_analysis.get('social_impact', {})
        if len(social_impact) >= 2:
            social_calories = {s: data['avg_calories'] for s, data in social_impact.items()}
            highest_social = max(social_calories.keys(), key=lambda x: social_calories[x])

            if social_calories[highest_social] > statistics.mean(social_calories.values()) * 1.3:
                insights.append(
                    f"В контексте '{highest_social}' вы едите значительно больше обычного"
                )

        # Context sensitivity insights
        context_score = context_analysis.get('context_score', 0.5)
        if context_score > 0.7:
            insights.append(
                "Внешние факторы сильно влияют на ваше пищевое поведение - это важно учитывать при планировании"
            )
        elif context_score < 0.3:
            insights.append(
                "Вы демонстрируете стабильное пищевое поведение независимо от обстоятельств"
            )

        # Archetype-specific contextual insights
        if nutrition_dna.archetype.value in ['STRESS_DRIVEN', 'SOCIAL_EATER']:
            insights.append(
                "Ваш тип питания особенно чувствителен к внешним факторам - развивайте осознанность"
            )

        return insights[:3]  # Top 3 insights