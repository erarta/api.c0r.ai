from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import base64
import json
from openai import OpenAI
from loguru import logger
from common.routes import Routes

app = FastAPI()

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None
    logger.warning("OpenAI API key not provided")

@app.get(Routes.ML_HEALTH)
async def health():
    return {"status": "ok", "service": "ml.c0r.ai"}

async def analyze_food_with_openai(image_bytes: bytes, user_language: str = "en") -> dict:
    """
    Analyze food image using OpenAI Vision API
    Returns KBZHU data in expected format
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
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
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
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
            max_tokens=300,
            temperature=0.1
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
            
            # Extract total nutrition data
            if "total_nutrition" in response_data:
                kbzhu_data = response_data["total_nutrition"]
            else:
                # Fallback to old format if present
                kbzhu_data = response_data
            
            # Validate required fields
            required_fields = ["calories", "proteins", "fats", "carbohydrates"]
            for field in required_fields:
                if field not in kbzhu_data:
                    raise ValueError(f"Missing field: {field}")
                # Ensure values are numbers
                kbzhu_data[field] = float(kbzhu_data[field])
            
            # Return both detailed breakdown and KBZHU summary
            result = {
                "kbzhu": kbzhu_data
            }
            
            # Add food items breakdown if available
            if "food_items" in response_data:
                result["food_items"] = response_data["food_items"]
            
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
async def analyze_file(
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
        
        # Analyze with OpenAI (default provider)
        if provider == "openai" or not provider:
            analysis_result = await analyze_food_with_openai(image_bytes, user_language)
        elif provider == "gemini":
            # For now, only OpenAI is supported
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")
        
        logger.info(f"Analysis complete for user {telegram_user_id}: {analysis_result}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post(Routes.ML_GENERATE_RECIPE)
async def generate_recipe(
    image_url: str = Form(...),
    telegram_user_id: str = Form(...),
    user_context: str = Form(...)
):
    """
    Generate recipe from food image using OpenAI GPT-4o
    """
    try:
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