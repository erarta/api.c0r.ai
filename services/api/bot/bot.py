import os
import asyncio
import time
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from services.api.bot.handlers.commands import start_command, help_command, status_command, buy_credits_command, handle_action_callback
from services.api.bot.handlers.photo import photo_handler
from services.api.bot.handlers.payments import handle_pre_checkout_query, handle_successful_payment, handle_buy_callback
from services.api.bot.handlers.profile import (
    profile_command,
    handle_profile_callback,
    process_age, process_height, process_weight,
    process_gender, process_activity, process_goal,
    process_dietary_preferences, process_allergies,
    ProfileStates
)
from services.api.bot.handlers.recipe import recipe_command, handle_recipe_callback, process_recipe_photo, RecipeStates
from services.api.bot.handlers.daily import daily_command, handle_daily_callback
from services.api.bot.handlers.nutrition import nutrition_insights_command, weekly_report_command, water_tracker_command, process_nutrition_photo, NutritionStates
from services.api.bot.handlers.language import language_command, handle_language_callback
from i18n.i18n import i18n
from loguru import logger

# Must be set in .env file
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

# Create dispatcher with memory storage for FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Anti-spam protection - Rate limiting
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.photo_requests = defaultdict(list)
        
    def is_rate_limited(self, user_id: int, request_type: str = "general") -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        
        if request_type == "photo":
            # Photo analysis: max 5 photos per minute
            user_requests = self.photo_requests[user_id]
            # Remove old requests (older than 1 minute)
            user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < 60]
            
            if len(user_requests) >= 5:
                return True
            
            user_requests.append(current_time)
            return False
        else:
            # General commands: max 20 requests per minute
            user_requests = self.requests[user_id]
            # Remove old requests (older than 1 minute)
            user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < 60]
            
            if len(user_requests) >= 20:
                return True
            
            user_requests.append(current_time)
            return False
    
    def get_remaining_time(self, user_id: int, request_type: str = "general") -> int:
        """Get remaining time until user can make next request"""
        current_time = time.time()
        
        if request_type == "photo":
            user_requests = self.photo_requests[user_id]
            if user_requests:
                return max(0, int(60 - (current_time - user_requests[0])))
        else:
            user_requests = self.requests[user_id]
            if user_requests:
                return max(0, int(60 - (current_time - user_requests[0])))
        
        return 0

# Create rate limiter instance
rate_limiter = RateLimiter()

# Rate limiting middleware
async def rate_limit_middleware(handler, event, data: dict):
    """Middleware to check rate limits"""
    # Only process messages, skip other events
    if not isinstance(event, types.Message):
        return await handler(event, data)
    
    message = event
    user_id = message.from_user.id
    
    # Get user's language (default to English for rate limit messages)
    user_language = "en"
    try:
        from common.supabase_client import get_user_by_telegram_id
        user = await get_user_by_telegram_id(user_id)
        if user and user.get('language'):
            user_language = user['language']
    except:
        pass  # Use default English if we can't get user language
    
    # Check for photo requests
    if message.photo:
        if rate_limiter.is_rate_limited(user_id, "photo"):
            remaining = rate_limiter.get_remaining_time(user_id, "photo")
            await message.answer(
                f"{i18n.get_text('error_rate_limit_photo_title', user_language)}\n\n"
                f"{i18n.get_text('error_rate_limit_photo', user_language, remaining=remaining)}",
                parse_mode="Markdown"
            )
            logger.warning(f"Rate limit hit for photo analysis by user {user_id}")
            return
    else:
        # Check for general commands
        if rate_limiter.is_rate_limited(user_id, "general"):
            remaining = rate_limiter.get_remaining_time(user_id, "general")
            await message.answer(
                f"{i18n.get_text('error_rate_limit_title', user_language)}\n\n"
                f"{i18n.get_text('error_rate_limit_general', user_language, remaining=remaining)}",
                parse_mode="Markdown"
            )
            logger.warning(f"Rate limit hit for general commands by user {user_id}")
            return
    
    # Continue to handler if not rate limited
    return await handler(event, data)

# Register middleware
dp.message.middleware(rate_limit_middleware)

