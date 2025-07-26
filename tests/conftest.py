"""
Global test configuration
"""
import os
import pytest
from dotenv import load_dotenv
from tests.test_utils import setup_test_imports

# Setup imports first
setup_test_imports()

# Load test environment
test_env_path = os.path.join(os.path.dirname(__file__), '.env.test')
if os.path.exists(test_env_path):
    load_dotenv(test_env_path)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('SUPABASE_URL', 'http://localhost:54321')
    os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test_key')
    os.environ.setdefault('YOOKASSA_SHOP_ID', 'test_shop_id')
    os.environ.setdefault('YOOKASSA_SECRET_KEY', 'test_secret_key')
    os.environ.setdefault('ML_SERVICE_URL', 'http://localhost:8001')
    os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test_token')

# Import shared fixtures to make them available globally
pytest_plugins = ["tests.shared_fixtures"]