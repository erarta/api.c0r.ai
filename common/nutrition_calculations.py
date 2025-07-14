"""
Advanced nutrition calculations for c0r.ai
Contains formulas for BMI, ideal weight, water needs, macro distribution, etc.
"""

import math
from typing import Dict, Any, List, Tuple


def calculate_bmi(weight_kg: float, height_cm: float, language: str = 'en') -> Dict[str, Any]:
    """
    Calculate BMI and determine category
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        language: Language code ('en' or 'ru')
        
    Returns:
        Dict with BMI value and category
    """
    # Import i18n here to avoid circular imports
    from api.c0r.ai.app.handlers.i18n import i18n
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "underweight"
        emoji = "⬇️"
        description = i18n.get_text("bmi_underweight", language)
        motivation = i18n.get_text("bmi_motivation_underweight", language)
    elif bmi < 25:
        category = "normal"
        emoji = "✅"
        description = i18n.get_text("bmi_normal", language)
        motivation = i18n.get_text("bmi_motivation_normal", language)
    elif bmi < 30:
        category = "overweight"
        emoji = "⚠️"
        description = i18n.get_text("bmi_overweight", language)
        motivation = i18n.get_text("bmi_motivation_overweight", language)
    else:
        category = "obese"
        emoji = "🔴"
        description = i18n.get_text("bmi_obese", language)
        motivation = i18n.get_text("bmi_motivation_obese", language)
    
    return {
        "bmi": round(bmi, 1),
        "category": category,
        "emoji": emoji,
        "description": description,
        "motivation": motivation
    }


def calculate_ideal_weight(height_cm: float, gender: str) -> Dict[str, Any]:
    """
    Calculate ideal weight using multiple formulas
    
    Args:
        height_cm: Height in centimeters
        gender: 'male' or 'female'
        
    Returns:
        Dict with ideal weight ranges
    """
    height_m = height_cm / 100
    
    # BMI-based ideal weight (BMI 20-25)
    ideal_min = 20 * (height_m ** 2)
    ideal_max = 25 * (height_m ** 2)
    
    # Broca formula (adjusted)
    if gender.lower() == 'male':
        broca = height_cm - 100 - ((height_cm - 150) / 4)
    else:
        broca = height_cm - 100 - ((height_cm - 150) / 2.5)
    
    return {
        "ideal_min": round(ideal_min, 1),
        "ideal_max": round(ideal_max, 1),
        "broca": round(broca, 1),
        "range": f"{round(ideal_min, 1)}-{round(ideal_max, 1)} kg"
    }


def calculate_water_needs(weight_kg: float, activity_level: str) -> Dict[str, Any]:
    """
    Calculate daily water needs based on weight and activity
    
    Args:
        weight_kg: Weight in kilograms
        activity_level: Activity level string
        
    Returns:
        Dict with water requirements
    """
    # Base water need: 35ml per kg of body weight
    base_water = weight_kg * 35
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.0,
        'lightly_active': 1.2,
        'moderately_active': 1.4,
        'very_active': 1.6,
        'extremely_active': 1.8
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.0)
    total_water = base_water * multiplier
    
    return {
        "base_ml": round(base_water),
        "total_ml": round(total_water),
        "liters": round(total_water / 1000, 1),
        "glasses": round(total_water / 250),  # 250ml per glass
        "activity_bonus": round(total_water - base_water)
    }


def calculate_macro_distribution(calories: int, goal: str) -> Dict[str, Any]:
    """
    Calculate optimal macro distribution based on goal
    
    Args:
        calories: Daily calorie target
        goal: User's goal (lose_weight, gain_weight, maintain_weight)
        
    Returns:
        Dict with macro breakdown
    """
    if goal == 'lose_weight':
        # Higher protein for muscle preservation
        protein_percent = 0.30
        fat_percent = 0.25
        carb_percent = 0.45
    elif goal == 'gain_weight':
        # Higher carbs for muscle building
        protein_percent = 0.25
        fat_percent = 0.25
        carb_percent = 0.50
    else:  # maintain_weight
        protein_percent = 0.25
        fat_percent = 0.30
        carb_percent = 0.45
    
    protein_calories = calories * protein_percent
    fat_calories = calories * fat_percent
    carb_calories = calories * carb_percent
    
    # Convert to grams (protein: 4 cal/g, fat: 9 cal/g, carbs: 4 cal/g)
    protein_grams = protein_calories / 4
    fat_grams = fat_calories / 9
    carb_grams = carb_calories / 4
    
    return {
        "protein": {
            "grams": round(protein_grams),
            "calories": round(protein_calories),
            "percent": round(protein_percent * 100)
        },
        "fat": {
            "grams": round(fat_grams),
            "calories": round(fat_calories),
            "percent": round(fat_percent * 100)
        },
        "carbs": {
            "grams": round(carb_grams),
            "calories": round(carb_calories),
            "percent": round(carb_percent * 100)
        }
    }


