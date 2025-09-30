"""
Telegram Bot Handler for Nutrition Onboarding.
Manages the questionnaire flow and preference collection in Telegram.
"""
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from loguru import logger
import os
import httpx
from typing import Dict, Any, Optional

from common.supabase_client import get_user_by_telegram_id
from shared.auth import get_auth_headers
from i18n.i18n import i18n


API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://api_public:8020")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-app.com")


async def handle_create_food_plan_request(callback: types.CallbackQuery):
    """
    Handle 'Create Food Plan' button press.
    First checks if user has completed onboarding, if not - starts questionnaire.
    """
    try:
        telegram_user_id = callback.from_user.id
        await callback.answer()

        # Get user from database
        user = await get_user_by_telegram_id(telegram_user_id)
        if not user:
            await callback.message.answer("❌ Пользователь не найден. Попробуйте позже.")
            return

        user_language = user.get("language", "ru")

        # Check if user has completed nutrition onboarding
        onboarding_status = await check_user_onboarding_status(user["id"])

        if not onboarding_status["has_profile"]:
            # User needs onboarding - start questionnaire flow
            await start_nutrition_onboarding(callback, user, user_language)
        else:
            # User has profile - proceed with meal plan generation
            await proceed_to_meal_plan_generation(callback, user, user_language, onboarding_status)

    except Exception as e:
        logger.error(f"Error handling create food plan request: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")


async def start_nutrition_onboarding(callback: types.CallbackQuery, user: Dict[str, Any], language: str):
    """Start the nutrition onboarding process"""

    # Get questionnaire summary
    questionnaire_info = await get_questionnaire_summary(user["id"])

    if not questionnaire_info:
        await callback.message.answer("❌ Не удалось загрузить опросник. Попробуйте позже.")
        return

    # Create welcome message
    welcome_text = f"""🧬 **Добро пожаловать в персонализированное питание!**

Чтобы создать идеальный план питания именно для вас, давайте узнаем о ваших предпочтениях.

📋 **Что вас ждет:**
• {questionnaire_info['total_steps']} шагов
• ~{questionnaire_info['estimated_time']}
• Вопросы о ваших целях, вкусах и образе жизни

🎯 **Что вы получите:**
✅ План питания под ваши вкусы
✅ Учет всех ограничений и аллергий
✅ Рецепты по вашему времени готовки
✅ Режим под ваш график
✅ Рекомендации под ваши цели

Готовы начать персонализацию?"""

    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Button to start questionnaire in WebApp
    start_questionnaire_btn = InlineKeyboardButton(
        text="🚀 Начать опрос",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/nutrition-onboarding")
    )

    # Button for quick setup (basic questions)
    quick_setup_btn = InlineKeyboardButton(
        text="⚡ Быстрая настройка",
        callback_data="nutrition:quick_setup"
    )

    # Button to learn more
    learn_more_btn = InlineKeyboardButton(
        text="ℹ️ Подробнее",
        callback_data="nutrition:learn_more"
    )

    # Button to skip (use basic plan)
    skip_btn = InlineKeyboardButton(
        text="⏭️ Пропустить",
        callback_data="nutrition:skip_onboarding"
    )

    keyboard.add(start_questionnaire_btn)
    keyboard.add(quick_setup_btn, learn_more_btn)
    keyboard.add(skip_btn)

    await callback.message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def handle_quick_setup(callback: types.CallbackQuery):
    """Handle quick setup option - ask only essential questions in Telegram"""

    await callback.answer()

    quick_setup_text = """⚡ **Быстрая настройка**

Ответьте на несколько ключевых вопросов прямо здесь:"""

    # Start with the first question
    await ask_quick_question_goal(callback.message, callback.from_user.id)


