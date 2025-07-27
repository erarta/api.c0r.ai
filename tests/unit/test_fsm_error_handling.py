"""
FSM error handling and edge cases
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

from app.handlers.photo import photo_handler
from common.supabase_client import get_user_with_profile


class NutritionStates(StatesGroup):
    waiting_for_photo = State()


class RecipeStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMErrorHandling(BaseFSMTest):
    """Test FSM error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_error_handling_clears_state(self, state, mock_message, mock_user_data):
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
    async def test_database_connection_error(self, state, mock_message):
        """Test handling when database connection fails"""
        
        with patch('app.handlers.photo.get_user_with_profile', side_effect=Exception("Database connection failed")):
            # Ensure no state is set
            await state.clear()
            
            # Process photo (should handle database error)
            await photo_handler(mock_message, state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "ошибка" in message_text.lower() or "проблема" in message_text.lower()

    @pytest.mark.asyncio
    async def test_ml_service_timeout(self, state, mock_message, mock_user_data):
        """Test handling when ML service times out"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.photo.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.photo.decrement_credits'), \
             patch('app.handlers.photo.log_user_action'):
            
            # Mock timeout error
            import httpx
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Request timeout")
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Process photo (should handle timeout)
            await photo_handler(mock_message, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify timeout error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "время" in message_text.lower() or "timeout" in message_text.lower()

    @pytest.mark.asyncio
    async def test_invalid_photo_format(self, state, mock_message, mock_user_data):
        """Test handling when photo format is invalid"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data):
            # Mock message with invalid photo
            mock_message.photo = None  # No photo
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Process message without photo
            await photo_handler(mock_message, state)
            
            # Verify appropriate message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "фото" in message_text.lower() or "изображение" in message_text.lower()

    @pytest.mark.asyncio
    async def test_corrupted_photo_handling(self, state, mock_message, mock_user_data):
        """Test handling when photo is corrupted"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', side_effect=Exception("Corrupted file")):
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Process corrupted photo
            await photo_handler(mock_message, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "ошибка" in message_text.lower()

    @pytest.mark.asyncio
    async def test_user_not_found_error(self, state, mock_message):
        """Test handling when user is not found in database"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=None):
            # Ensure no state is set
            await state.clear()
            
            # Process photo for non-existent user
            await photo_handler(mock_message, state)
            
            # Verify appropriate error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "пользователь" in message_text.lower() or "регистрация" in message_text.lower()

    @pytest.mark.asyncio
    async def test_concurrent_state_modifications(self, state, mock_message, mock_user_data):
        """Test handling concurrent state modifications"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.photo.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.photo.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.photo.decrement_credits'), \
             patch('app.handlers.photo.log_user_action'), \
             patch('app.handlers.photo.get_daily_calories_consumed', return_value={"total_calories": 1200}):
            
            # Mock ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "kbzhu": {"calories": 450, "proteins": 25.0, "fats": 15.0, "carbohydrates": 45.0},
                "food_items": [{"name": "Test food", "weight": "100g", "calories": 450}]
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            
            # Simulate concurrent state clearing during processing
            async def clear_state_during_processing(*args, **kwargs):
                await state.clear()
                return mock_response
            
            mock_client.return_value.__aenter__.return_value.post.side_effect = clear_state_during_processing
            
            # Process photo with concurrent state modification
            await photo_handler(mock_message, state)
            
            # Verify final state is cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_memory_storage_overflow(self, state, mock_message, mock_user_data):
        """Test handling when FSM storage has issues"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data):
            # Mock storage error
            state.set_state = AsyncMock(side_effect=Exception("Storage overflow"))
            
            # Try to set state (should handle storage error)
            try:
                await state.set_state(NutritionStates.waiting_for_photo)
            except Exception:
                pass  # Expected to fail
            
            # Process photo (should handle gracefully)
            await photo_handler(mock_message, state)
            
            # Should still send appropriate response
            mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_invalid_state_transition(self, state, mock_message, mock_user_data):
        """Test handling invalid state transitions"""
        
        with patch('app.handlers.photo.get_user_with_profile', return_value=mock_user_data):
            # Set an invalid state manually
            await state.set_state("InvalidState:invalid")
            
            # Process photo with invalid state
            await photo_handler(mock_message, state)
            
            # Should handle gracefully and clear invalid state
            final_state = await state.get_state()
            assert final_state is None
            
            # Should send appropriate message
            mock_message.answer.assert_called()