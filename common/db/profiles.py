"""
User profile management operations
Handles user profiles, calorie calculations, and daily nutrition tracking
"""
import asyncio
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from loguru import logger
from .client import supabase
from .users import get_or_create_user


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


def calculate_daily_calories(profile_data: dict) -> int:
    """
    Calculate daily calorie target using Mifflin-St Jeor Equation.
    
    Args:
        profile_data: Dictionary with age, gender, height_cm, weight_kg, activity_level, goal
        
    Returns:
        Daily calorie target as integer
        
    Raises:
        ValueError: If any input parameter is invalid or missing
    """
    # Validate all required fields are present and not None
    required_fields = ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']
    for field in required_fields:
        if field not in profile_data or profile_data[field] is None:
            raise ValueError(f"Missing or invalid {field} in profile data")
    
    age = profile_data['age']
    gender = profile_data['gender'].lower()
    height = profile_data['height_cm']
    weight = profile_data['weight_kg']
    activity = profile_data['activity_level'].lower()
    goal = profile_data['goal'].lower()
    
    # Validate gender
    if gender not in ['male', 'female']:
        raise ValueError("Gender must be 'male' or 'female'")
    
    # Mifflin-St Jeor Equation for BMR (Basal Metabolic Rate)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    }
    
    # Validate activity level
    if activity not in activity_multipliers:
        raise ValueError("Invalid activity level.")
    
    # Calculate TDEE (Total Daily Energy Expenditure)
    tdee = bmr * activity_multipliers[activity]
    
    # Adjust for goal
    if goal == 'lose_weight':
        tdee *= 0.85  # 15% deficit
    elif goal == 'gain_weight':
        tdee *= 1.15  # 15% surplus
    elif goal == 'maintain_weight':
        pass  # No adjustment
    else:
        raise ValueError("Goal must be 'lose_weight', 'gain_weight', or 'maintain_weight'.")
    
    return round(tdee)


async def validate_profile_completeness(profile_data: dict) -> Tuple[bool, List[str]]:
    """
    Validate that a profile has all required fields
    
    Args:
        profile_data: Dictionary with profile fields
        
    Returns:
        Tuple of (is_complete, missing_fields)
    """
    required_fields = ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']
    missing_fields = []
    
    for field in required_fields:
        if field not in profile_data or profile_data[field] is None:
            missing_fields.append(field)
    
    # Optional fields with defaults
    if 'dietary_preferences' not in profile_data:
        profile_data['dietary_preferences'] = ['none']
    if 'allergies' not in profile_data:
        profile_data['allergies'] = ['none']
    
    is_complete = len(missing_fields) == 0
    return is_complete, missing_fields


async def create_user_profile(user_id: str, profile_data: dict):
    """
    Create user profile with personal data for calorie calculation
    
    Args:
        user_id: User UUID from database
        profile_data: Dictionary with profile fields (age, gender, height_cm, weight_kg, activity_level, goal)
        
    Returns:
        Created profile data
    """
    logger.info(f"Creating profile for user {user_id}: {profile_data}")
    
    # Calculate daily calories target if we have enough data
    if all(key in profile_data for key in ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']):
        try:
            daily_calories = calculate_daily_calories(profile_data)
            profile_data['daily_calories_target'] = daily_calories
            logger.info(f"Calculated daily calories for user {user_id}: {daily_calories}")
        except ValueError as e:
            logger.error(f"Error calculating daily calories for user {user_id}: {e}")
            # Don't include calories in profile if calculation failed
    
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
        
    Returns:
        Updated profile data
    """
    logger.info(f"Updating profile for user {user_id}: {profile_data}")
    
    # Calculate daily calories target if we have enough data
    if all(key in profile_data for key in ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']):
        try:
            daily_calories = calculate_daily_calories(profile_data)
            profile_data['daily_calories_target'] = daily_calories
            logger.info(f"Calculated daily calories for user {user_id}: {daily_calories}")
        except ValueError as e:
            logger.error(f"Error calculating daily calories for user {user_id}: {e}")
            # Don't include calories in profile if calculation failed
    
    updated = supabase.table("user_profiles").update(profile_data).eq("user_id", user_id).execute().data[0]
    logger.info(f"Profile updated for user {user_id}: {updated}")
    return updated


async def create_or_update_profile(user_id: str, profile_data: dict):
    """
    Create new profile or update existing one
    
    Args:
        user_id: User UUID from database
        profile_data: Dictionary with profile fields
        
    Returns:
        Tuple of (profile_data, was_created)
        - profile_data: Profile data
        - was_created: True if created, False if updated
    """
    logger.info(f"Create or update profile for user {user_id}")
    
    # Check if profile exists
    existing_profile = await get_user_profile(user_id)
    
    if existing_profile:
        # Merge new data with existing profile data
        merged_data = existing_profile.copy()
        merged_data.update(profile_data)
        # Remove internal fields that shouldn't be updated
        merged_data.pop('id', None)
        merged_data.pop('user_id', None)
        merged_data.pop('created_at', None)
        merged_data.pop('updated_at', None)
        
        logger.info(f"Merging profile data for user {user_id}: existing={existing_profile}, new={profile_data}, merged={merged_data}")
        
        # Update existing profile with merged data
        updated_profile = await update_user_profile(user_id, merged_data)
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
            logger.info(f"Processing kbzhu data: {kbzhu}")
            
            calories = float(kbzhu.get('calories', 0))
            protein = float(kbzhu.get('proteins', 0))  # Changed from 'protein' to 'proteins'
            fats = float(kbzhu.get('fats', 0))
            carbs = float(kbzhu.get('carbohydrates', 0))  # Changed from 'carbs' to 'carbohydrates'
            
            logger.info(f"Extracted values - calories: {calories}, protein: {protein}, fats: {fats}, carbs: {carbs}")
            
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
    
    logger.info(f"Daily summary for user {user_id} on {date}: {result}")
    return result


async def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """
    Calculate Body Mass Index (BMI)
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        
    Returns:
        BMI value
        
    Raises:
        ValueError: If height or weight are invalid
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive values")
    
    height_m = height_cm / 100  # Convert to meters
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


async def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category based on BMI value
    
    Args:
        bmi: BMI value
        
    Returns:
        BMI category string
    """
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"


async def calculate_water_needs(weight_kg: float, activity_level: str = "moderately_active") -> float:
    """
    Calculate daily water needs based on weight and activity level
    
    Args:
        weight_kg: Weight in kilograms
        activity_level: Activity level
        
    Returns:
        Daily water needs in liters
    """
    # Base water needs: 35ml per kg of body weight
    base_water = weight_kg * 35 / 1000  # Convert to liters
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.0,
        'lightly_active': 1.1,
        'moderately_active': 1.2,
        'very_active': 1.3,
        'extremely_active': 1.4
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    daily_water = base_water * multiplier
    
    return round(daily_water, 1)