"""
Daily plan handler for c0r.ai Telegram Bot
Shows daily calorie progress, nutrition summary, and recommendations
"""
from aiogram import types
from loguru import logger
from datetime import datetime, timedelta
from common.supabase_client import (
    get_user_with_profile, 
    get_daily_calories_consumed,
    log_user_action,
    get_or_create_user
)
from .keyboards import create_main_menu_keyboard
from .i18n import i18n

# /daily command handler
async def daily_command(message: types.Message):
    """Handle /daily command - show daily nutrition plan and progress"""
    try:
        telegram_user_id = message.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log daily command usage
        await log_user_action(
            user_id=user['id'],
            action_type="daily",
            metadata={
                "username": message.from_user.username,
                "has_profile": has_profile
            }
        )
        
        if not has_profile:
            # No profile - encourage setup
            await show_no_profile_message(message)
        else:
            # Show daily plan
            await show_daily_plan(message, user, profile)
            
    except Exception as e:
        logger.error(f"Error in /daily command for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language), reply_markup=create_main_menu_keyboard())

async def show_no_profile_message(message: types.Message):
    """Show message encouraging profile setup"""
    # Get user's language
    user = await get_or_create_user(message.from_user.id)
    user_language = user.get('language', 'en')
    
    no_profile_text = (
        f"{i18n.get_text('daily_title', user_language)}\n\n"
        f"{i18n.get_text('daily_no_profile', user_language)}\n\n"
        f"{i18n.get_text('daily_benefits', user_language)}\n\n"
        f"{i18n.get_text('daily_no_profile_continue', user_language)}"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("btn_back", user_language),
                callback_data="action_main_menu"
            )
        ]
    ])
    
    await message.answer(no_profile_text, parse_mode="Markdown", reply_markup=keyboard)

