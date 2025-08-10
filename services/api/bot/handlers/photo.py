"""
Photo processing handler for c0r.ai bot
Handles food photo analysis and nutrition information
"""
import os
import httpx
from aiogram import types
from aiogram.fsm.context import FSMContext
from loguru import logger
from common.routes import Routes
from common.supabase_client import get_or_create_user, decrement_credits, get_user_with_profile, log_user_action
from common.calories_manager import add_calories_from_analysis, get_daily_calories
from services.api.bot.utils.r2 import upload_telegram_photo
from .keyboards import create_main_menu_keyboard
from aiogram.filters import StateFilter
import re
from typing import List, Tuple, Optional
from aiogram.fsm.state import State, StatesGroup
from common.db.logs import get_latest_photo_analysis_log_id
from i18n.i18n import i18n
from services.api.bot.config import PAYMENT_PLANS
from .nutrition import sanitize_markdown_text

# All values must be set in .env file
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

def _is_generic_points(points: Optional[List[str]], user_language: str) -> bool:
    if not points:
        return True
    if user_language == 'ru':
        joined = ' '.join(points)
        only_ascii = re.fullmatch(r"[\x00-\x7F\s.,!?'\-:;()]+", joined or '') is not None
        too_short = len(points) <= 1 and len(points[0]) <= 20
        common = any(p.strip().lower() in {'nutritious meal', 'healthy choice', 'add more vegetables'} for p in points)
        return only_ascii or too_short or common
    return len(points) == 1 and len(points[0]) < 16


def _generate_personalized_points(total_nutrition: dict, profile: Optional[dict], user_language: str) -> Tuple[List[str], List[str]]:
    def t(ru: str, en: str) -> str:
        return ru if user_language == 'ru' else en
    def to_float(v) -> float:
        try:
            return float(v)
        except Exception:
            return 0.0
    cals = to_float(total_nutrition.get('calories'))
    prot = to_float(total_nutrition.get('proteins'))
    fats = to_float(total_nutrition.get('fats'))
    carbs = to_float(total_nutrition.get('carbohydrates'))
    sugar = to_float(total_nutrition.get('sugars'))
    fiber = to_float(total_nutrition.get('fiber'))
    salt = to_float(total_nutrition.get('salt'))
    sat_fat = to_float(total_nutrition.get('saturated_fat'))
    goal = (profile or {}).get('goal') if profile else None
    positives: List[str] = []
    improvements: List[str] = []
    if prot >= 20:
        positives.append(t('Высокое содержание белка — поддерживает сытость', 'High protein — supports satiety'))
    if fiber >= 5:
        positives.append(t('Много клетчатки — хорошо для пищеварения', 'High in fiber — good for digestion'))
    if sugar > 0 and sugar <= 10:
        positives.append(t('Низкое содержание сахара', 'Low sugar'))
    if salt > 0 and salt <= 0.5:
        positives.append(t('Низкая соль', 'Low salt'))
    if cals <= 450:
        positives.append(t('Умеренная калорийность блюда', 'Moderate total calories'))
    if 15 <= fats <= 35 and 15 <= prot <= 40 and 20 <= carbs <= 60:
        positives.append(t('Сбалансированные макроэлементы', 'Balanced macros'))
    if sat_fat >= 12 or fats >= 40:
        improvements.append(t('Понизь долю насыщенных жиров: меньше сыра/масла', 'Reduce saturated fat: less cheese/butter'))
    if salt >= 2.0:
        improvements.append(t('Слишком много соли — выбери менее солёные ингредиенты', 'Too much salt — choose lower-salt ingredients'))
    if fiber < 5:
        improvements.append(t('Добавь овощи/зелень для клетчатки и микронутриентов', 'Add vegetables/greens for fiber and micronutrients'))
    if goal == 'gain_weight' and cals < 600:
        improvements.append(t('Для набора — добавь сложные углеводы (крупы/хлеб цельнозерн.)', 'For gain — add complex carbs (grains/wholegrain bread)'))
    if goal == 'lose_weight' and cals >= 600:
        improvements.append(t('Для снижения веса — уменьшай порцию или калорийные добавки', 'For weight loss — reduce portion or high-calorie add‑ons'))
    def dedup(items: List[str]) -> List[str]:
        seen = set(); out: List[str] = []
        for it in items:
            k = it.lower()
            if k in seen:
                continue
            seen.add(k); out.append(it)
        return out[:3]
    return dedup(positives), dedup(improvements)


