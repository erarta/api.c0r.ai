"""
LLM Provider Factory for dynamic model switching
"""

import os
from enum import Enum
from typing import Dict, Any, Callable, Optional
from loguru import logger

from services.ml.openai.client import analyze_food_with_openai
from services.ml.perplexity.client import analyze_food_with_perplexity
from services.ml.gemini.client import analyze_food_with_gemini


class LLMProvider(Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"


class LLMProviderFactory:
    """Factory for creating and managing LLM providers"""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, Callable] = {
            LLMProvider.OPENAI: analyze_food_with_openai,
            LLMProvider.PERPLEXITY: analyze_food_with_perplexity,
            LLMProvider.GEMINI: analyze_food_with_gemini,
        }
        
        # Get current provider from environment
        self.current_provider = self._get_current_provider()
        logger.info(f"🤖 LLM Provider initialized: {self.current_provider.value}")
    
    def _get_current_provider(self) -> LLMProvider:
        """
        Get current provider from environment variable
        
        Returns:
            LLMProvider enum value
        """
        # Support both LLM_PROVIDER and ANALYSIS_PROVIDER (alias)
        provider_name = (
            os.getenv("LLM_PROVIDER")
            or os.getenv("ANALYSIS_PROVIDER")
            or "openai"
        ).lower()
        
        try:
            return LLMProvider(provider_name)
        except ValueError:
            logger.warning(f"Invalid LLM_PROVIDER '{provider_name}', falling back to OpenAI")
            return LLMProvider.OPENAI
    
    async def analyze_food(
        self,
        image_bytes: bytes,
        user_language: str = "en",
        use_premium_model: bool = False,
        provider_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze food using current LLM provider
        
        Args:
            image_bytes: Image data to analyze
            user_language: User language preference
            use_premium_model: Whether to use premium model settings
            provider_override: If provided, use this provider for this call only
            
        Returns:
            Analysis result dict with provider info
        """
        # Decide which provider to use for this call
        effective_provider = self.current_provider
        if provider_override:
            try:
                effective_provider = LLMProvider(provider_override.lower())
            except ValueError:
                logger.warning(f"Invalid provider_override '{provider_override}', using default {self.current_provider.value}")
        
        logger.info(f"🎯 analyze_food called with provider: {effective_provider.value}")
        logger.info(f"📝 Available providers: {[p.value for p in self.providers.keys()]}")
        provider_func = self.providers.get(effective_provider)
        
        if not provider_func:
            logger.error(f"Provider {effective_provider} not implemented")
            raise ValueError(f"Provider {effective_provider} not available")
        
        logger.info(f"🔍 Using provider: {effective_provider.value}")

        logger.debug(f"Provider selected: {effective_provider.value}")

        try:
            logger.info(f"🔍 Analyzing food with {effective_provider.value}")
            logger.info(f"🔧 Provider function: {provider_func}")
            result = await provider_func(image_bytes, user_language, use_premium_model)
            logger.info(f"✅ {effective_provider.value} analysis completed successfully")
            
            # Ensure provider info is included for debugging
            if "analysis" in result:
                result["analysis"]["llm_provider"] = effective_provider.value
            else:
                result["llm_provider"] = effective_provider.value
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed with {effective_provider.value}: {str(e)}")
            
            # Try fallback to OpenAI if current provider fails
            if effective_provider != LLMProvider.OPENAI:
                logger.info("🔄 Falling back to OpenAI...")
                try:
                    result = await analyze_food_with_openai(image_bytes, user_language, use_premium_model)
                    if "analysis" in result:
                        result["analysis"]["llm_provider"] = effective_provider.value
                    else:
                        result["llm_provider"] = effective_provider.value
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback to OpenAI also failed: {str(fallback_error)}")
            
            # If all fails, return error structure
            return {
                "analysis": {
                    "llm_provider": f"{effective_provider.value} (failed)",
                    "error": str(e),
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
                        "improvement_suggestions": ["Please try again"]
                    },
                    "motivation_message": "Unable to analyze this image. Please try again!"
                }
            }
    
    def get_current_provider(self) -> str:
        """
        Get current provider name
        
        Returns:
            Provider name string
        """
        return self.current_provider.value
    
    def set_provider(self, provider: str) -> bool:
        """
        Set current provider
        
        Args:
            provider: Provider name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_provider = LLMProvider(provider.lower())
            self.current_provider = new_provider
            logger.info(f"🔄 Switched to provider: {provider}")
            return True
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            return False
    
    def list_available_providers(self) -> list:
        """
        List all available providers
        
        Returns:
            List of provider names
        """
        return [provider.value for provider in LLMProvider]


# Global factory instance
llm_factory = LLMProviderFactory() 