"""
Command handlers for NeuCor Telegram Bot
"""
import os
from datetime import datetime
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user, log_user_action, get_user_with_profile, get_daily_calories_consumed, get_user_total_paid
from .keyboards import create_main_menu_keyboard, create_main_menu_text
from config import VERSION

# /start command handler
async def start_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        username = message.from_user.username or "User"
        user = await get_or_create_user(telegram_user_id)
        
        # Log user action
        await log_user_action(
            user_id=user['id'],
            action_type="start",
            metadata={
                "username": username,
                "first_name": message.from_user.first_name,
                "credits_remaining": user['credits_remaining']
            }
        )
        
        # Create interactive welcome message
        welcome_text = (
            f"🎉 **Welcome to c0r.ai Food Analyzer!**\n\n"
            f"👋 Hello {message.from_user.first_name}!\n"
            f"💳 You have **{user['credits_remaining']} credits** remaining\n\n"
            f"🍎 **What I can do:**\n"
            f"• Analyze your food photos for calories, protein, fats, carbs\n"
            f"• Calculate your daily calorie needs\n"
            f"• Track your nutrition goals\n\n"
            f"🚀 **Ready to start?** Choose an option below:"
        )
        
        # Create interactive keyboard
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🍕 Analyze Food Photo",
                    callback_data="action_analyze_info"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📊 Check My Status",
                    callback_data="action_status"
                ),
                types.InlineKeyboardButton(
                    text="ℹ️ Help & Guide",
                    callback_data="action_help"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="💳 Buy More Credits",
                    callback_data="action_buy"
                ),
                types.InlineKeyboardButton(
                    text="👤 My Profile",
                    callback_data="action_profile"
                )
            ]
        ])
        
        await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)
        logger.info(f"/start by user {telegram_user_id} (@{username})")
        
    except Exception as e:
        logger.error(f"Error in /start: {e}")
        await message.answer("An error occurred. Please try again later.")

# /help command handler
async def help_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        
        # Log user action
        await log_user_action(
            user_id=user['id'],
            action_type="help",
            metadata={
                "username": message.from_user.username,
                "credits_remaining": user['credits_remaining']
            }
        )
        
        help_text = (
            "🤖 **c0r.ai Food Analyzer - Help Guide**\n\n"
            "📸 **How to use:**\n"
            "1. Send me a food photo\n"
            "2. I'll analyze calories, protein, fats, and carbs\n"
            "3. Get instant nutrition information\n\n"
            "🆓 **Free credits:**\n"
            "• You start with 3 free credits\n"
            "• Each photo analysis costs 1 credit\n\n"
            "🎯 **Features:**\n"
            "• Accurate calorie counting\n"
            "• Detailed macro breakdown\n"
            "• Daily calorie calculation\n"
            "• Personal nutrition tracking\n\n"
            "💡 **Commands:**\n"
            "• /start - Main menu with interactive buttons\n"
            "• /help - This help guide\n"
            "• /status - Check your account status\n"
            "• /buy - Purchase more credits\n"
            "• /profile - Set up your personal profile\n"
            "• /daily - View daily nutrition plan & progress\n\n"
            "💳 **Need more credits?**\n"
            "Use /buy to purchase additional credits when you run out.\n\n"
            "📞 **Support:** Contact team@c0r.ai"
        )
        
        await message.answer(help_text, parse_mode="Markdown", reply_markup=create_main_menu_keyboard())
        logger.info(f"/help by user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in /help: {e}")
        await message.answer("An error occurred. Please try again later.")

# Help callback handler - handles button clicks
async def help_callback(callback: types.CallbackQuery):
    """Handle help callback from button clicks"""
    try:
        telegram_user_id = callback.from_user.id
        user = await get_or_create_user(telegram_user_id)
        
        # Log user action with correct user data
        await log_user_action(
            user_id=user['id'],
            action_type="help",
            metadata={
                "username": callback.from_user.username,  # ← ПРАВИЛЬНО: используем callback.from_user
                "credits_remaining": user['credits_remaining']
            }
        )
        
        help_text = (
            "🤖 **c0r.ai Food Analyzer - Help Guide**\n\n"
            "📸 **How to use:**\n"
            "1. Send me a food photo\n"
            "2. I'll analyze calories, protein, fats, and carbs\n"
            "3. Get instant nutrition information\n\n"
            "🆓 **Free credits:**\n"
            "• You start with 3 free credits\n"
            "• Each photo analysis costs 1 credit\n\n"
            "🎯 **Features:**\n"
            "• Accurate calorie counting\n"
            "• Detailed macro breakdown\n"
            "• Daily calorie calculation\n"
            "• Personal nutrition tracking\n\n"
            "💡 **Commands:**\n"
            "• /start - Main menu with interactive buttons\n"
            "• /help - This help guide\n"
            "• /status - Check your account status\n"
            "• /buy - Purchase more credits\n"
            "• /profile - Set up your personal profile\n"
            "• /daily - View daily nutrition plan & progress\n\n"
            "💳 **Need more credits?**\n"
            "Use /buy to purchase additional credits when you run out.\n\n"
            "📞 **Support:** Contact team@c0r.ai"
        )
        
        await callback.message.answer(help_text, parse_mode="Markdown", reply_markup=create_main_menu_keyboard())
        logger.info(f"Help callback by user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in help callback: {e}")
        await callback.message.answer("An error occurred. Please try again later.")

