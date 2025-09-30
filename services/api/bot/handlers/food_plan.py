from aiogram import types
from loguru import logger
import os
import httpx
from typing import Dict, Any
from common.supabase_client import get_user_by_telegram_id
from shared.auth import get_auth_headers
from i18n.i18n import i18n
from .keyboards import create_main_menu_keyboard


API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://api_public:8020")


async def check_user_onboarding_status(user_id: str) -> Dict[str, Any]:
    """Check if user has completed nutrition onboarding"""
    try:
        url = f"{API_PUBLIC_URL}/nutrition-onboarding/check-profile-internal"
        payload = {"user_id": user_id}
        headers = get_auth_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)

        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Onboarding check failed: {resp.status_code} {resp.text}")
            return {"has_profile": False, "needs_onboarding": True}

    except Exception as e:
        logger.error(f"Error checking onboarding status: {e}")
        return {"has_profile": False, "needs_onboarding": True}


async def start_food_plan_generation(callback: types.CallbackQuery):
    """Handle 'Create Food Plan' action: Check onboarding first, then generate plan."""
    try:
        telegram_user_id = callback.from_user.id
        await callback.answer()

        user = await get_user_by_telegram_id(telegram_user_id)
        if not user:
            await callback.message.answer("❌ User not found. Please try again later.")
            return
        user_language = user.get("language", "en")

        # Temporarily skip onboarding check and generate plan directly
        # TODO: Fix onboarding flow keyboard issues
        # onboarding_status = await check_user_onboarding_status(user["id"])
        # if not onboarding_status.get("has_profile", False):
        #     from .nutrition_onboarding_bot import start_nutrition_onboarding
        #     await start_nutrition_onboarding(callback, user, user_language)
        #     return

        # User has completed onboarding, proceed with enhanced meal plan
        await callback.message.answer(i18n.get_text("food_plan_generating", user_language, default="🧠 Генерирую персонализированный план питания на 3 дня..."))

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
        intro_summary = data.get("intro_summary")
        plan_json = data.get("plan_json", {})
        shopping_list = data.get("shopping_list_json", {})

        # Send introduction message with analysis
        intro_parts = [f"✅ **План питания создан!**\n📅 Период: {start_date} — {end_date}"]
        if intro_summary:
            # Escape Markdown characters in intro_summary to avoid parsing errors
            escaped_summary = intro_summary.replace("*", "\\*").replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
            intro_parts.append(f"**📊 Анализ:**\n{escaped_summary}")

        intro_text = "\n\n".join(intro_parts)
        await callback.message.answer(intro_text, parse_mode="Markdown")

        # Send each day as a separate message for better readability
        day_index = 0
        for day_key, day_data in plan_json.items():
            day_index += 1
            day_parts = [f"День {day_index}"]

            mapping = [
                ("breakfast", "Завтрак 08:00"),
                ("lunch", "Обед 13:00"),
                ("dinner", "Ужин 19:00"),
            ]

            for meal_key, meal_title in mapping:
                meal = day_data.get(meal_key)
                if not meal:
                    continue

                day_parts.append(f"\n{meal_title}")
                # Escape Markdown characters in meal text to avoid parsing errors
                meal_text = meal.get('text', '')
                escaped_meal_text = meal_text.replace("*", "\\*").replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
                day_parts.append(f"{escaped_meal_text}")
                day_parts.append(
                    f"⚡ {meal.get('calories',0)} ккал | 🥩 {meal.get('protein',0)}г | 🥑 {meal.get('fats',0)}г | 🍞 {meal.get('carbs',0)}г"
                )

                ings = meal.get("ingredients") or []
                if ings:
                    day_parts.append("Ингредиенты:")
                    for ing in ings:
                        day_parts.append(f"• {ing.get('name')} — {ing.get('amount')}{ing.get('unit')}")

            # Add daily totals
            summary = day_data.get("summary", {}).get("totals", {})
            if summary:
                day_parts.append(f"\nИтого за день:")
                day_parts.append(
                    f"⚡ {summary.get('calories',0)} ккал | 🥩 {summary.get('protein',0)}г | 🥑 {summary.get('fats',0)}г | 🍞 {summary.get('carbs',0)}г"
                )

            day_text = "\n".join(day_parts)
            await callback.message.answer(day_text, parse_mode="Markdown")

        # Send shopping list as a separate message
        if shopping_list:
            shopping_parts = ["Список покупок:"]
            if isinstance(shopping_list, dict):
                # categorized
                for cat, items in shopping_list.items():
                    shopping_parts.append(f"\n{cat}:")
                    for it in items:
                        shopping_parts.append(f"• {it.get('name')} — {it.get('amount')}{it.get('unit')}")
            else:
                # simple list fallback
                for item in shopping_list:
                    shopping_parts.append(f"• {item}")

            shopping_text = "\n".join(shopping_parts)

            # Create main menu keyboard for the final message
            main_menu_keyboard = create_main_menu_keyboard(user_language)
            await callback.message.answer(shopping_text, parse_mode="Markdown", reply_markup=main_menu_keyboard)
        else:
            # If no shopping list, add keyboard to the last day message
            main_menu_keyboard = create_main_menu_keyboard(user_language)
            await callback.message.answer("План питания готов!", reply_markup=main_menu_keyboard)
    except Exception as e:
        logger.error(f"Error generating food plan: {e}")

        # Get user for language
        user = await get_user_by_telegram_id(callback.from_user.id)
        user_language = user.get("language", "en") if user else "en"

        # Create main menu keyboard for navigation back
        main_menu_keyboard = create_main_menu_keyboard(user_language)

        await callback.message.answer(
            "❌ Ошибка при создании плана питания.",
            reply_markup=main_menu_keyboard
        )


