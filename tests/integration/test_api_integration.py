#!/usr/bin/env python3
"""
Integration tests for API handlers working together
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from aiogram import types

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api.c0r.ai/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from handlers.commands import start_command, status_command, help_command
from handlers.nutrition import nutrition_insights_command, water_tracker_command
from handlers.keyboards import create_main_menu_keyboard

class TestUserJourney:
    """Integration tests for complete user journey"""
    
    @pytest.mark.asyncio
    async def test_new_user_complete_flow(self):
        """Test complete flow for new user from start to nutrition insights"""
        from config import VERSION
        
        # Mock user
        user_id = 123456789
        username = "testuser"
        
        # Mock message
        message = Mock()
        message.from_user.id = user_id
        message.from_user.username = username
        message.answer = AsyncMock()
        
        # Mock new user creation
        new_user = {
            'id': 'user-uuid',
            'telegram_id': user_id,
            'credits_remaining': 3,
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        # Test 1: Start command for new user
        with patch('handlers.commands.get_or_create_user', return_value=new_user):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.detect_and_set_user_language', return_value='en'):
                    
                    await start_command(message)
                    
                    # Verify start command worked
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "🎉 **Welcome to c0r.ai Food Analyzer!**" in call_args
                    assert "💳 You have **3 credits** remaining" in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test 2: Status command shows correct information
        with patch('handlers.commands.get_or_create_user', return_value=new_user):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=0.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        await status_command(message)
                        
                        # Verify status shows correct info
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💳 Credits remaining: *3*" in call_args
                        assert "💰 Total paid: *0.00 Р*" in call_args
                        assert f"System: *c0r.ai v{VERSION}*" in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test 3: Nutrition insights without profile
        user_data_no_profile = {
            'user': new_user,
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data_no_profile):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                    
                    await nutrition_insights_command(message)
                    
                    # Verify shows profile setup message
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "**Nutrition Insights**" in call_args
                    assert "Please complete your profile" in call_args
    
    @pytest.mark.asyncio
    async def test_existing_user_with_profile_flow(self):
        """Test flow for existing user with complete profile"""
        # Mock user with profile
        user_id = 987654321
        username = "existinguser"
        
        message = Mock()
        message.from_user.id = user_id
        message.from_user.username = username
        message.answer = AsyncMock()
        
        # Mock existing user with profile
        existing_user = {
            'id': 'existing-user-uuid',
            'telegram_id': user_id,
            'credits_remaining': 25,
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        complete_profile = {
            'age': 30,
            'weight_kg': 70,
            'height_cm': 175,
            'gender': 'male',
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
        }
        
        user_data_with_profile = {
            'user': existing_user,
            'profile': complete_profile,
            'has_profile': True
        }
        
        # Test 1: Start command for existing user
        with patch('handlers.commands.get_or_create_user', return_value=existing_user):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.detect_and_set_user_language', return_value='en'):
                    
                    await start_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "🎉 **Welcome to c0r.ai Food Analyzer!**" in call_args
                    assert "💳 You have **25 credits** remaining" in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test 2: Status command shows paid user info
        with patch('handlers.commands.get_or_create_user', return_value=existing_user):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=399.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        await status_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💳 Credits remaining: *25*" in call_args
                        assert "💰 Total paid: *399.00 Р*" in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test 3: Nutrition insights with complete profile
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data_with_profile):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.show_nutrition_insights_menu') as mock_show_menu:
                    
                    await nutrition_insights_command(message)
                    
                    # Verify shows nutrition insights menu
                    mock_show_menu.assert_called_once()
                    message.answer.assert_not_called()  # Menu is shown by show_nutrition_insights_menu
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test 4: Water tracker with profile
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data_with_profile):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.calculate_water_needs') as mock_water:
                        mock_water.return_value = {
                            'liters': 2.8,
                            'glasses': 11,
                            'base_ml': 2450,
                            'activity_bonus': 350,
                            'total_ml': 2800
                        }
                        
                        await water_tracker_command(message)
                        
                        # Verify water tracker works
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💧 **Your Water Needs**" in call_args
                        assert "2.8" in call_args
                        assert "11" in call_args


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components"""
    
    @pytest.mark.asyncio
    async def test_database_error_propagation(self):
        """Test that database errors are handled gracefully across all handlers"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        # Test database error in start command
        with patch('handlers.commands.get_or_create_user', side_effect=Exception("Database connection failed")):
            with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                
                await start_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "An error occurred. Please try again later." in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test database error in status command
        with patch('handlers.commands.get_or_create_user', side_effect=Exception("Database connection failed")):
            with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                
                await status_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "An error occurred while fetching your status. Please try again later." in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test database error in nutrition insights
        with patch('handlers.nutrition.get_user_with_profile', side_effect=Exception("Database connection failed")):
            with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                
                await nutrition_insights_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "❌ **Error**" in call_args
    
    @pytest.mark.asyncio
    async def test_partial_data_handling(self):
        """Test handling of partial or corrupted data"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        # Test user with corrupted profile data
        corrupted_user_data = {
            'user': {
                'id': 'user-uuid',
                'telegram_id': 123456789,
                'credits_remaining': 5
            },
            'profile': {
                'age': 30,
                'weight_kg': None,  # Missing weight
                'height_cm': 175,
                'gender': 'male',
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight'
            },
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=corrupted_user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                    
                    await nutrition_insights_command(message)
                    
                    # Should handle missing weight gracefully
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "Missing:" in call_args
                    assert "weight_kg" in call_args


class TestKeyboardIntegration:
    """Integration tests for keyboard functionality"""
    
    def test_main_menu_keyboard_creation(self):
        """Test that main menu keyboard is created correctly"""
        keyboard = create_main_menu_keyboard()
        
        # Keyboard should be created without errors
        assert keyboard is not None
    
    @pytest.mark.asyncio
    async def test_keyboard_consistency_across_handlers(self):
        """Test that keyboards are consistent across different handlers"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'id': 'user-uuid',
            'telegram_id': 123456789,
            'credits_remaining': 10
        }
        
        # Test that start command works
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.detect_and_set_user_language', return_value='en'):
                    
                    await start_command(message)
                    
                    # Verify start command worked
                    message.answer.assert_called_once()
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test help command works
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                
                await help_command(message)
                
                # Verify help command worked
                message.answer.assert_called_once()


class TestVersionConsistencyIntegration:
    """Integration tests for version consistency across the system"""
    
    @pytest.mark.asyncio
    async def test_version_in_status_commands(self):
        """Test that version is displayed consistently in status commands"""
        from config import VERSION
        
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'id': 'user-uuid',
            'telegram_id': 123456789,
            'credits_remaining': 10,
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        # Test status command
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=0.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        await status_command(message)
                        
                        # Verify version is displayed
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert f"System: *c0r.ai v{VERSION}*" in call_args
        
        # Reset mock
        message.answer.reset_mock()
        
        # Test status callback
        callback = Mock()
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=0.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        from handlers.commands import status_callback
                        await status_callback(callback)
                        
                        # Verify version is displayed in callback too
                        callback.message.answer.assert_called_once()
                        call_args = callback.message.answer.call_args[0][0]
                        assert f"System: *c0r.ai v{VERSION}*" in call_args


class TestCriticalPathsIntegration:
    """Integration tests for critical user paths"""
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_critical_path(self):
        """Test the critical path that was causing the original bug"""
        message = Mock()
        message.from_user.id = 7918860162  # Same user ID from the logs
        message.from_user.username = "c0rAIBot"
        message.answer = AsyncMock()
        
        # Simulate the exact scenario from the logs
        user_data = {
            'user': {
                'id': 'cbdbed50-7746-4c4f-842f-95e468fe823c',
                'telegram_id': 7918860162,
                'credits_remaining': 3,
                'created_at': '2025-07-11T18:45:25.375716+00:00'
            },
            'profile': None,  # This was causing the bug
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                    
                    # This should NOT raise an exception anymore
                    await nutrition_insights_command(message)
                    
                    # Verify it shows profile setup message instead of crashing
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "**Nutrition Insights**" in call_args
                    assert "Please complete your profile" in call_args
                    assert "Missing:" in call_args
                    assert "age, weight_kg, height_cm, gender, activity_level, goal" in call_args
    
    @pytest.mark.asyncio
    async def test_user_with_profile_critical_path(self):
        """Test the path for user with complete profile (like user 391490 from logs)"""
        message = Mock()
        message.from_user.id = 391490  # Same user ID from the logs
        message.from_user.username = "edubskiy"
        message.answer = AsyncMock()
        
        # Simulate the exact scenario from the logs
        user_data = {
            'user': {
                'id': 'c32ee412-5d6d-44df-914a-0276171e7456',
                'telegram_id': 391490,
                'credits_remaining': 115,
                'created_at': '2025-07-11T18:38:15.858729+00:00'
            },
            'profile': {
                'id': '3027584c-1585-4603-ab0b-71b56ffb7ed7',
                'user_id': 'c32ee412-5d6d-44df-914a-0276171e7456',
                'age': 38,
                'gender': 'male',
                'height_cm': 170,
                'weight_kg': 69.0,
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight',
                'daily_calories_target': 2430,
                'created_at': '2025-07-11T18:41:35.773524+00:00',
                'updated_at': '2025-07-12T10:34:47.876701+00:00'
            },
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.show_nutrition_insights_menu') as mock_show_menu:
                    
                    # This should show nutrition insights menu
                    await nutrition_insights_command(message)
                    
                    # Verify it shows nutrition insights menu
                    mock_show_menu.assert_called_once()
                    message.answer.assert_not_called()  # Menu is shown by show_nutrition_insights_menu


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 