# Command handlers
dp.message.register(start_command, Command(commands=["start"]))
dp.message.register(help_command, Command(commands=["help"]))
dp.message.register(status_command, Command(commands=["status"]))
dp.message.register(buy_credits_command, Command(commands=["buy"]))
dp.message.register(profile_command, Command(commands=["profile"]))
dp.message.register(recipe_command, Command(commands=["recipe"]))
dp.message.register(daily_command, Command(commands=["daily"]))
dp.message.register(nutrition_insights_command, Command(commands=["insights"]))
dp.message.register(weekly_report_command, Command(commands=["report"]))
dp.message.register(water_tracker_command, Command(commands=["water"]))
dp.message.register(language_command, Command(commands=["language"]))

# FSM handlers (MUST be registered BEFORE general photo handler)
dp.message.register(process_recipe_photo, RecipeStates.waiting_for_photo)
dp.message.register(process_nutrition_photo, NutritionStates.waiting_for_photo)

# Photo handler (only for photos, not documents) - registered AFTER FSM handlers
# This handler only processes photos when no FSM state is set
dp.message.register(photo_handler, lambda message: message.photo)

# Reject non-photo files
async def reject_non_photo(message: types.Message):
    """Reject documents, videos, and other non-photo files"""
    file_type = "unknown"
    if message.document:
        file_type = "document"
    elif message.video:
        file_type = "video"
    elif message.audio:
        file_type = "audio"
    elif message.voice:
        file_type = "voice message"
    elif message.sticker:
        file_type = "sticker"
    
    # Get user's language (default to English)
    user_language = "en"
    try:
        from common.supabase_client import get_user_by_telegram_id
        user = await get_user_by_telegram_id(message.from_user.id)
        if user and user.get('language'):
            user_language = user['language']
    except:
        pass
    
    await message.answer(
        f"{i18n.get_text('error_file_type', user_language, file_type=file_type)}",
        parse_mode="Markdown"
    )
    logger.warning(f"User {message.from_user.id} tried to send {file_type}")

# Register handlers for non-photo files
dp.message.register(reject_non_photo, lambda message: message.document)
dp.message.register(reject_non_photo, lambda message: message.video)
dp.message.register(reject_non_photo, lambda message: message.audio)
dp.message.register(reject_non_photo, lambda message: message.voice)
dp.message.register(reject_non_photo, lambda message: message.sticker)

# FSM handlers for profile setup
dp.message.register(process_age, ProfileStates.waiting_for_age)
dp.message.register(process_height, ProfileStates.waiting_for_height)
dp.message.register(process_weight, ProfileStates.waiting_for_weight)


# Callback handlers - ORDER MATTERS!
# Recipe callback must be registered BEFORE general action callback to avoid conflicts
dp.callback_query.register(handle_recipe_callback, lambda callback: callback.data == "action_recipe")
dp.callback_query.register(handle_action_callback, lambda callback: callback.data.startswith("action_"))
dp.callback_query.register(handle_buy_callback, lambda callback: callback.data.startswith("buy_"))
dp.callback_query.register(handle_profile_callback, lambda callback: callback.data.startswith("profile_"))
dp.callback_query.register(process_gender, lambda callback: callback.data.startswith("gender_"))
dp.callback_query.register(process_activity, lambda callback: callback.data.startswith("activity_"))
dp.callback_query.register(process_goal, lambda callback: callback.data.startswith("goal_"))
dp.callback_query.register(process_dietary_preferences, lambda callback: callback.data.startswith("diet_"))
dp.callback_query.register(process_allergies, lambda callback: callback.data.startswith("allergy_"))
dp.callback_query.register(handle_daily_callback, lambda callback: callback.data.startswith("daily_"))
dp.callback_query.register(handle_language_callback, lambda callback: callback.data.startswith("language_"))
# Nutrition insights section navigation
from services.api.bot.handlers.nutrition import handle_nutrition_section_callback, handle_nutrition_menu_callback
dp.callback_query.register(handle_nutrition_section_callback, lambda callback: callback.data.startswith("nutrition_section_"))
dp.callback_query.register(handle_nutrition_menu_callback, lambda callback: callback.data == "nutrition_menu")

# Payment handlers
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