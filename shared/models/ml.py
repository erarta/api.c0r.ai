"""
ML service Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from .common import BaseResponse
from .nutrition import NutritionData, FoodItem, RecipeData


class MLAnalysisRequest(BaseModel):
    """Request model for ML food analysis"""
    user_id: str = Field(..., description="User ID (telegram_id as string)")
    image_url: str = Field(..., description="URL of the food image to analyze")
    provider: str = Field(default="openai", pattern="^(openai|gemini)$", description="AI provider")
    user_language: str = Field(default="en", max_length=5, description="User language preference")
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must be a valid HTTP/HTTPS URL')
        return v


class MLAnalysisResponse(BaseResponse):
    """Response model for ML food analysis"""
    kbzhu: NutritionData = Field(..., description="Total nutritional information")
    food_items: Optional[List[FoodItem]] = Field(None, description="Individual food items breakdown")
    analysis_provider: str = Field(default="openai", description="AI provider used")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")


class RecipeGenerationContext(BaseModel):
    """User context for recipe generation"""
    language: str = Field(default="en", description="User language preference")
    has_profile: bool = Field(default=False, description="Whether user has a complete profile")
    dietary_preferences: Optional[List[str]] = Field(default_factory=list, description="Dietary preferences")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Food allergies")
    goal: Optional[str] = Field(None, description="Fitness goal")
    daily_calories_target: Optional[int] = Field(None, description="Daily calorie target")
    activity_level: Optional[str] = Field(None, description="Activity level")
    age: Optional[int] = Field(None, description="User age")
    gender: Optional[str] = Field(None, description="User gender")


class RecipeRequest(BaseModel):
    """Request model for recipe generation"""
    telegram_user_id: str = Field(..., description="Telegram user ID")
    image_url: str = Field(..., description="URL of the food/ingredient image")
    user_context: RecipeGenerationContext = Field(..., description="User context and preferences")
    
    @validator('image_url')
    def validate_image_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must be a valid HTTP/HTTPS URL')
        return v


class RecipeResponse(BaseResponse):
    """Response model for recipe generation"""
    recipe: RecipeData = Field(..., description="Generated recipe")
    personalized: bool = Field(default=False, description="Whether recipe was personalized")
    generation_provider: str = Field(default="openai", description="AI provider used")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")


class MLHealthCheck(BaseModel):
    """ML service health check model"""
    service: str = "ml"
    status: str = "healthy"
    openai_available: bool = Field(default=False, description="OpenAI API availability")
    gemini_available: bool = Field(default=False, description="Gemini API availability")
    models_loaded: List[str] = Field(default_factory=list, description="Loaded ML models")


class MLError(BaseModel):
    """ML service error model"""
    error_type: str = Field(..., description="Type of ML error")
    error_message: str = Field(..., description="Error message")
    provider: Optional[str] = Field(None, description="AI provider that caused the error")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch food analysis"""
    user_id: str = Field(..., description="User ID")
    image_urls: List[str] = Field(..., min_items=1, max_items=10, description="List of image URLs")
    provider: str = Field(default="openai", description="AI provider")
    user_language: str = Field(default="en", description="User language")
    
    @validator('image_urls')
    def validate_image_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid image URL: {url}')
        return v


class BatchAnalysisResponse(BaseResponse):
    """Response model for batch food analysis"""
    results: List[MLAnalysisResponse] = Field(..., description="Analysis results for each image")
    total_nutrition: NutritionData = Field(..., description="Combined nutritional information")
    processed_count: int = Field(..., description="Number of successfully processed images")
    failed_count: int = Field(default=0, description="Number of failed analyses")