"""
Photo handler for NeuCor Telegram Bot
"""
import os
import httpx
from aiogram import types
from loguru import logger
from common.routes import Routes
from common.supabase_client import get_or_create_user, decrement_credits

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
        user = await get_or_create_user(telegram_user_id)
        credits = user["credits_remaining"]
        
        if credits <= 0:
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
            logger.info(f"User {telegram_user_id} out of credits, showed payment options.")
            return

        # Download photo file
        photo = message.photo[-1]  # Get highest resolution
        file = await message.bot.get_file(photo.file_id)
        
        # Download file content using aiogram 3.x method
        from io import BytesIO
        file_bytes = BytesIO()
        await message.bot.download_file(file.file_path, file_bytes)
        file_bytes.seek(0)
        file_content = file_bytes.getvalue()
        
        await message.answer("Analyzing your photo, please wait... ⏳")
        
        # POST to analysis API
        async with httpx.AsyncClient(timeout=30) as client:
            files = {"photo": ("photo.jpg", file_content, "image/jpeg")}
            data = {
                "telegram_user_id": str(telegram_user_id),
                "provider": "openai"
            }
            response = await client.post(f"{ML_SERVICE_URL}{Routes.ML_ANALYZE}", data=data, files=files)
            response.raise_for_status()
            result = response.json()

        kbzhu = result.get("kbzhu")
        if not kbzhu:
            raise ValueError("No KBZHU data in API response.")

        # Decrement credits and show result
        try:
            updated_user = await decrement_credits(telegram_user_id)
            credits_left = updated_user["credits_remaining"]
        except Exception as e:
            logger.error(f"Failed to decrement credits after analysis: {e}")
            credits_left = "?"

        await message.answer(
            format_analysis_result(result) + f"\n\nCredits left: {credits_left}",
            parse_mode="Markdown"
        )
        logger.info(f"User {telegram_user_id} analyzed photo. Result: {result}. Credits left: {credits_left}")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e.response.status_code} {e.response.text}")
        await message.answer("Sorry, analysis failed. Please try again later.")
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await message.answer("An error occurred. Please try again later.")

# Handler for successful_payment event (placeholder)
async def handle_successful_payment(message: types.Message):
    telegram_user_id = message.from_user.id
    logger.info(f"Payment received from user {telegram_user_id}")
    await message.answer("Payment received! Credits will be added shortly.")
    
    # TODO: Integrate with actual payment processing
    # This is a placeholder for when payment webhooks are implemented 