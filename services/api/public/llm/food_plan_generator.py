import os
from typing import Any, Dict, List
import httpx
from loguru import logger


class FoodPlanGenerator:
    """
    Enhanced generator wrapper that either proxies to ML service, uses AI enhancement,
    or returns a deterministic fallback for development/tests.

    Contract per docs/food-plan/llm_prompt.md:
    - async generate_plan(profile, food_history, days) -> {
        plan_json, shopping_list_json, confidence?, model_used?
      }
    """

    def __init__(self) -> None:
        self.ml_service_url = os.getenv("ML_SERVICE_URL")
        self.use_enhanced_ai = os.getenv("USE_ENHANCED_AI", "true").lower() == "true"

        if self.use_enhanced_ai:
            try:
                from ..llm.enhanced_food_plan_generator import EnhancedFoodPlanGenerator
                self.enhanced_generator = EnhancedFoodPlanGenerator()
                logger.info("Enhanced AI food plan generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize enhanced generator: {e}")
                self.enhanced_generator = None
                self.use_enhanced_ai = False
        else:
            self.enhanced_generator = None

    async def generate_plan(self, profile: Dict[str, Any] | None, food_history: List[Dict[str, Any]], days: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Try enhanced AI generator first if enabled
        if self.use_enhanced_ai and self.enhanced_generator:
            try:
                logger.info("Using enhanced AI food plan generator")
                result = await self.enhanced_generator.generate_enhanced_plan(
                    profile or {}, food_history, days, context
                )
                return result
            except Exception as e:
                logger.warning(f"Enhanced AI generator failed, falling back: {e}")

        # Try ML service
        if self.ml_service_url:
            try:
                from shared.auth import get_auth_headers  # lazy import
                headers = get_auth_headers()
                payload = {
                    "profile": profile or {},
                    "food_history": food_history or [],
                    "days": days,
                }
                if context:
                    payload["context"] = context

                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{self.ml_service_url}/api/v1/food-plan/generate",
                        json=payload,
                        headers=headers,
                    )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "intro_summary": data.get("intro_summary"),
                    "plan_json": data.get("plan_json", {}),
                    "shopping_list_json": data.get("shopping_list_json", {}),
                    "confidence": data.get("confidence", 0.6),
                    "model_used": data.get("model_used", "ml-service"),
                }
            except Exception as e:
                logger.warning(f"ML service food-plan proxy failed, using fallback: {e}")
        # Fallback deterministic plan
        # Fallback with summary, diversification and kcal variance
        target = (profile or {}).get("daily_calories_target") or 2000
        try:
            target = int(target)
        except Exception:
            target = 2000
        goal = (profile or {}).get("goal") or "поддержание здоровья"
        intro_summary = (
            f"За последние недели вы поддерживали стабильный рацион. С учётом цели ({str(goal).lower()}) "
            f"я подготовил персональный план питания на {days} дня."
        )
        breakfasts = ["Овсянка с ягодами", "Омлет с овощами", "Тосты с авокадо и яйцом"]
        lunches = ["Куриное филе с гречкой и овощами", "Индейка с киноа и салатом", "Лосось с рисом и брокколи"]
        dinners = ["Треска с овощами на пару", "Паста из цельнозерновой муки с индейкой", "Овощное рагу с чечевицей"]
        deltas = [-150, 0, 150]
        def macros(c):
            return {"protein": int(c*0.2/4), "fats": int(c*0.3/9), "carbs": int(c*0.5/4)}
        plan = {}
        for d in range(1, days + 1):
            daily = max(1200, int(target + deltas[(d-1)%len(deltas)]))
            b_cal, l_cal = int(daily*0.3), int(daily*0.4)
            d_cal = daily - b_cal - l_cal
            plan[f"day_{d}"] = {
                "breakfast": {"calories": b_cal, **macros(b_cal), "text": f"{breakfasts[(d-1)%len(breakfasts)]} — сбалансированное начало дня.", "ingredients": []},
                "lunch": {"calories": l_cal, **macros(l_cal), "text": f"{lunches[(d-1)%len(lunches)]} — энергия для продуктивного дня.", "ingredients": []},
                "dinner": {"calories": d_cal, **macros(d_cal), "text": f"{dinners[(d-1)%len(dinners)]} — лёгкий ужин для восстановления.", "ingredients": []},
                "summary": {},
            }
        shopping = {"Злаки": [{"name": "овсянка", "amount": 300, "unit": "г"}, {"name": "рис", "amount": 300, "unit": "г"}, {"name": "киноа", "amount": 200, "unit": "г"}],
                    "Белки": [{"name": "яйца", "amount": 6, "unit": "шт"}, {"name": "курица", "amount": 700, "unit": "г"}, {"name": "индейка", "amount": 600, "unit": "г"}, {"name": "лосось", "amount": 500, "unit": "г"}, {"name": "чечевица", "amount": 200, "unit": "г"}],
                    "Овощи": [{"name": "овощи", "amount": 1500, "unit": "г"}]}
        return {"intro_summary": intro_summary, "plan_json": plan, "shopping_list_json": shopping, "confidence": 0.5, "model_used": "fallback"}


