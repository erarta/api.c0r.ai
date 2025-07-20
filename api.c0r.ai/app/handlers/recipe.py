"""
Recipe generation handlers for c0r.ai Telegram Bot
Handles recipe generation from food photos using OpenAI GPT-4o
"""
import logging
import re
import os
import aiohttp
import json
from datetime import datetime
from typing import Optional

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.supabase_client import get_or_create_user, get_user_with_profile, log_user_action, decrement_credits
from common.routes import Routes
from i18n.i18n import i18n
from utils.r2 import upload_photo_to_r2, upload_telegram_photo
from handlers.nutrition import sanitize_markdown_text

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escape special Markdown characters to prevent parsing errors"""
    if not text or text in ["—", "Нет", "None"]:
        return text
    
    # Only escape the most critical characters that cause parsing errors
    # Use single backslash for proper Telegram markdown escaping
    critical_chars = ['_', ',', '*']
    
    for char in critical_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

# FSM States for recipe generation
class RecipeStates(StatesGroup):
    waiting_for_photo = State()

# Recipe generation command handler
async def recipe_command(message: types.Message, state: FSMContext):
    """Handle /recipe command - start recipe generation"""
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"Recipe command called by telegram_user_id: {telegram_user_id}")
        
        # Clear any existing FSM state to start fresh (only if state is provided)
        if state:
            await state.clear()
        
        # Get user data using get_or_create_user for the most up-to-date credits
        user = await get_or_create_user(telegram_user_id)
        
        # Get user profile data separately
        user_data_with_profile = await get_user_with_profile(telegram_user_id)
        profile = user_data_with_profile['profile']
        has_profile = user_data_with_profile['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Log recipe command usage
        await log_user_action(
            user_id=user['id'],
            action_type="recipe_generation",
            metadata={
                "username": message.from_user.username,
                "has_profile": has_profile,
                "action": "start_recipe_generation"
            }
        )
        
        # Check if user has credits
        if user['credits_remaining'] <= 0:
            # Create keyboard with buy credits button and main menu
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="💳 Купить кредиты" if user_language == 'ru' else "💳 Buy Credits",
                    callback_data="action_buy"
                )],
                [types.InlineKeyboardButton(
                    text="🏠 Главное меню" if user_language == 'ru' else "🏠 Main Menu",
                    callback_data="action_main_menu"
                )]
            ])
            
            if user_language == 'ru':
                error_text = (
                    f"❌ **Кредиты закончились**\n\n"
                    f"Для генерации рецептов по фото нужны кредиты\\.\n\n"
                    f"💳 **Получи больше кредитов:**"
                )
            else:
                error_text = (
                    f"❌ **No Credits Remaining**\n\n"
                    f"You need credits to generate recipes from photos\\.\n\n"
                    f"💳 **Get more credits:**"
                )
            
            # Error text is already properly formatted
            
            await message.answer(
                error_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Start recipe generation process
        # Pass user and profile data separately to start_recipe_generation
        await start_recipe_generation(message, state, user, profile, has_profile)
            
    except Exception as e:
        logger.error(f"Error in /recipe command for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def recipe_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle recipe callback - start recipe generation from button"""
    try:
        telegram_user_id = callback.from_user.id
        logger.info(f"Recipe callback called by telegram_user_id: {telegram_user_id}")
        
        # Clear any existing FSM state to start fresh
        if state:
            await state.clear()
        
        # Get user data using get_or_create_user for the most up-to-date credits
        user = await get_or_create_user(telegram_user_id)
        
        # Debug logging immediately after getting user data
        logger.info(f"DEBUG: After get_or_create_user - user: {user!r}, credits_remaining: {user.get('credits_remaining')}, type: {type(user.get('credits_remaining'))}")
        
        # Get user profile data separately
        user_data_with_profile = await get_user_with_profile(telegram_user_id)
        profile = user_data_with_profile['profile']
        has_profile = user_data_with_profile['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Log recipe command usage
        await log_user_action(
            user_id=user['id'],
            action_type="recipe_generation",
            metadata={
                "username": callback.from_user.username,
                "has_profile": has_profile,
                "action": "start_recipe_generation_callback"
            }
        )
        
        # Debug logging for credits check in recipe_callback
        logger.info(f"DEBUG: recipe_callback - user_id: {user.get('id')}, credits_remaining: {user.get('credits_remaining')}, type: {type(user.get('credits_remaining'))}")
        
        # Check if user has credits
        if user['credits_remaining'] <= 0:
            # Create keyboard with buy credits button and main menu
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="💳 Купить кредиты" if user_language == 'ru' else "💳 Buy Credits",
                    callback_data="action_buy"
                )],
                [types.InlineKeyboardButton(
                    text="🏠 Главное меню" if user_language == 'ru' else "🏠 Main Menu",
                    callback_data="action_main_menu"
                )]
            ])
            
            if user_language == 'ru':
                error_text = (
                    f"❌ **Кредиты закончились**\n\n"
                    f"Для генерации рецептов по фото нужны кредиты\\.\n\n"
                    f"💳 **Получи больше кредитов:**"
                )
            else:
                error_text = (
                    f"❌ **No Credits Remaining**\n\n"
                    f"You need credits to generate recipes from photos\\.\n\n"
                    f"💳 **Get more credits:**"
                )
            
            # Error text is already properly formatted
            
            # Try to send error_text and log on failure
            try:
                logger.info(f"DEBUG: About to send error_text: {error_text!r}")
                print(f"DEBUG: About to send error_text: {error_text!r}")
                await callback.message.answer(
                    error_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            except Exception as send_exc:
                logger.error(f"TELEGRAM ERROR: Failed to send error_text: {error_text!r} | Exception: {send_exc}")
                print(f"TELEGRAM ERROR: Failed to send error_text: {error_text!r} | Exception: {send_exc}")
            return
        
        # Start recipe generation process using callback message
        await start_recipe_generation_callback(callback, state, user, profile, has_profile)
            
    except Exception as e:
        logger.error(f"Error in recipe callback for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await callback.message.answer(i18n.get_text("error_general", user_language))

async def start_recipe_generation_callback(callback: types.CallbackQuery, state: FSMContext, user: dict, profile: dict, has_profile: bool):
    """Start recipe generation process from callback"""
    # Set FSM state
    if state:
        await state.set_state(RecipeStates.waiting_for_photo)
    
    telegram_user_id = callback.from_user.id
    logger.info(f"start_recipe_generation_callback called with telegram_user_id: {telegram_user_id}")
    
    # Re-fetch user data to ensure credits are absolutely current
    user = await get_or_create_user(telegram_user_id)
    
    # Get user's language
    user_language = user.get('language', 'en')
    
    # Create instruction text based on profile availability and language
    dietary_prefs = profile.get('dietary_preferences', []) if has_profile else []
    allergies = profile.get('allergies', []) if has_profile else []
    dietary_text = ", ".join(dietary_prefs) if dietary_prefs and dietary_prefs != ['none'] else "Нет" if user_language == 'ru' else "None"
    allergies_text = ", ".join(allergies) if allergies and allergies != ['none'] else "Нет" if user_language == 'ru' else "None"
    goal_text = profile.get('goal', "—") if has_profile else "—"
    
    # Escape Markdown characters in user data
    dietary_text = escape_markdown(dietary_text)
    allergies_text = escape_markdown(allergies_text)
    goal_text = escape_markdown(goal_text)

    if has_profile:
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Создание рецепта**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам персонализированный рецепт для тебя!\n\n"
                f"👤 **Твой профиль:**\n"
                f"🎯 Цель: {goal_text}\n"
                f"🍽️ Диета: {dietary_text}\n"
                f"⚠️ Аллергии: {allergies_text}\n\n"
                f"✨ **Я создам рецепты, которые:**\n"
                f"• Соответствуют твоим диетическим предпочтениям\n"
                f"• Избегают твоих аллергий\n"
                f"• Соответствуют твоим фитнес-целям\n"
                f"• Включают информацию о питательности\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a personalized recipe for you!\n\n"
                f"👤 **Your Profile:**\n"
                f"🎯 Goal: {goal_text}\n"
                f"🍽️ Diet: {dietary_text}\n"
                f"⚠️ Allergies: {allergies_text}\n\n"
                f"✨ **I'll create recipes that:**\n"
                f"• Match your dietary preferences\n"
                f"• Avoid your allergies\n"
                f"• Align with your fitness goals\n"
                f"• Include nutritional information\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    else:
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Создание рецепта**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам рецепт для тебя!\n\n"
                f"💡 **Совет:** Настрой свой профиль для персонализированных рецептов, которые соответствуют твоим диетическим предпочтениям и целям.\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a recipe for you!\n\n"
                f"💡 **Tip:** Set up your profile for personalized recipes that match your dietary preferences and goals.\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    
    # Create keyboard with language-appropriate buttons
    if user_language == 'ru':
        profile_button_text = "👤 Настроить профиль" if not has_profile else "👤 Посмотреть профиль"
        cancel_button_text = "❌ Отмена"
    else:
        profile_button_text = "👤 Set Up Profile" if not has_profile else "👤 View Profile"
        cancel_button_text = "❌ Cancel"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=profile_button_text,
                callback_data="action_profile"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=cancel_button_text,
                callback_data="action_main_menu"
            )
        ]
    ])
    
    # Note: Profile data is already escaped with escape_markdown() above
    # Do not use sanitize_markdown_text() as it will undo the escaping
    
    # Debug logging
    logger.info(f"DEBUG: About to send instruction text (length: {len(instruction_text)})")
    logger.info(f"DEBUG: First 100 chars: {instruction_text[:100]}")
    try:
        await callback.message.answer(
            instruction_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as send_exc:
        logger.error(f"TELEGRAM ERROR: Failed to send instruction_text: {instruction_text!r} | Exception: {send_exc}")
        print(f"TELEGRAM ERROR: Failed to send instruction_text: {instruction_text!r} | Exception: {send_exc}")

async def start_recipe_generation(message: types.Message, state: FSMContext, user: dict, profile: dict, has_profile: bool):
    """Start recipe generation process"""
    # Set FSM state (only if state is provided)
    if state:
        await state.set_state(RecipeStates.waiting_for_photo)
    
    # Get fresh user data to ensure credits are up-to-date
    telegram_user_id = message.from_user.id
    logger.info(f"start_recipe_generation called with telegram_user_id: {telegram_user_id}")
    
    # Re-fetch user data to ensure credits are absolutely current
    user = await get_or_create_user(telegram_user_id)
    
    # Get user's language
    user_language = user.get('language', 'en')
    
    # Create instruction text based on profile availability and language using i18n
    dietary_prefs = profile.get('dietary_preferences', []) if has_profile else []
    allergies = profile.get('allergies', []) if has_profile else []
    dietary_text = ", ".join(dietary_prefs) if dietary_prefs and dietary_prefs != ['none'] else i18n.get_text("profile_dietary_none", user_language)
    allergies_text = ", ".join(allergies) if allergies and allergies != ['none'] else i18n.get_text("profile_allergy_none", user_language)
    goal_text = profile.get('goal', i18n.get_text("profile_goal", user_language, goal="—")) if has_profile else i18n.get_text("profile_goal", user_language, goal="—")
    
    # Escape Markdown characters in user data
    dietary_text = escape_markdown(dietary_text)
    allergies_text = escape_markdown(allergies_text)
    goal_text = escape_markdown(goal_text)

    if has_profile:
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Создание рецепта**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам персонализированный рецепт для тебя!\n\n"
                f"👤 **Твой профиль:**\n"
                f"🎯 Цель: {goal_text}\n"
                f"🍽️ Диета: {dietary_text}\n"
                f"⚠️ Аллергии: {allergies_text}\n\n"
                f"✨ **Я создам рецепты, которые:**\n"
                f"• Соответствуют твоим диетическим предпочтениям\n"
                f"• Избегают твоих аллергий\n"
                f"• Соответствуют твоим фитнес-целям\n"
                f"• Включают информацию о питательности\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a personalized recipe for you!\n\n"
                f"👤 **Your Profile:**\n"
                f"🎯 Goal: {goal_text}\n"
                f"🍽️ Diet: {dietary_text}\n"
                f"⚠️ Allergies: {allergies_text}\n\n"
                f"✨ **I'll create recipes that:**\n"
                f"• Match your dietary preferences\n"
                f"• Avoid your allergies\n"
                f"• Align with your fitness goals\n"
                f"• Include nutritional information\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    else:
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Создание рецепта**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам рецепт для тебя!\n\n"
                f"💡 **Совет:** Настрой свой профиль для персонализированных рецептов, которые соответствуют твоим диетическим предпочтениям и целям.\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a recipe for you!\n\n"
                f"💡 **Tip:** Set up your profile for personalized recipes that match your dietary preferences and goals.\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    
    # Create keyboard with language-appropriate buttons
    if user_language == 'ru':
        profile_button_text = "👤 Настроить профиль" if not has_profile else "👤 Посмотреть профиль"
        cancel_button_text = "❌ Отмена"
    else:
        profile_button_text = "👤 Set Up Profile" if not has_profile else "👤 View Profile"
        cancel_button_text = "❌ Cancel"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=profile_button_text,
                callback_data="action_profile"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=cancel_button_text,
                callback_data="action_main_menu"
            )
        ]
    ])
    
    # Note: Profile data is already escaped with escape_markdown() above
    # Do not use sanitize_markdown_text() as it will undo the escaping
    
    await message.answer(
        instruction_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# Recipe callback handlers
async def handle_recipe_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle recipe-related callbacks"""
    try:
        telegram_user_id = callback.from_user.id
        action = callback.data
        
        # Answer callback to remove loading state
        await callback.answer()
        
        if action == "action_recipe":
            await recipe_callback(callback, state)
        
    except Exception as e:
        logger.error(f"Error in recipe callback: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await callback.answer(i18n.get_text("error_general", user_language))

# Photo processing for recipe generation
async def process_recipe_photo(message: types.Message, state: FSMContext):
    """Process photo for recipe generation"""
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"process_recipe_photo called with telegram_user_id: {telegram_user_id}")
        
        # Get fresh user data to ensure credits are up-to-date
        logger.info(f"Getting fresh user data for telegram_user_id: {telegram_user_id}")
        user = await get_or_create_user(telegram_user_id) # Get user with latest credits
        user_data_with_profile = await get_user_with_profile(telegram_user_id) # Get profile data
        profile = user_data_with_profile['profile']
        has_profile = user_data_with_profile['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Check credits again with fresh data
        if user['credits_remaining'] <= 0:
            # Create keyboard with buy credits button
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="💳 Купить кредиты" if user_language == 'ru' else "💳 Buy Credits",
                    callback_data="action_buy"
                )],
                [types.InlineKeyboardButton(
                    text="🏠 Главное меню" if user_language == 'ru' else "🏠 Main Menu",
                    callback_data="action_main_menu"
                )]
            ])
            
            if user_language == 'ru':
                error_text = (
                    f"❌ **Кредиты закончились**\n\n"
                    f"Для генерации рецептов по фото нужны кредиты\\.\n\n"
                    f"💳 **Получи больше кредитов:**"
                )
            else:
                error_text = (
                    f"❌ **No Credits Remaining**\n\n"
                    f"You need credits to generate recipes from photos\\.\n\n"
                    f"💳 **Get more credits:**"
                )
            
            # Sanitize the error text
            error_text = sanitize_markdown_text(error_text)
            
            await message.answer(
                error_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            await state.clear()
            return
        
        # Send processing message
        if user_language == 'ru':
            processing_msg_text = (
                f"🔄 Обрабатываю ваше фото...\n\n"
                f"🤖 Анализирую ингредиенты и генерирую персонализированный рецепт...\n"
                f"⏱️ Это может занять несколько секунд."
            )
        else:
            processing_msg_text = (
                f"🔄 Processing your photo...\n\n"
                f"🤖 Analyzing ingredients and generating personalized recipe...\n"
                f"⏱️ This may take a few moments."
            )
        
        # Sanitize the processing message
        processing_msg_text = sanitize_markdown_text(processing_msg_text)
        
        processing_msg = await message.answer(
            processing_msg_text,
            parse_mode="Markdown"
        )
        
        try:
            # Get the largest photo
            photo = message.photo[-1]
            
            # Upload photo to R2 with recipe action type
            photo_url = await upload_telegram_photo(
                message.bot,
                photo,
                user['id'],
                action_type="recipe_generation"
            )
            
            if not photo_url:
                upload_error_text = (
                    f"❌ **Upload Failed**\n\n"
                    f"Failed to upload photo\\. Please try again\\."
                )
                upload_error_text = sanitize_markdown_text(upload_error_text)
                
                await processing_msg.edit_text(
                    upload_error_text,
                    parse_mode="Markdown"
                )
                return
            
            # Generate recipe using ML service
            user_data_for_ml = {
                'user': user,
                'profile': profile,
                'has_profile': has_profile
            }
            recipe_data = await generate_recipe_from_photo(photo_url, user_data_for_ml)
            
            if not recipe_data:
                # Create keyboard with main menu button
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="🏠 Главное меню" if user_language == 'ru' else "🏠 Main Menu",
                        callback_data="action_main_menu"
                    )]
                ])
                
                if user_language == 'ru':
                    error_text = (
                        f"❌ **Генерация рецепта не удалась**\n\n"
                        f"Не удалось создать рецепт по этому фото\\. Попробуйте с более четким изображением еды или ингредиентов\\."
                    )
                else:
                    error_text = (
                        f"❌ **Recipe Generation Failed**\n\n"
                        f"Unable to generate recipe from this photo\\. Please try with a clearer image of food or ingredients\\."
                    )
                
                # Sanitize the error text
                error_text = sanitize_markdown_text(error_text)
                
                await processing_msg.edit_text(
                    error_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                return
            
            # Decrement credits
            await decrement_credits(telegram_user_id, 1)
            
            # Log successful recipe generation
            await log_user_action(
                user_id=user['id'],
                action_type="recipe_generation",
                metadata={
                    "username": message.from_user.username,
                    "photo_url": photo_url,
                    "recipe_data": recipe_data,
                    "has_profile": has_profile,
                    "credits_used": 1,
                    "credits_remaining": user['credits_remaining'] - 1
                }
            )
            
            # Format and send recipe
            await send_recipe_response(processing_msg, recipe_data, user)
            
            # Keep FSM state active for more recipe generation
            # User can click "Создать ещё рецепт" or "❌ Отмена" to exit
            
        except Exception as e:
            logger.error(f"Error processing recipe photo for user {telegram_user_id}: {e}")
            from .keyboards import create_main_menu_keyboard
            await processing_msg.edit_text(
                f"❌ **Processing Error**\n\n"
                f"An error occurred while processing your photo\\. Please try again\\.",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard(user_language)
            )
            
    except Exception as e:
        logger.error(f"Error in recipe photo processing for user {telegram_user_id}: {e}")
        # Use default language since we can't safely get user data during error
        user_language = 'en'  # Default to English to avoid additional DB calls during error
        try:
            from .keyboards import create_main_menu_keyboard
            await message.answer(
                i18n.get_text("error_general", user_language),
                reply_markup=create_main_menu_keyboard(user_language)
            )
        except Exception as inner_e:
            logger.error(f"Error sending error message: {inner_e}")
            # Fallback message without any DB dependencies
            await message.answer("❌ An error occurred\\. Please try again later\\.")
        finally:
            # Clear FSM state to prevent user from being stuck
            try:
                await state.clear()
            except Exception:
                pass  # Ignore state clearing errors

async def generate_recipe_from_photo(photo_url: str, user_data: dict) -> dict:
    """Generate recipe from photo using ML service"""
    try:
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Prepare user context for recipe generation
        user_context = {
            "language": user_language,
            "has_profile": has_profile
        }
        
        if has_profile and profile:
            user_context.update({
                "age": profile.get('age'),
                "gender": profile.get('gender'),
                "height_cm": profile.get('height_cm'),
                "weight_kg": profile.get('weight_kg'),
                "activity_level": profile.get('activity_level'),
                "goal": profile.get('goal'),
                "dietary_preferences": profile.get('dietary_preferences', []),
                "allergies": profile.get('allergies', []),
                "daily_calories_target": profile.get('daily_calories_target')
            })
        
        # Call ML service for recipe generation
        ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
        
        # Prepare form data for ML service
        form_data = aiohttp.FormData()
        form_data.add_field('image_url', photo_url)
        form_data.add_field('telegram_user_id', str(user['id']))
        form_data.add_field('user_context', json.dumps(user_context))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ml_service_url}{Routes.ML_GENERATE_RECIPE}",
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"ML service error: {response.status}")
                    response_text = await response.text()
                    logger.error(f"ML service response: {response_text}")
                    return None
                    
    except Exception as e:
        logger.error(f"Error generating recipe from photo: {e}")
        return None

async def send_recipe_response(message: types.Message, recipe_data: dict, user: dict):
    """Send formatted recipe response to user"""
    try:
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Format recipe response
        recipe_text = format_recipe_text(recipe_data, user_language)
        
        # Sanitize the recipe text
        recipe_text = sanitize_markdown_text(recipe_text)
        
        # Create action buttons with language support
        if user_language == 'ru':
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🍽️ Создать ещё рецепт",
                        callback_data="action_recipe"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🍕 Анализ еды",
                        callback_data="action_analyze_info"
                    ),
                    types.InlineKeyboardButton(
                        text="📊 Дневной план",
                        callback_data="action_daily"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🏠 Главное меню",
                        callback_data="action_main_menu"
                    )
                ]
            ])
        else:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🍽️ Generate Another Recipe",
                        callback_data="action_recipe"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🍕 Analyze Food Instead",
                        callback_data="action_analyze_info"
                    ),
                    types.InlineKeyboardButton(
                        text="📊 View Daily Plan",
                        callback_data="action_daily"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="🏠 Main Menu",
                        callback_data="action_main_menu"
                    )
                ]
            ])
        
        await message.edit_text(
            recipe_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error sending recipe response: {e}")
        error_text = (
            f"✅ **Recipe Generated\\!**\n\n"
            f"Your personalized recipe has been created successfully\\!"
        )
        error_text = sanitize_markdown_text(error_text)
        
        await message.edit_text(
            error_text,
            parse_mode="Markdown"
        )

def format_recipe_text(recipe_data: dict, language: str = 'en') -> str:
    """Format recipe data into readable text"""
    try:
        recipe_name = recipe_data.get('name', 'Delicious Recipe')
        description = recipe_data.get('description', '')
        prep_time = recipe_data.get('prep_time', 'N/A')
        cook_time = recipe_data.get('cook_time', 'N/A')
        servings = recipe_data.get('servings', 'N/A')
        
        ingredients = recipe_data.get('ingredients', [])
        instructions = recipe_data.get('instructions', [])
        nutrition = recipe_data.get('nutrition', {})
        
        # Sanitize Markdown characters in recipe data
        recipe_name = sanitize_markdown_text(recipe_name)
        description = sanitize_markdown_text(description)
        prep_time = sanitize_markdown_text(str(prep_time))
        cook_time = sanitize_markdown_text(str(cook_time))
        servings = sanitize_markdown_text(str(servings))
        
        # Build recipe text
        text = f"🍽️ **{recipe_name}**\n\n"
        
        if description:
            text += f"📝 {description}\n\n"
        
        # Recipe info with translations
        if language == 'ru':
            text += f"⏱️ **Время подготовки:** {prep_time}\n"
            text += f"🔥 **Время готовки:** {cook_time}\n"
            text += f"👥 **Порций:** {servings}\n\n"
        else:
            text += f"⏱️ **Prep Time:** {prep_time}\n"
            text += f"🔥 **Cook Time:** {cook_time}\n"
            text += f"👥 **Servings:** {servings}\n\n"
        
        # Ingredients
        if ingredients:
            if language == 'ru':
                text += f"🛒 **Ингредиенты:**\n"
            else:
                text += f"🛒 **Ingredients:**\n"
            for ingredient in ingredients:
                sanitized_ingredient = sanitize_markdown_text(str(ingredient))
                text += f"• {sanitized_ingredient}\n"
            text += "\n"
        
        # Instructions
        if instructions:
            if language == 'ru':
                text += f"👨‍🍳 **Инструкции:**\n"
            else:
                text += f"👨‍🍳 **Instructions:**\n"
            for i, instruction in enumerate(instructions, 1):
                sanitized_instruction = sanitize_markdown_text(str(instruction))
                text += f"{i}. {sanitized_instruction}\n"
            text += "\n"
        
        # Nutrition info
        if nutrition:
            if language == 'ru':
                text += f"📊 **Питательность (на порцию):**\n"
                if 'calories' in nutrition:
                    calories = sanitize_markdown_text(str(nutrition['calories']))
                    text += f"🔥 Калории: {calories}\n"
                if 'protein' in nutrition:
                    protein = sanitize_markdown_text(str(nutrition['protein']))
                    text += f"🥩 Белок: {protein}г\n"
                if 'carbs' in nutrition:
                    carbs = sanitize_markdown_text(str(nutrition['carbs']))
                    text += f"🍞 Углеводы: {carbs}г\n"
                if 'fat' in nutrition:
                    fat = sanitize_markdown_text(str(nutrition['fat']))
                    text += f"🥑 Жиры: {fat}г\n"
            else:
                text += f"📊 **Nutrition (per serving):**\n"
                if 'calories' in nutrition:
                    calories = sanitize_markdown_text(str(nutrition['calories']))
                    text += f"🔥 Calories: {calories}\n"
                if 'protein' in nutrition:
                    protein = sanitize_markdown_text(str(nutrition['protein']))
                    text += f"🥩 Protein: {protein}g\n"
                if 'carbs' in nutrition:
                    carbs = sanitize_markdown_text(str(nutrition['carbs']))
                    text += f"🍞 Carbs: {carbs}g\n"
                if 'fat' in nutrition:
                    fat = sanitize_markdown_text(str(nutrition['fat']))
                    text += f"🥑 Fat: {fat}g\n"
        
        # Sanitize the final recipe text
        text = sanitize_markdown_text(text)
        return text
        
    except Exception as e:
        logger.error(f"Error formatting recipe text: {e}")
        if language == 'ru':
            fallback_text = f"🍽️ **Рецепт создан\\!**\n\nВаш персонализированный рецепт готов\\!"
        else:
            fallback_text = f"🍽️ **Recipe Generated\\!**\n\nYour personalized recipe is ready\\!"
        return sanitize_markdown_text(fallback_text)