import os
import base64
import json
import httpx
from loguru import logger

from shared.prompts.food_analysis import get_food_analysis_prompt, get_system_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def analyze_food_with_gemini(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
    """
    Analyze food image using Google Gemini Vision API
    Returns KBZHU data in expected format
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Get shared prompts
        prompt = get_food_analysis_prompt(user_language)
        
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
                
                # Add provider info for debugging
                model_name = "gemini-pro-vision"  # Gemini vision model
                
                # Check if we have the new analysis format
                if "analysis" in response_data:
                    # New format - add debug info and return
                    response_data["analysis"]["llm_provider"] = "gemini"
                    response_data["analysis"]["model_used"] = model_name
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
                            "llm_provider": "gemini",
                            "model_used": model_name,
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