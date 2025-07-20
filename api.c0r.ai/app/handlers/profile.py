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
    calculate_daily_calories,
    get_or_create_user
)
from i18n.i18n import i18n

# FSM States for profile setup
class ProfileStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_activity = State()
    waiting_for_goal = State()
    waiting_for_dietary_preferences = State()
    waiting_for_allergies = State()

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
            # Start profile setup immediately
            await start_profile_setup(message, state, telegram_user_id)
            
    except Exception as e:
        logger.error(f"Error in /profile command for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def show_profile_menu(message: types.Message, user: dict, profile: dict):
    """Show profile menu for existing profile"""
    user_language = user.get('language', 'en')
    # Format profile data
    age = profile.get('age', 'Not set')
    gender_map = {
        'male': '👨',
        'female': '👩',
        None: ''
    }
    gender = gender_map.get(profile.get('gender'), '')
    gender_label = i18n.get_text('profile_gender', user_language, gender=gender + ' ' + (i18n.get_text('gender_male', user_language) if profile.get('gender') == 'male' else i18n.get_text('gender_female', user_language) if profile.get('gender') == 'female' else ''))
    height = i18n.get_text('profile_height', user_language, height=profile.get('height_cm', 'Not set')) if profile.get('height_cm') else i18n.get_text('profile_height', user_language, height='Not set')
    weight = i18n.get_text('profile_weight', user_language, weight=profile.get('weight_kg', 'Not set')) if profile.get('weight_kg') else i18n.get_text('profile_weight', user_language, weight='Not set')
    
    activity_labels = {
        'sedentary': i18n.get_text('activity_sedentary', user_language),
        'lightly_active': i18n.get_text('activity_lightly_active', user_language),
        'moderately_active': i18n.get_text('activity_moderately_active', user_language),
        'very_active': i18n.get_text('activity_very_active', user_language),
        'extremely_active': i18n.get_text('activity_extremely_active', user_language)
    }
    activity = i18n.get_text('profile_activity', user_language, activity=activity_labels.get(profile.get('activity_level'), i18n.get_text('activity_not_set', user_language)))
    
    goal_labels = {
        'lose_weight': i18n.get_text('goal_lose_weight', user_language),
        'maintain_weight': i18n.get_text('goal_maintain_weight', user_language),
        'gain_weight': i18n.get_text('goal_gain_weight', user_language)
    }
    goal = i18n.get_text('profile_goal', user_language, goal=goal_labels.get(profile.get('goal'), i18n.get_text('goal_not_set', user_language)))
    
    daily_calories = profile.get('daily_calories_target', 'Not calculated')
    calories_label = i18n.get_text('profile_calories', user_language, calories=daily_calories if daily_calories != 'Not calculated' else i18n.get_text('calories_not_calculated', user_language))
    
    profile_text = (
        f"{i18n.get_text('profile_title', user_language)}\n\n"
        f"{i18n.get_text('profile_age', user_language, age=age)}\n"
        f"{gender_label}\n"
        f"{height}\n"
        f"{weight}\n"
        f"{activity}\n"
        f"{goal}\n\n"
        f"{calories_label}\n\n"
        f"{i18n.get_text('profile_what_next', user_language)}"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('profile_edit_btn', user_language),
                callback_data="profile_edit"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text('profile_recalculate_btn', user_language),
                callback_data="profile_recalculate"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('btn_daily_plan', user_language),
                callback_data="action_daily"
            ),
            types.InlineKeyboardButton(
                text=i18n.get_text('profile_progress_btn', user_language),
                callback_data="profile_progress"
            )
        ],
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('btn_back', user_language),
                callback_data="action_main_menu"
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
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await callback.answer(i18n.get_text("error_general", user_language))

