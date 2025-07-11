"""
Profile management handlers for c0r.ai Telegram Bot
Handles user profile setup, editing, and daily calorie calculation
"""
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from common.supabase_client import (
    get_user_with_profile, 
    create_or_update_profile, 
    log_user_action,
    calculate_daily_calories
)

# FSM States for profile setup
class ProfileStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_activity = State()
    waiting_for_goal = State()

# /profile command handler
async def profile_command(message: types.Message, state: FSMContext):
    """Handle /profile command - show profile menu"""
    try:
        telegram_user_id = message.from_user.id
        
        # Clear any existing FSM state to start fresh
        await state.clear()
        
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        profile = user_data['profile']
        has_profile = user_data['has_profile']
        
        # Log profile command usage
        await log_user_action(
            user_id=user['id'],
            action_type="profile",
            metadata={
                "username": message.from_user.username,
                "has_profile": has_profile,
                "action": "view_menu"
            }
        )
        
        if has_profile:
            # Show existing profile
            await show_profile_menu(message, user, profile)
        else:
            # Show setup prompt
            await show_profile_setup_prompt(message, user)
            
    except Exception as e:
        logger.error(f"Error in /profile command for user {telegram_user_id}: {e}")
        await message.answer("❌ An error occurred. Please try again later.")

async def show_profile_menu(message: types.Message, user: dict, profile: dict):
    """Show profile menu for existing profile"""
    # Format profile data
    age = profile.get('age', 'Not set')
    gender = "👨 Male" if profile.get('gender') == 'male' else "👩 Female" if profile.get('gender') == 'female' else 'Not set'
    height = f"{profile.get('height_cm', 'Not set')} cm" if profile.get('height_cm') else 'Not set'
    weight = f"{profile.get('weight_kg', 'Not set')} kg" if profile.get('weight_kg') else 'Not set'
    
    activity_labels = {
        'sedentary': '😴 Sedentary (little/no exercise)',
        'lightly_active': '🚶 Lightly active (light exercise 1-3 days/week)',
        'moderately_active': '🏃 Moderately active (moderate exercise 3-5 days/week)',
        'very_active': '💪 Very active (hard exercise 6-7 days/week)',
        'extremely_active': '🏋️ Extremely active (very hard exercise, physical job)'
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
        f"🔥 **Daily Calorie Target:** {daily_calories}\n\n"
        f"What would you like to do?"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="✏️ Edit Profile",
                callback_data="profile_edit"
            ),
            types.InlineKeyboardButton(
                text="🔄 Recalculate Calories",
                callback_data="profile_recalculate"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="📊 Daily Plan",
                callback_data="action_daily"
            ),
            types.InlineKeyboardButton(
                text="📈 Progress",
                callback_data="profile_progress"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🏠 Main Menu",
                callback_data="profile_main_menu"
            )
        ]
    ])
    
    await message.answer(profile_text, parse_mode="Markdown", reply_markup=keyboard)

async def show_profile_setup_prompt(message: types.Message, user: dict):
    """Show profile setup prompt for new users"""
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
                text="🚀 Start Profile Setup",
                callback_data="profile_start_setup"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="⏭️ Skip for Now",
                callback_data="profile_skip"
            )
        ]
    ])
    
    await message.answer(setup_text, parse_mode="Markdown", reply_markup=keyboard)