# Helper to format rich analysis result from ML service
def format_analysis_result(result: dict, user_language: str = 'en', profile: Optional[dict] = None) -> str:
    message_parts = []
    
    # Start with random creative success message with LLM provider
    creative_header = i18n.get_random_header("analysis_complete_headers", user_language)
    
    # Add LLM provider info to header
    llm_provider = result.get("analysis", {}).get("llm_provider", "unknown")
    model_used = result.get("analysis", {}).get("model_used", "")
    
    # Just use the creative header without provider information
    header_with_provider = creative_header
    
    message_parts.append(header_with_provider)
    message_parts.append("")  # Empty line
    
    # We now expect the analysis format from ML service
    if "analysis" in result and isinstance(result["analysis"], dict):
        analysis = result["analysis"]
        
        # Add regional dish identification at the beginning
        if "regional_analysis" in analysis:
            regional_info = analysis["regional_analysis"]
            dish_type = regional_info.get("dish_identification", "")
            # Fallback naming when provider returns generic/unknown
            if dish_type in ("", "Unknown", "Unknown Dish", "Analyzed Dish"):
                if "food_items" in analysis and analysis["food_items"]:
                    food_names = [item.get("name", "").lower() for item in analysis["food_items"][:3] if item.get("name")]
                    if food_names:
                        dish_type = (f"салат с {', '.join(food_names)}" if user_language == "ru" else f"salad with {', '.join(food_names)}")
                        regional_info["dish_identification"] = dish_type
            confidence = regional_info.get("regional_match_confidence", 0)
            
            # Always show dish name, even with low confidence
            if dish_type and dish_type != "Analyzed Dish":
                if user_language == "ru":
                    message_parts.append(f"🌍 Блюдо: {dish_type}")
                else:
                    message_parts.append(f"🌍 Dish: {dish_type}")
            else:
                # Already has a usable dish name
                pass
            
            message_parts.append("")  # Empty line
        
        # Add food items breakdown - first show all items by calories, then benefits
        if "food_items" in analysis and analysis["food_items"]:
            # Sort food items by calories (highest first)
            sorted_items = sorted(analysis["food_items"], key=lambda x: x.get("calories", 0), reverse=True)
            
            if user_language == "ru":
                message_parts.append("🥘 Обнаруженные продукты:")
            else:
                message_parts.append("🥘 Detected food items:")
            
            # First pass: show all items with their emojis and calories
            for item in sorted_items:
                name = item.get("name", "Unknown")
                weight_grams = item.get("weight_grams", 0)
                calories = item.get("calories", 0)
                emoji = item.get("emoji", "🍽️")  # Default emoji if not provided
                
                # Use language-aware weight and calorie units
                weight_unit = "г" if user_language == "ru" else "g"
                calorie_unit = "ккал" if user_language == "ru" else "kcal"
                message_parts.append(f"• {emoji} {name} ({weight_grams}{weight_unit}) - {calories} {calorie_unit}")
            
            message_parts.append("")  # Empty line
            
            # Second pass: show health benefits for each item
            if user_language == "ru":
                message_parts.append("💚 Польза продуктов:")
            else:
                message_parts.append("💚 Health Benefits:")
            
            for item in sorted_items:
                name = item.get("name", "Unknown")
                emoji = item.get("emoji", "🍽️")
                health_benefits = item.get("health_benefits", "")
                if health_benefits:
                    message_parts.append(f"  {emoji} {name}: {health_benefits}")
            
            message_parts.append("")  # Empty line
        
        # Add total nutrition
        if "total_nutrition" in analysis:
            nutrition = analysis["total_nutrition"]
            if user_language == "ru":
                message_parts.append("🍽️ Общая питательность:")
                message_parts.append(f"Калории: {nutrition.get('calories', '?')} ккал")
                message_parts.append(f"Белки: {nutrition.get('proteins', '?')} г")
                message_parts.append(f"Жиры: {nutrition.get('fats', '?')} г")
                message_parts.append(f"Углеводы: {nutrition.get('carbohydrates', '?')} г")
            else:
                message_parts.append("🍽️ Total nutrition:")
                message_parts.append(f"Calories: {nutrition.get('calories', '?')} kcal")
                message_parts.append(f"Proteins: {nutrition.get('proteins', '?')} g")
                message_parts.append(f"Fats: {nutrition.get('fats', '?')} g")
                message_parts.append(f"Carbohydrates: {nutrition.get('carbohydrates', '?')} g")
        
        message_parts.append("")  # Empty line
        
        # Add nutrition analysis if available
        if "nutrition_analysis" in analysis:
            nutrition_analysis = analysis["nutrition_analysis"]
            
            if user_language == "ru":
                message_parts.append("🧬 Анализ питательности:")
            else:
                message_parts.append("🧬 Nutrition Analysis:")
            
            health_score = nutrition_analysis.get("health_score", 5)
            if user_language == "ru":
                message_parts.append(f"📊 Рейтинг здоровости: {health_score}/10")
            else:
                message_parts.append(f"📊 Health Rating: {health_score}/10")
            
            message_parts.append("")  # Empty line
            
            # Add what's good about the meal (replace generic with personalized if needed)
            positive_aspects = nutrition_analysis.get("positive_aspects", [])
            if positive_aspects:
                if user_language == "ru":
                    message_parts.append("💪 Что хорошо в этом блюде:")
                else:
                    message_parts.append("💪 What's great about this meal:")
                
                # Handle both string and list formats
                if isinstance(positive_aspects, str):
                    # If it's a string, split by commas or use as single item
                    aspects = [aspect.strip() for aspect in positive_aspects.split(',') if aspect.strip()]
                else:
                    # If it's already a list
                    aspects = positive_aspects
                
                # If generic, replace with personalized suggestions based on totals and profile
                totals = analysis.get("total_nutrition", {})
                if _is_generic_points(aspects, user_language):
                    gen_pos, _ = _generate_personalized_points(totals, profile, user_language)
                    aspects = gen_pos or aspects
                for aspect in aspects[:5]:
                    message_parts.append(f"• {aspect}")
            
            # Add recommendations for improving
            improvement_suggestions = nutrition_analysis.get("improvement_suggestions", [])
            if improvement_suggestions:
                message_parts.append("")
                if user_language == "ru":
                    message_parts.append("💡 Как улучшить это блюдо:")
                else:
                    message_parts.append("💡 How to improve this meal:")
                
                # Handle both string and list formats
                if isinstance(improvement_suggestions, str):
                    # If it's a string, split by commas or use as single item
                    suggestions = [suggestion.strip() for suggestion in improvement_suggestions.split(',') if suggestion.strip()]
                else:
                    # If it's already a list
                    suggestions = improvement_suggestions
                # If generic, replace with personalized improvements
                totals = analysis.get("total_nutrition", {})
                if _is_generic_points(suggestions, user_language):
                    _, gen_imp = _generate_personalized_points(totals, profile, user_language)
                    suggestions = gen_imp or suggestions
                for s in suggestions[:5]:
                    message_parts.append(f"• {s}")
        
        # Add motivation message if available (localized/suppressed for RU)
        if "motivation_message" in analysis and analysis["motivation_message"]:
            mot = str(analysis["motivation_message"]).strip()
            if user_language == 'ru':
                mot_lc = mot.lower()
                if mot_lc == 'great choice for healthy eating!':
                    mot = 'Отличный выбор для здорового питания!'
                elif re.fullmatch(r"[\x00-\x7F\s.,!?'\-:;()]+", mot):
                    mot = ''  # suppress unknown English for RU UI
            if mot:
                message_parts.append("")  # Empty line
                message_parts.append(f"🌟 {mot}")
    else:
        # This should not happen anymore, but just in case
        raise ValueError("Invalid ML service response format - missing 'analysis' key")
    
    return "\n".join(message_parts)

