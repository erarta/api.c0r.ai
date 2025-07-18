"""
Shared keyboard utilities for c0r.ai Telegram Bot
This module contains reusable keyboard functions to avoid circular imports
"""
from aiogram import types
from i18n.i18n import i18n


def create_main_menu_keyboard(language: str = "en"):
    """Create keyboard with Main Menu button"""
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_main_menu", language),
                callback_data="action_main_menu"
            )
        ]
    ])


def create_payment_success_keyboard(language: str = "en"):
    """Create keyboard for payment success message with navigation options"""
    from i18n.i18n import i18n
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_check_status", language),
                callback_data="action_status"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_help_guide", language),
                callback_data="action_help"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_my_profile", language),
                callback_data="action_profile"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_daily_plan", language),
                callback_data="action_daily"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_main_menu", language),
                callback_data="action_main_menu"
            )
        ]
    ])


def create_main_menu_text(language: str = "en", has_profile: bool = False):
    """Create main menu message with interactive buttons"""
    from i18n.i18n import i18n
    
    # Base buttons that are always shown
    keyboard = [
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_analyze_food", language),
                callback_data="action_analyze_info"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_check_status", language),
                callback_data="action_status"
            )
        ]
    ]
    
    # Add nutrition insights button only if user has profile
    if has_profile:
        keyboard[1].append(
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_nutrition_insights", language),
                callback_data="action_nutrition_insights"
            )
        )
    
    # Add profile and daily plan buttons
    keyboard.extend([
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_my_profile", language),
                callback_data="action_profile"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_daily_plan", language),
                callback_data="action_daily"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_weekly_report", language),
                callback_data="action_weekly_report"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_water_tracker", language),
                callback_data="action_water_tracker"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_buy_credits", language),
                callback_data="action_buy"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_help_guide", language),
                callback_data="action_help"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_language", language),
                callback_data="action_language"
            )
        ]
    ])
    
    return (
        f"{i18n.get_text('main_menu_title', language)}"
    ), types.InlineKeyboardMarkup(inline_keyboard=keyboard) 