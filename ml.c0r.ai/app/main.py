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

            Пожалуйста, предоставьте:
            1. Список отдельных продуктов питания, видимых на изображении
            2. Оцененный вес/размер порции для каждого продукта
            3. Калории для каждого отдельного продукта
            4. Общую сводку по питанию

            Верните ТОЛЬКО JSON объект со следующей структурой:
            {
                "food_items": [
                    {
                        "name": "название продукта",
                        "weight": "оцененный вес с единицами (например, 150г, 1 стакан)",
                        "calories": число
                    }
                ],
                "total_nutrition": {
                    "calories": число,
                    "proteins": число,
                    "fats": число,
                    "carbohydrates": число
                }
            }

            Оцените значения для фактического размера порции, показанного на изображении.
            Все числовые значения должны быть числами (не строками).
            Будьте конкретны в отношении продуктов питания и реалистичны в отношении порций.
            """
        else:
            prompt = """
            Analyze this food image and provide detailed nutritional information. 

            Please provide:
            1. List of individual food items visible in the image
            2. Estimated weight/portion size for each item
            3. Calories for each individual item
            4. Total nutritional summary

            Return ONLY a JSON object with the following structure:
            {
                "food_items": [
                    {
                        "name": "product name",
                        "weight": "estimated weight with units (e.g., 150g, 1 cup)",
                        "calories": number
                    }
                ],
                "total_nutrition": {
                    "calories": number,
                    "proteins": number,
                    "fats": number,
                    "carbohydrates": number
                }
            }

            Estimate values for the actual serving size shown in the image.
            All numeric values should be numbers (not strings).
            Be specific about food items and realistic about portions.
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
        
        # Try to parse JSON from response
        try:
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
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
            # Return fallback values
            return {
                "kbzhu": {
                    "calories": 250,
                    "proteins": 15.0,
                    "fats": 8.0,
                    "carbohydrates": 30.0
                }
            }
            
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")

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