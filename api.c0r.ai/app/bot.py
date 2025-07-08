import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: Message):
    await message.answer("Hello from aiogram!")

async def start_bot():
    await dp.start_polling(bot)

# Для запуска бота отдельно:
# if __name__ == "__main__":
#     asyncio.run(start_bot()) 