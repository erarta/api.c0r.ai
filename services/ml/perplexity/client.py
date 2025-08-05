"""
Perplexity API client for food image analysis
"""

import os
import base64
import json
import httpx
from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger

from shared.prompts.food_analysis import get_food_analysis_prompt, get_system_prompt


def get_expert_prefix(user_language: str = "en") -> str:
    """Get expert prefix in the user's language"""
    if user_language == "ru":
        return "Ты эксперт-диетолог. Точно определи каждое блюдо и ингредиент на изображении. "
    else:
        return "You are an expert nutritionist. Accurately identify every dish and ingredient in the image. "


def get_json_instruction(user_language: str = "en") -> str:
    """Get JSON instruction in the user's language"""
    if user_language == "ru":
        return " Ответ дай строго в JSON формате."
    else:
        return " Provide the answer strictly in JSON format."


# Perplexity API configuration
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"


async def analyze_food_with_perplexity(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
    """
    Analyze food image using Perplexity API
    Returns KBZHU data in expected format
    
    Args:
        image_bytes: Image data to analyze
        user_language: User language preference
        use_premium_model: Whether to use premium model settings (not used for Perplexity)
    """
    if not PERPLEXITY_API_KEY:
        raise HTTPException(status_code=500, detail="Perplexity API key not configured")
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Get shared prompts
        user_prompt = get_food_analysis_prompt(user_language)
        system_prompt = get_system_prompt()
        
        # Perplexity API supports vision with sonar models
        # sonar-pro and sonar support images, sonar-deep-research does NOT
        model = "sonar-pro" if use_premium_model else "sonar"
        
        # Prepare the request payload with optimal settings for food recognition
        payload = {
            "model": model,
            "stream": False,
            "temperature": 0.2,      # Минимальная случайность для точности
            "top_p": 0.3,           # Ограничение ядра выборки для фокуса на вероятных токенах
            "presence_penalty": 0.1, # Снижает риск повторений, не подавляя новые токены
            "max_tokens": 1000,     # Достаточно для детального описания ингредиентов
            "return_images": False, # Не нужны обратные изображения - экономим токены
            "search_domain_filter": ["wikipedia.org", "seriouseats.com", "bonappetit.com"], # Источники с высокой кулинарной достоверностью
            "response_format": {"type": "text"}, # Perplexity uses "text" format, not "json_object"
            "messages": [
                {
                    "role": "system",
                    "content": get_expert_prefix(user_language) + system_prompt
                },
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": user_prompt + get_json_instruction(user_language)},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"🔍 Preparing to call Perplexity API with model: {model}")
        logger.info(f"🔧 Payload: {json.dumps(payload, indent=2)}")
        logger.info(f"🔑 Using API Key: {PERPLEXITY_API_KEY[:5]}...{PERPLEXITY_API_KEY[-5:]}")

        # Call Perplexity API
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info(f"Calling Perplexity API with model: {model}")
            
            logger.debug(f"Request URL: {PERPLEXITY_BASE_URL}/chat/completions")
            logger.debug(f"Request Headers: {headers}")
            logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                f"{PERPLEXITY_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            # Log response details
            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {response.headers}")
            logger.debug(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Perplexity API returned status {response.status_code}"
                )
            
            response_data = response.json()
            
        # Parse response
        content = response_data["choices"][0]["message"]["content"].strip()
        logger.info(f"Perplexity response: {content}")
        
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
            
            # Ensure content is valid JSON
            if not content.startswith('{'):
                logger.error(f"Invalid JSON content: {content}")
                raise json.JSONDecodeError("Content does not start with {", content, 0)
            
            response_data = json.loads(content)
            
            # Add provider info for debugging
            if "analysis" in response_data:
                response_data["analysis"]["llm_provider"] = "perplexity"
                response_data["analysis"]["model_used"] = model
            else:
                response_data["llm_provider"] = "perplexity"
                response_data["model_used"] = model
            
            # Check if we have the new analysis format
            if "analysis" in response_data:
                # New format - return as is
                return response_data
            else:
                # Old format fallback - convert to new structure
                logger.warning("Perplexity returned old format, converting...")
                return {
                    "analysis": {
                        "llm_provider": "perplexity",
                        "model_used": model,
                        "regional_analysis": {
                            "detected_cuisine_type": "Mixed",
                            "dish_identification": "Analyzed Dish",
                            "regional_match_confidence": 0.7
                        },
                        "food_items": response_data.get("food_items", []),
                        "total_nutrition": response_data.get("total_nutrition", {}),
                        "nutrition_analysis": response_data.get("nutrition_analysis", {}),
                        "motivation_message": response_data.get("motivation_message", "Great choice!")
                    }
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Perplexity JSON response: {e}")
            logger.error(f"Raw content: {content}")
            
            # Return error response in expected format
            return {
                "analysis": {
                    "llm_provider": "perplexity",
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
            
    except httpx.TimeoutException:
        logger.error("Perplexity API timeout")
        raise HTTPException(status_code=500, detail="Perplexity API timeout")
        
    except Exception as e:
        logger.error(f"Unexpected error in Perplexity analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Perplexity analysis failed: {str(e)}")


def test_perplexity_connection() -> bool:
    """
    Test Perplexity API connection
    
    Returns:
        True if connection successful, False otherwise
    """
    if not PERPLEXITY_API_KEY:
        logger.warning("Perplexity API key not configured")
        return False
        
    try:
        import asyncio
        
        async def test():
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{PERPLEXITY_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers
                )
                return response.status_code == 200
        
        return asyncio.run(test())
        
    except Exception as e:
        logger.error(f"Perplexity connection test failed: {e}")
        return False 