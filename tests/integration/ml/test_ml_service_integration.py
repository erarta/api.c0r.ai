"""
Integration tests for ML Service
Tests the complete ML service workflow with real components
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from services.ml.core.models.managers.model_manager import ModelManager
from services.ml.modules.location.detector import UserLocationDetector
from services.ml.core.prompts.base.prompt_builder import PromptBuilder
from services.ml.core.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from services.ml.core.reliability.fallback_manager import FallbackManager, FallbackStrategy


class TestMLServiceIntegration:
    """Integration tests for complete ML service workflow"""
    
    @pytest.fixture
    def model_manager(self):
        """Create ModelManager for integration testing"""
        return ModelManager()
    
    @pytest.fixture
    def location_detector(self):
        """Create UserLocationDetector for integration testing"""
        return UserLocationDetector()
    
    @pytest.fixture
    def prompt_builder(self):
        """Create PromptBuilder for integration testing"""
        return PromptBuilder()
    
    @pytest.fixture
    def sample_image_data(self):
        """Sample image data for testing"""
        return b"fake_image_data_for_testing"
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing"""
        return {
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "goal": "lose_weight",
            "cooking_level": "intermediate",
            "analysis_count": 15
        }
    
    @pytest.fixture
    def sample_telegram_user(self):
        """Sample Telegram user data"""
        return {
            "id": 12345,
            "language_code": "ru",
            "first_name": "Test User"
        }
    
    @pytest.mark.integration
    def test_complete_food_analysis_workflow(self, model_manager, location_detector, prompt_builder, 
                                           sample_image_data, sample_user_profile, sample_telegram_user):
        """Test complete food analysis workflow from location detection to analysis"""
        
        # Mock external dependencies
        with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
            with patch.object(model_manager, '_get_best_provider') as mock_get_provider:
                
                # Setup location detection mock
                from services.ml.modules.location.models import RegionalContext, LocationInfo
                
                mock_location = LocationInfo(
                    country_code="RU",
                    country_name="Russia",
                    city="Moscow",
                    language="ru",
                    confidence=0.9,
                    source="telegram"
                )
                
                mock_context = RegionalContext(
                    region_code="RU",
                    cuisine_types=["Russian", "Eastern European"],
                    common_products=["картофель", "капуста", "морковь", "лук", "мясо"],
                    seasonal_products={
                        "winter": ["капуста", "морковь", "картофель"]
                    },
                    cooking_methods=["варка", "жарка", "тушение"],
                    measurement_units="metric",
                    food_culture_notes="Традиционная русская кухня"
                )
                
                mock_get_context.return_value = mock_context
                
                # Setup model provider mock
                mock_provider = Mock()
                mock_provider.is_available.return_value = True
                
                from services.ml.core.models.providers.base_provider import ModelResponse
                mock_response = ModelResponse(
                    success=True,
                    content=json.dumps({
                        "motivation_message": "Отлично! Продолжайте отслеживать питание!",
                        "food_items": [
                            {
                                "name": "картофель",
                                "weight_grams": 150,
                                "calories": 120,
                                "proteins": 2.5,
                                "fats": 0.1,
                                "carbohydrates": 27,
                                "health_benefits": "Источник углеводов и калия"
                            }
                        ],
                        "total_nutrition": {
                            "calories": 120,
                            "proteins": 2.5,
                            "fats": 0.1,
                            "carbohydrates": 27
                        }
                    }),
                    model_used="gpt-4o",
                    tokens_used=200,
                    cost=0.02
                )
                mock_provider.analyze_food.return_value = mock_response
                mock_get_provider.return_value = mock_provider
                
                # Step 1: Detect user location
                location_result = location_detector.detect_location(
                    user_id=12345,
                    telegram_user=sample_telegram_user
                )
                
                assert location_result is not None
                assert location_result.location.country_code == "RU"
                assert location_result.regional_context.region_code == "RU"
                
                # Step 2: Build regional prompt
                prompt = prompt_builder.build_food_analysis_prompt(
                    user_language="ru",
                    regional_context=location_result.regional_context,
                    user_profile=sample_user_profile
                )
                
                assert prompt is not None
                assert "картофель" in prompt  # Regional products should be in prompt
                assert "русская кухня" in prompt.lower()
                
                # Step 3: Analyze food with model manager
                analysis_result = model_manager.analyze_food(
                    image_data=sample_image_data,
                    user_language="ru",
                    user_context=sample_user_profile,
                    regional_context=location_result.regional_context
                )
                
                assert analysis_result.success is True
                assert analysis_result.model_used == "gpt-4o"
                
                # Verify the complete workflow
                mock_provider.analyze_food.assert_called_once()
                call_args = mock_provider.analyze_food.call_args
                assert call_args[1]["user_language"] == "ru"
                assert call_args[1]["user_context"] == sample_user_profile
    
    @pytest.mark.integration
    def test_recipe_generation_workflow(self, model_manager, location_detector, prompt_builder,
                                      sample_image_data, sample_user_profile, sample_telegram_user):
        """Test complete recipe generation workflow"""
        
        with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
            with patch.object(model_manager, '_get_best_provider') as mock_get_provider:
                
                # Setup mocks
                from services.ml.modules.location.models import RegionalContext
                
                mock_context = RegionalContext(
                    region_code="IT",
                    cuisine_types=["Italian", "Mediterranean"],
                    common_products=["томаты", "базилик", "оливковое масло", "паста"],
                    seasonal_products={
                        "summer": ["томаты", "базилик", "цуккини"]
                    },
                    cooking_methods=["варка", "жарка", "запекание"],
                    measurement_units="metric",
                    food_culture_notes="Итальянская кухня с акцентом на свежесть"
                )
                
                mock_get_context.return_value = mock_context
                
                mock_provider = Mock()
                mock_provider.is_available.return_value = True
                
                from services.ml.core.models.providers.base_provider import ModelResponse
                mock_response = ModelResponse(
                    success=True,
                    content=json.dumps({
                        "recipes": [
                            {
                                "rank": 1,
                                "type": "personal",
                                "name": "Паста с томатами",
                                "suitability_score": 95,
                                "ingredients": [
                                    {"item": "паста", "amount": "100г"},
                                    {"item": "томаты", "amount": "200г"}
                                ]
                            }
                        ]
                    }),
                    model_used="gpt-4o",
                    tokens_used=300,
                    cost=0.03
                )
                mock_provider.generate_recipes.return_value = mock_response
                mock_get_provider.return_value = mock_provider
                
                # Execute workflow
                location_result = location_detector.detect_location(
                    user_id=12345,
                    telegram_user={"id": 12345, "language_code": "it"}
                )
                
                recipe_prompt = prompt_builder.build_recipe_generation_prompt(
                    user_language="ru",
                    regional_context=mock_context,
                    user_profile=sample_user_profile
                )
                
                recipe_result = model_manager.generate_recipes(
                    image_data=sample_image_data,
                    user_language="ru",
                    user_context=sample_user_profile,
                    regional_context=mock_context
                )
                
                assert recipe_result.success is True
                assert "паста" in recipe_result.content.lower()
    
    @pytest.mark.integration
    def test_fallback_mechanism_integration(self, model_manager):
        """Test fallback mechanism in integrated environment"""
        
        # Setup fallback manager
        fallback_manager = FallbackManager("ml_analysis", FallbackStrategy.SEQUENTIAL)
        
        # Primary provider that fails
        def primary_analysis(*args, **kwargs):
            raise Exception("Primary provider failed")
        
        # Fallback provider that succeeds
        def fallback_analysis(*args, **kwargs):
            from services.ml.core.models.providers.base_provider import ModelResponse
            return ModelResponse(
                success=True,
                content="Fallback analysis result",
                model_used="fallback-model",
                tokens_used=100,
                cost=0.01
            )
        
        # Add options to fallback manager
        fallback_manager.add_option("primary", primary_analysis, weight=1.0)
        fallback_manager.add_option("fallback", fallback_analysis, weight=0.8)
        
        # Execute with fallback
        result = fallback_manager.execute(
            image_data=b"test_data",
            user_language="ru",
            user_context={}
        )
        
        assert result.success is True
        assert result.executed_option == "fallback"
        assert result.fallback_used is True
        assert result.result.content == "Fallback analysis result"
    
    @pytest.mark.integration
    def test_circuit_breaker_integration(self, model_manager):
        """Test circuit breaker integration with model manager"""
        
        # Create circuit breaker for model provider
        cb_config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1,
            success_threshold=1
        )
        circuit_breaker = CircuitBreaker("model_provider", cb_config)
        
        # Function that fails initially then succeeds
        call_count = 0
        def unstable_provider(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                raise Exception(f"Provider failure #{call_count}")
            
            from services.ml.core.models.providers.base_provider import ModelResponse
            return ModelResponse(
                success=True,
                content="Analysis after recovery",
                model_used="recovered-model"
            )
        
        # Test circuit breaker behavior
        
        # First two calls should fail and open the circuit
        with pytest.raises(Exception):
            circuit_breaker.call(unstable_provider)
        
        with pytest.raises(Exception):
            circuit_breaker.call(unstable_provider)
        
        # Circuit should now be OPEN
        from services.ml.core.reliability.circuit_breaker import CircuitState, CircuitBreakerOpenException
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenException):
            circuit_breaker.call(unstable_provider)
        
        # Wait for recovery timeout and try again
        import time
        time.sleep(1.1)  # Wait longer than recovery_timeout
        
        # Should transition to HALF_OPEN and succeed
        result = circuit_breaker.call(unstable_provider)
        assert result.success is True
        assert circuit_breaker.state == CircuitState.CLOSED
    
    @pytest.mark.integration
    def test_error_handling_integration(self, model_manager, location_detector):
        """Test error handling across integrated components"""
        
        # Test with invalid user data
        result = location_detector.detect_location(
            user_id=None,  # Invalid user ID
            telegram_user={}  # Empty user data
        )
        
        # Should handle gracefully
        assert result is None
        
        # Test model manager with no providers
        model_manager.providers.clear()  # Remove all providers
        
        analysis_result = model_manager.analyze_food(
            image_data=b"test_data",
            user_language="ru",
            user_context={}
        )
        
        assert analysis_result.success is False
        assert "No providers available" in analysis_result.error_message
    
    @pytest.mark.integration
    def test_performance_under_load(self, model_manager):
        """Test system performance under concurrent load"""
        import threading
        import time
        
        results = []
        errors = []
        
        # Mock provider with variable response time
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        
        def slow_analysis(*args, **kwargs):
            time.sleep(0.1)  # Simulate processing time
            from services.ml.core.models.providers.base_provider import ModelResponse
            return ModelResponse(
                success=True,
                content="Load test analysis",
                model_used="load-test-model"
            )
        
        mock_provider.analyze_food.side_effect = slow_analysis
        model_manager.providers["test_provider"] = mock_provider
        
        def worker():
            try:
                result = model_manager.analyze_food(
                    image_data=b"load_test_data",
                    user_language="ru",
                    user_context={}
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple concurrent requests
        threads = []
        start_time = time.time()
        
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify results
        assert len(results) == 10
        assert len(errors) == 0
        assert all(result.success for result in results)
        
        # Performance should be reasonable (parallel execution)
        assert total_time < 2.0  # Should complete in less than 2 seconds
    
    @pytest.mark.integration
    def test_caching_integration(self, location_detector):
        """Test caching behavior in integrated environment"""
        
        with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
            from services.ml.modules.location.models import RegionalContext
            
            mock_context = RegionalContext(
                region_code="US",
                cuisine_types=["American"],
                common_products=["beef", "chicken"],
                seasonal_products={},
                cooking_methods=["grilling"],
                measurement_units="imperial",
                food_culture_notes="American cuisine"
            )
            mock_get_context.return_value = mock_context
            
            telegram_user = {"id": 12345, "language_code": "en"}
            
            # First call should perform detection
            result1 = location_detector.detect_location(
                user_id=12345,
                telegram_user=telegram_user
            )
            
            # Second call should use cache
            result2 = location_detector.detect_location(
                user_id=12345,
                telegram_user=telegram_user
            )
            
            # Verify both results are identical (from cache)
            assert result1.location.country_code == result2.location.country_code
            assert result1.regional_context.region_code == result2.regional_context.region_code
            
            # Verify cache was used (mock should only be called once)
            assert mock_get_context.call_count == 1
    
    @pytest.mark.integration
    def test_multilingual_support_integration(self, prompt_builder):
        """Test multilingual support across components"""
        
        from services.ml.modules.location.models import RegionalContext
        
        # Test Russian context
        ru_context = RegionalContext(
            region_code="RU",
            cuisine_types=["Russian"],
            common_products=["картофель", "капуста"],
            seasonal_products={},
            cooking_methods=["варка"],
            measurement_units="metric",
            food_culture_notes="Русская кухня"
        )
        
        ru_prompt = prompt_builder.build_food_analysis_prompt(
            user_language="ru",
            regional_context=ru_context,
            user_profile={"goal": "lose_weight"}
        )
        
        # Test English context
        en_context = RegionalContext(
            region_code="US",
            cuisine_types=["American"],
            common_products=["beef", "chicken"],
            seasonal_products={},
            cooking_methods=["grilling"],
            measurement_units="imperial",
            food_culture_notes="American cuisine"
        )
        
        en_prompt = prompt_builder.build_food_analysis_prompt(
            user_language="en",
            regional_context=en_context,
            user_profile={"goal": "lose_weight"}
        )
        
        # Verify language-specific content
        assert "картофель" in ru_prompt
        assert "русская" in ru_prompt.lower() or "russian" in ru_prompt.lower()
        
        assert "beef" in en_prompt
        assert "american" in en_prompt.lower()
        
        # Verify different languages produce different prompts
        assert ru_prompt != en_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])