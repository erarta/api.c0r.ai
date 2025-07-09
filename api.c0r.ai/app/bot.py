import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from handlers.commands import start_command, help_command, status_command, buy_credits_command
from handlers.photo import photo_handler
from handlers.payments import handle_pre_checkout_query, handle_successful_payment, handle_buy_callback
from loguru import logger

# Must be set in .env file
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Command handlers
dp.message.register(start_command, Command(commands=["start"]))
dp.message.register(help_command, Command(commands=["help"])) 
dp.message.register(status_command, Command(commands=["status"]))
dp.message.register(buy_credits_command, Command(commands=["buy"]))

# Photo handler
dp.message.register(photo_handler, lambda message: message.photo)

# Payment handlers
dp.callback_query.register(handle_buy_callback, lambda callback: callback.data.startswith("buy_"))
dp.pre_checkout_query.register(handle_pre_checkout_query)
dp.message.register(handle_successful_payment, lambda message: message.successful_payment)

async def start_bot():
    try:
        logger.info("Starting Telegram bot...")
        
        # Clear webhook to ensure polling mode
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(start_bot()) 