# /status command handler - NEW FEATURE
async def status_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"Status command called by user {telegram_user_id} (@{message.from_user.username})")
        
        user = await get_or_create_user(telegram_user_id)
        logger.info(f"User {telegram_user_id} data from database: {user}")
        
        # Get actual total paid from payments table
        total_paid = await get_user_total_paid(user['id'])
        
        # Log user action
        await log_user_action(
            user_id=user['id'],
            action_type="status",
            metadata={
                "username": message.from_user.username,
                "credits_remaining": user['credits_remaining'],
                "total_paid": total_paid
            }
        )
        
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
            f"💰 Total paid: *{total_paid:.2f} RUB*\n"
            f"📅 Member since: `{created_date}`\n\n"
            f"🤖 System: *c0r.ai v{VERSION}*\n"
            f"🌐 Status: *Online*\n"
            f"⚡ Powered by c0r AI Vision"
        )
        
        logger.info(f"Sending status to user {telegram_user_id}: credits={user['credits_remaining']}")
        await message.answer(status_text, parse_mode="Markdown", reply_markup=create_main_menu_keyboard())
        
    except Exception as e:
        logger.error(f"Error in /status for user {telegram_user_id}: {e}")
        import traceback
        logger.error(f"Status command error traceback: {traceback.format_exc()}")
        await message.answer("An error occurred while fetching your status. Please try again later.")

# Status callback handler - handles button clicks
async def status_callback(callback: types.CallbackQuery):
    """Handle status callback from button clicks"""
    try:
        telegram_user_id = callback.from_user.id  # ← ПРАВИЛЬНО: используем callback.from_user
        logger.info(f"Status callback called by user {telegram_user_id} (@{callback.from_user.username})")
        
        user = await get_or_create_user(telegram_user_id)
        logger.info(f"User {telegram_user_id} data from database: {user}")
        
        # Get actual total paid from payments table
        total_paid = await get_user_total_paid(user['id'])
        
        # Log user action with correct user data
        await log_user_action(
            user_id=user['id'],
            action_type="status",
            metadata={
                "username": callback.from_user.username,  # ← ПРАВИЛЬНО: используем callback.from_user
                "credits_remaining": user['credits_remaining'],
                "total_paid": total_paid
            }
        )
        
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
            f"💰 Total paid: *{total_paid:.2f} RUB*\n"
            f"📅 Member since: `{created_date}`\n\n"
            f"🤖 System: *c0r.ai v{VERSION}*\n"
            f"🌐 Status: *Online*\n"
            f"⚡ Powered by c0r AI Vision"
        )
        
        logger.info(f"Sending status to user {telegram_user_id}: credits={user['credits_remaining']}")
        await callback.message.answer(status_text, parse_mode="Markdown", reply_markup=create_main_menu_keyboard())
        
    except Exception as e:
        logger.error(f"Error in status callback for user {telegram_user_id}: {e}")
        import traceback
        logger.error(f"Status callback error traceback: {traceback.format_exc()}")
        await callback.message.answer("An error occurred while fetching your status. Please try again later.")

