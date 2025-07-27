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
            Проанализируйте это изображение еды и предоставьте подробную информацию о питании.

            ВАЖНО: Отвечайте ТОЛЬКО валидным JSON объектом без дополнительного текста.

            Пожалуйста, предоставьте:
            1. Список отдельных продуктов питания, видимых на изображении (используйте русские названия)
            2. Оцененный вес/размер порции для каждого продукта в граммах
            3. Калории для каждого отдельного продукта
            4. Общую сводку по питанию

            Верните ТОЛЬКО этот JSON объект:
            {
                "food_items": [
                    {
                        "name": "русское название продукта (например: гречка, куриная грудка, помидор)",
                        "weight": "вес в граммах (например: 100г, 150г)",
                        "calories": число_калорий
                    }
                ],
                "total_nutrition": {
                    "calories": общее_число_калорий,
                    "proteins": граммы_белков,
                    "fats": граммы_жиров,
                    "carbohydrates": граммы_углеводов
                }
            }

            Примеры русских названий продуктов: рис, гречка, макароны, куриная грудка, говядина, лосось, картофель, морковь, капуста, яблоко, банан, хлеб, сыр, молоко, яйцо.
            Оцените реалистичные порции. Все числовые значения должны быть числами без кавычек.
            НЕ добавляйте никакого текста до или после JSON.
            """
        else:
            prompt = """
            Analyze this food image and provide detailed nutritional information.

            IMPORTANT: Respond with ONLY a valid JSON object, no additional text.

            Please provide:
            1. List of individual food items visible in the image (use specific food names)
            2. Estimated weight/portion size for each item in grams
            3. Calories for each individual item
            4. Total nutritional summary

            Return ONLY this JSON object:
            {
                "food_items": [
                    {
                        "name": "specific food name (e.g., grilled chicken breast, brown rice, broccoli)",
                        "weight": "weight in grams (e.g., 100g, 150g)",
                        "calories": calorie_number
                    }
                ],
                "total_nutrition": {
                    "calories": total_calorie_number,
                    "proteins": protein_grams,
                    "fats": fat_grams,
                    "carbohydrates": carb_grams
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
                analysis_result = json.loads(content)
                logger.info(f"Gemini analysis successful: {analysis_result}")
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {content}")
                raise Exception(f"Invalid JSON response from Gemini: {e}")
                
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}")
        raise Exception(f"Gemini analysis failed: {str(e)}")

async def analyze_image_gemini(image_url: str) -> dict:
    # Legacy function - redirect to new implementation
    return await analyze_food_with_gemini(image_url.encode(), "en") 