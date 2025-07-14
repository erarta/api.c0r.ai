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
                text=i18n.get_text("daily_setup_btn", user_language),
                callback_data="profile_start_setup"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text("daily_analyze_btn", user_language),
                callback_data="action_analyze_info"
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
        recommendations = get_daily_recommendations(progress_percent, remaining, goal, daily_data['food_items_count'])
        
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
            f"{i18n.get_text('daily_activity', user_language)}\n"
            f"{i18n.get_text('daily_meals_analyzed', user_language, count=daily_data['food_items_count'])}\n\n"
            f"{i18n.get_text('daily_recommendations', user_language)}\n{recommendations}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text("daily_add_meal_btn", user_language),
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
        # Get user's language for error message
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language), reply_markup=create_main_menu_keyboard())

def get_daily_recommendations(progress_percent: int, remaining: int, goal: str, meals_count: int) -> str:
    """Generate personalized recommendations based on progress"""
    import random
    
    recommendations = []
    
    # Progress-based recommendations with variety
    if progress_percent < 30:
        if meals_count == 0:
            morning_tips = [
                "🍳 Start with a protein-rich breakfast to boost metabolism",
                "🥞 Try oatmeal with berries and nuts for sustained energy",
                "🥑 Avocado toast with eggs provides healthy fats and protein",
                "🥤 A protein smoothie is perfect for busy mornings",
                "🍌 Banana with peanut butter offers quick energy"
            ]
            recommendations.append(random.choice(morning_tips))
        else:
            early_day_tips = [
                "🥗 You have plenty of room for nutritious, satisfying meals",
                "🍽️ Focus on getting quality proteins and complex carbs",
                "🌈 Try to eat colorful vegetables with each meal",
                "🥜 Don't forget healthy fats like nuts and olive oil",
                "🐟 Consider fish or lean meats for protein"
            ]
            recommendations.append(random.choice(early_day_tips))
    
    elif progress_percent < 70:
        mid_day_tips = [
            "👍 Great progress! Keep up the balanced eating",
            "🎯 You're on track - maintain this steady pace",
            "⚖️ Perfect balance between nutrition and calories",
            "💪 Your body is getting the fuel it needs",
            "🔥 Keep this momentum going!"
        ]
        recommendations.append(random.choice(mid_day_tips))
        
        if remaining > 500:
            meal_suggestions = [
                "🍽️ You can fit in another substantial, nutritious meal",
                "🥘 Try a protein-rich dinner with vegetables",
                "🍲 A hearty soup or stew would be perfect",
                "🥙 Consider a wrap with lean protein and veggies",
                "🍝 Pasta with lean meat and vegetables is a good option"
            ]
            recommendations.append(random.choice(meal_suggestions))
    
    elif progress_percent < 100:
        approaching_tips = [
            "⚠️ Getting close to your target - choose lighter, nutrient-dense options",
            "🎨 Time for creative, low-calorie but satisfying choices",
            "🥗 Focus on volume with vegetables and lean proteins",
            "⏰ Consider the timing of your remaining calories",
            "🍃 Light but nutritious options will keep you satisfied"
        ]
        recommendations.append(random.choice(approaching_tips))
        
        if remaining > 200:
            light_meal_tips = [
                "🥗 Try a large salad with grilled chicken or fish",
                "🍲 Vegetable soup with lean protein works well",
                "🥒 Raw vegetables with hummus are filling and nutritious",
                "🐟 Grilled fish with steamed vegetables is perfect",
                "🥬 A lettuce wrap with turkey and avocado"
            ]
            recommendations.append(random.choice(light_meal_tips))
        else:
            snack_tips = [
                "🍎 Consider fruits or small, protein-rich snacks",
                "🥜 A handful of nuts or seeds is perfect",
                "🥛 Greek yogurt with berries is satisfying",
                "🥕 Carrot sticks with almond butter work great",
                "🍓 Fresh berries are low-calorie and nutritious"
            ]
            recommendations.append(random.choice(snack_tips))
    
    else:
        if goal == 'lose_weight':
            over_limit_tips = [
                "🛑 You've exceeded your weight loss target for today",
                "💧 Focus on hydration and light physical activity",
                "🚶‍♀️ A walk can help with digestion and mood",
                "🧘‍♀️ Consider meditation or light stretching",
                "💤 Ensure you get quality sleep tonight"
            ]
            recommendations.extend(random.sample(over_limit_tips, 2))
        elif goal == 'gain_weight':
            gain_success_tips = [
                "🎯 Excellent! You're meeting your calorie goals for muscle gain",
                "💪 Your body has the energy it needs to build muscle",
                "🏋️‍♂️ Perfect fuel for your workouts and recovery",
                "🌟 Consistency like this will lead to great results",
                "👏 Great job staying committed to your goals!"
            ]
            recommendations.append(random.choice(gain_success_tips))
        else:
            maintenance_tips = [
                "⚖️ You're over your maintenance calories for today",
                "🔄 Tomorrow is a fresh start - stay consistent",
                "💚 One day won't derail your progress",
                "🎯 Focus on balance over perfection",
                "⏰ Consider adjusting meal timing tomorrow"
            ]
            recommendations.append(random.choice(maintenance_tips))
    
    # Activity and tracking recommendations
    if meals_count == 0:
        tracking_tips = [
            "📱 Don't forget to log your meals for better tracking",
            "📊 Consistent logging helps you understand your patterns",
            "🎯 Tracking keeps you accountable to your goals",
            "💡 Use photos to make logging easier and more accurate"
        ]
        recommendations.append(random.choice(tracking_tips))
    elif meals_count >= 5:
        tracking_praise = [
            "📊 Outstanding job tracking your nutrition today!",
            "🏆 Your dedication to logging is impressive",
            "💪 This level of tracking will lead to great results",
            "🎉 You're building excellent healthy habits!"
        ]
        recommendations.append(random.choice(tracking_praise))
    
    # Add occasional motivational or educational tips
    if random.random() < 0.3:  # 30% chance
        bonus_tips = [
            "💧 Remember to drink plenty of water throughout the day",
            "🌅 Eating at regular intervals helps maintain energy",
            "🥗 Aim for at least 5 servings of fruits and vegetables daily",
            "😴 Quality sleep is just as important as nutrition",
            "🚶‍♂️ Light movement after meals aids digestion",
            "🧘‍♀️ Mindful eating helps with satisfaction and digestion",
            "🏃‍♀️ Regular exercise complements your nutrition goals"
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