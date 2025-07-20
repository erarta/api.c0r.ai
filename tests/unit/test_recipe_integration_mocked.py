"""
Test recipe generation functionality with mocked OpenAI calls
Ensures the full workflow reaches the OpenAI integration
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize
import aiohttp
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.c0r.ai.app.handlers.recipe import (
    RecipeStates, 
    handle_recipe_callback, 
    process_recipe_photo,
    generate_recipe_from_photo,
    send_recipe_response,
    format_recipe_text
)


class TestRecipeIntegrationMocked:
    """Test recipe generation with mocked external services"""
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock complete user data with profile"""
        return {
            'user': {
                'id': 'd4047507-274c-493c-99b5-af801a5b7195',
                'telegram_id': 391490,
                'credits_remaining': 5,
                'language': 'ru'
            },
            'profile': {
                'age': 30,
                'gender': 'male',
                'height_cm': 180,
                'weight_kg': 75,
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight',
                'dietary_preferences': ['vegetarian', 'gluten_free'],
                'allergies': ['nuts', 'dairy'],
                'daily_calories_target': 2200
            },
            'has_profile': True
        }
    
    @pytest.fixture
    def mock_callback_query(self):
        """Create mock callback query"""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = MagicMock(spec=User)
        callback.from_user.id = 391490
        callback.from_user.language_code = 'ru'
        callback.from_user.username = 'testuser'
        callback.message = MagicMock(spec=Message)
        callback.message.chat = MagicMock(spec=Chat)
        callback.message.chat.id = 391490
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.data = "recipe"
        return callback
    
    @pytest.fixture
    def mock_message_with_photo(self):
        """Create mock message with photo"""
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 391490
        message.from_user.language_code = 'ru'
        message.from_user.username = 'testuser'
        message.chat = MagicMock(spec=Chat)
        message.chat.id = 391490
        message.answer = AsyncMock()
        
        # Mock photo
        photo_size = MagicMock(spec=PhotoSize)
        photo_size.file_id = 'test_file_id_12345'
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
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "name": "Vegetarian Gluten-Free Pasta",
            "description": "A delicious and healthy pasta dish perfect for vegetarians with gluten sensitivity",
            "prep_time": "15 minutes",
            "cook_time": "20 minutes",
            "servings": "2",
            "ingredients": [
                "200g gluten-free pasta",
                "2 tbsp olive oil",
                "1 bell pepper, sliced",
                "1 zucchini, diced",
                "2 cloves garlic, minced",
                "1 can diced tomatoes",
                "Fresh basil leaves",
                "Salt and pepper to taste"
            ],
            "instructions": [
                "Cook gluten-free pasta according to package instructions",
                "Heat olive oil in a large pan over medium heat",
                "Add bell pepper and zucchini, cook for 5 minutes",
                "Add garlic and cook for 1 minute",
                "Add diced tomatoes and simmer for 10 minutes",
                "Season with salt, pepper, and fresh basil",
                "Serve over cooked pasta"
            ],
            "nutrition": {
                "calories": 450,
                "protein": 12,
                "carbs": 65,
                "fat": 18
            }
        }
    
    @pytest.mark.asyncio
    async def test_recipe_callback_with_credits(self, mock_callback_query, mock_state, mock_user_data):
        """Test recipe callback when user has sufficient credits"""
        with patch('api.c0r.ai.app.handlers.recipe.get_user_with_profile') as mock_get_user:
            mock_get_user.return_value = mock_user_data
            
            # Call handler
            await handle_recipe_callback(mock_callback_query, mock_state)
            
            # Verify user data was fetched
            mock_get_user.assert_called_once_with(391490)
            
            # Verify state was set
            mock_state.set_state.assert_called_once_with(RecipeStates.waiting_for_photo)
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()
            
            # Verify instruction message was sent
            mock_callback_query.message.edit_text.assert_called_once()
            call_args = mock_callback_query.message.edit_text.call_args[1]
            assert 'Recipe Generation' in call_args['text'] or 'рецепт' in call_args['text'].lower()
    
    @pytest.mark.asyncio
    async def test_full_recipe_generation_workflow_with_openai_mock(
        self, 
        mock_message_with_photo, 
        mock_state, 
        mock_user_data, 
        mock_openai_response
    ):
        """Test complete recipe generation workflow with mocked OpenAI call"""
        # Set FSM state to waiting for photo
        mock_state.get_state.return_value = RecipeStates.waiting_for_photo
        
        with patch('api.c0r.ai.app.handlers.recipe.get_user_with_profile') as mock_get_user, \
             patch('api.c0r.ai.app.handlers.recipe.upload_telegram_photo') as mock_upload, \
             patch('api.c0r.ai.app.handlers.recipe.generate_recipe_from_photo') as mock_generate, \
             patch('api.c0r.ai.app.handlers.recipe.log_user_action') as mock_log, \
             patch('api.c0r.ai.app.handlers.recipe.deduct_credit') as mock_deduct, \
             patch('aiogram.Bot.get_current') as mock_bot_current:
            
            # Setup mocks
            mock_get_user.return_value = mock_user_data
            mock_upload.return_value = 'https://r2.example.com/user123/2025/07/19/recipe_generation/photo.jpg'
            mock_generate.return_value = mock_openai_response
            
            # Mock bot instance
            mock_bot = MagicMock()
            mock_bot_current.return_value = mock_bot
            
            # Call the photo processing handler
            await process_recipe_photo(mock_message_with_photo, mock_state)
            
            # Verify user data was fetched
            mock_get_user.assert_called_once_with(391490)
            
            # Verify photo was uploaded to R2
            mock_upload.assert_called_once()
            upload_args = mock_upload.call_args[0]
            assert upload_args[1] == mock_message_with_photo.photo[-1]  # Photo object
            assert upload_args[2] == mock_user_data['user']['id']  # User ID
            
            # Verify recipe generation was called with correct parameters
            mock_generate.assert_called_once()
            generate_args = mock_generate.call_args[0]
            assert generate_args[0] == 'https://r2.example.com/user123/2025/07/19/recipe_generation/photo.jpg'
            assert generate_args[1] == mock_user_data
            
            # Verify credit was deducted
            mock_deduct.assert_called_once_with(391490, 1)
            
            # Verify action was logged
            mock_log.assert_called_once()
            log_args = mock_log.call_args[1]
            assert log_args['user_id'] == mock_user_data['user']['id']
            assert log_args['action_type'] == 'recipe_generation'
            assert 'recipe_data' in log_args['metadata']
            
            # Verify FSM state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify response was sent to user
            mock_message_with_photo.answer.assert_called()
    
    @pytest.mark.asyncio
    async def test_openai_integration_with_user_context(self, mock_user_data, mock_openai_response):
        """Test that OpenAI integration receives correct user context"""
        photo_url = 'https://r2.example.com/test_photo.jpg'
        
        # Mock aiohttp session and response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_openai_response)
        
        mock_session = MagicMock()
        mock_session.post = AsyncMock()
        mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session), \
             patch.dict(os.environ, {'ML_SERVICE_URL': 'http://test-ml-service:8001'}):
            
            # Call the recipe generation function
            result = await generate_recipe_from_photo(photo_url, mock_user_data)
            
            # Verify the result
            assert result == mock_openai_response
            
            # Verify the ML service was called
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            
            # Check URL
            assert call_args[0][0] == 'http://test-ml-service:8001/api/v1/generate-recipe'
            
            # Check form data was prepared correctly
            form_data = call_args[1]['data']
            assert form_data is not None
            
            # Verify timeout was set
            assert 'timeout' in call_args[1]
            assert call_args[1]['timeout'].total == 60
    
    @pytest.mark.asyncio
    async def test_openai_service_failure_handling(self, mock_user_data):
        """Test handling of OpenAI service failures"""
        photo_url = 'https://r2.example.com/test_photo.jpg'
        
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status = 500
        
        mock_session = MagicMock()
        mock_session.post = AsyncMock()
        mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            # Call the recipe generation function
            result = await generate_recipe_from_photo(photo_url, mock_user_data)
            
            # Verify None is returned on failure
            assert result is None
    
    @pytest.mark.asyncio
    async def test_openai_network_error_handling(self, mock_user_data):
        """Test handling of network errors when calling OpenAI"""
        photo_url = 'https://r2.example.com/test_photo.jpg'
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Mock network error
            mock_session = MagicMock()
            mock_session.post.side_effect = aiohttp.ClientError("Network error")
            mock_session_class.return_value = mock_session
            
            # Call the recipe generation function
            result = await generate_recipe_from_photo(photo_url, mock_user_data)
            
            # Verify None is returned on network error
            assert result is None
    
    def test_recipe_text_formatting(self, mock_openai_response):
        """Test recipe text formatting function"""
        formatted_text = format_recipe_text(mock_openai_response, 'en')
        
        # Verify all components are included
        assert "Vegetarian Gluten-Free Pasta" in formatted_text
        assert "15 minutes" in formatted_text  # prep time
        assert "20 minutes" in formatted_text  # cook time
        assert "2" in formatted_text  # servings
        assert "200g gluten-free pasta" in formatted_text  # ingredient
        assert "Cook gluten-free pasta" in formatted_text  # instruction
        assert "450" in formatted_text  # calories
        assert "12" in formatted_text  # protein
    
    def test_recipe_text_formatting_minimal_data(self):
        """Test recipe text formatting with minimal data"""
        minimal_recipe = {
            "name": "Simple Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2"]
        }
        
        formatted_text = format_recipe_text(minimal_recipe, 'en')
        
        # Verify basic components are included
        assert "Simple Recipe" in formatted_text
        assert "ingredient 1" in formatted_text
        assert "step 1" in formatted_text
    
    @pytest.mark.asyncio
    async def test_user_context_preparation_with_profile(self, mock_user_data):
        """Test that user context is properly prepared for OpenAI"""
        photo_url = 'https://r2.example.com/test_photo.jpg'
        
        # Mock the form data to capture what's sent
        captured_form_data = {}
        
        def capture_form_data(*args, **kwargs):
            mock_form = MagicMock()
            def add_field(key, value):
                captured_form_data[key] = value
            mock_form.add_field = add_field
            return mock_form
        
        with patch('aiohttp.FormData', side_effect=capture_form_data), \
             patch('aiohttp.ClientSession') as mock_session_class:
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'test': 'response'})
            
            mock_session = MagicMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            # Call the function
            await generate_recipe_from_photo(photo_url, mock_user_data)
            
            # Verify user context was properly prepared
            assert 'user_context' in captured_form_data
            user_context = json.loads(captured_form_data['user_context'])
            
            # Check profile data is included
            assert user_context['has_profile'] == True
            assert user_context['language'] == 'ru'
            assert user_context['age'] == 30
            assert user_context['gender'] == 'male'
            assert user_context['dietary_preferences'] == ['vegetarian', 'gluten_free']
            assert user_context['allergies'] == ['nuts', 'dairy']
            assert user_context['goal'] == 'maintain_weight'
    
    @pytest.mark.asyncio
    async def test_user_context_preparation_without_profile(self):
        """Test user context preparation for users without profile"""
        user_data_no_profile = {
            'user': {
                'id': 'test-user-id',
                'telegram_id': 12345,
                'credits_remaining': 3,
                'language': 'en'
            },
            'profile': None,
            'has_profile': False
        }
        
        photo_url = 'https://r2.example.com/test_photo.jpg'
        captured_form_data = {}
        
        def capture_form_data(*args, **kwargs):
            mock_form = MagicMock()
            def add_field(key, value):
                captured_form_data[key] = value
            mock_form.add_field = add_field
            return mock_form
        
        with patch('aiohttp.FormData', side_effect=capture_form_data), \
             patch('aiohttp.ClientSession') as mock_session_class:
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'test': 'response'})
            
            mock_session = MagicMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            # Call the function
            await generate_recipe_from_photo(photo_url, user_data_no_profile)
            
            # Verify user context was properly prepared
            assert 'user_context' in captured_form_data
            user_context = json.loads(captured_form_data['user_context'])
            
            # Check basic data is included
            assert user_context['has_profile'] == False
            assert user_context['language'] == 'en'
            
            # Check profile-specific data is not included
            assert 'age' not in user_context
            assert 'dietary_preferences' not in user_context
    
    @pytest.mark.asyncio
    async def test_recipe_generation_reaches_openai_endpoint(self, mock_user_data, mock_openai_response):
        """Test that recipe generation actually reaches the OpenAI endpoint"""
        photo_url = 'https://r2.example.com/test_photo.jpg'
        
        # Track if the endpoint was called
        endpoint_called = False
        
        async def mock_post(*args, **kwargs):
            nonlocal endpoint_called
            endpoint_called = True
            
            # Verify correct endpoint
            assert args[0] == 'http://localhost:8001/api/v1/generate-recipe'
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_openai_response)
            return mock_response
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session.post = mock_post
            mock_session_class.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Call the function
            result = await generate_recipe_from_photo(photo_url, mock_user_data)
            
            # Verify endpoint was called
            assert endpoint_called == True
            
            # Verify result is correct
            assert result == mock_openai_response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])