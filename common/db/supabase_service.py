"""
Supabase-backed service for food plan operations.

This module centralizes all database access for the food plan feature so API
routers can depend on a single, typed service instead of raw queries.

Notes:
- Keeps the LLM generation completely unchanged (handled by the router/LLM modules).
- Degrades gracefully when Supabase is not configured (dev environments).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from loguru import logger

from .client import supabase


class SupabaseService:
    """Encapsulates food plan specific database operations."""

    async def get_food_plan_context(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive context for plan generation: profile, food history,
        and a compact summary of recent history.

        Returns a dict with keys: profile, food_history, history_summary.
        """
        global supabase
        if supabase is None:
            # Initialize Supabase connection for dynamic data
            from .client import initialize_supabase
            supabase = initialize_supabase()

            if supabase is None:
                logger.warning("Supabase client not available - using fallback data for development")
                # Return realistic fallback data for testing instead of raising exception
                from datetime import datetime, timedelta

                # Generate realistic test food history for the last week
                test_food_history = []
                for i in range(7):
                    date_offset = datetime.utcnow() - timedelta(days=i)

                    # Vary the food items and timing
                    if i % 3 == 0:  # Breakfast foods
                        test_food_history.append({
                            "timestamp": date_offset.replace(hour=8).isoformat(),
                            "analysis": {
                                "total_nutrition": {"calories": 450, "proteins": 18, "fats": 12, "carbohydrates": 65},
                                "food_items": [
                                    {"name": "Овсянка", "calories": 300, "weight_grams": 80},
                                    {"name": "Ягоды", "calories": 50, "weight_grams": 100},
                                    {"name": "Миндаль", "calories": 100, "weight_grams": 20}
                                ]
                            }
                        })
                    elif i % 3 == 1:  # Lunch foods
                        test_food_history.append({
                            "timestamp": date_offset.replace(hour=13).isoformat(),
                            "analysis": {
                                "total_nutrition": {"calories": 620, "proteins": 35, "fats": 18, "carbohydrates": 55},
                                "food_items": [
                                    {"name": "Лосось", "calories": 280, "weight_grams": 120},
                                    {"name": "Рис", "calories": 240, "weight_grams": 80},
                                    {"name": "Брокколи", "calories": 35, "weight_grams": 150},
                                    {"name": "Оливковое масло", "calories": 65, "weight_grams": 8}
                                ]
                            }
                        })
                    else:  # Dinner foods
                        test_food_history.append({
                            "timestamp": date_offset.replace(hour=19).isoformat(),
                            "analysis": {
                                "total_nutrition": {"calories": 380, "proteins": 28, "fats": 8, "carbohydrates": 45},
                                "food_items": [
                                    {"name": "Курица", "calories": 220, "weight_grams": 100},
                                    {"name": "Овощи", "calories": 80, "weight_grams": 200},
                                    {"name": "Киноа", "calories": 80, "weight_grams": 30}
                                ]
                            }
                        })

                fallback_data = {
                    "profile": {
                        "user_id": user_id,
                        "age": 30,
                        "gender": "male",
                        "height_cm": 175,
                        "weight_kg": 70,
                        "activity_level": "moderately_active",
                        "goal": "maintain_weight",
                        "dietary_preferences": [],
                        "allergies": [],
                        "daily_calories_target": 2200,
                        "language": "ru",
                        "recent_history_by_day": {},
                        "food_history_14d_text": "Тестовые данные для демонстрации анализа"
                    },
                    "food_history": test_food_history,
                    "history_summary": {
                        "total_analyses_7d": len(test_food_history),
                        "active_days_7d": 7
                    },
                    "history_by_day": {},
                    "last_plan_history": await self.get_latest_food_plan(user_id) or None
                }
                return fallback_data

            logger.info(f"Supabase client initialized for user {user_id}")

        # Profile (extract fields relevant for personalization)
        try:
            profile_rows = (
                supabase.table("user_profiles").select("*").eq("user_id", user_id).execute().data
            )
            raw_profile = profile_rows[0] if profile_rows else None
            if raw_profile:
                profile = {
                    "user_id": user_id,
                    "age": raw_profile.get("age"),
                    "gender": raw_profile.get("gender"),
                    "height_cm": raw_profile.get("height_cm"),
                    "weight_kg": raw_profile.get("weight_kg"),
                    "activity_level": raw_profile.get("activity_level"),
                    "goal": raw_profile.get("goal"),
                    "dietary_preferences": raw_profile.get("dietary_preferences") or [],
                    "allergies": raw_profile.get("allergies") or [],
                    "daily_calories_target": raw_profile.get("daily_calories_target"),
                    "language": raw_profile.get("language") or raw_profile.get("locale") or "en",
                }
            else:
                profile = None
        except Exception as e:
            logger.error(f"Failed to fetch profile for user {user_id}: {e}")
            profile = None

        # Recent history (7 days) from logs, day-by-day
        try:
            since = (datetime.utcnow() - timedelta(days=7)).isoformat()
            logs = (
                supabase.table("logs")
                .select("timestamp, kbzhu, metadata")
                .eq("user_id", user_id)
                .eq("action_type", "photo_analysis")
                .gte("timestamp", since)
                .order("timestamp", desc=False)
                .execute()
                .data
            ) or []
            # Attach date field for LLM day-by-day context
            for row in logs:
                ts = row.get("timestamp")
                row["date"] = (ts[:10] if isinstance(ts, str) and len(ts) >= 10 else None)
        except Exception as e:
            logger.error(f"Failed to fetch logs for user {user_id}: {e}")
            logs = []

        # Summarize history (last 7 days)
        try:
            total_analyses = len(logs)
            active_days = len({row.get("date") for row in logs if row.get("date")})
            # Group by day
            history_by_day: Dict[str, list] = {}
            for row in logs:
                d = row.get("date")
                if not d:
                    # skip if no date
                    continue
                history_by_day.setdefault(d, []).append(row)
            history_summary = {
                "total_analyses_7d": total_analyses,
                "active_days_7d": active_days,
            }
        except Exception:
            history_summary = {}
            history_by_day = {}

        # Build a human-readable 14d summary using timestamps only (portable, no model deps)
        history_summary_text_14d = None
        try:
            since_14d = (datetime.utcnow() - timedelta(days=14)).isoformat()
            rows_14d = (
                supabase.table("logs")
                .select("timestamp")
                .eq("user_id", user_id)
                .eq("action_type", "photo_analysis")
                .gte("timestamp", since_14d)
                .order("timestamp", desc=False)
                .execute()
                .data
            ) or []
            total_analyses_14d = len(rows_14d)
            dates_14d = []
            breakfast_days = set()
            late_snacks = 0
            for r in rows_14d:
                ts = r.get("timestamp")
                if not isinstance(ts, str) or len(ts) < 19:
                    continue
                date_str = ts[:10]
                dates_14d.append(date_str)
                try:
                    hour = int(ts[11:13])
                except Exception:
                    hour = None
                if hour is not None:
                    if 5 <= hour <= 11:
                        breakfast_days.add(date_str)
                    if hour >= 21:
                        late_snacks += 1
            active_days_14d = len(set(dates_14d))
            breakfast_skips = max(0, active_days_14d - len(breakfast_days))
            history_summary_text_14d = (
                f"За последние 14 дней: {total_analyses_14d} анализов в {active_days_14d} активных днях; "
                f"завтраки пропускались примерно в {breakfast_skips} дн.; поздних перекусов: {late_snacks}."
            )
            # augment numeric fields too
            history_summary.update({
                "total_analyses_14d": total_analyses_14d,
                "active_days_14d": active_days_14d,
                "breakfast_skips_14d_est": breakfast_skips,
                "late_snacks_14d_est": late_snacks,
            })
        except Exception as e:
            logger.warning(f"Failed to build 14d summary for {user_id}: {e}")
            history_summary_text_14d = None

        # Enrich profile with recent grouped history to assist LLM (non-breaking)
        if profile is not None:
            profile = profile | {
                "recent_history_by_day": history_by_day,
                "food_history_14d_text": history_summary_text_14d,
            }

        return {
            "profile": profile,
            "food_history": logs,
            "history_summary": history_summary,
            "history_by_day": history_by_day,
            # Optional: last plan meta for LLM context
            "last_plan_history": await self.get_latest_food_plan(user_id) or None,
        }

    async def check_food_plan_unlock_status(self, user_id: str, bypass_subscription: bool = False) -> Dict[str, Any]:
        """
        Return unlock status based on recent activity or subscription.

        For now we keep the logic simple and transparent:
        - If bypass_subscription is True or Supabase is unavailable → unlocked.
        - Otherwise: unlocked after 21 analyses OR 14 days with 10 active days in last 14d.
        """
        if supabase is None:
            logger.warning("Supabase client missing; returning unlocked status for dev env")
            return {
                "unlocked": True,
                "subscribed": False,
                "total_analyses_14d": 0,
                "active_days_14d": 0,
            }

        if bypass_subscription:
            return {
                "unlocked": True,
                "subscribed": False,
                "total_analyses_14d": 0,
                "active_days_14d": 0,
            }

        try:
            since = (datetime.utcnow() - timedelta(days=14)).isoformat()
            rows = (
                supabase.table("logs")
                .select("timestamp")
                .eq("user_id", user_id)
                .eq("action_type", "photo_analysis")
                .gte("timestamp", since)
                .execute()
                .data
            )
            total_analyses_14d = len(rows)
            active_days_14d = len({row["timestamp"][:10] for row in rows if row.get("timestamp")})

            unlocked = total_analyses_14d >= 21 or active_days_14d >= 10
            return {
                "unlocked": unlocked,
                "subscribed": False,  # Extend later with real subscription check
                "total_analyses_14d": total_analyses_14d,
                "active_days_14d": active_days_14d,
            }
        except Exception as e:
            logger.error(f"Failed to compute unlock status for {user_id}: {e}")
            return {
                "unlocked": False,
                "subscribed": False,
                "total_analyses_14d": 0,
                "active_days_14d": 0,
            }

    async def upsert_food_plan(self, user_id: str, plan_record: Dict[str, Any], force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Insert or update a meal plan for a given period.

        If an existing plan for the same (user_id, start_date, end_date) exists and force=False,
        the existing record is returned. Otherwise it is replaced.
        """
        if supabase is None:
            logger.warning("Supabase client missing; skipping upsert (dev env)")
            return plan_record | {"id": "dev-null"}

        start_date = plan_record.get("start_date")
        end_date = plan_record.get("end_date")
        if not start_date or not end_date:
            logger.error("Plan record must include start_date and end_date")
            return None

        try:
            # Check for existing
            existing = (
                supabase.table("meal_plans")
                .select("*")
                .eq("user_id", user_id)
                .eq("start_date", start_date)
                .eq("end_date", end_date)
                .execute()
                .data
            )
            if existing and not force:
                return existing[0]

            # Upsert (requires unique index on user_id,start_date,end_date)
            upserted = (
                supabase.table("meal_plans")
                .upsert(plan_record, on_conflict="user_id,start_date,end_date")
                .execute()
                .data
            )
            return (upserted[0] if upserted else None)
        except Exception as e:
            logger.error(f"Failed to upsert meal plan for {user_id}: {e}")
            return None

    async def get_food_plan_covering_date(self, user_id: str, day: date) -> Optional[Dict[str, Any]]:
        """Get a plan that covers the specified day, if any."""
        if supabase is None:
            return None
        try:
            rows = (
                supabase.table("meal_plans")
                .select("*")
                .eq("user_id", user_id)
                .lte("start_date", str(day))
                .gte("end_date", str(day))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
                .data
            )
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Failed to get plan covering {day} for {user_id}: {e}")
            return None

    async def get_latest_food_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recently created plan for the user."""
        if supabase is None:
            return None
        try:
            rows = (
                supabase.table("meal_plans")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
                .data
            )
            return rows[0] if rows else None
        except Exception as e:
            logger.error(f"Failed to get latest plan for {user_id}: {e}")
            return None


# Singleton-style instance used by routers
supabase_service = SupabaseService()


