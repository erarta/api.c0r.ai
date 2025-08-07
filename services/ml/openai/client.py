"""
OpenAI API client for food image analysis using shared prompts
"""

import os
import base64
import json
import httpx
from openai import OpenAI
from fastapi import HTTPException
from loguru import logger

from shared.prompts.food_analysis import get_food_analysis_prompt, get_system_prompt
from services.ml.config import get_model_config


# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
                proxy=http_proxy or https_proxy,
                verify=False
            )
        )
    else:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    
    logger.info("OpenAI client initialized successfully")
else:
    openai_client = None
    logger.warning("OpenAI API key not found")


async def analyze_food_with_openai(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
    """
    Analyze food image using OpenAI Vision API with shared prompts
    Returns KBZHU data in expected format
    
    Args:
        image_bytes: Image data to analyze
        user_language: User language preference
        use_premium_model: Whether to use premium model settings
    """
<<<<<<< Updated upstream
=======
    # Create language-specific fallback values
    if user_language == "ru":
        fallback_positive = ["Питательное блюдо"]
        fallback_suggestions = ["Добавить больше овощей"]
        fallback_motivation = "Отличный выбор для здорового питания!"
    else:
        fallback_positive = ["Nutritious meal"]
        fallback_suggestions = ["Add more vegetables"]
        fallback_motivation = "Great choice for healthy eating!"

>>>>>>> Stashed changes
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
        
        # Get shared prompts
        prompt = get_food_analysis_prompt(user_language)
        system_prompt_text = get_system_prompt()
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt_text
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
            
            # Add provider info for debugging
            if "analysis" in response_data:
                response_data["analysis"]["llm_provider"] = "openai"
                response_data["analysis"]["model_used"] = model
            else:
                response_data["llm_provider"] = "openai"
                response_data["model_used"] = model
            
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
                elif "nutrition" in response_data:
                    kbzhu_data = response_data["nutrition"]
                elif "kbzhu" in response_data:
                    kbzhu_data = response_data["kbzhu"]
                elif "nutritional_info" in response_data:
                    kbzhu_data = response_data["nutritional_info"]
                
                # Convert to new format
                converted_result = {
                    "analysis": {
                        "llm_provider": "openai",
                        "model_used": model,
                        "regional_analysis": {
                            "detected_cuisine_type": response_data.get("cuisine_type", "Mixed"),
                            "dish_identification": response_data.get("dish_name", "Unknown Dish"),
                            "regional_match_confidence": 0.7
                        },
                        "food_items": response_data.get("food_items", response_data.get("ingredients", [])),
                        "total_nutrition": kbzhu_data or {
                            "calories": 0,
                            "proteins": 0,
                            "fats": 0,
                            "carbohydrates": 0
                        },
                        "nutrition_analysis": response_data.get("health_analysis", {
                            "health_score": 7,
                            "positive_aspects": ["Nutritious meal"],
                            "improvement_suggestions": ["Add more vegetables"]
                        }),
                        "motivation_message": response_data.get("motivation", "Great choice for healthy eating!")
                    }
                }
                
                return converted_result
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            logger.error(f"Raw content: {content}")
            
            # Return error response in expected format
            return {
                "analysis": {
                    "llm_provider": "openai",
                    "model_used": model,
                    "error": "Failed to parse response",
                    "raw_response": content,
                    "regional_analysis": {
                        "detected_cuisine_type": "Unknown",
                        "dish_identification": "Analysis Failed",
                        "regional_match_confidence": 0.0
                    },
                    "food_items": [],
                    "total_nutrition": {
                        "calories": 0,
                        "proteins": 0,
                        "fats": 0,
                        "carbohydrates": 0
                    },
                    "nutrition_analysis": {
                        "health_score": 0,
                        "positive_aspects": [],
                        "improvement_suggestions": ["Try again with a different photo"]
                    },
                    "motivation_message": "Unable to analyze this image. Please try again!"
                }
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}") 