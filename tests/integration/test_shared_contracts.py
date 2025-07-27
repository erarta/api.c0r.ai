"""
Integration tests for shared contracts
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.contracts.api_ml import APIMLContract
from shared.contracts.api_pay import APIPayContract
from shared.contracts.ml_pay import MLPayContract
from shared.models.ml import MLAnalysisRequest, RecipeRequest, RecipeGenerationContext
from shared.models.payment import InvoiceRequest
from shared.models.user import UserCreditsRequest


class TestAPIMLContract:
    """Test API ↔ ML service contract"""
    
    def test_analyze_food_request_creation(self):
        """Test creating ML analysis request"""
        request = APIMLContract.analyze_food_request(
            user_id="123456789",
            image_url="https://example.com/food.jpg",
            provider="openai",
            user_language="ru"
        )
        
        assert isinstance(request, MLAnalysisRequest)
        assert request.user_id == "123456789"
        assert request.image_url == "https://example.com/food.jpg"
        assert request.provider == "openai"
        assert request.user_language == "ru"
    
    def test_analyze_food_response_parsing(self):
        """Test parsing ML analysis response"""
        response_data = {
            "success": True,
            "message": "Analysis complete",
            "kbzhu": {
                "calories": 250.0,
                "proteins": 15.0,
                "fats": 8.0,
                "carbohydrates": 30.0
            },
            "food_items": [
                {
                    "name": "Apple",
                    "weight": "150g",
                    "calories": 80.0
                }
            ],
            "analysis_provider": "openai",
            "confidence_score": 0.95
        }
        
        response = APIMLContract.analyze_food_response(response_data)
        
        assert response.success is True
        assert response.kbzhu.calories == 250.0
        assert len(response.food_items) == 1
        assert response.food_items[0].name == "Apple"
        assert response.analysis_provider == "openai"
        assert response.confidence_score == 0.95
    
    def test_generate_recipe_request_creation(self):
        """Test creating recipe generation request"""
        user_context = {
            "language": "ru",
            "has_profile": True,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "goal": "lose_weight"
        }
        
        request = APIMLContract.generate_recipe_request(
            telegram_user_id="123456789",
            image_url="https://example.com/ingredients.jpg",
            user_context=user_context
        )
        
        assert isinstance(request, RecipeRequest)
        assert request.telegram_user_id == "123456789"
        assert request.image_url == "https://example.com/ingredients.jpg"
        assert request.user_context.language == "ru"
        assert request.user_context.has_profile is True
        assert "vegetarian" in request.user_context.dietary_preferences
    
    def test_ml_error_handling(self):
        """Test ML service error handling"""
        error_data = {
            "detail": "OpenAI API error",
            "error_type": "api_error"
        }
        
        error_response = APIMLContract.handle_ml_error(500, error_data)
        
        assert error_response.success is False
        assert error_response.message == "OpenAI API error"
        assert error_response.error_code == "ML_500"
        assert error_response.details == error_data
    
    @patch('shared.auth.get_auth_headers')
    def test_required_headers(self, mock_get_auth_headers):
        """Test getting required headers for ML service"""
        mock_get_auth_headers.return_value = {"X-Internal-Token": "test-token"}
        
        headers = APIMLContract.get_required_headers()
        
        assert "X-Internal-Token" in headers
        assert headers["X-Internal-Token"] == "test-token"
        mock_get_auth_headers.assert_called_once()
    
    def test_endpoints_configuration(self):
        """Test ML service endpoints configuration"""
        endpoints = APIMLContract.ENDPOINTS
        
        assert "analyze" in endpoints
        assert "generate_recipe" in endpoints
        assert "health" in endpoints
        assert endpoints["analyze"] == "/api/v1/analyze"
        assert endpoints["generate_recipe"] == "/api/v1/generate-recipe"
    
    def test_validation_rules(self):
        """Test ML service validation rules"""
        rules = APIMLContract.VALIDATION_RULES
        
        assert "max_image_size" in rules
        assert "supported_formats" in rules
        assert "timeout_seconds" in rules
        assert rules["max_image_size"] == 10 * 1024 * 1024  # 10MB
        assert "image/jpeg" in rules["supported_formats"]


class TestAPIPayContract:
    """Test API ↔ Payment service contract"""
    
    def test_create_invoice_request_creation(self):
        """Test creating invoice request"""
        request = APIPayContract.create_invoice_request(
            user_id="123456789",
            amount=100.0,
            description="Buy credits",
            plan_id="premium",
            currency="USD"
        )
        
        assert isinstance(request, InvoiceRequest)
        assert request.user_id == "123456789"
        assert request.amount == 100.0
        assert request.description == "Buy credits"
        assert request.plan_id == "premium"
        assert request.currency == "USD"
    
    def test_create_invoice_response_parsing(self):
        """Test parsing invoice creation response"""
        response_data = {
            "success": True,
            "message": "Invoice created",
            "invoice_id": "inv_123",
            "payment_url": "https://payment.example.com/pay/inv_123",
            "amount": 100.0,
            "currency": "RUB"
        }
        
        response = APIPayContract.create_invoice_response(response_data)
        
        assert response.success is True
        assert response.invoice_id == "inv_123"
        assert response.payment_url == "https://payment.example.com/pay/inv_123"
        assert response.amount == 100.0
        assert response.currency == "RUB"
    
    def test_add_credits_request_creation(self):
        """Test creating add credits request"""
        request = APIPayContract.add_credits_request(
            user_id="123456789",
            count=50,
            payment_id="pay_123",
            amount=200.0,
            gateway="stripe",
            status="succeeded"
        )
        
        assert isinstance(request, UserCreditsRequest)
        assert request.user_id == "123456789"
        assert request.count == 50
        assert request.payment_id == "pay_123"
        assert request.amount == 200.0
        assert request.gateway == "stripe"
        assert request.status == "succeeded"
    
    def test_payment_error_handling(self):
        """Test payment service error handling"""
        error_data = {
            "detail": "Payment gateway error",
            "gateway": "yookassa"
        }
        
        error_response = APIPayContract.handle_payment_error(402, error_data)
        
        assert error_response.success is False
        assert error_response.message == "Payment gateway error"
        assert error_response.error_code == "PAY_402"
        assert error_response.details == error_data
    
    @patch('shared.auth.get_auth_headers')
    def test_required_headers(self, mock_get_auth_headers):
        """Test getting required headers for Payment service"""
        mock_get_auth_headers.return_value = {"X-Internal-Token": "test-token"}
        
        headers = APIPayContract.get_required_headers()
        
        assert "X-Internal-Token" in headers
        mock_get_auth_headers.assert_called_once()
    
    def test_endpoints_configuration(self):
        """Test Payment service endpoints configuration"""
        endpoints = APIPayContract.ENDPOINTS
        
        assert "create_invoice" in endpoints
        assert "webhook_yookassa" in endpoints
        assert "webhook_stripe" in endpoints
        assert endpoints["create_invoice"] == "/invoice"
        assert endpoints["webhook_yookassa"] == "/webhook/yookassa"
    
    def test_validation_rules(self):
        """Test Payment service validation rules"""
        rules = APIPayContract.VALIDATION_RULES
        
        assert "min_amount" in rules
        assert "max_amount" in rules
        assert "supported_currencies" in rules
        assert "supported_gateways" in rules
        assert rules["min_amount"] == 1.0
        assert "RUB" in rules["supported_currencies"]
        assert "yookassa" in rules["supported_gateways"]
    
    @patch('common.config.payment_plans.PAYMENT_PLANS')
    def test_get_available_plans(self, mock_payment_plans):
        """Test getting available payment plans"""
        mock_payment_plans.return_value = {
            "basic": {"name": "Basic", "price": 100, "credits": 20},
            "premium": {"name": "Premium", "price": 500, "credits": 120}
        }
        
        plans = APIPayContract.get_available_plans()
        
        assert "basic" in plans
        assert "premium" in plans


class TestMLPayContract:
    """Test ML ↔ Payment service contract (future features)"""
    
    def test_track_premium_usage_request(self):
        """Test tracking premium AI model usage"""
        request = MLPayContract.track_premium_usage_request(
            user_id="123456789",
            model_used="gpt-4o",
            tokens_consumed=1500,
            processing_time=2.5,
            cost_estimate=0.075
        )
        
        assert request["user_id"] == "123456789"
        assert request["model_used"] == "gpt-4o"
        assert request["tokens_consumed"] == 1500
        assert request["processing_time"] == 2.5
        assert request["cost_estimate"] == 0.075
    
    def test_calculate_usage_cost_request(self):
        """Test calculating usage-based costs"""
        model_usage = {
            "gpt-4o-mini": 1000,
            "gpt-4o": 500
        }
        
        request = MLPayContract.calculate_usage_cost_request(
            user_id="123456789",
            usage_period="monthly",
            model_usage=model_usage
        )
        
        assert request["user_id"] == "123456789"
        assert request["usage_period"] == "monthly"
        assert request["model_usage"] == model_usage
    
    def test_model_cost_calculation(self):
        """Test AI model cost calculation"""
        # Test GPT-4o-mini cost calculation
        cost = MLPayContract.calculate_model_cost("gpt-4o-mini", 1000, 500)
        expected_cost = (1000/1000 * 0.00015) + (500/1000 * 0.0006)
        assert cost == round(expected_cost, 6)
        
        # Test unknown model
        cost = MLPayContract.calculate_model_cost("unknown-model", 1000, 500)
        assert cost == 0.0
    
    def test_configuration_flags(self):
        """Test configuration flags for future features"""
        config = MLPayContract.CONFIG
        
        assert "usage_tracking_enabled" in config
        assert "cost_allocation_enabled" in config
        assert "billing_integration_enabled" in config
        assert config["usage_tracking_enabled"] is False  # Currently disabled
    
    def test_model_costs_mapping(self):
        """Test model costs mapping"""
        costs = MLPayContract.MODEL_COSTS
        
        assert "gpt-4o-mini" in costs
        assert "gpt-4o" in costs
        assert "claude-3-haiku" in costs
        assert "claude-3-sonnet" in costs
        
        # Check cost structure
        gpt4_mini = costs["gpt-4o-mini"]
        assert "input" in gpt4_mini
        assert "output" in gpt4_mini
        assert gpt4_mini["input"] == 0.00015
        assert gpt4_mini["output"] == 0.0006


class TestContractIntegration:
    """Test contract integration scenarios"""
    
    def test_api_to_ml_flow(self):
        """Test complete API to ML service flow"""
        # 1. API service creates ML request
        ml_request = APIMLContract.analyze_food_request(
            user_id="123456789",
            image_url="https://example.com/food.jpg",
            provider="openai",
            user_language="en"
        )
        
        # 2. Simulate ML service response
        ml_response_data = {
            "success": True,
            "kbzhu": {
                "calories": 300.0,
                "proteins": 20.0,
                "fats": 10.0,
                "carbohydrates": 35.0
            },
            "analysis_provider": "openai"
        }
        
        # 3. API service parses ML response
        ml_response = APIMLContract.analyze_food_response(ml_response_data)
        
        assert ml_request.user_id == "123456789"
        assert ml_response.success is True
        assert ml_response.kbzhu.calories == 300.0
    
    def test_api_to_pay_flow(self):
        """Test complete API to Payment service flow"""
        # 1. API service creates invoice request
        invoice_request = APIPayContract.create_invoice_request(
            user_id="123456789",
            amount=100.0,
            description="Buy credits",
            plan_id="basic"
        )
        
        # 2. Simulate Payment service response
        invoice_response_data = {
            "success": True,
            "invoice_id": "inv_123",
            "payment_url": "https://pay.example.com/inv_123",
            "amount": 100.0,
            "currency": "RUB"
        }
        
        # 3. API service parses Payment response
        invoice_response = APIPayContract.create_invoice_response(invoice_response_data)
        
        assert invoice_request.user_id == "123456789"
        assert invoice_response.success is True
        assert invoice_response.invoice_id == "inv_123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])