# Daily callback handler
async def daily_callback(callback: types.CallbackQuery):
    """Handle daily callback from button clicks"""
    try:
        telegram_user_id = callback.from_user.id
        
        # Answer callback to remove loading state
        await callback.answer()
        
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log daily action
        await log_user_action(
            user_id=user['id'],
            action_type="daily",
            metadata={
                "username": callback.from_user.username,
                "has_profile": has_profile
            }
        )
        
        if not has_profile:
            # No profile - encourage setup
            await show_no_profile_message(callback.message)
        else:
            # Show daily plan
            await show_daily_plan(callback.message, user, profile)
            
    except Exception as e:
        logger.error(f"Error in daily callback for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await callback.message.answer(i18n.get_text("error_general", user_language), reply_markup=create_main_menu_keyboard())

async def show_daily_plan(message: types.Message, user: dict, profile: dict):
    """Show comprehensive daily plan for user with profile"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = await get_daily_calories_consumed(user['id'], today)
        
        # Get profile data
        daily_target = profile.get('daily_calories_target', 0)
        goal = profile.get('goal', 'maintain_weight')
        
        # Calculate progress
        consumed_today = daily_data['total_calories']
        remaining = max(0, daily_target - consumed_today) if daily_target else 0
        progress_percent = min(100, int((consumed_today / daily_target) * 100)) if daily_target else 0
        
        # Create progress bar
        progress_bar = "▓" * (progress_percent // 10) + "░" * (10 - progress_percent // 10)
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Format goal message
        goal_messages = {
            'lose_weight': i18n.get_text('daily_goal_lose', user_language),
            'maintain_weight': i18n.get_text('daily_goal_maintain', user_language),
            'gain_weight': i18n.get_text('daily_goal_gain', user_language)
        }
        goal_message = goal_messages.get(goal, i18n.get_text('daily_goal_custom', user_language))
        
        # Format macros
        protein = daily_data['total_protein']
        fats = daily_data['total_fats']
        carbs = daily_data['total_carbs']
        
        # Calculate recommended macros (rough estimates)
        if daily_target > 0:
            protein_target = int(daily_target * 0.25 / 4)  # 25% calories from protein
            fat_target = int(daily_target * 0.30 / 9)      # 30% calories from fat  
            carb_target = int(daily_target * 0.45 / 4)     # 45% calories from carbs
            
            # Determine status for each macro
            protein_status = i18n.get_text('daily_status_good', user_language) if protein >= protein_target * 0.8 else i18n.get_text('daily_status_low', user_language)
            fat_status = i18n.get_text('daily_status_good', user_language) if fats >= fat_target * 0.8 else i18n.get_text('daily_status_low', user_language)
            carb_status = i18n.get_text('daily_status_good', user_language) if carbs >= carb_target * 0.8 else i18n.get_text('daily_status_low', user_language)
            
            macro_progress = (
                f"{i18n.get_text('daily_protein', user_language, current=protein, target=protein_target, status=protein_status)}\n"
                f"{i18n.get_text('daily_fats', user_language, current=fats, target=fat_target, status=fat_status)}\n"
                f"{i18n.get_text('daily_carbs', user_language, current=carbs, target=carb_target, status=carb_status)}\n"
            )
        else:
            macro_progress = (
                f"{i18n.get_text('daily_protein', user_language, current=protein, target='-', status='')}\n"
                f"{i18n.get_text('daily_fats', user_language, current=fats, target='-', status='')}\n"
                f"{i18n.get_text('daily_carbs', user_language, current=carbs, target='-', status='')}\n"
            )
        
        # Status message
        if progress_percent < 70:
            status_emoji = "🟢"
            status_msg = i18n.get_text('daily_status_on_track', user_language)
        elif progress_percent < 90:
            status_emoji = "🟡"
            status_msg = i18n.get_text('daily_status_close', user_language)
        elif progress_percent < 110:
            status_emoji = "🟠"
            status_msg = i18n.get_text('daily_status_limit', user_language)
        else:
            status_emoji = "🔴"
            status_msg = i18n.get_text('daily_status_over', user_language)
        
        # Get recommendations
        recommendations = get_daily_recommendations(progress_percent, remaining, goal, daily_data['food_items_count'], user_language)
        
        plan_text = (
            f"{i18n.get_text('daily_plan_title', user_language, date=today)}\n\n"
            f"{goal_message}\n\n"
            f"{i18n.get_text('daily_calorie_progress', user_language)}\n"
            f"{i18n.get_text('daily_target', user_language, target=daily_target)}\n"
            f"{i18n.get_text('daily_consumed', user_language, consumed=consumed_today)}\n"
            f"{i18n.get_text('daily_remaining', user_language, remaining=remaining)}\n\n"
            f"{i18n.get_text('daily_progress', user_language, progress_bar=progress_bar, percent=progress_percent)}\n"
            f"{status_emoji} {status_msg}\n\n"
            f"{i18n.get_text('daily_nutrition_breakdown', user_language)}\n"
            f"{macro_progress}\n"
            f"💡 {i18n.get_text('daily_status_explanation', user_language)}\n\n"
            f"{i18n.get_text('daily_activity', user_language)}\n"
            f"{i18n.get_text('daily_meals_analyzed', user_language, count=daily_data['food_items_count'])}\n\n"
            f"{i18n.get_text('daily_recommendations', user_language)}\n{recommendations}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(plan_text, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing daily plan: {e}")
        # Get user's language for error message
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language), reply_markup=create_main_menu_keyboard())

def get_daily_recommendations(progress_percent: int, remaining: int, goal: str, meals_count: int, language: str) -> str:
    """Generate personalized recommendations based on progress, fully localized"""
    import random
    from .i18n import i18n
    recommendations = []

    # Progress-based recommendations with variety
    if progress_percent < 30:
        if meals_count == 0:
            morning_tips = [
                i18n.get_text("rec_morning_1", language),
                i18n.get_text("rec_morning_2", language),
                i18n.get_text("rec_morning_3", language),
                i18n.get_text("rec_morning_4", language),
                i18n.get_text("rec_morning_5", language),
            ]
            recommendations.append(random.choice(morning_tips))
        else:
            early_day_tips = [
                i18n.get_text("rec_early_1", language),
                i18n.get_text("rec_early_2", language),
                i18n.get_text("rec_early_3", language),
                i18n.get_text("rec_early_4", language),
                i18n.get_text("rec_early_5", language),
            ]
            recommendations.append(random.choice(early_day_tips))

    elif progress_percent < 70:
        mid_day_tips = [
            i18n.get_text("rec_mid_1", language),
            i18n.get_text("rec_mid_2", language),
            i18n.get_text("rec_mid_3", language),
            i18n.get_text("rec_mid_4", language),
            i18n.get_text("rec_mid_5", language),
        ]
        recommendations.append(random.choice(mid_day_tips))

        if remaining > 500:
            meal_suggestions = [
                i18n.get_text("rec_meal_1", language),
                i18n.get_text("rec_meal_2", language),
                i18n.get_text("rec_meal_3", language),
                i18n.get_text("rec_meal_4", language),
                i18n.get_text("rec_meal_5", language),
            ]
            recommendations.append(random.choice(meal_suggestions))

    elif progress_percent < 100:
        approaching_tips = [
            i18n.get_text("rec_approach_1", language),
            i18n.get_text("rec_approach_2", language),
            i18n.get_text("rec_approach_3", language),
            i18n.get_text("rec_approach_4", language),
            i18n.get_text("rec_approach_5", language),
        ]
        recommendations.append(random.choice(approaching_tips))

        if remaining > 200:
            light_meal_tips = [
                i18n.get_text("rec_light_1", language),
                i18n.get_text("rec_light_2", language),
                i18n.get_text("rec_light_3", language),
                i18n.get_text("rec_light_4", language),
                i18n.get_text("rec_light_5", language),
            ]
            recommendations.append(random.choice(light_meal_tips))
        else:
            snack_tips = [
                i18n.get_text("rec_snack_1", language),
                i18n.get_text("rec_snack_2", language),
                i18n.get_text("rec_snack_3", language),
                i18n.get_text("rec_snack_4", language),
                i18n.get_text("rec_snack_5", language),
            ]
            recommendations.append(random.choice(snack_tips))

    else:
        if goal == 'lose_weight':
            over_limit_tips = [
                i18n.get_text("rec_over_lose_1", language),
                i18n.get_text("rec_over_lose_2", language),
                i18n.get_text("rec_over_lose_3", language),
                i18n.get_text("rec_over_lose_4", language),
                i18n.get_text("rec_over_lose_5", language),
            ]
            recommendations.extend(random.sample(over_limit_tips, 2))
        elif goal == 'gain_weight':
            gain_success_tips = [
                i18n.get_text("rec_over_gain_1", language),
                i18n.get_text("rec_over_gain_2", language),
                i18n.get_text("rec_over_gain_3", language),
                i18n.get_text("rec_over_gain_4", language),
                i18n.get_text("rec_over_gain_5", language),
            ]
            recommendations.append(random.choice(gain_success_tips))
        else:
            maintenance_tips = [
                i18n.get_text("rec_over_maintain_1", language),
                i18n.get_text("rec_over_maintain_2", language),
                i18n.get_text("rec_over_maintain_3", language),
                i18n.get_text("rec_over_maintain_4", language),
                i18n.get_text("rec_over_maintain_5", language),
            ]
            recommendations.append(random.choice(maintenance_tips))

    # Activity and tracking recommendations
    if meals_count == 0:
        tracking_tips = [
            i18n.get_text("rec_track_1", language),
            i18n.get_text("rec_track_2", language),
            i18n.get_text("rec_track_3", language),
            i18n.get_text("rec_track_4", language),
        ]
        recommendations.append(random.choice(tracking_tips))
    elif meals_count >= 5:
        tracking_praise = [
            i18n.get_text("rec_track_praise_1", language),
            i18n.get_text("rec_track_praise_2", language),
            i18n.get_text("rec_track_praise_3", language),
            i18n.get_text("rec_track_praise_4", language),
        ]
        recommendations.append(random.choice(tracking_praise))

    # Add occasional motivational or educational tips
    if random.random() < 0.3:  # 30% chance
        bonus_tips = [
            i18n.get_text("rec_bonus_1", language),
            i18n.get_text("rec_bonus_2", language),
            i18n.get_text("rec_bonus_3", language),
            i18n.get_text("rec_bonus_4", language),
            i18n.get_text("rec_bonus_5", language),
            i18n.get_text("rec_bonus_6", language),
            i18n.get_text("rec_bonus_7", language),
        ]
        recommendations.append(random.choice(bonus_tips))

    return "\n".join(f"• {rec}" for rec in recommendations)

# Daily callback handlers
async def handle_daily_callback(callback: types.CallbackQuery):
    """Handle daily plan related callbacks"""
    try:
        telegram_user_id = callback.from_user.id
        action = callback.data
        
        # Answer callback to remove loading state
        await callback.answer()
        
        if action == "daily_weekly":
            await show_weekly_progress(callback.message, telegram_user_id)
        elif action == "daily_history":
            await show_meal_history(callback.message, telegram_user_id)
        
    except Exception as e:
        logger.error(f"Error in daily callback: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await callback.answer(i18n.get_text("error_general", user_language))

async def show_weekly_progress(message: types.Message, telegram_user_id: int):
    """Show weekly progress summary"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Get data for last 7 days
        weekly_data = []
        total_calories_week = 0
        total_days_tracked = 0
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_data = await get_daily_calories_consumed(user['id'], date)
            
            if daily_data['food_items_count'] > 0:
                total_days_tracked += 1
                total_calories_week += daily_data['total_calories']
            
            weekly_data.append({
                'date': date,
                'calories': daily_data['total_calories'],
                'meals': daily_data['food_items_count']
            })
        
        # Calculate averages
        avg_calories = int(total_calories_week / total_days_tracked) if total_days_tracked > 0 else 0
        daily_target = profile.get('daily_calories_target', 0) if profile else 0
        
        # Format weekly summary
        weekly_text = (
            f"{i18n.get_text('weekly_progress_title', user_language)}\n\n"
            f"{i18n.get_text('weekly_progress_last_7_days', user_language)}\n"
            f"{i18n.get_text('weekly_progress_days_tracked', user_language, tracked=total_days_tracked)}\n"
            f"{i18n.get_text('weekly_progress_avg_calories', user_language, calories=avg_calories)}\n"
        )
        
        if daily_target > 0:
            avg_vs_target = int((avg_calories / daily_target) * 100)
            weekly_text += f"{i18n.get_text('weekly_progress_target_adherence', user_language, percent=avg_vs_target)}\n"
        
        weekly_text += f"\n{i18n.get_text('weekly_progress_daily_breakdown', user_language)}\n"
        
        for day_data in weekly_data:
            date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            
            if day_data['meals'] > 0:
                weekly_text += f"{i18n.get_text('weekly_progress_day_with_meals', user_language, day=day_name, calories=day_data['calories'], meals=day_data['meals'])}\n"
            else:
                weekly_text += f"{i18n.get_text('weekly_progress_day_no_data', user_language, day=day_name)}\n"
        
        weekly_text += (
            f"\n{i18n.get_text('weekly_progress_keep_tracking', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(weekly_text, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing weekly progress: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def show_meal_history(message: types.Message, telegram_user_id: int):
    """Show recent meal history"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = await get_daily_calories_consumed(user['id'], today)
        
        if daily_data['food_items_count'] == 0:
            await message.answer(
                f"{i18n.get_text('meal_history_no_meals', user_language)}\n\n"
                f"{i18n.get_text('meal_history_no_meals_tip', user_language)}",
                parse_mode="Markdown"
            )
            return
        
        history_text = f"{i18n.get_text('meal_history_title', user_language, date=today)}\n\n"
        
        for i, item in enumerate(daily_data['food_items'], 1):
            # Format timestamp
            timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%H:%M')
            
            history_text += (
                f"{i18n.get_text('meal_history_item_format', user_language, number=i, time=time_str, calories=item['calories'], protein=item['protein'], fats=item['fats'], carbs=item['carbs'])}\n\n"
            )
        
        history_text += (
            f"{i18n.get_text('meal_history_total_title', user_language)}\n"
            f"{i18n.get_text('meal_history_total_calories', user_language, calories=daily_data['total_calories'])}\n"
            f"{i18n.get_text('meal_history_total_protein', user_language, protein=daily_data['total_protein'])}\n"
            f"{i18n.get_text('meal_history_total_fats', user_language, fats=daily_data['total_fats'])}\n"
            f"{i18n.get_text('meal_history_total_carbs', user_language, carbs=daily_data['total_carbs'])}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", user_language),
                    callback_data="action_main_menu"
                )
            ]
        ])
        
        await message.answer(history_text, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing meal history: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language)) 