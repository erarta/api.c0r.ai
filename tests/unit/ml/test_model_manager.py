"""
Unit tests for Model Manager
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from services.ml.core.models.managers.model_manager import ModelManager
from services.ml.core.models.config.sota_config import ModelTier, TaskType
from services.ml.core.models.providers.base_provider import ModelResponse


class TestModelManager:
    """Test ModelManager functionality"""
    
    @pytest.fixture
    def model_manager(self):
        """Create ModelManager instance for testing"""
        return ModelManager()
    
    @pytest.fixture
    def mock_openai_provider(self):
        """Mock OpenAI provider"""
        provider = Mock()
        provider.is_available.return_value = True
        provider.get_health_status.return_value = {"status": "healthy"}
        return provider
    
    def test_model_manager_initialization(self, model_manager):
        """Test ModelManager initialization"""
        assert model_manager is not None
        assert hasattr(model_manager, 'providers')
        assert hasattr(model_manager, 'health_stats')
        assert isinstance(model_manager.providers, dict)
    
    @patch('services.ml.core.models.managers.model_manager.OpenAIProvider')
    def test_initialize_providers_success(self, mock_openai_class, model_manager):
        """Test successful provider initialization"""
        # Setup mock
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_openai_class.return_value = mock_provider
        
        # Initialize providers
        model_manager._initialize_providers()
        
        # Verify
        assert "openai" in model_manager.providers
        mock_openai_class.assert_called_once()
    
    @patch('services.ml.core.models.managers.model_manager.OpenAIProvider')
    def test_initialize_providers_failure(self, mock_openai_class, model_manager):
        """Test provider initialization failure handling"""
        # Setup mock to raise exception
        mock_openai_class.side_effect = Exception("API key not found")
        
        # Initialize providers (should not raise exception)
        model_manager._initialize_providers()
        
        # Verify provider not added on failure
        assert "openai" not in model_manager.providers
    
    def test_get_best_provider_with_available_provider(self, model_manager):
        """Test getting best provider when providers are available"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        model_manager.providers["openai"] = mock_provider
        
        # Get best provider
        provider = model_manager._get_best_provider(ModelTier.SOTA, TaskType.FOOD_ANALYSIS)
        
        # Verify
        assert provider == mock_provider
    
    def test_get_best_provider_no_available_providers(self, model_manager):
        """Test getting best provider when no providers are available"""
        # Setup mock provider that's not available
        mock_provider = Mock()
        mock_provider.is_available.return_value = False
        model_manager.providers["openai"] = mock_provider
        
        # Get best provider
        provider = model_manager._get_best_provider(ModelTier.SOTA, TaskType.FOOD_ANALYSIS)
        
        # Verify
        assert provider is None
    
    def test_analyze_food_success(self, model_manager):
        """Test successful food analysis"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        expected_response = ModelResponse(
            success=True,
            content="Mock analysis result",
            model_used="gpt-4o",
            tokens_used=100,
            cost=0.01
        )
        mock_provider.analyze_food.return_value = expected_response
        model_manager.providers["openai"] = mock_provider
        
        # Test food analysis
        result = model_manager.analyze_food(
            image_data=b"fake_image_data",
            user_language="ru",
            user_context={}
        )
        
        # Verify
        assert result.success is True
        assert result.content == "Mock analysis result"
        assert result.model_used == "gpt-4o"
        mock_provider.analyze_food.assert_called_once()
    
    def test_analyze_food_no_providers(self, model_manager):
        """Test food analysis when no providers are available"""
        # No providers available
        result = model_manager.analyze_food(
            image_data=b"fake_image_data",
            user_language="ru",
            user_context={}
        )
        
        # Verify failure response
        assert result.success is False
        assert "No providers available" in result.error_message
    
    def test_generate_recipes_success(self, model_manager):
        """Test successful recipe generation"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        expected_response = ModelResponse(
            success=True,
            content="Mock recipe result",
            model_used="gpt-4o",
            tokens_used=150,
            cost=0.015
        )
        mock_provider.generate_recipes.return_value = expected_response
        model_manager.providers["openai"] = mock_provider
        
        # Test recipe generation
        result = model_manager.generate_recipes(
            image_data=b"fake_image_data",
            user_language="ru",
            user_context={}
        )
        
        # Verify
        assert result.success is True
        assert result.content == "Mock recipe result"
        mock_provider.generate_recipes.assert_called_once()
    
    def test_generate_recipes_provider_failure(self, model_manager):
        """Test recipe generation with provider failure"""
        # Setup mock provider that fails
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.generate_recipes.side_effect = Exception("API Error")
        model_manager.providers["openai"] = mock_provider
        
        # Test recipe generation
        result = model_manager.generate_recipes(
            image_data=b"fake_image_data",
            user_language="ru",
            user_context={}
        )
        
        # Verify failure handling
        assert result.success is False
        assert "API Error" in result.error_message
    
    def test_get_health_status(self, model_manager):
        """Test health status retrieval"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.get_health_status.return_value = {
            "status": "healthy",
            "response_time": 0.5
        }
        model_manager.providers["openai"] = mock_provider
        
        # Get health status
        health = model_manager.get_health_status()
        
        # Verify
        assert "providers" in health
        assert "openai" in health["providers"]
        assert health["providers"]["openai"]["status"] == "healthy"
    
    def test_get_health_status_no_providers(self, model_manager):
        """Test health status when no providers are available"""
        # Get health status with no providers
        health = model_manager.get_health_status()
        
        # Verify
        assert health["overall_status"] == "unhealthy"
        assert health["providers"] == {}
    
    def test_fallback_mechanism(self, model_manager):
        """Test fallback mechanism when primary provider fails"""
        # Setup primary provider that fails
        primary_provider = Mock()
        primary_provider.is_available.return_value = True
        primary_provider.analyze_food.side_effect = Exception("Primary failed")
        
        # Setup fallback provider that succeeds
        fallback_provider = Mock()
        fallback_provider.is_available.return_value = True
        expected_response = ModelResponse(
            success=True,
            content="Fallback analysis",
            model_used="gpt-3.5-turbo",
            tokens_used=80,
            cost=0.008
        )
        fallback_provider.analyze_food.return_value = expected_response
        
        # Add providers (primary first, fallback second)
        model_manager.providers["openai"] = primary_provider
        model_manager.providers["fallback"] = fallback_provider
        
        # Mock _get_best_provider to return providers in order
        with patch.object(model_manager, '_get_best_provider') as mock_get_provider:
            mock_get_provider.side_effect = [primary_provider, fallback_provider]
            
            # Test with fallback
            result = model_manager.analyze_food(
                image_data=b"fake_image_data",
                user_language="ru",
                user_context={}
            )
        
        # Verify fallback was used
        assert result.success is True
        assert result.content == "Fallback analysis"
        primary_provider.analyze_food.assert_called_once()
        fallback_provider.analyze_food.assert_called_once()
    
    def test_model_tier_selection(self, model_manager):
        """Test model tier selection logic"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        model_manager.providers["openai"] = mock_provider
        
        # Test SOTA tier selection
        with patch.object(model_manager, '_get_best_provider') as mock_get_provider:
            mock_get_provider.return_value = mock_provider
            
            model_manager.analyze_food(
                image_data=b"fake_image_data",
                user_language="ru",
                user_context={},
                tier=ModelTier.SOTA
            )
            
            # Verify SOTA tier was requested
            mock_get_provider.assert_called_with(ModelTier.SOTA, TaskType.FOOD_ANALYSIS)
    
    def test_user_context_handling(self, model_manager):
        """Test user context is properly passed to providers"""
        # Setup mock provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.analyze_food.return_value = ModelResponse(
            success=True,
            content="Analysis with context",
            model_used="gpt-4o"
        )
        model_manager.providers["openai"] = mock_provider
        
        # Test with user context
        user_context = {
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "goal": "lose_weight"
        }
        
        result = model_manager.analyze_food(
            image_data=b"fake_image_data",
            user_language="ru",
            user_context=user_context
        )
        
        # Verify context was passed
        call_args = mock_provider.analyze_food.call_args
        assert call_args[1]["user_context"] == user_context
    
    def test_error_handling_and_logging(self, model_manager):
        """Test error handling and logging"""
        # Setup provider that raises unexpected exception
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.analyze_food.side_effect = RuntimeError("Unexpected error")
        model_manager.providers["openai"] = mock_provider
        
        # Test error handling
        with patch('services.ml.core.models.managers.model_manager.logger') as mock_logger:
            result = model_manager.analyze_food(
                image_data=b"fake_image_data",
                user_language="ru",
                user_context={}
            )
            
            # Verify error was logged
            mock_logger.error.assert_called()
            assert result.success is False
    
    def test_concurrent_requests_handling(self, model_manager):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        # Setup mock provider with delay
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        
        def slow_analyze(*args, **kwargs):
            time.sleep(0.1)  # Simulate processing time
            return ModelResponse(
                success=True,
                content="Concurrent analysis",
                model_used="gpt-4o"
            )
        
        mock_provider.analyze_food.side_effect = slow_analyze
        model_manager.providers["openai"] = mock_provider
        
        # Test concurrent requests
        results = []
        threads = []
        
        def make_request():
            result = model_manager.analyze_food(
                image_data=b"fake_image_data",
                user_language="ru",
                user_context={}
            )
            results.append(result)
        
        # Start multiple threads
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 3
        assert all(result.success for result in results)
        assert mock_provider.analyze_food.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])