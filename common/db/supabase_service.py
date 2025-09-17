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
        if supabase is None:
            logger.warning("Supabase client is not configured; returning empty context")
            return {
                "profile": None,
                "food_history": [],
                "history_summary": {},
            }

        # Profile
        try:
            profile_rows = (
                supabase.table("user_profiles").select("*").eq("user_id", user_id).execute().data
            )
            profile = profile_rows[0] if profile_rows else None
        except Exception as e:
            logger.error(f"Failed to fetch profile for user {user_id}: {e}")
            profile = None

        # Recent history (30 days) from logs
        try:
            since = (datetime.utcnow() - timedelta(days=30)).isoformat()
            logs = (
                supabase.table("logs")
                .select("timestamp, kbzhu, metadata")
                .eq("user_id", user_id)
                .eq("action_type", "photo_analysis")
                .gte("timestamp", since)
                .order("timestamp", desc=False)
                .execute()
                .data
            )
        except Exception as e:
            logger.error(f"Failed to fetch logs for user {user_id}: {e}")
            logs = []

        # Summarize history
        try:
            total_analyses = len(logs)
            active_days = len({row["timestamp"][:10] for row in logs if row.get("timestamp")})
            history_summary = {
                "total_analyses_30d": total_analyses,
                "active_days_30d": active_days,
            }
        except Exception:
            history_summary = {}

        return {
            "profile": profile,
            "food_history": logs,
            "history_summary": history_summary,
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


