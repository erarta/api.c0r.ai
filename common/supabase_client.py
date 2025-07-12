import os
from supabase import create_client, Client
import asyncio
from typing import Optional
from loguru import logger

# Must be set in .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# USERS
async def get_or_create_user(telegram_id: int, country: Optional[str] = None):
    logger.info(f"Getting or creating user for telegram_id: {telegram_id}")
    # Поиск пользователя
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    if user:
        logger.info(f"Found existing user {telegram_id}: {user[0]}")
        return user[0]
    # Создание пользователя с 3 кредитами
    data = {"telegram_id": telegram_id, "credits_remaining": 3}
    if country:
        data["country"] = country
    logger.info(f"Creating new user {telegram_id} with data: {data}")
    user = supabase.table("users").insert(data).execute().data[0]
    logger.info(f"Created new user {telegram_id}: {user}")
    return user

async def get_user_by_telegram_id(telegram_id: int):
    logger.info(f"Getting user by telegram_id: {telegram_id}")
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    result = user[0] if user else None
    logger.info(f"User {telegram_id} query result: {result}")
    return result

async def decrement_credits(telegram_id: int, count: int = 1):
    logger.info(f"Decrementing {count} credits for user {telegram_id}")
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for credit decrement")
        return None
    
    old_credits = user["credits_remaining"]
    new_credits = max(0, old_credits - count)
    logger.info(f"User {telegram_id} credits: {old_credits} -> {new_credits}")
    
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Credits decremented for user {telegram_id}: {updated}")
    return updated

async def add_credits(telegram_id: int, count: int = 20):
    logger.info(f"Adding {count} credits for user {telegram_id}")
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for credit addition")
        return None
    
    old_credits = user["credits_remaining"]
    new_credits = old_credits + count
    logger.info(f"User {telegram_id} credits: {old_credits} -> {new_credits}")
    
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Credits added for user {telegram_id}: {updated}")
    return updated

# USER PROFILES
async def get_user_profile(user_id: str):
    """
    Get user profile by user_id
    
    Args:
        user_id: User UUID from database
        
    Returns:
        Profile data or None if not exists
    """
    logger.info(f"Getting profile for user {user_id}")
    profile = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute().data
    result = profile[0] if profile else None
    logger.info(f"Profile for user {user_id}: {result}")
    return result

async def get_user_with_profile(telegram_id: int):
    """
    Get user data together with profile
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        Dictionary with user and profile data
    """
    logger.info(f"Getting user with profile for telegram_id: {telegram_id}")
    
    # Get user
    user = await get_or_create_user(telegram_id)
    if not user:
        return None
    
    # Get profile
    profile = await get_user_profile(user['id'])
    
    result = {
        'user': user,
        'profile': profile,
        'has_profile': profile is not None
    }
    
    logger.info(f"User with profile for {telegram_id}: has_profile={result['has_profile']}")
    return result

