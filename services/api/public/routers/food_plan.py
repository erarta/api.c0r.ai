import os
from datetime import datetime, timedelta
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from common.db.supabase_service import supabase_service
from deps import require_auth_context, AuthContext, require_internal_auth
from common.cache.redis_client import get_async_redis, make_cache_key
from common.config.feature_flags import feature_flags

try:
    from llm.food_plan_generator import FoodPlanGenerator as FoodPlanGenerator
except Exception:
    from llm.meal_plan_generator import MealPlanGenerator

router = APIRouter()


class GenerateFoodPlanRequest(BaseModel):
    days: int = Field(default=3, ge=1, le=7)
    user_id: str = Field(description="User ID for internal API calls")
    force: bool = Field(default=False, description="Force regenerate and overwrite existing plan for the same period")


def ensure_day_totals(plan_json):
    """Compute per-day totals if missing (server-side safety)."""
    if not isinstance(plan_json, dict):
        return plan_json
    for day_key, day_data in plan_json.items():
        if not isinstance(day_data, dict):
            continue
        totals = {"calories": 0, "protein": 0, "fats": 0, "carbs": 0}
        for meal_key in ("breakfast", "lunch", "dinner", "snack"):
            meal = day_data.get(meal_key)
            if isinstance(meal, dict):
                try:
                    totals["calories"] += int(meal.get("calories", 0) or 0)
                    totals["protein"] += int(meal.get("protein", 0) or 0)
                    totals["fats"] += int(meal.get("fats", 0) or 0)
                    totals["carbs"] += int(meal.get("carbs", 0) or 0)
                except Exception:
                    pass
        summary = day_data.get("summary") or {}
        # Always overwrite with server-computed totals to avoid LLM static examples
        summary["totals"] = totals
        day_data["summary"] = summary
    return plan_json


@router.post("/food-plan/generate", response_model=dict)
async def generate_food_plan(payload: GenerateFoodPlanRequest, auth: AuthContext = Depends(require_auth_context)):
    """Generate personalized meal plan using centralized Supabase service"""
    
    # 1) Get comprehensive user context (profile, history, unlock status)
    try:
        context = await supabase_service.get_food_plan_context(auth['user_id'])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    profile = context['profile']
    food_history = context['food_history']
    history_summary = context['history_summary']
    history_by_day = context.get('history_by_day')
    
    # 2) Check unlock status
    unlock_status = await supabase_service.check_food_plan_unlock_status(
        auth['user_id'], 
        feature_flags.BYPASS_SUBSCRIPTION
    )
    
    if not unlock_status['unlocked']:
        if not unlock_status['subscribed']:
            raise HTTPException(status_code=402, detail="Subscription required")
        else:
            raise HTTPException(
                status_code=403, 
                detail=f"Unlock after 21 analyses or 14 days with 10 active days. "
                       f"Current: {unlock_status['total_analyses_14d']} analyses, "
                       f"{unlock_status['active_days_14d']} active days"
            )
    
    # 3) Cache history summary for future use
    redis = await get_async_redis()
    cache_key = make_cache_key("meal_history_30d", {"user": auth["user_id"]})
    try:
        await redis.setex(cache_key, 48 * 3600, json.dumps(history_summary, ensure_ascii=False))
    except Exception:
        pass
    
    # 4) Generate meal plan using LLM with full context
    generator = FoodPlanGenerator()
    generated_plan = await generator.generate_plan(profile, food_history, payload.days)
    
    # 5) Compute per-day totals server-side
    generated_plan["plan_json"] = ensure_day_totals(generated_plan.get("plan_json", {}))
    
    # 6) Save to database using centralized service
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=payload.days - 1)
    
    plan_record = {
        "user_id": auth['user_id'],
        "start_date": str(start_date),
        "end_date": str(end_date),
        "plan_json": generated_plan.get("plan_json", {}),
        "shopping_list_json": generated_plan.get("shopping_list_json", {}),
        "intro_summary": generated_plan.get("intro_summary"),
        "generated_from": "llm_generated"
    }
    
    result = await supabase_service.upsert_food_plan(auth['user_id'], plan_record, payload.force)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save meal plan")
    
    # Add generation metadata
    result["confidence"] = generated_plan.get("confidence", 0.5)
    result["model_used"] = generated_plan.get("model_used", "unknown")
    
    return result


