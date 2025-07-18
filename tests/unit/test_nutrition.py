#!/usr/bin/env python3
"""
Unit tests for nutrition.py handler - critical component testing
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from aiogram import types

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api.c0r.ai/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from handlers.nutrition import (
    nutrition_insights_command,
    nutrition_insights_callback,
    generate_nutrition_insights,
    get_goal_specific_advice,
    weekly_report_command,
    water_tracker_command,
    sanitize_markdown_text
)

class TestNutritionInsights:
    """Test suite for nutrition insights functionality"""
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_with_none_profile(self):
        """Test the critical bug: nutrition insights with None profile"""
        # Mock message
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        # Mock user data with None profile (the bug scenario)
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': None,  # This caused the original bug
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.get_or_create_user', return_value={'id': 'user-uuid', 'language': 'en'}):
                        
                        # This should NOT raise an exception
                        await nutrition_insights_command(message)
                    
                    # Verify it shows profile setup message
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "**Nutrition Insights**" in call_args
                    assert "Almost ready! Please complete your profile" in call_args
                    assert "Missing:" in call_args
                    assert "age, weight_kg, height_cm, gender, activity_level, goal" in call_args
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_with_empty_profile(self):
        """Test nutrition insights with empty profile dict"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': {},  # Empty profile
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.get_or_create_user', return_value={'id': 'user-uuid', 'language': 'en'}):
                        
                        await nutrition_insights_command(message)
                    
                    # Should show missing fields message
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "Missing:" in call_args
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_with_partial_profile(self):
        """Test nutrition insights with partial profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': {'age': 30, 'weight_kg': 70},  # Partial profile
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                    
                    await nutrition_insights_command(message)
                    
                    # Should show missing fields
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "Missing:" in call_args
                    assert "height_cm, gender, activity_level, goal" in call_args
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_with_complete_profile(self):
        """Test nutrition insights with complete profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        complete_profile = {
            'age': 30,
            'weight_kg': 70,
            'height_cm': 170,
            'gender': 'male',
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
        }
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': complete_profile,
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.show_nutrition_insights_menu') as mock_show_menu:
                    
                    await nutrition_insights_command(message)
                    
                    # Should show nutrition insights menu
                    mock_show_menu.assert_called_once()
                    message.answer.assert_not_called()  # Menu is shown by show_nutrition_insights_menu
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_exception_handling(self):
        """Test exception handling in nutrition insights"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        # Mock to raise exception
        with patch('handlers.nutrition.get_user_with_profile', side_effect=Exception("Database error")):
            with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'en'}):
                
                await nutrition_insights_command(message)
                
                # Should show error message
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "❌ **Error**" in call_args
                assert "Sorry, there was an error generating your nutrition insights" in call_args
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_callback(self):
        """Test nutrition insights callback"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': {
                'age': 30,
                'gender': 'male',
                'weight_kg': 75.0,
                'height_cm': 180.0,
                'activity_level': 'moderately_active',
                'goal': 'lose_weight',
                'daily_calories_target': 2000
            },
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.show_nutrition_insights_menu') as mock_show_menu:
                    await nutrition_insights_callback(callback)
                    
                    callback.answer.assert_called_once()
                    mock_show_menu.assert_called_once()
                    callback.message.answer.assert_not_called()  # Menu is shown by show_nutrition_insights_menu

    @pytest.mark.asyncio
    async def test_nutrition_insights_callback_with_none_profile(self):
        """Test nutrition insights callback with None profile - critical bug scenario"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        # Mock user data with None profile (the original bug scenario)
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'ru'},
            'profile': None,  # This caused the original Markdown parsing error
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'ru'}):
                    
                    # This should NOT raise any exception
                    await nutrition_insights_callback(callback)
                    
                    # Should show profile setup message
                    callback.message.answer.assert_called_once()
                    call_args = callback.message.answer.call_args[0][0]
                    assert "🔍 **Анализ питания**" in call_args
                    assert "Почти готово! Пожалуйста, заверши настройку профиля" in call_args

    @pytest.mark.asyncio
    async def test_nutrition_insights_callback_exception_handling(self):
        """Test exception handling in nutrition insights callback"""
        callback = Mock()
        callback.from_user.id = 123456789
        callback.from_user.username = "testuser"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        
        # Mock to raise exception during show_nutrition_insights_menu
        with patch('handlers.nutrition.get_user_with_profile', return_value={
            'user': {'id': 'user-uuid', 'language': 'ru'},
            'profile': {'age': 30, 'weight_kg': 70, 'height_cm': 170, 'gender': 'male', 'activity_level': 'moderately_active', 'goal': 'maintain_weight'},
            'has_profile': True
        }):
            with patch('handlers.nutrition.show_nutrition_insights_menu', side_effect=Exception("Markdown parsing error")):
                with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'ru'}):
                    
                    # This should handle the exception gracefully
                    await nutrition_insights_callback(callback)
                    
                    # Should show error message
                    callback.message.answer.assert_called_once()
                    call_args = callback.message.answer.call_args[0][0]
                    assert "❌ **Ошибка**" in call_args
                    assert "Извини, произошла ошибка" in call_args

    @pytest.mark.asyncio
    async def test_nutrition_insights_russian_language(self):
        """Test nutrition insights with Russian language"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'ru'},
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.get_or_create_user', return_value={'language': 'ru'}):
                        
                        await nutrition_insights_command(message)
                    
                    # Verify Russian text is shown
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "🔍 **Анализ питания**" in call_args
                    assert "Почти готово! Пожалуйста, заверши настройку профиля" in call_args
                    assert "Отсутствует:" in call_args