async def create_user_profile(user_id: str, profile_data: dict):
    """
    Create user profile with personal data for calorie calculation
    
    Args:
        user_id: User UUID from database
        profile_data: Dictionary with profile fields (age, gender, height_cm, weight_kg, activity_level, goal)
    """
    logger.info(f"Creating profile for user {user_id}: {profile_data}")
    
    # Calculate daily calories target if we have enough data
    if all(key in profile_data for key in ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']):
        daily_calories = calculate_daily_calories(profile_data)
        profile_data['daily_calories_target'] = daily_calories
        logger.info(f"Calculated daily calories for user {user_id}: {daily_calories}")
    
    # Add user_id to profile data
    profile_data['user_id'] = user_id
    
    created = supabase.table("user_profiles").insert(profile_data).execute().data[0]
    logger.info(f"Profile created for user {user_id}: {created}")
    return created

async def update_user_profile(user_id: str, profile_data: dict):
    """
    Update user profile with personal data for calorie calculation
    
    Args:
        user_id: User UUID from database
        profile_data: Dictionary with profile fields (age, gender, height_cm, weight_kg, activity_level, goal)
    """
    logger.info(f"Updating profile for user {user_id}: {profile_data}")
    
    # Calculate daily calories target if we have enough data
    if all(key in profile_data for key in ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']):
        daily_calories = calculate_daily_calories(profile_data)
        profile_data['daily_calories_target'] = daily_calories
        logger.info(f"Calculated daily calories for user {user_id}: {daily_calories}")
    
    updated = supabase.table("user_profiles").update(profile_data).eq("user_id", user_id).execute().data[0]
    logger.info(f"Profile updated for user {user_id}: {updated}")
    return updated

def calculate_daily_calories(profile_data: dict) -> int:
    """
    Calculate daily calorie target using Mifflin-St Jeor Equation
    
    Args:
        profile_data: Dictionary with age, gender, height_cm, weight_kg, activity_level, goal
        
    Returns:
        Daily calorie target as integer
    """
    age = profile_data['age']
    gender = profile_data['gender']
    height = profile_data['height_cm']
    weight = profile_data['weight_kg']
    activity = profile_data['activity_level']
    goal = profile_data['goal']
    
    # Mifflin-St Jeor Equation for BMR (Basal Metabolic Rate)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    }
    
    # Calculate TDEE (Total Daily Energy Expenditure)
    tdee = bmr * activity_multipliers.get(activity, 1.2)
    
    # Adjust for goal
    if goal == 'lose_weight':
        tdee *= 0.85  # 15% deficit
    elif goal == 'gain_weight':
        tdee *= 1.15  # 15% surplus
    # maintain_weight: no adjustment
    
    return int(tdee)

async def create_or_update_profile(user_id: str, profile_data: dict):
    """
    Create new profile or update existing one
    
    Args:
        user_id: User UUID from database
        profile_data: Dictionary with profile fields
        
    Returns:
        Profile data and whether it was created (True) or updated (False)
    """
    logger.info(f"Create or update profile for user {user_id}")
    
    # Check if profile exists
    existing_profile = await get_user_profile(user_id)
    
    if existing_profile:
        # Update existing profile
        updated_profile = await update_user_profile(user_id, profile_data)
        logger.info(f"Profile updated for user {user_id}")
        return updated_profile, False
    else:
        # Create new profile
        new_profile = await create_user_profile(user_id, profile_data)
        logger.info(f"Profile created for user {user_id}")
        return new_profile, True

async def get_daily_calories_consumed(user_id: str, date: str = None):
    """
    Get calories consumed by user for specific date
    
    Args:
        user_id: User UUID from database
        date: Date in YYYY-MM-DD format (default: today)
        
    Returns:
        Dictionary with consumed calories and food items
    """
    from datetime import datetime
    
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"Getting daily calories for user {user_id} on {date}")
    
    # Get all photo analyses for the date
    logs = supabase.table("logs").select("*").eq("user_id", user_id).eq("action_type", "photo_analysis").gte("timestamp", f"{date}T00:00:00").lt("timestamp", f"{date}T23:59:59").execute().data
    
    total_calories = 0
    total_protein = 0
    total_fats = 0
    total_carbs = 0
    food_items = []
    
    for log in logs:
        if log.get('kbzhu'):
            kbzhu = log['kbzhu']
            calories = float(kbzhu.get('calories', 0))
            protein = float(kbzhu.get('protein', 0))
            fats = float(kbzhu.get('fats', 0))
            carbs = float(kbzhu.get('carbs', 0))
            
            total_calories += calories
            total_protein += protein
            total_fats += fats
            total_carbs += carbs
            
            food_items.append({
                'timestamp': log['timestamp'],
                'photo_url': log.get('photo_url'),
                'calories': calories,
                'protein': protein,
                'fats': fats,
                'carbs': carbs,
                'metadata': log.get('metadata', {})
            })
    
    result = {
        'date': date,
        'total_calories': round(total_calories, 1),
        'total_protein': round(total_protein, 1),
        'total_fats': round(total_fats, 1),
        'total_carbs': round(total_carbs, 1),
        'food_items_count': len(food_items),
        'food_items': food_items
    }
    
    logger.info(f"Daily calories for user {user_id} on {date}: {total_calories}")
    return result

# LOGS
async def log_user_action(user_id: str, action_type: str, metadata: dict = None, photo_url: str = None, kbzhu: dict = None, model_used: str = None):
    """
    Universal function to log all user actions
    
    Args:
        user_id: User UUID from database
        action_type: Type of action (start, help, status, buy, photo_analysis, profile, daily)
        metadata: Additional action-specific data
        photo_url: URL of photo (for photo_analysis only)
        kbzhu: Nutritional data (for photo_analysis only)
        model_used: AI model used (for photo_analysis only)
    """
    logger.info(f"Logging user action: {action_type} for user {user_id}")
    
    log = {
        "user_id": user_id,
        "action_type": action_type,
        "metadata": metadata or {}
    }
    
    # Add photo-specific data if provided
    if photo_url:
        log["photo_url"] = photo_url
    if kbzhu:
        log["kbzhu"] = kbzhu
    if model_used:
        log["model_used"] = model_used
    
    supabase.table("logs").insert(log).execute()
    logger.info(f"Action {action_type} logged for user {user_id}")
    return True

async def log_analysis(user_id: str, photo_url: str, kbzhu: dict, model_used: str):
    """
    Legacy function for photo analysis logging - now uses log_user_action
    """
    logger.info(f"Logging analysis for user {user_id}")
    return await log_user_action(
        user_id=user_id,
        action_type="photo_analysis",
        photo_url=photo_url,
        kbzhu=kbzhu,
        model_used=model_used
    )

# PAYMENTS
async def add_payment(user_id: str, amount: float, gateway: str, status: str):
    logger.info(f"Adding payment record for user {user_id}: {amount} via {gateway}")
    payment = {
        "user_id": user_id,
        "amount": amount,
        "gateway": gateway,
        "status": status
    }
    supabase.table("payments").insert(payment).execute()
    logger.info(f"Payment recorded for user {user_id}")
    return True

async def get_user_total_paid(user_id: str) -> float:
    """
    Calculate total amount paid by user from payments table
    
    Args:
        user_id: User UUID from database
        
    Returns:
        Total amount paid by user
    """
    try:
        logger.info(f"Calculating total paid for user {user_id}")
        
        # Get all successful payments for user
        payments = supabase.table("payments").select("amount").eq("user_id", user_id).eq("status", "succeeded").execute().data
        
        total = sum(float(payment['amount']) for payment in payments)
        logger.info(f"Total paid for user {user_id}: {total}")
        
        return total
    except Exception as e:
        logger.error(f"Error calculating total paid for user {user_id}: {e}")
        return 0.0 