#!/usr/bin/env python3
"""
Unit tests for recipe generation functionality
Tests recipe FSM states, photo processing, and ML service integration
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

# Add project paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api.c0r.ai/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

# Mock common and i18n modules before importing handlers
import unittest.mock as mock
sys.modules['common'] = mock.MagicMock()
sys.modules['common.supabase_client'] = mock.MagicMock()
sys.modules['common.routes'] = mock.MagicMock()
sys.modules['i18n'] = mock.MagicMock()
sys.modules['i18n.i18n'] = mock.MagicMock()

from handlers.recipe import (
    RecipeStates,
    recipe_command,
    start_recipe_generation,
    process_recipe_photo,
    handle_recipe_callback
)


@pytest.fixture(autouse=True)
def patch_i18n_get_text():
    """Patch i18n.get_text to return real English text"""
    with patch('handlers.recipe.i18n.i18n.get_text') as mock_get_text:
        def fake_get_text(key, lang, **kwargs):
            # Return real English text from i18n/en.py
            en_texts = {
                'recipe_title': '🍽️ **Recipe Generation**',
                'recipe_setup_needed': '📝 **Profile Setup Recommended**\n\nFor personalized recipes that match your dietary preferences and goals, please set up your profile first.',
                'recipe_continue_without': '📸 You can still generate recipes without a profile!',
                'recipe_upload_photo': '📸 **Send me a photo of food or ingredients**\n\nI\'ll create a personalized recipe based on what I see in your photo.',
                'recipe_photo_tips': '💡 **Tips for better recipes:**\n• Include all ingredients you want to use\n• Clear, well-lit photos work best\n• Show individual ingredients or prepared dishes',
                'recipe_generating': '👨‍🍳 Generating your personalized recipe...',
                'recipe_error': '❌ **Recipe Generation Error**\n\nSorry, I couldn\'t generate a recipe from this photo. Please try with a different image showing food or ingredients.',
                'recipe_success_title': '🍽️ **Your Personalized Recipe**',
                'recipe_name': '📝 **{name}**',
                'recipe_description': '📖 {description}',
                'recipe_time_info': '⏱️ **Prep:** {prep_time} | **Cook:** {cook_time} | **Serves:** {servings}',
                'recipe_ingredients_title': '🛒 **Ingredients:**',
                'recipe_instructions_title': '👨‍🍳 **Instructions:**',
                'recipe_nutrition_title': '📊 **Nutrition (per serving):**',
                'recipe_nutrition_calories': '🔥 **Calories:** {calories}',
                'recipe_nutrition_protein': '🥩 **Protein:** {protein}g',
                'recipe_nutrition_carbs': '🍞 **Carbs:** {carbs}g',
                'recipe_nutrition_fat': '🥑 **Fat:** {fat}g',
                'recipe_credit_used': '💳 **1 credit used** for recipe generation',
                'btn_main_menu': '🏠 Main Menu',
                'error_general': 'An error occurred. Please try again later.',
                'photo_out_of_credits_title': '💳 **You\'re out of credits!**',
                'photo_out_of_credits_choose_plan': 'Choose a plan to continue analyzing your food:'
            }
            
            text = en_texts.get(key, key)
            if kwargs:
                return text.format(**kwargs)
            return text
        
        mock_get_text.side_effect = fake_get_text
        yield mock_get_text


class TestRecipeGeneration:
    """Test recipe generation functionality"""
    
    @pytest.fixture
    def mock_state(self):
        """Create mock FSM state"""
        state = Mock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.clear = AsyncMock()
        return state
    
    @pytest.fixture
    def mock_message(self):
        """Create mock message"""
        message = Mock(spec=types.Message)
        from_user = Mock()
        from_user.id = 123456789
        from_user.username = "testuser"
        message.from_user = from_user
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback"""
        callback = Mock(spec=types.CallbackQuery)
        from_user = Mock()
        from_user.id = 123456789
        from_user.username = "testuser"
        callback.from_user = from_user
        callback.data = "action_recipe"
        callback.answer = AsyncMock()
        callback.message = Mock()
        callback.message.answer = AsyncMock()
        return callback
    
    @pytest.fixture
    def mock_photo_message(self):
        """Create mock message with photo"""
        message = Mock(spec=types.Message)
        from_user = Mock()
        from_user.id = 123456789
        from_user.username = "testuser"
        message.from_user = from_user
        message.answer = AsyncMock()
        
        # Mock photo
        photo = Mock()
        photo.file_id = "test_file_id"
        photo.width = 1024
        photo.height = 768
        message.photo = [photo]  # Telegram sends array of photo sizes
        
        return message
    
    @pytest.mark.asyncio
    async def test_start_recipe_generation_with_profile(self, mock_message, mock_state):
        """Test starting recipe generation with existing profile"""
        with patch('handlers.recipe.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user, \
             patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile:
            
            # Mock user with complete profile
            user_data = {
                'user': {'id': 'user-uuid', 'credits': 5, 'language': 'en'},
                'profile': {
                    'age': 25,
                    'gender': 'male',
                    'dietary_preferences': ['vegetarian'],
                    'allergies': ['nuts']
                },
                'has_profile': True
            }
            
            await start_recipe_generation(mock_message, mock_state, user_data)
            
            # Verify state was set correctly
            mock_state.set_state.assert_called_once_with(RecipeStates.waiting_for_photo)
            
            # Verify message was sent with photo upload instructions
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "📸 **Send me a photo**" in call_args
            assert "Your Profile:" in call_args
    
    @pytest.mark.asyncio
    async def test_start_recipe_generation_without_profile(self, mock_message, mock_state):
        """Test starting recipe generation without profile"""
        # Mock user without profile
        user_data = {
            'user': {'id': 'user-uuid', 'credits': 5, 'language': 'en'},
            'profile': None,
            'has_profile': False
        }
        
        await start_recipe_generation(mock_message, mock_state, user_data)
        
        # Verify profile setup recommendation was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "📸 **Send me a photo**" in call_args
        assert "Set up your profile for personalized recipes" in call_args
    
    @pytest.mark.asyncio
    async def test_recipe_command_no_credits(self, mock_message, mock_state):
        """Test recipe command with no credits"""
        with patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.recipe.log_user_action', new=AsyncMock()) as mock_log:
            
            # Mock user with no credits
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid', 'credits': 0, 'language': 'en'},
                'profile': {'age': 25},
                'has_profile': True
            }
            
            await recipe_command(mock_message, mock_state)
            
            # Verify out of credits message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **No Credits Remaining**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_recipe_photo_success(self, mock_photo_message, mock_state):
        """Test successful recipe photo processing"""
        with patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.recipe.upload_telegram_photo', new=AsyncMock()) as mock_upload, \
             patch('handlers.recipe.generate_recipe_from_photo', new=AsyncMock()) as mock_generate, \
             patch('handlers.recipe.deduct_credit', new=AsyncMock()) as mock_deduct, \
             patch('handlers.recipe.log_user_action', new=AsyncMock()) as mock_log, \
             patch('handlers.recipe.send_recipe_response', new=AsyncMock()) as mock_send:
            
            # Mock user with profile and credits
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid', 'credits': 5, 'language': 'en'},
                'profile': {
                    'age': 25,
                    'gender': 'male',
                    'dietary_preferences': ['vegetarian'],
                    'allergies': ['nuts']
                },
                'has_profile': True
            }
            
            # Mock successful photo upload
            mock_upload.return_value = "https://r2.example.com/photo.jpg"
            
            # Mock successful recipe generation
            mock_generate.return_value = {
                'name': 'Vegetarian Pasta',
                'description': 'A delicious vegetarian pasta dish',
                'prep_time': '15 minutes',
                'cook_time': '20 minutes',
                'servings': 4,
                'ingredients': ['pasta', 'tomatoes', 'basil'],
                'instructions': ['Cook pasta', 'Add sauce', 'Serve'],
                'nutrition': {
                    'calories': 350,
                    'protein': 12,
                    'carbs': 65,
                    'fat': 8
                }
            }
            
            await process_recipe_photo(mock_photo_message, mock_state)
            
            # Verify photo was uploaded
            mock_upload.assert_called_once()
            
            # Verify recipe was generated
            mock_generate.assert_called_once()
            
            # Verify credit was deducted
            mock_deduct.assert_called_once()
            
            # Verify recipe response was sent
            mock_send.assert_called_once()
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_recipe_photo_ml_service_error(self, mock_photo_message, mock_state):
        """Test recipe photo processing with ML service error"""
        with patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.recipe.upload_telegram_photo', new=AsyncMock()) as mock_upload, \
             patch('handlers.recipe.generate_recipe_from_photo', new=AsyncMock()) as mock_generate, \
             patch('handlers.recipe.log_user_action', new=AsyncMock()) as mock_log:
            
            # Mock user with profile and credits
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid', 'credits': 5, 'language': 'en'},
                'profile': {'age': 25},
                'has_profile': True
            }
            
            # Mock successful photo upload
            mock_upload.return_value = "https://r2.example.com/photo.jpg"
            
            # Mock ML service error (returns None)
            mock_generate.return_value = None
            
            await process_recipe_photo(mock_photo_message, mock_state)
            
            # Verify error message was sent
            mock_photo_message.answer.assert_called()
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_recipe_photo_no_credits(self, mock_photo_message, mock_state):
        """Test recipe photo processing with no credits"""
        with patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile:
            
            # Mock user with no credits
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid', 'credits': 0, 'language': 'en'},
                'profile': {'age': 25},
                'has_profile': True
            }
            
            await process_recipe_photo(mock_photo_message, mock_state)
            
            # Verify out of credits message was sent
            mock_photo_message.answer.assert_called()
            call_args = mock_photo_message.answer.call_args[0][0]
            assert "❌ **No Credits Remaining**" in call_args
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_recipe_callback(self, mock_callback, mock_state):
        """Test recipe callback handler"""
        mock_callback.data = "action_recipe"
        
        with patch('handlers.recipe.recipe_command', new=AsyncMock()) as mock_recipe_cmd:
            
            await handle_recipe_callback(mock_callback, mock_state)
            
            # Verify recipe_command was called
            mock_recipe_cmd.assert_called_once_with(mock_callback.message, mock_state)
            
            # Verify callback was answered
            mock_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recipe_generation_with_dietary_preferences(self, mock_photo_message, mock_state):
        """Test recipe generation considers dietary preferences"""
        with patch('handlers.recipe.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.recipe.upload_telegram_photo', new=AsyncMock()) as mock_upload, \
             patch('handlers.recipe.generate_recipe_from_photo', new=AsyncMock()) as mock_generate, \
             patch('handlers.recipe.deduct_credit', new=AsyncMock()) as mock_deduct, \
             patch('handlers.recipe.log_user_action', new=AsyncMock()) as mock_log, \
             patch('handlers.recipe.send_recipe_response', new=AsyncMock()) as mock_send:
            
            # Mock user with specific dietary preferences and allergies
            user_data = {
                'user': {'id': 'user-uuid', 'credits': 5, 'language': 'en'},
                'profile': {
                    'age': 25,
                    'gender': 'female',
                    'goal': 'lose_weight',
                    'dietary_preferences': ['vegan', 'gluten_free'],
                    'allergies': ['nuts', 'dairy']
                },
                'has_profile': True
            }
            mock_get_profile.return_value = user_data
            
            # Mock successful photo upload
            mock_upload.return_value = "https://r2.example.com/photo.jpg"
            
            # Mock successful recipe generation
            mock_generate.return_value = {
                'name': 'Vegan Gluten-Free Bowl',
                'description': 'A healthy vegan and gluten-free bowl',
                'prep_time': '10 minutes',
                'cook_time': '15 minutes',
                'servings': 2,
                'ingredients': ['quinoa', 'vegetables', 'tahini'],
                'instructions': ['Cook quinoa', 'Prepare vegetables', 'Mix with tahini'],
                'nutrition': {
                    'calories': 280,
                    'protein': 10,
                    'carbs': 45,
                    'fat': 12
                }
            }
            
            await process_recipe_photo(mock_photo_message, mock_state)
            
            # Verify generate_recipe_from_photo was called with user_data containing dietary preferences
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            passed_user_data = call_args[0][1]  # Second argument is user_data
            
            # Verify user context includes dietary preferences and allergies
            assert 'profile' in passed_user_data
            profile = passed_user_data['profile']
            assert 'dietary_preferences' in profile
            assert 'vegan' in profile['dietary_preferences']
            assert 'gluten_free' in profile['dietary_preferences']
            assert 'allergies' in profile
            assert 'nuts' in profile['allergies']
            assert 'dairy' in profile['allergies']


class TestRecipeGenerationIntegration:
    """Integration tests for recipe generation workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_recipe_generation_flow(self):
        """Test complete recipe generation flow from start to finish"""
        # This test would simulate the complete flow:
        # 1. User clicks recipe button
        # 2. System checks profile and credits
        # 3. User uploads photo
        # 4. System processes photo and generates recipe
        # 5. User receives personalized recipe
        pass
    
    @pytest.mark.asyncio
    async def test_recipe_generation_with_russian_language(self):
        """Test recipe generation with Russian language"""
        # Test that all messages are properly localized to Russian
        pass
    
    @pytest.mark.asyncio
    async def test_recipe_generation_error_recovery(self):
        """Test that recipe generation can recover from errors"""
        # Test that users can retry after ML service failures
        pass