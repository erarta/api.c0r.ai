"""
Advanced nutrition analysis and insights for c0r.ai
Provides BMI, ideal weight, water needs, macro distribution, and recommendations
"""

from aiogram import types
from loguru import logger
from common.supabase_client import get_user_with_profile, log_user_action
from common.nutrition_calculations import (
    calculate_bmi, calculate_ideal_weight, calculate_water_needs,
    calculate_macro_distribution, calculate_metabolic_age,
    calculate_meal_portions, get_nutrition_recommendations
)
from .keyboards import create_main_menu_keyboard
from datetime import datetime, timedelta


async def nutrition_insights_command(message: types.Message):
    """
    Show comprehensive nutrition insights for the user
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
            await message.answer(
                "🔍 **Nutrition Insights**\n\n"
                f"Almost ready! Please complete your profile to get personalized analysis.\n\n"
                f"**Missing:** {', '.join(missing_fields)}\n\n"
                "Use /profile to complete your information.",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
            return
        
        # Generate comprehensive nutrition insights
        insights_text = await generate_nutrition_insights(profile, user)
        
        await message.answer(
            insights_text,
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in nutrition_insights_command: {e}")
        await message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error generating your nutrition insights.\n\n"
            "Please try again or contact support if the problem persists.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )


async def nutrition_insights_callback(callback: types.CallbackQuery):
    """Handle nutrition insights callback from button clicks"""
    try:
        # Answer callback to remove loading state
        await callback.answer()
        
        # Call the main insights function
        await nutrition_insights_command(callback.message)
        
    except Exception as e:
        logger.error(f"Error in nutrition_insights_callback: {e}")
        await callback.message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error generating your nutrition insights.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )


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
    
    # Header
    insights.append("🔬 **Your Nutrition Analysis**\n")
    
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
        bmi_data = calculate_bmi(weight, height)
        insights.append(f"📊 **Body Mass Index (BMI)**")
        insights.append(f"{bmi_data['emoji']} **{bmi_data['bmi']}** - {bmi_data['description']}")
        insights.append(f"💡 {bmi_data['motivation']}")
        insights.append("")
        
        # Ideal weight
        ideal_weight = calculate_ideal_weight(height, gender)
        insights.append(f"🎯 **Ideal Weight Range**")
        insights.append(f"**{ideal_weight['range']}** (BMI-based)")
        insights.append(f"**{ideal_weight['broca']} kg** (Broca formula)")
        insights.append("")
    
    # 2. Metabolic Age
    if age > 0 and weight > 0 and height > 0:
        metabolic_data = calculate_metabolic_age(age, gender, weight, height, activity)
        insights.append(f"🧬 **Metabolic Age**")
        insights.append(f"{metabolic_data['emoji']} **{metabolic_data['metabolic_age']} years** (vs {age} actual)")
        insights.append(f"{metabolic_data['description']}")
        insights.append(f"💡 {metabolic_data['motivation']}")
        insights.append("")
    
    # 3. Daily Water Needs
    if weight > 0:
        water_data = calculate_water_needs(weight, activity)
        insights.append(f"💧 **Daily Water Needs**")
        insights.append(f"**{water_data['liters']}L** ({water_data['glasses']} glasses)")
        insights.append(f"Base: {water_data['base_ml']}ml + Activity: {water_data['activity_bonus']}ml")
        insights.append("")
    
    # 4. Macro Distribution
    if daily_calories > 0:
        macro_data = calculate_macro_distribution(daily_calories, goal)
        insights.append(f"🥗 **Optimal Macro Distribution**")
        insights.append(f"**Protein:** {macro_data['protein']['grams']}g ({macro_data['protein']['percent']}%)")
        insights.append(f"**Carbs:** {macro_data['carbs']['grams']}g ({macro_data['carbs']['percent']}%)")
        insights.append(f"**Fats:** {macro_data['fat']['grams']}g ({macro_data['fat']['percent']}%)")
        insights.append("")
        
        # Meal portions
        meal_data = calculate_meal_portions(daily_calories, 3)
        insights.append(f"🍽️ **Meal Distribution**")
        for meal in meal_data['meal_breakdown']:
            insights.append(f"**{meal['name']}:** {meal['calories']} cal ({meal['percent']}%)")
        insights.append("")
    
    # 5. Personalized Recommendations
    recommendations = get_nutrition_recommendations(profile, [])
    if recommendations:
        insights.append(f"💡 **Personal Recommendations**")
        for rec in recommendations[:4]:  # Show top 4 recommendations
            insights.append(f"• {rec}")
        insights.append("")
    
    # 6. Goal-specific advice
    goal_advice = get_goal_specific_advice(goal, profile)
    if goal_advice:
        insights.append(f"🎯 **Goal-Specific Advice**")
        insights.append(goal_advice)
        insights.append("")
    
    # Footer
    insights.append(f"📅 **Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}")
    insights.append(f"🔄 **Credits Remaining:** {user.get('credits_remaining', 0)}")
    
    return "\n".join(insights)


def get_goal_specific_advice(goal: str, profile: dict) -> str:
    """Get specific advice based on user's goal"""
    
    if goal == 'lose_weight':
        return (
            "🎯 **Your Weight Loss Journey**:\n"
            "• 💪 Create a gentle calorie deficit (300-500 calories) - sustainable wins!\n"
            "• 🥩 Protein is your secret weapon for preserving muscle and feeling full\n"
            "• 🏋️‍♀️ Strength training 2-3x/week will boost your metabolism\n"
            "• 🧘‍♀️ Eat slowly and savor your food - your brain needs 20 minutes to register fullness"
        )
    
    elif goal == 'gain_weight':
        return (
            "🌱 **Your Healthy Weight Gain Plan**:\n"
            "• 🍽️ Gentle calorie surplus (300-500 calories) - steady progress is best!\n"
            "• 🥑 Healthy fats are your friend - nutrient-dense calories that fuel growth\n"
            "• ⏰ Frequent, enjoyable meals keep your energy steady all day\n"
            "• 💪 Resistance training transforms those calories into strong, healthy muscle"
        )
    
    else:  # maintain_weight
        return (
            "⚖️ **Your Maintenance Mastery**:\n"
            "• 🎯 You've found your sweet spot! Focus on consistent, joyful eating\n"
            "• 📊 Weekly check-ins help you stay in tune with your body\n"
            "• 🌈 Variety keeps nutrition exciting and ensures you get all nutrients\n"
            "• 🏃‍♀️ Mix cardio and strength training for total body wellness"
        )


