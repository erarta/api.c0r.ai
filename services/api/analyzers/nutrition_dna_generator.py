"""
Nutrition DNA Generator - The core intelligence that creates personalized eating profiles.
This is like genetic sequencing for nutrition habits.
"""
from __future__ import annotations

import statistics
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

from loguru import logger

from ..models.nutrition_profile import (
    NutritionDNA, EatingPersonality, EnhancedUserProfile
)
from .temporal_patterns import TemporalPatternsAnalyzer
from .psychological_profile import PsychologicalProfileAnalyzer


class NutritionDNAGenerator:
    """
    Generates comprehensive nutritional behavioral profiles (Nutrition DNA).
    Combines temporal, psychological, and contextual analysis into a unified profile.
    """

    @classmethod
    def generate_nutrition_dna(
        cls,
        user_profile: Dict[str, Any],
        food_logs: List[Dict[str, Any]],
        context_data: Optional[Dict[str, Any]] = None
    ) -> NutritionDNA:
        """
        Generate complete Nutrition DNA from user data.

        Args:
            user_profile: Basic user profile data
            food_logs: List of food analysis logs
            context_data: Additional context (location, weather, etc.)

        Returns:
            Complete NutritionDNA profile
        """
        logger.info(f"Generating Nutrition DNA for user with {len(food_logs)} food logs")

        try:
            # 1. Temporal Pattern Analysis
            temporal_patterns = TemporalPatternsAnalyzer.analyze_temporal_patterns(food_logs)
            energy_patterns = TemporalPatternsAnalyzer.analyze_energy_patterns(food_logs)

            # 2. Psychological Profile Analysis
            eating_personality = PsychologicalProfileAnalyzer.detect_eating_personality(
                food_logs, temporal_patterns.meal_timing_consistency
            )
            social_patterns = PsychologicalProfileAnalyzer.analyze_social_eating_patterns(food_logs)

            # 3. Behavioral Learning
            triggers = PsychologicalProfileAnalyzer.identify_triggers(food_logs)
            success_patterns = PsychologicalProfileAnalyzer.identify_success_patterns(
                food_logs, user_profile.get('goal')
            )
            optimization_zones = PsychologicalProfileAnalyzer.identify_optimization_zones(
                food_logs, user_profile
            )

            # 4. Calculate Confidence and Quality Scores
            confidence_score = cls._calculate_confidence_score(food_logs, user_profile)
            data_quality_score = cls._calculate_data_quality_score(food_logs)

            # 5. Calculate Metrics
            diversity_score = cls._calculate_diversity_score(food_logs)
            consistency_score = temporal_patterns.meal_timing_consistency
            goal_alignment = cls._calculate_goal_alignment(food_logs, user_profile)

            # 6. Assemble DNA
            nutrition_dna = NutritionDNA(
                archetype=eating_personality,
                confidence_score=confidence_score,
                energy_patterns=energy_patterns,
                social_patterns=social_patterns,
                temporal_patterns=temporal_patterns,
                triggers=triggers,
                success_patterns=success_patterns,
                optimization_zones=optimization_zones,
                diversity_score=diversity_score,
                consistency_score=consistency_score,
                goal_alignment_score=goal_alignment,
                data_quality_score=data_quality_score
            )

            logger.info(f"Generated DNA: {eating_personality} with confidence {confidence_score:.2f}")
            return nutrition_dna

        except Exception as e:
            logger.error(f"Failed to generate Nutrition DNA: {e}")
            # Return minimal DNA profile as fallback
            return cls._create_fallback_dna()

    @staticmethod
    def _calculate_confidence_score(food_logs: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate how confident we are in the generated profile"""

        # Base confidence factors
        log_count_score = min(1.0, len(food_logs) / 50)  # 50+ logs = full confidence

        # Date range coverage
        dates = set()
        for log in food_logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    dates.add(dt.date())
                except Exception:
                    continue

        date_range_days = len(dates)
        date_coverage_score = min(1.0, date_range_days / 14)  # 14+ days = full confidence

        # Profile completeness
        profile_fields = ['age', 'gender', 'weight_kg', 'goal', 'daily_calories_target']
        filled_fields = sum(1 for field in profile_fields if user_profile.get(field))
        profile_completeness = filled_fields / len(profile_fields)

        # Data quality (logs with nutritional data)
        quality_logs = sum(1 for log in food_logs if log.get('kbzhu'))
        data_quality = quality_logs / max(len(food_logs), 1)

        # Combined confidence score
        confidence = statistics.mean([
            log_count_score, date_coverage_score, profile_completeness, data_quality
        ])

        return round(confidence, 3)

    @staticmethod
    def _calculate_data_quality_score(food_logs: List[Dict[str, Any]]) -> float:
        """Assess the quality of data used for analysis"""

        if not food_logs:
            return 0.0

        # Check for complete nutritional data
        complete_logs = sum(1 for log in food_logs if log.get('kbzhu') and
                          all(log['kbzhu'].get(key, 0) > 0 for key in ['calories', 'protein', 'fats', 'carbs']))

        completeness_score = complete_logs / len(food_logs)

        # Check for metadata richness
        metadata_logs = sum(1 for log in food_logs if log.get('metadata'))
        metadata_score = metadata_logs / len(food_logs)

        # Check for timestamp quality
        valid_timestamps = sum(1 for log in food_logs if cls._is_valid_timestamp(log.get('timestamp')))
        timestamp_score = valid_timestamps / len(food_logs)

        return statistics.mean([completeness_score, metadata_score, timestamp_score])

    @staticmethod
    def _is_valid_timestamp(timestamp_str: Optional[str]) -> bool:
        """Check if timestamp is valid and parseable"""
        if not timestamp_str:
            return False
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return True
        except Exception:
            return False

    @staticmethod
    def _calculate_diversity_score(food_logs: List[Dict[str, Any]]) -> float:
        """Calculate how diverse the user's diet is"""

        if not food_logs:
            return 0.0

        # Use metadata to identify unique foods (simplified approach)
        unique_foods = set()

        for log in food_logs:
            metadata = log.get('metadata', {})
            if isinstance(metadata, dict):
                # Extract food names/descriptions from metadata
                description = str(metadata).lower()
                # This is simplified - in real implementation, would use NLP/food recognition
                unique_foods.add(description[:50])  # Use first 50 chars as unique identifier

        # Diversity based on unique foods per total logs
        raw_diversity = len(unique_foods) / len(food_logs)

        # Normalize to 0-1 scale (assume 0.5 unique ratio = good diversity)
        diversity_score = min(1.0, raw_diversity / 0.5)

        return round(diversity_score, 3)

    @staticmethod
    def _calculate_goal_alignment(food_logs: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
        """Calculate how well current eating aligns with user's stated goals"""

        goal = user_profile.get('goal', '').lower()
        if not goal or not food_logs:
            return 0.5  # Neutral score

        # Calculate average daily calories
        total_calories = sum(log.get('kbzhu', {}).get('calories', 0) for log in food_logs if log.get('kbzhu'))
        days = len(set(log.get('timestamp', '')[:10] for log in food_logs if log.get('timestamp')))
        days = max(days, 1)
        avg_daily_calories = total_calories / days

        target_calories = user_profile.get('daily_calories_target')

        # Goal-specific alignment calculations
        if 'weight loss' in goal or 'похуд' in goal or 'снижение' in goal:
            # For weight loss, eating below target is good
            if target_calories:
                if avg_daily_calories <= target_calories:
                    alignment = min(1.0, target_calories / max(avg_daily_calories, 1) - 0.9)
                else:
                    alignment = max(0.2, 1.0 - (avg_daily_calories - target_calories) / target_calories)
            else:
                # General weight loss: moderate calories are good
                alignment = 0.8 if 1200 <= avg_daily_calories <= 1800 else 0.4

        elif 'muscle' in goal or 'мышц' in goal or 'набор' in goal:
            # For muscle gain, adequate calories and protein
            protein_ratio = sum(log.get('kbzhu', {}).get('protein', 0) for log in food_logs if log.get('kbzhu')) / max(total_calories, 1)

            calorie_alignment = 0.8 if avg_daily_calories >= 2000 else avg_daily_calories / 2000
            protein_alignment = min(1.0, protein_ratio / 0.15)  # 15% protein target

            alignment = statistics.mean([calorie_alignment, protein_alignment])

        else:
            # Maintenance or general health
            if target_calories:
                calorie_diff = abs(avg_daily_calories - target_calories) / target_calories
                alignment = max(0.3, 1.0 - calorie_diff)
            else:
                alignment = 0.7  # Neutral for maintenance without specific target

        return round(max(0.0, min(1.0, alignment)), 3)

    @classmethod
    def _create_fallback_dna(cls) -> NutritionDNA:
        """Create a minimal fallback DNA profile when generation fails"""
        from ..models.nutrition_profile import EnergyPattern, SocialEatingPattern, TemporalPattern
        from datetime import time

        return NutritionDNA(
            archetype=EatingPersonality.INTUITIVE_GRAZER,
            confidence_score=0.1,
            energy_patterns=EnergyPattern(
                morning_appetite=0.3,
                afternoon_hunger=0.5,
                evening_comfort_eating=0.4,
                peak_hunger_time=time(13, 0),
                lowest_energy_time=time(6, 0)
            ),
            social_patterns=SocialEatingPattern(
                weekend_indulgence_score=0.3,
                work_stress_snacking=0.3,
                restaurant_frequency=0.2,
                social_meal_impact=0.3,
                planning_score=0.4
            ),
            temporal_patterns=TemporalPattern(
                preferred_breakfast_time=time(8, 0),
                preferred_lunch_time=time(13, 0),
                preferred_dinner_time=time(19, 0),
                meal_timing_consistency=0.5,
                weekend_shift_hours=1.0,
                late_night_eating_frequency=0.2
            ),
            triggers=[],
            success_patterns=[],
            optimization_zones=[],
            diversity_score=0.5,
            consistency_score=0.5,
            goal_alignment_score=0.5,
            data_quality_score=0.1
        )

    @classmethod
    def update_nutrition_dna(
        cls,
        existing_dna: NutritionDNA,
        new_food_logs: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        days_since_last_update: int = 0
    ) -> NutritionDNA:
        """
        Update existing Nutrition DNA with new data.
        Uses weighted averaging to preserve established patterns while incorporating new insights.
        """

        # If not much time has passed and we have high confidence, only minor updates
        if days_since_last_update < 3 and existing_dna.confidence_score > 0.8:
            logger.info("DNA confidence high and recent, applying minor updates only")
            return cls._apply_minor_updates(existing_dna, new_food_logs)

        # Full regeneration for significant time gaps or low confidence
        if days_since_last_update > 14 or existing_dna.confidence_score < 0.5:
            logger.info("Regenerating DNA due to time gap or low confidence")
            return cls.generate_nutrition_dna(user_profile, new_food_logs)

        # Weighted update - blend old and new
        logger.info("Applying weighted DNA update")
        return cls._apply_weighted_update(existing_dna, new_food_logs, user_profile)

    @classmethod
    def _apply_minor_updates(cls, existing_dna: NutritionDNA, new_logs: List[Dict[str, Any]]) -> NutritionDNA:
        """Apply minor updates to existing DNA without full regeneration"""

        # Update only timestamps and minor metrics
        updated_dna = existing_dna.model_copy(deep=True)
        updated_dna.generated_at = datetime.utcnow()

        # Slightly adjust confidence based on new data consistency
        if new_logs:
            new_data_quality = cls._calculate_data_quality_score(new_logs)
            confidence_adjustment = (new_data_quality - updated_dna.data_quality_score) * 0.1
            updated_dna.confidence_score = max(0.0, min(1.0, updated_dna.confidence_score + confidence_adjustment))

        return updated_dna

    @classmethod
    def _apply_weighted_update(cls, existing_dna: NutritionDNA, new_logs: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> NutritionDNA:
        """Apply weighted update blending existing DNA with new analysis"""

        # Generate new DNA from recent data
        new_dna = cls.generate_nutrition_dna(user_profile, new_logs)

        # Blend weights based on confidence and data amount
        existing_weight = existing_dna.confidence_score * 0.7  # Preserve 70% of confident data
        new_weight = 1.0 - existing_weight

        # Weighted averaging of numeric metrics
        blended_dna = existing_dna.model_copy(deep=True)

        # Update metrics with weighted averages
        blended_dna.diversity_score = (
            existing_dna.diversity_score * existing_weight +
            new_dna.diversity_score * new_weight
        )

        blended_dna.goal_alignment_score = (
            existing_dna.goal_alignment_score * existing_weight +
            new_dna.goal_alignment_score * new_weight
        )

        # Update archetype only if new DNA has high confidence and different archetype
        if new_dna.confidence_score > 0.7 and new_dna.archetype != existing_dna.archetype:
            blended_dna.archetype = new_dna.archetype

        # Always update timestamp and add new triggers/patterns
        blended_dna.generated_at = datetime.utcnow()
        blended_dna.triggers.extend(new_dna.triggers)
        blended_dna.success_patterns.extend(new_dna.success_patterns)

        # Update confidence as weighted average
        blended_dna.confidence_score = (
            existing_dna.confidence_score * existing_weight +
            new_dna.confidence_score * new_weight
        )

        return blended_dna

    @classmethod
    def get_dna_summary(cls, nutrition_dna: NutritionDNA) -> str:
        """Generate a human-readable summary of the Nutrition DNA"""

        archetype_descriptions = {
            EatingPersonality.EARLY_BIRD_PLANNER: "Ранняя пташка с хорошим планированием",
            EatingPersonality.LATE_STARTER_IMPULSIVE: "Поздний старт, импульсивные решения",
            EatingPersonality.STRUCTURED_BALANCED: "Структурированный и сбалансированный",
            EatingPersonality.STRESS_DRIVEN: "Питание под влиянием стресса",
            EatingPersonality.SOCIAL_EATER: "Социальный тип питания",
            EatingPersonality.INTUITIVE_GRAZER: "Интуитивное питание малыми порциями",
            EatingPersonality.BUSY_PROFESSIONAL: "Занятый профессионал",
            EatingPersonality.WEEKEND_WARRIOR: "Воин выходного дня"
        }

        archetype_desc = archetype_descriptions.get(nutrition_dna.archetype, "Смешанный тип")

        summary_parts = [
            f"🧬 **Ваш тип питания**: {archetype_desc}",
            f"🎯 **Точность профиля**: {nutrition_dna.confidence_score:.0%}",
            f"🌈 **Разнообразие рациона**: {nutrition_dna.diversity_score:.0%}",
            f"⏰ **Стабильность режима**: {nutrition_dna.consistency_score:.0%}",
            f"🎪 **Соответствие целям**: {nutrition_dna.goal_alignment_score:.0%}"
        ]

        if nutrition_dna.triggers:
            main_trigger = nutrition_dna.triggers[0]
            summary_parts.append(f"⚡ **Главный триггер**: {main_trigger.food_response} при {main_trigger.trigger}")

        if nutrition_dna.optimization_zones:
            top_zone = max(nutrition_dna.optimization_zones, key=lambda z: z.impact == "high")
            summary_parts.append(f"🔧 **Зона роста**: {top_zone.area}")

        return "\n".join(summary_parts)