# /buy command handler - NEW FEATURE
async def buy_credits_command(message: types.Message):
    """
    Handle /buy command - show payment options
    """
    try:
        telegram_user_id = message.from_user.id
        username = message.from_user.username
        
        logger.info(f"=== BUY_COMMAND DEBUG ===")
        logger.info(f"/buy command by user {telegram_user_id} (@{username})")
        logger.info(f"Message object type: {type(message)}")
        logger.info(f"Message from_user: {message.from_user}")
        logger.info(f"========================")
        
        user = await get_or_create_user(telegram_user_id)
        
        # Log user action
        await log_user_action(
            user_id=user['id'],
            action_type="buy",
            metadata={
                "username": username,
                "credits_remaining": user['credits_remaining'],
                "total_paid": await get_user_total_paid(user['id'])
            }
        )
        
        # Show current credits and payment options
        await message.answer(
            f"💳 **Buy Credits**\n\n"
            f"Current credits: *{user['credits_remaining']}*\n\n"
            f"📦 **Basic Plan**: 20 credits for 99 RUB\n"
            f"📦 **Pro Plan**: 100 credits for 399 RUB\n\n"
            f"Choose a plan to continue:",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="💰 Basic Plan (99 RUB)",
                        callback_data="buy_basic"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="💎 Pro Plan (399 RUB)", 
                        callback_data="buy_pro"
                    )
                ]
            ])
        )
        
    except Exception as e:
        logger.error(f"Error in /buy for user {telegram_user_id}: {e}")
        await message.answer("An error occurred. Please try again later.")

# Buy callback handler - handles button clicks
async def buy_callback(callback: types.CallbackQuery):
    """Handle buy callback from button clicks"""
    try:
        telegram_user_id = callback.from_user.id
        username = callback.from_user.username
        
        logger.info(f"=== BUY_CALLBACK DEBUG ===")
        logger.info(f"Buy callback by user {telegram_user_id} (@{username})")
        logger.info(f"Callback object type: {type(callback)}")
        logger.info(f"Callback from_user: {callback.from_user}")
        logger.info(f"========================")
        
        user = await get_or_create_user(telegram_user_id)
        
        # Log user action with correct user data
        await log_user_action(
            user_id=user['id'],
            action_type="buy",
            metadata={
                "username": username,  # ← ПРАВИЛЬНО: используем callback.from_user
                "credits_remaining": user['credits_remaining'],
                "total_paid": await get_user_total_paid(user['id'])
            }
        )
        
        # Show current credits and payment options
        await callback.message.answer(
            f"💳 **Buy Credits**\n\n"
            f"Current credits: *{user['credits_remaining']}*\n\n"
            f"📦 **Basic Plan**: 20 credits for 99 RUB\n"
            f"📦 **Pro Plan**: 100 credits for 399 RUB\n\n"
            f"Choose a plan to continue:",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="💰 Basic Plan (99 RUB)",
                        callback_data="buy_basic"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="💎 Pro Plan (399 RUB)", 
                        callback_data="buy_pro"
                    )
                ]
            ])
        )
        
    except Exception as e:
        logger.error(f"Error in buy callback for user {telegram_user_id}: {e}")
        await callback.message.answer("An error occurred. Please try again later.")

# Profile callback handler - handles button clicks
async def profile_callback(callback: types.CallbackQuery):
    """Handle profile callback from button clicks"""
    try:
        telegram_user_id = callback.from_user.id
        
        # Answer callback to remove loading state
        await callback.answer()
        
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log profile action with correct user data
        await log_user_action(
            user_id=user['id'],
            action_type="profile",
            metadata={
                "username": callback.from_user.username,  # ← ПРАВИЛЬНО: используем callback.from_user
                "has_profile": has_profile,
                "action": "view_menu"
            }
        )
        
        if has_profile:
            # Show existing profile
            await show_profile_info(callback, user, profile)
        else:
            # Show setup prompt
            await show_profile_setup_info(callback, user)
            
    except Exception as e:
        logger.error(f"Error in profile callback for user {telegram_user_id}: {e}")
        await callback.message.answer("❌ An error occurred. Please try again later.")

