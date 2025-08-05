"""
Nutrition and food analysis Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from .common import BaseResponse


class NutritionData(BaseModel):
    """Nutritional information model"""
    calories: float = Field(..., ge=0, description="Calories per serving")
    proteins: float = Field(..., ge=0, description="Protein content in grams")
    fats: float = Field(..., ge=0, description="Fat content in grams")
    carbohydrates: float = Field(..., ge=0, description="Carbohydrate content in grams")
    fiber: Optional[float] = Field(None, ge=0, description="Fiber content in grams")
    sugar: Optional[float] = Field(None, ge=0, description="Sugar content in grams")
    sodium: Optional[float] = Field(None, ge=0, description="Sodium content in mg")


class FoodItem(BaseModel):
    """Individual food item model"""
    name: str = Field(..., min_length=1, max_length=200, description="Food item name")
    weight: str = Field(..., description="Weight or portion size (e.g., '100g', '1 cup')")
    calories: float = Field(..., ge=0, description="Calories for this item")
    nutrition: Optional[NutritionData] = Field(None, description="Detailed nutrition for this item")


class AnalysisRequest(BaseModel):
    """Request model for food analysis"""
    user_id: str = Field(..., description="User ID (telegram_id as string)")
    image_url: str = Field(..., description="URL of the food image to analyze")
    provider: str = Field(default="openai", pattern="^(openai|gemini)$", description="AI provider")
    user_language: str = Field(default="en", max_length=5, description="User language preference")


class AnalysisResponse(BaseResponse):
    """Response model for food analysis"""
    kbzhu: NutritionData = Field(..., description="Total nutritional information (KBZHU)")
    food_items: Optional[List[FoodItem]] = Field(None, description="Individual food items breakdown")
    analysis_provider: str = Field(default="openai", description="AI provider used for analysis")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence (0-1)")


class RecipeIngredient(BaseModel):
    """Recipe ingredient model"""
    name: str = Field(..., min_length=1, max_length=200)
    amount: str = Field(..., description="Amount with units (e.g., '2 cups', '100g')")


class RecipeInstruction(BaseModel):
    """Recipe instruction step model"""
    step: int = Field(..., ge=1, description="Step number")
    instruction: str = Field(..., min_length=1, description="Instruction text")


class RecipeNutrition(BaseModel):
    """Recipe nutrition per serving"""
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0, description="Protein in grams")
    carbs: float = Field(..., ge=0, description="Carbohydrates in grams")
    fat: float = Field(..., ge=0, description="Fat in grams")


class RecipeData(BaseModel):
    """Complete recipe model"""
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    description: Optional[str] = Field(None, max_length=500, description="Recipe description")
    prep_time: str = Field(..., description="Preparation time (e.g., '15 minutes')")
    cook_time: str = Field(..., description="Cooking time (e.g., '30 minutes')")
    servings: str = Field(..., description="Number of servings (e.g., '4')")
    ingredients: List[str] = Field(..., min_items=1, description="List of ingredients with amounts")
    instructions: List[str] = Field(..., min_items=1, description="List of cooking instructions")
    nutrition: RecipeNutrition = Field(..., description="Nutrition per serving")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$", description="Recipe difficulty")
    cuisine: Optional[str] = Field(None, max_length=50, description="Cuisine type")
    tags: Optional[List[str]] = Field(default_factory=list, description="Recipe tags")


class RecipeRequest(BaseModel):
    """Request model for recipe generation"""
    telegram_user_id: str = Field(..., description="Telegram user ID")
    image_url: str = Field(..., description="URL of the food/ingredient image")
    user_context: Dict[str, Any] = Field(..., description="User context and preferences")


class RecipeResponse(BaseResponse):
    """Response model for recipe generation"""
    recipe: RecipeData = Field(..., description="Generated recipe")
    personalized: bool = Field(default=False, description="Whether recipe was personalized")
    generation_provider: str = Field(default="openai", description="AI provider used")