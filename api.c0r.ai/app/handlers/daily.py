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
    log_user_action
)
from .commands import create_main_menu_keyboard

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
        await message.answer("❌ An error occurred. Please try again later.", reply_markup=create_main_menu_keyboard())

async def show_no_profile_message(message: types.Message):
    """Show message encouraging profile setup"""
    no_profile_text = (
        f"📊 **Daily Plan**\n\n"
        f"🎯 To show your personalized daily nutrition plan, I need your profile information.\n\n"
        f"💡 **With a profile, you'll see:**\n"
        f"• Daily calorie target based on your goals\n"
        f"• Real-time progress tracking\n"
        f"• Nutritional balance recommendations\n"
        f"• Meal planning suggestions\n\n"
        f"📸 You can still analyze food photos without a profile!"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="👤 Set Up Profile",
                callback_data="profile_start_setup"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="📸 Analyze Food",
                callback_data="action_analyze_info"
            )
        ]
    ])
    
    await message.answer(no_profile_text, parse_mode="Markdown", reply_markup=keyboard)

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
        
        # Format goal message
        goal_messages = {
            'lose_weight': '📉 **Goal:** Lose weight (15% calorie deficit)',
            'maintain_weight': '⚖️ **Goal:** Maintain weight',
            'gain_weight': '📈 **Goal:** Gain weight (15% calorie surplus)'
        }
        goal_message = goal_messages.get(goal, '🎯 **Goal:** Custom plan')
        
        # Format macros
        protein = daily_data['total_protein']
        fats = daily_data['total_fats']
        carbs = daily_data['total_carbs']
        
        # Calculate recommended macros (rough estimates)
        if daily_target > 0:
            protein_target = int(daily_target * 0.25 / 4)  # 25% calories from protein
            fat_target = int(daily_target * 0.30 / 9)      # 30% calories from fat  
            carb_target = int(daily_target * 0.45 / 4)     # 45% calories from carbs
            
            macro_progress = (
                f"🥩 **Protein:** {protein}g / {protein_target}g "
                f"({'✅' if protein >= protein_target * 0.8 else '⚠️'})\n"
                f"🥑 **Fats:** {fats}g / {fat_target}g "
                f"({'✅' if fats >= fat_target * 0.8 else '⚠️'})\n"
                f"🍞 **Carbs:** {carbs}g / {carb_target}g "
                f"({'✅' if carbs >= carb_target * 0.8 else '⚠️'})\n"
            )
        else:
            macro_progress = (
                f"🥩 **Protein:** {protein}g\n"
                f"🥑 **Fats:** {fats}g\n"
                f"🍞 **Carbs:** {carbs}g\n"
            )
        
        # Status message
        if progress_percent < 70:
            status_emoji = "🟢"
            status_msg = "You're on track!"
        elif progress_percent < 90:
            status_emoji = "🟡"
            status_msg = "Getting close to your target"
        elif progress_percent < 110:
            status_emoji = "🟠"
            status_msg = "Almost at your limit"
        else:
            status_emoji = "🔴"
            status_msg = "Over your daily target"
        
        # Get recommendations
        recommendations = get_daily_recommendations(progress_percent, remaining, goal, daily_data['food_items_count'])
        
        plan_text = (
            f"📊 **Your Daily Plan** - {today}\n\n"
            f"{goal_message}\n\n"
            f"🔥 **Calorie Progress:**\n"
            f"Target: {daily_target:,} calories\n"
            f"Consumed: {consumed_today:,} calories\n"
            f"Remaining: {remaining:,} calories\n\n"
            f"📈 **Progress:** {progress_bar} {progress_percent}%\n"
            f"{status_emoji} {status_msg}\n\n"
            f"🍽️ **Nutrition Breakdown:**\n"
            f"{macro_progress}\n"
            f"📱 **Today's Activity:**\n"
            f"🍎 Meals analyzed: {daily_data['food_items_count']}\n\n"
            f"💡 **Recommendations:**\n{recommendations}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📸 Add Meal",
                    callback_data="action_analyze_info"
                ),
                types.InlineKeyboardButton(
                    text="📈 Weekly Progress",
                    callback_data="daily_weekly"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="👤 Edit Profile",
                    callback_data="profile_edit"
                ),
                types.InlineKeyboardButton(
                    text="🍽️ Meal History",
                    callback_data="daily_history"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="profile_main_menu"
                )
            ]
        ])
        
        await message.answer(plan_text, parse_mode="Markdown", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing daily plan: {e}")
        await message.answer("❌ An error occurred while loading your daily plan.", reply_markup=create_main_menu_keyboard())

def get_daily_recommendations(progress_percent: int, remaining: int, goal: str, meals_count: int) -> str:
    """Generate personalized recommendations based on progress"""
    recommendations = []
    
    if progress_percent < 30:
        if meals_count == 0:
            recommendations.append("🍳 Start with a healthy breakfast!")
        else:
            recommendations.append("🥗 You have plenty of room for nutritious meals")
    elif progress_percent < 70:
        recommendations.append("👍 Good progress! Keep eating balanced meals")
        if remaining > 500:
            recommendations.append("🍽️ You can fit in another substantial meal")
    elif progress_percent < 100:
        recommendations.append("⚠️ Getting close to your target - choose lighter options")
        if remaining > 200:
            recommendations.append("🥗 Try a salad or vegetable-based meal")
        else:
            recommendations.append("🍎 Consider fruits or small snacks")
    else:
        if goal == 'lose_weight':
            recommendations.append("🛑 You've exceeded your weight loss target")
            recommendations.append("💧 Focus on hydration and light activity")
        elif goal == 'gain_weight':
            recommendations.append("🎯 Great! You're meeting your calorie goals")
        else:
            recommendations.append("⚖️ You're over your maintenance calories")
    
    # Activity-based recommendations
    if meals_count == 0:
        recommendations.append("📱 Don't forget to log your meals for better tracking")
    elif meals_count >= 5:
        recommendations.append("📊 Great job tracking your nutrition!")
    
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
        await callback.answer("❌ An error occurred. Please try again later.")

async def show_weekly_progress(message: types.Message, telegram_user_id: int):
    """Show weekly progress summary"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        
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
            f"📈 **Weekly Progress Summary**\n\n"
            f"📅 **Last 7 Days:**\n"
            f"🍽️ Days tracked: {total_days_tracked}/7\n"
            f"📊 Average calories: {avg_calories:,}/day\n"
        )
        
        if daily_target > 0:
            avg_vs_target = int((avg_calories / daily_target) * 100)
            weekly_text += f"🎯 Target adherence: {avg_vs_target}%\n"
        
        weekly_text += "\n📊 **Daily Breakdown:**\n"
        
        for day_data in weekly_data:
            date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            
            if day_data['meals'] > 0:
                weekly_text += f"• {day_name}: {day_data['calories']:,} cal ({day_data['meals']} meals)\n"
            else:
                weekly_text += f"• {day_name}: No data\n"
        
        weekly_text += (
            f"\n💡 **Keep tracking consistently for better insights!**"
        )
        
        await message.answer(weekly_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing weekly progress: {e}")
        await message.answer("❌ An error occurred while loading weekly data.")

async def show_meal_history(message: types.Message, telegram_user_id: int):
    """Show recent meal history"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = await get_daily_calories_consumed(user['id'], today)
        
        if daily_data['food_items_count'] == 0:
            await message.answer(
                f"📱 **No meals logged today**\n\n"
                f"📸 Send me a food photo to start tracking your nutrition!",
                parse_mode="Markdown"
            )
            return
        
        history_text = f"🍽️ **Today's Meals** ({today})\n\n"
        
        for i, item in enumerate(daily_data['food_items'], 1):
            # Format timestamp
            timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%H:%M')
            
            history_text += (
                f"**{i}. {time_str}**\n"
                f"🔥 {item['calories']} cal | "
                f"🥩 {item['protein']}g | "
                f"🥑 {item['fats']}g | "
                f"🍞 {item['carbs']}g\n\n"
            )
        
        history_text += (
            f"📊 **Total Today:**\n"
            f"🔥 {daily_data['total_calories']} calories\n"
            f"🥩 {daily_data['total_protein']}g protein\n"
            f"🥑 {daily_data['total_fats']}g fats\n"
            f"🍞 {daily_data['total_carbs']}g carbs"
        )
        
        await message.answer(history_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing meal history: {e}")
        await message.answer("❌ An error occurred while loading meal history.") 