def calculate_metabolic_age(age: int, gender: str, weight_kg: float, height_cm: float, activity_level: str, language: str = 'en') -> Dict[str, Any]:
    """
    Estimate metabolic age based on BMR and lifestyle factors
    
    Args:
        age: Chronological age
        gender: 'male' or 'female'
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        activity_level: Activity level string
        language: Language code ('en' or 'ru')
        
    Returns:
        Dict with metabolic age estimation
    """
    # Import i18n here to avoid circular imports
    from api.c0r.ai.app.handlers.i18n import i18n
    
    # Calculate BMR using Mifflin-St Jeor
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity factor
    activity_factors = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    }
    
    activity_factor = activity_factors.get(activity_level.lower(), 1.2)
    
    # BMI factor
    bmi_data = calculate_bmi(weight_kg, height_cm, language)
    bmi = bmi_data['bmi']
    
    # Metabolic age estimation (simplified formula)
    # Higher BMI and lower activity = older metabolic age
    bmi_adjustment = 0 if 20 <= bmi <= 25 else (bmi - 22.5) * 0.5
    activity_adjustment = (1.55 - activity_factor) * 10
    
    metabolic_age = age + bmi_adjustment + activity_adjustment
    metabolic_age = max(18, min(80, metabolic_age))  # Reasonable bounds
    
    difference = metabolic_age - age
    
    if difference <= -2:
        status = "younger"
        emoji = "🌟"
        description = i18n.get_text("metabolic_younger", language)
        motivation = i18n.get_text("metabolic_motivation_younger", language)
    elif difference >= 2:
        status = "older"
        emoji = "⚠️"
        description = i18n.get_text("metabolic_older", language)
        motivation = i18n.get_text("metabolic_motivation_older", language)
    else:
        status = "normal"
        emoji = "✅"
        description = i18n.get_text("metabolic_normal", language)
        motivation = i18n.get_text("metabolic_motivation_normal", language)
    
    return {
        "metabolic_age": round(metabolic_age),
        "chronological_age": age,
        "difference": round(difference, 1),
        "status": status,
        "emoji": emoji,
        "description": description,
        "motivation": motivation
    }


def calculate_meal_portions(calories: int, meals_per_day: int = 3, language: str = 'en') -> Dict[str, Any]:
    """
    Calculate portion sizes for meals throughout the day
    
    Args:
        calories: Daily calorie target
        meals_per_day: Number of meals per day
        language: Language code ('en' or 'ru')
        
    Returns:
        Dict with meal portion breakdowns
    """
    # Import i18n here to avoid circular imports
    from api.c0r.ai.app.handlers.i18n import i18n
    
    if meals_per_day == 3:
        # Breakfast: 25%, Lunch: 40%, Dinner: 35%
        portions = [0.25, 0.40, 0.35]
        meal_names = [
            i18n.get_text("meal_breakfast", language),
            i18n.get_text("meal_lunch", language),
            i18n.get_text("meal_dinner", language)
        ]
    elif meals_per_day == 5:
        # Breakfast: 20%, Snack: 10%, Lunch: 30%, Snack: 10%, Dinner: 30%
        portions = [0.20, 0.10, 0.30, 0.10, 0.30]
        meal_names = [
            i18n.get_text("meal_breakfast", language),
            i18n.get_text("meal_morning_snack", language),
            i18n.get_text("meal_lunch", language),
            i18n.get_text("meal_afternoon_snack", language),
            i18n.get_text("meal_dinner", language)
        ]
    else:
        # Equal portions
        portion_size = 1.0 / meals_per_day
        portions = [portion_size] * meals_per_day
        meal_names = [i18n.get_text("meal_generic", language, number=i+1) for i in range(meals_per_day)]
    
    meal_breakdown = []
    for i, (name, portion) in enumerate(zip(meal_names, portions)):
        meal_calories = calories * portion
        meal_breakdown.append({
            "name": name,
            "calories": round(meal_calories),
            "percent": round(portion * 100)
        })
    
    return {
        "total_calories": calories,
        "meals_per_day": meals_per_day,
        "meal_breakdown": meal_breakdown
    }


