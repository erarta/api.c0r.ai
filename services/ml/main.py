import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
import base64
import json
import httpx
from openai import OpenAI
from loguru import logger
from common.routes import Routes
from shared.health import create_health_response
from shared.auth import require_internal_auth
from .config import get_model_config, validate_model_for_task

app = FastAPI()

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize OpenAI client with proxy support
if OPENAI_API_KEY:
    # Check for proxy settings
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    
    if http_proxy or https_proxy:
        logger.info(f"Using proxy: HTTP={http_proxy}, HTTPS={https_proxy}")
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(
                proxies={
                    "http://": http_proxy,
                    "https://": https_proxy
                } if http_proxy or https_proxy else None
            )
        )
    else:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized without proxy")
else:
    openai_client = None
    logger.warning("OpenAI API key not provided")

@app.get(Routes.ML_HEALTH)
async def health():
    """Comprehensive health check for ML service"""
    from shared.health import create_comprehensive_health_response
    
    return await create_comprehensive_health_response(
        service_name="ml",
        check_database=True,
        check_openai=True,
        additional_info={
            "openai_configured": bool(OPENAI_API_KEY),
            "gemini_configured": bool(GEMINI_API_KEY),
            "default_provider": "openai" if OPENAI_API_KEY else "none"
        }
    )

@app.get("/health")
async def health_alias():
    """Health check alias endpoint"""
    return await health()