async def start_profile_setup(message: types.Message, state: FSMContext, telegram_user_id: int):
    """Start profile setup process"""
    # Clear any existing state
    await state.clear()
    await state.set_state(ProfileStates.waiting_for_age)
    
    # Get user's language
    user = await get_or_create_user(telegram_user_id)
    user_language = user.get('language', 'en')
    
    # Show setup instructions with better guidance
    setup_text = (
        f"{i18n.get_text('profile_setup_age', user_language)}\n\n"
        f"💡 {i18n.get_text('profile_setup_important', user_language)}\n"
        f"📝 {i18n.get_text('profile_setup_restart', user_language)}\n"
        f"🔄 {i18n.get_text('profile_setup_step', user_language, step=1, total=8)}"
    )
    
    await message.answer(
        setup_text,
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
        try:
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
        except ValueError as e:
            logger.error(f"Error recalculating calories: {e}")
            await message.answer(
                f"❌ **Calculation Error**\n\n"
                f"There was an issue with your profile data: {str(e)}\n\n"
                f"Please check your profile settings and try again.",
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Error recalculating calories for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def profile_skip(message: types.Message, telegram_user_id: int):
    """Handle profile setup skip"""
    try:
        # Show skip message
        skip_text = (
            f"⏭️ **Profile setup skipped**\n\n"
            f"💡 **Benefits of setting up a profile:**\n"
            f"• Personalized daily calorie targets\n"
            f"• Progress tracking\n"
            f"• Better nutrition recommendations\n\n"
            f"📸 You can still analyze food photos without a profile!"
        )
        
        skip_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="👤 Set Up Profile",
                    callback_data="profile_start_setup"
                )
            ]
        ])
        
        await message.answer(skip_text, parse_mode="Markdown", reply_markup=skip_keyboard)
        
        # Get user data for main menu
        from common.supabase_client import get_or_create_user
        user = await get_or_create_user(telegram_user_id)
        
        # Show main menu with buttons
        welcome_text = (
            f"🚀 **Ready to start?** Choose an option below:"
        )
        
        # Create interactive keyboard (same as in start_command)
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
        
    except Exception as e:
        logger.error(f"Error in profile_skip for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def profile_main_menu(message: types.Message, telegram_user_id: int):
    """Return to main menu"""
    from .commands import start_command
    await start_command(message)

async def show_progress(message: types.Message, telegram_user_id: int):
    """Show user progress and statistics"""
    try:
        user_data = await get_user_with_profile(telegram_user_id)
        user = user_data['user']
        
        # Get user's language
        user_language = user.get('language', 'en')
        
        # Get daily calories data
        from common.supabase_client import get_daily_calories_consumed
        from datetime import datetime
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_data = await get_daily_calories_consumed(user_data['user']['id'], today)
        
        progress_text = (
            f"{i18n.get_text('progress_title', user_language)}\n\n"
            f"{i18n.get_text('progress_today', user_language, date=today)}\n"
            f"{i18n.get_text('progress_meals_analyzed', user_language, count=daily_data['food_items_count'])}\n"
            f"{i18n.get_text('progress_calories_consumed', user_language, calories=daily_data['total_calories'])}\n"
            f"{i18n.get_text('progress_protein', user_language, protein=daily_data['total_protein'])}\n"
            f"{i18n.get_text('progress_fats', user_language, fats=daily_data['total_fats'])}\n"
            f"{i18n.get_text('progress_carbs', user_language, carbs=daily_data['total_carbs'])}\n\n"
        )
        
        if user_data['has_profile'] and user_data['profile'].get('daily_calories_target'):
            target = user_data['profile']['daily_calories_target']
            remaining = max(0, target - daily_data['total_calories'])
            progress_percent = min(100, int((daily_data['total_calories'] / target) * 100))
            
            progress_bar = "▓" * (progress_percent // 10) + "░" * (10 - progress_percent // 10)
            
            progress_text += (
                f"{i18n.get_text('progress_goal_title', user_language)}\n"
                f"{i18n.get_text('progress_target', user_language, target=target)}\n"
                f"{i18n.get_text('progress_remaining', user_language, remaining=remaining)}\n\n"
                f"{i18n.get_text('progress_bar', user_language, progress_bar=progress_bar, percent=progress_percent)}"
            )
        else:
            progress_text += i18n.get_text('progress_setup_needed', user_language)
        
        await message.answer(progress_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing progress for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        await message.answer(i18n.get_text("error_general", user_language))

async def show_profile_info(callback: types.CallbackQuery, user: dict, profile: dict):
    """Show profile information for existing profile"""
    user_language = user.get('language', 'en')
    age = profile.get('age', 'Not set')
    gender_map = {
        'male': '👨',
        'female': '👩',
        None: ''
    }
    gender = gender_map.get(profile.get('gender'), '')
    gender_label = i18n.get_text('profile_gender', user_language, gender=gender + ' ' + (i18n.get_text('gender_male', user_language) if profile.get('gender') == 'male' else i18n.get_text('gender_female', user_language) if profile.get('gender') == 'female' else ''))
    height = i18n.get_text('profile_height', user_language, height=profile.get('height_cm', 'Not set')) if profile.get('height_cm') else i18n.get_text('profile_height', user_language, height='Not set')
    weight = i18n.get_text('profile_weight', user_language, weight=profile.get('weight_kg', 'Not set')) if profile.get('weight_kg') else i18n.get_text('profile_weight', user_language, weight='Not set')
    
    activity_labels = {
        'sedentary': i18n.get_text('activity_sedentary', user_language),
        'lightly_active': i18n.get_text('activity_lightly_active', user_language),
        'moderately_active': i18n.get_text('activity_moderately_active', user_language),
        'very_active': i18n.get_text('activity_very_active', user_language),
        'extremely_active': i18n.get_text('activity_extremely_active', user_language)
    }
    activity = i18n.get_text('profile_activity', user_language, activity=activity_labels.get(profile.get('activity_level'), i18n.get_text('activity_not_set', user_language)))
    
    goal_labels = {
        'lose_weight': i18n.get_text('goal_lose_weight', user_language),
        'maintain_weight': i18n.get_text('goal_maintain_weight', user_language),
        'gain_weight': i18n.get_text('goal_gain_weight', user_language)
    }
    goal = i18n.get_text('profile_goal', user_language, goal=goal_labels.get(profile.get('goal'), i18n.get_text('goal_not_set', user_language)))
    
    daily_calories = profile.get('daily_calories_target', 'Not calculated')
    calories_label = i18n.get_text('profile_calories', user_language, calories=daily_calories if daily_calories != 'Not calculated' else i18n.get_text('calories_not_calculated', user_language))
    
    # Format dietary preferences
    dietary_prefs = profile.get('dietary_preferences', [])
    if dietary_prefs:
        dietary_items = []
        for pref in dietary_prefs:
            if pref == "none":
                dietary_items.append(i18n.get_text('profile_dietary_none', user_language))
            else:
                diet_translation_map = {
                    "vegetarian": "profile_dietary_vegetarian",
                    "vegan": "profile_dietary_vegan",
                    "pescatarian": "profile_dietary_pescatarian",
                    "keto": "profile_dietary_keto",
                    "paleo": "profile_dietary_paleo",
                    "mediterranean": "profile_dietary_mediterranean",
                    "low_carb": "profile_dietary_low_carb",
                    "low_fat": "profile_dietary_low_fat",
                    "gluten_free": "profile_dietary_gluten_free",
                    "dairy_free": "profile_dietary_dairy_free",
                    "halal": "profile_dietary_halal",
                    "kosher": "profile_dietary_kosher"
                }
                translation_key = diet_translation_map.get(pref, pref)
                dietary_items.append(i18n.get_text(translation_key, user_language))
        dietary_text = ", ".join(dietary_items)
    else:
        dietary_text = i18n.get_text('profile_dietary_none', user_language)
    
    # Format allergies
    allergies = profile.get('allergies', [])
    if allergies:
        allergy_items = []
        for allergy in allergies:
            if allergy == "none":
                allergy_items.append(i18n.get_text('profile_allergy_none', user_language))
            else:
                allergy_translation_map = {
                    "nuts": "profile_allergy_nuts",
                    "peanuts": "profile_allergy_peanuts",
                    "shellfish": "profile_allergy_shellfish",
                    "fish": "profile_allergy_fish",
                    "eggs": "profile_allergy_eggs",
                    "dairy": "profile_allergy_dairy",
                    "soy": "profile_allergy_soy",
                    "wheat": "profile_allergy_wheat",
                    "gluten": "profile_allergy_gluten",
                    "sesame": "profile_allergy_sesame",
                    "sulfites": "profile_allergy_sulfites"
                }
                translation_key = allergy_translation_map.get(allergy, allergy)
                allergy_items.append(i18n.get_text(translation_key, user_language))
        allergies_text = ", ".join(allergy_items)
    else:
        allergies_text = i18n.get_text('profile_allergy_none', user_language)
    
    profile_text = (
        f"{i18n.get_text('profile_title', user_language)}\n\n"
        f"{i18n.get_text('profile_age', user_language, age=age)}\n"
        f"{gender_label}\n"
        f"{height}\n"
        f"{weight}\n"
        f"{activity}\n"
        f"{goal}\n"
        f"{i18n.get_text('profile_diet', user_language, diet=dietary_text)}\n"
        f"{i18n.get_text('profile_allergies', user_language, allergies=allergies_text)}\n\n"
        f"{calories_label}"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=i18n.get_text('profile_edit_btn', user_language),
                callback_data="profile_edit"
            )
        ]
    ])
    
    await callback.message.answer(profile_text, parse_mode="Markdown", reply_markup=keyboard)