class TestMarkdownSanitization:
    """Test suite for markdown sanitization functionality"""
    
    def test_sanitize_markdown_text_balanced_bold(self):
        """Test sanitize_markdown_text with balanced bold markers"""
        text = "**Test**"
        result = sanitize_markdown_text(text)
        assert result == "**Test**"
        assert result.count('**') == 2  # Balanced
    
    def test_sanitize_markdown_text_unbalanced_bold(self):
        """Test sanitize_markdown_text with unbalanced bold markers"""
        text = "**Test"
        result = sanitize_markdown_text(text)
        assert result.count('**') == 0  # Should remove unbalanced markers
    
    def test_sanitize_markdown_text_triple_asterisks(self):
        """Test sanitize_markdown_text with triple asterisks"""
        text = "***Test***"
        result = sanitize_markdown_text(text)
        assert result == "** *Test** *"
    
    def test_sanitize_markdown_text_quadruple_asterisks(self):
        """Test sanitize_markdown_text with quadruple asterisks"""
        text = "****Test****"
        result = sanitize_markdown_text(text)
        assert result == "** **Test** **"
    
    def test_sanitize_markdown_text_empty_bold(self):
        """Test sanitize_markdown_text with empty bold markers"""
        text = "**  **"
        result = sanitize_markdown_text(text)
        assert result == "** **"
    
    def test_sanitize_markdown_text_missing_translation(self):
        """Test sanitize_markdown_text with missing translation pattern"""
        text = "[Missing translation: test_key]"
        result = sanitize_markdown_text(text)
        assert result == " test_key"
    
    def test_sanitize_markdown_text_russian_text(self):
        """Test sanitize_markdown_text with Russian text"""
        text = "📊 **Анализ питания**\n\n🎯 Для показа персонального анализа питания"
        result = sanitize_markdown_text(text)
        assert result.count('**') == 2  # Should be balanced
        assert "📊 **Анализ питания**" in result
    
    def test_sanitize_markdown_text_complex_case(self):
        """Test sanitize_markdown_text with complex case that caused the original bug"""
        text = "📊 **Анализ питания**\n\n🎯 Для показа персонального анализа питания мне нужна информация о твоем профиле.\n\n💡 **Создай профиль, чтобы получить:**\n• Персональный анализ ИМТ\n• Рекомендации по идеальному весу\n• Метаболический возраст\n• Потребность в воде\n• Распределение макронутриентов\n• Персональные рекомендации"
        result = sanitize_markdown_text(text)
        assert result.count('**') == 4  # Should be balanced (2 pairs)
        assert "📊 **Анализ питания**" in result
        assert "💡 **Создай профиль, чтобы получить:**" in result


