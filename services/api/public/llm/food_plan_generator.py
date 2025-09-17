import os
from typing import Any, Dict, List
import httpx
from loguru import logger


class FoodPlanGenerator:
    """
    Minimal generator wrapper that either proxies to ML service or returns a
    deterministic fallback for development/tests.

    Contract per docs/food-plan/llm_prompt.md:
    - async generate_plan(profile, food_history, days) -> {
        plan_json, shopping_list_json, confidence?, model_used?
      }
    """

    def __init__(self) -> None:
        self.ml_service_url = os.getenv("ML_SERVICE_URL")

    async def generate_plan(self, profile: Dict[str, Any] | None, food_history: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        if self.ml_service_url:
            try:
                from shared.auth import get_auth_headers  # lazy import
                headers = get_auth_headers()
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{self.ml_service_url}/api/v1/food-plan/generate",
                        json={
                            "profile": profile or {},
                            "food_history": food_history or [],
                            "days": days,
                        },
                        headers=headers,
                    )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "plan_json": data.get("plan_json", {}),
                    "shopping_list_json": data.get("shopping_list_json", {}),
                    "confidence": data.get("confidence", 0.6),
                    "model_used": data.get("model_used", "ml-service"),
                }
            except Exception as e:
                logger.warning(f"ML service food-plan proxy failed, using fallback: {e}")
        # Fallback deterministic plan
        target = (profile or {}).get("daily_calories_target") or 2000
        per_meal = int(target // 4)
        plan = {}
        for d in range(1, days + 1):
            plan[f"day_{d}"] = {
                "breakfast": {"calories": per_meal, "protein": 20, "fats": 15, "carbs": 45, "text": "Oatmeal with berries"},
                "lunch": {"calories": per_meal, "protein": 25, "fats": 18, "carbs": 40, "text": "Chicken, rice, salad"},
                "dinner": {"calories": per_meal, "protein": 25, "fats": 18, "carbs": 40, "text": "Fish, quinoa, veggies"},
                "snack": {"calories": per_meal, "protein": 10, "fats": 10, "carbs": 25, "text": "Yogurt and nuts"},
                "summary": {},
            }
        shopping = {"items": ["oats", "berries", "chicken", "rice", "salad", "fish", "quinoa", "yogurt", "nuts"]}
        return {"plan_json": plan, "shopping_list_json": shopping, "confidence": 0.4, "model_used": "fallback"}


