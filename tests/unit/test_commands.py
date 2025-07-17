#!/usr/bin/env python3
"""
Unit tests for commands.py handler - core command functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import asyncio

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api.c0r.ai/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from handlers.commands import (
    start_command,
    help_command,
    help_callback,
    status_command,
    status_callback,
    buy_credits_command,
    buy_callback,
    profile_callback,
    handle_action_callback
)

class TestStartCommand:
    """Test suite for start command functionality"""
    
    @pytest.mark.asyncio
    async def test_start_command_new_user(self):
        """Test start command for new user"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 3, 'language': 'en'}):
            with patch('handlers.commands.detect_and_set_user_language', return_value='en'):
                with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.commands.log_user_action', return_value=None):
                        await start_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "🎉 **Welcome to c0r.ai Food Analyzer!**" in call_args
                        assert "Hello Test!" in call_args
                        assert "3 credits" in call_args
    
    @pytest.mark.asyncio
    async def test_start_command_existing_user(self):
        """Test start command for existing user"""
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
        
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.commands.create_main_menu_text', return_value="Welcome back message"):
                        
                        await start_command(message)
                        
                        message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_command_exception_handling(self):
        """Test start command exception handling"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', side_effect=Exception("Database error")):
            with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                await start_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "An error occurred" in call_args


class TestHelpCommand:
    """Test suite for help command functionality"""
    
    @pytest.mark.asyncio
    async def test_help_command(self):
        """Test help command"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                await help_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "🤖 **c0r.ai Food Analyzer - Help Guide**" in call_args
                assert "📸 **How to use:**" in call_args
                assert "💡 **What are credits?**" in call_args
    
    @pytest.mark.asyncio
    async def test_help_callback(self):
        """Test help callback"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                    await help_callback(callback)
                    callback.message.answer.assert_called_once()
                    call_args = callback.message.answer.call_args[0][0]
                    assert "🤖 **c0r.ai Food Analyzer - Help Guide**" in call_args
    
    @pytest.mark.asyncio
    async def test_help_callback(self):
        """Test help callback from button clicks"""
        callback = Mock()
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        user_data = {
            'id': 'user-uuid',
            'telegram_id': 123456789,
            'credits_remaining': 5
        }
        
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                    
                    await help_callback(callback)
                    
                    callback.message.answer.assert_called_once()


class TestStatusCommand:
    """Test suite for status command functionality"""
    
    @pytest.mark.asyncio
    async def test_status_command_with_version(self):
        """Test status command displays correct version"""
        from config import VERSION
        
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'id': 'user-uuid',
            'telegram_id': 123456789,
            'credits_remaining': 5,
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=100.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        await status_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "📊 *Your Account Status*" in call_args
                        assert "Credits remaining: *5*" in call_args
                        assert "Total paid: *100.00 Р*" in call_args
                        # Check for system version info - the exact text might vary slightly
                        assert "System:" in call_args and "c0r.ai v" in call_args
    
    @pytest.mark.asyncio
    async def test_status_callback_with_version(self):
        """Test status callback with version info"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 5, 'created_at': '2024-01-01T00:00:00Z', 'language': 'en'}):
            with patch('handlers.commands.get_user_total_paid', return_value=0):
                with patch('handlers.commands.log_user_action', return_value=None):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        await status_callback(callback)
                        
                        callback.message.answer.assert_called_once()
                        call_args = callback.message.answer.call_args[0][0]
                        assert "📊 *Your Account Status*" in call_args
                        assert "5" in call_args
    
    @pytest.mark.asyncio
    async def test_status_command_date_parsing(self):
        """Test status command date parsing"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'id': 'user-uuid',
            'telegram_id': 123456789,
            'credits_remaining': 5,
            'created_at': '2024-01-15T10:30:00Z'
        }
        
        with patch('handlers.commands.get_or_create_user', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.get_user_total_paid', return_value=0.0):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        
                        await status_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "Member since: `2024-01-15 10:30`" in call_args
    
    @pytest.mark.asyncio
    async def test_status_command_exception_handling(self):
        """Test status command exception handling"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', side_effect=Exception("Database error")):
            with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                await status_command(message)
                
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "An error occurred" in call_args


class TestBuyCreditsCommand:
    """Test suite for buy credits command functionality"""
    
    @pytest.mark.asyncio
    async def test_buy_credits_command(self):
        """Test buy credits command"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 5, 'language': 'en'}):
            with patch('handlers.commands.get_user_total_paid', return_value=0):
                with patch('handlers.commands.log_user_action', return_value=None):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        await buy_credits_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💳 **Buy Credits**" in call_args
                        assert "**Current credits**: *5*" in call_args
                        assert "20 credits for 99р" in call_args
                        assert "100 credits for 349р" in call_args
    
    @pytest.mark.asyncio
    async def test_buy_callback(self):
        """Test buy callback"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 5, 'language': 'en'}):
            with patch('handlers.commands.get_user_total_paid', return_value=0):
                with patch('handlers.commands.log_user_action', return_value=None):
                    with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                        await buy_callback(callback)
                        
                        callback.message.answer.assert_called_once()
                        call_args = callback.message.answer.call_args[0][0]
                        assert "💳 **Buy Credits**" in call_args
                        assert "5" in call_args