async def weekly_report_callback(callback: types.CallbackQuery):
    """Handle weekly report callback from button clicks"""
    try:
        # Answer callback to remove loading state
        await callback.answer()
        
        # Get user ID from callback, not from message
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
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
        await callback.message.answer(
            "📊 **Weekly Report**\n\n"
            "📅 **Week of:** {}\n\n"
            "🍽️ **Meals Analyzed:** 0\n"
            "📈 **Average Calories:** Not enough data\n"
            "🎯 **Goal Progress:** Set up profile to track\n"
            "⭐ **Consistency Score:** N/A\n\n"
            "📝 **Note:** Start analyzing your meals to see detailed weekly insights!\n\n"
            "🔜 **Coming Soon:**\n"
            "• Detailed calorie trends\n"
            "• Macro balance analysis\n"
            "• Nutrition quality scoring\n"
            "• Goal progress tracking".format(datetime.now().strftime('%b %d, %Y')),
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in weekly_report_callback: {e}")
        await callback.message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error generating your weekly report.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )


async def weekly_report_command(message: types.Message):
    """
    Generate weekly nutrition report for user
    """
    try:
        telegram_user_id = message.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # For now, show a placeholder - in future will analyze actual logs
        await message.answer(
            "📊 **Weekly Report**\n\n"
            "📅 **Week of:** {}\n\n"
            "🍽️ **Meals Analyzed:** 0\n"
            "📈 **Average Calories:** Not enough data\n"
            "🎯 **Goal Progress:** Set up profile to track\n"
            "⭐ **Consistency Score:** N/A\n\n"
            "📝 **Note:** Start analyzing your meals to see detailed weekly insights!\n\n"
            "🔜 **Coming Soon:**\n"
            "• Detailed calorie trends\n"
            "• Macro balance analysis\n"
            "• Nutrition quality scoring\n"
            "• Goal progress tracking".format(datetime.now().strftime('%b %d, %Y')),
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in weekly_report_command: {e}")
        await message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error generating your weekly report.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
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
            await callback.message.answer(
                "💧 **Water Tracker**\n\n"
                "Set up your profile to get personalized water recommendations!\n\n"
                "💡 **General Guidelines:**\n"
                "• 8-10 glasses (2-2.5L) per day\n"
                "• More if you exercise or live in hot climate\n"
                "• Check urine color - should be light yellow\n\n"
                "Use /profile to set up your personal data.",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
            return
        
        weight = profile.get('weight_kg', 70)
        activity = profile.get('activity_level', 'sedentary')
        
        water_data = calculate_water_needs(weight, activity)
        
        await callback.message.answer(
            f"💧 **Your Water Needs**\n\n"
            f"🎯 **Daily Target:** {water_data['liters']}L\n"
            f"🥤 **In Glasses:** {water_data['glasses']} glasses (250ml each)\n\n"
            f"📊 **Breakdown:**\n"
            f"• Base need: {water_data['base_ml']}ml\n"
            f"• Activity bonus: +{water_data['activity_bonus']}ml\n"
            f"• Total: {water_data['total_ml']}ml\n\n"
            f"💡 **Tips:**\n"
            f"• Drink 1-2 glasses when you wake up\n"
            f"• Have water with each meal\n"
            f"• Keep a water bottle nearby\n"
            f"• Set reminders if you forget to drink\n\n"
            f"🔜 **Coming Soon:** Water intake logging and reminders!",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in water_tracker_callback: {e}")
        await callback.message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error with the water tracker.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
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
        
        if not has_profile:
            await message.answer(
                "💧 **Water Tracker**\n\n"
                "Set up your profile to get personalized water recommendations!\n\n"
                "💡 **General Guidelines:**\n"
                "• 8-10 glasses (2-2.5L) per day\n"
                "• More if you exercise or live in hot climate\n"
                "• Check urine color - should be light yellow\n\n"
                "Use /profile to set up your personal data.",
                parse_mode="Markdown",
                reply_markup=create_main_menu_keyboard()
            )
            return
        
        weight = profile.get('weight_kg', 70)
        activity = profile.get('activity_level', 'sedentary')
        
        water_data = calculate_water_needs(weight, activity)
        
        await message.answer(
            f"💧 **Your Water Needs**\n\n"
            f"🎯 **Daily Target:** {water_data['liters']}L\n"
            f"🥤 **In Glasses:** {water_data['glasses']} glasses (250ml each)\n\n"
            f"📊 **Breakdown:**\n"
            f"• Base need: {water_data['base_ml']}ml\n"
            f"• Activity bonus: +{water_data['activity_bonus']}ml\n"
            f"• Total: {water_data['total_ml']}ml\n\n"
            f"💡 **Tips:**\n"
            f"• Drink 1-2 glasses when you wake up\n"
            f"• Have water with each meal\n"
            f"• Keep a water bottle nearby\n"
            f"• Set reminders if you forget to drink\n\n"
            f"🔜 **Coming Soon:** Water intake logging and reminders!",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in water_tracker_command: {e}")
        await message.answer(
            "❌ **Error**\n\n"
            "Sorry, there was an error with the water tracker.",
            parse_mode="Markdown",
            reply_markup=create_main_menu_keyboard()
        ) 