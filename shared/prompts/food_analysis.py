"""
Shared food analysis prompts for different LLM providers
These prompts are optimized for accurate food recognition with emphasis on distinguishing similar items
"""

def get_food_analysis_prompt(user_language: str = "en") -> str:
    """
    Get the food analysis prompt for the specified language
    
    Args:
        user_language: Language code ('en' or 'ru')
        
    Returns:
        Formatted prompt string
    """
    if user_language == "ru":
        return """
        Проанализируйте блюдо на фотографии и определите ВСЕ продукты максимально точно.
        Требуется:
        - Точно назвать каждый продукт
        - Реалистично оценить вес каждой позиции в граммах
        - Рассчитать питание по каждому продукту и общий итог
        - Коротко пояснить пользу для здоровья

        Верните JSON с полями:
        - regional_analysis: {detected_cuisine_type, dish_identification, regional_match_confidence}
        - food_items: [{name, weight_grams, calories, emoji, health_benefits}]
        - total_nutrition: {calories, proteins, fats, carbohydrates}
        - nutrition_analysis: {health_score, positive_aspects, improvement_suggestions}
        - motivation_message: строка
        
        ВАЖНО: dish_identification должно быть конкретным названием блюда (например, "салат с лососем"), а не "Analyzed Dish"!
        """
    else:
        return """
        Analyze the dish in the photo and identify ALL food items as accurately as possible.
        Requirements:
        - Use precise names for each item
        - Estimate realistic weight in grams per item
        - Compute per-item nutrition and the total
        - Briefly explain health benefits

        Return JSON with fields:
        - regional_analysis: {detected_cuisine_type, dish_identification, regional_match_confidence}
        - food_items: [{name, weight_grams, calories, emoji, health_benefits}]
        - total_nutrition: {calories, proteins, fats, carbohydrates}
        - nutrition_analysis: {health_score, positive_aspects, improvement_suggestions}
        - motivation_message: string
        
        IMPORTANT: dish_identification should be a specific dish name (e.g., "salad with salmon"), not "Analyzed Dish"!
        """

def get_system_prompt() -> str:
    """
    Get the system prompt for food analysis
    
    Returns:
        System prompt string
    """
    return """You are an expert food recognition AI with advanced visual analysis capabilities. Your primary task is to accurately identify food items in images with precise attention to visual details like shape, color, texture, and size. Pay special attention to distinguishing between similar-looking foods (eggs vs cheese, different proteins, etc). Always prioritize accuracy over speed. Return only valid JSON format.""" 