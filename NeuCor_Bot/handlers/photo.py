"""
Photo handler for NeuCor Telegram Bot
"""
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes, MessageHandler, filters
from loguru import logger
from utils.supabase import get_or_create_user, decrement_credits

domain = os.getenv("BASE_URL", "c0r.ai")
ANALYZE_API_URL = f"https://api.{domain}/v1/analyze"

# --- Payment Config ---
YOOKASSA_PRICE_RUB = 29900  # 299.00 RUB
YOOKASSA_CREDITS = 10
YOOKASSA_DESCRIPTION = "10 credits for food analysis"

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

# Send a YooKassa invoice using Telegram's native payment system
async def send_yookassa_invoice(update, context):
    await update.message.bot.send_invoice(
        chat_id=update.effective_user.id,
        title="Buy Credits",
        description=YOOKASSA_DESCRIPTION,
        payload="yookassa-payload-10-credits",
        provider_token=os.getenv("YOOKASSA_PROVIDER_TOKEN"),  # from BotFather
        currency="RUB",
        prices=[LabeledPrice(f"{YOOKASSA_CREDITS} credits", YOOKASSA_PRICE_RUB)],
        start_parameter="buy_credits",
        need_name=True,
        need_phone_number=True,
        need_email=False,
        is_flexible=False,
    )

# Main photo handler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_user_id = update.effective_user.id
        user, _ = await get_or_create_user(telegram_user_id)
        credits = user["credits_remaining"]
        if credits <= 0:
            # Out of credits: send a YooKassa invoice using Telegram Payments
            await send_yookassa_invoice(update, context)
            logger.info(f"User {telegram_user_id} out of credits, sent invoice.")
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

# Handler for successful_payment event (YooKassa in Telegram)
async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = update.effective_user.id
    # Increment credits (configurable)
    user, _ = await get_or_create_user(telegram_user_id)
    new_credits = user["credits_remaining"] + YOOKASSA_CREDITS
    from utils.supabase import supabase
    supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_user_id).execute()
    await update.message.reply_text(f"Payment received! {YOOKASSA_CREDITS} credits added. Thank you!")
    # Notify admin bot (optional)
    service_bot_url = os.getenv("SERVICE_BOT_URL")
    if service_bot_url:
        async with httpx.AsyncClient() as client:
            await client.post(service_bot_url, json={
                "event": "payment",
                "user_id": telegram_user_id,
                "amount": f"{YOOKASSA_PRICE_RUB/100:.2f} RUB (YooKassa)",
                "credits_added": YOOKASSA_CREDITS
            })

# --- Register the successful_payment handler at module level ---
def register_handlers(app):
    # Call this from your main bot setup
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))
# Usage in main.py:
# from handlers.photo import register_handlers
# register_handlers(app) 