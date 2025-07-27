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

# All values must be set in .env file
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

# Helper to format KBZHU nicely with detailed breakdown
def format_analysis_result(result: dict, user_language: str = 'en') -> str:
    message_parts = []
    
    # Add food items breakdown if available
    if "food_items" in result and result["food_items"]:
        message_parts.append("🥘 *Food Items Detected:*")
        for item in result["food_items"]:
            name = item.get("name", "Unknown")
            weight = item.get("weight", "Unknown")
            calories = item.get("calories", 0)
            message_parts.append(f"• {name} ({weight}) - {calories} {i18n.get_text('cal', user_language)}")
        message_parts.append("")  # Empty line
    
    # Add total KBZHU
    kbzhu = result.get("kbzhu", {})
    message_parts.append("🍽️ *Total Nutrition:*")
    message_parts.append(f"Calories: {kbzhu.get('calories', '?')} {i18n.get_text('cal', user_language)}")
    message_parts.append(f"Proteins: {kbzhu.get('proteins', '?')} {i18n.get_text('g', user_language)}")
    message_parts.append(f"Fats: {kbzhu.get('fats', '?')} {i18n.get_text('g', user_language)}")
    message_parts.append(f"Carbohydrates: {kbzhu.get('carbohydrates', '?')} {i18n.get_text('g', user_language)}")
    
    return "\n".join(message_parts)

# Process nutrition analysis for a photo
async def process_nutrition_analysis(message: types.Message, state: FSMContext):
    """
    Process photo for nutrition analysis
    """
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"Processing nutrition analysis for user {telegram_user_id}")
        
        # Check photo size limit
        photo = message.photo[-1]  # Get highest resolution
        if photo.file_size and photo.file_size > 10 * 1024 * 1024:  # 10MB limit
            await message.answer(
                "❌ **Photo too large!**\n\n"
                "📏 Maximum photo size: 10MB\n"
                "💡 Please compress your photo or take a new one.",
                parse_mode="Markdown"
            )
            return
        
        # Get user info
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        credits = user["credits_remaining"]
        if credits <= 0:
            await message.answer(
                "❌ **No credits remaining!**\n\n"
                "Please purchase more credits to continue.",
                parse_mode="Markdown"
            )
            return
        
        # Send processing message
        user_language = user.get('language', 'en')
        if user_language == 'ru':
            processing_msg = await message.answer("🔍 Анализирую фото...\n\nПожалуйста, подождите...")
        else:
            processing_msg = await message.answer("🔍 Analyzing photo...\n\nPlease wait...")
        
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
                    "❌ **Analysis failed**\n\n"
                    "Sorry, we couldn't analyze your photo. Please try again.",
                    parse_mode="Markdown"
                )
                return
            
            result = response.json()
        
        # Format and send result
        analysis_text = format_analysis_result(result, user_language)
        
        # Add daily progress if user has profile
        if has_profile and profile:
            daily_data = await get_daily_calories_consumed(str(user["id"]))
            daily_consumed = daily_data.get("total_calories", 0) if isinstance(daily_data, dict) else daily_data
            daily_target = profile.get("daily_calories_target", 2000)
            remaining = daily_target - daily_consumed
            
            if user_language == 'ru':
                progress_text = f"\n📊 **Дневной прогресс:**\nПотреблено: {daily_consumed} ккал\nЦель: {daily_target} ккал\nОсталось: {remaining} ккал"
            else:
                progress_text = f"\n📊 **Daily Progress:**\nConsumed: {daily_consumed} cal\nTarget: {daily_target} cal\nRemaining: {remaining} cal"
            
            analysis_text += progress_text
        
        # Decrement credits
        await decrement_credits(telegram_user_id)
        
        # Log action
        await log_user_action(str(user["id"]), "nutrition_analysis")
        
        # Clear the state
        await state.clear()
        
        # Send result with main menu
        keyboard = create_main_menu_keyboard(user_language)
        
        if user_language == 'ru':
            final_text = f"✅ **Анализ завершен!**\n\n{analysis_text}\n\n💳 **Осталось кредитов:** {credits - 1}"
        else:
            final_text = f"✅ **Analysis complete!**\n\n{analysis_text}\n\n💳 **Credits remaining:** {credits - 1}"
        
        await processing_msg.edit_text(
            final_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in nutrition analysis for user {telegram_user_id}: {e}")
        await message.answer(
            "❌ **Error**\n\n"
            "Something went wrong during analysis. Please try again.",
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
            await message.answer(
                "❌ **Photo too large!**\n\n"
                "📏 Maximum photo size: 10MB\n"
                "💡 Please compress your photo or take a new one.",
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
        
        if user_language == 'ru':
            choice_text = (
                f"📸 **Фото получено!**\n\n"
                f"Что вы хотите сделать с этим фото?\n\n"
                f"🍕 **Анализ еды** - Получить детальную информацию о калориях и питательности\n"
                f"🍽️ **Создать рецепт** - Сгенерировать персонализированный рецепт\n\n"
                f"💳 **Осталось кредитов:** {credits}"
            )
            analyze_button_text = "🍕 Анализ еды"
            recipe_button_text = "🍽️ Создать рецепт"
            cancel_button_text = "❌ Отмена"
        else:
            choice_text = (
                f"📸 **Photo received!**\n\n"
                f"What would you like to do with this photo?\n\n"
                f"🍕 **Analyze Food** - Get detailed calorie and nutrition information\n"
                f"🍽️ **Generate Recipe** - Create a personalized recipe\n\n"
                f"💳 **Credits remaining:** {credits}"
            )
            analyze_button_text = "🍕 Analyze Food"
            recipe_button_text = "🍽️ Generate Recipe"
            cancel_button_text = "❌ Cancel"
        
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
        await message.answer(
            "❌ **Error**\n\n"
            "Something went wrong. Please try again.",
            parse_mode="Markdown"
        )

# Handler for successful_payment event (placeholder)
async def handle_successful_payment(message: types.Message):
    telegram_user_id = message.from_user.id
    logger.info(f"Payment received from user {telegram_user_id}")
    await message.answer("Payment received! Credits will be added shortly.")
    
    # TODO: Integrate with actual payment processing
    # This is a placeholder for when payment webhooks are implemented 