class TestGenerateNutritionInsights:
    """Test suite for generate_nutrition_insights function"""
    
    @pytest.mark.asyncio
    async def test_generate_insights_complete_profile(self):
        """Test generate_nutrition_insights with complete profile"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 75.0,
            'height_cm': 180.0,
            'activity_level': 'moderately_active',
            'goal': 'lose_weight',
            'daily_calories_target': 2000
        }
        
        user = {'language': 'en'}
        
        result = await generate_nutrition_insights(profile, user)
        
        # Should contain nutrition analysis sections
        assert "**Your Nutrition Analysis**" in result
        assert "**Body Mass Index (BMI):**" in result
        assert "**Ideal Weight Range:**" in result
        assert "**Metabolic Age:**" in result
        assert "**Daily Water Needs:**" in result
        assert "**Optimal Macro Distribution:**" in result
        
        # Should be properly sanitized
        assert result.count('**') % 2 == 0  # Balanced bold markers
    
    @pytest.mark.asyncio
    async def test_generate_insights_russian_language(self):
        """Test generate_nutrition_insights with Russian language"""
        profile = {
            'age': 25,
            'gender': 'female',
            'weight_kg': 60.0,
            'height_cm': 165.0,
            'activity_level': 'lightly_active',
            'goal': 'maintain_weight',
            'daily_calories_target': 1800
        }
        
        user = {'language': 'ru'}
        
        result = await generate_nutrition_insights(profile, user)
        
        # Should contain Russian nutrition analysis sections
        assert "**Твой анализ питания**" in result
        assert "**Индекс массы тела (ИМТ):**" in result
        assert "**Идеальный диапазон веса:**" in result
        assert "**Метаболический возраст:**" in result
        assert "**Дневные потребности в воде:**" in result
        assert "**Оптимальное распределение макронутриентов:**" in result
        
        # Should be properly sanitized
        assert result.count('**') % 2 == 0  # Balanced bold markers


class TestGoalSpecificAdvice:
    """Test suite for goal-specific advice"""
    
    def test_weight_loss_advice(self):
        """Test weight loss goal advice"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 80,
            'height_cm': 175,
            'activity_level': 'moderately_active'
        }
        
        advice = get_goal_specific_advice('lose_weight', profile, 'en')
        
        assert isinstance(advice, str)
        assert "weight" in advice.lower()
    
    def test_weight_gain_advice(self):
        """Test weight gain goal advice"""
        profile = {
            'age': 25,
            'gender': 'female',
            'weight_kg': 50,
            'height_cm': 165,
            'activity_level': 'lightly_active'
        }
        
        advice = get_goal_specific_advice('gain_weight', profile, 'en')
        
        assert isinstance(advice, str)
        assert "weight" in advice.lower()
    
    def test_maintenance_advice(self):
        """Test weight maintenance goal advice"""
        profile = {
            'age': 35,
            'gender': 'male',
            'weight_kg': 70,
            'height_cm': 170,
            'activity_level': 'moderately_active'
        }
        
        advice = get_goal_specific_advice('maintain_weight', profile, 'en')
        
        assert isinstance(advice, str)
        assert "maintenance" in advice.lower() or "sweet spot" in advice.lower() or "consistent" in advice.lower()


class TestWaterTracker:
    """Test suite for water tracker functionality"""
    
    @pytest.mark.asyncio
    async def test_water_tracker_with_profile(self):
        """Test water tracker with complete profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': {
                'weight_kg': 70,
                'activity_level': 'moderately_active'
            },
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.calculate_water_needs') as mock_water:
                        mock_water.return_value = {
                            'liters': 3.4,
                            'glasses': 14,
                            'base_ml': 2415,
                            'activity_bonus': 966,
                            'total_ml': 3381
                        }
                        
                        await water_tracker_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💧 **Your Water Needs**" in call_args
                        assert "3.4L" in call_args
                        assert "14 glasses" in call_args
    
    @pytest.mark.asyncio
    async def test_water_tracker_without_profile(self):
        """Test water tracker without profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    await water_tracker_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "💧 **Water Tracker**" in call_args
                    assert "Set up your profile" in call_args


class TestWeeklyReport:
    """Test suite for weekly report functionality"""
    
    @pytest.mark.asyncio
    async def test_weekly_report_with_profile(self):
        """Test weekly report with complete profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': {
                'weight_kg': 70,
                'activity_level': 'moderately_active'
            },
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    await weekly_report_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "📊 **Weekly Report**" in call_args
                    assert "Week of:" in call_args
    
    @pytest.mark.asyncio
    async def test_weekly_report_without_profile(self):
        """Test weekly report without profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'},
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    await weekly_report_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "📊 **Weekly Report**" in call_args
                    assert "Week of:" in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 