from aiogram import types
from loguru import logger
import os
import httpx
from common.supabase_client import get_user_by_telegram_id
from shared.auth import get_auth_headers
from i18n.i18n import i18n


API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://api_public:8020")


async def start_food_plan_generation(callback: types.CallbackQuery):
    """Handle 'Create Food Plan' action: trigger 3‑day plan generation via Public API."""
    try:
        telegram_user_id = callback.from_user.id
        await callback.answer()

        user = await get_user_by_telegram_id(telegram_user_id)
        if not user:
            await callback.message.answer("❌ User not found. Please try again later.")
            return
        user_language = user.get("language", "en")

        # Inform user
        await callback.message.answer(i18n.get_text("food_plan_generating", user_language, default="🧠 Генерирую план питания на 3 дня..."))

        # Call Public API internal endpoint
        url = f"{API_PUBLIC_URL}/food-plan/generate-internal"
        payload = {"user_id": user["id"], "days": 3, "force": True}
        headers = get_auth_headers()
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Food plan API error: {resp.status_code} {resp.text}")
            await callback.message.answer(i18n.get_text("food_plan_failed", user_language, default="❌ Не удалось создать план питания. Попробуйте позже."))
            return

        data = resp.json()
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        plan_json = data.get("plan_json", {})
        shopping_list = data.get("shopping_list_json", {}).get("items", [])

        # Format the complete food plan
        text = f"✅ **План питания создан!**\n📅 Период: {start_date} — {end_date}\n\n"
        
        # Add each day's plan
        for day_key, day_data in plan_json.items():
            day_num = day_key.split("_")[1] if "_" in day_key else day_key
            text += f"**📅 День {day_num}**\n"
            
            # Add each meal
            for meal_key in ["breakfast", "lunch", "dinner", "snack"]:
                meal = day_data.get(meal_key, {})
                if meal:
                    meal_emoji = {"breakfast": "🌅", "lunch": "🌞", "dinner": "🌙", "snack": "🍎"}.get(meal_key, "🍽️")
                    text += f"{meal_emoji} **{meal_key.title()}**: {meal.get('text', 'N/A')}\n"
                    text += f"   🔥 {meal.get('calories', 0)} ккал | 🥩 {meal.get('protein', 0)}г белка | 🥑 {meal.get('fats', 0)}г жиров | 🍞 {meal.get('carbs', 0)}г углеводов\n\n"
            
            # Add daily totals
            summary = day_data.get("summary", {}).get("totals", {})
            if summary:
                text += f"📊 **Итого за день**: {summary.get('calories', 0)} ккал | {summary.get('protein', 0)}г белка | {summary.get('fats', 0)}г жиров | {summary.get('carbs', 0)}г углеводов\n\n"
        
        # Add shopping list
        if shopping_list:
            text += "🛒 **Список покупок**:\n"
            for item in shopping_list:
                text += f"• {item}\n"
        
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error generating food plan: {e}")
        await callback.message.answer("❌ Ошибка при создании плана питания.")


