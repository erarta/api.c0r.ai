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
from common.supabase_client import get_or_create_user, decrement_credits, get_user_with_profile, log_user_action, get_daily_calories_consumed
from services.api.bot.utils.r2 import upload_telegram_photo
from .keyboards import create_main_menu_keyboard
from i18n.i18n import i18n
from services.api.bot.config import PAYMENT_PLANS
from .nutrition import sanitize_markdown_text

# All values must be set in .env file
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

# Helper to format rich analysis result from ML service
def format_analysis_result(result: dict, user_language: str = 'en') -> str:
    message_parts = []
    
    # Check if we have the new rich format from PromptBuilder
    if "analysis" in result and isinstance(result["analysis"], dict):
        analysis = result["analysis"]
        
        # Add motivation message if available (without "Мотивация:" label)
        if "motivation_message" in analysis and analysis["motivation_message"]:
            message_parts.append(f"💚 {analysis['motivation_message']}")
            message_parts.append("")  # Empty line
        
        # Add food items breakdown
        if "food_items" in analysis and analysis["food_items"]:
            message_parts.append(f"🥘 *{i18n.get_text('food_items_detected', user_language)}*")
                
            for item in analysis["food_items"]:
                name = item.get("name", "Unknown")
                weight_grams = item.get("weight_grams", 0)
                calories = item.get("calories", 0)
                
                # Add health benefits if available
                health_benefits = item.get("health_benefits", "")
                if health_benefits:
                    # Use language-aware weight and calorie units
                    weight_unit = "г" if user_language == "ru" else "g"
                    calorie_unit = "ккал" if user_language == "ru" else "kcal"
                    message_parts.append(f"• {name} ({weight_grams}{weight_unit}) - {calories} {calorie_unit}")
                    message_parts.append(f"  💚 {health_benefits}")
                else:
                    # Use language-aware weight and calorie units
                    weight_unit = "г" if user_language == "ru" else "g"
                    calorie_unit = "ккал" if user_language == "ru" else "kcal"
                    message_parts.append(f"• {name} ({weight_grams}{weight_unit}) - {calories} {calorie_unit}")
            message_parts.append("")  # Empty line
        
        # Add total nutrition
        if "total_nutrition" in analysis:
            nutrition = analysis["total_nutrition"]
            message_parts.append(f"🍽️ *{i18n.get_text('total_nutrition', user_language)}*")
            message_parts.append(f"{i18n.get_text('calories_label', user_language)}: {nutrition.get('calories', '?')} {i18n.get_text('cal', user_language)}")
            message_parts.append(f"{i18n.get_text('proteins_label', user_language)}: {nutrition.get('proteins', '?')} {i18n.get_text('g', user_language)}")
            message_parts.append(f"{i18n.get_text('fats_label', user_language)}: {nutrition.get('fats', '?')} {i18n.get_text('g', user_language)}")
            message_parts.append(f"{i18n.get_text('carbohydrates_label', user_language)}: {nutrition.get('carbohydrates', '?')} {i18n.get_text('g', user_language)}")
        
        # Add encouragement message if available (without "Поощрение:" label)
        if "encouragement" in analysis and analysis["encouragement"]:
            message_parts.append("")  # Empty line
            message_parts.append(f"✨ {analysis['encouragement']}")
            
    else:
        # Fallback to old format for backward compatibility
        # Add food items breakdown if available
        if "food_items" in result and result["food_items"]:
            message_parts.append(f"🥘 *{i18n.get_text('food_items_detected', user_language)}*")
            for item in result["food_items"]:
                name = item.get("name", "Unknown")
                weight = item.get("weight", "Unknown")
                calories = item.get("calories", 0)
                message_parts.append(f"• {name} ({weight}) - {calories} {i18n.get_text('cal', user_language)}")
            message_parts.append("")  # Empty line
        
        # Add total KBZHU
        kbzhu = result.get("kbzhu", {})
        message_parts.append(f"🍽️ *{i18n.get_text('total_nutrition', user_language)}*")
        message_parts.append(f"{i18n.get_text('calories_label', user_language)}: {kbzhu.get('calories', '?')} {i18n.get_text('cal', user_language)}")
        message_parts.append(f"{i18n.get_text('proteins_label', user_language)}: {kbzhu.get('proteins', '?')} {i18n.get_text('g', user_language)}")
        message_parts.append(f"{i18n.get_text('fats_label', user_language)}: {kbzhu.get('fats', '?')} {i18n.get_text('g', user_language)}")
        message_parts.append(f"{i18n.get_text('carbohydrates_label', user_language)}: {kbzhu.get('carbohydrates', '?')} {i18n.get_text('g', user_language)}")
    
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
        
        # Send processing message
        processing_msg = await message.answer(i18n.get_text('analyzing_photo', user_language))
        
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
            photo_bytes = await message.bot.download_file(photo_file.file_path)
            
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
            
            response = await client.post(
                f"{ML_SERVICE_URL}/api/v1/analyze",
                files=files,
                data=data,
                headers=auth_headers,
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"ML service error: {response.status_code} - {response.text}")
                await processing_msg.edit_text(
                    i18n.get_text('analysis_failed', user_language),
                    parse_mode="Markdown"
                )
                return
            
            result = response.json()
        
        # Format and send result
        analysis_text = format_analysis_result(result, user_language)
        
        # Add daily progress if user has profile
        if has_profile:
            daily_data = await get_daily_calories_consumed(str(user["id"]))
            daily_consumed = daily_data.get("total_calories", 0) if isinstance(daily_data, dict) else daily_data
            daily_target = profile.get("daily_calories_target", 2000)
            remaining = daily_target - daily_consumed
            
            # Calculate progress percentage and create progress bar
            progress_percent = min(100, (daily_consumed / daily_target * 100)) if daily_target > 0 else 0
            progress_bars = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
            
            progress_text = f"\n\n{i18n.get_text('daily_progress_title', user_language)}\n{i18n.get_text('daily_progress_target', user_language, target=daily_target, calories=i18n.get_text('cal', user_language))}\n{i18n.get_text('daily_progress_consumed', user_language, consumed=daily_consumed, calories=i18n.get_text('cal', user_language), percent=int(progress_percent))}\n{i18n.get_text('daily_progress_remaining', user_language, remaining=remaining, calories=i18n.get_text('cal', user_language))}\n{i18n.get_text('daily_progress', user_language, progress_bar=progress_bars, percent=int(progress_percent))}"
            
            analysis_text += progress_text
        
        # Decrement credits
        await decrement_credits(telegram_user_id)
        
        # Log action
        await log_user_action(str(user["id"]), "nutrition_analysis")
        
        # Clear the state
        await state.clear()
        
        # Send result with main menu
        keyboard = create_main_menu_keyboard(user_language)
        
        final_text = f"{i18n.get_text('analysis_complete', user_language)}\n\n{analysis_text}\n\n{i18n.get_text('credits_remaining', user_language)} {credits - 1} {i18n.get_text('credits', user_language)} {i18n.get_text('left', user_language)}! 💪"
        
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