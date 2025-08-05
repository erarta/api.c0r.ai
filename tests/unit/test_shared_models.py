"""
Unit tests for shared Pydantic models
"""

import pytest
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.models.common import BaseResponse, ErrorResponse, HealthResponse
from shared.models.user import UserProfile, UserRequest, UserCreditsRequest
from shared.models.nutrition import NutritionData, FoodItem, AnalysisRequest
from shared.models.payment import InvoiceRequest, PaymentRequest
from shared.models.ml import MLAnalysisRequest, RecipeRequest, RecipeGenerationContext
from pydantic import ValidationError


class TestCommonModels:
    """Test common models"""
    
    def test_base_response_creation(self):
        """Test BaseResponse model creation"""
        response = BaseResponse(message="Test message")
        
        assert response.success is True
        assert response.message == "Test message"
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response_creation(self):
        """Test ErrorResponse model creation"""
        error = ErrorResponse(
            message="Test error",
            error_code="TEST_001",
            details={"field": "value"}
        )
        
        assert error.success is False
        assert error.message == "Test error"
        assert error.error_code == "TEST_001"
        assert error.details == {"field": "value"}
    
    def test_health_response_creation(self):
        """Test HealthResponse model creation"""
        health = HealthResponse(
            service="test-service",
            version="1.0.0",
            dependencies={"db": "healthy"}
        )
        
        assert health.service == "test-service"
        assert health.status == "healthy"
        assert health.version == "1.0.0"
        assert health.dependencies == {"db": "healthy"}


class TestUserModels:
    """Test user-related models"""
    
    def test_user_profile_creation(self):
        """Test UserProfile model creation"""
        profile = UserProfile(
            telegram_id=123456789,
            credits_remaining=50,
            country="US",
            language="en",
            age=25,
            gender="male",
            height=180.0,
            weight=75.0
        )
        
        assert profile.telegram_id == 123456789
        assert profile.credits_remaining == 50
        assert profile.country == "US"
        assert profile.language == "en"
        assert profile.age == 25
        assert profile.gender == "male"
        assert profile.height == 180.0
        assert profile.weight == 75.0
    
    def test_user_profile_validation(self):
        """Test UserProfile validation"""
        # Test invalid telegram_id
        with pytest.raises(ValueError, match="Telegram ID must be positive"):
            UserProfile(telegram_id=-1)
    
        # Test invalid country code - Pydantic v2 validation
        with pytest.raises(ValidationError):
            UserProfile(telegram_id=123456789, country="USA")
        
        # Test invalid age
        with pytest.raises(ValueError):
            UserProfile(telegram_id=123456789, age=150)
    
    def test_user_request_creation(self):
        """Test UserRequest model creation"""
        request = UserRequest(
            telegram_id=123456789,
            country="RU",
            language="ru"
        )
        
        assert request.telegram_id == 123456789
        assert request.country == "RU"
        assert request.language == "ru"
    
    def test_user_credits_request_creation(self):
        """Test UserCreditsRequest model creation"""
        request = UserCreditsRequest(
            user_id="123456789",
            count=20,
            payment_id="pay_123",
            amount=100.0,
            gateway="yookassa"
        )
        
        assert request.user_id == "123456789"
        assert request.count == 20
        assert request.payment_id == "pay_123"
        assert request.amount == 100.0
        assert request.gateway == "yookassa"


class TestNutritionModels:
    """Test nutrition-related models"""
    
    def test_nutrition_data_creation(self):
        """Test NutritionData model creation"""
        nutrition = NutritionData(
            calories=250.0,
            proteins=15.0,
            fats=8.0,
            carbohydrates=30.0,
            fiber=5.0,
            sugar=10.0,
            sodium=500.0
        )
        
        assert nutrition.calories == 250.0
        assert nutrition.proteins == 15.0
        assert nutrition.fats == 8.0
        assert nutrition.carbohydrates == 30.0
        assert nutrition.fiber == 5.0
        assert nutrition.sugar == 10.0
        assert nutrition.sodium == 500.0
    
    def test_food_item_creation(self):
        """Test FoodItem model creation"""
        nutrition = NutritionData(calories=100.0, proteins=5.0, fats=2.0, carbohydrates=15.0)
        
        food_item = FoodItem(
            name="Apple",
            weight="150g",
            calories=80.0,
            nutrition=nutrition
        )
        
        assert food_item.name == "Apple"
        assert food_item.weight == "150g"
        assert food_item.calories == 80.0
        assert food_item.nutrition.calories == 100.0
    
    def test_analysis_request_creation(self):
        """Test AnalysisRequest model creation"""
        request = AnalysisRequest(
            user_id="123456789",
            image_url="https://example.com/image.jpg",
            provider="openai",
            user_language="en"
        )
        
        assert request.user_id == "123456789"
        assert request.image_url == "https://example.com/image.jpg"
        assert request.provider == "openai"
        assert request.user_language == "en"