# FSM handlers for profile setup steps
async def process_age(message: types.Message, state: FSMContext):
    """Process age input"""
    try:
        age = int(message.text.strip())
        if age < 10 or age > 120:
            # Get user's language
            user = await get_or_create_user(message.from_user.id)
            user_language = user.get('language', 'en')
            
            await message.answer(
                i18n.get_text("profile_error_age", user_language),
                parse_mode="Markdown"
            )
            return
        
        # Get user's language first
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        
        # Store age in FSM data
        await state.update_data(age=age)
        
        # Move to next step - gender
        await state.set_state(ProfileStates.waiting_for_gender)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text=i18n.get_text('gender_male', user_language), callback_data="gender_male"),
                types.InlineKeyboardButton(text=i18n.get_text('gender_female', user_language), callback_data="gender_female")
            ]
        ])
        
        await message.answer(
            f"✅ {i18n.get_text('profile_setup_age_success', user_language, age=age)}\n\n"
            f"{i18n.get_text('profile_setup_gender', user_language)}\n\n"
            f"🔄 {i18n.get_text('profile_setup_step', user_language, step=2, total=8)}",
            reply_markup=keyboard
        )
        
    except ValueError:
        # Get user's language
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        
        await message.answer(
            i18n.get_text("profile_error_age_number", user_language),
            parse_mode="Markdown"
        )

