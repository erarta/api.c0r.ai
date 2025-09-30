"""
Enhanced Supabase service with support for all new nutrition features.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from .client import supabase
from ...services.api.models.nutrition_profile import NutritionDNA, WeeklyInsight


class EnhancedSupabaseService:
    """Enhanced database service with support for Nutrition DNA and advanced features."""

    async def save_nutrition_dna(self, user_id: str, nutrition_dna: NutritionDNA) -> Optional[str]:
        """Save or update user's Nutrition DNA profile"""

        if supabase is None:
            logger.warning("Supabase client is not configured")
            return None

        try:
            # Convert DNA to database format
            dna_data = {
                "user_id": user_id,
                "archetype": nutrition_dna.archetype.value,
                "confidence_score": nutrition_dna.confidence_score,
                "energy_patterns": nutrition_dna.energy_patterns.dict(),
                "social_patterns": nutrition_dna.social_patterns.dict(),
                "temporal_patterns": nutrition_dna.temporal_patterns.dict(),
                "triggers": [trigger.dict() for trigger in nutrition_dna.triggers],
                "success_patterns": [pattern.dict() for pattern in nutrition_dna.success_patterns],
                "optimization_zones": [zone.dict() for zone in nutrition_dna.optimization_zones],
                "diversity_score": nutrition_dna.diversity_score,
                "consistency_score": nutrition_dna.consistency_score,
                "goal_alignment_score": nutrition_dna.goal_alignment_score,
                "data_quality_score": nutrition_dna.data_quality_score,
                "generated_at": nutrition_dna.generated_at.isoformat(),
                "version": 1
            }

            # Upsert DNA record
            result = (
                supabase.table("nutrition_dna")
                .upsert(dna_data, on_conflict="user_id")
                .execute()
            )

            if result.data:
                dna_id = result.data[0]["id"]

                # Update user profile with DNA reference
                supabase.table("user_profiles").update({
                    "nutrition_dna_id": dna_id
                }).eq("user_id", user_id).execute()

                logger.info(f"Saved Nutrition DNA for user {user_id}")
                return dna_id
            else:
                logger.error("Failed to save Nutrition DNA - no data returned")
                return None

        except Exception as e:
            logger.error(f"Failed to save Nutrition DNA for user {user_id}: {e}")
            return None

    async def get_nutrition_dna(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user's Nutrition DNA profile"""

        if supabase is None:
            return None

        try:
            result = (
                supabase.table("nutrition_dna")
                .select("*")
                .eq("user_id", user_id)
                .order("generated_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                return result.data[0]
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get Nutrition DNA for user {user_id}: {e}")
            return None

    async def save_behavioral_insights(
        self,
        user_id: str,
        insights: List[str],
        insight_type: str = "daily",
        generated_for_date: date = None,
        context: Dict[str, Any] = None
    ) -> bool:
        """Save behavioral insights for user"""

        if supabase is None or not insights:
            return False

        try:
            # Get DNA ID
            dna_result = await self.get_nutrition_dna(user_id)
            dna_id = dna_result.get("id") if dna_result else None

            insights_data = []
            for insight_text in insights:
                insights_data.append({
                    "user_id": user_id,
                    "nutrition_dna_id": dna_id,
                    "insight_type": insight_type,
                    "insight_text": insight_text,
                    "confidence": 0.8,  # Default confidence
                    "generated_for_date": generated_for_date.isoformat() if generated_for_date else None,
                    "context_data": json.dumps(context) if context else "{}",
                    "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()  # Insights valid for 1 week
                })

            result = supabase.table("behavioral_insights").insert(insights_data).execute()

            logger.info(f"Saved {len(insights)} behavioral insights for user {user_id}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to save behavioral insights for user {user_id}: {e}")
            return False

    async def save_behavioral_predictions(
        self,
        user_id: str,
        predictions: List[Dict[str, Any]],
        prediction_date: date = None
    ) -> bool:
        """Save behavioral predictions for user"""

        if supabase is None or not predictions:
            return False

        try:
            # Get DNA ID
            dna_result = await self.get_nutrition_dna(user_id)
            dna_id = dna_result.get("id") if dna_result else None

            prediction_date = prediction_date or date.today()

            predictions_data = []
            for pred in predictions:
                predictions_data.append({
                    "user_id": user_id,
                    "nutrition_dna_id": dna_id,
                    "event": pred.get("event", "unknown"),
                    "probability": pred.get("probability", 0.5),
                    "confidence": pred.get("confidence", 0.5),
                    "recommended_action": pred.get("recommended_action", ""),
                    "optimal_timing": pred.get("optimal_timing"),
                    "prediction_date": prediction_date.isoformat(),
                    "context_factors": json.dumps(pred.get("context", {})),
                    "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat()
                })

            result = supabase.table("behavioral_predictions").insert(predictions_data).execute()

            logger.info(f"Saved {len(predictions)} behavioral predictions for user {user_id}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to save behavioral predictions for user {user_id}: {e}")
            return False

    async def save_meal_recommendations(
        self,
        user_id: str,
        recommendations: List[Dict[str, Any]],
        recommended_for_date: date = None
    ) -> bool:
        """Save meal recommendations for user"""

        if supabase is None or not recommendations:
            return False

        try:
            # Get DNA ID
            dna_result = await self.get_nutrition_dna(user_id)
            dna_id = dna_result.get("id") if dna_result else None

            recommended_for_date = recommended_for_date or date.today()

            recommendations_data = []
            for rec in recommendations:
                recommendations_data.append({
                    "user_id": user_id,
                    "nutrition_dna_id": dna_id,
                    "meal_type": rec.get("meal_type"),
                    "dish_name": rec.get("dish_name"),
                    "description": rec.get("description"),
                    "reasoning": rec.get("reasoning"),
                    "recommended_time": rec.get("recommended_time"),
                    "calories": rec.get("calories", 0),
                    "protein": rec.get("protein", 0),
                    "fats": rec.get("fats", 0),
                    "carbs": rec.get("carbs", 0),
                    "fiber": rec.get("fiber"),
                    "prep_time_minutes": rec.get("prep_time_minutes", 30),
                    "difficulty_level": rec.get("difficulty_level", "medium"),
                    "ingredients": json.dumps(rec.get("ingredients", [])),
                    "matches_energy_level": rec.get("matches_energy_level", False),
                    "addresses_typical_craving": rec.get("addresses_typical_craving", False),
                    "fits_schedule_pattern": rec.get("fits_schedule_pattern", False),
                    "supports_current_goal": rec.get("supports_current_goal", False),
                    "recommended_for_date": recommended_for_date.isoformat()
                })

            result = supabase.table("meal_recommendations").insert(recommendations_data).execute()

            logger.info(f"Saved {len(recommendations)} meal recommendations for user {user_id}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to save meal recommendations for user {user_id}: {e}")
            return False

    async def save_context_analysis(
        self,
        user_id: str,
        context_analysis: Dict[str, Any],
        start_date: date,
        end_date: date
    ) -> bool:
        """Save context analysis results"""

        if supabase is None:
            return False

        try:
            analysis_data = {
                "user_id": user_id,
                "analysis_start_date": start_date.isoformat(),
                "analysis_end_date": end_date.isoformat(),
                "weather_impact": json.dumps(context_analysis.get("weather_impact", {})),
                "time_impact": json.dumps(context_analysis.get("time_impact", {})),
                "social_impact": json.dumps(context_analysis.get("social_impact", {})),
                "location_impact": json.dumps(context_analysis.get("location_impact", {})),
                "strongest_influences": json.dumps(context_analysis.get("strongest_influences", [])),
                "context_sensitivity_score": context_analysis.get("context_score", 0.5),
                "contextual_recommendations": json.dumps(context_analysis.get("recommendations", []))
            }

            result = (
                supabase.table("context_analysis")
                .upsert(analysis_data, on_conflict="user_id,analysis_start_date,analysis_end_date")
                .execute()
            )

            logger.info(f"Saved context analysis for user {user_id}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to save context analysis for user {user_id}: {e}")
            return False

    async def save_user_feedback(
        self,
        user_id: str,
        feedback_type: str,
        target_id: str,
        rating: int,
        feedback_text: str = None,
        improvement_suggestion: str = None
    ) -> bool:
        """Save user feedback for learning"""

        if supabase is None:
            return False

        try:
            feedback_data = {
                "user_id": user_id,
                "feedback_type": feedback_type,
                "target_id": target_id,
                "rating": rating,
                "feedback_text": feedback_text,
                "improvement_suggestion": improvement_suggestion,
                "feedback_date": date.today().isoformat()
            }

            result = supabase.table("user_feedback").insert(feedback_data).execute()

            logger.info(f"Saved user feedback for user {user_id}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to save user feedback for user {user_id}: {e}")
            return False

    async def get_recent_insights(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent insights for user"""

        if supabase is None:
            return []

        try:
            result = (
                supabase.table("behavioral_insights")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get recent insights for user {user_id}: {e}")
            return []

    async def get_recent_predictions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent predictions for user"""

        if supabase is None:
            return []

        try:
            since_date = (date.today() - timedelta(days=days)).isoformat()

            result = (
                supabase.table("behavioral_predictions")
                .select("*")
                .eq("user_id", user_id)
                .gte("prediction_date", since_date)
                .order("prediction_date", desc=True)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get recent predictions for user {user_id}: {e}")
            return []

    async def get_meal_recommendations(
        self,
        user_id: str,
        meal_type: str = None,
        for_date: date = None
    ) -> List[Dict[str, Any]]:
        """Get meal recommendations for user"""

        if supabase is None:
            return []

        try:
            query = (
                supabase.table("meal_recommendations")
                .select("*")
                .eq("user_id", user_id)
                .gt("expires_at", datetime.utcnow().isoformat())
                .order("created_at", desc=True)
            )

            if meal_type:
                query = query.eq("meal_type", meal_type)

            if for_date:
                query = query.eq("recommended_for_date", for_date.isoformat())

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get meal recommendations for user {user_id}: {e}")
            return []

    async def update_nutrition_analytics(self, user_id: str) -> bool:
        """Update nutrition analytics for user"""

        if supabase is None:
            return False

        try:
            # This would calculate various metrics from recent data
            # For now, just create a basic analytics record

            analytics_data = {
                "user_id": user_id,
                "analysis_date": date.today().isoformat(),
                "period_type": "daily",
                "goal_progress_score": 0.7,  # Would calculate from actual data
                "consistency_score": 0.8,
                "diversity_score": 0.6,
                "recommendations_used": 0,
                "insights_rated": 0
            }

            result = (
                supabase.table("nutrition_analytics")
                .upsert(analytics_data, on_conflict="user_id,analysis_date,period_type")
                .execute()
            )

            return bool(result.data)

        except Exception as e:
            logger.error(f"Failed to update nutrition analytics for user {user_id}: {e}")
            return False

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired insights and predictions"""

        if supabase is None:
            return {"insights": 0, "predictions": 0}

        try:
            cleanup_counts = {"insights": 0, "predictions": 0}

            # Clean expired insights
            insights_result = (
                supabase.table("behavioral_insights")
                .delete()
                .lt("expires_at", datetime.utcnow().isoformat())
                .execute()
            )
            cleanup_counts["insights"] = len(insights_result.data or [])

            # Clean expired predictions
            predictions_result = (
                supabase.table("behavioral_predictions")
                .delete()
                .lt("valid_until", datetime.utcnow().isoformat())
                .execute()
            )
            cleanup_counts["predictions"] = len(predictions_result.data or [])

            logger.info(f"Cleaned up {cleanup_counts['insights']} insights and {cleanup_counts['predictions']} predictions")
            return cleanup_counts

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return {"insights": 0, "predictions": 0}

    async def get_user_nutrition_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive nutrition summary for user"""

        if supabase is None:
            return None

        try:
            # Use the view created in migration
            result = (
                supabase.table("user_nutrition_summary")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            if result.data:
                return result.data[0]
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get nutrition summary for user {user_id}: {e}")
            return None


# Singleton instance
enhanced_supabase_service = EnhancedSupabaseService()