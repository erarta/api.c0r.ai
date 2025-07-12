"""
Photo handler for NeuCor Telegram Bot
"""
import os
import httpx
from aiogram import types
from loguru import logger
from common.routes import Routes
from common.supabase_client import get_or_create_user, decrement_credits, get_user_with_profile, log_user_action, get_daily_calories_consumed
from utils.r2 import upload_telegram_photo
from .commands import create_main_menu_keyboard

# All values must be set in .env file
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")

# Helper to format KBZHU nicely with detailed breakdown
def format_analysis_result(result: dict) -> str:
    message_parts = []
    
    # Add food items breakdown if available
    if "food_items" in result and result["food_items"]:
        message_parts.append("🥘 *Food Items Detected:*")
        for item in result["food_items"]:
            name = item.get("name", "Unknown")
            weight = item.get("weight", "Unknown")
            calories = item.get("calories", 0)
            message_parts.append(f"• {name} ({weight}) - {calories} kcal")
        message_parts.append("")  # Empty line
    
    # Add total KBZHU
    kbzhu = result.get("kbzhu", {})
    message_parts.append("🍽️ *Total Nutrition:*")
    message_parts.append(f"Calories: {kbzhu.get('calories', '?')} kcal")
    message_parts.append(f"Proteins: {kbzhu.get('proteins', '?')} g")
    message_parts.append(f"Fats: {kbzhu.get('fats', '?')} g")
    message_parts.append(f"Carbohydrates: {kbzhu.get('carbohydrates', '?')} g")
    
    return "\n".join(message_parts)

