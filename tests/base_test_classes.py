"""
Base test classes with common functionality
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize
from tests.test_utils import setup_test_imports

# Ensure proper imports
setup_test_imports()

class BaseHandlerTest:
    """Base class for handler tests"""
    
    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = 391490
        user.username = "testuser"
        user.language_code = "ru"
        return user
    
    @pytest.fixture
    def mock_chat(self):
        chat = MagicMock(spec=Chat)
        chat.id = 123456789
        chat.type = "private"
        return chat
    
    @pytest.fixture
    def mock_message(self, mock_user, mock_chat):
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.chat = mock_chat
        message.message_id = 123
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_callback(self, mock_user, mock_chat):
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        callback.message = MagicMock(spec=Message)
        callback.message.chat = mock_chat
        callback.answer = AsyncMock()
        return callback

class BaseFSMTest(BaseHandlerTest):
    """Base class for FSM-related tests"""
    
    @pytest.fixture
    def mock_user_data(self):
        return {
            'user': {
                'id': 'd4047507-274c-493c-99b5-af801a5b7195',
                'telegram_id': 391490,
                'credits_remaining': 25,
                'language': 'ru'
            },
            'profile': {
                'age': 38,
                'gender': 'male',
                'height_cm': 170,
                'weight_kg': 69.0,
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight'
            },
            'has_profile': True
        }

class BaseIntegrationTest:
    """Base class for integration tests"""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client for integration tests"""
        client = MagicMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        return client
    
    @pytest.fixture
    def mock_external_service_response(self):
        """Mock external service response"""
        return {
            'status': 'success',
            'data': {'result': 'test_result'}
        }