# Profile callback handlers
async def handle_profile_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile-related callbacks"""
    try:
        telegram_user_id = callback.from_user.id
        action = callback.data
        
        # Answer callback to remove loading state
        await callback.answer()
        
        if action == "profile_start_setup":
            await start_profile_setup(callback.message, state, telegram_user_id)
        elif action == "profile_edit":
            await start_profile_edit(callback.message, state, telegram_user_id)
        elif action == "profile_recalculate":
            await recalculate_calories(callback.message, telegram_user_id)
        elif action == "profile_skip":
            await profile_skip(callback.message, telegram_user_id)
        elif action == "profile_main_menu":
            await profile_main_menu(callback.message, telegram_user_id)
        elif action == "profile_progress":
            await show_progress(callback.message, telegram_user_id)
        
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")
        await callback.answer("❌ An error occurred. Please try again later.")

async def start_profile_setup(message: types.Message, state: FSMContext, telegram_user_id: int):
    """Start profile setup process"""
    # Clear any existing state
    await state.clear()
    await state.set_state(ProfileStates.waiting_for_age)
    
    await message.answer(
        f"👶 **Step 1/6: Your Age**\n\n"
        f"Please enter your age in years (e.g., 25):\n\n"
        f"💡 *Tip: Use /profile to restart setup anytime*",
        parse_mode="Markdown"
    )

async def start_profile_edit(message: types.Message, state: FSMContext, telegram_user_id: int):
    """Start profile editing process"""
    # For editing, we'll use the same setup flow
    await start_profile_setup(message, state, telegram_user_id)

async def recalculate_calories(message: types.Message, telegram_user_id: int):
    """Recalculate daily calories for existing profile"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        profile = user_data['profile']
        
        if not profile:
            await message.answer("❌ No profile found. Please set up your profile first.")
            return
        
        # Check if all required data is present
        required_fields = ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']
        if not all(profile.get(field) for field in required_fields):
            await message.answer(
                "❌ **Profile incomplete**\n\n"
                "Some required information is missing. Please edit your profile to add all details.",
                parse_mode="Markdown"
            )
            return
        
        # Recalculate calories
        new_calories = calculate_daily_calories(profile)
        
        # Update profile with new calorie target
        await create_or_update_profile(user_data['user']['id'], {
            'daily_calories_target': new_calories
        })
        
        await message.answer(
            f"🔄 **Calories Recalculated!**\n\n"
            f"🔥 **New Daily Target:** {new_calories:,} calories\n\n"
            f"Based on your current profile settings.",
            parse_mode="Markdown"
        )
        
        logger.info(f"Recalculated calories for user {telegram_user_id}: {new_calories}")
        
    except Exception as e:
        logger.error(f"Error recalculating calories for user {telegram_user_id}: {e}")
        await message.answer("❌ An error occurred while recalculating. Please try again.")

async def profile_skip(message: types.Message, telegram_user_id: int):
    """Handle profile setup skip"""
    await message.answer(
        f"⏭️ **Profile setup skipped**\n\n"
        f"You can set up your profile anytime using the /profile command.\n\n"
        f"💡 **Benefits of setting up a profile:**\n"
        f"• Personalized daily calorie targets\n"
        f"• Progress tracking\n"
        f"• Better nutrition recommendations\n\n"
        f"📸 You can still analyze food photos without a profile!",
        parse_mode="Markdown"
    )

async def profile_main_menu(message: types.Message, telegram_user_id: int):
    """Return to main menu"""
    from .commands import start_command
    await start_command(message)

