"""
Test FSM states for recipe generation functionality
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize

from tests.test_utils import setup_test_imports
from tests.base_test_classes import BaseFSMTest
from tests.shared_fixtures import *

# Ensure proper imports
setup_test_imports()

from app.handlers.recipe import RecipeStates, handle_recipe_callback, process_recipe_photo
from app.handlers.keyboards import create_main_menu_keyboard


class TestRecipeFSMStates(BaseFSMTest):
    """Test recipe generation FSM states and transitions"""
    
    @pytest.mark.asyncio
    async def test_recipe_callback_sets_waiting_photo_state(self, mock_callback, state):
        """Test that recipe callback sets FSM state to waiting for photo"""
        with patch('app.handlers.recipe.supabase') as mock_supabase:
            # Mock user with credits
            mock_supabase.table().select().eq().execute.return_value.data = [
                {'id': 391490, 'credits_remaining': 5}
            ]
            
            # Call handler
            await handle_recipe_callback(mock_callback, state)
            
            # Verify state was set to waiting for photo
            current_state = await state.get_state()
            assert current_state == "RecipeStates:waiting_for_photo"
            
            # Verify callback was answered
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_callback_insufficient_credits(self, mock_callback, state):
        """Test recipe callback when user has insufficient credits"""
        with patch('app.handlers.recipe.supabase') as mock_supabase:
            # Mock user with no credits
            mock_supabase.table().select().eq().execute.return_value.data = [
                {'id': 391490, 'credits_remaining': 0}
            ]
            
            # Call handler
            await handle_recipe_callback(mock_callback, state)
            
            # Verify state was NOT set
            current_state = await state.get_state()
            assert current_state is None
            
            # Verify callback was answered
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_callback_user_not_found(self, mock_callback, state):
        """Test recipe callback when user is not found in database"""
        with patch('app.handlers.recipe.supabase') as mock_supabase:
            # Mock empty user data
            mock_supabase.table().select().eq().execute.return_value.data = []
            
            # Call handler
            await handle_recipe_callback(mock_callback, state)
            
            # Verify state was NOT set
            current_state = await state.get_state()
            assert current_state is None
            
            # Verify callback was answered
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_valid_state(self, mock_message, state, mock_user_data):
        """Test recipe photo handler when in correct FSM state"""
        # Set FSM state as waiting for photo
        await state.set_state(RecipeStates.waiting_for_photo)
        
        with patch('app.handlers.recipe.supabase') as mock_supabase, \
             patch('app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
             patch('app.handlers.recipe.bot') as mock_bot:
            
            # Mock successful upload
            mock_upload.return_value = 'https://r2.example.com/photo.jpg'
            
            # Mock successful recipe generation
            mock_generate.return_value = {
                'recipe': 'Test recipe content',
                'success': True
            }
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data['user']]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await process_recipe_photo(mock_message, state)
            
            # Verify state was cleared after processing
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify photo was uploaded
            mock_upload.assert_called_once()
            
            # Verify recipe was generated
            mock_generate.assert_called_once()
            
            # Verify response was sent
            mock_message.answer.assert_called()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_wrong_state(self, mock_message, state):
        """Test recipe photo handler when not in correct FSM state"""
        # Ensure no state is set
        await state.clear()
        
        # Call handler
        await process_recipe_photo(mock_message, state)
        
        # Verify no processing occurred (should handle gracefully)
        final_state = await state.get_state()
        assert final_state is None
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_no_photo(self, mock_message, state):
        """Test recipe photo handler when message has no photo"""
        # Set FSM state as waiting for photo
        await state.set_state(RecipeStates.waiting_for_photo)
        
        # Remove photo from message
        mock_message.photo = None
        
        # Call handler
        await process_recipe_photo(mock_message, state)
        
        # Verify state was cleared
        final_state = await state.get_state()
        assert final_state is None
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_upload_failure(self, mock_message, state, mock_user_data):
        """Test recipe photo handler when photo upload fails"""
        # Set FSM state as waiting for photo
        await state.set_state(RecipeStates.waiting_for_photo)
        
        with patch('app.handlers.recipe.supabase') as mock_supabase, \
             patch('app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('app.handlers.recipe.bot') as mock_bot:
            
            # Mock failed upload
            mock_upload.return_value = None
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data['user']]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await process_recipe_photo(mock_message, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower() or 'error' in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_generation_failure(self, mock_message, state, mock_user_data):
        """Test recipe photo handler when recipe generation fails"""
        # Set FSM state as waiting for photo
        await state.set_state(RecipeStates.waiting_for_photo)
        
        with patch('app.handlers.recipe.supabase') as mock_supabase, \
             patch('app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
             patch('app.handlers.recipe.bot') as mock_bot:
            
            # Mock successful upload
            mock_upload.return_value = 'https://r2.example.com/photo.jpg'
            
            # Mock failed recipe generation
            mock_generate.return_value = {
                'error': 'Generation failed',
                'success': False
            }
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data['user']]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await process_recipe_photo(mock_message, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower() or 'error' in call_args.lower()


class TestRecipeStatesEnum:
    """Test RecipeStates enum values"""
    
    def test_recipe_states_defined(self):
        """Test that RecipeStates enum has required states"""
        assert hasattr(RecipeStates, 'waiting_for_photo')
        assert RecipeStates.waiting_for_photo is not None
    
    def test_recipe_states_unique(self):
        """Test that RecipeStates values are unique"""
        states = [getattr(RecipeStates, attr) for attr in dir(RecipeStates) 
                 if not attr.startswith('_')]
        assert len(states) == len(set(states))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])