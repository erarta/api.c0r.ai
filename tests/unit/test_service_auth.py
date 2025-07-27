"""
Tests for inter-service authentication system
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.auth import (
    validate_internal_token,
    require_internal_auth,
    get_auth_headers,
    check_service_auth,
    AuthenticationError,
    INTERNAL_API_TOKEN
)

class TestServiceAuthentication:
    """Test service authentication functionality"""
    
    def test_validate_internal_token_with_valid_token(self):
        """Test token validation with valid token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            # Re-import to get updated token
            from shared.auth.middleware import validate_internal_token
            assert validate_internal_token('test-token-12345') is True
    
    def test_validate_internal_token_with_invalid_token(self):
        """Test token validation with invalid token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import validate_internal_token
            assert validate_internal_token('wrong-token') is False
    
    def test_validate_internal_token_with_empty_token(self):
        """Test token validation with empty token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import validate_internal_token
            assert validate_internal_token('') is False
            assert validate_internal_token(None) is False
    
    def test_validate_internal_token_without_env_token(self):
        """Test token validation when INTERNAL_API_TOKEN is not set"""
        with patch.dict(os.environ, {}, clear=True):
            from shared.auth.middleware import validate_internal_token
            assert validate_internal_token('any-token') is False
    
    def test_get_auth_headers_with_token(self):
        """Test getting auth headers when token is configured"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import get_auth_headers
            headers = get_auth_headers()
            expected = {
                "X-Internal-Token": "test-token-12345",
                "Content-Type": "application/json"
            }
            assert headers == expected
    
    def test_get_auth_headers_without_token(self):
        """Test getting auth headers when token is not configured"""
        with patch.dict(os.environ, {}, clear=True):
            from shared.auth.middleware import get_auth_headers
            with pytest.raises(ValueError, match="Internal API token not configured"):
                get_auth_headers()
    
    def test_check_service_auth_with_valid_config(self):
        """Test service auth check with valid configuration"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'a' * 32}):
            from shared.auth.middleware import check_service_auth
            # Should not raise exception
            check_service_auth()
    
    def test_check_service_auth_without_token(self):
        """Test service auth check without token"""
        with patch.dict(os.environ, {}, clear=True):
            from shared.auth.middleware import check_service_auth
            with pytest.raises(AuthenticationError, match="INTERNAL_API_TOKEN environment variable not set"):
                check_service_auth()
    
    def test_check_service_auth_with_short_token(self):
        """Test service auth check with too short token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'short'}):
            from shared.auth.middleware import check_service_auth
            with pytest.raises(AuthenticationError, match="should be at least 32 characters long"):
                check_service_auth()

class TestAuthDecorator:
    """Test the require_internal_auth decorator"""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object"""
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        return request
    
    def test_require_internal_auth_with_valid_token(self, mock_request):
        """Test decorator with valid token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import require_internal_auth
            
            # Mock request with valid token
            mock_request.headers.get.return_value = 'test-token-12345'
            
            @require_internal_auth
            async def test_endpoint(request: Request):
                return {"status": "success"}
            
            # Should execute without raising exception
            import asyncio
            result = asyncio.run(test_endpoint(mock_request))
            assert result == {"status": "success"}
    
    def test_require_internal_auth_with_invalid_token(self, mock_request):
        """Test decorator with invalid token"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import require_internal_auth
            
            # Mock request with invalid token
            mock_request.headers.get.return_value = 'wrong-token'
            
            @require_internal_auth
            async def test_endpoint(request: Request):
                return {"status": "success"}
            
            # Should raise HTTPException
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(test_endpoint(mock_request))
            
            assert exc_info.value.status_code == 401
            assert "Invalid or missing internal API token" in str(exc_info.value.detail)
    
    def test_require_internal_auth_without_token(self, mock_request):
        """Test decorator without token header"""
        with patch.dict(os.environ, {'INTERNAL_API_TOKEN': 'test-token-12345'}):
            from shared.auth.middleware import require_internal_auth
            
            # Mock request without token
            mock_request.headers.get.return_value = None
            
            @require_internal_auth
            async def test_endpoint(request: Request):
                return {"status": "success"}
            
            # Should raise HTTPException
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(test_endpoint(mock_request))
            
            assert exc_info.value.status_code == 401

class TestAuthenticationError:
    """Test custom AuthenticationError exception"""
    
    def test_authentication_error_creation(self):
        """Test creating AuthenticationError"""
        error = AuthenticationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])