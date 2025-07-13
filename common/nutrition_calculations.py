"""
Advanced nutrition calculations for c0r.ai
Contains formulas for BMI, ideal weight, water needs, macro distribution, etc.
"""

import math
from typing import Dict, Any, List, Tuple


def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """
    Calculate BMI and determine category
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
    Returns:
        Dict with BMI value and category
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "underweight"
        emoji = "⬇️"
        description = "Below ideal range"
        motivation = "Let's focus on healthy weight gain together! 🌱 Every nutritious meal is a step forward!"
    elif bmi < 25:
        category = "normal"
        emoji = "✅"
        description = "Healthy weight range"
        motivation = "Fantastic! You're in the ideal range! 🎉 Keep up the great work maintaining your health!"
    elif bmi < 30:
        category = "overweight"
        emoji = "⚠️"
        description = "Above ideal range"
        motivation = "You're taking the right steps by tracking! 💪 Small changes lead to big results!"
    else:
        category = "obese"
        emoji = "🔴"
        description = "Well above ideal range"
        motivation = "Every healthy choice counts! 🌟 You're already on the path to positive change!"
    
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


def calculate_metabolic_age(age: int, gender: str, weight_kg: float, height_cm: float, activity_level: str) -> Dict[str, Any]:
    """
    Estimate metabolic age based on BMR and lifestyle factors
    
    Args:
        age: Chronological age
        gender: 'male' or 'female'
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        activity_level: Activity level string
        
    Returns:
        Dict with metabolic age estimation
    """
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
    bmi_data = calculate_bmi(weight_kg, height_cm)
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
        description = "Your metabolism is younger than your age!"
        motivation = "Amazing! Your healthy lifestyle is paying off! Keep doing what you're doing! 🚀"
    elif difference >= 2:
        status = "older"
        emoji = "⚠️"
        description = "Your metabolism is older than your age"
        motivation = "No worries! With consistent nutrition and activity, you can improve this! 💪 You're on the right track!"
    else:
        status = "normal"
        emoji = "✅"
        description = "Your metabolism matches your age"
        motivation = "Perfect balance! You're maintaining great metabolic health! 🎯 Keep it up!"
    
    return {
        "metabolic_age": round(metabolic_age),
        "chronological_age": age,
        "difference": round(difference, 1),
        "status": status,
        "emoji": emoji,
        "description": description,
        "motivation": motivation
    }


def calculate_meal_portions(calories: int, meals_per_day: int = 3) -> Dict[str, Any]:
    """
    Calculate portion sizes for meals throughout the day
    
    Args:
        calories: Daily calorie target
        meals_per_day: Number of meals per day
        
    Returns:
        Dict with meal portion breakdowns
    """
    if meals_per_day == 3:
        # Breakfast: 25%, Lunch: 40%, Dinner: 35%
        portions = [0.25, 0.40, 0.35]
        meal_names = ["Breakfast", "Lunch", "Dinner"]
    elif meals_per_day == 5:
        # Breakfast: 20%, Snack: 10%, Lunch: 30%, Snack: 10%, Dinner: 30%
        portions = [0.20, 0.10, 0.30, 0.10, 0.30]
        meal_names = ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"]
    else:
        # Equal portions
        portion_size = 1.0 / meals_per_day
        portions = [portion_size] * meals_per_day
        meal_names = [f"Meal {i+1}" for i in range(meals_per_day)]
    
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


def get_nutrition_recommendations(profile: Dict, recent_logs: List[Dict]) -> List[str]:
    """
    Generate nutrition recommendations based on profile and recent logs
    
    Args:
        profile: User profile data
        recent_logs: Recent nutrition logs
        
    Returns:
        List of personalized recommendations
    """
    recommendations = []
    
    # BMI-based recommendations
    if 'weight_kg' in profile and 'height_cm' in profile:
        bmi_data = calculate_bmi(profile['weight_kg'], profile['height_cm'])
        if bmi_data['category'] == 'underweight':
            recommendations.append("🍽️ Let's build healthy weight together! Focus on nutrient-rich foods like nuts, avocados, and wholesome meals")
        elif bmi_data['category'] == 'overweight' or bmi_data['category'] == 'obese':
            recommendations.append("🥗 You're on the right path! Prioritize colorful vegetables, lean proteins, and feel-good whole grains")
        else:  # normal weight
            recommendations.append("🎉 You're maintaining great health! Keep enjoying balanced, nutritious meals")
    
    # Activity-based recommendations
    if profile.get('activity_level') in ['very_active', 'extremely_active']:
        recommendations.append("💪 Amazing dedication to fitness! Boost your protein to 1.6-2.2g per kg for optimal recovery")
        recommendations.append("🍌 Fuel your workouts! Try post-exercise carbs within 30 minutes for best results")
    elif profile.get('activity_level') in ['sedentary', 'lightly_active']:
        recommendations.append("🚶‍♀️ Every step counts! Even light daily walks can boost your metabolism and mood")
    
    # Goal-based recommendations
    if profile.get('goal') == 'lose_weight':
        recommendations.append("⏰ Smart strategy: Try eating your heartiest meal earlier when your metabolism is highest")
        recommendations.append("🥛 Protein is your friend! Include it in every meal to preserve muscle while losing fat")
    elif profile.get('goal') == 'gain_weight':
        recommendations.append("🍞 Building healthy weight! Include energizing carbs like oats, quinoa, and sweet potatoes")
        recommendations.append("🥜 Power up with healthy fats! Nuts, seeds, and olive oil add nutritious calories")
    else:  # maintain_weight
        recommendations.append("🎯 Maintaining beautifully! Focus on consistent, enjoyable eating patterns")
    
    # Water recommendations
    if 'weight_kg' in profile:
        water_data = calculate_water_needs(profile['weight_kg'], profile.get('activity_level', 'sedentary'))
        recommendations.append(f"💧 Stay hydrated for success! Aim for {water_data['liters']}L daily ({water_data['glasses']} glasses)")
    
    # Add motivational "wins" - positive reinforcement
    wins = [
        "🌟 You're taking control of your health by tracking nutrition!",
        "🎉 Every food analysis brings you closer to your goals!",
        "💪 Small consistent steps lead to amazing transformations!",
        "🚀 You're investing in the most important asset - your health!",
        "✨ Progress, not perfection - you're doing great!"
    ]
    
    # Add a random win to keep it fresh
    import random
    recommendations.append(random.choice(wins))
    
    return recommendations 