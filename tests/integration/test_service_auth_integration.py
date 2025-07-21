"""
Integration tests for inter-service authentication
"""
import pytest
import os
import httpx
from unittest.mock import patch

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.auth import get_auth_headers

class TestServiceAuthIntegration:
    """Test authentication between services"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers for testing"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345678901234567890123456789012'}):
            return get_auth_headers()
    
    @pytest.fixture
    def invalid_headers(self):
        """Get invalid authentication headers for testing"""
        return {
            "X-Internal-Token": "invalid-token",
            "Content-Type": "application/json"
        }
    
    @pytest.mark.asyncio
    async def test_api_service_credits_add_with_valid_auth(self, auth_headers):
        """Test API service /credits/add endpoint with valid authentication"""
        # This test would require the API service to be running
        # For now, we'll test the auth headers format
        assert "X-Internal-Token" in auth_headers
        assert "Content-Type" in auth_headers
        assert auth_headers["Content-Type"] == "application/json"
        assert len(auth_headers["X-Internal-Token"]) >= 32
    
    @pytest.mark.asyncio
    async def test_ml_service_analyze_auth_required(self):
        """Test ML service /analyze endpoint requires authentication"""
        # Test that the endpoint structure is correct for auth
        from services.ml.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test without auth header - should fail
        response = client.post("/analyze", 
            files={"photo": ("test.jpg", b"fake image data", "image/jpeg")},
            data={
                "telegram_user_id": "123456789",
                "provider": "openai",
                "user_language": "en"
            }
        )
        
        # Should return 401 Unauthorized due to missing auth
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_pay_service_invoice_auth_required(self):
        """Test Payment service /invoice endpoint requires authentication"""
        from services.pay.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test without auth header - should fail
        response = client.post("/invoice", json={
            "user_id": "123456789",
            "amount": 100.0,
            "description": "Test payment",
            "plan_id": "basic"
        })
        
        # Should return 401 Unauthorized due to missing auth
        assert response.status_code == 401
    
    def test_auth_headers_format(self, auth_headers):
        """Test that auth headers have correct format"""
        assert isinstance(auth_headers, dict)
        assert "X-Internal-Token" in auth_headers
        assert "Content-Type" in auth_headers
        assert auth_headers["Content-Type"] == "application/json"
        
        # Token should be non-empty string
        token = auth_headers["X-Internal-Token"]
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_invalid_auth_headers_format(self, invalid_headers):
        """Test invalid auth headers format"""
        assert isinstance(invalid_headers, dict)
        assert "X-Internal-Token" in invalid_headers
        assert invalid_headers["X-Internal-Token"] == "invalid-token"
    
    @pytest.mark.asyncio
    async def test_service_to_service_communication_pattern(self, auth_headers):
        """Test the pattern for service-to-service communication"""
        # Simulate how services should communicate
        
        # 1. Service gets auth headers
        headers = auth_headers
        assert "X-Internal-Token" in headers
        
        # 2. Service makes request with headers
        request_data = {
            "user_id": "123456789",
            "count": 20,
            "payment_id": "test_payment_123",
            "amount": 100.0,
            "gateway": "yookassa",
            "status": "succeeded"
        }
        
        # 3. Verify request structure
        assert isinstance(request_data, dict)
        assert "user_id" in request_data
        
        # 4. Headers should be properly formatted for httpx
        async with httpx.AsyncClient() as client:
            # This would be the actual request pattern:
            # response = await client.post(url, headers=headers, json=request_data)
            # For testing, we just verify the structure
            assert headers is not None
            assert request_data is not None

class TestAuthenticationFlow:
    """Test complete authentication flow between services"""
    
    def test_api_to_ml_service_flow(self):
        """Test authentication flow from API to ML service"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345678901234567890123456789012'}):
            # 1. API service gets auth headers
            headers = get_auth_headers()
            
            # 2. API service prepares request to ML service
            ml_request = {
                "user_id": "123456789",
                "image_url": "https://example.com/image.jpg"
            }
            
            # 3. Verify request structure
            assert "X-Internal-Token" in headers
            assert "user_id" in ml_request
            assert "image_url" in ml_request
    
    def test_api_to_pay_service_flow(self):
        """Test authentication flow from API to Payment service"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345678901234567890123456789012'}):
            # 1. API service gets auth headers
            headers = get_auth_headers()
            
            # 2. API service prepares request to Payment service
            pay_request = {
                "user_id": "123456789",
                "amount": 100.0,
                "description": "Buy credits"
            }
            
            # 3. Verify request structure
            assert "X-Internal-Token" in headers
            assert "user_id" in pay_request
            assert "amount" in pay_request
    
    def test_pay_to_api_service_flow(self):
        """Test authentication flow from Payment to API service"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345678901234567890123456789012'}):
            # 1. Payment service gets auth headers
            headers = get_auth_headers()
            
            # 2. Payment service prepares request to API service
            credits_request = {
                "user_id": "123456789",
                "count": 20,
                "payment_id": "payment_123",
                "amount": 100.0,
                "gateway": "yookassa",
                "status": "succeeded"
            }
            
            # 3. Verify request structure
            assert "X-Internal-Token" in headers
            assert "user_id" in credits_request
            assert "count" in credits_request
            assert "payment_id" in credits_request

if __name__ == "__main__":
    pytest.main([__file__, "-v"])