async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    """Process gender selection"""
    gender = "male" if callback.data == "gender_male" else "female"
    
    # Get user's language
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    gender_label = i18n.get_text('gender_male', user_language) if gender == "male" else i18n.get_text('gender_female', user_language)
    
    # Store gender in FSM data
    await state.update_data(gender=gender)
    
    # Move to next step - height
    await state.set_state(ProfileStates.waiting_for_height)
    
    await callback.answer()
    await callback.message.answer(
        f"✅ {i18n.get_text('profile_setup_gender_success', user_language, gender=gender_label)}\n\n"
        f"{i18n.get_text('profile_setup_height', user_language)}\n\n"
        f"🔄 {i18n.get_text('profile_setup_step', user_language, step=3, total=8)}"
    )

async def process_height(message: types.Message, state: FSMContext):
    """Process height input"""
    try:
        height = int(message.text.strip())
        if height < 100 or height > 250:
            # Get user's language
            user = await get_or_create_user(message.from_user.id)
            user_language = user.get('language', 'en')
            
            await message.answer(
                i18n.get_text("profile_error_height", user_language),
                parse_mode="Markdown"
            )
            return
        
        # Store height in FSM data
        await state.update_data(height_cm=height)
        
        # Move to next step - weight
        await state.set_state(ProfileStates.waiting_for_weight)
        
        # Get user's language
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        
        await message.answer(
            f"✅ {i18n.get_text('profile_setup_height_success', user_language, height=height)}\n\n"
            f"{i18n.get_text('profile_setup_weight', user_language)}\n\n"
            f"🔄 {i18n.get_text('profile_setup_step', user_language, step=4, total=8)}"
        )
        
    except ValueError:
        # Get user's language
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en')
        
        await message.answer(
            i18n.get_text("profile_error_height_number", user_language),
            parse_mode="Markdown"
        )

async def process_weight(message: types.Message, state: FSMContext):
    """Process weight input"""
    # Get user's language first
    user = await get_or_create_user(message.from_user.id)
    user_language = user.get('language', 'en')
    
    try:
        weight = float(message.text.strip().replace(',', '.'))
        if weight < 30 or weight > 300:
            await message.answer(
                i18n.get_text("profile_error_weight", user_language),
                parse_mode="Markdown"
            )
            return
        
        # Store weight in FSM data
        await state.update_data(weight_kg=weight)
        
        # Move to next step - activity level
        await state.set_state(ProfileStates.waiting_for_activity)
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=i18n.get_text('activity_sedentary', user_language), callback_data="activity_sedentary")],
            [types.InlineKeyboardButton(text=i18n.get_text('activity_lightly_active', user_language), callback_data="activity_lightly_active")],
            [types.InlineKeyboardButton(text=i18n.get_text('activity_moderately_active', user_language), callback_data="activity_moderately_active")],
            [types.InlineKeyboardButton(text=i18n.get_text('activity_very_active', user_language), callback_data="activity_very_active")],
            [types.InlineKeyboardButton(text=i18n.get_text('activity_extremely_active', user_language), callback_data="activity_extremely_active")]
        ])
        
        await message.answer(
            f"✅ {i18n.get_text('profile_setup_weight_success', user_language, weight=weight)}\n\n"
            f"🔄 {i18n.get_text('profile_setup_step', user_language, step=5, total=8)}",
            reply_markup=keyboard
        )
        
    except ValueError:
        await message.answer(
            i18n.get_text("profile_error_weight_number", user_language),
            parse_mode="Markdown"
        )

