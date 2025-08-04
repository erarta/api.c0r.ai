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
            Вы эксперт по пищевой ценности и распознаванию продуктов питания. Проанализируйте это изображение еды с максимальной точностью.

            КРИТИЧЕСКИ ВАЖНО: Очень внимательно определите каждый продукт. Обращайте особое внимание на:
            - Цвет (красный перец ≠ помидор, зеленый перец ≠ огурец, яйцо ≠ сыр)
            - Форму (круглая, овальная, длинная, сферическая)
            - Текстуру (гладкая, шероховатая, блестящая, пористая)
            - Размер и контекст
            - Поверхность (гладкая скорлупа яйца ≠ пористый сыр)

            ВАЖНО: Отвечайте ТОЛЬКО валидным JSON объектом без дополнительного текста.

            Задачи анализа:
            1. Точно определите ВСЕ продукты питания на изображении
            2. Определите региональную принадлежность блюда
            3. Рассчитайте вес каждого продукта в граммах
            4. Вычислите точную пищевую ценность
            5. Опишите КОНКРЕТНУЮ пользу каждого ингредиента
            6. Дайте общую оценку полезности блюда
            7. Предложите КОНКРЕТНЫЕ способы улучшения блюда

            Верните ТОЛЬКО этот JSON объект:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "название региональной кухни (например: Русская, Азиатская, Средиземноморская)",
                        "dish_identification": "название блюда (например: Бутерброд, Салат, Овощное рагу)",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "точное русское название продукта (например: красный болгарский перец, а НЕ помидор)",
                            "weight_grams": число_граммов,
                            "calories": число_калорий,
                            "emoji": "подходящий emoji для продукта (например: 🥚 для яйца, 🧀 для сыра, 🍅 для помидора)",
                            "health_benefits": "КОНКРЕТНАЯ польза этого продукта (например: 'Красный перец богат витамином С (120% дневной нормы), бета-каротином для здоровья глаз и капсаицином для ускорения метаболизма')"
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
                        "key_benefits": [
                            "КОНКРЕТНАЯ польза 1 (например: 'Высокое содержание белка (30г) поддерживает рост мышц')",
                            "КОНКРЕТНАЯ польза 2 (например: 'Омега-3 из тунца улучшают работу мозга')",
                            "КОНКРЕТНАЯ польза 3 (например: 'Клетчатка из салата улучшает пищеварение')"
                        ],
                        "recommendations": "КОНКРЕТНЫЕ способы улучшить блюдо для повышения рейтинга (например: 'Добавьте авокадо (+2 балла за полезные жиры), замените белый хлеб на цельнозерновой (+1 балл за клетчатку), добавьте помидоры черри (+1 балл за витамин К)')"
                    },
                    "motivation_message": "Позитивное мотивационное сообщение о правильном питании и отслеживании калорий"
                }
            }

            Примеры точных названий и их отличий:
            - 🥚 Яйцо: гладкая скорлупа, овальная форма, белый/коричневый цвет
            - 🧀 Сыр: пористая текстура, может быть разных цветов, мягкая консистенция
            - 🍅 Помидор: красный цвет, круглая форма, гладкая кожица
            - 🌶️ Красный перец: красный цвет, вытянутая форма, гладкая кожица
            - 🥒 Огурец: зеленый цвет, вытянутая форма, бугристая поверхность
            - 🥕 Морковь: оранжевый цвет, вытянутая форма, гладкая поверхность
            - 🥩 Куриная грудка: белое мясо, волокнистая текстура
            - 🐟 Лосось: розовое мясо, жирная текстура
            - 🍞 Хлеб: пористая текстура, может быть разных цветов
            - 🍚 Рис: мелкие белые зерна
            - 🥔 Картофель: коричневая кожица, белая мякоть
            
            ОБЯЗАТЕЛЬНО: Различайте похожие продукты по цвету, форме и текстуре!
            НЕ добавляйте никакого текста до или после JSON.
            """
        else:
            prompt = """
            You are an expert in nutritional analysis and food recognition. Analyze this food image with maximum accuracy.

            CRITICALLY IMPORTANT: Very carefully identify each food item. Pay special attention to:
            - Color (red bell pepper ≠ tomato, green pepper ≠ cucumber, egg ≠ cheese)
            - Shape (round, oval, elongated, spherical)
            - Texture (smooth, rough, shiny, porous)
            - Size and context
            - Surface (smooth eggshell ≠ porous cheese)

            IMPORTANT: Respond with ONLY a valid JSON object, no additional text.

            Analysis tasks:
            1. Accurately identify ALL food items in the image
            2. Determine regional dish origin
            3. Calculate weight of each item in grams
            4. Compute precise nutritional values
            5. Describe SPECIFIC health benefits of each ingredient
            6. Provide overall healthiness assessment
            7. Suggest SPECIFIC ways to improve the dish

            Return ONLY this JSON object:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "cuisine type (e.g., Mediterranean, Asian, American)",
                        "dish_identification": "dish name (e.g., Sandwich, Salad, Vegetable Stir-fry)",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "precise food name (e.g., red bell pepper, NOT tomato)",
                            "weight_grams": weight_number,
                            "calories": calorie_number,
                            "emoji": "appropriate emoji for the food item (e.g., 🥚 for egg, 🧀 for cheese, 🍅 for tomato)",
                            "health_benefits": "SPECIFIC health benefits of this product (e.g., 'Red bell pepper is rich in vitamin C (120% daily value), beta-carotene for eye health, and capsaicin to boost metabolism')"
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
                        "key_benefits": [
                            "SPECIFIC benefit 1 (e.g., 'High protein content (30g) supports muscle growth')",
                            "SPECIFIC benefit 2 (e.g., 'Omega-3 from tuna improves brain function')",
                            "SPECIFIC benefit 3 (e.g., 'Fiber from lettuce aids digestion')"
                        ],
                        "recommendations": "SPECIFIC ways to improve the dish for higher rating (e.g., 'Add avocado (+2 points for healthy fats), replace white bread with whole grain (+1 point for fiber), add cherry tomatoes (+1 point for vitamin K)')"
                    },
                    "motivation_message": "Positive motivational message about healthy eating and calorie tracking"
                }
            }

            Examples of precise names and their differences:
            - 🥚 Egg: smooth shell, oval shape, white/brown color
            - 🧀 Cheese: porous texture, can be different colors, soft consistency
            - 🍅 Tomato: red color, round shape, smooth skin
            - 🌶️ Red bell pepper: red color, elongated shape, smooth skin
            - 🥒 Cucumber: green color, elongated shape, bumpy surface
            - 🥕 Carrot: orange color, elongated shape, smooth surface
            - 🥩 Chicken breast: white meat, fibrous texture
            - 🐟 Salmon: pink meat, fatty texture
            - 🍞 Bread: porous texture, can be different colors
            - 🍚 Rice: small white grains
            - 🥔 Potato: brown skin, white flesh

            MANDATORY: Distinguish similar products by color, shape, and texture!
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