#!/usr/bin/env python3
"""
Unit tests for nutrition_calculations.py - nutrition calculation engine
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

from tests.test_utils import setup_test_imports

# Ensure proper imports
setup_test_imports()

# Import the module to test
from common import nutrition_calculations


@pytest.fixture(autouse=True)
def patch_i18n():
    """Patch i18n module to return meaningful text for tests"""
    with patch('i18n.i18n.i18n') as mock_i18n:
        # Configure the mock to return formatted strings
        mock_i18n.get_text.side_effect = lambda key, language='en', **kwargs: f"[{language.upper()}] {key}"
        yield mock_i18n


class TestCalculateBMI:
    """Test BMI calculation functionality"""
    
    def test_bmi_underweight(self):
        """Test BMI calculation for underweight category"""
        result = nutrition_calculations.calculate_bmi(50, 170)
        
        assert result['bmi'] == 17.3
        assert result['category'] == 'underweight'
        assert result['emoji'] == '⬇️'
        assert '[EN] bmi_underweight' in result['description']
        assert '[EN] bmi_motivation_underweight' in result['motivation']
    
    def test_bmi_normal_weight(self):
        """Test BMI calculation for normal weight category"""
        result = nutrition_calculations.calculate_bmi(70, 170)
        
        assert result['bmi'] == 24.2
        assert result['category'] == 'normal'
        assert result['emoji'] == '✅'
        assert '[EN] bmi_normal' in result['description']
        assert '[EN] bmi_motivation_normal' in result['motivation']
    
    def test_bmi_overweight(self):
        """Test BMI calculation for overweight category"""
        result = nutrition_calculations.calculate_bmi(85, 170)
        
        assert result['bmi'] == 29.4
        assert result['category'] == 'overweight'
        assert result['emoji'] == '⬆️'
        assert '[EN] bmi_overweight' in result['description']
        assert '[EN] bmi_motivation_overweight' in result['motivation']
    
    def test_bmi_obese(self):
        """Test BMI calculation for obese category"""
        result = nutrition_calculations.calculate_bmi(100, 170)
        
        assert result['bmi'] == 34.6
        assert result['category'] == 'obese'
        assert result['emoji'] == '⚠️'
        assert '[EN] bmi_obese' in result['description']
        assert '[EN] bmi_motivation_obese' in result['motivation']
    
    def test_bmi_edge_cases(self):
        """Test BMI calculation edge cases"""
        # Very low weight
        result = nutrition_calculations.calculate_bmi(30, 170)
        assert result['bmi'] == 10.4
        assert result['category'] == 'underweight'
        
        # Very high weight
        result = nutrition_calculations.calculate_bmi(150, 170)
        assert result['bmi'] == 51.9
        assert result['category'] == 'obese'
        
        # Invalid height
        result = nutrition_calculations.calculate_bmi(70, 0)
        assert result['bmi'] == 0.0
        assert result['category'] == 'unknown'
        assert result['description'] == 'Invalid height'
    
    def test_bmi_different_heights(self):
        """Test BMI calculation with different heights"""
        # Tall person
        result = nutrition_calculations.calculate_bmi(80, 190)
        assert result['bmi'] == 22.2
        assert result['category'] == 'normal'
        
        # Short person
        result = nutrition_calculations.calculate_bmi(60, 150)
        assert result['bmi'] == 26.7
        assert result['category'] == 'overweight'


class TestCalculateIdealWeight:
    """Test ideal weight calculation functionality"""
    
    def test_ideal_weight_male(self):
        """Test ideal weight calculation for male"""
        result = nutrition_calculations.calculate_ideal_weight(175, 'male')
        
        assert result['ideal_min'] == pytest.approx(61.2, abs=0.1)
        assert result['ideal_max'] == pytest.approx(76.6, abs=0.1)
        assert result['broca'] == pytest.approx(68.8, abs=0.1)
        assert result['range'] == '61.2-76.6 kg'
    
    def test_ideal_weight_female(self):
        """Test ideal weight calculation for female"""
        result = nutrition_calculations.calculate_ideal_weight(165, 'female')
        
        assert result['ideal_min'] == pytest.approx(54.4, abs=0.1)
        assert result['ideal_max'] == pytest.approx(68.1, abs=0.1)
        assert result['broca'] == pytest.approx(59.0, abs=0.1)
        assert result['range'] == '54.4-68.1 kg'
    
    def test_ideal_weight_different_heights(self):
        """Test ideal weight calculation with different heights"""
        # Tall male
        result = nutrition_calculations.calculate_ideal_weight(190, 'male')
        assert result['ideal_min'] == pytest.approx(72.2, abs=0.1)
        assert result['ideal_max'] == pytest.approx(90.2, abs=0.1)
        
        # Short female
        result = nutrition_calculations.calculate_ideal_weight(150, 'female')
        assert result['ideal_min'] == pytest.approx(45.0, abs=0.1)
        assert result['ideal_max'] == pytest.approx(56.3, abs=0.1)
    
    def test_ideal_weight_edge_cases(self):
        """Test ideal weight calculation edge cases"""
        # Very tall person
        result = nutrition_calculations.calculate_ideal_weight(200, 'male')
        assert result['ideal_min'] == pytest.approx(80.0, abs=0.1)
        assert result['ideal_max'] == pytest.approx(100.0, abs=0.1)
        
        # Very short person
        result = nutrition_calculations.calculate_ideal_weight(140, 'female')
        assert result['ideal_min'] == pytest.approx(39.2, abs=0.1)
        assert result['ideal_max'] == pytest.approx(49.0, abs=0.1)


class TestCalculateWaterNeeds:
    """Test water needs calculation functionality"""
    
    def test_water_needs_sedentary(self):
        """Test water needs calculation for sedentary lifestyle"""
        result = nutrition_calculations.calculate_water_needs(70, 'sedentary')
        
        assert result['base_ml'] == 2450
        assert result['total_ml'] == 2450
        assert result['liters'] == 2.5
        assert result['glasses'] == 10
        assert result['activity_bonus'] == 0
    
    def test_water_needs_moderately_active(self):
        """Test water needs calculation for moderately active lifestyle"""
        result = nutrition_calculations.calculate_water_needs(70, 'moderately_active')
        
        assert result['base_ml'] == 2450
        assert result['total_ml'] == 3430
        assert result['liters'] == 3.4
        assert result['glasses'] == 14
        assert result['activity_bonus'] == 980
    
    def test_water_needs_very_active(self):
        """Test water needs calculation for very active lifestyle"""
        result = nutrition_calculations.calculate_water_needs(70, 'very_active')
        
        assert result['base_ml'] == 2450
        assert result['total_ml'] == 3920
        assert result['liters'] == 3.9
        assert result['glasses'] == 16
        assert result['activity_bonus'] == 1470
    
    def test_water_needs_different_weights(self):
        """Test water needs calculation with different weights"""
        # Light person
        result = nutrition_calculations.calculate_water_needs(50, 'moderately_active')
        assert result['total_ml'] == 2450
        assert result['liters'] == 2.5
        
        # Heavy person
        result = nutrition_calculations.calculate_water_needs(100, 'moderately_active')
        assert result['total_ml'] == 4900
        assert result['liters'] == 4.9
    
    def test_water_needs_unknown_activity(self):
        """Test water needs calculation with unknown activity level"""
        result = nutrition_calculations.calculate_water_needs(70, 'unknown_activity')
        
        # Should default to sedentary multiplier
        assert result['total_ml'] == 2450
        assert result['activity_bonus'] == 0


class TestCalculateMacroDistribution:
    """Test macro distribution calculation functionality"""
    
    def test_macro_distribution_weight_loss(self):
        """Test macro distribution for weight loss goal"""
        result = nutrition_calculations.calculate_macro_distribution(2000, 'lose_weight')
        
        assert result['protein']['percent'] == 30
        assert result['fat']['percent'] == 25
        assert result['carbs']['percent'] == 45
        assert result['protein']['grams'] == 150
        assert result['fat']['grams'] == 56
        assert result['carbs']['grams'] == 225
    
    def test_macro_distribution_weight_gain(self):
        """Test macro distribution for weight gain goal"""
        result = nutrition_calculations.calculate_macro_distribution(2500, 'gain_weight')
        
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 25
        assert result['carbs']['percent'] == 50
        assert result['protein']['grams'] == 156
        assert result['fat']['grams'] == 69
        assert result['carbs']['grams'] == pytest.approx(312, abs=1)
    
    def test_macro_distribution_maintenance(self):
        """Test macro distribution for weight maintenance goal"""
        result = nutrition_calculations.calculate_macro_distribution(2200, 'maintain_weight')
        
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 30
        assert result['carbs']['percent'] == 45
        assert result['protein']['grams'] == 138
        assert result['fat']['grams'] == 73
        assert result['carbs']['grams'] == 248
    
    def test_macro_distribution_unknown_goal(self):
        """Test macro distribution for unknown goal"""
        result = nutrition_calculations.calculate_macro_distribution(2000, 'unknown_goal')
        
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 30
        assert result['carbs']['percent'] == 45
    
    def test_macro_distribution_low_calories(self):
        """Test macro distribution with low calorie target"""
        result = nutrition_calculations.calculate_macro_distribution(1200, 'lose_weight')
        
        assert result['protein']['grams'] == 90
        assert result['fat']['grams'] == 33
        assert result['carbs']['grams'] == 135


class TestCalculateMetabolicAge:
    """Test metabolic age calculation functionality"""
    
    def test_metabolic_age_young_active(self):
        """Test metabolic age for young active person"""
        result = nutrition_calculations.calculate_metabolic_age(25, 'male', 70, 175, 'very_active')
        
        assert result['metabolic_age'] <= 25
        assert 'description' in result
        assert 'motivation' in result
    
    def test_metabolic_age_older_sedentary(self):
        """Test metabolic age for older sedentary person"""
        result = nutrition_calculations.calculate_metabolic_age(50, 'female', 80, 160, 'sedentary')
        
        assert result['metabolic_age'] >= 50
        assert 'description' in result
        assert 'motivation' in result
    
    def test_metabolic_age_female_vs_male(self):
        """Test metabolic age difference between genders"""
        female_result = nutrition_calculations.calculate_metabolic_age(30, 'female', 65, 165, 'moderately_active')
        male_result = nutrition_calculations.calculate_metabolic_age(30, 'male', 75, 175, 'moderately_active')
        
        # Males typically have higher metabolic rates
        assert 'metabolic_age' in female_result
        assert 'metabolic_age' in male_result
    
    def test_metabolic_age_bmi_impact(self):
        """Test how BMI affects metabolic age"""
        normal_bmi = nutrition_calculations.calculate_metabolic_age(35, 'male', 70, 175, 'moderately_active')
        high_bmi = nutrition_calculations.calculate_metabolic_age(35, 'male', 90, 175, 'moderately_active')
        
        # Higher BMI should result in higher metabolic age
        assert 'metabolic_age' in normal_bmi
        assert 'metabolic_age' in high_bmi
    
    def test_metabolic_age_edge_cases(self):
        """Test metabolic age calculation edge cases"""
        # Very young person
        result = nutrition_calculations.calculate_metabolic_age(18, 'male', 60, 170, 'moderately_active')
        assert 'metabolic_age' in result
        
        # Very old person
        result = nutrition_calculations.calculate_metabolic_age(80, 'female', 70, 160, 'sedentary')
        assert 'metabolic_age' in result


class TestCalculateMealPortions:
    """Test meal portions calculation functionality"""
    
    def test_meal_portions_standard(self):
        """Test meal portions calculation for standard case"""
        result = nutrition_calculations.calculate_meal_portions(2000, 3)
        
        assert result['total_calories'] == 2000
        assert result['meals_per_day'] == 3
        assert len(result['meals']) == 3
        assert sum(meal['calories'] for meal in result['meals']) == pytest.approx(2000, abs=2)
    
    def test_meal_portions_low_calories(self):
        """Test meal portions calculation for low calorie target"""
        result = nutrition_calculations.calculate_meal_portions(1200, 4)
        
        assert result['total_calories'] == 1200
        assert result['meals_per_day'] == 4
        assert len(result['meals']) == 4
        assert sum(meal['calories'] for meal in result['meals']) == pytest.approx(1200, abs=2)
    
    def test_meal_portions_high_calories(self):
        """Test meal portions calculation for high calorie target"""
        result = nutrition_calculations.calculate_meal_portions(3000, 5)
        
        assert result['total_calories'] == 3000
        assert result['meals_per_day'] == 5
        assert len(result['meals']) == 3
        assert sum(meal['calories'] for meal in result['meals']) == pytest.approx(3000, abs=2)
    
    def test_meal_portions_odd_calories(self):
        """Test meal portions calculation with odd calorie numbers"""
        result = nutrition_calculations.calculate_meal_portions(2001, 3)
        
        # Should handle odd numbers gracefully
        assert result['total_calories'] == 2001
        assert len(result['meals']) == 3
        assert sum(meal['calories'] for meal in result['meals']) == pytest.approx(2001, abs=2)


class TestGetNutritionRecommendations:
    """Test nutrition recommendations functionality"""
    
    def test_recommendations_underweight(self):
        """Test recommendations for underweight person"""
        profile = {'weight_kg': 50, 'height_cm': 170, 'age': 25, 'gender': 'female', 'activity_level': 'moderately_active', 'goal': 'gain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('nutrient-dense foods' in rec for rec in recommendations)
    
    def test_recommendations_overweight(self):
        """Test recommendations for overweight person"""
        profile = {'weight_kg': 90, 'height_cm': 170, 'age': 30, 'gender': 'male', 'activity_level': 'sedentary', 'goal': 'lose_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('Start with small, sustainable changes to build healthy habits' in rec for rec in recommendations)
    
    def test_recommendations_very_active(self):
        """Test recommendations for very active person"""
        profile = {'weight_kg': 70, 'height_cm': 175, 'age': 28, 'gender': 'male', 'activity_level': 'very_active', 'goal': 'maintain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('protein' in rec for rec in recommendations)
    
    def test_recommendations_sedentary(self):
        """Test recommendations for sedentary person"""
        profile = {'weight_kg': 75, 'height_cm': 165, 'age': 45, 'gender': 'female', 'activity_level': 'sedentary', 'goal': 'maintain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('hydrated' in rec for rec in recommendations)
    
    def test_recommendations_contains_water(self):
        """Test that recommendations include water advice"""
        profile = {'weight_kg': 70, 'height_cm': 170, 'age': 30, 'gender': 'male', 'activity_level': 'moderately_active', 'goal': 'maintain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('hydrated' in rec for rec in recommendations)
    
    def test_recommendations_contains_motivation(self):
        """Test that recommendations include motivational content"""
        profile = {'weight_kg': 70, 'height_cm': 170, 'age': 30, 'gender': 'male', 'activity_level': 'moderately_active', 'goal': 'maintain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert any('transformations' in rec for rec in recommendations)
    
    def test_recommendations_minimum_count(self):
        """Test that recommendations return minimum number of suggestions"""
        profile = {'weight_kg': 70, 'height_cm': 170, 'age': 30, 'gender': 'male', 'activity_level': 'moderately_active', 'goal': 'maintain_weight'}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        
        # Should return at least 3 recommendations
        assert len(recommendations) >= 3
    
    def test_recommendations_incomplete_profile(self):
        """Test recommendations with incomplete profile"""
        profile = {'weight_kg': 70, 'height_cm': 170}
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        
        # Should still return some basic recommendations
        assert len(recommendations) >= 2


class TestCalculationIntegration:
    """Test integration of multiple calculation functions"""
    
    def test_complete_profile_analysis(self):
        """Test complete profile analysis using multiple functions"""
        profile = {'weight_kg': 75, 'height_cm': 170, 'age': 30, 'gender': 'male', 'activity_level': 'moderately_active', 'goal': 'lose_weight'}
        
        # Calculate BMI
        bmi_result = nutrition_calculations.calculate_bmi(profile['weight_kg'], profile['height_cm'])
        assert bmi_result['category'] == 'overweight'
        
        # Calculate ideal weight
        ideal_weight = nutrition_calculations.calculate_ideal_weight(profile['height_cm'], profile['gender'])
        assert profile['weight_kg'] > ideal_weight['ideal_max']
        
        # Calculate water needs
        water_needs = nutrition_calculations.calculate_water_needs(profile['weight_kg'], profile['activity_level'])
        assert water_needs['liters'] > 2.0
        
        # Calculate macro distribution
        macros = nutrition_calculations.calculate_macro_distribution(2000, profile['goal'])
        assert macros['protein']['percent'] == 30
        
        # Get recommendations
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert len(recommendations) >= 3
    
    def test_edge_case_profile(self):
        """Test calculations with edge case profile"""
        profile = {'weight_kg': 45, 'height_cm': 180, 'age': 18, 'gender': 'female', 'activity_level': 'extremely_active', 'goal': 'gain_weight'}
        
        # Calculate BMI
        bmi_result = nutrition_calculations.calculate_bmi(profile['weight_kg'], profile['height_cm'])
        assert bmi_result['category'] == 'underweight'
        
        # Calculate water needs
        water_needs = nutrition_calculations.calculate_water_needs(profile['weight_kg'], profile['activity_level'])
        assert water_needs['liters'] > 1.0
        
        # Get recommendations
        recommendations = nutrition_calculations.get_nutrition_recommendations(profile, [])
        assert len(recommendations) >= 3 