async def process_activity(callback: types.CallbackQuery, state: FSMContext):
    """Process activity level selection"""
    # Get user's language first
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    activity_map = {
        "activity_sedentary": ("sedentary", i18n.get_text('activity_sedentary', user_language)),
        "activity_lightly_active": ("lightly_active", i18n.get_text('activity_lightly_active', user_language)),
        "activity_moderately_active": ("moderately_active", i18n.get_text('activity_moderately_active', user_language)),
        "activity_very_active": ("very_active", i18n.get_text('activity_very_active', user_language)),
        "activity_extremely_active": ("extremely_active", i18n.get_text('activity_extremely_active', user_language))
    }
    
    activity_value, activity_label = activity_map[callback.data]
    
    # Store activity in FSM data
    await state.update_data(activity_level=activity_value)
    
    # Move to final step - goal
    await state.set_state(ProfileStates.waiting_for_goal)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=i18n.get_text('goal_lose_weight', user_language), callback_data="goal_lose_weight")],
        [types.InlineKeyboardButton(text=i18n.get_text('goal_maintain_weight', user_language), callback_data="goal_maintain_weight")],
        [types.InlineKeyboardButton(text=i18n.get_text('goal_gain_weight', user_language), callback_data="goal_gain_weight")]
    ])
    
    await callback.answer()
    await callback.message.answer(
        f"✅ {i18n.get_text('profile_setup_activity_success', user_language, activity=activity_label)}\n\n"
        f"{i18n.get_text('profile_setup_goal', user_language)}\n\n"
        f"🔄 {i18n.get_text('profile_setup_step', user_language, step=6, total=8)}",
        reply_markup=keyboard
    )

