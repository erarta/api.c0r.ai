"""
Test nutrition insights formatting and Telegram compatibility
"""
import pytest
import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'api.c0r.ai')))

from app.handlers.nutrition import generate_nutrition_insights, get_goal_specific_advice


class TestNutritionInsightsFormatting:
    """Test nutrition insights formatting to prevent Telegram errors"""
    
    @pytest.mark.asyncio
    async def test_generate_insights_with_complete_profile(self):
        """Test insights generation with complete profile"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 75.0,
            'height_cm': 180.0,
            'activity_level': 'moderately_active',
            'goal': 'lose_weight',
            'daily_calories_target': 2000
        }
        
        user = {
            'id': 'test-user-123',
            'credits_remaining': 100
        }
        
        # This should not raise any exceptions
        result = await generate_nutrition_insights(profile, user)
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Verify no unmatched markdown entities
        assert self._check_markdown_entities(result)
        
        # Verify all sections are present
        assert "Your Nutrition Analysis" in result
        assert "Body Mass Index (BMI)" in result
        assert "Metabolic Age" in result
        assert "Daily Water Needs" in result
        assert "Optimal Macro Distribution" in result
        assert "Personal Recommendations" in result
        assert "Goal-Specific Advice" in result
        
    @pytest.mark.asyncio
    async def test_generate_insights_with_minimal_profile(self):
        """Test insights generation with minimal profile data"""
        profile = {
            'age': 25,
            'weight_kg': 70.0,
            'height_cm': 175.0,
            'gender': 'female',
            'activity_level': 'sedentary',
            'goal': 'maintain_weight'
            # No daily_calories_target
        }
        
        user = {
            'id': 'test-user-456',
            'credits_remaining': 50
        }
        
        # This should not raise any exceptions
        result = await generate_nutrition_insights(profile, user)
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Verify no unmatched markdown entities
        assert self._check_markdown_entities(result)
        
        # Should have basic sections but not macro distribution
        assert "Your Nutrition Analysis" in result
        assert "Body Mass Index (BMI)" in result
        assert "Daily Water Needs" in result
        # Should NOT have macro distribution without calories
        assert "Optimal Macro Distribution" not in result
        
    @pytest.mark.asyncio
    async def test_generate_insights_with_edge_case_values(self):
        """Test insights generation with edge case values"""
        profile = {
            'age': 18,  # Minimum age
            'gender': 'male',
            'weight_kg': 45.0,  # Very low weight
            'height_cm': 150.0,  # Short height
            'activity_level': 'extremely_active',
            'goal': 'gain_weight',
            'daily_calories_target': 3000
        }
        
        user = {
            'id': 'test-user-789',
            'credits_remaining': 0
        }
        
        # This should not raise any exceptions
        result = await generate_nutrition_insights(profile, user)
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Verify no unmatched markdown entities
        assert self._check_markdown_entities(result)
        
    @pytest.mark.asyncio
    async def test_generate_insights_with_zero_values(self):
        """Test insights generation with zero values"""
        profile = {
            'age': 0,
            'gender': 'unknown',
            'weight_kg': 0,
            'height_cm': 0,
            'activity_level': 'sedentary',
            'goal': 'maintain_weight',
            'daily_calories_target': 0
        }
        
        user = {
            'id': 'test-user-000',
            'credits_remaining': 10
        }
        
        # This should not raise any exceptions
        result = await generate_nutrition_insights(profile, user)
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should only have basic header and footer
        assert "Your Nutrition Analysis" in result
        assert "Analysis Date" in result
        assert "Credits Remaining" in result
        
    def test_goal_specific_advice_all_goals(self):
        """Test goal-specific advice for all goal types"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 75.0,
            'height_cm': 180.0,
            'activity_level': 'moderately_active',
            'daily_calories_target': 2000
        }
        
        goals = ['lose_weight', 'gain_weight', 'maintain_weight']
        
        for goal in goals:
            advice = get_goal_specific_advice(goal, profile)
            
            # Verify advice is a string
            assert isinstance(advice, str)
            assert len(advice) > 0
            
            # Verify no unmatched markdown entities
            assert self._check_markdown_entities(advice)
            
            # Verify goal-specific content
            if goal == 'lose_weight':
                assert "Weight Loss Journey" in advice
                assert "calorie deficit" in advice
            elif goal == 'gain_weight':
                assert "Weight Gain Plan" in advice
                assert "calorie surplus" in advice
            else:  # maintain_weight
                assert "Maintenance Mastery" in advice
                assert "sweet spot" in advice
                
    def test_markdown_entity_validation(self):
        """Test various markdown patterns that could cause issues"""
        test_strings = [
            "**Bold text**",
            "**Bold with emoji 🎯**",
            "**Bold:**: Regular text",
            "**Bold** and **more bold**",
            "• Bullet point with **bold**",
            "Text with **bold** and *italic*",
            "🔬 **Header:**\n• Bullet with **bold**"
        ]
        
        for test_string in test_strings:
            assert self._check_markdown_entities(test_string), f"Failed for: {test_string}"
            
    @pytest.mark.asyncio
    async def test_string_length_limits(self):
        """Test that generated strings are within reasonable limits"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 75.0,
            'height_cm': 180.0,
            'activity_level': 'moderately_active',
            'goal': 'lose_weight',
            'daily_calories_target': 2000
        }
        
        user = {
            'id': 'test-user-123',
            'credits_remaining': 100
        }
        
        result = await generate_nutrition_insights(profile, user)
        
        # Telegram message limit is 4096 characters
        assert len(result) < 4000, f"Message too long: {len(result)} characters"
        
    def _check_markdown_entities(self, text: str) -> bool:
        """
        Check if markdown entities are properly matched
        
        Args:
            text: Text to check
            
        Returns:
            True if entities are properly matched, False otherwise
        """
        # Count bold entities
        bold_count = text.count('**')
        if bold_count % 2 != 0:
            return False
            
        # Check for common problematic patterns
        problematic_patterns = [
            '***',  # Three asterisks
            '****',  # Four asterisks
            '**\n**',  # Bold across newlines
            '**  **',  # Empty bold
        ]
        
        for pattern in problematic_patterns:
            if pattern in text:
                return False
                
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 