# Process nutrition analysis for a photo
async def process_nutrition_analysis(message: types.Message, state: FSMContext):
    """
    Process photo for nutrition analysis
    """
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"Processing nutrition analysis for user {telegram_user_id}")
        
        # Get user info first
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        user_language = user.get('language', 'en')
        
        # Check photo size limit
        photo = message.photo[-1]  # Get highest resolution
        if photo.file_size and photo.file_size > 10 * 1024 * 1024:  # 10MB limit
            await message.answer(
                i18n.get_text('photo_too_large', user_language),
                parse_mode="Markdown"
            )
            return
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        credits = user["credits_remaining"]
        if credits <= 0:
            await message.answer(
                i18n.get_text('no_credits_remaining', user_language),
                parse_mode="Markdown"
            )
            return
        
        # Send processing message with random waiting phrase and food fact
        waiting_phrase = i18n.get_random_waiting_phrase(user_language)
        food_fact = i18n.get_random_fact(user_language)
        
        processing_text = f"{i18n.get_text('waiting_phrase_title', user_language)}\n\n{waiting_phrase}\n\n{i18n.get_text('food_facts_title', user_language)}\n{food_fact}"
        
        processing_msg = await message.answer(processing_text)
        
        # Download and upload photo to R2
        photo = message.photo[-1]  # Get highest resolution photo
        photo_url = await upload_telegram_photo(
            message.bot, 
            photo, 
            str(user["id"]), 
            "nutrition_analysis"
        )
        
        # Call ML service for analysis
        async with httpx.AsyncClient() as client:
            # Download photo data for ML service
            photo_file = await message.bot.get_file(photo.file_id)
            photo_bytes_io = await message.bot.download_file(photo_file.file_path)
            
            # Convert BytesIO to bytes
            if hasattr(photo_bytes_io, 'read'):
                photo_bytes = photo_bytes_io.read()
            elif hasattr(photo_bytes_io, 'getvalue'):
                photo_bytes = photo_bytes_io.getvalue()
            else:
                photo_bytes = photo_bytes_io
            
            logger.info(f"🔍 Calling ML service for user {telegram_user_id}, photo size: {len(photo_bytes)} bytes")
            
            # Prepare form data for ML service
            files = {"photo": ("photo.jpg", photo_bytes, "image/jpeg")}
            data = {
                "telegram_user_id": str(telegram_user_id),
                "provider": "openai",
                "user_language": user_language
            }
            
            # Get authentication headers
            from shared.auth import get_auth_headers
            auth_headers = get_auth_headers()
            # Remove Content-Type to let httpx set it automatically for multipart/form-data
            if 'Content-Type' in auth_headers:
                del auth_headers['Content-Type']
            
            logger.info(f"🚀 Sending request to ML service: {ML_SERVICE_URL}/api/v1/analyze")
            
            response = await client.post(
                f"{ML_SERVICE_URL}/api/v1/analyze",
                files=files,
                data=data,
                headers=auth_headers,
                timeout=60.0
            )
            
            logger.info(f"📨 ML service response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"ML service error: {response.status_code} - {response.text}")
                await processing_msg.edit_text(
                    i18n.get_text('analysis_failed', user_language),
                    parse_mode="Markdown"
                )
                return
            
            result = response.json()
            logger.info(f"✅ ML service result received: {len(str(result))} chars")
            logger.info(f"🔍 ML service result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            logger.info(f"🔍 ML service result content: {result}")
        
        # Format and send result
        analysis_text = format_analysis_result(result, user_language)
        
        # Decrement credits
        await decrement_credits(telegram_user_id)
        
        # Add calories to daily consumption using new calories manager
        daily_summary = add_calories_from_analysis(
            user_id=str(user["id"]),
            analysis_data=result,
            photo_url=photo_url
        )
        
        if not daily_summary:
            logger.error(f"Failed to add calories for user {user['id']}")
            daily_summary = get_daily_calories(str(user["id"]))

        # Add daily progress if user has profile (AFTER adding calories)
        if has_profile:
            # Get updated daily data after adding calories
            daily_data = get_daily_calories(str(user["id"]))
            daily_consumed = daily_data.get("total_calories", 0) if isinstance(daily_data, dict) else daily_data
            daily_target = profile.get("daily_calories_target", 2000)
            remaining = max(0, daily_target - daily_consumed)
            
            # Calculate progress percentage and create progress bar
            progress_percent = min(100, (daily_consumed / daily_target * 100)) if daily_target > 0 else 0
            progress_bars = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
            
            progress_text = f"\n\n{i18n.get_text('daily_progress_title', user_language)}\n{i18n.get_text('daily_progress_target', user_language, target=daily_target, calories=i18n.get_text('cal', user_language))}\n{i18n.get_text('daily_progress_consumed', user_language, consumed=daily_consumed, calories=i18n.get_text('cal', user_language), percent=int(progress_percent))}\n{i18n.get_text('daily_progress_remaining', user_language, remaining=remaining, calories=i18n.get_text('cal', user_language))}\n{i18n.get_text('daily_progress_bar', user_language, bar=progress_bars, percent=int(progress_percent))}"
            
            analysis_text += progress_text
        
        # Clear the state
        await state.clear()
        
        # Send result with main menu and Fix Calories/Add to favorites buttons
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('fix_calories_btn', user_language),
                    callback_data='action_fix_calories'
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_save_to_favorites', user_language, default='⭐ Save to favorites'),
                    callback_data='action_save_favorite'
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_main_menu', user_language),
                    callback_data='action_main_menu'
                )
            ]
        ])
        
        final_text = f"{analysis_text}\n\n{i18n.get_text('credits_remaining', user_language)} {credits - 1} {i18n.get_text('credits', user_language)} {i18n.get_text('left', user_language)}! 💪"
        
        # Sanitize the final text to prevent Telegram markdown parsing errors
        sanitized_final_text = sanitize_markdown_text(final_text)
        
        await processing_msg.edit_text(
            sanitized_final_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in nutrition analysis for user {telegram_user_id}: {e}")
        await message.answer(
            i18n.get_text('error_analysis', user_language),
            parse_mode="Markdown"
        )
        # Clear state on error
        await state.clear()

# Main photo handler - only handles photos when no FSM state is set
async def photo_handler(message: types.Message, state: FSMContext):
    try:
        telegram_user_id = message.from_user.id
        
        # Check if we're in any FSM state - if so, let the FSM handlers handle it
        current_state = await state.get_state()
        
        # If we're in nutrition_analysis state, process the photo directly for analysis
        if current_state == "nutrition_analysis":
            logger.info(f"Photo received for user {telegram_user_id} in nutrition_analysis state - processing directly")
            await process_nutrition_analysis(message, state)
            return
        
        if current_state is not None:
            logger.info(f"Photo received for user {telegram_user_id} but FSM state is {current_state}, skipping general handler")
            return
        
        logger.info(f"Photo handler called for user {telegram_user_id} with no FSM state - offering choice")
        
        # Check photo size limit (Telegram max is 20MB, we'll set 10MB limit)
        photo = message.photo[-1]  # Get highest resolution
        if photo.file_size and photo.file_size > 10 * 1024 * 1024:  # 10MB limit
            user_language = 'en'  # Default language for error case
            await message.answer(
                i18n.get_text('photo_too_large', user_language),
                parse_mode="Markdown"
            )
            return
        
        # Get user info with profile
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        logger.info(f"User {telegram_user_id} data: {user}, has_profile: {has_profile}")
        
        credits = user["credits_remaining"]
        logger.info(f"User {telegram_user_id} has {credits} credits")
        
        if credits <= 0:
            logger.warning(f"User {telegram_user_id} has no credits ({credits}), showing payment options")
            
            # Get user's language for localization
            user = await get_or_create_user(telegram_user_id)
            user_language = user.get('language', 'en')
            
            # Out of credits - show payment options
            await message.answer(
                f"{i18n.get_text('photo_out_of_credits_title', user_language)}\n\n"
                f"{i18n.get_text('current_credits', user_language, credits=user['credits_remaining'])}: *{user['credits_remaining']}*\n\n"
                f"📦 {i18n.get_text('basic_plan_title', user_language)}: {PAYMENT_PLANS['basic']['credits']} {i18n.get_text('credits', user_language)} {i18n.get_text('for', user_language)} {PAYMENT_PLANS['basic']['price'] // 100} {i18n.get_text('rubles', user_language)}\n"
                f"📦 {i18n.get_text('pro_plan_title', user_language)}: {PAYMENT_PLANS['pro']['credits']} {i18n.get_text('credits', user_language)} {i18n.get_text('for', user_language)} {PAYMENT_PLANS['pro']['price'] // 100} {i18n.get_text('rubles', user_language)}\n\n"
                f"{i18n.get_text('photo_out_of_credits_choose_plan', user_language)}:",
                parse_mode="Markdown",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=f"💰 {i18n.get_text('basic_plan_btn', user_language, price=PAYMENT_PLANS['basic']['price'] // 100)}",
                            callback_data="buy_basic"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text=f"💎 {i18n.get_text('pro_plan_btn', user_language, price=PAYMENT_PLANS['pro']['price'] // 100)}",
                            callback_data="buy_pro"
                        )
                    ]
                ])
            )
            return
        
        # Default behavior: offer choice between food analysis and recipe generation
        user_language = user.get('language', 'en')
        
        choice_text = (
            f"{i18n.get_text('photo_received', user_language)}\n\n"
            f"{i18n.get_text('what_to_do', user_language)}\n\n"
            f"{i18n.get_text('analyze_food_option', user_language)}\n"
            f"{i18n.get_text('generate_recipe_option', user_language)}\n\n"
            f"{i18n.get_text('credits_remaining', user_language)} {credits} {i18n.get_text('credits', user_language)}! 🚀"
        )
        analyze_button_text = i18n.get_text('analyze_food_btn', user_language)
        recipe_button_text = i18n.get_text('generate_recipe_btn', user_language)
        cancel_button_text = i18n.get_text('cancel_btn', user_language)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=analyze_button_text,
                    callback_data="action_analyze_info"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=recipe_button_text,
                    callback_data="action_recipe"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=cancel_button_text,
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(
            choice_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    except Exception as e:
        logger.error(f"Error in photo handler for user {telegram_user_id}: {e}")
        user_language = 'en'  # Default language for error case
        await message.answer(
            i18n.get_text('error_generic', user_language),
            parse_mode="Markdown"
        )

# Handler for successful_payment event (placeholder)
async def handle_successful_payment(message: types.Message):
    telegram_user_id = message.from_user.id
    logger.info(f"Payment received from user {telegram_user_id}")
    user_language = 'en'  # Default language for payment message
    await message.answer(i18n.get_text('payment_received', user_language))
    
    # TODO: Integrate with actual payment processing
    # This is a placeholder for when payment webhooks are implemented

 