async def process_goal(callback: types.CallbackQuery, state: FSMContext):
    """Process goal selection and move to dietary preferences"""
    # Get user's language first
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    goal_map = {
        "goal_lose_weight": ("lose_weight", i18n.get_text('goal_lose_weight', user_language)),
        "goal_maintain_weight": ("maintain_weight", i18n.get_text('goal_maintain_weight', user_language)),
        "goal_gain_weight": ("gain_weight", i18n.get_text('goal_gain_weight', user_language))
    }
    
    goal_value, goal_label = goal_map[callback.data]
    
    # Store goal in FSM data
    await state.update_data(goal=goal_value)
    
    # Move to dietary preferences step
    await state.set_state(ProfileStates.waiting_for_dietary_preferences)
    
    # Get user's language
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    # Initialize dietary preferences list in state
    await state.update_data(dietary_preferences=[])
    
    # Create dietary preferences keyboard
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_vegetarian', user_language), callback_data="diet_vegetarian")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_vegan', user_language), callback_data="diet_vegan")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_pescatarian', user_language), callback_data="diet_pescatarian")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_keto', user_language), callback_data="diet_keto")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_paleo', user_language), callback_data="diet_paleo")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_mediterranean', user_language), callback_data="diet_mediterranean")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_gluten_free', user_language), callback_data="diet_gluten_free")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_dairy_free', user_language), callback_data="diet_dairy_free")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_halal', user_language), callback_data="diet_halal")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_kosher', user_language), callback_data="diet_kosher")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_none', user_language), callback_data="diet_none")],
        [types.InlineKeyboardButton(text=i18n.get_text('profile_dietary_done', user_language), callback_data="diet_done")]
    ])
    
    await callback.answer()
    await callback.message.answer(
        f"✅ {i18n.get_text('profile_setup_goal_success', user_language, goal=goal_label)}\n\n"
        f"{i18n.get_text('profile_setup_dietary', user_language)}\n\n"
        f"💡 {i18n.get_text('profile_setup_dietary_tip', user_language)}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
async def process_dietary_preferences(callback: types.CallbackQuery, state: FSMContext):
    """Process dietary preferences selection"""
    # Get user's language first
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    # Get current data
    data = await state.get_data()
    dietary_preferences = data.get('dietary_preferences', [])
    
    if callback.data == "diet_done":
        # Move to allergies step
        await state.set_state(ProfileStates.waiting_for_allergies)
        
        # Initialize allergies list in state
        await state.update_data(allergies=[])
        
        # Create allergies keyboard
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_nuts', user_language), callback_data="allergy_nuts")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_peanuts', user_language), callback_data="allergy_peanuts")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_shellfish', user_language), callback_data="allergy_shellfish")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_fish', user_language), callback_data="allergy_fish")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_eggs', user_language), callback_data="allergy_eggs")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_dairy', user_language), callback_data="allergy_dairy")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_soy', user_language), callback_data="allergy_soy")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_gluten', user_language), callback_data="allergy_gluten")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_sesame', user_language), callback_data="allergy_sesame")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_sulfites', user_language), callback_data="allergy_sulfites")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_none', user_language), callback_data="allergy_none")],
            [types.InlineKeyboardButton(text=i18n.get_text('profile_allergy_done', user_language), callback_data="allergy_done")]
        ])
        
        selected_text = ", ".join(dietary_preferences) if dietary_preferences else i18n.get_text('profile_dietary_none', user_language)
        
        await callback.answer()
        await callback.message.answer(
            f"✅ {i18n.get_text('profile_setup_dietary_success', user_language, preferences=selected_text)}\n\n"
            f"{i18n.get_text('profile_setup_allergies', user_language)}\n\n"
            f"💡 {i18n.get_text('profile_setup_allergies_tip', user_language)}",
            reply_markup=keyboard
        )
        return
    
    elif callback.data == "diet_none":
        # Clear all preferences and set to none
        dietary_preferences = ["none"]
        await state.update_data(dietary_preferences=dietary_preferences)
    else:
        # Handle individual dietary preference selection
        diet_map = {
            "diet_vegetarian": "vegetarian",
            "diet_vegan": "vegan",
            "diet_pescatarian": "pescatarian",
            "diet_keto": "keto",
            "diet_paleo": "paleo",
            "diet_mediterranean": "mediterranean",
            "diet_low_carb": "low_carb",
            "diet_low_fat": "low_fat",
            "diet_gluten_free": "gluten_free",
            "diet_dairy_free": "dairy_free",
            "diet_halal": "halal",
            "diet_kosher": "kosher"
        }
        
        preference = diet_map.get(callback.data)
        if preference:
            # Remove "none" if it exists
            if "none" in dietary_preferences:
                dietary_preferences.remove("none")
            
            # Toggle preference
            if preference in dietary_preferences:
                dietary_preferences.remove(preference)
            else:
                dietary_preferences.append(preference)
            
            await state.update_data(dietary_preferences=dietary_preferences)
    
    # Update the message with current selections
    if dietary_preferences:
        selected_items = []
        for pref in dietary_preferences:
            if pref == "none":
                selected_items.append(i18n.get_text('profile_dietary_none', user_language))
            else:
                # Map English values to translation keys
                diet_translation_map = {
                    "vegetarian": "profile_dietary_vegetarian",
                    "vegan": "profile_dietary_vegan",
                    "pescatarian": "profile_dietary_pescatarian",
                    "keto": "profile_dietary_keto",
                    "paleo": "profile_dietary_paleo",
                    "mediterranean": "profile_dietary_mediterranean",
                    "low_carb": "profile_dietary_low_carb",
                    "low_fat": "profile_dietary_low_fat",
                    "gluten_free": "profile_dietary_gluten_free",
                    "dairy_free": "profile_dietary_dairy_free",
                    "halal": "profile_dietary_halal",
                    "kosher": "profile_dietary_kosher"
                }
                translation_key = diet_translation_map.get(pref, pref)
                selected_items.append(i18n.get_text(translation_key, user_language))
        selected_text = ", ".join(selected_items)
    else:
        selected_text = i18n.get_text('profile_dietary_none', user_language)
    
    await callback.answer(f"{i18n.get_text('profile_setup_dietary_success', user_language, preferences=selected_text)}")

