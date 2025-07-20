#!/usr/bin/env python3
"""
Unit tests for extended profile functionality
Tests dietary preferences and allergies steps (7/8 and 8/8)
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
sys.modules['common.nutrition_calculations'] = mock.MagicMock()
sys.modules['i18n'] = mock.MagicMock()
sys.modules['i18n.i18n'] = mock.MagicMock()

from handlers.profile import (
    ProfileStates,
    process_goal,
    process_dietary_preferences,
    process_allergies,
    complete_profile_setup
)


@pytest.fixture(autouse=True)
def patch_i18n_get_text():
    """Patch i18n.get_text to return real English text"""
    with patch('handlers.profile.i18n.get_text') as mock_get_text:
        def fake_get_text(key, lang, **kwargs):
            # Return real English text from i18n/en.py
            en_texts = {
                'profile_setup_goal': '🎯 **Step 6/8: Your Goal**\n\nPlease select your nutrition goal:',
                'profile_setup_dietary': '🥗 **Step 7/8: Dietary Preferences**\n\nSelect any dietary preferences that apply to you (optional):',
                'profile_setup_allergies': '⚠️ **Step 8/8: Food Allergies**\n\nSelect any food allergies you have (optional):',
                'profile_setup_dietary_success': 'Dietary preferences: {preferences}',
                'profile_setup_allergies_success': 'Allergies: {allergies}',
                'profile_setup_complete': '✅ **Profile Setup Complete!**\n\nYour daily calorie target: **{calories:,} calories**\n\nYou can now get personalized nutrition recommendations!',
                'profile_updated_successfully': '🎉 **Profile {action} Successfully!**',
                'profile_created': 'Created',
                'profile_summary_title': '📊 **Your Profile Summary:**',
                'profile_summary_age': '📅 Age: {age} years',
                'profile_summary_gender': '👤 Gender: {gender}',
                'profile_summary_height': '📏 Height: {height} cm',
                'profile_summary_weight': '⚖️ Weight: {weight} kg',
                'profile_summary_activity': '🏃 Activity: {activity}',
                'profile_summary_goal': '🎯 Goal: {goal}',
                'profile_daily_calorie_target': '🔥 **Daily Calorie Target: {calories} calories**',
                'profile_personalized_progress': '✨ Now you\'ll see personalized progress when analyzing food photos!',
                'btn_view_daily_plan': '📊 View Daily Plan',
                'btn_analyze_food': '📸 Analyze Food',
                'profile_dietary_none': '🍽️ No specific preferences',
                'profile_dietary_vegetarian': '🥬 Vegetarian',
                'profile_dietary_vegan': '🌱 Vegan',
                'profile_dietary_keto': '🥩 Keto',
                'profile_dietary_done': '✅ Done',
                'profile_allergy_none': '✅ No allergies',
                'profile_allergy_nuts': '🥜 Nuts',
                'profile_allergy_dairy': '🥛 Dairy',
                'profile_allergy_gluten': '🌾 Gluten',
                'profile_allergy_done': '✅ Done',
                'goal_lose_weight': '📉 Lose Weight',
                'goal_maintain_weight': '⚖️ Maintain Weight',
                'goal_gain_weight': '📈 Gain Weight',
                'gender_male': 'Male',
                'gender_female': 'Female',
                'activity_moderately_active': 'Moderately Active',
                'error_general': 'An error occurred. Please try again later.'
            }
            
            text = en_texts.get(key, key)
            if kwargs:
                return text.format(**kwargs)
            return text
        
        mock_get_text.side_effect = fake_get_text
        yield mock_get_text


class TestExtendedProfile:
    """Test extended profile functionality with dietary preferences and allergies"""
    
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
    def mock_callback(self):
        """Create mock callback"""
        callback = Mock(spec=types.CallbackQuery)
        from_user = Mock()
        from_user.id = 123456789
        from_user.username = "testuser"
        callback.from_user = from_user
        callback.data = "goal_maintain_weight"
        callback.answer = AsyncMock()
        callback.message = Mock()
        callback.message.answer = AsyncMock()
        return callback
    
    @pytest.mark.asyncio
    async def test_process_goal_moves_to_dietary_preferences(self, mock_callback, mock_state):
        """Test that process_goal now moves to dietary preferences instead of completing"""
        mock_callback.data = "goal_maintain_weight"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_goal(mock_callback, mock_state)
            
            # Verify goal was stored
            mock_state.update_data.assert_called_once_with(goal="maintain_weight")
            
            # Verify state moved to dietary preferences (not completed)
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_dietary_preferences)
            
            # Verify dietary preferences prompt was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "🥗 **Step 7/8: Dietary Preferences**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_dietary_preferences_single_selection(self, mock_callback, mock_state):
        """Test processing single dietary preference selection"""
        mock_callback.data = "dietary_vegetarian"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_dietary_preferences(mock_callback, mock_state)
            
            # Verify dietary preference was stored
            mock_state.update_data.assert_called_once_with(dietary_preferences=["vegetarian"])
            
            # Verify state moved to allergies
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_allergies)
            
            # Verify success message and allergies prompt were sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Dietary preferences: 🥬 Vegetarian" in call_args
            assert "⚠️ **Step 8/8: Food Allergies**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_dietary_preferences_multiple_selections(self, mock_callback, mock_state):
        """Test processing multiple dietary preference selections"""
        mock_callback.data = "dietary_vegan"
        
        # Mock existing dietary preferences in state
        mock_state.get_data.return_value = {
            'dietary_preferences': ['vegetarian']
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_dietary_preferences(mock_callback, mock_state)
            
            # Verify both dietary preferences were stored
            mock_state.update_data.assert_called_once_with(dietary_preferences=["vegetarian", "vegan"])
            
            # Verify success message shows both preferences
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "🥬 Vegetarian, 🌱 Vegan" in call_args
    
    @pytest.mark.asyncio
    async def test_process_dietary_preferences_none_selected(self, mock_callback, mock_state):
        """Test processing 'no preferences' selection"""
        mock_callback.data = "dietary_none"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_dietary_preferences(mock_callback, mock_state)
            
            # Verify empty list was stored
            mock_state.update_data.assert_called_once_with(dietary_preferences=[])
            
            # Verify state moved to allergies
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_allergies)
            
            # Verify success message
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Dietary preferences: 🍽️ No specific preferences" in call_args
    
    @pytest.mark.asyncio
    async def test_process_dietary_preferences_done_button(self, mock_callback, mock_state):
        """Test processing 'done' button for dietary preferences"""
        mock_callback.data = "dietary_done"
        
        # Mock existing dietary preferences in state
        mock_state.get_data.return_value = {
            'dietary_preferences': ['vegetarian', 'keto']
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_dietary_preferences(mock_callback, mock_state)
            
            # Verify state moved to allergies without updating data
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_allergies)
            mock_state.update_data.assert_not_called()
            
            # Verify success message shows existing preferences
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "🥬 Vegetarian, 🥩 Keto" in call_args
    
    @pytest.mark.asyncio
    async def test_process_allergies_single_selection(self, mock_callback, mock_state):
        """Test processing single allergy selection"""
        mock_callback.data = "allergy_nuts"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_allergies(mock_callback, mock_state)
            
            # Verify allergy was stored
            mock_state.update_data.assert_called_once_with(allergies=["nuts"])
            
            # Verify success message was sent (but state not changed yet)
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Allergies: 🥜 Nuts" in call_args
    
    @pytest.mark.asyncio
    async def test_process_allergies_multiple_selections(self, mock_callback, mock_state):
        """Test processing multiple allergy selections"""
        mock_callback.data = "allergy_dairy"
        
        # Mock existing allergies in state
        mock_state.get_data.return_value = {
            'allergies': ['nuts']
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_allergies(mock_callback, mock_state)
            
            # Verify both allergies were stored
            mock_state.update_data.assert_called_once_with(allergies=["nuts", "dairy"])
            
            # Verify success message shows both allergies
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "🥜 Nuts, 🥛 Dairy" in call_args
    
    @pytest.mark.asyncio
    async def test_process_allergies_none_selected(self, mock_callback, mock_state):
        """Test processing 'no allergies' selection"""
        mock_callback.data = "allergy_none"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_allergies(mock_callback, mock_state)
            
            # Verify empty list was stored
            mock_state.update_data.assert_called_once_with(allergies=[])
            
            # Verify success message
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Allergies: ✅ No allergies" in call_args
    
    @pytest.mark.asyncio
    async def test_process_allergies_done_completes_profile(self, mock_callback, mock_state):
        """Test that 'done' button for allergies completes the profile setup"""
        mock_callback.data = "allergy_done"
        
        # Mock complete profile data
        mock_state.get_data.return_value = {
            'age': 25,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 70,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight',
            'dietary_preferences': ['vegetarian'],
            'allergies': ['nuts']
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user, \
             patch('handlers.profile.complete_profile_setup', new=AsyncMock()) as mock_complete:
            
            await process_allergies(mock_callback, mock_state)
            
            # Verify complete_profile_setup was called
            mock_complete.assert_called_once_with(mock_callback, mock_state)
    
    @pytest.mark.asyncio
    async def test_complete_profile_setup_with_dietary_data(self, mock_callback, mock_state):
        """Test complete profile setup includes dietary preferences and allergies"""
        # Mock complete profile data including new fields
        mock_state.get_data.return_value = {
            'age': 25,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 70,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight',
            'dietary_preferences': ['vegetarian', 'gluten_free'],
            'allergies': ['nuts', 'dairy']
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user, \
             patch('handlers.profile.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.profile.create_or_update_profile', new=AsyncMock()) as mock_create_profile, \
             patch('handlers.profile.log_user_action', new=AsyncMock()) as mock_log_action:
            
            mock_get_user.return_value = {'language': 'en'}
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid'},
                'profile': None
            }
            mock_create_profile.return_value = ({'daily_calories_target': 2200}, True)
            
            await complete_profile_setup(mock_callback, mock_state)
            
            # Verify profile was created with dietary data
            mock_create_profile.assert_called_once()
            call_args = mock_create_profile.call_args[0]  # positional args
            profile_data = call_args[1]  # second argument is profile data
            
            # Verify dietary preferences and allergies are included
            assert 'dietary_preferences' in profile_data
            assert profile_data['dietary_preferences'] == ['vegetarian', 'gluten_free']
            assert 'allergies' in profile_data
            assert profile_data['allergies'] == ['nuts', 'dairy']
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify success message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "✅ **Profile Setup Complete!**" in call_args
    
    @pytest.mark.asyncio
    async def test_complete_profile_setup_error_handling(self, mock_callback, mock_state):
        """Test error handling in complete profile setup"""
        # Mock complete profile data
        mock_state.get_data.return_value = {
            'age': 25,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 70,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight',
            'dietary_preferences': ['vegetarian'],
            'allergies': []
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user, \
             patch('handlers.profile.get_user_with_profile', new=AsyncMock()) as mock_get_profile, \
             patch('handlers.profile.create_or_update_profile', side_effect=Exception("Database error")):
            
            mock_get_user.return_value = {'language': 'en'}
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid'},
                'profile': None
            }
            
            await complete_profile_setup(mock_callback, mock_state)
            
            # Verify error message was sent
            mock_callback.answer.assert_called_once()
            call_args = mock_callback.answer.call_args[0][0]
            assert "An error occurred" in call_args
            
            # Verify state was cleared on error
            mock_state.clear.assert_called_once()


class TestExtendedProfileIntegration:
    """Integration tests for extended profile functionality"""
    
    @pytest.mark.asyncio
    async def test_complete_8_step_profile_flow(self):
        """Test complete 8-step profile flow including dietary preferences and allergies"""
        # This test would simulate the complete flow:
        # 1. Age -> 2. Gender -> 3. Height -> 4. Weight -> 5. Activity -> 6. Goal
        # 7. Dietary Preferences -> 8. Allergies -> Complete
        pass
    
    @pytest.mark.asyncio
    async def test_profile_with_no_dietary_restrictions(self):
        """Test profile setup with no dietary preferences or allergies"""
        # Test that users can skip both dietary preferences and allergies
        pass
    
    @pytest.mark.asyncio
    async def test_profile_with_complex_dietary_needs(self):
        """Test profile setup with multiple dietary preferences and allergies"""
        # Test users with complex dietary needs (e.g., vegan + gluten-free + multiple allergies)
        pass