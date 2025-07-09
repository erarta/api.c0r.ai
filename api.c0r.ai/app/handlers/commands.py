"""
Command handlers for NeuCor Telegram Bot
"""
import os
from datetime import datetime
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
        "You start with 3 free credits.\n\n"
        "Commands:\n"
        "• /start - Check your credits\n"
        "• /help - Show this help\n"
        "• /status - Show your account status\n\n"
        "If you run out of credits, you can buy more."
    )
    await message.answer(help_text)

# /status command handler - NEW FEATURE
async def status_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        
        # Format user creation date
        created_at = user.get('created_at', 'Unknown')
        if created_at != 'Unknown':
            try:
                # Parse ISO datetime string
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                created_date = created_at
        else:
            created_date = 'Unknown'
        
        status_text = (
            f"📊 *Your Account Status*\n\n"
            f"🆔 User ID: `{telegram_user_id}`\n"
            f"💳 Credits remaining: *{user['credits_remaining']}*\n"
            f"💰 Total paid: *${user.get('total_paid', 0):.2f}*\n"
            f"📅 Member since: `{created_date}`\n\n"
            f"🤖 System: *c0r.ai v0.3.4*\n"
            f"🌐 Status: *Online*\n"
            f"⚡ Powered by OpenAI Vision"
        )
        
        await message.answer(status_text, parse_mode="Markdown")
        logger.info(f"/status by user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in /status: {e}")
        await message.answer("An error occurred while fetching your status. Please try again later.") 