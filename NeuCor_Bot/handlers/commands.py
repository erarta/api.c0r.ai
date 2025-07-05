"""
Command handlers for NeuCor Telegram Bot
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from utils.supabase import get_or_create_user

# /start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_user_id = update.effective_user.id
        user, created = await get_or_create_user(telegram_user_id)
        if created:
            welcome = f"Welcome! You have been registered and received 3 free credits."
        else:
            welcome = f"Welcome back! You have {user['credits_remaining']} credits."
        await update.message.reply_text(welcome)
        logger.info(f"/start by user {telegram_user_id} (created={created})")
    except Exception as e:
        logger.error(f"Error in /start: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Send me a food photo and I will analyze it for calories, protein, fats, and carbs.\n"
        "You start with 3 free credits.\n"
        "Use /start to check your credits.\n"
        "If you run out, you can buy more."
    )
    await update.message.reply_text(help_text) 