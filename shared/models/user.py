"""
User-related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .common import BaseResponse


class UserProfile(BaseModel):
    """User profile model"""
    telegram_id: int = Field(..., description="Telegram user ID")
    credits_remaining: int = Field(default=0, ge=0, description="Remaining credits")
    country: Optional[str] = Field(None, max_length=2, description="Country code (ISO 3166-1 alpha-2)")
    language: str = Field(default="en", max_length=5, description="User language preference")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Profile data
    age: Optional[int] = Field(None, ge=13, le=120, description="User age")
    gender: Optional[str] = Field(None, regex="^(male|female|other)$", description="User gender")
    height: Optional[float] = Field(None, gt=0, le=300, description="Height in cm")
    weight: Optional[float] = Field(None, gt=0, le=1000, description="Weight in kg")
    activity_level: Optional[str] = Field(None, regex="^(sedentary|light|moderate|active|very_active)$")
    goal: Optional[str] = Field(None, regex="^(lose_weight|maintain_weight|gain_weight)$")
    dietary_preferences: Optional[List[str]] = Field(default_factory=list, description="Dietary preferences")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Food allergies")
    daily_calories_target: Optional[int] = Field(None, gt=0, le=10000, description="Daily calorie target")

    @validator('telegram_id')
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('Telegram ID must be positive')
        return v

    @validator('country')
    def validate_country(cls, v):
        if v and len(v) != 2:
            raise ValueError('Country code must be 2 characters')
        return v.upper() if v else v


class UserRequest(BaseModel):
    """Request model for user operations"""
    telegram_id: int = Field(..., description="Telegram user ID")
    country: Optional[str] = Field(None, max_length=2, description="Country code")
    language: Optional[str] = Field("en", max_length=5, description="User language")


class UserResponse(BaseResponse):
    """Response model for user operations"""
    user: UserProfile


class UserCreditsRequest(BaseModel):
    """Request model for adding credits to user"""
    user_id: str = Field(..., description="User ID (telegram_id as string)")
    count: int = Field(default=20, ge=1, le=1000, description="Number of credits to add")
    payment_id: Optional[str] = Field(None, description="Payment ID for tracking")
    amount: Optional[float] = Field(None, ge=0, description="Payment amount")
    gateway: str = Field(default="yookassa", description="Payment gateway")
    status: str = Field(default="succeeded", description="Payment status")


class UserCreditsResponse(BaseResponse):
    """Response model for credits operations"""
    user: UserProfile
    credits_added: Optional[int] = None