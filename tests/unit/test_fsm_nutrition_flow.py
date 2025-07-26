"""
FSM nutrition analysis workflow tests
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tests.test_utils import setup_test_imports
from tests.base_test_classes import BaseFSMTest
from tests.shared_fixtures import *

# Ensure proper imports
setup_test_imports()

from app.handlers.commands import handle_action_callback
from app.handlers.photo import photo_handler, process_nutrition_analysis
from app.handlers.nutrition import process_nutrition_photo
from common.supabase_client import get_user_with_profile, decrement_credits, log_user_action
from app.utils.r2 import upload_telegram_photo


class NutritionStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMNutritionFlow(BaseFSMTest):
    """Test nutrition analysis FSM workflow"""
    
    @pytest.mark.asyncio
    async def test_enter_analyze_state_and_get_analysis(self, state, mock_message, mock_user_data, mock_ml_response):
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
    async def test_exit_analyze_state(self, state, mock_callback, mock_user_data):
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
    async def test_no_state_choice_message(self, state, mock_message, mock_user_data):
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
    async def test_multiple_photos_in_same_state(self, state, mock_message, mock_user_data, mock_ml_response):
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

    @pytest.mark.asyncio
    async def test_insufficient_credits_handling(self, state, mock_message):
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
    async def test_photo_size_limit_handling(self, state, mock_message, mock_user_data):
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