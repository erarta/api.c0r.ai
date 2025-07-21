"""
API ↔ ML Service Contract
Defines the interface between API service and ML service
"""

from typing import Dict, Any
from ..models.ml import MLAnalysisRequest, MLAnalysisResponse, RecipeRequest, RecipeResponse
from ..models.common import BaseResponse, ErrorResponse


class APIMLContract:
    """Contract for API service to ML service communication"""
    
    # === Food Analysis Endpoints ===
    
    @staticmethod
    def analyze_food_request(
        user_id: str,
        image_url: str,
        provider: str = "openai",
        user_language: str = "en"
    ) -> MLAnalysisRequest:
        """
        Create request for food analysis
        
        Args:
            user_id: Telegram user ID as string
            image_url: URL of the food image
            provider: AI provider (openai, gemini)
            user_language: User language preference
            
        Returns:
            MLAnalysisRequest: Validated request model
        """
        return MLAnalysisRequest(
            user_id=user_id,
            image_url=image_url,
            provider=provider,
            user_language=user_language
        )
    
    @staticmethod
    def analyze_food_response(response_data: Dict[str, Any]) -> MLAnalysisResponse:
        """
        Parse ML service response for food analysis
        
        Args:
            response_data: Raw response from ML service
            
        Returns:
            MLAnalysisResponse: Validated response model
        """
        return MLAnalysisResponse(**response_data)
    
    # === Recipe Generation Endpoints ===
    
    @staticmethod
    def generate_recipe_request(
        telegram_user_id: str,
        image_url: str,
        user_context: Dict[str, Any]
    ) -> RecipeRequest:
        """
        Create request for recipe generation
        
        Args:
            telegram_user_id: Telegram user ID
            image_url: URL of the food/ingredient image
            user_context: User preferences and context
            
        Returns:
            RecipeRequest: Validated request model
        """
        return RecipeRequest(
            telegram_user_id=telegram_user_id,
            image_url=image_url,
            user_context=user_context
        )
    
    @staticmethod
    def generate_recipe_response(response_data: Dict[str, Any]) -> RecipeResponse:
        """
        Parse ML service response for recipe generation
        
        Args:
            response_data: Raw response from ML service
            
        Returns:
            RecipeResponse: Validated response model
        """
        return RecipeResponse(**response_data)
    
    # === Error Handling ===
    
    @staticmethod
    def handle_ml_error(status_code: int, error_data: Dict[str, Any]) -> ErrorResponse:
        """
        Handle ML service errors
        
        Args:
            status_code: HTTP status code
            error_data: Error response data
            
        Returns:
            ErrorResponse: Standardized error response
        """
        return ErrorResponse(
            success=False,
            message=error_data.get("detail", "ML service error"),
            error_code=f"ML_{status_code}",
            details=error_data
        )
    
    # === Service Endpoints ===
    
    ENDPOINTS = {
        "analyze": "/api/v1/analyze",
        "generate_recipe": "/api/v1/generate-recipe",
        "health": "/",
    }
    
    # === Request Headers ===
    
    @staticmethod
    def get_required_headers() -> Dict[str, str]:
        """
        Get required headers for ML service requests
        
        Returns:
            Dict[str, str]: Required headers
        """
        from ..auth import get_auth_headers
        return get_auth_headers()
    
    # === Validation Rules ===
    
    VALIDATION_RULES = {
        "max_image_size": 10 * 1024 * 1024,  # 10MB
        "supported_formats": ["image/jpeg", "image/png", "image/webp"],
        "timeout_seconds": 60,
        "max_retries": 3,
    }