async def ask_quick_question_goal(message: types.Message, telegram_user_id: int):
    """Ask about primary goal"""

    question_text = """🎯 **Вопрос 1 из 5**

Какая ваша основная цель в питании?"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    goals = [
        ("weight_loss", "🔽 Снижение веса"),
        ("muscle_gain", "💪 Набор мышечной массы"),
        ("maintenance", "⚖️ Поддержание формы"),
        ("health_improvement", "❤️ Улучшение здоровья"),
        ("energy_boost", "⚡ Больше энергии")
    ]

    for goal_id, goal_label in goals:
        keyboard.add(InlineKeyboardButton(
            text=goal_label,
            callback_data=f"quick:goal:{goal_id}"
        ))

    await message.answer(question_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_quick_goal_selection(callback: types.CallbackQuery):
    """Handle goal selection in quick setup"""

    await callback.answer()

    goal = callback.data.split(":")[-1]

    # Store response temporarily
    await store_quick_response(callback.from_user.id, "primary_goal", goal)

    # Move to next question
    await ask_quick_question_dietary_restrictions(callback.message, callback.from_user.id)


async def ask_quick_question_dietary_restrictions(message: types.Message, telegram_user_id: int):
    """Ask about dietary restrictions"""

    question_text = """🚫 **Вопрос 2 из 5**