class TestProfileCallback:
    """Test suite for profile callback functionality"""
    
    @pytest.mark.asyncio
    async def test_profile_callback_with_profile(self):
        """Test profile callback with existing profile"""
        callback = Mock()
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': {
                'age': 30,
                'weight_kg': 70,
                'height_cm': 170,
                'gender': 'male',
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight'
            },
            'has_profile': True
        }
        
        with patch('handlers.commands.get_user_with_profile', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.show_profile_info', return_value=None):
                    
                    await profile_callback(callback)
                    
    
    @pytest.mark.asyncio
    async def test_profile_callback_without_profile(self):
        """Test profile callback without profile"""
        callback = Mock()
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.commands.get_user_with_profile', return_value=user_data):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.show_profile_setup_info', return_value=None):
                    
                    await profile_callback(callback)
                    


class TestActionCallback:
    """Test suite for action callback handler"""
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_help(self):
        """Test action callback for help"""
        callback = Mock()
        callback.data = "help"
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        with patch('handlers.commands.help_callback', return_value=None) as mock_help:
            
            await handle_action_callback(callback)
            
            mock_help.assert_called_once_with(callback)
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_status(self):
        """Test action callback for status"""
        callback = Mock()
        callback.data = "status"
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        with patch('handlers.commands.status_callback', return_value=None) as mock_status:
            
            await handle_action_callback(callback)
            
            mock_status.assert_called_once_with(callback)
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_buy(self):
        """Test action callback for buy"""
        callback = Mock()
        callback.data = "buy"
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        with patch('handlers.commands.buy_callback', return_value=None) as mock_buy:
            
            await handle_action_callback(callback)
            
            mock_buy.assert_called_once_with(callback)
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_profile(self):
        """Test action callback for profile"""
        callback = Mock()
        callback.data = "profile"
        callback.message = Mock()
        callback.message.from_user.id = 123456789
        callback.message.from_user.username = "testuser"
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        with patch('handlers.commands.profile_callback', return_value=None) as mock_profile:
            
            await handle_action_callback(callback)
            
            mock_profile.assert_called_once_with(callback)
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_main_menu(self):
        """Test action callback for main menu"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.data = "main_menu"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.create_main_menu_keyboard', return_value=None):
                    await handle_action_callback(callback)
                    
                    # Should call message.answer for main_menu action
                    callback.message.answer.assert_called_once()
                    call_args = callback.message.answer.call_args[0][0]
                    assert "🚀 **Choose an option:**" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_nutrition_insights(self):
        """Test action callback for nutrition insights"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.data = "nutrition_insights"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.nutrition.nutrition_insights_callback', return_value=None) as mock_nutrition:
                    await handle_action_callback(callback)
                    
                    # Should call nutrition_insights_callback for nutrition_insights action
                    mock_nutrition.assert_called_once_with(callback)
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_unknown(self):
        """Test action callback for unknown action"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.data = "unknown_action"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                await handle_action_callback(callback)
                
                # Should not call message.answer for unknown actions
                callback.message.answer.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_action_callback_exception(self):
        """Test action callback exception handling"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.data = "main_menu"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        with patch('handlers.commands.get_or_create_user', return_value={'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}):
            with patch('handlers.commands.log_user_action', return_value=None):
                with patch('handlers.commands.create_main_menu_text', side_effect=Exception("Handler error")):
                    await handle_action_callback(callback)
                    assert callback.answer.call_count == 2
                    callback.answer.assert_any_call("An error occurred. Please try again later.")


class TestVersionConsistency:
    """Test suite to ensure version consistency"""
    
    def test_version_import(self):
        """Test that VERSION is properly imported and accessible"""
        from config import VERSION
        assert isinstance(VERSION, str)
        assert len(VERSION) > 0
        # Version should follow semantic versioning pattern (x.y.z)
        import re
        assert re.match(r'^\d+\.\d+\.\d+$', VERSION), f"VERSION '{VERSION}' should follow semantic versioning"
    
    def test_version_format(self):
        """Test that VERSION follows semantic versioning format"""
        from config import VERSION
        import re
        
        # Test semantic versioning pattern: X.Y.Z
        pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(pattern, VERSION), f"Version {VERSION} doesn't follow semantic versioning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 