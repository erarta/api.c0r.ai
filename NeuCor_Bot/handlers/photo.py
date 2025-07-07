"""
Photo handler for NeuCor Telegram Bot
"""
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from utils.supabase import get_or_create_user, decrement_credits

domain = os.getenv("PRODUCTION_DOMAIN", "c0r.ai")
ANALYZE_API_URL = f"https://api.{domain}/v1/analyze"

# Helper to format KBZHU nicely
def format_kbzhu(kbzhu: dict) -> str:
    return (
        f"🍽️ *Analysis Result*\n"
        f"Calories: {kbzhu.get('calories', '?')} kcal\n"
        f"Protein: {kbzhu.get('protein', '?')} g\n"
        f"Fats: {kbzhu.get('fats', '?')} g\n"
        f"Carbs: {kbzhu.get('carbs', '?')} g"
    )

# Helper to generate payment link (stub, replace with real logic)
def get_payment_link(telegram_user_id: int) -> str:
    return f"https://pay.{domain}/?user_id={telegram_user_id}"

# Main photo handler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_user_id = update.effective_user.id
        user, _ = await get_or_create_user(telegram_user_id)
        credits = user["credits_remaining"]
        if credits <= 0:
            # Out of credits: show payment button
            pay_url = get_payment_link(telegram_user_id)
            keyboard = [
                [InlineKeyboardButton("Buy Credits 💳", url=pay_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "You are out of credits! Please buy more to continue.",
                reply_markup=reply_markup
            )
            logger.info(f"User {telegram_user_id} out of credits.")
            return
        # Download photo file
        photo = update.message.photo[-1]  # Get highest resolution
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        await update.message.reply_text("Analyzing your photo, please wait... ⏳")
        # POST to analysis API
        async with httpx.AsyncClient(timeout=30) as client:
            files = {"photo": ("photo.jpg", file_bytes, "image/jpeg")}
            data = {"telegram_user_id": str(telegram_user_id)}
            response = await client.post(ANALYZE_API_URL, data=data, files=files)
            response.raise_for_status()
            result = response.json()
        kbzhu = result.get("kbzhu")
        if not kbzhu:
            raise ValueError("No KBZHU data in API response.")
        # Show KBZHU to user
        try:
            updated_user = await decrement_credits(telegram_user_id)
            credits_left = updated_user["credits_remaining"]
        except Exception as e:
            logger.error(f"Failed to decrement credits after analysis: {e}")
            credits_left = "?"
        await update.message.reply_text(
            format_kbzhu(kbzhu) + f"\n\nCredits left: {credits_left}",
            parse_mode="Markdown"
        )
        logger.info(f"User {telegram_user_id} analyzed photo. KBZHU: {kbzhu}. Credits left: {credits_left}")
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e.response.status_code} {e.response.text}")
        await update.message.reply_text("Sorry, analysis failed. Please try again later.")
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await update.message.reply_text("An error occurred. Please try again later.") 