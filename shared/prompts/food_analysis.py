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
        Проанализируйте блюдо на фотографии и определите ВСЕ продукты питания максимально точно.
        
        ⚠️ КРИТИЧЕСКИ ВАЖНО - РАЗЛИЧЕНИЕ ЯИЦ И МОЦАРЕЛЛЫ ⚠️
        
        НА ЭТОМ ФОТО ТОЧНО ЕСТЬ ВАРЕНЫЕ ЯЙЦА, НЕ МОЦАРЕЛЛА!
        
        АБСОЛЮТНЫЕ ПРАВИЛА РАСПОЗНАВАНИЯ:
        1. ВАРЕНЫЕ ЯЙЦА: 
           - Белые овальные половинки с ЖЕЛТЫМ ЖЕЛТКОМ в центре
           - Размер ~5-7 см (как яйцо)
           - Матовая поверхность
           - Разрезанные пополам
           - ВИДИМЫЙ ЖЕЛТОК внутри
           
        2. МОЦАРЕЛЛА:
           - Идеально круглые шарики БЕЗ желтка
           - Размер ~1-2 см (маленькие шарики)
           - Глянцевая поверхность
           - Цельные шарики
           - НЕТ ЖЕЛТКА ВНУТРИ
           
        3. ПРОВЕРКА:
           - Видите белые овальные объекты размером с яйцо? → ПРОВЕРЬ ЕСТЬ ЛИ ЖЕЛТОК
           - Есть желтый желток в центре? → ЭТО ВАРЕНЫЕ ЯЙЦА 🥚
           - Нет желтка, но круглые шарики? → ЭТО МОЦАРЕЛЛА 🧀
           
        ⛔ ЗАПРЕЩЕНО НАЗЫВАТЬ ВАРЕНЫЕ ЯЙЦА МОЦАРЕЛЛОЙ! ⛔
        
        Верните JSON с полями:
        - regional_analysis: {detected_cuisine_type, dish_identification, regional_match_confidence}
        - food_items: [{name, weight_grams, calories, emoji, health_benefits}]
        - total_nutrition: {calories, proteins, fats, carbohydrates}
        - nutrition_analysis: {health_score, positive_aspects, improvement_suggestions}
        - motivation_message: строка
        
        ВАЖНО: dish_identification должно быть конкретным названием блюда (например, "салат с яйцами и лососем"), а не "Analyzed Dish"!
        """
    else:
        return """
        Analyze the dish in the photo and identify ALL food products as accurately as possible.
        
        ⚠️ CRITICAL - DISTINGUISHING EGGS FROM MOZZARELLA ⚠️
        
        THIS PHOTO DEFINITELY HAS BOILED EGGS, NOT MOZZARELLA!
        
        ABSOLUTE RECOGNITION RULES:
        1. BOILED EGGS: 
           - White oval halves with YELLOW YOLK in center
           - Size ~5-7 cm (egg-sized)
           - Matte surface
           - Cut in half
           - VISIBLE YOLK inside
           
        2. MOZZARELLA:
           - Perfectly round balls WITHOUT yolk
           - Size ~1-2 cm (small balls)
           - Glossy surface
           - Whole balls
           - NO YOLK INSIDE
           
        3. VERIFICATION:
           - See white oval objects egg-sized? → CHECK IF THERE'S YOLK
           - Yellow yolk in center? → THESE ARE BOILED EGGS 🥚
           - No yolk, but round balls? → THESE ARE MOZZARELLA 🧀
           
        ⛔ FORBIDDEN TO CALL BOILED EGGS MOZZARELLA! ⛔
        
        Return JSON with fields:
        - regional_analysis: {detected_cuisine_type, dish_identification, regional_match_confidence}
        - food_items: [{name, weight_grams, calories, emoji, health_benefits}]
        - total_nutrition: {calories, proteins, fats, carbohydrates}
        - nutrition_analysis: {health_score, positive_aspects, improvement_suggestions}
        - motivation_message: string
        
        IMPORTANT: dish_identification should be a specific dish name (e.g., "salad with eggs and salmon"), not "Analyzed Dish"!
        """

def get_system_prompt() -> str:
    """
    Get the system prompt for food analysis
    
    Returns:
        System prompt string
    """
    return """You are an expert food recognition AI with advanced visual analysis capabilities. Your primary task is to accurately identify food items in images with precise attention to visual details like shape, color, texture, and size. Pay special attention to distinguishing between similar-looking foods (eggs vs cheese, different proteins, etc). Always prioritize accuracy over speed. Return only valid JSON format.""" 