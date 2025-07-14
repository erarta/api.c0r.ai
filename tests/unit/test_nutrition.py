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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from handlers.nutrition import (
    nutrition_insights_command,
    nutrition_insights_callback,
    generate_nutrition_insights,
    get_goal_specific_advice,
    weekly_report_command,
    water_tracker_command
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
                    
                    # This should NOT raise an exception
                    await nutrition_insights_command(message)
                    
                    # Verify it shows profile setup message
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "🔍 **Nutrition Insights**" in call_args
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
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    
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
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': complete_profile,
            'has_profile': True
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.generate_nutrition_insights', return_value="Mocked insights"):
                        
                        await nutrition_insights_command(message)
                        
                        # Should generate insights
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert call_args == "Mocked insights"
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_exception_handling(self):
        """Test exception handling in nutrition insights"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        # Mock to raise exception
        with patch('handlers.nutrition.get_user_with_profile', side_effect=Exception("Database error")):
            with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                
                await nutrition_insights_command(message)
                
                # Should show error message
                message.answer.assert_called_once()
                call_args = message.answer.call_args[0][0]
                assert "❌ **Error**" in call_args
                assert "Sorry, there was an error generating your nutrition insights" in call_args
    
    @pytest.mark.asyncio
    async def test_nutrition_insights_callback(self):
        """Test nutrition insights callback from button clicks"""
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
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    
                    await nutrition_insights_callback(callback)
                    
                    # Should answer callback
                    callback.answer.assert_called_once()
                    # Should show profile setup message
                    callback.message.answer.assert_called_once()


class TestGenerateNutritionInsights:
    """Test suite for generate_nutrition_insights function"""
    
    @pytest.mark.asyncio
    async def test_generate_insights_complete_profile(self):
        """Test insights generation with complete profile"""
        profile = {
            'age': 30,
            'weight_kg': 70,
            'height_cm': 170,
            'gender': 'male',
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
        }
        
        user = {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}
        
        with patch('handlers.nutrition.calculate_bmi') as mock_bmi:
            with patch('handlers.nutrition.calculate_ideal_weight') as mock_ideal:
                with patch('handlers.nutrition.calculate_metabolic_age') as mock_age:
                    with patch('handlers.nutrition.calculate_water_needs') as mock_water:
                        with patch('handlers.nutrition.calculate_macro_distribution') as mock_macro:
                            with patch('handlers.nutrition.calculate_meal_portions') as mock_portions:
                                with patch('handlers.nutrition.get_goal_specific_advice') as mock_advice:
                                    with patch('handlers.nutrition.get_nutrition_recommendations') as mock_recs:
                                        
                                        # Mock all calculation returns
                                        mock_bmi.return_value = {
                                            'bmi': 24.2,
                                            'category': 'normal',
                                            'emoji': '✅',
                                            'description': 'Healthy weight range',
                                            'motivation': 'Great job!'
                                        }
                                        mock_ideal.return_value = {'range': '58-72 kg', 'broca': 65.0}
                                        mock_age.return_value = {
                                            'metabolic_age': 28, 
                                            'emoji': '✅',
                                            'description': 'Your metabolism matches your age',
                                            'motivation': 'Excellent!'
                                        }
                                        mock_water.return_value = {'liters': 2.5, 'glasses': 10, 'base_ml': 2450, 'activity_bonus': 50}
                                        mock_macro.return_value = {
                                            'protein': {'grams': 140, 'percent': 25},
                                            'fat': {'grams': 70, 'percent': 30},
                                            'carbs': {'grams': 250, 'percent': 45}
                                        }
                                        mock_portions.return_value = {
                                            'meal_breakdown': [
                                                {'name': 'Breakfast', 'calories': 500, 'percent': 25},
                                                {'name': 'Lunch', 'calories': 800, 'percent': 40},
                                                {'name': 'Dinner', 'calories': 700, 'percent': 35}
                                            ]
                                        }
                                        mock_advice.return_value = "Maintain your current approach"
                                        mock_recs.return_value = ["Drink more water", "Eat vegetables"]
                                        
                                        insights = await generate_nutrition_insights(profile, user)
                                        
                                        # Check that insights contain key information
                                        assert "🔬 **Nutrition Insights**" in insights
                                        assert "BMI" in insights
                                        assert "24.2" in insights
                                        assert "✅" in insights
                                        assert "Great job!" in insights


class TestGoalSpecificAdvice:
    """Test suite for goal-specific advice"""
    
    def test_weight_loss_advice(self):
        """Test advice for weight loss goal"""
        profile = {
            'goal': 'lose_weight',
            'weight_kg': 80,
            'height_cm': 170,
            'activity_level': 'moderately_active'
        }
        
        advice = get_goal_specific_advice('lose_weight', profile)
        
        assert "sustainable wins" in advice.lower()
        assert "gentle deficit" in advice.lower()
        assert "🎯" in advice
    
    def test_weight_gain_advice(self):
        """Test advice for weight gain goal"""
        profile = {
            'goal': 'gain_weight',
            'weight_kg': 60,
            'height_cm': 170,
            'activity_level': 'moderately_active'
        }
        
        advice = get_goal_specific_advice('gain_weight', profile)
        
        assert "healthy weight building" in advice.lower()
        assert "steady progress" in advice.lower()
        assert "💪" in advice
    
    def test_maintenance_advice(self):
        """Test advice for maintenance goal"""
        profile = {
            'goal': 'maintain_weight',
            'weight_kg': 70,
            'height_cm': 170,
            'activity_level': 'moderately_active'
        }
        
        advice = get_goal_specific_advice('maintain_weight', profile)
        
        assert "sweet spot" in advice.lower()
        assert "joyful eating" in advice.lower()
        assert "🎉" in advice


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
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
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
                            'liters': 2.5,
                            'glasses': 10,
                            'base_water': 2.45,
                            'activity_bonus': 0.05
                        }
                        
                        await water_tracker_command(message)
                        
                        message.answer.assert_called_once()
                        call_args = message.answer.call_args[0][0]
                        assert "💧 **Water Tracker**" in call_args
                        assert "2.5" in call_args
                        assert "10" in call_args
    
    @pytest.mark.asyncio
    async def test_water_tracker_without_profile(self):
        """Test water tracker without profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
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
                    assert "Please complete your profile" in call_args


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
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    
                    await weekly_report_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "📈 **Weekly Report**" in call_args
                    assert "Coming soon" in call_args
    
    @pytest.mark.asyncio
    async def test_weekly_report_without_profile(self):
        """Test weekly report without profile"""
        message = Mock()
        message.from_user.id = 123456789
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        
        user_data = {
            'user': {'id': 'user-uuid', 'credits_remaining': 10},
            'profile': None,
            'has_profile': False
        }
        
        with patch('handlers.nutrition.get_user_with_profile', return_value=user_data):
            with patch('handlers.nutrition.log_user_action', return_value=None):
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    
                    await weekly_report_command(message)
                    
                    message.answer.assert_called_once()
                    call_args = message.answer.call_args[0][0]
                    assert "📈 **Weekly Report**" in call_args
                    assert "Please complete your profile" in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 