async def analyze_food_with_openai(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
    """
    Analyze food image using OpenAI Vision API
    Returns KBZHU data in expected format
    
    Args:
        image_bytes: Image data to analyze
        user_language: User language preference
        use_premium_model: Whether to use premium model settings
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Get model configuration for analysis task
        config = get_model_config("analysis", use_premium_model)
        model = config["model"]
        max_tokens = config["max_tokens"]
        temperature = config["temperature"]
        
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
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {content}")
        
        # Try to parse JSON from response with improved handling
        try:
            # Clean up the response content
            content = content.strip()
            
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            # Try to extract JSON from text if it's mixed with other content
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            response_data = json.loads(content)
            
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
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.error(f"Raw OpenAI response content: {content}")
            
            # Try to extract basic nutrition info from text if JSON parsing failed
            # This is a fallback to provide some detailed info even when JSON fails
            fallback_food_items = []
            
            # Simple text parsing for common food items (basic fallback)
            import re
            
            # Look for food names and calories in the text
            food_patterns = [
                r'(\w+(?:\s+\w+)*)\s*\(([^)]+)\)\s*-?\s*(\d+)\s*(?:cal|ккал)',
                r'(\w+(?:\s+\w+)*)\s*:\s*(\d+)\s*(?:cal|ккал)',
                r'•\s*(\w+(?:\s+\w+)*)\s*\(([^)]+)\)\s*-?\s*(\d+)'
            ]
            
            for pattern in food_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 3:
                        name, weight, calories = match
                        fallback_food_items.append({
                            "name": name.strip(),
                            "weight": weight.strip(),
                            "calories": int(calories)
                        })
                    elif len(match) == 2:
                        name, calories = match
                        fallback_food_items.append({
                            "name": name.strip(),
                            "weight": "estimated portion",
                            "calories": int(calories)
                        })
            
            # Return enhanced fallback with food items if found
            result = {
                "kbzhu": {
                    "calories": 250,
                    "proteins": 15.0,
                    "fats": 8.0,
                    "carbohydrates": 30.0
                }
            }
            
            if fallback_food_items:
                result["food_items"] = fallback_food_items
                # Recalculate total calories from food items
                total_calories = sum(item["calories"] for item in fallback_food_items)
                if total_calories > 0:
                    result["kbzhu"]["calories"] = total_calories
            
            return result
            
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")

async def generate_recipe_with_openai(image_url: str, user_context: dict) -> dict:
    """
    Generate recipe from food image using OpenAI GPT-4o
    Returns recipe data with ingredients, instructions, and nutrition
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
    try:
        # Get user language
        user_language = user_context.get('language', 'en')
        has_profile = user_context.get('has_profile', False)
        
        # Build personalized context
        context_parts = []
        
        if has_profile:
            # Add profile information to context
            if user_context.get('dietary_preferences'):
                dietary_prefs = [pref for pref in user_context['dietary_preferences'] if pref != 'none']
                if dietary_prefs:
                    context_parts.append(f"Dietary preferences: {', '.join(dietary_prefs)}")
            
            if user_context.get('allergies'):
                allergies = [allergy for allergy in user_context['allergies'] if allergy != 'none']
                if allergies:
                    context_parts.append(f"Food allergies to avoid: {', '.join(allergies)}")
            
            if user_context.get('goal'):
                goal_map = {
                    'lose_weight': 'weight loss',
                    'maintain_weight': 'weight maintenance',
                    'gain_weight': 'weight gain'
                }
                goal = goal_map.get(user_context['goal'], user_context['goal'])
                context_parts.append(f"Fitness goal: {goal}")
            
            if user_context.get('daily_calories_target'):
                context_parts.append(f"Daily calorie target: {user_context['daily_calories_target']} calories")
        
        # Create personalized context string
        personal_context = "\n".join(context_parts) if context_parts else "No specific dietary requirements"
        
        # Create prompt for recipe generation based on user language
        if user_language == "ru":
            prompt = f"""
            Проанализируйте это изображение еды/ингредиентов и создайте персонализированный рецепт.

            ПЕРСОНАЛЬНЫЙ КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:
            {personal_context}

            Пожалуйста, создайте рецепт, который:
            1. Использует ингредиенты, видимые на изображении
            2. Соответствует диетическим предпочтениям пользователя
            3. Избегает указанных аллергенов
            4. Подходит для цели пользователя по фитнесу
            5. Включает точную информацию о питании

            Верните ТОЛЬКО JSON объект со следующей структурой:
            {{
                "name": "название рецепта",
                "description": "краткое описание блюда",
                "prep_time": "время подготовки (например, 15 минут)",
                "cook_time": "время приготовления (например, 30 минут)",
                "servings": "количество порций (например, 4)",
                "ingredients": [
                    "ингредиент 1 с количеством",
                    "ингредиент 2 с количеством"
                ],
                "instructions": [
                    "шаг 1 инструкции",
                    "шаг 2 инструкции"
                ],
                "nutrition": {{
                    "calories": число_калорий_на_порцию,
                    "protein": число_белков_в_граммах,
                    "carbs": число_углеводов_в_граммах,
                    "fat": число_жиров_в_граммах
                }}
            }}

            Убедитесь, что рецепт безопасен и подходит для указанных диетических ограничений.
            Все числовые значения должны быть числами (не строками).
            """
        else:
            prompt = f"""
            Analyze this food/ingredient image and create a personalized recipe.

            USER'S PERSONAL CONTEXT:
            {personal_context}

            Please create a recipe that:
            1. Uses the ingredients visible in the image
            2. Matches the user's dietary preferences
            3. Avoids specified allergens
            4. Suits the user's fitness goal
            5. Includes accurate nutritional information

            Return ONLY a JSON object with the following structure:
            {{
                "name": "recipe name",
                "description": "brief description of the dish",
                "prep_time": "preparation time (e.g., 15 minutes)",
                "cook_time": "cooking time (e.g., 30 minutes)",
                "servings": "number of servings (e.g., 4)",
                "ingredients": [
                    "ingredient 1 with quantity",
                    "ingredient 2 with quantity"
                ],
                "instructions": [
                    "step 1 instruction",
                    "step 2 instruction"
                ],
                "nutrition": {{
                    "calories": calories_per_serving_number,
                    "protein": protein_grams_number,
                    "carbs": carbs_grams_number,
                    "fat": fat_grams_number
                }}
            }}

            Ensure the recipe is safe and suitable for the specified dietary restrictions.
            All numeric values should be numbers (not strings).
            """
        
        # Call OpenAI Vision API for recipe generation
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Use full GPT-4o for better recipe generation
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,  # More tokens for detailed recipes
            temperature=0.3  # Slightly more creative for recipe generation
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI recipe response: {content}")
        
        # Try to parse JSON from response
        try:
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            recipe_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["name", "ingredients", "instructions"]
            for field in required_fields:
                if field not in recipe_data:
                    raise ValueError(f"Missing field: {field}")
            
            # Validate nutrition data if present
            if "nutrition" in recipe_data:
                nutrition = recipe_data["nutrition"]
                for nutrient in ["calories", "protein", "carbs", "fat"]:
                    if nutrient in nutrition:
                        nutrition[nutrient] = float(nutrition[nutrient])
            
            return recipe_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI recipe response: {e}")
            # Return fallback recipe based on user language
            if user_language == "ru":
                return {
                    "name": "Вкусный рецепт",
                    "description": "Аппетитное блюдо из ингредиентов с вашего фото",
                    "prep_time": "15 минут",
                    "cook_time": "30 минут",
                    "servings": "4",
                    "ingredients": ["Ингредиенты с вашего фото"],
                    "instructions": ["Подготовьте ингредиенты как показано", "Готовьте согласно вашим предпочтениям"],
                    "nutrition": {
                        "calories": 300,
                        "protein": 20,
                        "carbs": 25,
                        "fat": 12
                    }
                }
            else:
                return {
                    "name": "Delicious Recipe",
                    "description": "A tasty dish made from the ingredients in your photo",
                    "prep_time": "15 minutes",
                    "cook_time": "30 minutes",
                    "servings": "4",
                    "ingredients": ["Ingredients from your photo"],
                    "instructions": ["Prepare ingredients as shown", "Cook according to your preference"],
                    "nutrition": {
                        "calories": 300,
                        "protein": 20,
                        "carbs": 25,
                        "fat": 12
                    }
                }
            
    except Exception as e:
        logger.error(f"OpenAI recipe generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recipe generation failed: {str(e)}")

@app.post(Routes.ML_ANALYZE)
@require_internal_auth
async def analyze_file(
    request: Request,
    photo: UploadFile = File(...),
    telegram_user_id: str = Form(...),
    provider: str = Form(default="openai"),
    user_language: str = Form(default="en")
):
    """
    Analyze food image and return KBZHU data
    """
    try:
        logger.info(f"Analyzing photo for user {telegram_user_id} with provider {provider}")
        
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await photo.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Analyze with selected provider
        if provider == "openai" or not provider:
            try:
                analysis_result = await analyze_food_with_openai(image_bytes, user_language)
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}")
                # Fallback to Gemini if OpenAI fails
                if GEMINI_API_KEY:
                    logger.info("Falling back to Gemini for analysis")
                    from .gemini.client import analyze_food_with_gemini
                    analysis_result = await analyze_food_with_gemini(image_bytes, user_language)
                else:
                    raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")
        elif provider == "gemini":
            if not GEMINI_API_KEY:
                raise HTTPException(status_code=400, detail="Gemini API key not configured")
            from .gemini.client import analyze_food_with_gemini
            analysis_result = await analyze_food_with_gemini(image_bytes, user_language)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")
        
        logger.info(f"Analysis complete for user {telegram_user_id}: {analysis_result}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post(Routes.ML_GENERATE_RECIPE)
@require_internal_auth
async def generate_recipe(
    request: Request,
    image_url: str = Form(...),
    telegram_user_id: str = Form(...),
    user_context: str = Form(...)
):
    """
    Generate recipe from food image using OpenAI GPT-4o
    """
    try:
        logger.info(f"DEBUG: ML service received request:")
        logger.info(f"  - image_url: {image_url}")
        logger.info(f"  - telegram_user_id: {telegram_user_id}")
        logger.info(f"  - user_context: {user_context}")
        logger.info(f"Generating recipe for user {telegram_user_id}")
        
        # Parse user context JSON
        try:
            context_data = json.loads(user_context)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid user_context JSON")
        
        # Generate recipe with OpenAI
        recipe_result = await generate_recipe_with_openai(image_url, context_data)
        
        logger.info(f"Recipe generation complete for user {telegram_user_id}: {recipe_result['name']}")
        
        return recipe_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recipe generation error: {e}")
        raise HTTPException(status_code=500, detail="Recipe generation failed")