async def show_progress(message: types.Message, telegram_user_id: int):
    """Show user progress and statistics"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        
        # Get daily calories data
        from common.supabase_client import get_daily_calories_consumed
        from datetime import datetime
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = await get_daily_calories_consumed(user_data['user']['id'], today)
        
        progress_text = (
            f"📈 **Your Progress**\n\n"
            f"📅 **Today ({today}):**\n"
            f"🍽️ Meals analyzed: {daily_data['food_items_count']}\n"
            f"🔥 Calories consumed: {daily_data['total_calories']:,}\n"
            f"🥩 Protein: {daily_data['total_protein']}g\n"
            f"🥑 Fats: {daily_data['total_fats']}g\n"
            f"🍞 Carbs: {daily_data['total_carbs']}g\n\n"
        )
        
        if user_data['has_profile'] and user_data['profile'].get('daily_calories_target'):
            target = user_data['profile']['daily_calories_target']
            remaining = max(0, target - daily_data['total_calories'])
            progress_percent = min(100, int((daily_data['total_calories'] / target) * 100))
            
            progress_bar = "▓" * (progress_percent // 10) + "░" * (10 - progress_percent // 10)
            
            progress_text += (
                f"🎯 **Daily Goal Progress:**\n"
                f"Target: {target:,} calories\n"
                f"Remaining: {remaining:,} calories\n\n"
                f"Progress: {progress_bar} {progress_percent}%"
            )
        else:
            progress_text += "💡 Set up your profile to see daily goal progress!"
        
        await message.answer(progress_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing progress for user {telegram_user_id}: {e}")
        await message.answer("❌ An error occurred while loading progress.")

# FSM handlers for profile setup steps
async def process_age(message: types.Message, state: FSMContext):
    """Process age input"""
    try:
        age = int(message.text.strip())
        if age < 10 or age > 120:
            await message.answer(
                "❌ **Invalid age**\n\n"
                "Please enter an age between 10 and 120 years:",
                parse_mode="Markdown"
            )
            return
        
        # Store age in FSM data
        await state.update_data(age=age)
        
        # Move to next step - gender
        await state.set_state(ProfileStates.waiting_for_gender)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="👨 Male", callback_data="gender_male"),
                types.InlineKeyboardButton(text="👩 Female", callback_data="gender_female")
            ]
        ])
        
        await message.answer(
            f"✅ Age: {age} years\n\n"
            f"👤 **Step 2/6: Your Gender**\n\n"
            f"Please select your gender:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except ValueError:
        await message.answer(
            "❌ **Invalid input**\n\n"
            "Please enter your age as a number (e.g., 25):",
            parse_mode="Markdown"
        )

async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    """Process gender selection"""
    gender = "male" if callback.data == "gender_male" else "female"
    gender_label = "👨 Male" if gender == "male" else "👩 Female"
    
    # Store gender in FSM data
    await state.update_data(gender=gender)
    
    # Move to next step - height
    await state.set_state(ProfileStates.waiting_for_height)
    
    await callback.answer()
    await callback.message.answer(
        f"✅ Gender: {gender_label}\n\n"
        f"📏 **Step 3/6: Your Height**\n\n"
        f"Please enter your height in centimeters (e.g., 175):",
        parse_mode="Markdown"
    )

async def process_height(message: types.Message, state: FSMContext):
    """Process height input"""
    try:
        height = int(message.text.strip())
        if height < 100 or height > 250:
            await message.answer(
                "❌ **Invalid height**\n\n"
                "Please enter height between 100 and 250 cm:",
                parse_mode="Markdown"
            )
            return
        
        # Store height in FSM data
        await state.update_data(height_cm=height)
        
        # Move to next step - weight
        await state.set_state(ProfileStates.waiting_for_weight)
        
        await message.answer(
            f"✅ Height: {height} cm\n\n"
            f"⚖️ **Step 4/6: Your Weight**\n\n"
            f"Please enter your weight in kilograms (e.g., 70 or 70.5):",
            parse_mode="Markdown"
        )
        
    except ValueError:
        await message.answer(
            "❌ **Invalid input**\n\n"
            "Please enter your height as a number in centimeters (e.g., 175):",
            parse_mode="Markdown"
        )

async def process_weight(message: types.Message, state: FSMContext):
    """Process weight input"""
    try:
        weight = float(message.text.strip().replace(',', '.'))
        if weight < 30 or weight > 300:
            await message.answer(
                "❌ **Invalid weight**\n\n"
                "Please enter weight between 30 and 300 kg:",
                parse_mode="Markdown"
            )
            return
        
        # Store weight in FSM data
        await state.update_data(weight_kg=weight)
        
        # Move to next step - activity level
        await state.set_state(ProfileStates.waiting_for_activity)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="😴 Sedentary", callback_data="activity_sedentary")],
            [types.InlineKeyboardButton(text="🚶 Lightly Active", callback_data="activity_lightly_active")],
            [types.InlineKeyboardButton(text="🏃 Moderately Active", callback_data="activity_moderately_active")],
            [types.InlineKeyboardButton(text="💪 Very Active", callback_data="activity_very_active")],
            [types.InlineKeyboardButton(text="🏋️ Extremely Active", callback_data="activity_extremely_active")]
        ])
        
        await message.answer(
            f"✅ Weight: {weight} kg\n\n"
            f"🏃 **Step 5/6: Activity Level**\n\n"
            f"Please select your typical activity level:\n\n"
            f"😴 **Sedentary** - Little/no exercise\n"
            f"🚶 **Lightly Active** - Light exercise 1-3 days/week\n"
            f"🏃 **Moderately Active** - Moderate exercise 3-5 days/week\n"
            f"💪 **Very Active** - Hard exercise 6-7 days/week\n"
            f"🏋️ **Extremely Active** - Very hard exercise + physical job",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except ValueError:
        await message.answer(
            "❌ **Invalid input**\n\n"
            "Please enter your weight as a number (e.g., 70 or 70.5):",
            parse_mode="Markdown"
        )

async def process_activity(callback: types.CallbackQuery, state: FSMContext):
    """Process activity level selection"""
    activity_map = {
        "activity_sedentary": ("sedentary", "😴 Sedentary"),
        "activity_lightly_active": ("lightly_active", "🚶 Lightly Active"),
        "activity_moderately_active": ("moderately_active", "🏃 Moderately Active"),
        "activity_very_active": ("very_active", "💪 Very Active"),
        "activity_extremely_active": ("extremely_active", "🏋️ Extremely Active")
    }
    
    activity_value, activity_label = activity_map[callback.data]
    
    # Store activity in FSM data
    await state.update_data(activity_level=activity_value)
    
    # Move to final step - goal
    await state.set_state(ProfileStates.waiting_for_goal)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📉 Lose Weight", callback_data="goal_lose_weight")],
        [types.InlineKeyboardButton(text="⚖️ Maintain Weight", callback_data="goal_maintain_weight")],
        [types.InlineKeyboardButton(text="📈 Gain Weight", callback_data="goal_gain_weight")]
    ])
    
    await callback.answer()
    await callback.message.answer(
        f"✅ Activity Level: {activity_label}\n\n"
        f"🎯 **Step 6/6: Your Goal**\n\n"
        f"What is your primary goal?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def process_goal(callback: types.CallbackQuery, state: FSMContext):
    """Process goal selection and complete profile setup"""
    goal_map = {
        "goal_lose_weight": ("lose_weight", "📉 Lose Weight"),
        "goal_maintain_weight": ("maintain_weight", "⚖️ Maintain Weight"),
        "goal_gain_weight": ("gain_weight", "📈 Gain Weight")
    }
    
    goal_value, goal_label = goal_map[callback.data]
    
    # Store goal in FSM data
    await state.update_data(goal=goal_value)
    
    # Get all collected data
    data = await state.get_data()
    
    try:
        # Get user
        telegram_user_id = callback.from_user.id
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # Create or update profile
        profile, was_created = await create_or_update_profile(user['id'], data)
        
        # Log profile creation/update
        await log_user_action(
            user_id=user['id'],
            action_type="profile_setup" if was_created else "profile_update",
            metadata={
                "username": callback.from_user.username,
                "profile_data": data,
                "daily_calories_calculated": profile.get('daily_calories_target')
            }
        )
        
        # Clear FSM state
        await state.clear()
        
        gender_label = "👨 Male" if data['gender'] == 'male' else "👩 Female"
        activity_labels = {
            'sedentary': '😴 Sedentary',
            'lightly_active': '🚶 Lightly Active',
            'moderately_active': '🏃 Moderately Active',
            'very_active': '💪 Very Active',
            'extremely_active': '🏋️ Extremely Active'
        }
        activity_label = activity_labels.get(data['activity_level'], data['activity_level'])
        
        success_text = (
            f"🎉 **Profile {'Created' if was_created else 'Updated'} Successfully!**\n\n"
            f"📊 **Your Profile Summary:**\n"
            f"📅 Age: {data['age']} years\n"
            f"👤 Gender: {gender_label}\n"
            f"📏 Height: {data['height_cm']} cm\n"
            f"⚖️ Weight: {data['weight_kg']} kg\n"
            f"🏃 Activity: {activity_label}\n"
            f"🎯 Goal: {goal_label}\n\n"
            f"🔥 **Daily Calorie Target: {profile.get('daily_calories_target', 'Calculating...')} calories**\n\n"
            f"✨ Now you'll see personalized progress when analyzing food photos!"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📊 View Daily Plan",
                    callback_data="action_daily"
                ),
                types.InlineKeyboardButton(
                    text="📸 Analyze Food",
                    callback_data="action_analyze_info"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="profile_main_menu"
                )
            ]
        ])
        
        await callback.answer()
        await callback.message.answer(success_text, parse_mode="Markdown", reply_markup=keyboard)
        
        logger.info(f"Profile {'created' if was_created else 'updated'} for user {telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Error saving profile for user {telegram_user_id}: {e}")
        await callback.answer("❌ An error occurred while saving your profile. Please try again.")
        await state.clear() 