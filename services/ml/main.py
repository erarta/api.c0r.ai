import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from collections import defaultdict, deque
import uuid
import time
import base64
import json
import httpx
from openai import OpenAI
from loguru import logger
from common.routes import Routes
from shared.health import create_health_response
from shared.auth import require_internal_auth
from .config import get_model_config, validate_model_for_task
from services.ml.core.providers.llm_factory import llm_factory
from services.ml.openfoodfacts_client import fetch_product_by_barcode, map_off_to_nutrition

# Environment and app configuration
ENV = os.getenv("ENV", "development").lower()

# Swagger/Docs exposure: enabled in non-production by default; use ENABLE_SWAGGER to override
_enable_swagger_env = os.getenv("ENABLE_SWAGGER")
ENABLE_SWAGGER = (
    (_enable_swagger_env or ("true" if ENV != "production" else "false")).lower() == "true"
)

docs_url = "/docs" if ENABLE_SWAGGER else None
openapi_url = "/openapi.json" if ENABLE_SWAGGER else None

app = FastAPI(docs_url=docs_url, openapi_url=openapi_url, redoc_url=None)

# CORS for mobile/web clients (locked down in production)
_default_origins = "*" if ENV != "production" else ""
_origins = os.getenv("CORS_ORIGINS", _default_origins)
origins = [o.strip() for o in _origins.split(",") if o.strip()]
if ENV == "production" and ("*" in origins or not origins):
    # Disable CORS by default in production unless explicitly allowed
    origins = []
    logger.warning(
        "CORS is disabled by default in production. Set CORS_ORIGINS to an allowlist if needed."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic request ID middleware for observability
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Lightweight per-IP rate limiter (internal endpoints still benefit from abuse protection)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
_request_history: dict[str, deque[float]] = defaultdict(deque)

def _rate_limit_ok(key: str) -> bool:
    now = time.time()
    window_seconds = 60.0
    dq = _request_history[key]
    while dq and (now - dq[0] > window_seconds):
        dq.popleft()
    if len(dq) >= RATE_LIMIT_PER_MINUTE:
        return False
    dq.append(now)
    return True

# Upload size guard
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "8"))
MAX_UPLOAD_BYTES = int(MAX_UPLOAD_MB * 1024 * 1024)

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

class DetectedBarcode(BaseModel):
    type: str
    value: str

class OcrBlock(BaseModel):
    text: str
    confidence: Optional[float] = None

class LabelAnalyzeResponse(BaseModel):
    language: str
    barcodes: List[DetectedBarcode] = Field(default_factory=list)
    ocr_text: str = ""
    ocr_blocks: List[OcrBlock] = Field(default_factory=list)
    parsed_nutrition: Optional[dict] = None
    notes: Optional[str] = None

async def _stub_detect_barcodes(image_bytes: bytes) -> List[DetectedBarcode]:
    # TODO (v0.2.0): integrate pyzbar/zxing. For v0.1.0, return empty.
    return []

async def _stub_ocr_text(image_bytes: bytes, lang: str) -> tuple[str, List[OcrBlock]]:
    # TODO: integrate pytesseract/easyocr; for now return empty
    return "", []

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
            "current_llm_provider": llm_factory.get_current_provider(),
            "available_providers": llm_factory.list_available_providers()
        }
    )

@app.get("/health")
async def health_alias():
    """Health check alias endpoint"""
    return await health()