async def show_profile_info(callback: types.CallbackQuery, user: dict, profile: dict):
    """Show profile information for existing profile"""
    # Format profile data
    age = profile.get('age', 'Not set')
    gender = "👨 Male" if profile.get('gender') == 'male' else "👩 Female" if profile.get('gender') == 'female' else 'Not set'
    height = f"{profile.get('height_cm', 'Not set')} cm" if profile.get('height_cm') else 'Not set'
    weight = f"{profile.get('weight_kg', 'Not set')} kg" if profile.get('weight_kg') else 'Not set'
    
    activity_labels = {
        'sedentary': '😴 Sedentary',
        'lightly_active': '🚶 Lightly Active',
        'moderately_active': '🏃 Moderately Active',
        'very_active': '💪 Very Active',
        'extremely_active': '🏋️ Extremely Active'
    }
    activity = activity_labels.get(profile.get('activity_level'), 'Not set')
    
    goal_labels = {
        'lose_weight': '📉 Lose weight',
        'maintain_weight': '⚖️ Maintain weight',
        'gain_weight': '📈 Gain weight'
    }
    goal = goal_labels.get(profile.get('goal'), 'Not set')
    
    daily_calories = profile.get('daily_calories_target', 'Not calculated')
    if daily_calories != 'Not calculated':
        daily_calories = f"{daily_calories:,} calories"
    
    profile_text = (
        f"👤 **Your Profile**\n\n"
        f"📅 **Age:** {age}\n"
        f"👤 **Gender:** {gender}\n"
        f"📏 **Height:** {height}\n"
        f"⚖️ **Weight:** {weight}\n"
        f"🏃 **Activity Level:** {activity}\n"
        f"🎯 **Goal:** {goal}\n\n"
        f"🔥 **Daily Calorie Target:** {daily_calories}"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="✏️ Edit Profile",
                callback_data="profile_edit"
            )
        ]
    ])
    
    await callback.message.answer(profile_text, parse_mode="Markdown", reply_markup=keyboard)

async def show_profile_setup_info(callback: types.CallbackQuery, user: dict):
    """Show profile setup information for new users"""
    setup_text = (
        f"👤 **Profile Setup**\n\n"
        f"🎯 To provide you with personalized nutrition recommendations and daily calorie targets, "
        f"I need some information about you.\n\n"
        f"📊 **What I'll calculate for you:**\n"
        f"• Daily calorie target based on your goals\n"
        f"• Personalized nutrition recommendations\n"
        f"• Progress tracking towards your goals\n\n"
        f"🔒 **Your data is private and secure.**\n\n"
        f"Ready to get started?"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="🚀 Set Up Profile",
                callback_data="profile_start_setup"
            )
        ]
    ])
    
    await callback.message.answer(setup_text, parse_mode="Markdown", reply_markup=keyboard)

# Callback handlers for interactive buttons
async def handle_action_callback(callback: types.CallbackQuery):
    """
    Handle callbacks from interactive buttons in /start command
    """
    try:
        telegram_user_id = callback.from_user.id
        action = callback.data.replace("action_", "")
        
        # Answer callback to remove loading state
        await callback.answer()
        
        if action == "analyze_info":
            await callback.message.answer(
                "📸 **How to Analyze Food Photos:**\n\n"
                "1. Take a clear photo of your food\n"
                "2. Make sure the food is well-lit and visible\n"
                "3. Send the photo to me\n"
                "4. I'll analyze it and give you:\n"
                "   • Calories\n"
                "   • Protein\n"
                "   • Fats\n"
                "   • Carbohydrates\n\n"
                "💡 **Tips for better results:**\n"
                "• Include the whole meal in the photo\n"
                "• Avoid blurry or dark photos\n"
                "• One dish per photo works best\n\n"
                "📤 **Ready?** Send me your food photo now!",
                parse_mode="Markdown"
            )
        elif action == "status":
            await status_callback(callback)  # ← ИСПРАВЛЕНО: используем callback вместо callback.message
        elif action == "help":
            await help_callback(callback)  # ← ИСПРАВЛЕНО: используем callback вместо callback.message
        elif action == "buy":
            await buy_callback(callback)  # ← ИСПРАВЛЕНО: используем callback вместо callback.message
        elif action == "profile":
            await profile_callback(callback)  # ← ИСПРАВЛЕНО: используем реальную функцию профиля
        elif action == "daily":
            # Handle daily plan callback
            from .daily import daily_callback
            await daily_callback(callback)
        elif action == "nutrition_insights":
            # Handle nutrition insights callback
            from .nutrition import nutrition_insights_callback
            await nutrition_insights_callback(callback)
        elif action == "weekly_report":
            # Handle weekly report callback
            from .nutrition import weekly_report_command
            await weekly_report_command(callback.message)
        elif action == "water_tracker":
            # Handle water tracker callback
            from .nutrition import water_tracker_command
            await water_tracker_command(callback.message)
        elif action == "main_menu":
            # Show main menu
            menu_text, menu_keyboard = create_main_menu_text()
            await callback.message.answer(menu_text, parse_mode="Markdown", reply_markup=menu_keyboard)
        
        logger.info(f"Action callback '{action}' handled for user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in action callback: {e}")
        await callback.answer("An error occurred. Please try again later.") 