# Main photo handler
async def photo_handler(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        
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
        logger.info(f"Photo handler called by user {telegram_user_id} (@{message.from_user.username})")
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        logger.info(f"User {telegram_user_id} data: {user}, has_profile: {has_profile}")
        
        credits = user["credits_remaining"]
        logger.info(f"User {telegram_user_id} has {credits} credits")
        
        if credits <= 0:
            logger.warning(f"User {telegram_user_id} has no credits ({credits}), showing payment options")
            # Out of credits - show payment options
            await message.answer(
                f"❌ You have no credits left!\n\n"
                f"💳 **Buy Credits to Continue:**\n"
                f"📦 Basic Plan: 20 credits for 99 RUB\n"
                f"📦 Pro Plan: 100 credits for 399 RUB\n\n"
                f"Choose a plan to continue analyzing your food:",
                parse_mode="Markdown",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="💰 Basic Plan (99 RUB)",
                            callback_data="buy_basic"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="💎 Pro Plan (399 RUB)", 
                            callback_data="buy_pro"
                        )
                    ]
                ])
            )
            return

        # Download photo file
        file = await message.bot.get_file(photo.file_id)
        
        await message.answer("Uploading and analyzing your photo... ⏳")
        logger.info(f"Starting photo upload and analysis for user {telegram_user_id}")
        
        # Upload photo to R2 storage
        photo_url = await upload_telegram_photo(message.bot, photo, user['id'])
        if photo_url:
            logger.info(f"Photo uploaded to R2 for user {telegram_user_id}: {photo_url}")
        else:
            logger.warning(f"Failed to upload photo to R2 for user {telegram_user_id}, using fallback")
            photo_url = f"telegram_photo_{photo.file_id}"
        
        # Download file content directly as bytes for ML analysis
        file_content = await message.bot.download_file(file.file_path)
        
        # Call ML service for analysis
        logger.info(f"Sending photo to ML service for user {telegram_user_id}")
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            files = {
                "photo": ("photo.jpg", file_content, "image/jpeg")  # ← ИСПРАВЛЕНО: "image" -> "photo"
            }
            data = {
                "telegram_user_id": str(telegram_user_id),  # ← ИСПРАВЛЕНО: "user_id" -> "telegram_user_id"
                "provider": "openai"
            }
            response = await client.post(
                f"{ML_SERVICE_URL}{Routes.ML_ANALYZE}", 
                data=data, 
                files=files
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"ML analysis result for user {telegram_user_id}: {result}")

        # Check if food was detected
        kbzhu = result.get("kbzhu")
        if not kbzhu:
            # No food detected scenario
            await message.answer(
                "🤔 **No food detected in this photo**\n\n"
                "📸 **Tips for better results:**\n"
                "• Make sure the food is clearly visible\n"
                "• Use good lighting\n"
                "• Focus on the food, not the background\n"
                "• Try taking the photo from above\n\n"
                "📤 **Try again with a clearer photo!**\n\n"
                "💡 *Don't worry - your credit wasn't used since no food was detected.*",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
            # Log the failed detection but don't use credits
            await log_user_action(
                user_id=user['id'],
                action_type="photo_analysis_failed",
                photo_url=photo_url,
                metadata={
                    "username": message.from_user.username,
                    "reason": "no_food_detected",
                    "telegram_file_id": photo.file_id,
                    "photo_size": photo.file_size
                }
            )
            return

        # Check if KBZHU data is valid
        if not isinstance(kbzhu, dict) or not any(kbzhu.values()):
            await message.answer(
                "❌ **Analysis failed**\n\n"
                "The food analysis couldn't be completed properly. Please try again with a clearer photo.\n\n"
                "💡 *Your credit wasn't used since the analysis failed.*",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
            return

        # Decrement credits only after successful analysis
        try:
            logger.info(f"Decrementing credits for user {telegram_user_id}")
            updated_user = await decrement_credits(telegram_user_id)
            logger.info(f"Credits decremented for user {telegram_user_id}: {updated_user}")
            credits_left = updated_user["credits_remaining"]
        except Exception as e:
            logger.error(f"Failed to decrement credits for user {telegram_user_id}: {e}")
            credits_left = "?"

        # Log the photo analysis action
        await log_user_action(
            user_id=user['id'],
            action_type="photo_analysis",
            photo_url=photo_url,
            kbzhu=kbzhu,
            model_used="openai-vision",
            metadata={
                "username": message.from_user.username,
                "credits_remaining": credits_left,
                "has_profile": has_profile,
                "telegram_file_id": photo.file_id,
                "photo_size": photo.file_size
            }
        )

        # Show different results based on profile
        if has_profile:
            # User has profile - show detailed progress
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            daily_data = await get_daily_calories_consumed(user['id'], today)
            
            daily_target = profile.get('daily_calories_target', 0)
            consumed_today = daily_data['total_calories']
            remaining = max(0, daily_target - consumed_today) if daily_target else 0
            progress_percent = min(100, int((consumed_today / daily_target) * 100)) if daily_target else 0
            
            # Create progress bar
            progress_bar = "▓" * (progress_percent // 10) + "░" * (10 - progress_percent // 10)
            
            result_message = (
                f"{format_analysis_result(result)}\n\n"
                f"📊 **Your Daily Progress:**\n"
                f"🎯 Daily Target: {daily_target:,} calories\n"
                f"📈 Consumed Today: {consumed_today:,} calories ({progress_percent}%)\n"
                f"⏳ Remaining: {remaining:,} calories\n\n"
                f"📈 Daily Progress:\n{progress_bar} {progress_percent}%\n\n"
                f"🍎 Meals Analyzed Today: {daily_data['food_items_count']}\n"
                f"💳 Credits Remaining: {credits_left}"
            )
            
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="📊 Daily Plan", 
                        callback_data="action_daily"
                    ),
                    types.InlineKeyboardButton(
                        text="👤 Profile", 
                        callback_data="action_profile"
                    )
                ]
            ])
        else:
            # User without profile - encourage to set up profile
            result_message = (
                f"{format_analysis_result(result)}\n\n"
                f"💡 **Want to see how this fits your daily goals?**\n"
                f"Set up your profile for personalized recommendations!\n\n"
                f"💳 Credits Remaining: {credits_left}"
            )
            
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="👤 Set Up Profile", 
                        callback_data="action_profile"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🏠 Main Menu",
                        callback_data="action_main_menu"
                    )
                ]
            ])

        await message.answer(result_message, parse_mode="Markdown", reply_markup=keyboard)
        logger.info(f"Photo analysis completed for user {telegram_user_id}. Credits left: {credits_left}")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"API error for user {telegram_user_id}: {e.response.status_code} {e.response.text}")
        await message.answer(
            "❌ **Analysis service temporarily unavailable**\n\n"
            "Please try again in a few minutes.\n\n"
            "💡 *Your credit wasn't used since the analysis failed.*",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Photo handler error for user {telegram_user_id}: {e}")
        await message.answer(
            "❌ **An error occurred during analysis**\n\n"
            "Please try again later.\n\n"
            "💡 *Your credit wasn't used since the analysis failed.*",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )

# Handler for successful_payment event (placeholder)
async def handle_successful_payment(message: types.Message):
    telegram_user_id = message.from_user.id
    logger.info(f"Payment received from user {telegram_user_id}")
    await message.answer("Payment received! Credits will be added shortly.")
    
    # TODO: Integrate with actual payment processing
    # This is a placeholder for when payment webhooks are implemented 