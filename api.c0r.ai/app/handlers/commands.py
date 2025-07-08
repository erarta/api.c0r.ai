"""
Command handlers for NeuCor Telegram Bot
"""
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user

# /start command handler
async def start_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        welcome = f"Welcome! You have {user['credits_remaining']} credits."
        await message.answer(welcome)
        logger.info(f"/start by user {telegram_user_id}")
    except Exception as e:
        logger.error(f"Error in /start: {e}")
        await message.answer("An error occurred. Please try again later.")

# /help command handler
async def help_command(message: types.Message):
    help_text = (
        "Send me a food photo and I will analyze it for calories, protein, fats, and carbs.\n"
        "You start with 3 free credits.\n"
        "Use /start to check your credits.\n"
        "If you run out, you can buy more."
    )
    await message.answer(help_text) 