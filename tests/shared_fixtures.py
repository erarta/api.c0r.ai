"""
Shared fixtures for all tests
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize

@pytest.fixture
def mock_bot():
    """Create properly configured bot mock"""
    bot = AsyncMock(spec=Bot)
    bot.id = 12345  # Set as property, not mock
    return bot

@pytest_asyncio.fixture
async def storage():
    """Create memory storage for FSM"""
    return MemoryStorage()

@pytest_asyncio.fixture
async def dp(storage):
    """Create dispatcher with memory storage"""
    return Dispatcher(storage=storage)

@pytest_asyncio.fixture
async def state(dp, mock_bot):
    """Create FSM context with proper async handling"""
    storage_key = StorageKey(
        bot_id=mock_bot.id,  # Now this is a real value
        chat_id=123456789,
        user_id=391490
    )
    return FSMContext(storage=dp.storage, key=storage_key)

@pytest.fixture
def mock_user():
    """Create a mock user"""
    user = MagicMock(spec=User)
    user.id = 391490
    user.username = "testuser"
    user.language_code = "ru"
    return user

@pytest.fixture
def mock_chat():
    """Create a mock chat"""
    chat = MagicMock(spec=Chat)
    chat.id = 123456789
    chat.type = "private"
    return chat

@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Create a mock message"""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.message_id = 123
    message.answer = AsyncMock()
    
    # Mock photo
    photo = MagicMock(spec=PhotoSize)
    photo.file_id = "test_file_id"
    photo.file_size = 50000
    message.photo = [photo]
    
    return message

@pytest.fixture
def mock_callback(mock_user, mock_chat):
    """Create a mock callback query"""
    callback = MagicMock(spec=CallbackQuery)
    callback.from_user = mock_user
    callback.message = MagicMock(spec=Message)
    callback.message.chat = mock_chat
    callback.message.message_id = 123
    callback.answer = AsyncMock()
    callback.data = "action_analyze_info"
    return callback

@pytest.fixture
def mock_user_data():
    """Mock user data from database"""
    return {
        'user': {
            'id': 'd4047507-274c-493c-99b5-af801a5b7195',
            'telegram_id': 391490,
            'credits_remaining': 25,
            'total_paid': 0,
            'language': 'ru'
        },
        'profile': {
            'id': 'd357c557-bb1d-4334-a1b6-6c547bff8246',
            'user_id': 'd4047507-274c-493c-99b5-af801a5b7195',
            'age': 38,
            'gender': 'male',
            'height_cm': 170,
            'weight_kg': 69.0,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight',
            'daily_calories_target': 2430,
            'dietary_preferences': ['low_fat', 'low_carb'],
            'allergies': ['sulfites']
        },
        'has_profile': True
    }

@pytest.fixture
def mock_ml_response():
    """Mock ML service response for nutrition analysis"""
    return {
        "kbzhu": {
            "calories": 450,
            "proteins": 25.0,
            "fats": 15.0,
            "carbohydrates": 45.0
        },
        "food_items": [
            {
                "name": "Куриная грудка",
                "weight": "150г",
                "calories": 250
            },
            {
                "name": "Рис",
                "weight": "100г", 
                "calories": 200
            }
        ]
    }

@pytest.fixture
def mock_recipe_response():
    """Mock ML service response for recipe generation"""
    return {
        "recipe": {
            "name": "Куриная грудка с рисом",
            "description": "Полезное блюдо с высоким содержанием белка",
            "ingredients": [
                "Куриная грудка - 150г",
                "Рис - 100г",
                "Оливковое масло - 1 ст.л.",
                "Соль, перец - по вкусу"
            ],
            "instructions": [
                "1. Разогрейте сковороду с оливковым маслом",
                "2. Обжарьте куриную грудку до золотистой корочки",
                "3. Отварите рис согласно инструкции на упаковке",
                "4. Подавайте курицу с рисом"
            ],
            "nutrition": {
                "calories": 450,
                "proteins": 25.0,
                "fats": 15.0,
                "carbohydrates": 45.0
            }
        }
    }