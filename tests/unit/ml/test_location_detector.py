"""
Unit tests for Location Detector
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from services.ml.modules.location.detector import LocationDetector
from services.ml.modules.location.models import LocationInfo, RegionalContext


class TestLocationDetector:
    """Test LocationDetector functionality"""
    
    @pytest.fixture
    def location_detector(self):
        """Create LocationDetector instance for testing"""
        return LocationDetector()
    
    @pytest.fixture
    def mock_telegram_user(self):
        """Mock Telegram user data"""
        return {
            "id": 12345,
            "language_code": "ru",
            "first_name": "Test User"
        }
    
    @pytest.fixture
    def mock_location_info(self):
        """Mock LocationInfo object"""
        return LocationInfo(
            country_code="RU",
            country_name="Russia",
            city="Moscow",
            region="Moscow",
            timezone="Europe/Moscow",
            language="ru",
            confidence=0.9,
            source="telegram"
        )
    
    @pytest.fixture
    def mock_regional_context(self):
        """Mock RegionalContext object"""
        return RegionalContext(
            region_code="RU",
            cuisine_types=["Russian", "Eastern European"],
            common_products=["картофель", "капуста", "морковь", "лук", "мясо"],
            seasonal_products={
                "spring": ["редис", "зелень", "лук зеленый"],
                "summer": ["помидоры", "огурцы", "ягоды"],
                "autumn": ["тыква", "яблоки", "орехи"],
                "winter": ["капуста", "морковь", "картофель"]
            },
            cooking_methods=["варка", "жарка", "тушение", "запекание"],
            measurement_units="metric",
            food_culture_notes="Традиционная русская кухня с акцентом на сытные блюда"
        )
    
    def test_location_detector_initialization(self, location_detector):
        """Test LocationDetector initialization"""
        assert location_detector is not None
        assert hasattr(location_detector, 'cache')
        assert hasattr(location_detector, 'providers')
        assert location_detector.cache_ttl == 86400  # 24 hours
    
    @patch('services.ml.modules.location.detector.get_regional_context')
    def test_detect_location_from_telegram_success(self, mock_get_context, location_detector, mock_telegram_user, mock_location_info, mock_regional_context):
        """Test successful location detection from Telegram"""
        # Setup mocks
        mock_get_context.return_value = mock_regional_context
        
        with patch.object(location_detector, '_detect_from_telegram') as mock_telegram:
            mock_telegram.return_value = mock_location_info
            
            # Test location detection
            result = location_detector.detect_location(
                user_id=12345,
                telegram_user=mock_telegram_user
            )
            
            # Verify
            assert result is not None
            assert result.location.country_code == "RU"
            assert result.location.source == "telegram"
            assert result.regional_context.region_code == "RU"
            mock_telegram.assert_called_once_with(mock_telegram_user)
    
    def test_detect_location_cached_result(self, location_detector, mock_telegram_user, mock_location_info, mock_regional_context):
        """Test location detection returns cached result"""
        # Setup cache
        cache_key = f"location_12345"
        cached_result = {
            "location": mock_location_info,
            "regional_context": mock_regional_context,
            "timestamp": 1234567890
        }
        location_detector.cache[cache_key] = cached_result
        
        with patch('time.time', return_value=1234567890 + 3600):  # 1 hour later
            result = location_detector.detect_location(
                user_id=12345,
                telegram_user=mock_telegram_user
            )
            
            # Verify cached result is returned
            assert result.location == mock_location_info
            assert result.regional_context == mock_regional_context
    
    def test_detect_location_cache_expired(self, location_detector, mock_telegram_user, mock_location_info, mock_regional_context):
        """Test location detection when cache is expired"""
        # Setup expired cache
        cache_key = f"location_12345"
        cached_result = {
            "location": mock_location_info,
            "regional_context": mock_regional_context,
            "timestamp": 1234567890
        }
        location_detector.cache[cache_key] = cached_result
        
        with patch('time.time', return_value=1234567890 + 90000):  # 25 hours later (expired)
            with patch.object(location_detector, '_detect_from_telegram') as mock_telegram:
                with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
                    mock_telegram.return_value = mock_location_info
                    mock_get_context.return_value = mock_regional_context
                    
                    result = location_detector.detect_location(
                        user_id=12345,
                        telegram_user=mock_telegram_user
                    )
                    
                    # Verify new detection was performed
                    mock_telegram.assert_called_once()
                    assert result.location == mock_location_info
    
    def test_detect_from_telegram_with_language_code(self, location_detector):
        """Test Telegram detection with language code"""
        telegram_user = {
            "id": 12345,
            "language_code": "ru",
            "first_name": "Test User"
        }
        
        result = location_detector._detect_from_telegram(telegram_user)
        
        # Verify
        assert result is not None
        assert result.language == "ru"
        assert result.source == "telegram"
        assert result.confidence > 0.5
    
    def test_detect_from_telegram_without_language_code(self, location_detector):
        """Test Telegram detection without language code"""
        telegram_user = {
            "id": 12345,
            "first_name": "Test User"
        }
        
        result = location_detector._detect_from_telegram(telegram_user)
        
        # Should return None when no language info available
        assert result is None
    
    @patch('requests.get')
    def test_detect_from_ip_success(self, mock_get, location_detector):
        """Test successful IP-based location detection"""
        # Mock IP geolocation response
        mock_response = Mock()
        mock_response.json.return_value = {
            "country": "RU",
            "countryCode": "RU",
            "region": "MOW",
            "regionName": "Moscow",
            "city": "Moscow",
            "timezone": "Europe/Moscow",
            "status": "success"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = location_detector._detect_from_ip("8.8.8.8")
        
        # Verify
        assert result is not None
        assert result.country_code == "RU"
        assert result.city == "Moscow"
        assert result.source == "ip"
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_detect_from_ip_failure(self, mock_get, location_detector):
        """Test IP-based location detection failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = location_detector._detect_from_ip("invalid_ip")
        
        # Should return None on failure
        assert result is None
    
    @patch('requests.get')
    def test_detect_from_ip_exception(self, mock_get, location_detector):
        """Test IP-based location detection with exception"""
        # Mock exception
        mock_get.side_effect = Exception("Network error")
        
        result = location_detector._detect_from_ip("8.8.8.8")
        
        # Should return None on exception
        assert result is None
    
    def test_detect_from_timezone(self, location_detector):
        """Test timezone-based location detection"""
        result = location_detector._detect_from_timezone("Europe/Moscow")
        
        # Verify
        assert result is not None
        assert result.timezone == "Europe/Moscow"
        assert result.source == "timezone"
        assert result.confidence < 0.7  # Lower confidence for timezone-only
    
    def test_detect_from_timezone_invalid(self, location_detector):
        """Test timezone-based detection with invalid timezone"""
        result = location_detector._detect_from_timezone("Invalid/Timezone")
        
        # Should return None for invalid timezone
        assert result is None
    
    def test_detect_from_language(self, location_detector):
        """Test language-based location detection"""
        result = location_detector._detect_from_language("ru")
        
        # Verify
        assert result is not None
        assert result.language == "ru"
        assert result.source == "language"
        assert result.confidence < 0.5  # Lowest confidence
    
    def test_detect_from_language_unsupported(self, location_detector):
        """Test language-based detection with unsupported language"""
        result = location_detector._detect_from_language("xyz")
        
        # Should return None for unsupported language
        assert result is None
    
    def test_fallback_chain_execution(self, location_detector, mock_telegram_user):
        """Test fallback chain execution when primary methods fail"""
        with patch.object(location_detector, '_detect_from_telegram', return_value=None):
            with patch.object(location_detector, '_detect_from_ip', return_value=None):
                with patch.object(location_detector, '_detect_from_timezone', return_value=None):
                    with patch.object(location_detector, '_detect_from_language') as mock_language:
                        mock_location = LocationInfo(
                            country_code="US",
                            country_name="United States",
                            language="en",
                            confidence=0.3,
                            source="language"
                        )
                        mock_language.return_value = mock_location
                        
                        with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
                            mock_context = RegionalContext(
                                region_code="US",
                                cuisine_types=["American"],
                                common_products=["beef", "chicken", "potatoes"],
                                seasonal_products={},
                                cooking_methods=["grilling", "frying"],
                                measurement_units="imperial",
                                food_culture_notes="American cuisine"
                            )
                            mock_get_context.return_value = mock_context
                            
                            result = location_detector.detect_location(
                                user_id=12345,
                                telegram_user=mock_telegram_user,
                                ip_address="8.8.8.8",
                                timezone="America/New_York"
                            )
                            
                            # Verify fallback was used
                            assert result.location.source == "language"
                            assert result.location.confidence == 0.3
    
    def test_cache_management(self, location_detector, mock_location_info, mock_regional_context):
        """Test cache management functionality"""
        user_id = 12345
        
        # Test cache storage
        location_detector._cache_result(user_id, mock_location_info, mock_regional_context)
        
        cache_key = f"location_{user_id}"
        assert cache_key in location_detector.cache
        
        cached_data = location_detector.cache[cache_key]
        assert cached_data["location"] == mock_location_info
        assert cached_data["regional_context"] == mock_regional_context
        assert "timestamp" in cached_data
    
    def test_cache_cleanup(self, location_detector):
        """Test cache cleanup functionality"""
        # Add expired entries
        old_timestamp = 1234567890
        location_detector.cache["location_1"] = {
            "location": Mock(),
            "regional_context": Mock(),
            "timestamp": old_timestamp
        }
        location_detector.cache["location_2"] = {
            "location": Mock(),
            "regional_context": Mock(),
            "timestamp": old_timestamp
        }
        
        # Add fresh entry
        fresh_timestamp = 1234567890 + 3600
        location_detector.cache["location_3"] = {
            "location": Mock(),
            "regional_context": Mock(),
            "timestamp": fresh_timestamp
        }
        
        with patch('time.time', return_value=1234567890 + 90000):  # 25 hours later
            location_detector._cleanup_cache()
            
            # Verify expired entries are removed
            assert "location_1" not in location_detector.cache
            assert "location_2" not in location_detector.cache
            assert "location_3" in location_detector.cache
    
    def test_get_stats(self, location_detector):
        """Test statistics retrieval"""
        # Add some cache entries
        location_detector.cache["location_1"] = {"timestamp": 1234567890}
        location_detector.cache["location_2"] = {"timestamp": 1234567890}
        
        stats = location_detector.get_stats()
        
        # Verify stats structure
        assert "cache_size" in stats
        assert "cache_hit_rate" in stats
        assert "provider_usage" in stats
        assert stats["cache_size"] == 2
    
    def test_clear_cache(self, location_detector):
        """Test cache clearing"""
        # Add cache entries
        location_detector.cache["location_1"] = {"data": "test"}
        location_detector.cache["location_2"] = {"data": "test"}
        
        # Clear cache
        location_detector.clear_cache()
        
        # Verify cache is empty
        assert len(location_detector.cache) == 0
    
    def test_concurrent_detection_requests(self, location_detector, mock_telegram_user):
        """Test handling of concurrent detection requests"""
        import threading
        import time
        
        results = []
        
        def detect_location():
            with patch.object(location_detector, '_detect_from_telegram') as mock_telegram:
                mock_location = LocationInfo(
                    country_code="RU",
                    country_name="Russia",
                    language="ru",
                    confidence=0.8,
                    source="telegram"
                )
                mock_telegram.return_value = mock_location
                
                with patch('services.ml.modules.location.detector.get_regional_context') as mock_get_context:
                    mock_context = RegionalContext(
                        region_code="RU",
                        cuisine_types=["Russian"],
                        common_products=["картофель"],
                        seasonal_products={},
                        cooking_methods=["варка"],
                        measurement_units="metric",
                        food_culture_notes="Russian cuisine"
                    )
                    mock_get_context.return_value = mock_context
                    
                    result = location_detector.detect_location(
                        user_id=12345,
                        telegram_user=mock_telegram_user
                    )
                    results.append(result)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=detect_location)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 3
        assert all(result.location.country_code == "RU" for result in results)
    
    def test_error_handling_and_logging(self, location_detector, mock_telegram_user):
        """Test error handling and logging"""
        with patch.object(location_detector, '_detect_from_telegram', side_effect=Exception("Test error")):
            with patch.object(location_detector, '_detect_from_ip', return_value=None):
                with patch.object(location_detector, '_detect_from_timezone', return_value=None):
                    with patch.object(location_detector, '_detect_from_language', return_value=None):
                        with patch('services.ml.modules.location.detector.logger') as mock_logger:
                            result = location_detector.detect_location(
                                user_id=12345,
                                telegram_user=mock_telegram_user
                            )
                            
                            # Verify error was logged and None returned
                            mock_logger.error.assert_called()
                            assert result is None


if __name__ == "__main__":
    pytest.main([__file__])