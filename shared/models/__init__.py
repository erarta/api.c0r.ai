"""
Shared Pydantic models for inter-service communication
"""

from .user import UserProfile, UserRequest, UserResponse
from .nutrition import NutritionData, FoodItem, AnalysisRequest, AnalysisResponse
from .payment import PaymentRequest, PaymentResponse, InvoiceRequest, InvoiceResponse
from .ml import MLAnalysisRequest, MLAnalysisResponse, RecipeRequest, RecipeResponse
from .common import BaseResponse, ErrorResponse, HealthResponse

__all__ = [
    # User models
    "UserProfile",
    "UserRequest", 
    "UserResponse",
    
    # Nutrition models
    "NutritionData",
    "FoodItem",
    "AnalysisRequest",
    "AnalysisResponse",
    
    # Payment models
    "PaymentRequest",
    "PaymentResponse", 
    "InvoiceRequest",
    "InvoiceResponse",
    
    # ML models
    "MLAnalysisRequest",
    "MLAnalysisResponse",
    "RecipeRequest",
    "RecipeResponse",
    
    # Common models
    "BaseResponse",
    "ErrorResponse",
    "HealthResponse",
]