async def process_allergies(callback: types.CallbackQuery, state: FSMContext):
    """Process allergies selection and complete profile setup"""
    # Get user's language first
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    # Get current data
    data = await state.get_data()
    allergies = data.get('allergies', [])
    
    if callback.data == "allergy_done":
        # Complete profile setup
        await complete_profile_setup(callback, state)
        return
    
    elif callback.data == "allergy_none":
        # Clear all allergies and set to none
        allergies = ["none"]
        await state.update_data(allergies=allergies)
    else:
        # Handle individual allergy selection
        allergy_map = {
            "allergy_nuts": "nuts",
            "allergy_peanuts": "peanuts",
            "allergy_shellfish": "shellfish",
            "allergy_fish": "fish",
            "allergy_eggs": "eggs",
            "allergy_dairy": "dairy",
            "allergy_soy": "soy",
            "allergy_wheat": "wheat",
            "allergy_gluten": "gluten",
            "allergy_sesame": "sesame",
            "allergy_sulfites": "sulfites"
        }
        
        allergy = allergy_map.get(callback.data)
        if allergy:
            # Remove "none" if it exists
            if "none" in allergies:
                allergies.remove("none")
            
            # Toggle allergy
            if allergy in allergies:
                allergies.remove(allergy)
            else:
                allergies.append(allergy)
            
            await state.update_data(allergies=allergies)
    
    # Update the message with current selections
    if allergies:
        selected_items = []
        for allergy in allergies:
            if allergy == "none":
                selected_items.append(i18n.get_text('profile_allergy_none', user_language))
            else:
                # Map English values to translation keys
                allergy_translation_map = {
                    "nuts": "profile_allergy_nuts",
                    "peanuts": "profile_allergy_peanuts",
                    "shellfish": "profile_allergy_shellfish",
                    "fish": "profile_allergy_fish",
                    "eggs": "profile_allergy_eggs",
                    "dairy": "profile_allergy_dairy",
                    "soy": "profile_allergy_soy",
                    "wheat": "profile_allergy_wheat",
                    "gluten": "profile_allergy_gluten",
                    "sesame": "profile_allergy_sesame",
                    "sulfites": "profile_allergy_sulfites"
                }
                translation_key = allergy_translation_map.get(allergy, allergy)
                selected_items.append(i18n.get_text(translation_key, user_language))
        selected_text = ", ".join(selected_items)
    else:
        selected_text = i18n.get_text('profile_allergy_none', user_language)
    
    await callback.answer(f"{i18n.get_text('profile_setup_allergies_success', user_language, allergies=selected_text)}")

