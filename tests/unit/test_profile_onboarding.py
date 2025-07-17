#!/usr/bin/env python3
"""
Unit tests for profile onboarding process
Tests all steps of profile setup from age to goal selection
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
    process_age,
    process_gender,
    process_height,
    process_weight,
    process_activity,
    process_goal,
    start_profile_setup
)


@pytest.fixture(autouse=True)
def patch_i18n_get_text():
    with patch('i18n.i18n.i18n.get_text') as mock_get_text:
        def fake_get_text(key, lang, **kwargs):
            params = ', '.join(f'{k}={v}' for k, v in kwargs.items())
            return f'{key} {params}'.strip()
        mock_get_text.side_effect = fake_get_text
        yield


class TestProfileOnboarding:
    """Test profile onboarding process"""
    
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
        message.text = "25"
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
        callback.data = "gender_male"
        callback.answer = AsyncMock()
        callback.message = Mock()
        callback.message.answer = AsyncMock()
        return callback
    
    @pytest.mark.asyncio
    async def test_start_profile_setup(self, mock_message, mock_state):
        """Test starting profile setup"""
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await start_profile_setup(mock_message, mock_state, 123456789)
            
            # Verify state was set correctly
            mock_state.clear.assert_called_once()
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_age)
            
            # Verify message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "👶 **Step 1/6: Your Age**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_age_valid(self, mock_message, mock_state):
        """Test processing valid age input"""
        mock_message.text = "25"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_age(mock_message, mock_state)
            
            # Verify age was stored
            mock_state.update_data.assert_called_once_with(age=25)
            
            # Verify state moved to gender
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_gender)
            
            # Verify success message and gender prompt were sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Age: 25 years" in call_args
            assert "👥 **Step 2/6: Your Gender**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_age_invalid_too_young(self, mock_message, mock_state):
        """Test processing age that's too young"""
        mock_message.text = "5"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_age(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid age**" in call_args
            
            # Verify state wasn't changed
            mock_state.set_state.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_age_invalid_too_old(self, mock_message, mock_state):
        """Test processing age that's too old"""
        mock_message.text = "150"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_age(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid age**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_age_invalid_format(self, mock_message, mock_state):
        """Test processing age with invalid format"""
        mock_message.text = "abc"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_age(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid age format**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_gender_male(self, mock_callback, mock_state):
        """Test processing male gender selection"""
        mock_callback.data = "gender_male"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_gender(mock_callback, mock_state)
            
            # Verify gender was stored
            mock_state.update_data.assert_called_once_with(gender="male")
            
            # Verify state moved to height
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_height)
            
            # Verify success message and height prompt were sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Gender: 👨 Male" in call_args
            assert "Step 3/6: Your Height" in call_args
    
    @pytest.mark.asyncio
    async def test_process_gender_female(self, mock_callback, mock_state):
        """Test processing female gender selection"""
        mock_callback.data = "gender_female"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_gender(mock_callback, mock_state)
            
            # Verify gender was stored
            mock_state.update_data.assert_called_once_with(gender="female")
            
            # Verify success message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Gender: 👩 Female" in call_args
            assert "Step 3/6: Your Height" in call_args
    
    @pytest.mark.asyncio
    async def test_process_height_valid(self, mock_message, mock_state):
        """Test processing valid height input"""
        mock_message.text = "175"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_height(mock_message, mock_state)
            
            # Verify height was stored
            mock_state.update_data.assert_called_once_with(height_cm=175)
            
            # Verify state moved to weight
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_weight)
            
            # Verify success message and weight prompt were sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Height: 175 cm" in call_args
            assert "⚖️ **Step 4/6: Your Weight**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_height_invalid_too_short(self, mock_message, mock_state):
        """Test processing height that's too short"""
        mock_message.text = "50"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_height(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid height**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_height_invalid_too_tall(self, mock_message, mock_state):
        """Test processing height that's too tall"""
        mock_message.text = "300"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_height(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid height**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_weight_valid(self, mock_message, mock_state):
        """Test processing valid weight input"""
        mock_message.text = "70.5"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_weight(mock_message, mock_state)
            
            # Verify weight was stored
            mock_state.update_data.assert_called_once_with(weight_kg=70.5)
            
            # Verify state moved to activity
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_activity)
            
            # Verify success message and activity prompt were sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Weight: 70.5 kg" in call_args
    
    @pytest.mark.asyncio
    async def test_process_weight_with_comma(self, mock_message, mock_state):
        """Test processing weight with comma decimal separator"""
        mock_message.text = "70,5"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_weight(mock_message, mock_state)
            
            # Verify weight was stored correctly
            mock_state.update_data.assert_called_once_with(weight_kg=70.5)
    
    @pytest.mark.asyncio
    async def test_process_weight_invalid_too_light(self, mock_message, mock_state):
        """Test processing weight that's too light"""
        mock_message.text = "10"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_weight(mock_message, mock_state)
            
            # Verify error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "❌ **Invalid weight**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_activity_sedentary(self, mock_callback, mock_state):
        """Test processing sedentary activity selection"""
        mock_callback.data = "activity_sedentary"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_activity(mock_callback, mock_state)
            
            # Verify activity was stored
            mock_state.update_data.assert_called_once_with(activity_level="sedentary")
            
            # Verify state moved to goal
            mock_state.set_state.assert_called_once_with(ProfileStates.waiting_for_goal)
            
            # Verify success message and goal prompt were sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Activity Level: 😴 Sedentary" in call_args
            assert "🎯 **Step 6/6: Your Goal**" in call_args
    
    @pytest.mark.asyncio
    async def test_process_activity_moderately_active(self, mock_callback, mock_state):
        """Test processing moderately active selection"""
        mock_callback.data = "activity_moderately_active"
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user:
            
            await process_activity(mock_callback, mock_state)
            
            # Verify activity was stored
            mock_state.update_data.assert_called_once_with(activity_level="moderately_active")
            
            # Verify success message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Activity Level: 🏃 Moderately Active" in call_args
    
    @pytest.mark.asyncio
    async def test_process_goal_maintain_weight(self, mock_callback, mock_state):
        """Test processing maintain weight goal selection"""
        mock_callback.data = "goal_maintain_weight"
        
        # Mock state data
        mock_state.get_data.return_value = {
            'age': 25,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 70,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
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
            
            await process_goal(mock_callback, mock_state)
            
            # Verify goal was stored
            mock_state.update_data.assert_called_once_with(goal="maintain_weight")
            
            # Verify profile was created
            mock_create_profile.assert_called_once()
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify success message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Profile Created Successfully!" in call_args
            assert "Daily Calorie Target: 2200 calories" in call_args
    
    @pytest.mark.asyncio
    async def test_process_goal_lose_weight(self, mock_callback, mock_state):
        """Test processing lose weight goal selection"""
        mock_callback.data = "goal_lose_weight"
        
        # Mock state data
        mock_state.get_data.return_value = {
            'age': 30,
            'gender': 'female',
            'height_cm': 165,
            'weight_kg': 65,
            'activity_level': 'lightly_active',
            'goal': 'lose_weight'
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
            mock_create_profile.return_value = ({'daily_calories_target': 1800}, True)
            
            await process_goal(mock_callback, mock_state)
            
            # Verify success message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Profile Created Successfully!" in call_args
            assert "Goal: 📉 Lose Weight" in call_args
    
    @pytest.mark.asyncio
    async def test_process_goal_error_handling(self, mock_callback, mock_state):
        """Test error handling in goal processing"""
        mock_callback.data = "goal_maintain_weight"
        
        # Mock state data
        mock_state.get_data.return_value = {
            'age': 25,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 70,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
        }
        
        with patch('handlers.profile.get_or_create_user', new=AsyncMock(return_value={'language': 'en'})) as mock_get_user, \
             patch('handlers.profile.get_user_with_profile') as mock_get_profile, \
             patch('handlers.profile.create_or_update_profile', side_effect=Exception("Database error")):
            
            mock_get_user.return_value = {'language': 'en'}
            mock_get_profile.return_value = {
                'user': {'id': 'user-uuid'},
                'profile': None
            }
            
            await process_goal(mock_callback, mock_state)
            
            # Verify error message was sent
            mock_callback.answer.assert_called_once()
            call_args = mock_callback.answer.call_args[0][0]
            assert "error_general" in call_args or "An error occurred" in call_args
            
            # Verify state was cleared on error
            mock_state.clear.assert_called_once()


class TestProfileOnboardingIntegration:
    """Integration tests for complete profile onboarding flow"""
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_flow(self):
        """Test complete profile onboarding flow from start to finish"""
        # This test would simulate the complete flow
        # Implementation would be similar to the individual tests above
        # but would test the entire sequence as one unit
        pass
    
    @pytest.mark.asyncio
    async def test_onboarding_with_russian_language(self):
        """Test profile onboarding with Russian language"""
        # Test that all messages are properly localized
        pass
    
    @pytest.mark.asyncio
    async def test_onboarding_error_recovery(self):
        """Test that onboarding can recover from errors"""
        # Test that users can retry after invalid inputs
        pass 