class TestPaymentModels:
    """Test payment-related models"""
    
    def test_invoice_request_creation(self):
        """Test InvoiceRequest model creation"""
        request = InvoiceRequest(
            user_id="123456789",
            amount=100.0,
            description="Buy credits",
            plan_id="basic",
            currency="RUB"
        )
        
        assert request.user_id == "123456789"
        assert request.amount == 100.0
        assert request.description == "Buy credits"
        assert request.plan_id == "basic"
        assert request.currency == "RUB"
    
    def test_invoice_request_validation(self):
        """Test InvoiceRequest validation"""
        # Test invalid amount - Pydantic v2 validation
        with pytest.raises(ValidationError):
            InvoiceRequest(
                user_id="123456789",
                amount=-10.0,
                description="Invalid amount"
            )
    
    def test_payment_request_creation(self):
        """Test PaymentRequest model creation"""
        request = PaymentRequest(
            user_id="123456789",
            payment_id="pay_123",
            amount=100.0,
            currency="RUB",
            gateway="yookassa",
            status="succeeded",
            metadata={"plan_id": "basic"}
        )
        
        assert request.user_id == "123456789"
        assert request.payment_id == "pay_123"
        assert request.amount == 100.0
        assert request.currency == "RUB"
        assert request.gateway == "yookassa"
        assert request.status == "succeeded"
        assert request.metadata == {"plan_id": "basic"}


class TestMLModels:
    """Test ML-related models"""
    
    def test_ml_analysis_request_creation(self):
        """Test MLAnalysisRequest model creation"""
        request = MLAnalysisRequest(
            user_id="123456789",
            image_url="https://example.com/image.jpg",
            provider="openai",
            user_language="en"
        )
        
        assert request.user_id == "123456789"
        assert request.image_url == "https://example.com/image.jpg"
        assert request.provider == "openai"
        assert request.user_language == "en"
    
    def test_ml_analysis_request_validation(self):
        """Test MLAnalysisRequest validation"""
        # Test invalid image URL
        with pytest.raises(ValueError, match="Image URL must be a valid HTTP/HTTPS URL"):
            MLAnalysisRequest(
                user_id="123456789",
                image_url="invalid-url",
                provider="openai"
            )
    
    def test_recipe_generation_context_creation(self):
        """Test RecipeGenerationContext model creation"""
        context = RecipeGenerationContext(
            language="ru",
            has_profile=True,
            dietary_preferences=["vegetarian"],
            allergies=["nuts"],
            goal="lose_weight",
            daily_calories_target=1800,
            age=25,
            gender="female"
        )
        
        assert context.language == "ru"
        assert context.has_profile is True
        assert context.dietary_preferences == ["vegetarian"]
        assert context.allergies == ["nuts"]
        assert context.goal == "lose_weight"
        assert context.daily_calories_target == 1800
        assert context.age == 25
        assert context.gender == "female"
    
    def test_recipe_request_creation(self):
        """Test RecipeRequest model creation"""
        context = RecipeGenerationContext(language="en", has_profile=False)
        
        request = RecipeRequest(
            telegram_user_id="123456789",
            image_url="https://example.com/ingredients.jpg",
            user_context=context
        )
        
        assert request.telegram_user_id == "123456789"
        assert request.image_url == "https://example.com/ingredients.jpg"
        assert request.user_context.language == "en"
        assert request.user_context.has_profile is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])