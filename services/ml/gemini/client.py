import os
import base64
import json
import httpx
from loguru import logger

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def analyze_food_with_gemini(image_bytes: bytes, user_language: str = "en") -> dict:
    """
    Analyze food image using Google Gemini Vision API
    Returns KBZHU data in expected format
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt for food analysis based on user language
        if user_language == "ru":
            prompt = """
            Проанализируйте это изображение еды и предоставьте подробную информацию о питании с региональным анализом.

            ВАЖНО: Отвечайте ТОЛЬКО валидным JSON объектом без дополнительного текста.

            Пожалуйста, предоставьте:
            1. Региональное распознавание блюда и его происхождение
            2. Список отдельных продуктов питания с их пользой
            3. Оцененный вес/размер порции для каждого продукта в граммах
            4. Калории для каждого отдельного продукта
            5. Общую сводку по питанию
            6. Анализ полезности и мотивационное сообщение

            Верните ТОЛЬКО этот JSON объект:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "название региональной кухни (например: Русская, Азиатская, Средиземноморская)",
                        "dish_identification": "название блюда (например: Бутерброд, Салат, Овсяная каша)",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "русское название продукта",
                            "weight_grams": число_граммов,
                            "calories": число_калорий,
                            "health_benefits": "краткое описание пользы этого продукта"
                        }
                    ],
                    "total_nutrition": {
                        "calories": общее_число_калорий,
                        "proteins": граммы_белков,
                        "fats": граммы_жиров,
                        "carbohydrates": граммы_углеводов
                    },
                    "nutritional_summary": {
                        "healthiness_rating": рейтинг_от_1_до_10,
                        "key_benefits": ["польза 1", "польза 2", "польза 3"],
                        "recommendations": "краткие рекомендации по питанию"
                    },
                    "motivation_message": "Позитивное мотивационное сообщение о правильном питании и отслеживании калорий"
                }
            }

            Примеры русских названий продуктов: рис, гречка, макароны, куриная грудка, говядина, лосось, картофель, морковь, капуста, яблоко, банан, хлеб, сыр, молоко, яйцо.
            Оцените реалистичные порции. Все числовые значения должны быть числами без кавычек.
            НЕ добавляйте никакого текста до или после JSON.
            """
        else:
            prompt = """
            Analyze this food image and provide detailed nutritional information with regional analysis.

            IMPORTANT: Respond with ONLY a valid JSON object, no additional text.

            Please provide:
            1. Regional dish recognition and origin
            2. List of individual food items with their health benefits
            3. Estimated weight/portion size for each item in grams
            4. Calories for each individual item
            5. Total nutritional summary
            6. Health analysis and motivational message

            Return ONLY this JSON object:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "cuisine type (e.g., Mediterranean, Asian, American)",
                        "dish_identification": "dish name (e.g., Sandwich, Salad, Oatmeal)",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "specific food name",
                            "weight_grams": weight_number,
                            "calories": calorie_number,
                            "health_benefits": "brief description of health benefits"
                        }
                    ],
                    "total_nutrition": {
                        "calories": total_calorie_number,
                        "proteins": protein_grams,
                        "fats": fat_grams,
                        "carbohydrates": carb_grams
                    },
                    "nutritional_summary": {
                        "healthiness_rating": rating_from_1_to_10,
                        "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
                        "recommendations": "brief nutrition recommendations"
                    },
                    "motivation_message": "Positive motivational message about healthy eating and calorie tracking"
                }
            }

            Examples of specific food names: rice, pasta, chicken breast, salmon, beef, potato, carrot, apple, bread, cheese, egg.
            Estimate realistic portion sizes. All numeric values must be numbers without quotes.
            DO NOT add any text before or after the JSON.
            """
        
        # Prepare request payload for Gemini
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 300
            }
        }
        
        # Call Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise Exception(f"Gemini API error: {response.status_code}")
            
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                raise Exception("Invalid response from Gemini API")
            
            # Parse JSON response
            try:
                response_data = json.loads(content)
                logger.info(f"Gemini analysis successful: {response_data}")
                
                # Check if we have the new analysis format
                if "analysis" in response_data:
                    # New format - return as is
                    return response_data
                else:
                    # Old format fallback - convert to new structure
                    kbzhu_data = response_data.get("total_nutrition", response_data)
                    
                    # Validate required fields
                    required_fields = ["calories", "proteins", "fats", "carbohydrates"]
                    for field in required_fields:
                        if field not in kbzhu_data:
                            raise ValueError(f"Missing field: {field}")
                        # Ensure values are numbers
                        kbzhu_data[field] = float(kbzhu_data[field])
                    
                    # Convert old format to new format structure
                    result = {
                        "analysis": {
                            "food_items": response_data.get("food_items", []),
                            "total_nutrition": kbzhu_data,
                            "motivation_message": "Keep tracking your nutrition!"
                        }
                    }
                    return result
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {content}")
                raise Exception(f"Invalid JSON response from Gemini: {e}")
                
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}")
        raise Exception(f"Gemini analysis failed: {str(e)}")

async def analyze_image_gemini(image_url: str) -> dict:
    # Legacy function - redirect to new implementation
    return await analyze_food_with_gemini(image_url.encode(), "en") 