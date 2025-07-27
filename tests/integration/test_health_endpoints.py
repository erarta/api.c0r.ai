"""
Integration tests for health check endpoints across all services
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi.testclient import TestClient


class TestAPIServiceHealthEndpoint:
    """Test API service health endpoint"""
    
    @patch('services.api.bot.main.ML_SERVICE_URL', 'https://ml.c0r.ai')
    @patch('services.api.bot.main.PAY_SERVICE_URL', 'https://pay.c0r.ai')
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_external_service_health')
    def test_api_health_endpoint_success(self, mock_service_check, mock_db_check):
        """Test API service health endpoint with healthy dependencies"""
        from shared.health import DependencyCheck, HealthStatus
        from services.api.bot.main import app
        
        # Mock healthy dependencies
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_service_check.side_effect = [
            DependencyCheck("ml_service", HealthStatus.HEALTHY, 0.2),
            DependencyCheck("pay_service", HealthStatus.HEALTHY, 0.3)
        ]
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "api.c0r.ai"
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "ml_service" in data["dependencies"]
        assert "pay_service" in data["dependencies"]
        assert data["ml_service_configured"] is True
        assert data["pay_service_configured"] is True
    
    @patch('services.api.bot.main.ML_SERVICE_URL', None)
    @patch('services.api.bot.main.PAY_SERVICE_URL', None)
    @patch('shared.health.check_database_health')
    def test_api_health_endpoint_no_external_services(self, mock_db_check):
        """Test API service health endpoint without external services configured"""
        from shared.health import DependencyCheck, HealthStatus
        from services.api.bot.main import app
        
        # Mock healthy database
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "api.c0r.ai"
        assert data["status"] == "healthy"
        assert data["ml_service_configured"] is False
        assert data["pay_service_configured"] is False
        assert "dependencies" in data
        assert "database" in data["dependencies"]
    
    @patch('services.api.bot.main.ML_SERVICE_URL', 'https://ml.c0r.ai')
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_external_service_health')
    def test_api_health_endpoint_unhealthy_dependency(self, mock_service_check, mock_db_check):
        """Test API service health endpoint with unhealthy dependency"""
        from shared.health import DependencyCheck, HealthStatus
        from services.api.bot.main import app
        
        # Mock unhealthy ML service
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_service_check.return_value = DependencyCheck("ml_service", HealthStatus.UNHEALTHY, error="Connection failed")
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "api.c0r.ai"
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["ml_service"]["status"] == "unhealthy"
        assert data["dependencies"]["ml_service"]["error"] == "Connection failed"
    
    def test_api_health_alias_endpoint(self):
        """Test API service health alias endpoint"""
        from services.api.bot.main import app
        
        with patch('shared.health.check_database_health') as mock_db_check:
            from shared.health import DependencyCheck, HealthStatus
            mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "api.c0r.ai"


class TestMLServiceHealthEndpoint:
    """Test ML service health endpoint"""
    
    @patch('services.ml.main.OPENAI_API_KEY', 'test-key')
    @patch('services.ml.main.GEMINI_API_KEY', 'test-gemini-key')
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_openai_health')
    def test_ml_health_endpoint_success(self, mock_openai_check, mock_db_check):
        """Test ML service health endpoint with healthy dependencies"""
        from shared.health import DependencyCheck, HealthStatus
        from services.ml.main import app
        
        # Mock healthy dependencies
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_openai_check.return_value = DependencyCheck("openai", HealthStatus.HEALTHY, 0.2)
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "ml.c0r.ai"
        assert data["status"] == "healthy"
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "openai" in data["dependencies"]
        assert data["openai_configured"] is True
        assert data["gemini_configured"] is True
        assert data["default_provider"] == "openai"
    
    @patch('services.ml.main.OPENAI_API_KEY', None)
    @patch('services.ml.main.GEMINI_API_KEY', None)
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_openai_health')
    def test_ml_health_endpoint_no_api_keys(self, mock_openai_check, mock_db_check):
        """Test ML service health endpoint without API keys"""
        from shared.health import DependencyCheck, HealthStatus
        from services.ml.main import app
        
        # Mock healthy database but unhealthy OpenAI
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_openai_check.return_value = DependencyCheck("openai", HealthStatus.UNHEALTHY, error="API key not configured")
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "ml.c0r.ai"
        assert data["status"] == "unhealthy"
        assert data["openai_configured"] is False
        assert data["gemini_configured"] is False
        assert data["default_provider"] == "none"
        assert data["dependencies"]["openai"]["status"] == "unhealthy"
    
    def test_ml_health_alias_endpoint(self):
        """Test ML service health alias endpoint"""
        from services.ml.main import app
        
        with patch('shared.health.check_database_health') as mock_db_check, \
             patch('shared.health.check_openai_health') as mock_openai_check:
            from shared.health import DependencyCheck, HealthStatus
            mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
            mock_openai_check.return_value = DependencyCheck("openai", HealthStatus.HEALTHY, 0.2)
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "ml.c0r.ai"


class TestPaymentServiceHealthEndpoint:
    """Test Payment service health endpoint"""
    
    @patch('services.pay.main.API_SERVICE_URL', 'https://api.c0r.ai')
    @patch('os.getenv')
    @patch('shared.health.check_database_health')
    @patch('shared.health.check_external_service_health')
    def test_pay_health_endpoint_success(self, mock_service_check, mock_db_check, mock_getenv):
        """Test Payment service health endpoint with healthy dependencies"""
        from shared.health import DependencyCheck, HealthStatus
        from services.pay.main import app
        
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'YOOKASSA_SHOP_ID': 'test-shop-id',
                'YOOKASSA_SECRET_KEY': 'test-secret',
                'STRIPE_SECRET_KEY': 'test-stripe-key'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock healthy dependencies
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        mock_service_check.return_value = DependencyCheck("api_service", HealthStatus.HEALTHY, 0.2)
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "pay.c0r.ai"
        assert data["status"] == "healthy"
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "api_service" in data["dependencies"]
        assert data["api_service_configured"] is True
        assert data["yookassa_configured"] is True
        assert data["stripe_configured"] is True
        assert "available_plans" in data
    
    @patch('services.pay.main.API_SERVICE_URL', None)
    @patch('os.getenv')
    @patch('shared.health.check_database_health')
    def test_pay_health_endpoint_no_external_services(self, mock_db_check, mock_getenv):
        """Test Payment service health endpoint without external services"""
        from shared.health import DependencyCheck, HealthStatus
        from services.pay.main import app
        
        # Mock no payment providers configured
        mock_getenv.return_value = None
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "pay.c0r.ai"
        assert data["status"] == "healthy"
        assert data["api_service_configured"] is False
        assert data["yookassa_configured"] is False
        assert data["stripe_configured"] is False
    
    def test_pay_health_alias_endpoint(self):
        """Test Payment service health alias endpoint"""
        from services.pay.main import app
        
        with patch('shared.health.check_database_health') as mock_db_check, \
             patch('os.getenv') as mock_getenv:
            from shared.health import DependencyCheck, HealthStatus
            mock_db_check.return_value = DependencyCheck("database", HealthStatus.HEALTHY, 0.1)
            mock_getenv.return_value = None
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "pay.c0r.ai"


class TestHealthEndpointIntegration:
    """Test health endpoint integration scenarios"""
    
    def test_health_response_structure_consistency(self):
        """Test that all services return consistent health response structure"""
        from shared.health import create_health_response, DependencyCheck, HealthStatus
        
        # Test basic response structure
        response = create_health_response("test")
        
        required_fields = ["service", "status", "timestamp", "version"]
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
        
        # Test with dependencies
        dependencies = [DependencyCheck("db", HealthStatus.HEALTHY, 0.1)]
        response_with_deps = create_health_response("test", dependencies=dependencies)
        
        assert "dependencies" in response_with_deps
        assert "db" in response_with_deps["dependencies"]
        assert "status" in response_with_deps["dependencies"]["db"]
    
    @patch('shared.health.check_database_health')
    def test_database_connectivity_across_services(self, mock_db_check):
        """Test database connectivity check across all services"""
        from shared.health import DependencyCheck, HealthStatus
        
        # Mock database failure
        mock_db_check.return_value = DependencyCheck("database", HealthStatus.UNHEALTHY, error="Connection failed")
        
        # Test each service handles database failure gracefully
        services = [
            ('services.api.bot.main', 'api.c0r.ai'),
            ('services.ml.main', 'ml.c0r.ai'),
            ('services.pay.main', 'pay.c0r.ai')
        ]
        
        for service_module, expected_service_name in services:
            try:
                module = __import__(service_module, fromlist=['app'])
                app = module.app
                client = TestClient(app)
                
                with patch('shared.health.check_external_service_health'), \
                     patch('shared.health.check_openai_health'):
                    response = client.get("/")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["service"] == expected_service_name
                    assert data["status"] == "unhealthy"
                    assert "dependencies" in data
                    assert data["dependencies"]["database"]["status"] == "unhealthy"
                    
            except ImportError:
                # Skip if service module not available in test environment
                continue


if __name__ == "__main__":
    pytest.main([__file__])