@app.post(Routes.ML_LABEL_ANALYZE, response_model=LabelAnalyzeResponse)
@require_internal_auth
async def label_analyze(
    request: Request,
    photo: UploadFile = File(...),
    user_language: str = Form(default="en"),
):
    """
    Analyze packaging/label image. Skeleton only: returns OCR/barcodes stubs.
    """
    try:
        # Rate limiting (by client IP)
        client_ip = request.client.host if request.client else "unknown"
        if not _rate_limit_ok(f"label_analyze:{client_ip}"):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Content length early check (if present)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        image_bytes = await photo.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        barcodes = await _stub_detect_barcodes(image_bytes)
        ocr_text, ocr_blocks = await _stub_ocr_text(image_bytes, user_language)

        # If we have a barcode, try OpenFoodFacts as first release logic
        parsed_nutrition = None
        if barcodes:
            for b in barcodes:
                off_product = await fetch_product_by_barcode(b.value)
                if off_product:
                    mapped = map_off_to_nutrition(off_product)
                    if mapped and isinstance(mapped, dict) and "analysis" in mapped:
                        parsed_nutrition = mapped
                        break

        return LabelAnalyzeResponse(
            language=user_language,
            barcodes=barcodes,
            ocr_text=ocr_text,
            ocr_blocks=ocr_blocks,
            parsed_nutrition=parsed_nutrition,
            notes=(
                "Matched OpenFoodFacts by barcode"
                if parsed_nutrition else
                "No barcode match; OCR pipeline planned v0.2.0"
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Label analyze error [{getattr(request.state, 'request_id', '-') }]: {e}")
        raise HTTPException(status_code=500, detail="Label analysis failed")

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
            Проанализируйте блюдо на фотографии и определите ВСЕ продукты питания максимально точно.
            
            ВАЖНЫЕ ПРАВИЛА РАСПОЗНАВАНИЯ:
            1. ВНИМАТЕЛЬНО изучите форму, цвет, текстуру каждого продукта
            2. Отличайте похожие продукты:
               - Вареные яйца: белые, овальные, со специфической текстурой белка
               - Моцарелла: более гладкая, кремовая текстура
               - Сыр фета: крупинчатая структура, белый цвет
            3. Оценивайте размеры порций РЕАЛИСТИЧНО:
               - Одно вареное яйцо = 50-60г
               - Порция сыра = 20-40г
               - Листья салата = 10-30г за пучок
            4. Указывайте ТОЧНЫЕ названия продуктов
            
                         ⚠️ КРИТИЧЕСКОЕ ВНИМАНИЕ К БЕЛЫМ ПРОДУКТАМ ⚠️
             
             НА ЭТОМ ФОТО ТОЧНО ЕСТЬ ЯЙЦА, НЕ МОЦАРЕЛЛА!
             
             АБСОЛЮТНЫЕ ПРАВИЛА:
             🥚 ЯЙЦА = Белые овальные кусочки с ВИДИМЫМ ЖЕЛТКОМ в центре, матовые, разрезанные пополам
             🧀 МОЦАРЕЛЛА = Идеально круглые шарики БЕЗ желтка, глянцевые, цельные
             
             ⛔ ЗАПРЕЩЕНО НАЗЫВАТЬ ЯЙЦА МОЦАРЕЛЛОЙ! ⛔
             
             ПОШАГОВАЯ ПРОВЕРКА:
             1. Вижу белые овальные объекты? → ПРОВЕРЬ ЕСТЬ ЛИ ЖЕЛТОК
             2. Есть желток в центре? → ЭТО ЯЙЦА 🥚
             3. Нет желтка, но круглые шарики? → ЭТО МОЦАРЕЛЛА 🧀
             4. Оранжевые куски? → ЛОСОСЬ 🐟
             5. Зеленые листья? → ШПИНАТ/РУККОЛА 🥬
             
             ВНИМАНИЕ: Разрезанные вареные яйца выглядят как белые овалы с желтой серединой!
            
            Верните JSON в формате:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "название кухни",
                        "dish_identification": "название блюда",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "точное название продукта",
                            "weight_grams": реальный_вес,
                            "calories": калории,
                            "emoji": "🍽️",
                            "health_benefits": "польза для здоровья"
                        }
                    ],
                    "total_nutrition": {
                        "calories": 300,
                        "proteins": 20,
                        "fats": 10,
                        "carbohydrates": 30
                    },
                    "nutrition_analysis": {
                        "health_score": 8,
                        "positive_aspects": ["высокое содержание белка"],
                        "improvement_suggestions": ["добавить овощи"]
                    },
                    "motivation_message": "Отличный выбор для здорового питания!"
                }
            }
            """
        else:
            prompt = """
            Analyze the food in this image and identify ALL food items with MAXIMUM ACCURACY.
            
            CRITICAL RECOGNITION RULES:
            1. CAREFULLY examine shape, color, texture of each item
            2. Distinguish between similar foods:
               - Hard-boiled eggs: white, oval, specific egg white texture
               - Mozzarella: smoother, creamy texture
               - Feta cheese: crumbly structure, white color
            3. Estimate portion sizes REALISTICALLY:
               - One hard-boiled egg = 50-60g
               - Cheese portion = 20-40g
               - Salad leaves = 10-30g per handful
            4. Use PRECISE food names
            
                         ⚠️ CRITICAL ATTENTION TO WHITE FOOD ITEMS ⚠️
             
             THIS PHOTO DEFINITELY HAS EGGS, NOT MOZZARELLA!
             
             ABSOLUTE RULES:
             🥚 EGGS = White oval pieces with VISIBLE YOLK in center, matte surface, cut in half
             🧀 MOZZARELLA = Perfectly round balls WITHOUT yolk, glossy, whole pieces
             
             ⛔ FORBIDDEN TO CALL EGGS MOZZARELLA! ⛔
             
             STEP-BY-STEP CHECK:
             1. See white oval objects? → CHECK FOR YOLK
             2. Has yolk in center? → THESE ARE EGGS 🥚
             3. No yolk but round balls? → THIS IS MOZZARELLA 🧀
             4. Orange pieces? → SALMON 🐟
             5. Green leaves? → SPINACH/ARUGULA 🥬
             
             ATTENTION: Cut hard-boiled eggs look like white ovals with yellow center!
            
            Return JSON in format:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "cuisine name",
                        "dish_identification": "dish name", 
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "precise food name",
                            "weight_grams": realistic_weight,
                            "calories": calories,
                            "emoji": "🍽️",
                            "health_benefits": "health benefits"
                        }
                    ],
                    "total_nutrition": {
                        "calories": 300,
                        "proteins": 20,
                        "fats": 10,
                        "carbohydrates": 30
                    },
                    "nutrition_analysis": {
                        "health_score": 8,
                        "positive_aspects": ["high protein content"],
                        "improvement_suggestions": ["add vegetables"]
                    },
                    "motivation_message": "Great choice for healthy eating!"
                }
            }
            """
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert food recognition AI with advanced visual analysis capabilities. Your primary task is to accurately identify food items in images with precise attention to visual details like shape, color, texture, and size. Pay special attention to distinguishing between similar-looking foods (eggs vs cheese, different proteins, etc). Always prioritize accuracy over speed."
                },
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
                # Handle different possible old format keys
                kbzhu_data = None
                if "total_nutrition" in response_data:
                    kbzhu_data = response_data["total_nutrition"]
                elif "kbzhu" in response_data:
                    kbzhu_data = response_data["kbzhu"]
                else:
                    # Use the entire response as nutrition data
                    kbzhu_data = response_data
                
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
            logger.info("Entering fallback logic due to JSON parsing failure")
            
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
            # Convert to new format structure
            fallback_nutrition = {
                "calories": 250,
                "proteins": 15.0,
                "fats": 8.0,
                "carbohydrates": 30.0
            }
            
            if fallback_food_items:
                # Recalculate total calories from food items
                total_calories = sum(item["calories"] for item in fallback_food_items)
                if total_calories > 0:
                    fallback_nutrition["calories"] = total_calories
            
            # Convert fallback food items to new format
            new_format_food_items = []
            for item in fallback_food_items:
                new_format_food_items.append({
                    "name": item["name"],
                    "weight_grams": 100,  # Default weight
                    "calories": item["calories"],
                    "emoji": "🍽️",
                    "health_benefits": f"Contains {item['calories']} calories"
                })
            
            result = {
                "analysis": {
                    "food_items": new_format_food_items,
                    "total_nutrition": fallback_nutrition,
                    "motivation_message": "Keep tracking your nutrition!"
                }
            }
            
            logger.info(f"Fallback result: {result}")
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
        # Rate limiting (by client IP)
        client_ip = request.client.host if request.client else "unknown"
        if not _rate_limit_ok(f"analyze_file:{client_ip}"):
            raise HTTPException(status_code=429, detail="Too many requests")
        # Content length early check (if present)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        logger.info(f"🔥 ANALYZE_FILE CALLED: user={telegram_user_id}, provider={provider}")
        logger.info(f"🎯 Factory current provider: {llm_factory.get_current_provider()}")
        logger.info(f"Analyzing photo for user {telegram_user_id} with provider {provider}")
        
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await photo.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")
        
        # Use LLM factory for analysis (respects LLM_PROVIDER/ANALYSIS_PROVIDER env vars) and per-request override
        analysis_result = await llm_factory.analyze_food(
            image_bytes,
            user_language,
            use_premium_model=False,
            provider_override=provider,
        )
        
        logger.info(f"Analysis complete for user {telegram_user_id}: {analysis_result}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error [{getattr(request.state, 'request_id', '-') }]: {e}")
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
