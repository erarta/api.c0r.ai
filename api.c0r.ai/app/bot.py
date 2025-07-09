import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from handlers.commands import start_command, help_command, status_command
from handlers.photo import photo_handler, handle_successful_payment

# Must be set in .env file
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.message.register(start_command, F.text, lambda message: message.text and message.text.startswith('/start'))
dp.message.register(help_command, F.text, lambda message: message.text and message.text.startswith('/help'))
dp.message.register(status_command, F.text, lambda message: message.text and message.text.startswith('/status'))
dp.message.register(photo_handler, F.photo)
dp.message.register(handle_successful_payment, F.successful_payment)

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot()) 