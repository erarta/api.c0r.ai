"""
Advanced nutrition analysis and insights for c0r.ai
Provides BMI, ideal weight, water needs, macro distribution, and recommendations
"""

from aiogram import types
from loguru import logger
from common.supabase_client import get_user_with_profile, log_user_action, get_or_create_user
from common.nutrition_calculations import (
    calculate_bmi, calculate_ideal_weight, calculate_water_needs,
    calculate_macro_distribution, calculate_metabolic_age,
    calculate_meal_portions, get_nutrition_recommendations
)
from .keyboards import create_main_menu_keyboard
from i18n.i18n import i18n
from datetime import datetime, timedelta
import re


async def nutrition_insights_command(message: types.Message):
    """
    Show nutrition insights menu with buttons for different sections
    """
    try:
        telegram_user_id = message.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log nutrition insights action
        await log_user_action(
            user_id=user['id'],
            action_type="nutrition_insights",
            metadata={
                "username": message.from_user.username,
                "has_profile": has_profile
            }
        )
        
        # Check if we have enough data for nutrition insights
        required_fields = ['age', 'weight_kg', 'height_cm', 'gender', 'activity_level', 'goal']
        
        # If profile is None, all fields are missing
        if profile is None:
            missing_fields = required_fields
        else:
            missing_fields = [field for field in required_fields if not profile.get(field)]
        
        if missing_fields:
            # Get user's language
            user = await get_or_create_user(message.from_user.id)
            user_language = user.get('language', 'en')
            
            # Create keyboard with back button
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text('btn_back', user_language),
                        callback_data="action_main_menu"
                    )
                ]
            ])
            
            await message.answer(
                i18n.get_text("nutrition_incomplete", user_language, missing_fields=', '.join(missing_fields)),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Show nutrition insights menu
        await show_nutrition_insights_menu(message, user, profile)
        
    except Exception as e:
        logger.error(f"Error in nutrition_insights_command: {e}")
        # Get user's language
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(
            i18n.get_text("nutrition_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def nutrition_insights_callback(callback: types.CallbackQuery):
    """Handle nutrition insights callback from button clicks"""
    try:
        # Answer callback to remove loading state
        await callback.answer()
        
        # Get the correct user ID from callback (not from bot message)
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log nutrition insights action
        await log_user_action(
            user_id=user['id'],
            action_type="nutrition_insights",
            metadata={
                "username": callback.from_user.username,
                "has_profile": has_profile
            }
        )
        
        # Check if we have enough data for nutrition insights
        required_fields = ['age', 'weight_kg', 'height_cm', 'gender', 'activity_level', 'goal']
        
        # If profile is None, all fields are missing
        if profile is None:
            missing_fields = required_fields
        else:
            missing_fields = [field for field in required_fields if not profile.get(field)]
        
        if missing_fields:
            # Get user's language
            user = await get_or_create_user(callback.from_user.id)
            user_language = user.get('language', 'en')
            
            # Create keyboard with back button
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text('btn_back', user_language),
                        callback_data="action_main_menu"
                    )
                ]
            ])
            
            await callback.message.answer(
                i18n.get_text("nutrition_incomplete", user_language, missing_fields=', '.join(missing_fields)),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        # Show nutrition insights menu
        await show_nutrition_insights_menu(callback.message, user, profile)
        
    except Exception as e:
        logger.error(f"Error in nutrition_insights_callback: {e}")
        # Get user's language
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await callback.message.answer(
            i18n.get_text("nutrition_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


def sanitize_markdown_text(text: str) -> str:
    """
    Sanitize markdown text to prevent Telegram parsing issues
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for Telegram markdown
    """
    # Fix problematic **\n** patterns by adding space after **
    text = text.replace('**\n**', '** \n**')
    
    # Fix any triple asterisks
    text = text.replace('***', '** *')
    
    # Fix any quadruple asterisks
    text = text.replace('****', '** **')
    
    # Fix empty bold patterns
    text = text.replace('**  **', '** **')
    
    return text


async def generate_nutrition_insights(profile: dict, user: dict) -> str:
    """
    Generate comprehensive nutrition insights text
    
    Args:
        profile: User profile data
        user: User data
        
    Returns:
        Formatted insights text
    """
    insights = []
    
    # Get user's language
    user_language = user.get('language', 'en')
    
    # Header
    insights.append(f"{i18n.get_text('nutrition_analysis_title', user_language)}\n")
    
    # Basic info
    age = profile.get('age', 0)
    gender = profile.get('gender', 'unknown')
    weight = profile.get('weight_kg', 0)
    height = profile.get('height_cm', 0)
    activity = profile.get('activity_level', 'sedentary')
    goal = profile.get('goal', 'maintain_weight')
    daily_calories = profile.get('daily_calories_target', 0)
    
    # 1. BMI Analysis
    if weight > 0 and height > 0:
        bmi_data = calculate_bmi(weight, height, user_language)
        insights.append(f"{i18n.get_text('nutrition_bmi_title', user_language)}")
        insights.append(f"{bmi_data['emoji']} **{bmi_data['bmi']}** - {bmi_data['description']}")
        insights.append(f"💡 {bmi_data['motivation']}")
        insights.append("")
        
        # Ideal weight
        ideal_weight = calculate_ideal_weight(height, gender)
        insights.append(f"{i18n.get_text('nutrition_ideal_weight_title', user_language)}")
        insights.append(f"**{ideal_weight['range']}** ({i18n.get_text('bmi_based', user_language)})")
        insights.append(f"**{ideal_weight['broca']} {i18n.get_text('kg', user_language)}** ({i18n.get_text('broca_formula', user_language)})")
        insights.append("")
    
    # 2. Metabolic Age
    if age > 0 and weight > 0 and height > 0:
        metabolic_data = calculate_metabolic_age(age, gender, weight, height, activity, user_language)
        insights.append(f"{i18n.get_text('nutrition_metabolic_age_title', user_language)}")
        insights.append(f"{metabolic_data['emoji']} **{metabolic_data['metabolic_age']} {i18n.get_text('years', user_language)}** (vs {age} {i18n.get_text('actual', user_language)})")
        insights.append(f"{metabolic_data['description']}")
        insights.append(f"💡 {metabolic_data['motivation']}")
        insights.append("")
    
    # 3. Daily Water Needs
    if weight > 0:
        water_data = calculate_water_needs(weight, activity)
        insights.append(f"{i18n.get_text('nutrition_water_needs_title', user_language)}")
        insights.append(f"**{water_data['liters']}{i18n.get_text('L', user_language)}** ({water_data['glasses']} {i18n.get_text('glasses', user_language)})")
        insights.append(f"{i18n.get_text('base', user_language).capitalize()}: {water_data['base_ml']}{i18n.get_text('ml', user_language)} + {i18n.get_text('activity', user_language).capitalize()}: {water_data['activity_bonus']}{i18n.get_text('ml', user_language)}")
        insights.append("")
    
    # 4. Macro Distribution
    if daily_calories > 0:
        macro_data = calculate_macro_distribution(daily_calories, goal)
        insights.append(f"{i18n.get_text('nutrition_macro_title', user_language)}")
        insights.append(f"**Protein:** {macro_data['protein']['grams']}{i18n.get_text('g', user_language)} ({macro_data['protein']['percent']}%)")
        insights.append(f"**Carbs:** {macro_data['carbs']['grams']}{i18n.get_text('g', user_language)} ({macro_data['carbs']['percent']}%)")
        insights.append(f"**Fats:** {macro_data['fat']['grams']}{i18n.get_text('g', user_language)} ({macro_data['fat']['percent']}%)")
        insights.append("")
        
        # Meal portions
        meal_data = calculate_meal_portions(daily_calories, 3, user_language)
        insights.append(f"{i18n.get_text('nutrition_meal_distribution_title', user_language)}")
        for meal in meal_data['meals']:
            insights.append(f"**{meal['name']}:** {meal['calories']} {i18n.get_text('cal', user_language)} ({meal['percentage']}%)")
        insights.append("")
    
    # 5. Personalized Recommendations
    recommendations = get_nutrition_recommendations(profile, [], user_language)
    if recommendations:
        insights.append(f"{i18n.get_text('nutrition_personal_recommendations_title', user_language)}")
        for rec in recommendations[:4]:  # Show top 4 recommendations
            insights.append(f"• {rec}")
        insights.append("")
    
    # 6. Goal-specific advice
    goal_advice = get_goal_specific_advice(goal, profile, user_language)
    if goal_advice:
        insights.append(f"{i18n.get_text('nutrition_goal_advice_title', user_language)}")
        # Split the advice into lines and add each line
        advice_lines = goal_advice.split('\n')
        for line in advice_lines:
            if line.strip():  # Only add non-empty lines
                insights.append(line)
        insights.append("")
    
    # Footer
    insights.append(f"{i18n.get_text('nutrition_analysis_date', user_language, date=datetime.now().strftime('%Y-%m-%d'))}")
    insights.append(f"{i18n.get_text('nutrition_credits_remaining', user_language, credits=user.get('credits_remaining', 0))}")
    
    # Join all insights and sanitize
    raw_text = "\n".join(insights)
    return sanitize_markdown_text(raw_text)


def get_goal_specific_advice(goal: str, profile: dict, language: str) -> str:
    """Get specific advice based on user's goal, fully localized"""
    if goal == 'lose_weight':
        return i18n.get_text("advice_lose_weight", language)
    elif goal == 'gain_weight':
        return i18n.get_text("advice_gain_weight", language)
    else:  # maintain_weight
        return i18n.get_text("advice_maintain_weight", language)


async def weekly_report_callback(callback: types.CallbackQuery):
    """Handle weekly report callback from button clicks"""
    try:
        # Answer callback to remove loading state
        await callback.answer()
        
        # Get user ID from callback, not from message
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Log weekly report action
        await log_user_action(
            user_id=user['id'],
            action_type="weekly_report",
            metadata={
                "username": callback.from_user.username,
                "has_profile": user_data['has_profile']
            }
        )
        
        # For now, show a placeholder - in future will analyze actual logs
        report_text = (
            f"{i18n.get_text('weekly_report_title', user_language)}\n\n"
            f"{i18n.get_text('weekly_report_week_of', user_language, date=datetime.now().strftime('%b %d, %Y'))}\n\n"
            f"{i18n.get_text('weekly_report_meals_analyzed', user_language, count=0)}\n"
            f"{i18n.get_text('weekly_report_avg_calories', user_language, calories='Not enough data')}\n"
            f"{i18n.get_text('weekly_report_goal_progress', user_language, progress='Set up profile to track')}\n"
            f"{i18n.get_text('weekly_report_consistency_score', user_language, score='N/A')}\n\n"
            f"{i18n.get_text('weekly_report_note', user_language)}\n\n"
            f"{i18n.get_text('weekly_report_coming_soon', user_language)}\n"
            f"{i18n.get_text('weekly_report_trends', user_language)}\n"
            f"{i18n.get_text('weekly_report_macro', user_language)}\n"
            f"{i18n.get_text('weekly_report_quality', user_language)}\n"
            f"{i18n.get_text('weekly_report_tracking', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await callback.message.answer(
            report_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in weekly_report_callback: {e}")
        # Get user's language for error message
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        await callback.message.answer(
            i18n.get_text("weekly_report_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def weekly_report_command(message: types.Message):
    """
    Generate weekly nutrition report for user
    """
    try:
        telegram_user_id = message.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # For now, show a placeholder - in future will analyze actual logs
        report_text = (
            f"{i18n.get_text('weekly_report_title', user_language)}\n\n"
            f"{i18n.get_text('weekly_report_week_of', user_language, date=datetime.now().strftime('%b %d, %Y'))}\n\n"
            f"{i18n.get_text('weekly_report_meals_analyzed', user_language, count=0)}\n"
            f"{i18n.get_text('weekly_report_avg_calories', user_language, calories='Not enough data')}\n"
            f"{i18n.get_text('weekly_report_goal_progress', user_language, progress='Set up profile to track')}\n"
            f"{i18n.get_text('weekly_report_consistency_score', user_language, score='N/A')}\n\n"
            f"{i18n.get_text('weekly_report_note', user_language)}\n\n"
            f"{i18n.get_text('weekly_report_coming_soon', user_language)}\n"
            f"{i18n.get_text('weekly_report_trends', user_language)}\n"
            f"{i18n.get_text('weekly_report_macro', user_language)}\n"
            f"{i18n.get_text('weekly_report_quality', user_language)}\n"
            f"{i18n.get_text('weekly_report_tracking', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(
            report_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in weekly_report_command: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        await message.answer(
            i18n.get_text("weekly_report_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def water_tracker_callback(callback: types.CallbackQuery):
    """Handle water tracker callback from button clicks"""
    try:
        # Answer callback to remove loading state
        await callback.answer()
        
        # Get user ID from callback, not from message
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Log water tracker action
        await log_user_action(
            user_id=user['id'],
            action_type="water_tracker",
            metadata={
                "username": callback.from_user.username,
                "has_profile": has_profile
            }
        )
        
        if not has_profile:
            water_text = (
                f"{i18n.get_text('water_tracker_title', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_setup_needed', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_guidelines', user_language)}\n"
                f"{i18n.get_text('water_tracker_glasses', user_language)}\n"
                f"{i18n.get_text('water_tracker_exercise', user_language)}\n"
                f"{i18n.get_text('water_tracker_urine', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_setup_profile', user_language)}"
            )
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text("btn_back", user_language),
                        callback_data="action_main_menu"
                    )
                ]
            ])
            
            await callback.message.answer(
                water_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        weight = profile.get('weight_kg', 70)
        activity = profile.get('activity_level', 'sedentary')
        
        water_data = calculate_water_needs(weight, activity)
        
        water_text = (
            f"{i18n.get_text('water_tracker_your_needs', user_language)}\n\n"
            f"{i18n.get_text('water_tracker_daily_target', user_language, liters=water_data['liters'])}\n"
            f"{i18n.get_text('water_tracker_glasses_count', user_language, glasses=water_data['glasses'])}\n\n"
            f"{i18n.get_text('water_tracker_breakdown', user_language)}\n"
            f"{i18n.get_text('water_tracker_base_need', user_language, base_ml=water_data['base_ml'])}\n"
            f"{i18n.get_text('water_tracker_activity_bonus', user_language, activity_bonus=water_data['activity_bonus'])}\n"
            f"{i18n.get_text('water_tracker_total', user_language, total_ml=water_data['total_ml'])}\n\n"
            f"{i18n.get_text('water_tracker_tips', user_language)}\n"
            f"{i18n.get_text('water_tracker_wake_up', user_language)}\n"
            f"{i18n.get_text('water_tracker_meals', user_language)}\n"
            f"{i18n.get_text('water_tracker_bottle', user_language)}\n"
            f"{i18n.get_text('water_tracker_reminders', user_language)}\n\n"
            f"{i18n.get_text('water_tracker_coming_soon', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await callback.message.answer(
            water_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in water_tracker_callback: {e}")
        # Get user's language for error message
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        await callback.message.answer(
            i18n.get_text("water_tracker_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def water_tracker_command(message: types.Message):
    """
    Show water tracking information and recommendations
    """
    try:
        telegram_user_id = message.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        if not has_profile:
            water_text = (
                f"{i18n.get_text('water_tracker_title', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_setup_needed', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_guidelines', user_language)}\n"
                f"{i18n.get_text('water_tracker_glasses', user_language)}\n"
                f"{i18n.get_text('water_tracker_exercise', user_language)}\n"
                f"{i18n.get_text('water_tracker_urine', user_language)}\n\n"
                f"{i18n.get_text('water_tracker_setup_profile', user_language)}"
            )
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text("btn_back", user_language),
                        callback_data="action_main_menu"
                    )
                ]
            ])
            
            await message.answer(
                water_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
        
        weight = profile.get('weight_kg', 70)
        activity = profile.get('activity_level', 'sedentary')
        
        water_data = calculate_water_needs(weight, activity)
        
        water_text = (
            f"{i18n.get_text('water_tracker_your_needs', user_language)}\n\n"
            f"{i18n.get_text('water_tracker_daily_target', user_language, liters=water_data['liters'])}\n"
            f"{i18n.get_text('water_tracker_glasses_count', user_language, glasses=water_data['glasses'])}\n\n"
            f"{i18n.get_text('water_tracker_breakdown', user_language)}\n"
            f"{i18n.get_text('water_tracker_base_need', user_language, base_ml=water_data['base_ml'])}\n"
            f"{i18n.get_text('water_tracker_activity_bonus', user_language, activity_bonus=water_data['activity_bonus'])}\n"
            f"{i18n.get_text('water_tracker_total', user_language, total_ml=water_data['total_ml'])}\n\n"
            f"{i18n.get_text('water_tracker_tips', user_language)}\n"
            f"{i18n.get_text('water_tracker_wake_up', user_language)}\n"
            f"{i18n.get_text('water_tracker_meals', user_language)}\n"
            f"{i18n.get_text('water_tracker_bottle', user_language)}\n"
            f"{i18n.get_text('water_tracker_reminders', user_language)}\n\n"
            f"{i18n.get_text('water_tracker_coming_soon', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(
            water_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in water_tracker_command: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        await message.answer(
            i18n.get_text("water_tracker_error", user_language),
            parse_mode="Markdown",
            reply_markup=keyboard
        )


async def show_nutrition_insights_menu(message_or_callback, user: dict, profile: dict):
    """Show nutrition insights menu with buttons for different sections"""
    user_language = user.get('language', 'en')
    
    menu_text = f"{i18n.get_text('nutrition_analysis_title', user_language)}\n\n{i18n.get_text('nutrition_menu_select_section', user_language)}"
    
    # Create keyboard with section buttons
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_bmi', user_language),
                callback_data="nutrition_section_bmi"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_ideal_weight', user_language),
                callback_data="nutrition_section_ideal_weight"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_metabolic_age', user_language),
                callback_data="nutrition_section_metabolic_age"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_water_needs', user_language),
                callback_data="nutrition_section_water_needs"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_macro_distribution', user_language),
                callback_data="nutrition_section_macro_distribution"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_meal_distribution', user_language),
                callback_data="nutrition_section_meal_distribution"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_recommendations', user_language),
                callback_data="nutrition_section_recommendations"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('nutrition_menu_goal_advice', user_language),
                callback_data="nutrition_section_goal_advice"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('btn_back', user_language),
                callback_data="action_main_menu"
            )
        ]
    ])
    
    if hasattr(message_or_callback, 'answer'):
        # It's a message
        await message_or_callback.answer(menu_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        # It's a callback
        await message_or_callback.message.answer(menu_text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_nutrition_section_callback(callback: types.CallbackQuery):
    """Handle nutrition section callbacks"""
    try:
        await callback.answer()
        
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        
        section = callback.data.replace("nutrition_section_", "")
        user_language = user.get('language', 'en')
        
        # Generate section content
        if section == "bmi":
            content = await generate_bmi_section(profile, user)
        elif section == "ideal_weight":
            content = await generate_ideal_weight_section(profile, user)
        elif section == "metabolic_age":
            content = await generate_metabolic_age_section(profile, user)
        elif section == "water_needs":
            content = await generate_water_needs_section(profile, user)
        elif section == "macro_distribution":
            content = await generate_macro_distribution_section(profile, user)
        elif section == "meal_distribution":
            content = await generate_meal_distribution_section(profile, user)
        elif section == "recommendations":
            content = await generate_recommendations_section(profile, user)
        elif section == "goal_advice":
            content = await generate_goal_advice_section(profile, user)
        else:
            await callback.message.answer(i18n.get_text("error_general", user_language))
            return
        
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_back', user_language),
                    callback_data="nutrition_menu"
                )
            ]
        ])
        
        await callback.message.answer(content, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in nutrition section callback: {e}")
        await callback.message.answer(i18n.get_text("nutrition_error", "en"))


async def handle_nutrition_menu_callback(callback: types.CallbackQuery):
    """Handle nutrition menu callback (back to menu)"""
    try:
        await callback.answer()
        
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        
        await show_nutrition_insights_menu(callback.message, user, profile)
        
    except Exception as e:
        logger.error(f"Error in nutrition menu callback: {e}")
        await callback.message.answer(i18n.get_text("nutrition_error", "en")) 