async def complete_profile_setup(callback: types.CallbackQuery, state: FSMContext):
    """Complete profile setup with all collected data"""
    # Get user's language first
    user = await get_or_create_user(callback.from_user.id)
    user_language = user.get('language', 'en')
    
    # Get all collected data
    data = await state.get_data()
    
    # Validate that all required fields are present and valid
    required_fields = {
        'age': 'age',
        'gender': 'gender',
        'height_cm': 'height',
        'weight_kg': 'weight',
        'activity_level': 'activity level',
        'goal': 'goal'
    }
    
    missing_fields = []
    for field, field_name in required_fields.items():
        if field not in data or data[field] is None:
            missing_fields.append(field_name)
    
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        error_message = i18n.get_text('profile_error_missing_fields', user_language, fields=missing_text)
        
        await callback.answer(error_message)
        
        # Restart profile setup
        await start_profile_setup(callback.message, state, callback.from_user.id)
        return
    
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
        
        gender_label = i18n.get_text('gender_male', user_language) if data['gender'] == 'male' else i18n.get_text('gender_female', user_language)
        
        activity_labels = {
            'sedentary': i18n.get_text('activity_sedentary', user_language),
            'lightly_active': i18n.get_text('activity_lightly_active', user_language),
            'moderately_active': i18n.get_text('activity_moderately_active', user_language),
            'very_active': i18n.get_text('activity_very_active', user_language),
            'extremely_active': i18n.get_text('activity_extremely_active', user_language)
        }
        activity_label = activity_labels.get(data['activity_level'], data['activity_level'])
        
        goal_labels = {
            'lose_weight': i18n.get_text('goal_lose_weight', user_language),
            'maintain_weight': i18n.get_text('goal_maintain_weight', user_language),
            'gain_weight': i18n.get_text('goal_gain_weight', user_language)
        }
        goal_label = goal_labels.get(data['goal'], data['goal'])
        
        action_text = i18n.get_text('profile_created', user_language) if was_created else i18n.get_text('profile_updated', user_language)
        
        # Format dietary preferences and allergies
        dietary_prefs = data.get('dietary_preferences', [])
        allergies = data.get('allergies', [])
        
        # Format dietary preferences with translations
        if dietary_prefs:
            dietary_items = []
            for pref in dietary_prefs:
                if pref == "none":
                    dietary_items.append(i18n.get_text('profile_dietary_none', user_language))
                else:
                    diet_translation_map = {
                        "vegetarian": "profile_dietary_vegetarian",
                        "vegan": "profile_dietary_vegan",
                        "pescatarian": "profile_dietary_pescatarian",
                        "keto": "profile_dietary_keto",
                        "paleo": "profile_dietary_paleo",
                        "mediterranean": "profile_dietary_mediterranean",
                        "low_carb": "profile_dietary_low_carb",
                        "low_fat": "profile_dietary_low_fat",
                        "gluten_free": "profile_dietary_gluten_free",
                        "dairy_free": "profile_dietary_dairy_free",
                        "halal": "profile_dietary_halal",
                        "kosher": "profile_dietary_kosher"
                    }
                    translation_key = diet_translation_map.get(pref, pref)
                    dietary_items.append(i18n.get_text(translation_key, user_language))
            dietary_text = ", ".join(dietary_items)
        else:
            dietary_text = i18n.get_text('profile_dietary_none', user_language)
        
        # Format allergies with translations
        if allergies:
            allergy_items = []
            for allergy in allergies:
                if allergy == "none":
                    allergy_items.append(i18n.get_text('profile_allergy_none', user_language))
                else:
                    allergy_translation_map = {
                        "nuts": "profile_allergy_nuts",
                        "peanuts": "profile_allergy_peanuts",
                        "shellfish": "profile_allergy_shellfish",
                        "fish": "profile_allergy_fish",
                        "eggs": "profile_allergy_eggs",
                        "dairy": "profile_allergy_dairy",
                        "soy": "profile_allergy_soy",
                        "wheat": "profile_allergy_wheat",
                        "gluten": "profile_allergy_gluten",
                        "sesame": "profile_allergy_sesame",
                        "sulfites": "profile_allergy_sulfites"
                    }
                    translation_key = allergy_translation_map.get(allergy, allergy)
                    allergy_items.append(i18n.get_text(translation_key, user_language))
            allergies_text = ", ".join(allergy_items)
        else:
            allergies_text = i18n.get_text('profile_allergy_none', user_language)
        
        success_text = (
            f"{i18n.get_text('profile_setup_complete', user_language)}\n\n"
            f"{i18n.get_text('profile_summary', user_language)}\n"
            f"{i18n.get_text('profile_age', user_language, age=data['age'])}\n"
            f"{gender_label}\n"
            f"{i18n.get_text('profile_height', user_language, height=data['height_cm'])}\n"
            f"{i18n.get_text('profile_weight', user_language, weight=data['weight_kg'])}\n"
            f"{i18n.get_text('profile_activity', user_language, activity=activity_label)}\n"
            f"{i18n.get_text('profile_goal', user_language, goal=goal_label)}\n"
            f"{i18n.get_text('profile_diet', user_language, diet=dietary_text)}\n"
            f"{i18n.get_text('profile_allergies', user_language, allergies=allergies_text)}\n\n"
            f"{i18n.get_text('profile_calories', user_language, calories=profile.get('daily_calories_target', 'Вычисляется...'))}\n\n"
            f"{i18n.get_text('profile_ready', user_language)}"
        )
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_view_daily_plan', user_language),
                    callback_data="action_daily"
                ),
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_analyze_food', user_language),
                    callback_data="action_analyze_info"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_get_recipe', user_language),
                    callback_data="action_recipe"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=i18n.get_text('btn_main_menu', user_language),
                    callback_data="profile_main_menu"
                )
            ]
        ])
        
        await callback.answer()
        await callback.message.answer(success_text, parse_mode="Markdown", reply_markup=keyboard)
        
        logger.info(f"Profile {'created' if was_created else 'updated'} for user {telegram_user_id}")
        
    except ValueError as e:
        logger.error(f"Validation error saving profile for user {telegram_user_id}: {e}")
        
        # Get user's language for error message
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        
        # Provide more specific error message for missing data
        if "Missing or invalid" in str(e):
            await callback.answer(f"❌ {i18n.get_text('profile_incomplete', user_language)}")
        else:
            await callback.answer(i18n.get_text("error_general", user_language))
        await state.clear()
    except Exception as e:
        logger.error(f"Error saving profile for user {telegram_user_id}: {e}")
        # Get user's language for error message
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        await callback.answer(i18n.get_text("error_general", user_language))
        await state.clear()