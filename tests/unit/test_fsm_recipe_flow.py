"""
FSM recipe generation workflow tests
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
from app.handlers.recipe import process_recipe_photo
from common.supabase_client import get_user_with_profile, decrement_credits, log_user_action
from app.utils.r2 import upload_telegram_photo


class RecipeStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMRecipeFlow(BaseFSMTest):
    """Test recipe generation FSM workflow"""
    
    @pytest.mark.asyncio
    async def test_enter_recipe_state_and_get_recipe(self, state, mock_message, mock_user_data, mock_recipe_response):
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
    async def test_exit_recipe_state(self, state, mock_callback, mock_user_data):
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
    async def test_recipe_generation_with_dietary_preferences(self, state, mock_message, mock_user_data, mock_recipe_response):
        """Test recipe generation considers user dietary preferences"""
        
        # Mock user with specific dietary preferences
        user_with_preferences = mock_user_data.copy()
        user_with_preferences['profile']['dietary_preferences'] = ['vegetarian', 'gluten_free']
        user_with_preferences['profile']['allergies'] = ['nuts', 'dairy']
        
        with patch('app.handlers.recipe.get_user_with_profile', return_value=user_with_preferences), \
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
            
            # Process photo in recipe generation state
            await process_recipe_photo(mock_message, state)
            
            # Verify ML service was called with dietary preferences
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            
            # Check that request includes dietary preferences
            request_data = call_args[1]['json']
            assert 'dietary_preferences' in request_data or 'preferences' in request_data

    @pytest.mark.asyncio
    async def test_recipe_generation_failure_handling(self, state, mock_message, mock_user_data):
        """Test handling when recipe generation fails"""
        
        with patch('app.handlers.recipe.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.recipe.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.recipe.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.recipe.decrement_credits'), \
             patch('app.handlers.recipe.log_user_action'):
            
            # Mock failed ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Service unavailable"}
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            
            # Process photo (should handle error gracefully)
            await process_recipe_photo(mock_message, state)
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "ошибка" in message_text.lower() or "error" in message_text.lower()

    @pytest.mark.asyncio
    async def test_recipe_state_with_no_profile(self, state, mock_message):
        """Test recipe generation when user has no profile"""
        
        # Mock user without profile
        user_no_profile = {
            'user': {
                'id': 'd4047507-274c-493c-99b5-af801a5b7195',
                'telegram_id': 391490,
                'credits_remaining': 25,
                'language': 'ru'
            },
            'profile': None,
            'has_profile': False
        }
        
        with patch('app.handlers.recipe.get_user_with_profile', return_value=user_no_profile), \
             patch('app.handlers.recipe.upload_telegram_photo', return_value="https://example.com/photo.jpg"), \
             patch('app.handlers.recipe.httpx.AsyncClient') as mock_client, \
             patch('app.handlers.recipe.decrement_credits'), \
             patch('app.handlers.recipe.log_user_action'):
            
            # Mock ML service response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "recipe": {
                    "name": "Простой рецепт",
                    "description": "Базовый рецепт без учета предпочтений",
                    "ingredients": ["Основные ингредиенты"],
                    "instructions": ["Базовые инструкции"]
                }
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            
            # Process photo
            await process_recipe_photo(mock_message, state)
            
            # Verify ML service was called without dietary preferences
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            
            # Check that request doesn't include dietary preferences
            request_data = call_args[1]['json']
            assert 'dietary_preferences' not in request_data or not request_data.get('dietary_preferences')

    @pytest.mark.asyncio
    async def test_recipe_upload_failure_handling(self, state, mock_message, mock_user_data):
        """Test handling when photo upload fails during recipe generation"""
        
        with patch('app.handlers.recipe.get_user_with_profile', return_value=mock_user_data), \
             patch('app.handlers.recipe.upload_telegram_photo', side_effect=Exception("Upload failed")), \
             patch('app.handlers.recipe.decrement_credits'), \
             patch('app.handlers.recipe.log_user_action'):
            
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            
            # Process photo (should handle upload error)
            await process_recipe_photo(mock_message, state)
            
            # Verify state was cleared even after error
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args
            message_text = call_args[0][0]
            assert "ошибка" in message_text.lower() or "error" in message_text.lower()