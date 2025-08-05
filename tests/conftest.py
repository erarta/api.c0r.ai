"""
Pytest configuration and shared fixtures for c0r.AI ML Service tests
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""
    return {
        "test_mode": True,
        "mock_external_apis": True,
        "cache_ttl": 60,  # Shorter TTL for tests
        "timeout": 5.0,   # Shorter timeout for tests
    }


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API responses"""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = {
            "choices": [{
                "message": {
                    "content": '{"analysis": "mock food analysis result"}'
                }
            }],
            "usage": {
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50
            }
        }
        yield mock_create


@pytest.fixture
def mock_requests():
    """Mock requests library for external API calls"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "country": "RU",
            "countryCode": "RU",
            "city": "Moscow",
            "timezone": "Europe/Moscow",
            "status": "success"
        }
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def sample_user_profile():
    """Standard user profile for testing"""
    return {
        "user_id": 12345,
        "dietary_preferences": ["vegetarian"],
        "allergies": ["nuts", "dairy"],
        "goal": "lose_weight",
        "cooking_level": "intermediate",
        "daily_calories_target": 1800,
        "analysis_count": 25,
        "preferred_cuisines": ["italian", "mediterranean"]
    }


@pytest.fixture
def sample_telegram_user():
    """Standard Telegram user data for testing"""
    return {
        "id": 12345,
        "language_code": "ru",
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser"
    }


@pytest.fixture
def sample_location_info():
    """Standard LocationInfo for testing"""
    from services.ml.modules.location.models import LocationInfo
    
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
def sample_regional_context():
    """Standard RegionalContext for testing"""
    from services.ml.modules.location.models import RegionalContext
    
    return RegionalContext(
        region_code="RU",
        cuisine_types=["Russian", "Eastern European"],
        common_products=[
            "картофель", "капуста", "морковь", "лук", "мясо",
            "рыба", "хлеб", "молоко", "яйца", "масло"
        ],
        seasonal_products={
            "spring": ["редис", "зелень", "лук зеленый", "укроп"],
            "summer": ["помидоры", "огурцы", "ягоды", "фрукты"],
            "autumn": ["тыква", "яблоки", "орехи", "грибы"],
            "winter": ["капуста", "морковь", "картофель", "свекла"]
        },
        cooking_methods=["варка", "жарка", "тушение", "запекание", "варка на пару"],
        measurement_units="metric",
        food_culture_notes="Традиционная русская кухня с акцентом на сытные блюда и использование местных продуктов"
    )


@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    return b"fake_image_data_for_testing_purposes"


@pytest.fixture
def mock_model_response():
    """Mock ModelResponse for testing"""
    from services.ml.core.models.providers.base_provider import ModelResponse
    
    return ModelResponse(
        success=True,
        content='{"food_items": [{"name": "test_food", "calories": 100}]}',
        model_used="gpt-4o",
        tokens_used=150,
        cost=0.015,
        response_time=1.2
    )


@pytest.fixture
def mock_failed_model_response():
    """Mock failed ModelResponse for testing"""
    from services.ml.core.models.providers.base_provider import ModelResponse
    
    return ModelResponse(
        success=False,
        content="",
        error_message="API rate limit exceeded",
        model_used="gpt-4o",
        tokens_used=0,
        cost=0.0,
        response_time=0.5
    )


@pytest.fixture
def clean_cache():
    """Fixture to clean caches before and after tests"""
    # Clean before test
    yield
    
    # Clean after test
    try:
        from services.ml.modules.location.detector import LocationDetector
        detector = LocationDetector()
        detector.clear_cache()
    except ImportError:
        pass


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing"""
    test_env = {
        "OPENAI_API_KEY": "test_openai_key",
        "OPENAI_MODEL": "gpt-4o",
        "OPENAI_MAX_TOKENS": "4000",
        "OPENAI_TEMPERATURE": "0.1",
        "CACHE_TTL": "3600",
        "MAX_RETRIES": "3",
        "REQUEST_TIMEOUT": "30",
        "LOG_LEVEL": "DEBUG"
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('services.ml.core.models.managers.model_manager.logger') as mock_log:
        yield mock_log


@pytest.fixture(scope="function")
def isolated_registry():
    """Provide isolated circuit breaker registry for tests"""
    from services.ml.core.reliability.circuit_breaker import CircuitBreakerRegistry
    
    # Create new registry for this test
    registry = CircuitBreakerRegistry()
    
    # Patch the global registry
    with patch('services.ml.core.reliability.circuit_breaker.circuit_breaker_registry', registry):
        yield registry


@pytest.fixture
def mock_time():
    """Mock time.time() for consistent testing"""
    with patch('time.time', return_value=1234567890.0):
        yield 1234567890.0


@pytest.fixture
def performance_monitor():
    """Monitor test performance"""
    import time
    
    start_time = time.time()
    yield
    end_time = time.time()
    
    execution_time = end_time - start_time
    if execution_time > 5.0:  # Warn if test takes longer than 5 seconds
        pytest.warn(f"Test took {execution_time:.2f} seconds - consider optimization")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external_api: mark test as requiring external API"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["load", "performance", "concurrent"]):
            item.add_marker(pytest.mark.slow)


# Custom assertions
def assert_model_response_valid(response):
    """Assert that a ModelResponse is valid"""
    from services.ml.core.models.providers.base_provider import ModelResponse
    
    assert isinstance(response, ModelResponse)
    assert hasattr(response, 'success')
    assert hasattr(response, 'content')
    assert hasattr(response, 'model_used')
    
    if response.success:
        assert response.content is not None
        assert response.model_used is not None
    else:
        assert response.error_message is not None


def assert_location_info_valid(location_info):
    """Assert that LocationInfo is valid"""
    from services.ml.modules.location.models import LocationInfo
    
    assert isinstance(location_info, LocationInfo)
    assert location_info.country_code is not None
    assert location_info.confidence >= 0.0
    assert location_info.confidence <= 1.0
    assert location_info.source is not None


def assert_regional_context_valid(regional_context):
    """Assert that RegionalContext is valid"""
    from services.ml.modules.location.models import RegionalContext
    
    assert isinstance(regional_context, RegionalContext)
    assert regional_context.region_code is not None
    assert isinstance(regional_context.cuisine_types, list)
    assert isinstance(regional_context.common_products, list)
    assert isinstance(regional_context.cooking_methods, list)
    assert regional_context.measurement_units in ["metric", "imperial"]


# Test data generators
def generate_test_user_profiles(count: int = 5):
    """Generate multiple test user profiles"""
    profiles = []
    
    base_profiles = [
        {
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "goal": "lose_weight",
            "cooking_level": "beginner"
        },
        {
            "dietary_preferences": ["vegan"],
            "allergies": ["gluten"],
            "goal": "gain_weight",
            "cooking_level": "advanced"
        },
        {
            "dietary_preferences": ["keto"],
            "allergies": [],
            "goal": "maintain_weight",
            "cooking_level": "intermediate"
        },
        {
            "dietary_preferences": ["paleo"],
            "allergies": ["dairy", "soy"],
            "goal": "lose_weight",
            "cooking_level": "intermediate"
        },
        {
            "dietary_preferences": [],
            "allergies": ["shellfish"],
            "goal": "gain_weight",
            "cooking_level": "beginner"
        }
    ]
    
    for i in range(min(count, len(base_profiles))):
        profile = base_profiles[i].copy()
        profile["user_id"] = 10000 + i
        profile["analysis_count"] = i * 5
        profiles.append(profile)
    
    return profiles


# Cleanup functions
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test"""
    yield
    
    # Clean up any global state
    try:
        # Reset circuit breakers
        from services.ml.core.reliability.circuit_breaker import circuit_breaker_registry
        circuit_breaker_registry.reset_all()
        
        # Clear location cache
        from services.ml.modules.location.detector import LocationDetector
        detector = LocationDetector()
        detector.clear_cache()
        
    except ImportError:
        # Modules might not be available in all test contexts
        pass


# Performance testing utilities
@pytest.fixture
def benchmark():
    """Simple benchmarking fixture"""
    import time
    
    times = {}
    
    def measure(name):
        def decorator(func):
            start = time.time()
            result = func()
            end = time.time()
            times[name] = end - start
            return result
        return decorator
    
    def get_times():
        return times.copy()
    
    measure.get_times = get_times
    return measure


# Database fixtures (if needed for integration tests)
@pytest.fixture
def mock_database():
    """Mock database connection for testing"""
    db_mock = Mock()
    db_mock.execute.return_value = Mock()
    db_mock.fetchall.return_value = []
    db_mock.fetchone.return_value = None
    db_mock.commit.return_value = None
    db_mock.rollback.return_value = None
    
    return db_mock