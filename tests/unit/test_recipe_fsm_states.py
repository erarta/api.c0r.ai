"""
Test FSM states for recipe generation functionality
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.c0r.ai.app.handlers.recipe import RecipeStates, handle_recipe_callback, handle_recipe_photo
from api.c0r.ai.app.handlers.keyboards import get_main_menu_keyboard


class TestRecipeFSMStates:
    """Test recipe generation FSM states and transitions"""
    
    @pytest.fixture
    def mock_callback_query(self):
        """Create mock callback query"""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = MagicMock(spec=User)
        callback.from_user.id = 12345
        callback.from_user.language_code = 'ru'
        callback.message = MagicMock(spec=Message)
        callback.message.chat = MagicMock(spec=Chat)
        callback.message.chat.id = 12345
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        return callback
    
    @pytest.fixture
    def mock_message(self):
        """Create mock message with photo"""
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.from_user.language_code = 'ru'
        message.chat = MagicMock(spec=Chat)
        message.chat.id = 12345
        message.answer = AsyncMock()
        
        # Mock photo
        photo_size = MagicMock(spec=PhotoSize)
        photo_size.file_id = 'test_file_id'
        photo_size.width = 1024
        photo_size.height = 768
        message.photo = [photo_size]
        
        return message
    
    @pytest.fixture
    def mock_state(self):
        """Create mock FSM state"""
        state = AsyncMock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.get_state = AsyncMock()
        state.clear = AsyncMock()
        return state
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock user data from database"""
        return {
            'id': 12345,
            'credits_remaining': 5,
            'dietary_preferences': ['vegetarian', 'gluten_free'],
            'allergies': ['nuts', 'dairy'],
            'language': 'ru'
        }
    
    @pytest.mark.asyncio
    async def test_recipe_callback_sets_waiting_photo_state(self, mock_callback_query, mock_state):
        """Test that recipe callback sets FSM state to waiting for photo"""
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase:
            # Mock user with credits
            mock_supabase.table().select().eq().execute.return_value.data = [
                {'id': 12345, 'credits_remaining': 5}
            ]
            
            # Call handler
            await handle_recipe_callback(mock_callback_query, mock_state)
            
            # Verify state was set to waiting for photo
            mock_state.set_state.assert_called_once_with(RecipeStates.waiting_for_photo)
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify message was edited
            mock_callback_query.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_callback_insufficient_credits(self, mock_callback_query, mock_state):
        """Test recipe callback when user has insufficient credits"""
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase:
            # Mock user with no credits
            mock_supabase.table().select().eq().execute.return_value.data = [
                {'id': 12345, 'credits_remaining': 0}
            ]
            
            # Call handler
            await handle_recipe_callback(mock_callback_query, mock_state)
            
            # Verify state was NOT set
            mock_state.set_state.assert_not_called()
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify insufficient credits message was sent
            mock_callback_query.message.edit_text.assert_called_once()
            call_args = mock_callback_query.message.edit_text.call_args[1]
            assert 'недостаточно кредитов' in call_args['text'].lower() or 'insufficient credits' in call_args['text'].lower()
    
    @pytest.mark.asyncio
    async def test_recipe_callback_user_not_found(self, mock_callback_query, mock_state):
        """Test recipe callback when user is not found in database"""
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase:
            # Mock empty user data
            mock_supabase.table().select().eq().execute.return_value.data = []
            
            # Call handler
            await handle_recipe_callback(mock_callback_query, mock_state)
            
            # Verify state was NOT set
            mock_state.set_state.assert_not_called()
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify error message was sent
            mock_callback_query.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_valid_state(self, mock_message, mock_state, mock_user_data):
        """Test recipe photo handler when in correct FSM state"""
        # Mock FSM state as waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase, \
             patch('api.c0r.ai.app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('api.c0r.ai.app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
             patch('api.c0r.ai.app.handlers.recipe.bot') as mock_bot:
            
            # Mock successful upload
            mock_upload.return_value = 'https://r2.example.com/photo.jpg'
            
            # Mock successful recipe generation
            mock_generate.return_value = {
                'recipe': 'Test recipe content',
                'success': True
            }
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await handle_recipe_photo(mock_message, mock_state)
            
            # Verify state was cleared after processing
            mock_state.clear.assert_called_once()
            
            # Verify photo was uploaded
            mock_upload.assert_called_once()
            
            # Verify recipe was generated
            mock_generate.assert_called_once()
            
            # Verify response was sent
            mock_message.answer.assert_called()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_wrong_state(self, mock_message, mock_state):
        """Test recipe photo handler when not in correct FSM state"""
        # Mock FSM state as None (not waiting for photo)
        mock_state.get_state.return_value = None
        
        # Call handler
        await handle_recipe_photo(mock_message, mock_state)
        
        # Verify no processing occurred
        mock_state.clear.assert_not_called()
        mock_message.answer.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_no_photo(self, mock_message, mock_state):
        """Test recipe photo handler when message has no photo"""
        # Mock FSM state as waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        # Remove photo from message
        mock_message.photo = None
        
        # Call handler
        await handle_recipe_photo(mock_message, mock_state)
        
        # Verify no processing occurred
        mock_state.clear.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_upload_failure(self, mock_message, mock_state, mock_user_data):
        """Test recipe photo handler when photo upload fails"""
        # Mock FSM state as waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase, \
             patch('api.c0r.ai.app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('api.c0r.ai.app.handlers.recipe.bot') as mock_bot:
            
            # Mock failed upload
            mock_upload.return_value = None
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await handle_recipe_photo(mock_message, mock_state)
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower() or 'error' in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_generation_failure(self, mock_message, mock_state, mock_user_data):
        """Test recipe photo handler when recipe generation fails"""
        # Mock FSM state as waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase, \
             patch('api.c0r.ai.app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('api.c0r.ai.app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
             patch('api.c0r.ai.app.handlers.recipe.bot') as mock_bot:
            
            # Mock successful upload
            mock_upload.return_value = 'https://r2.example.com/photo.jpg'
            
            # Mock failed recipe generation
            mock_generate.return_value = {
                'error': 'Generation failed',
                'success': False
            }
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await handle_recipe_photo(mock_message, mock_state)
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify error message was sent
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert 'ошибка' in call_args.lower() or 'error' in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_recipe_photo_handler_credits_deducted(self, mock_message, mock_state, mock_user_data):
        """Test that credits are properly deducted after successful recipe generation"""
        # Mock FSM state as waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase, \
             patch('api.c0r.ai.app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
             patch('api.c0r.ai.app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
             patch('api.c0r.ai.app.handlers.recipe.bot') as mock_bot:
            
            # Mock successful upload and generation
            mock_upload.return_value = 'https://r2.example.com/photo.jpg'
            mock_generate.return_value = {
                'recipe': 'Test recipe content',
                'success': True
            }
            
            # Mock user data
            mock_supabase.table().select().eq().execute.return_value.data = [mock_user_data]
            
            # Mock file download
            mock_bot.download_file = AsyncMock()
            mock_bot.get_file = AsyncMock()
            mock_bot.get_file.return_value.file_path = 'test/path.jpg'
            
            # Call handler
            await handle_recipe_photo(mock_message, mock_state)
            
            # Verify credits were deducted
            update_call = mock_supabase.table().update().eq().execute
            update_call.assert_called_once()
            
            # Check that credits_remaining was decremented
            update_args = mock_supabase.table().update.call_args[0][0]
            assert update_args['credits_remaining'] == mock_user_data['credits_remaining'] - 1
    
    @pytest.mark.asyncio
    async def test_fsm_state_transitions(self, mock_callback_query, mock_state):
        """Test complete FSM state transition flow"""
        with patch('api.c0r.ai.app.handlers.recipe.supabase') as mock_supabase:
            # Mock user with credits
            mock_supabase.table().select().eq().execute.return_value.data = [
                {'id': 12345, 'credits_remaining': 5}
            ]
            
            # Test initial state transition
            await handle_recipe_callback(mock_callback_query, mock_state)
            
            # Verify state was set to waiting for photo
            mock_state.set_state.assert_called_once_with(RecipeStates.waiting_for_photo)
            
            # Reset mock
            mock_state.reset_mock()
            
            # Test state clearing after photo processing
            mock_state.get_state.return_value = RecipeStates.waiting_for_photo
            
            with patch('api.c0r.ai.app.handlers.recipe.upload_photo_to_r2') as mock_upload, \
                 patch('api.c0r.ai.app.handlers.recipe.generate_recipe_with_openai') as mock_generate, \
                 patch('api.c0r.ai.app.handlers.recipe.bot') as mock_bot:
                
                # Mock successful processing
                mock_upload.return_value = 'https://r2.example.com/photo.jpg'
                mock_generate.return_value = {'recipe': 'Test recipe', 'success': True}
                mock_bot.download_file = AsyncMock()
                mock_bot.get_file = AsyncMock()
                mock_bot.get_file.return_value.file_path = 'test/path.jpg'
                
                # Create mock message with photo
                mock_message = MagicMock(spec=Message)
                mock_message.from_user = MagicMock(spec=User)
                mock_message.from_user.id = 12345
                mock_message.from_user.language_code = 'ru'
                mock_message.chat = MagicMock(spec=Chat)
                mock_message.chat.id = 12345
                mock_message.answer = AsyncMock()
                
                photo_size = MagicMock(spec=PhotoSize)
                photo_size.file_id = 'test_file_id'
                mock_message.photo = [photo_size]
                
                # Process photo
                await handle_recipe_photo(mock_message, mock_state)
                
                # Verify state was cleared
                mock_state.clear.assert_called_once()


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