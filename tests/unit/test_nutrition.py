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
                with patch('handlers.nutrition.create_main_menu_keyboard', return_value=None):
                    with patch('handlers.nutrition.generate_nutrition_insights', return_value="Mock insights"):
                        await nutrition_insights_callback(callback)
                        
                        callback.answer.assert_called_once()
                        callback.message.answer.assert_called_once()
                        call_args = callback.message.answer.call_args[0][0]
                        assert "Mock insights" in call_args


class TestGenerateNutritionInsights:
    """Test suite for generate_nutrition_insights function"""
    
    @pytest.mark.asyncio
    async def test_generate_insights_complete_profile(self):
        """Test nutrition insights generation with complete profile"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 75.0,
            'height_cm': 180.0,
            'activity_level': 'moderately_active',
            'goal': 'lose_weight',
            'daily_calories_target': 2000
        }
        
        user = {'id': 'user-uuid', 'credits_remaining': 10, 'language': 'en'}
        
        with patch('handlers.nutrition.calculate_bmi') as mock_bmi, \
             patch('handlers.nutrition.calculate_ideal_weight') as mock_ideal, \
             patch('handlers.nutrition.calculate_metabolic_age') as mock_age, \
             patch('handlers.nutrition.calculate_water_needs') as mock_water, \
             patch('handlers.nutrition.calculate_macro_distribution') as mock_macro, \
             patch('handlers.nutrition.calculate_meal_portions') as mock_meals, \
             patch('handlers.nutrition.get_nutrition_recommendations') as mock_rec, \
             patch('handlers.nutrition.get_goal_specific_advice') as mock_goal:
            
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
            mock_water.return_value = {
                'liters': 3.4,
                'glasses': 14,
                'base_ml': 2415,
                'activity_bonus': 966
            }
            mock_macro.return_value = {
                'protein': {'grams': 152, 'percent': 25},
                'carbs': {'grams': 273, 'percent': 45},
                'fat': {'grams': 81, 'percent': 30}
            }
            mock_meals.return_value = {
                'meals': [
                    {'name': 'Breakfast', 'calories': 608, 'percentage': 25},
                    {'name': 'Lunch', 'calories': 972, 'percentage': 40},
                    {'name': 'Dinner', 'calories': 850, 'percentage': 35}
                ]
            }
            mock_rec.return_value = ['Stay hydrated!', 'Eat more protein']
            mock_goal.return_value = 'Focus on portion control for weight loss success!'
            
            insights = await generate_nutrition_insights(profile, user)
            
            # Check that insights contain expected i18n-based content
            assert "🔬 **Your Nutrition Analysis**" in insights
            assert "📊 **Body Mass Index (BMI):**" in insights
            assert "✅ **24.2** - Healthy weight range" in insights
            assert "🎯 **Ideal Weight Range:**" in insights
            assert "🧬 **Metabolic Age:**" in insights
            assert "💧 **Daily Water Needs:**" in insights
            assert "🥗 **Optimal Macro Distribution:**" in insights
            assert "🍽️ **Meal Distribution:**" in insights
            assert "💡 **Personal Recommendations:**" in insights
            assert "🎯 **Goal-Specific Advice:**" in insights


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