"""
Nutrition Insights Visualizer.
Creates visual representations and charts for nutrition data, DNA insights, and progress tracking.
"""
from __future__ import annotations

import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..models.nutrition_profile import NutritionDNA, EatingPersonality


class NutritionVisualizer:
    """
    Creates data visualizations and formatted outputs for nutrition insights.
    Generates charts, progress indicators, and visual summaries.
    """

    @classmethod
    def create_dna_summary_card(cls, nutrition_dna: NutritionDNA) -> Dict[str, Any]:
        """Create a visual summary card for Nutrition DNA"""

        # Archetype visualization
        archetype_icons = {
            EatingPersonality.EARLY_BIRD_PLANNER: "🌅",
            EatingPersonality.LATE_STARTER_IMPULSIVE: "😴",
            EatingPersonality.STRUCTURED_BALANCED: "⚖️",
            EatingPersonality.STRESS_DRIVEN: "😰",
            EatingPersonality.SOCIAL_EATER: "👥",
            EatingPersonality.INTUITIVE_GRAZER: "🌿",
            EatingPersonality.BUSY_PROFESSIONAL: "💼",
            EatingPersonality.WEEKEND_WARRIOR: "🏃"
        }

        archetype_names = {
            EatingPersonality.EARLY_BIRD_PLANNER: "Ранняя пташка",
            EatingPersonality.LATE_STARTER_IMPULSIVE: "Поздний старт",
            EatingPersonality.STRUCTURED_BALANCED: "Сбалансированный",
            EatingPersonality.STRESS_DRIVEN: "Стрессовый тип",
            EatingPersonality.SOCIAL_EATER: "Социальный едок",
            EatingPersonality.INTUITIVE_GRAZER: "Интуитивный",
            EatingPersonality.BUSY_PROFESSIONAL: "Занятый профи",
            EatingPersonality.WEEKEND_WARRIOR: "Воин выходного дня"
        }

        return {
            "type": "dna_summary_card",
            "archetype": {
                "name": archetype_names.get(nutrition_dna.archetype, "Смешанный тип"),
                "icon": archetype_icons.get(nutrition_dna.archetype, "🧬"),
                "confidence": nutrition_dna.confidence_score
            },
            "scores": {
                "diversity": {
                    "value": nutrition_dna.diversity_score,
                    "label": "Разнообразие",
                    "color": cls._get_score_color(nutrition_dna.diversity_score),
                    "description": cls._get_diversity_description(nutrition_dna.diversity_score)
                },
                "consistency": {
                    "value": nutrition_dna.consistency_score,
                    "label": "Стабильность",
                    "color": cls._get_score_color(nutrition_dna.consistency_score),
                    "description": cls._get_consistency_description(nutrition_dna.consistency_score)
                },
                "goal_alignment": {
                    "value": nutrition_dna.goal_alignment_score,
                    "label": "Соответствие целям",
                    "color": cls._get_score_color(nutrition_dna.goal_alignment_score),
                    "description": cls._get_goal_alignment_description(nutrition_dna.goal_alignment_score)
                }
            },
            "generated_at": nutrition_dna.generated_at.isoformat(),
            "data_quality": nutrition_dna.data_quality_score
        }

    @classmethod
    def create_weekly_insights_chart(cls, weekly_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create visual chart for weekly insights"""

        return {
            "type": "weekly_insights_chart",
            "title": "📊 Недельный обзор питания",
            "daily_insights": weekly_insights.get("day_insights", {}),
            "patterns": {
                "observed": weekly_insights.get("observed_patterns", []),
                "risk_days": weekly_insights.get("risk_days", []),
                "opportunities": weekly_insights.get("opportunity_moments", [])
            },
            "micro_goals": [
                {
                    "text": goal,
                    "priority": "high" if i == 0 else "medium",
                    "icon": "🎯"
                }
                for i, goal in enumerate(weekly_insights.get("micro_goals", []))
            ]
        }

    @classmethod
    def create_temporal_patterns_chart(cls, nutrition_dna: NutritionDNA) -> Dict[str, Any]:
        """Create visualization for temporal eating patterns"""

        temporal = nutrition_dna.temporal_patterns
        energy = nutrition_dna.energy_patterns

        # Create time-based eating pattern
        time_pattern = []
        for hour in range(6, 23):  # 6 AM to 11 PM
            energy_level = 0.3  # Base level

            # Adjust based on meal times
            if abs(hour - temporal.preferred_breakfast_time.hour) <= 1:
                energy_level += energy.morning_appetite * 0.7
            elif abs(hour - temporal.preferred_lunch_time.hour) <= 1:
                energy_level += energy.afternoon_hunger * 0.8
            elif abs(hour - temporal.preferred_dinner_time.hour) <= 1:
                energy_level += 0.6

            # Late night eating
            if hour >= 21:
                energy_level += energy.evening_comfort_eating * 0.5

            time_pattern.append({
                "hour": hour,
                "energy_level": min(energy_level, 1.0),
                "is_meal_time": (
                    abs(hour - temporal.preferred_breakfast_time.hour) <= 1 or
                    abs(hour - temporal.preferred_lunch_time.hour) <= 1 or
                    abs(hour - temporal.preferred_dinner_time.hour) <= 1
                )
            })

        return {
            "type": "temporal_patterns_chart",
            "title": "⏰ Ваши временные паттерны питания",
            "time_pattern": time_pattern,
            "meal_times": {
                "breakfast": temporal.preferred_breakfast_time.strftime("%H:%M"),
                "lunch": temporal.preferred_lunch_time.strftime("%H:%M"),
                "dinner": temporal.preferred_dinner_time.strftime("%H:%M")
            },
            "consistency_score": temporal.meal_timing_consistency,
            "weekend_shift": f"{temporal.weekend_shift_hours:.1f} часов",
            "late_eating_frequency": f"{temporal.late_night_eating_frequency:.0%}"
        }

    @classmethod
    def create_predictions_dashboard(cls, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create dashboard for behavioral predictions"""

        # Group predictions by risk level
        high_risk = [p for p in predictions if p.get("probability", 0) > 0.7]
        medium_risk = [p for p in predictions if 0.4 < p.get("probability", 0) <= 0.7]
        low_risk = [p for p in predictions if p.get("probability", 0) <= 0.4]

        # Create prediction cards
        prediction_cards = []

        for pred in high_risk:
            prediction_cards.append({
                "risk_level": "high",
                "event": pred.get("event", "unknown"),
                "probability": pred.get("probability", 0),
                "action": pred.get("recommended_action", ""),
                "timing": pred.get("optimal_timing"),
                "icon": cls._get_prediction_icon(pred.get("event", "")),
                "color": "#FF6B6B"
            })

        for pred in medium_risk[:3]:  # Limit to top 3 medium risk
            prediction_cards.append({
                "risk_level": "medium",
                "event": pred.get("event", "unknown"),
                "probability": pred.get("probability", 0),
                "action": pred.get("recommended_action", ""),
                "timing": pred.get("optimal_timing"),
                "icon": cls._get_prediction_icon(pred.get("event", "")),
                "color": "#FFD93D"
            })

        return {
            "type": "predictions_dashboard",
            "title": "🔮 Прогнозы поведения",
            "summary": {
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk)
            },
            "prediction_cards": prediction_cards,
            "overall_risk_score": cls._calculate_overall_risk_score(predictions)
        }

    @classmethod
    def create_optimization_zones_chart(cls, nutrition_dna: NutritionDNA) -> Dict[str, Any]:
        """Create visualization for optimization opportunities"""

        optimization_cards = []

        for zone in nutrition_dna.optimization_zones:
            progress_percentage = zone.current_score * 100
            target_percentage = zone.target_score * 100
            improvement_needed = target_percentage - progress_percentage

            difficulty_colors = {
                "easy_wins": "#4ECDC4",
                "moderate_effort": "#45B7D1",
                "requires_strategy": "#FFA07A",
                "long_term_goal": "#DDA0DD"
            }

            impact_icons = {
                "low": "📈",
                "medium": "🚀",
                "high": "💥"
            }

            optimization_cards.append({
                "area": cls._translate_optimization_area(zone.area),
                "current_score": progress_percentage,
                "target_score": target_percentage,
                "improvement_needed": improvement_needed,
                "difficulty": zone.difficulty,
                "difficulty_color": difficulty_colors.get(zone.difficulty, "#95A5A6"),
                "impact": zone.impact,
                "impact_icon": impact_icons.get(zone.impact, "📈"),
                "priority": cls._calculate_zone_priority(zone)
            })

        # Sort by priority
        optimization_cards.sort(key=lambda x: x["priority"], reverse=True)

        return {
            "type": "optimization_zones_chart",
            "title": "🔧 Зоны роста",
            "optimization_cards": optimization_cards,
            "total_zones": len(optimization_cards),
            "easy_wins": len([z for z in nutrition_dna.optimization_zones if z.difficulty == "easy_wins"])
        }

    @classmethod
    def create_progress_timeline(
        cls,
        food_history: List[Dict[str, Any]],
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Create progress timeline visualization"""

        if not food_history:
            return {
                "type": "progress_timeline",
                "title": "📈 История прогресса",
                "message": "Недостаточно данных для отображения прогресса",
                "timeline": []
            }

        # Group logs by day
        daily_data = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)

        for log in food_history:
            timestamp_str = log.get("timestamp")
            if not timestamp_str:
                continue

            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if dt >= cutoff_date:
                    day_key = dt.date().isoformat()
                    daily_data[day_key].append(log)
            except Exception:
                continue

        # Create timeline points
        timeline_points = []
        dates = sorted(daily_data.keys())

        for day_str in dates[-14:]:  # Last 14 days
            day_logs = daily_data[day_str]

            # Calculate daily metrics
            total_calories = sum(
                log.get('kbzhu', {}).get('calories', 0)
                for log in day_logs
                if log.get('kbzhu')
            )

            analysis_count = len(day_logs)
            variety_score = len(set(str(log.get('metadata', {}))[:50] for log in day_logs)) / max(analysis_count, 1)

            timeline_points.append({
                "date": day_str,
                "analyses_count": analysis_count,
                "total_calories": total_calories,
                "variety_score": variety_score,
                "quality_score": cls._calculate_day_quality_score(day_logs)
            })

        return {
            "type": "progress_timeline",
            "title": "📈 История прогресса (14 дней)",
            "timeline": timeline_points,
            "summary": {
                "total_analyses": sum(point["analyses_count"] for point in timeline_points),
                "active_days": len([p for p in timeline_points if p["analyses_count"] > 0]),
                "avg_daily_analyses": statistics.mean([p["analyses_count"] for p in timeline_points]) if timeline_points else 0
            }
        }

    @classmethod
    def create_social_patterns_radar(cls, nutrition_dna: NutritionDNA) -> Dict[str, Any]:
        """Create radar chart for social eating patterns"""

        social = nutrition_dna.social_patterns

        radar_data = [
            {
                "axis": "Планирование",
                "value": social.planning_score,
                "max": 1.0
            },
            {
                "axis": "Выходные",
                "value": 1.0 - social.weekend_indulgence_score,  # Invert for radar
                "max": 1.0
            },
            {
                "axis": "Стресс-контроль",
                "value": 1.0 - social.work_stress_snacking,  # Invert for radar
                "max": 1.0
            },
            {
                "axis": "Домашнее питание",
                "value": 1.0 - social.restaurant_frequency,  # Invert for radar
                "max": 1.0
            },
            {
                "axis": "Независимость",
                "value": 1.0 - social.social_meal_impact,  # Invert for radar
                "max": 1.0
            }
        ]

        return {
            "type": "social_patterns_radar",
            "title": "🕸️ Социальные паттерны питания",
            "radar_data": radar_data,
            "insights": [
                f"Планирование питания: {social.planning_score:.0%}",
                f"Контроль в выходные: {(1-social.weekend_indulgence_score):.0%}",
                f"Устойчивость к стрессу: {(1-social.work_stress_snacking):.0%}"
            ]
        }

    @staticmethod
    def _get_score_color(score: float) -> str:
        """Get color based on score"""
        if score >= 0.8:
            return "#4ECDC4"  # Excellent - teal
        elif score >= 0.6:
            return "#45B7D1"  # Good - blue
        elif score >= 0.4:
            return "#FFD93D"  # Fair - yellow
        else:
            return "#FF6B6B"  # Needs improvement - red

    @staticmethod
    def _get_diversity_description(score: float) -> str:
        """Get description for diversity score"""
        if score >= 0.8:
            return "Отличное разнообразие в питании"
        elif score >= 0.6:
            return "Хорошее разнообразие"
        elif score >= 0.4:
            return "Умеренное разнообразие"
        else:
            return "Стоит добавить разнообразия"

    @staticmethod
    def _get_consistency_description(score: float) -> str:
        """Get description for consistency score"""
        if score >= 0.8:
            return "Очень стабильный режим"
        elif score >= 0.6:
            return "Стабильные привычки"
        elif score >= 0.4:
            return "Умеренная стабильность"
        else:
            return "Режим требует упорядочивания"

    @staticmethod
    def _get_goal_alignment_description(score: float) -> str:
        """Get description for goal alignment score"""
        if score >= 0.8:
            return "Отлично соответствует целям"
        elif score >= 0.6:
            return "Хорошо поддерживает цели"
        elif score >= 0.4:
            return "Частично соответствует целям"
        else:
            return "Требует корректировки под цели"

    @staticmethod
    def _get_prediction_icon(event: str) -> str:
        """Get icon for prediction event"""
        event_lower = event.lower()

        if "stress" in event_lower:
            return "😰"
        elif "late" in event_lower or "night" in event_lower:
            return "🌙"
        elif "social" in event_lower:
            return "👥"
        elif "weekend" in event_lower:
            return "🏖️"
        elif "comfort" in event_lower:
            return "🍫"
        elif "skip" in event_lower:
            return "⏰"
        else:
            return "🔮"

    @staticmethod
    def _calculate_overall_risk_score(predictions: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score from predictions"""
        if not predictions:
            return 0.0

        # Weight predictions by probability and confidence
        weighted_scores = []
        for pred in predictions:
            prob = pred.get("probability", 0)
            conf = pred.get("confidence", 0.5)
            weighted_scores.append(prob * conf)

        return statistics.mean(weighted_scores) if weighted_scores else 0.0

    @staticmethod
    def _translate_optimization_area(area: str) -> str:
        """Translate optimization area to Russian"""
        translations = {
            "protein_intake": "Потребление белка",
            "fiber_intake": "Потребление клетчатки",
            "meal_timing": "Время приемов пищи",
            "weekend_consistency": "Стабильность в выходные",
            "portion_control": "Контроль порций",
            "hydration": "Потребление жидкости",
            "snack_quality": "Качество перекусов"
        }
        return translations.get(area, area.replace("_", " ").title())

    @staticmethod
    def _calculate_zone_priority(zone) -> float:
        """Calculate priority score for optimization zone"""
        impact_weights = {"low": 0.3, "medium": 0.6, "high": 1.0}
        difficulty_weights = {"easy_wins": 1.0, "moderate_effort": 0.8, "requires_strategy": 0.6, "long_term_goal": 0.4}

        impact_score = impact_weights.get(zone.impact, 0.5)
        difficulty_score = difficulty_weights.get(zone.difficulty, 0.5)
        improvement_potential = zone.target_score - zone.current_score

        return impact_score * difficulty_score * improvement_potential

    @staticmethod
    def _calculate_day_quality_score(day_logs: List[Dict[str, Any]]) -> float:
        """Calculate quality score for a day based on logs"""
        if not day_logs:
            return 0.0

        # Simple quality metrics
        has_breakfast = any(
            5 <= datetime.fromisoformat(log.get("timestamp", "").replace('Z', '+00:00')).hour <= 11
            for log in day_logs
            if log.get("timestamp")
        )

        has_lunch = any(
            11 <= datetime.fromisoformat(log.get("timestamp", "").replace('Z', '+00:00')).hour <= 16
            for log in day_logs
            if log.get("timestamp")
        )

        has_dinner = any(
            17 <= datetime.fromisoformat(log.get("timestamp", "").replace('Z', '+00:00')).hour <= 22
            for log in day_logs
            if log.get("timestamp")
        )

        meal_distribution = sum([has_breakfast, has_lunch, has_dinner]) / 3.0

        # Variety score
        variety = len(set(str(log.get("metadata", {}))[:30] for log in day_logs)) / max(len(day_logs), 1)

        # Timing score (avoid very late eating)
        late_eating_penalty = 0
        for log in day_logs:
            try:
                hour = datetime.fromisoformat(log.get("timestamp", "").replace('Z', '+00:00')).hour
                if hour >= 22:
                    late_eating_penalty += 0.1
            except Exception:
                continue

        quality_score = meal_distribution * 0.5 + variety * 0.3 + max(0, 0.2 - late_eating_penalty)
        return min(quality_score, 1.0)

    @classmethod
    def generate_nutrition_report(
        cls,
        nutrition_dna: NutritionDNA,
        food_history: List[Dict[str, Any]],
        weekly_insights: Dict[str, Any] = None,
        predictions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive nutrition report with all visualizations"""

        report_components = []

        # 1. DNA Summary Card
        report_components.append(cls.create_dna_summary_card(nutrition_dna))

        # 2. Temporal Patterns
        report_components.append(cls.create_temporal_patterns_chart(nutrition_dna))

        # 3. Social Patterns Radar
        report_components.append(cls.create_social_patterns_radar(nutrition_dna))

        # 4. Optimization Zones
        report_components.append(cls.create_optimization_zones_chart(nutrition_dna))

        # 5. Progress Timeline
        report_components.append(cls.create_progress_timeline(food_history))

        # 6. Weekly Insights (if available)
        if weekly_insights:
            report_components.append(cls.create_weekly_insights_chart(weekly_insights))

        # 7. Predictions Dashboard (if available)
        if predictions:
            report_components.append(cls.create_predictions_dashboard(predictions))

        return {
            "type": "comprehensive_nutrition_report",
            "title": "🧬 Полный отчет по питанию",
            "generated_at": datetime.utcnow().isoformat(),
            "user_archetype": nutrition_dna.archetype.value,
            "components": report_components,
            "summary": {
                "overall_score": statistics.mean([
                    nutrition_dna.diversity_score,
                    nutrition_dna.consistency_score,
                    nutrition_dna.goal_alignment_score
                ]),
                "data_quality": nutrition_dna.data_quality_score,
                "confidence": nutrition_dna.confidence_score,
                "total_components": len(report_components)
            }
        }