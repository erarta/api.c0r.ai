"""
Comprehensive FSM State Management Tests

This test suite covers all FSM state transitions, photo processing scenarios,
and user interactions to ensure the bot behaves correctly in all situations.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api.c0r.ai'))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize
from aiogram.fsm.state import State, StatesGroup

# Import the handlers we need to test
from app.handlers.commands import handle_action_callback
from app.handlers.photo import photo_handler, process_nutrition_analysis
from app.handlers.recipe import process_recipe_photo
from app.handlers.nutrition import process_nutrition_photo
from app.common.supabase_client import get_user_with_profile, decrement_credits, log_user_action
from app.utils.r2 import upload_telegram_photo


class NutritionStates(StatesGroup):
    waiting_for_photo = State()


class RecipeStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMStateManagement:
    """Comprehensive FSM state management test suite"""
    
    @pytest.fixture
    async def bot(self):
        """Create a mock bot instance"""
        return AsyncMock(spec=Bot)
    
    @pytest.fixture
    async def storage(self):
        """Create a memory storage for FSM"""
        return MemoryStorage()
    
    @pytest.fixture
    async def dp(self, storage):
        """Create a dispatcher with memory storage"""
        return Dispatcher(storage=storage)
    
    @pytest.fixture
    async def state(self, dp, bot):
        """Create FSM context"""
        from aiogram.fsm.storage.base import StorageKey
        storage_key = StorageKey(
            bot_id=bot.id,
            chat_id=123456789,
            user_id=391490
        )
        return FSMContext(storage=dp.storage, key=storage_key)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = MagicMock(spec=User)
        user.id = 391490
        user.username = "testuser"
        return user
    
    @pytest.fixture
    def mock_chat(self):
        """Create a mock chat"""
        chat = MagicMock(spec=Chat)
        chat.id = 123456789
        chat.type = "private"
        return chat
    
    @pytest.fixture
    def mock_message(self, mock_user, mock_chat):
        """Create a mock message"""
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.chat = mock_chat
        message.message_id = 123
        
        # Mock photo
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "test_file_id"
        photo.file_size = 50000
        message.photo = [photo]
        
        return message
    
    @pytest.fixture
    def mock_callback(self, mock_user, mock_chat):
        """Create a mock callback query"""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        callback.message.chat = mock_chat
        callback.message.message_id = 123
        callback.data = "action_analyze_info"
        return callback
    
    @pytest.fixture
    def mock_user_data(self):
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
    def mock_ml_response(self):
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
    def mock_recipe_response(self):
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

    @pytest.mark.asyncio
    async def test_enter_analyze_state_and_get_analysis(self, dp, state, mock_message, mock_user_data, mock_ml_response):
        """Test entering nutrition analysis state and processing photo"""
        
        # Mock all external dependencies
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.photo.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.photo.decrement_credits'), \
             patch('app.handlers.photo.log_user_action'), \
             patch('app.handlers.photo.get_daily_calories_consumed', return_value={"total_calories": 1200}):
            
            # Mock ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_ml_response
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"
            
            # Process photo in nutrition analysis state
            await photo_handler(mock_message, state)
            
            # Verify state was cleared after processing
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify ML service was called with correct parameters
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert "/api/v1/analyze" in call_args[0][0]  # URL contains correct endpoint
            
            # Verify credits were decremented
            from app.handlers.photo import decrement_credits
            decrement_credits.assert_called_once_with(391490)

    @pytest.mark.asyncio
    async def test_exit_analyze_state(self, dp, state, mock_callback, mock_user_data):
        """Test exiting nutrition analysis state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"
            
            # Call main menu to exit state
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_no_state_choice_message(self, dp, state, mock_message, mock_user_data):
        """Test that when no state is set, user gets choice message"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set
            await state.clear()
            current_state = await state.get_state()
            assert current_state is None
            
            # Process photo without state
            await photo_handler(mock_message, state)
            
            # Verify choice message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            
            # Check that choice message contains expected text
            assert "Что вы хотите сделать с этим фото?" in message_text
            assert "🍕 Анализ еды" in message_text
            assert "🍽️ Создать рецепт" in message_text

    @pytest.mark.asyncio
    async def test_enter_recipe_state_and_get_recipe(self, dp, state, mock_message, mock_user_data, mock_recipe_response):
        """Test entering recipe generation state and processing photo"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.recipe.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.recipe.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.recipe.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.recipe.decrement_credits'), \
             patch('app.handlers.recipe.log_user_action'):
            
            # Mock ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_recipe_response
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            current_state = await state.get_state()
            assert current_state == "RecipeStates:waiting_for_photo"
            
            # Process photo in recipe generation state
            await process_recipe_photo(mock_message, state)
            
            # Verify ML service was called
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            
            # Verify credits were decremented
            from app.handlers.recipe import decrement_credits
            decrement_credits.assert_called_once_with(391490)

    @pytest.mark.asyncio
    async def test_exit_recipe_state(self, dp, state, mock_callback, mock_user_data):
        """Test exiting recipe generation state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            current_state = await state.get_state()
            assert current_state == "RecipeStates:waiting_for_photo"
            
            # Call main menu to exit state
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_analyze_button_sets_correct_state(self, dp, state, mock_callback, mock_user_data):
        """Test that analyze button sets nutrition analysis state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set initially
            await state.clear()
            assert await state.get_state() is None
            
            # Call analyze button
            mock_callback.data = "action_analyze_info"
            await handle_action_callback(mock_callback, state)
            
            # Verify nutrition analysis state was set
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"

    @pytest.mark.asyncio
    async def test_recipe_button_sets_correct_state(self, dp, state, mock_callback, mock_user_data):
        """Test that recipe button sets recipe generation state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set initially
            await state.clear()
            assert await state.get_state() is None
            
            # Call recipe button
            mock_callback.data = "action_recipe"
            await handle_action_callback(mock_callback, state)
            
            # Verify recipe generation state was set
            current_state = await state.get_state()
            assert current_state == "RecipeStates:waiting_for_photo"

    @pytest.mark.asyncio
    async def test_cancel_button_clears_state(self, dp, state, mock_callback, mock_user_data):
        """Test that cancel button clears any active state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            assert await state.get_state() == "NutritionStates:waiting_for_photo"
            
            # Call cancel button
            mock_callback.data = "action_cancel"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_back_button_clears_state(self, dp, state, mock_callback, mock_user_data):
        """Test that back button clears any active state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            assert await state.get_state() == "RecipeStates:waiting_for_photo"
            
            # Call back button
            mock_callback.data = "action_back"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_insufficient_credits_handling(self, dp, state, mock_message):
        """Test handling when user has insufficient credits"""
        
        # Mock user with no credits
        no_credits_user_data = {
            'user': {
                'id': 'd4047507-274c-493c-99b5-af801a5b7195',
                'telegram_id': 391490,
                'credits_remaining': 0,
                'total_paid': 0,
                'language': 'ru'
            },
            'profile': None,
            'has_profile': False
        }
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=no_credits_user_data):
            # Ensure no state is set
            await state.clear()
            
            # Process photo without state
            await photo_handler(mock_message, state)
            
            # Verify payment options message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            
            # Check that payment message contains expected text
            assert "кредитов" in message_text.lower()
            assert "план" in message_text.lower()

    @pytest.mark.asyncio
    async def test_photo_size_limit_handling(self, dp, state, mock_message, mock_user_data):
        """Test handling when photo exceeds size limit"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set
            await state.clear()
            
            # Mock oversized photo
            mock_message.photo[-1].file_size = 15 * 1024 * 1024  # 15MB
            
            # Process oversized photo
            await photo_handler(mock_message, state)
            
            # Verify size limit message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            
            # Check that size limit message contains expected text
            assert "слишком большое" in message_text.lower()
            assert "10MB" in message_text

    @pytest.mark.asyncio
    async def test_state_transition_flow(self, dp, state, mock_callback, mock_user_data):
        """Test complete state transition flow"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # 1. Start with no state
            await state.clear()
            assert await state.get_state() is None
            
            # 2. Enter nutrition analysis state
            mock_callback.data = "action_analyze_info"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() == "NutritionStates:waiting_for_photo"
            
            # 3. Exit to main menu
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() is None
            
            # 4. Enter recipe generation state
            mock_callback.data = "action_recipe"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() == "RecipeStates:waiting_for_photo"
            
            # 5. Exit to main menu
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() is None

    @pytest.mark.asyncio
    async def test_error_handling_clears_state(self, dp, state, mock_message, mock_user_data):
        """Test that errors during processing clear the state"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', side_effect=Exception("Upload failed")):
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            assert await state.get_state() == "NutritionStates:waiting_for_photo"
            
            # Process photo (should fail)
            await photo_handler(mock_message, state)
            
            # Verify state was cleared even after error
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "ошибка" in message_text.lower()

    @pytest.mark.asyncio
    async def test_multiple_photos_in_same_state(self, dp, state, mock_message, mock_user_data, mock_ml_response):
        """Test processing multiple photos in the same state"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.photo.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.photo.decrement_credits'), \
             patch('app.handlers.photo.log_user_action'), \
             patch('app.handlers.photo.get_daily_calories_consumed', return_value={"total_calories": 1200}):
            
            # Mock ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_ml_response
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Process first photo
            await photo_handler(mock_message, state)
            
            # Verify state was cleared after first photo
            assert await state.get_state() is None
            
            # Set state again for second photo
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Process second photo
            await photo_handler(mock_message, state)
            
            # Verify state was cleared after second photo
            assert await state.get_state() is None
            
            # Verify ML service was called twice
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 2 