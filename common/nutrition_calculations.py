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
    # Try to import i18n, fallback to hardcoded text if not available
    try:
        from api.c0r.ai.app.handlers.i18n import i18n
        use_i18n = True
    except ImportError:
        # Fallback for test environment
        use_i18n = False
        # Fallback text for tests
        fallback_texts = {
            'en': {
                'bmi_underweight': 'Below ideal range',
                'bmi_normal': 'Healthy weight range',
                'bmi_overweight': 'Above ideal range',
                'bmi_obese': 'Significantly above ideal range',
                'bmi_motivation_underweight': "Let's build healthy weight together! 🌱 Every nutritious meal is a step forward!",
                'bmi_motivation_normal': "Fantastic! You're in the ideal range! 🎉 Keep up the great work maintaining your health!",
                'bmi_motivation_overweight': "You're making great progress! 🌟 Focus on sustainable, healthy habits!",
                'bmi_motivation_obese': "You've got this! 💪 Every small step toward health counts! Keep going!"
            },
            'ru': {
                'bmi_underweight': 'Ниже идеального диапазона',
                'bmi_normal': 'Здоровый диапазон веса',
                'bmi_overweight': 'Выше идеального диапазона',
                'bmi_obese': 'Значительно выше идеального диапазона',
                'bmi_motivation_underweight': "Давайте вместе набирать здоровый вес! 🌱 Каждый питательный прием пищи — шаг вперед!",
                'bmi_motivation_normal': "Фантастика! Вы в идеальном диапазоне! 🎉 Просто отлично поддерживаете здоровье!",
                'bmi_motivation_overweight': "Вы отлично прогрессируете! 🌟 Сосредоточьтесь на устойчивых, здоровых привычках!",
                'bmi_motivation_obese': "У вас все получится! 💪 Каждый маленький шаг к здоровью имеет значение! Продолжайте!"
            }
        }
    
    height_m = height_cm / 100
    if height_m <= 0:
        # Return default values for invalid height
        return {
            'bmi': 0.0,
            'category': 'unknown',
            'emoji': '❓',
            'description': 'Invalid height',
            'motivation': 'Please provide a valid height'
        }
    
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "underweight"
        emoji = "⬇️"
        if use_i18n:
            description = i18n.get_text("bmi_underweight", language)
            motivation = i18n.get_text("bmi_motivation_underweight", language)
        else:
            description = fallback_texts[language]['bmi_underweight']
            motivation = fallback_texts[language]['bmi_motivation_underweight']
    elif bmi < 25:
        category = "normal"
        emoji = "✅"
        if use_i18n:
            description = i18n.get_text("bmi_normal", language)
            motivation = i18n.get_text("bmi_motivation_normal", language)
        else:
            description = fallback_texts[language]['bmi_normal']
            motivation = fallback_texts[language]['bmi_motivation_normal']
    elif bmi < 30:
        category = "overweight"
        emoji = "⬆️"
        if use_i18n:
            description = i18n.get_text("bmi_overweight", language)
            motivation = i18n.get_text("bmi_motivation_overweight", language)
        else:
            description = fallback_texts[language]['bmi_overweight']
            motivation = fallback_texts[language]['bmi_motivation_overweight']
    else:
        category = "obese"
        emoji = "⚠️"
        if use_i18n:
            description = i18n.get_text("bmi_obese", language)
            motivation = i18n.get_text("bmi_motivation_obese", language)
        else:
            description = fallback_texts[language]['bmi_obese']
            motivation = fallback_texts[language]['bmi_motivation_obese']
    
    return {
        'bmi': round(bmi, 1),
        'category': category,
        'emoji': emoji,
        'description': description,
        'motivation': motivation
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
    
    # Convert to grams (protein: 4 kcal/g, fat: 9 kcal/g, carbs: 4 kcal/g)
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
    # Try to import i18n, fallback to hardcoded text if not available
    try:
        from api.c0r.ai.app.handlers.i18n import i18n
        use_i18n = True
    except ImportError:
        # Fallback for test environment
        use_i18n = False
        # Fallback text for tests
        fallback_texts = {
            'en': {
                'metabolic_age_match': 'Your metabolism matches your age',
                'metabolic_age_younger': 'Your metabolism is younger than your age',
                'metabolic_age_older': 'Your metabolism is older than your age',
                'metabolic_motivation_match': 'Perfect balance! You\'re maintaining great metabolic health! 🎯 Keep it up!',
                'metabolic_motivation_younger': 'Excellent! Your metabolism is thriving! 🌟 Keep up the great lifestyle!',
                'metabolic_motivation_older': 'You\'re making positive changes! 💪 Every healthy choice improves your metabolism!'
            },
            'ru': {
                'metabolic_age_match': 'Ваш метаболизм соответствует возрасту',
                'metabolic_age_younger': 'Ваш метаболизм моложе вашего возраста',
                'metabolic_age_older': 'Ваш метаболизм старше вашего возраста',
                'metabolic_motivation_match': 'Идеальный баланс! Вы отлично поддерживаете метаболическое здоровье! 🎯 Продолжайте!',
                'metabolic_motivation_younger': 'Отлично! Ваш метаболизм процветает! 🌟 Продолжайте отличный образ жизни!',
                'metabolic_motivation_older': 'Вы делаете позитивные изменения! 💪 Каждый здоровый выбор улучшает ваш метаболизм!'
            }
        }
    
    # Calculate BMR using Mifflin-St Jeor
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    }
    
    # Get activity multiplier
    activity_key = activity_level.lower().replace(' ', '_')
    multiplier = activity_multipliers.get(activity_key, 1.55)
    
    # Calculate TDEE
    tdee = bmr * multiplier
    
    # Estimate metabolic age based on TDEE vs expected
    expected_tdee = bmr * 1.55  # Moderate activity baseline
    
    if abs(tdee - expected_tdee) < 100:
        # Metabolism matches age
        metabolic_age = age
        emoji = "✅"
        if use_i18n:
            description = i18n.get_text("metabolic_age_match", language)
            motivation = i18n.get_text("metabolic_motivation_match", language)
        else:
            description = fallback_texts[language]['metabolic_age_match']
            motivation = fallback_texts[language]['metabolic_motivation_match']
    elif tdee > expected_tdee:
        # Younger metabolism
        metabolic_age = max(18, age - 5)
        emoji = "🌟"
        if use_i18n:
            description = i18n.get_text("metabolic_age_younger", language)
            motivation = i18n.get_text("metabolic_motivation_younger", language)
        else:
            description = fallback_texts[language]['metabolic_age_younger']
            motivation = fallback_texts[language]['metabolic_motivation_younger']
    else:
        # Older metabolism
        metabolic_age = age + 5
        emoji = "💪"
        if use_i18n:
            description = i18n.get_text("metabolic_age_older", language)
            motivation = i18n.get_text("metabolic_motivation_older", language)
        else:
            description = fallback_texts[language]['metabolic_age_older']
            motivation = fallback_texts[language]['metabolic_motivation_older']
    
    return {
        'metabolic_age': metabolic_age,
        'emoji': emoji,
        'description': description,
        'motivation': motivation
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
    # Try to import i18n, fallback to hardcoded text if not available
    try:
        from api.c0r.ai.app.handlers.i18n import i18n
        use_i18n = True
    except ImportError:
        # Fallback for test environment
        use_i18n = False
        # Fallback text for tests
        fallback_texts = {
            'en': {
                'meal_breakfast': 'Breakfast',
                'meal_lunch': 'Lunch',
                'meal_dinner': 'Dinner',
                'meal_snack': 'Snack'
            },
            'ru': {
                'meal_breakfast': 'Завтрак',
                'meal_lunch': 'Обед',
                'meal_dinner': 'Ужин',
                'meal_snack': 'Перекус'
            }
        }
    
    if meals_per_day == 3:
        # Breakfast: 25%, Lunch: 40%, Dinner: 35%
        portions = [0.25, 0.40, 0.35]
        if use_i18n:
            meal_names = [
                i18n.get_text("meal_breakfast", language),
                i18n.get_text("meal_lunch", language),
                i18n.get_text("meal_dinner", language)
            ]
        else:
            meal_names = [
                fallback_texts[language]['meal_breakfast'],
                fallback_texts[language]['meal_lunch'],
                fallback_texts[language]['meal_dinner']
            ]
    elif meals_per_day == 4:
        # Breakfast: 25%, Lunch: 30%, Dinner: 30%, Snack: 15%
        portions = [0.25, 0.30, 0.30, 0.15]
        if use_i18n:
            meal_names = [
                i18n.get_text("meal_breakfast", language),
                i18n.get_text("meal_lunch", language),
                i18n.get_text("meal_dinner", language),
                i18n.get_text("meal_snack", language)
            ]
        else:
            meal_names = [
                fallback_texts[language]['meal_breakfast'],
                fallback_texts[language]['meal_lunch'],
                fallback_texts[language]['meal_dinner'],
                fallback_texts[language]['meal_snack']
            ]
    else:
        # Default to 3 meals
        portions = [0.25, 0.40, 0.35]
        if use_i18n:
            meal_names = [
                i18n.get_text("meal_breakfast", language),
                i18n.get_text("meal_lunch", language),
                i18n.get_text("meal_dinner", language)
            ]
        else:
            meal_names = [
                fallback_texts[language]['meal_breakfast'],
                fallback_texts[language]['meal_lunch'],
                fallback_texts[language]['meal_dinner']
            ]
    
    meal_breakdown = []
    for i, (portion, meal_name) in enumerate(zip(portions, meal_names)):
        meal_calories = int(calories * portion)
        meal_breakdown.append({
            'name': meal_name,
            'calories': meal_calories,
            'percentage': int(portion * 100)
        })
    
    return {
        'meals': meal_breakdown,
        'total_calories': calories,
        'meals_per_day': meals_per_day
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
    # Try to import i18n, fallback to hardcoded text if not available
    try:
        from api.c0r.ai.app.handlers.i18n import i18n
        use_i18n = True
    except ImportError:
        # Fallback for test environment
        use_i18n = False
        # Fallback text for tests
        fallback_texts = {
            'en': {
                'recommendation_underweight': 'Focus on nutrient-dense foods to build healthy weight',
                'recommendation_normal': 'You\'re maintaining great health! Keep enjoying balanced, nutritious meals',
                'recommendation_overweight': 'Focus on portion control and regular physical activity',
                'recommendation_obese': 'Start with small, sustainable changes to build healthy habits',
                'recommendation_water': 'Stay hydrated for success! Aim for adequate water intake daily',
                'recommendation_protein': 'Include lean protein sources in your meals',
                'recommendation_consistency': 'Small consistent steps lead to amazing transformations!'
            },
            'ru': {
                'recommendation_underweight': 'Сосредоточьтесь на питательных продуктах для набора здорового веса',
                'recommendation_normal': 'Вы отлично поддерживаете здоровье! Продолжайте наслаждаться сбалансированным питанием',
                'recommendation_overweight': 'Сосредоточьтесь на контроле порций и регулярной физической активности',
                'recommendation_obese': 'Начните с небольших, устойчивых изменений для формирования здоровых привычек',
                'recommendation_water': 'Оставайтесь гидратированными для успеха! Стремитесь к адекватному потреблению воды',
                'recommendation_protein': 'Включайте нежирные источники белка в приемы пищи',
                'recommendation_consistency': 'Маленькие последовательные шаги приводят к удивительным трансформациям!'
            }
        }
    
    recommendations = []
    
    # BMI-based recommendations
    if 'weight_kg' in profile and 'height_cm' in profile:
        bmi_data = calculate_bmi(profile['weight_kg'], profile['height_cm'], language)
        if bmi_data['category'] == 'underweight':
            if use_i18n:
                recommendations.append(i18n.get_text("recommendation_underweight", language))
            else:
                recommendations.append(fallback_texts[language]['recommendation_underweight'])
        elif bmi_data['category'] == 'normal':
            if use_i18n:
                recommendations.append(i18n.get_text("recommendation_normal", language))
            else:
                recommendations.append(fallback_texts[language]['recommendation_normal'])
        elif bmi_data['category'] == 'overweight':
            if use_i18n:
                recommendations.append(i18n.get_text("recommendation_overweight", language))
            else:
                recommendations.append(fallback_texts[language]['recommendation_overweight'])
        else:  # obese
            if use_i18n:
                recommendations.append(i18n.get_text("recommendation_obese", language))
            else:
                recommendations.append(fallback_texts[language]['recommendation_obese'])
    
    # Water intake recommendation
    if use_i18n:
        recommendations.append(i18n.get_text("recommendation_water", language))
    else:
        recommendations.append(fallback_texts[language]['recommendation_water'])
    
    # Protein recommendation
    if use_i18n:
        recommendations.append(i18n.get_text("recommendation_protein", language))
    else:
        recommendations.append(fallback_texts[language]['recommendation_protein'])
    
    # Consistency recommendation
    if use_i18n:
        recommendations.append(i18n.get_text("recommendation_consistency", language))
    else:
        recommendations.append(fallback_texts[language]['recommendation_consistency'])
    
    return recommendations 