Есть ли у вас ограничения в питании?"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    restrictions = [
        ("none", "✅ Нет ограничений"),
        ("vegetarian", "🥬 Вегетарианство"),
        ("vegan", "🌱 Веганство"),
        ("gluten_free", "🌾 Без глютена"),
        ("dairy_free", "🥛 Без молочных"),
        ("other", "❓ Другие")
    ]

    for rest_id, rest_label in restrictions:
        keyboard.add(InlineKeyboardButton(
            text=rest_label,
            callback_data=f"quick:dietary:{rest_id}"
        ))

    await message.edit_text(question_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_quick_dietary_selection(callback: types.CallbackQuery):
    """Handle dietary restrictions selection"""

    await callback.answer()

    dietary = callback.data.split(":")[-1]
    await store_quick_response(callback.from_user.id, "dietary_type", [dietary])

    await ask_quick_question_cooking_time(callback.message, callback.from_user.id)


async def ask_quick_question_cooking_time(message: types.Message, telegram_user_id: int):
    """Ask about cooking time"""

    question_text = """⏱️ **Вопрос 3 из 5**

Сколько времени готовы тратить на готовку?"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    times = [
        ("minimal", "⚡ 10-20 минут (быстрые блюда)"),
        ("moderate", "⏰ 30-45 минут (умеренно)"),
        ("generous", "🍳 1+ час (люблю готовить)")
    ]

    for time_id, time_label in times:
        keyboard.add(InlineKeyboardButton(
            text=time_label,
            callback_data=f"quick:cooking_time:{time_id}"
        ))

    await message.edit_text(question_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_quick_cooking_time_selection(callback: types.CallbackQuery):
    """Handle cooking time selection"""

    await callback.answer()

    cooking_time = callback.data.split(":")[-1]
    await store_quick_response(callback.from_user.id, "cooking_time", cooking_time)

    await ask_quick_question_activity_level(callback.message, callback.from_user.id)


async def ask_quick_question_activity_level(message: types.Message, telegram_user_id: int):
    """Ask about activity level"""

    question_text = """🏃‍♀️ **Вопрос 4 из 5**

Какой у вас уровень физической активности?"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    activities = [
        ("sedentary", "🪑 Сидячий образ жизни"),
        ("light", "🚶 Легкая активность (1-3 раза в неделю)"),
        ("moderate", "🏃 Умеренная (3-5 раз в неделю)"),
        ("high", "💪 Высокая (6-7 раз в неделю)")
    ]

    for activity_id, activity_label in activities:
        keyboard.add(InlineKeyboardButton(
            text=activity_label,
            callback_data=f"quick:activity:{activity_id}"
        ))

    await message.edit_text(question_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_quick_activity_selection(callback: types.CallbackQuery):
    """Handle activity level selection"""

    await callback.answer()

    activity = callback.data.split(":")[-1]
    await store_quick_response(callback.from_user.id, "activity_level", activity)

    await ask_quick_question_meal_frequency(callback.message, callback.from_user.id)


async def ask_quick_question_meal_frequency(message: types.Message, telegram_user_id: int):
    """Ask about meal frequency"""

    question_text = """🍽️ **Вопрос 5 из 5**

Как часто предпочитаете есть?"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    frequencies = [
        ("3_meals", "🍽️ 3 основных приема пищи"),
        ("5_small", "🥄 5-6 небольших приемов"),
        ("2_meals", "⏰ 2 основных приема (интервальное голодание)"),
        ("flexible", "🔄 Гибкий график")
    ]

    for freq_id, freq_label in frequencies:
        keyboard.add(InlineKeyboardButton(
            text=freq_label,
            callback_data=f"quick:frequency:{freq_id}"
        ))

    await message.edit_text(question_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_quick_frequency_selection(callback: types.CallbackQuery):
    """Handle meal frequency selection and complete quick setup"""

    await callback.answer()

    frequency = callback.data.split(":")[-1]
    await store_quick_response(callback.from_user.id, "eating_frequency", frequency)

    # Complete quick setup
    await complete_quick_setup(callback)


async def complete_quick_setup(callback: types.CallbackQuery):
    """Complete quick setup and generate meal plan"""

    try:
        telegram_user_id = callback.from_user.id

        # Get user from database
        user = await get_user_by_telegram_id(telegram_user_id)
        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден.")
            return

        # Get stored responses
        quick_responses = await get_quick_responses(telegram_user_id)

        if not quick_responses:
            await callback.message.edit_text("❌ Ошибка: не удалось получить ответы.")
            return

        # Submit responses to create basic preferences
        success = await submit_quick_responses(user["id"], quick_responses)

        if success:
            completion_text = """✅ **Быстрая настройка завершена!**

Ваши предпочтения сохранены. Теперь создаем персонализированный план питания...

💡 *Совет: позже вы можете пройти полный опрос для максимальной персонализации.*"""

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text="🍽️ Создать план питания",
                callback_data="nutrition:generate_plan"
            ))

            await callback.message.edit_text(
                completion_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )

            # Clean up temporary storage
            await clear_quick_responses(telegram_user_id)

        else:
            await callback.message.edit_text("❌ Ошибка при сохранении предпочтений. Попробуйте позже.")

    except Exception as e:
        logger.error(f"Error completing quick setup: {e}")
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже.")


async def handle_learn_more(callback: types.CallbackQuery):
    """Show more information about personalized nutrition"""

    await callback.answer()

    learn_more_text = """📚 **Персонализированное питание**

🧬 **Nutrition DNA**
Мы анализируем ваши пищевые привычки и создаем уникальный "генетический код" питания - ваш Nutrition DNA. Это позволяет понять:

• Ваш архетип питания (8 типов)
• Временные паттерны (когда вы едите)
• Социальные триггеры (как окружение влияет на выбор пищи)
• Стрессовые реакции и эмоциональное питание

🎯 **Предиктивная аналитика**
Система предсказывает:
• Моменты риска (когда вы можете сорваться)
• Оптимальное время для приемов пищи
• Вероятность успеха в достижении целей
• Персональные рекомендации на каждый день

📊 **Что учитывается:**
✅ Ваши вкусовые предпочтения
✅ Аллергии и ограничения
✅ Рабочий график и образ жизни
✅ Кулинарные навыки
✅ Время на готовку
✅ Социальные привычки
✅ Цели и мотивация

Готовы создать свой уникальный план?"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="🚀 Начать полный опрос",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}/nutrition-onboarding")
    ))
    keyboard.add(InlineKeyboardButton(
        text="⚡ Быстрая настройка",
        callback_data="nutrition:quick_setup"
    ))
    keyboard.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="nutrition:back_to_welcome"
    ))

    await callback.message.edit_text(
        learn_more_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def handle_skip_onboarding(callback: types.CallbackQuery):
    """Handle skip onboarding - create basic plan"""

    await callback.answer()

    skip_text = """⏭️ **Пропустить персонализацию**

Вы можете создать базовый план питания без персонализации, но он будет менее точным.

**Базовый план включает:**
✅ Стандартные здоровые рецепты
✅ Сбалансированное питание
✅ Основные макронутриенты

**Что вы упустите:**
❌ Учет ваших вкусов
❌ Адаптация под график
❌ Персональные рекомендации
❌ Прогнозы поведения

Уверены, что хотите пропустить?"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="✅ Да, создать базовый план",
        callback_data="nutrition:create_basic_plan"
    ))
    keyboard.add(InlineKeyboardButton(
        text="🚀 Нет, пройти опрос",
        callback_data="nutrition:back_to_welcome"
    ))

    await callback.message.edit_text(
        skip_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def handle_create_basic_plan(callback: types.CallbackQuery):
    """Create basic meal plan without personalization"""

    await callback.answer()

    try:
        telegram_user_id = callback.from_user.id
        user = await get_user_by_telegram_id(telegram_user_id)

        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return

        # Use the existing food plan generation
        from ..food_plan import start_food_plan_generation

        # Create a mock callback for the existing function
        mock_callback = types.CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            message=callback.message,
            data="create_food_plan"
        )

        await start_food_plan_generation(mock_callback)

    except Exception as e:
        logger.error(f"Error creating basic plan: {e}")
        await callback.message.edit_text("❌ Ошибка при создании плана. Попробуйте позже.")


# Helper functions

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
            logger.error(f"Failed to check onboarding status: {resp.status_code}")
            return {"has_profile": False, "needs_onboarding": True}

    except Exception as e:
        logger.error(f"Error checking onboarding status: {e}")
        return {"has_profile": False, "needs_onboarding": True}


async def get_questionnaire_summary(user_id: str) -> Optional[Dict[str, Any]]:
    """Get questionnaire summary"""

    try:
        url = f"{API_PUBLIC_URL}/nutrition-onboarding/questionnaire-summary"
        headers = get_auth_headers()
        headers["X-User-ID"] = user_id  # Add user ID to headers

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Failed to get questionnaire summary: {resp.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error getting questionnaire summary: {e}")
        return None


async def proceed_to_meal_plan_generation(callback: types.CallbackQuery, user: Dict[str, Any], language: str, onboarding_status: Dict[str, Any]):
    """Proceed with meal plan generation for user with completed profile"""

    preferences_summary = onboarding_status.get("preferences_summary", "")

    welcome_back_text = f"""✅ **Ваш профиль готов!**

{preferences_summary}

Создаю персонализированный план питания на 3 дня..."""

    await callback.message.edit_text(welcome_back_text, parse_mode="Markdown")

    # Use the existing enhanced food plan generation
    from ..food_plan import start_food_plan_generation
    await start_food_plan_generation(callback)


# Quick setup temporary storage functions (in production, use Redis or database)
_quick_responses_storage = {}

async def store_quick_response(telegram_user_id: int, question_id: str, value: Any):
    """Store quick response temporarily"""
    if telegram_user_id not in _quick_responses_storage:
        _quick_responses_storage[telegram_user_id] = {}
    _quick_responses_storage[telegram_user_id][question_id] = value


async def get_quick_responses(telegram_user_id: int) -> Dict[str, Any]:
    """Get stored quick responses"""
    return _quick_responses_storage.get(telegram_user_id, {})


async def clear_quick_responses(telegram_user_id: int):
    """Clear stored quick responses"""
    if telegram_user_id in _quick_responses_storage:
        del _quick_responses_storage[telegram_user_id]


async def submit_quick_responses(user_id: str, responses: Dict[str, Any]) -> bool:
    """Submit quick setup responses to API"""

    try:
        # Convert responses to API format
        response_list = []
        for question_id, value in responses.items():
            response_list.append({
                "question_id": question_id,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })

        url = f"{API_PUBLIC_URL}/nutrition-onboarding/responses"
        payload = {"responses": response_list}
        headers = get_auth_headers()
        headers["X-User-ID"] = user_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)

        return resp.status_code == 200

    except Exception as e:
        logger.error(f"Error submitting quick responses: {e}")
        return False