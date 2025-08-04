"""
Unit tests for enhanced health check system
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.health import (
    HealthStatus,
    DependencyCheck,
    create_health_response,
    create_comprehensive_health_response,
    check_database_health,
    check_external_service_health,
    check_openai_health
)


class TestDependencyCheck:
    """Test DependencyCheck class"""
    
    def test_dependency_check_creation(self):
        """Test DependencyCheck object creation"""
        check = DependencyCheck("test_service", HealthStatus.HEALTHY, 0.5)
        
        assert check.name == "test_service"
        assert check.status == HealthStatus.HEALTHY
        assert check.response_time == 0.5
        assert check.error is None
    
    def test_dependency_check_with_error(self):
        """Test DependencyCheck with error"""
        check = DependencyCheck("test_service", HealthStatus.UNHEALTHY, error="Connection failed")
        
        assert check.name == "test_service"
        assert check.status == HealthStatus.UNHEALTHY
        assert check.error == "Connection failed"
    
    def test_dependency_check_to_dict(self):
        """Test DependencyCheck to_dict conversion"""
        check = DependencyCheck("test_service", HealthStatus.HEALTHY, 0.123)
        result = check.to_dict()
        
        expected = {
            "status": HealthStatus.HEALTHY,
            "response_time_ms": 123.0
        }
        assert result == expected
    
    def test_dependency_check_to_dict_with_error(self):
        """Test DependencyCheck to_dict with error"""
        check = DependencyCheck("test_service", HealthStatus.UNHEALTHY, error="Failed")
        result = check.to_dict()
        
        expected = {
            "status": HealthStatus.UNHEALTHY,
            "error": "Failed"
        }
        assert result == expected


class TestHealthResponse:
    """Test health response creation"""
    
    def test_basic_health_response(self):
        """Test basic health response creation"""
        response = create_health_response("test")
        
        assert response["service"] == "test.c0r.ai"
        assert response["status"] == HealthStatus.HEALTHY
        assert "timestamp" in response
        assert "version" in response
    
    def test_health_response_with_additional_info(self):
        """Test health response with additional information"""
        additional_info = {"custom_field": "custom_value"}
        response = create_health_response("test", additional_info)
        
        assert response["service"] == "test.c0r.ai"
        assert response["custom_field"] == "custom_value"
    
    def test_health_response_with_healthy_dependencies(self):
        """Test health response with healthy dependencies"""
        dependencies = [
            DependencyCheck("db", HealthStatus.HEALTHY, 0.1),
            DependencyCheck("api", HealthStatus.HEALTHY, 0.2)
        ]
        
        response = create_health_response("test", dependencies=dependencies)
        
        assert response["status"] == HealthStatus.HEALTHY
        assert "dependencies" in response
        assert "db" in response["dependencies"]
        assert "api" in response["dependencies"]
        assert response["dependencies"]["db"]["status"] == HealthStatus.HEALTHY
    
    def test_health_response_with_unhealthy_dependencies(self):
        """Test health response with unhealthy dependencies"""
        dependencies = [
            DependencyCheck("db", HealthStatus.HEALTHY, 0.1),
            DependencyCheck("api", HealthStatus.UNHEALTHY, error="Connection failed")
        ]
        
        response = create_health_response("test", dependencies=dependencies)
        
        assert response["status"] == HealthStatus.UNHEALTHY
        assert response["dependencies"]["api"]["status"] == HealthStatus.UNHEALTHY
        assert response["dependencies"]["api"]["error"] == "Connection failed"
    
    def test_health_response_with_degraded_dependencies(self):
        """Test health response with degraded dependencies"""
        dependencies = [
            DependencyCheck("db", HealthStatus.HEALTHY, 0.1),
            DependencyCheck("cache", HealthStatus.DEGRADED, 2.0)
        ]
        
        response = create_health_response("test", dependencies=dependencies)
        
        assert response["status"] == HealthStatus.DEGRADED


class TestDatabaseHealthCheck:
    """Test database health check functionality"""
    
    @patch('common.supabase_client.supabase')
    @pytest.mark.asyncio
    async def test_database_health_check_success(self, mock_supabase):
        """Test successful database health check"""
        # Mock successful database response
        mock_result = MagicMock()
        mock_result.data = [{"id": 1}]
        mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result
        
        result = await check_database_health()
        
        assert result.name == "database"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time is not None
        assert result.error is None
    
    @patch('common.supabase_client.supabase')
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self, mock_supabase):
        """Test failed database health check"""
        # Mock database exception
        mock_supabase.table.side_effect = Exception("Connection failed")
        
        result = await check_database_health()
        
        assert result.name == "database"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error == "Connection failed"


class TestExternalServiceHealthCheck:
    """Test external service health check functionality"""
    
    @patch('shared.health.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_external_service_health_check_success(self, mock_client):
        """Test successful external service health check"""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await check_external_service_health("test_service", "https://example.com")
        
        assert result.name == "test_service"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time is not None
    
    @patch('shared.health.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_external_service_health_check_http_error(self, mock_client):
        """Test external service health check with HTTP error"""
        # Mock HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await check_external_service_health("test_service", "https://example.com")
        
        assert result.name == "test_service"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error == "HTTP 500"
    
    @patch('shared.health.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_external_service_health_check_exception(self, mock_client):
        """Test external service health check with exception"""
        # Mock connection exception
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Connection timeout")
        
        result = await check_external_service_health("test_service", "https://example.com")
        
        assert result.name == "test_service"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error == "Connection timeout"


class TestOpenAIHealthCheck:
    """Test OpenAI health check functionality"""
    
    @patch('shared.health.os.getenv')
    @pytest.mark.asyncio
    async def test_openai_health_check_no_api_key(self, mock_getenv):
        """Test OpenAI health check without API key"""
        mock_getenv.return_value = None
        
        result = await check_openai_health()
        
        assert result.name == "openai"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error == "API key not configured"
    
    @patch('shared.health.os.getenv')
    @patch('shared.health.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_openai_health_check_success(self, mock_client, mock_getenv):
        """Test successful OpenAI health check"""
        mock_getenv.return_value = "test-api-key"
        
        # Mock successful OpenAI API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await check_openai_health()
        
        assert result.name == "openai"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time is not None


class TestComprehensiveHealthResponse:
    """Test comprehensive health response creation"""
    
    @patch('shared.health.check_database_health')
    @pytest.mark.asyncio
    async def test_comprehensive_health_response_basic(self, mock_db_check):
        """Test basic comprehensive health response"""
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        
        response = await create_comprehensive_health_response("test", check_database=True)
        
        assert response["service"] == "test.c0r.ai"
        assert response["status"] == HealthStatus.HEALTHY
        assert "dependencies" in response
        assert "database" in response["dependencies"]
    
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_external_service_health')
    @patch('shared.health.check_openai_health')
    @pytest.mark.asyncio
    async def test_comprehensive_health_response_full(self, mock_openai_check, mock_service_check, mock_db_check):
        """Test comprehensive health response with all checks"""
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_service_check.return_value = DependencyCheck("external_service", HealthStatus.HEALTHY, 0.2)
        mock_openai_check.return_value = DependencyCheck("openai", HealthStatus.HEALTHY, 0.3)
        
        response = await create_comprehensive_health_response(
            "test",
            check_database=True,
            check_external_services={"external_service": "https://example.com"},
            check_openai=True,
            additional_info={"custom": "info"}
        )
        
        assert response["service"] == "test.c0r.ai"
        assert response["status"] == HealthStatus.HEALTHY
        assert response["custom"] == "info"
        assert len(response["dependencies"]) == 3
        assert "database" in response["dependencies"]
        assert "external_service" in response["dependencies"]
        assert "openai" in response["dependencies"]


if __name__ == "__main__":
    pytest.main([__file__])