def analyze_weekly_progress(daily_logs: List[Dict]) -> Dict[str, Any]:
    """
    Analyze weekly nutrition progress from daily logs
    
    Args:
        daily_logs: List of daily nutrition logs
        
    Returns:
        Dict with weekly analysis
    """
    if not daily_logs:
        return {"error": "No data available"}
    
    total_calories = sum(log.get('calories', 0) for log in daily_logs)
    days = len(daily_logs)
    
    avg_calories = total_calories / days if days > 0 else 0
    
    # Calculate consistency (how close to target each day)
    target_calories = daily_logs[0].get('target_calories', avg_calories)
    variances = [abs(log.get('calories', 0) - target_calories) for log in daily_logs]
    consistency_score = max(0, 100 - (sum(variances) / len(variances) / target_calories * 100))
    
    return {
        "days_logged": days,
        "total_calories": round(total_calories),
        "average_calories": round(avg_calories),
        "target_calories": round(target_calories),
        "consistency_score": round(consistency_score),
        "weekly_trend": "improving" if daily_logs[-1].get('calories', 0) > daily_logs[0].get('calories', 0) else "stable"
    }


def get_nutrition_recommendations(profile: Dict, recent_logs: List[Dict], language: str = 'en') -> List[str]:
    """
    Generate nutrition recommendations based on profile and recent logs
    
    Args:
        profile: User profile data
        recent_logs: Recent nutrition logs
        language: Language code ('en' or 'ru')
        
    Returns:
        List of personalized recommendations
    """
    # Import i18n here to avoid circular imports
    from api.c0r.ai.app.handlers.i18n import i18n
    
    recommendations = []
    
    # BMI-based recommendations
    if 'weight_kg' in profile and 'height_cm' in profile:
        bmi_data = calculate_bmi(profile['weight_kg'], profile['height_cm'], language)
        if bmi_data['category'] == 'underweight':
            recommendations.append(i18n.get_text("rec_underweight", language))
        elif bmi_data['category'] == 'overweight' or bmi_data['category'] == 'obese':
            recommendations.append(i18n.get_text("rec_overweight", language))
        else:  # normal weight
            recommendations.append(i18n.get_text("rec_normal_weight", language))
    
    # Activity-based recommendations
    if profile.get('activity_level') in ['very_active', 'extremely_active']:
        recommendations.append(i18n.get_text("rec_very_active_protein", language))
        recommendations.append(i18n.get_text("rec_very_active_carbs", language))
    elif profile.get('activity_level') in ['sedentary', 'lightly_active']:
        recommendations.append(i18n.get_text("rec_sedentary", language))
    
    # Goal-based recommendations
    if profile.get('goal') == 'lose_weight':
        recommendations.append(i18n.get_text("rec_lose_weight_timing", language))
        recommendations.append(i18n.get_text("rec_lose_weight_protein", language))
    elif profile.get('goal') == 'gain_weight':
        recommendations.append(i18n.get_text("rec_gain_weight_carbs", language))
        recommendations.append(i18n.get_text("rec_gain_weight_fats", language))
    else:  # maintain_weight
        recommendations.append(i18n.get_text("rec_maintain_weight", language))
    
    # Water recommendations
    if 'weight_kg' in profile:
        water_data = calculate_water_needs(profile['weight_kg'], profile.get('activity_level', 'sedentary'))
        recommendations.append(i18n.get_text("rec_water_hydration", language, liters=water_data['liters'], glasses=water_data['glasses']))
    
    # Add motivational "wins" - positive reinforcement
    wins = [
        i18n.get_text("rec_win_1", language),
        i18n.get_text("rec_win_2", language),
        i18n.get_text("rec_win_3", language),
        i18n.get_text("rec_win_4", language),
        i18n.get_text("rec_win_5", language)
    ]
    
    # Add a random win to keep it fresh
    import random
    recommendations.append(random.choice(wins))
    
    return recommendations 