"""
Shared keyboard utilities for c0r.ai Telegram Bot
This module contains reusable keyboard functions to avoid circular imports
"""
from aiogram import types


def create_main_menu_keyboard():
    """Create keyboard with Main Menu button"""
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="🏠 Main Menu",
                callback_data="action_main_menu"
            )
        ]
    ])


def create_payment_success_keyboard():
    """Create keyboard for payment success message with navigation options"""
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="📊 Check My Status",
                callback_data="action_status"
            ),
            types.InlineKeyboardButton(
                text="❓ Help & Guide",
                callback_data="action_help"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="👤 My Profile",
                callback_data="action_profile"
            ),
            types.InlineKeyboardButton(
                text="📅 Daily Plan",
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


def create_main_menu_text():
    """Create main menu message with interactive buttons"""
    return (
        f"🚀 **Choose an option:**"
    ), types.InlineKeyboardMarkup(inline_keyboard=[
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
                text="🔬 Nutrition Insights",
                callback_data="action_nutrition_insights"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="👤 My Profile",
                callback_data="action_profile"
            ),
            types.InlineKeyboardButton(
                text="📅 Daily Plan",
                callback_data="action_daily"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="📈 Weekly Report",
                callback_data="action_weekly_report"
            ),
            types.InlineKeyboardButton(
                text="💧 Water Tracker",
                callback_data="action_water_tracker"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="💳 Buy More Credits",
                callback_data="action_buy"
            ),
            types.InlineKeyboardButton(
                text="ℹ️ Help & Guide",
                callback_data="action_help"
            )
        ]
    ]) 