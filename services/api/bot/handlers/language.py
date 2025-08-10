"""
Language handler for c0r.ai Telegram Bot
Handles language switching and language detection
"""
from aiogram import types
from loguru import logger
from common.supabase_client import update_user_language
from i18n.i18n import i18n, Language


async def language_command(message: types.Message):
    """Handle /language command"""
    try:
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        
        # Get current language from user data
        current_language = user.get('language', 'en')
        language_name = i18n.get_language_name(current_language)
        
        # Create language selection keyboard
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("language_english", current_language),
                    callback_data="language_en"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("language_russian", current_language),
                    callback_data="language_ru"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_main_menu", current_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        # Create language settings message
        language_text = (
            f"{i18n.get_text('language_title', current_language)}\n\n"
            f"{i18n.get_text('language_current', current_language, lang_name=language_name)}\n\n"
            f"{i18n.get_text('language_choose', current_language)}"
        )
        
        await message.answer(language_text, parse_mode="Markdown", reply_markup=keyboard)
        logger.info(f"Language command by user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in language command: {e}")
        await message.answer(i18n.get_text("error_general", "en"))


async def handle_language_callback(callback: types.CallbackQuery):
    """Handle language selection callback"""
    try:
        telegram_user_id = callback.from_user.id
        telegram_user = callback.from_user
        telegram_language_code = telegram_user.language_code or "unknown"
        
        # Extract language from callback data
        if not callback.data.startswith("language_"):
            return
        
        selected_language = callback.data.split("_")[1]
        
        if selected_language not in ['en', 'ru']:
            await callback.answer("Invalid language selection")
            return
        
        # 🔍 DEBUG: Language Change
        logger.info(f"🔍 LANGUAGE CHANGE DEBUG for user {telegram_user_id}:")
        logger.info(f"   Telegram language_code: {telegram_language_code}")
        logger.info(f"   Selected language: {selected_language}")
        
        # Print to terminal for immediate visibility
        print(f"\n🔍 LANGUAGE CHANGE DEBUG for user {telegram_user_id}:")
        print(f"   Telegram language_code: {telegram_language_code}")
        print(f"   Selected language: {selected_language}")
        print("=" * 50)
        
        # Update user language in database
        updated_user = await update_user_language(telegram_user_id, selected_language)
        
        if not updated_user:
            await callback.answer("Failed to update language")
            return
        
        # Log language change
        await log_user_action(
            user_id=updated_user['id'],
            action_type="language_change",
            metadata={
                "username": callback.from_user.username,
                "old_language": updated_user.get('language', 'en'),
                "new_language": selected_language
            }
        )
        
        # Get language name for display
        language_name = i18n.get_language_name(selected_language)
        
        # Create success message
        success_text = i18n.get_text("language_changed", selected_language, lang_name=language_name)
        
        # Create back keyboard with new language
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", selected_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await callback.message.edit_text(success_text, parse_mode="Markdown", reply_markup=keyboard)
        logger.info(f"Language changed to {selected_language} for user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in language callback: {e}")
        await callback.answer("An error occurred while changing language")


async def detect_and_set_user_language(message: types.Message) -> str:
    """
    Detect user's language and set it in database
    
    Args:
        message: Telegram message object
        
    Returns:
        Detected language code ('en' or 'ru')
    """
    try:
        telegram_user_id = message.from_user.id
        user_language = message.from_user.language_code or "en"
        
        # Update user's language in database
        await update_user_language(telegram_user_id, user_language)
        
        logger.info(f"Set language {user_language} for user {telegram_user_id}")
        
        return user_language
        
    except Exception as e:
        logger.error(f"Error setting language for user {telegram_user_id}: {e}")
        return 'en'  # Default to English on error


# Import these functions to avoid circular imports
from common.supabase_client import get_or_create_user, log_user_action 