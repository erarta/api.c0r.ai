"""
Command handlers for NeuCor Telegram Bot
"""
import os
from datetime import datetime
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user, log_user_action, get_user_with_profile, get_daily_calories_consumed
from .payments import create_invoice_message

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
            "📞 **Support:** Contact @your_support_bot"
        )
        
        await message.answer(help_text, parse_mode="Markdown")
        logger.info(f"/help by user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in /help: {e}")
        await message.answer("An error occurred. Please try again later.")

# /status command handler - NEW FEATURE
async def status_command(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        logger.info(f"Status command called by user {telegram_user_id} (@{message.from_user.username})")
        
        user = await get_or_create_user(telegram_user_id)
        logger.info(f"User {telegram_user_id} data from database: {user}")
        
        # Log user action
        await log_user_action(
            user_id=user['id'],
            action_type="status",
            metadata={
                "username": message.from_user.username,
                "credits_remaining": user['credits_remaining'],
                "total_paid": user.get('total_paid', 0)
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
            f"💰 Total paid: *${user.get('total_paid', 0):.2f}*\n"
            f"📅 Member since: `{created_date}`\n\n"
            f"🤖 System: *c0r.ai v0.3.4*\n"
            f"🌐 Status: *Online*\n"
            f"⚡ Powered by c0r AI Vision"
        )
        
        logger.info(f"Sending status to user {telegram_user_id}: credits={user['credits_remaining']}")
        await message.answer(status_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in /status for user {telegram_user_id}: {e}")
        import traceback
        logger.error(f"Status command error traceback: {traceback.format_exc()}")
        await message.answer("An error occurred while fetching your status. Please try again later.")

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
                "total_paid": user.get('total_paid', 0)
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
            await status_command(callback.message)
        elif action == "help":
            await help_command(callback.message)
        elif action == "buy":
            await buy_credits_command(callback.message)
        elif action == "profile":
            await callback.message.answer(
                "👤 **Profile Setup**\n\n"
                "To calculate your daily calorie needs, I need some information about you.\n"
                "Use the /profile command to set up your profile with:\n\n"
                "• Age\n"
                "• Gender\n"
                "• Height\n"
                "• Weight\n"
                "• Activity level\n"
                "• Goal (lose/maintain/gain weight)\n\n"
                "🔜 **Coming soon:** Full profile setup wizard!",
                parse_mode="Markdown"
            )
        
        logger.info(f"Action callback '{action}' handled for user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error in action callback: {e}")
        await callback.answer("An error occurred. Please try again later.") 