@router.post("/food-plan/generate-internal", response_model=dict)
@require_internal_auth
async def generate_food_plan_internal(request: Request, payload: GenerateFoodPlanRequest):
    """Internal endpoint for bot to generate meal plan using centralized service"""
    
    user_id = payload.user_id
    
    # 1) Get comprehensive user context
    try:
        context = await supabase_service.get_food_plan_context(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    profile = context['profile']
    food_history = context['food_history']
    history_summary = context['history_summary']
    
    # 2) Check unlock status
    unlock_status = await supabase_service.check_food_plan_unlock_status(
        user_id, 
        feature_flags.BYPASS_SUBSCRIPTION
    )
    
    if not unlock_status['unlocked']:
        if not unlock_status['subscribed']:
            raise HTTPException(status_code=402, detail="Subscription required")
        else:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient analysis history. "
                       f"Current: {unlock_status['total_analyses_14d']} analyses, "
                       f"{unlock_status['active_days_14d']} active days"
            )
    
    # 3) Cache history summary
    redis = await get_async_redis()
    cache_key = make_cache_key("meal_history_7d", {"user": user_id})
    try:
        await redis.setex(cache_key, 48 * 3600, json.dumps({
            "summary": history_summary,
            "by_day": history_by_day,
        }, ensure_ascii=False))
    except Exception:
        pass
    
    # 4) Generate meal plan using LLM with full context
    generator = FoodPlanGenerator()
    generated_plan = await generator.generate_plan(profile, food_history, payload.days)
    
    # 5) Compute per-day totals server-side
    generated_plan["plan_json"] = ensure_day_totals(generated_plan.get("plan_json", {}))
    
    # 6) Save to database using centralized service
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=payload.days - 1)
    
    plan_record = {
        "user_id": user_id,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "plan_json": generated_plan.get("plan_json", {}),
        "shopping_list_json": generated_plan.get("shopping_list_json", {}),
        "intro_summary": generated_plan.get("intro_summary"),
        "generated_from": "llm_generated"
    }
    
    result = await supabase_service.upsert_food_plan(user_id, plan_record, payload.force)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save meal plan")
    
    # Add generation metadata
    result["confidence"] = generated_plan.get("confidence", 0.5)
    result["model_used"] = generated_plan.get("model_used", "unknown")
    
    return result


@router.get("/food-plan/current", response_model=dict)
async def get_current_meal_plan(auth: AuthContext = Depends(require_auth_context)):
    """Get current meal plan using centralized service"""
    today = datetime.utcnow().date()
    
    # Try to get plan covering today
    plan = await supabase_service.get_food_plan_covering_date(auth['user_id'], today)
    if plan:
        return plan
    
    # Fallback: get latest plan
    plan = await supabase_service.get_latest_food_plan(auth['user_id'])
    return plan or {}


@router.get("/food-plan/current-internal", response_model=dict)
async def get_current_meal_plan_internal(user_id: str, auth: dict = Depends(require_internal_auth)):
    """Get current meal plan for internal API using centralized service"""
    today = datetime.utcnow().date()
    
    # Try to get plan covering today
    plan = await supabase_service.get_food_plan_covering_date(user_id, today)
    if plan:
        return plan
    
    # Fallback: get latest plan
    plan = await supabase_service.get_latest_food_plan(user_id)
    return plan or {}


@router.get("/food-plan/unlock-status-internal", response_model=dict)
async def get_meal_plan_unlock_status_internal(user_id: str, auth: dict = Depends(require_internal_auth)):
    """Get meal plan unlock status using centralized service"""
    return await supabase_service.check_food_plan_unlock_status(
        user_id, 
        feature_flags.BYPASS_SUBSCRIPTION
    )


