#!/usr/bin/env python3
"""
Unit tests for nutrition_calculations.py - nutrition calculation engine
"""

import pytest
import sys
import os
import math

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from nutrition_calculations import (
    calculate_bmi,
    calculate_ideal_weight,
    calculate_water_needs,
    calculate_macro_distribution,
    calculate_metabolic_age,
    calculate_meal_portions,
    get_nutrition_recommendations
)

class TestCalculateBMI:
    """Test suite for BMI calculation"""
    
    def test_bmi_underweight(self):
        """Test BMI calculation for underweight category"""
        result = calculate_bmi(45, 170)
        
        assert result['bmi'] == 15.6
        assert result['category'] == 'underweight'
        assert result['emoji'] == '⬇️'
        assert 'Below ideal range' in result['description']
        assert "Let's focus on healthy weight gain together!" in result['motivation']
    
    def test_bmi_normal_weight(self):
        """Test BMI calculation for normal weight category"""
        result = calculate_bmi(70, 170)
        
        assert result['bmi'] == 24.2
        assert result['category'] == 'normal'
        assert result['emoji'] == '✅'
        assert 'Healthy weight range' in result['description']
        assert 'Fantastic!' in result['motivation']
    
    def test_bmi_overweight(self):
        """Test BMI calculation for overweight category"""
        result = calculate_bmi(85, 170)
        
        assert result['bmi'] == 29.4
        assert result['category'] == 'overweight'
        assert result['emoji'] == '⬆️'
        assert 'Above ideal range' in result['description']
        assert "You're taking the right steps by tracking!" in result['motivation']
    
    def test_bmi_obese(self):
        """Test BMI calculation for obese category"""
        result = calculate_bmi(100, 170)
        
        assert result['bmi'] == 34.6
        assert result['category'] == 'obese'
        assert result['emoji'] == '⚠️'
        assert 'Well above ideal range' in result['description']
        assert "Every healthy choice counts!" in result['motivation']
    
    def test_bmi_edge_cases(self):
        """Test BMI calculation edge cases"""
        # Exactly at boundaries
        result_18_5 = calculate_bmi(53.465, 170)  # BMI exactly 18.5
        assert result_18_5['category'] == 'normal'
        
        result_25 = calculate_bmi(72.25, 170)  # BMI exactly 25
        assert result_25['category'] == 'overweight'
        
        result_30 = calculate_bmi(86.7, 170)  # BMI exactly 30
        assert result_30['category'] == 'obese'
    
    def test_bmi_different_heights(self):
        """Test BMI calculation with different heights"""
        # Same weight, different heights
        result_short = calculate_bmi(70, 160)
        result_tall = calculate_bmi(70, 180)
        
        assert result_short['bmi'] > result_tall['bmi']
        assert result_short['bmi'] == 27.3
        assert result_tall['bmi'] == 21.6


class TestCalculateIdealWeight:
    """Test suite for ideal weight calculation"""
    
    def test_ideal_weight_male(self):
        """Test ideal weight calculation for male"""
        result = calculate_ideal_weight(170, 'male')
        
        assert result['ideal_min'] == 57.8
        assert result['ideal_max'] == 72.2
        assert result['broca'] == 65.0
        assert result['range'] == "57.8-72.2 kg"
    
    def test_ideal_weight_female(self):
        """Test ideal weight calculation for female"""
        result = calculate_ideal_weight(165, 'female')
        
        assert result['ideal_min'] == 54.4
        assert result['ideal_max'] == 68.1
        assert result['broca'] == 59.0
        assert result['range'] == "54.4-68.1 kg"
    
    def test_ideal_weight_different_heights(self):
        """Test ideal weight calculation with different heights"""
        result_160 = calculate_ideal_weight(160, 'male')
        result_180 = calculate_ideal_weight(180, 'male')
        
        assert result_160['ideal_min'] < result_180['ideal_min']
        assert result_160['ideal_max'] < result_180['ideal_max']
        assert result_160['broca'] < result_180['broca']
    
    def test_ideal_weight_edge_cases(self):
        """Test ideal weight calculation edge cases"""
        # Very short height
        result_short = calculate_ideal_weight(150, 'female')
        assert result_short['ideal_min'] == 45.0
        assert result_short['ideal_max'] == 56.2
        assert result_short['broca'] == 50.0
        
        # Very tall height
        result_tall = calculate_ideal_weight(200, 'male')
        assert result_tall['ideal_min'] == 80.0
        assert result_tall['ideal_max'] == 100.0
        assert result_tall['broca'] == 87.5


class TestCalculateWaterNeeds:
    """Test suite for water needs calculation"""
    
    def test_water_needs_sedentary(self):
        """Test water needs for sedentary activity"""
        result = calculate_water_needs(70, 'sedentary')
        
        assert result['base_ml'] == 2450
        assert result['activity_bonus'] == 0
        assert result['total_ml'] == 2450
        assert result['liters'] == 2.5
        assert result['glasses'] == 10
    
    def test_water_needs_moderately_active(self):
        """Test water needs for moderately active"""
        result = calculate_water_needs(70, 'moderately_active')
        
        assert result['base_ml'] == 2450
        assert result['activity_bonus'] == 980
        assert result['total_ml'] == 3430
        assert result['liters'] == 3.4
        assert result['glasses'] == 14
    
    def test_water_needs_very_active(self):
        """Test water needs for very active"""
        result = calculate_water_needs(70, 'very_active')
        
        assert result['base_ml'] == 2450
        assert result['activity_bonus'] == 1470
        assert result['total_ml'] == 3920
        assert result['liters'] == 3.9
        assert result['glasses'] == 16
    
    def test_water_needs_different_weights(self):
        """Test water needs with different weights"""
        result_50kg = calculate_water_needs(50, 'sedentary')
        result_100kg = calculate_water_needs(100, 'sedentary')
        
        assert result_50kg['base_ml'] == 1750
        assert result_100kg['base_ml'] == 3500
        assert result_50kg['total_ml'] < result_100kg['total_ml']
    
    def test_water_needs_unknown_activity(self):
        """Test water needs with unknown activity level"""
        result = calculate_water_needs(70, 'unknown_activity')
        
        # Should default to sedentary
        assert result['activity_bonus'] == 0
        assert result['total_ml'] == 2450


class TestCalculateMacroDistribution:
    """Test suite for macro distribution calculation"""
    
    def test_macro_distribution_weight_loss(self):
        """Test macro distribution for weight loss"""
        result = calculate_macro_distribution(2000, 'lose_weight')
        
        assert result['protein']['percent'] == 30
        assert result['fat']['percent'] == 25
        assert result['carbs']['percent'] == 45
        assert result['protein']['calories'] == 600
        assert result['fat']['calories'] == 500
        assert result['carbs']['calories'] == 900
        assert result['protein']['grams'] == 150
        assert result['fat']['grams'] == 56
        assert result['carbs']['grams'] == 225
    
    def test_macro_distribution_weight_gain(self):
        """Test macro distribution for weight gain"""
        result = calculate_macro_distribution(2500, 'gain_weight')
        
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 25
        assert result['carbs']['percent'] == 50
        assert result['protein']['calories'] == 625
        assert result['fat']['calories'] == 625
        assert result['carbs']['calories'] == 1250
    
    def test_macro_distribution_maintenance(self):
        """Test macro distribution for maintenance"""
        result = calculate_macro_distribution(2200, 'maintain_weight')
        
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 30
        assert result['carbs']['percent'] == 45
        assert result['protein']['calories'] == 550
        assert result['fat']['calories'] == 660
        assert result['carbs']['calories'] == 990
    
    def test_macro_distribution_unknown_goal(self):
        """Test macro distribution with unknown goal"""
        result = calculate_macro_distribution(2000, 'unknown_goal')
        
        # Should default to maintenance
        assert result['protein']['percent'] == 25
        assert result['fat']['percent'] == 30
        assert result['carbs']['percent'] == 45
    
    def test_macro_distribution_low_calories(self):
        """Test macro distribution with low calories"""
        result = calculate_macro_distribution(1200, 'lose_weight')
        
        assert result['protein']['grams'] == 90
        assert result['fat']['grams'] == 33
        assert result['carbs']['grams'] == 135
        assert result['protein']['calories'] + result['fat']['calories'] + result['carbs']['calories'] == 1200


class TestCalculateMetabolicAge:
    """Test suite for metabolic age calculation"""
    
    def test_metabolic_age_young_active(self):
        """Test metabolic age for young active person"""
        result = calculate_metabolic_age(25, 'male', 70, 175, 'very_active')
        
        assert result['metabolic_age'] <= 25
        assert 'Amazing! Your healthy lifestyle is paying off!' in result['motivation']
        assert 'lifestyle' in result['motivation']
    
    def test_metabolic_age_older_sedentary(self):
        """Test metabolic age for older sedentary person"""
        result = calculate_metabolic_age(45, 'male', 90, 175, 'sedentary')
        
        assert result['metabolic_age'] >= 45
        assert 'No worries! With consistent nutrition and activity' in result['motivation']
        assert 'consistent nutrition and activity' in result['motivation']
    
    def test_metabolic_age_female_vs_male(self):
        """Test metabolic age comparison between genders"""
        result_male = calculate_metabolic_age(30, 'male', 70, 170, 'moderately_active')
        result_female = calculate_metabolic_age(30, 'female', 70, 170, 'moderately_active')
        
        # Both should return valid metabolic ages
        assert result_male['metabolic_age'] >= 18
        assert result_female['metabolic_age'] >= 18
        assert 'motivation' in result_male
        assert 'motivation' in result_female
    
    def test_metabolic_age_bmi_impact(self):
        """Test metabolic age with different BMI values"""
        result_normal = calculate_metabolic_age(30, 'male', 70, 175, 'moderately_active')
        result_obese = calculate_metabolic_age(30, 'male', 100, 175, 'moderately_active')
        
        # Both should return valid metabolic ages
        assert result_normal['metabolic_age'] >= 18
        assert result_obese['metabolic_age'] >= 18
        assert 'motivation' in result_normal
        assert 'motivation' in result_obese
    
    def test_metabolic_age_edge_cases(self):
        """Test metabolic age edge cases"""
        # Very young
        result_young = calculate_metabolic_age(18, 'male', 70, 175, 'very_active')
        assert result_young['metabolic_age'] >= 18
        
        # Very old
        result_old = calculate_metabolic_age(80, 'female', 60, 160, 'sedentary')
        assert result_old['metabolic_age'] >= 80


class TestCalculateMealPortions:
    """Test suite for meal portions calculation"""
    
    def test_meal_portions_standard(self):
        """Test meal portions calculation with standard calories"""
        result = calculate_meal_portions(2000)
        
        assert len(result['meals']) == 3
        assert result['meals'][0]['name'] == 'Breakfast'
        assert result['meals'][0]['calories'] == 500
        assert result['meals'][1]['name'] == 'Lunch'
        assert result['meals'][1]['calories'] == 800
        assert result['meals'][2]['name'] == 'Dinner'
        assert result['meals'][2]['calories'] == 700
        assert result['total_calories'] == 2000
    
    def test_meal_portions_low_calories(self):
        """Test meal portions with low calories"""
        result = calculate_meal_portions(1200)
        
        assert len(result['meals']) == 3
        assert result['meals'][0]['calories'] == 300
        assert result['meals'][1]['calories'] == 480
        assert result['meals'][2]['calories'] == 420
        assert result['total_calories'] == 1200
    
    def test_meal_portions_high_calories(self):
        """Test meal portions with high calories"""
        result = calculate_meal_portions(3000)
        
        assert len(result['meals']) == 3
        assert result['meals'][0]['calories'] == 750
        assert result['meals'][1]['calories'] == 1200
        assert result['meals'][2]['calories'] == 1050
        assert result['total_calories'] == 3000
    
    def test_meal_portions_odd_calories(self):
        """Test meal portions with odd calorie numbers"""
        result = calculate_meal_portions(1999)
        
        # Should handle rounding properly
        total = sum(meal['calories'] for meal in result['meals'])
        assert abs(total - 1999) <= 2  # Allow for rounding differences
        assert result['total_calories'] == 1999


class TestGetNutritionRecommendations:
    """Test suite for nutrition recommendations"""
    
    def test_recommendations_underweight(self):
        """Test recommendations for underweight profile"""
        profile = {
            'weight_kg': 45,
            'height_cm': 170,
            'goal': 'gain_weight',
            'activity_level': 'sedentary'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should contain underweight-specific advice
        underweight_advice = [r for r in recommendations if 'build healthy weight' in r.lower()]
        assert len(underweight_advice) > 0
        
        # Should contain water advice
        water_advice = [r for r in recommendations if 'hydrated' in r.lower()]
        assert len(water_advice) > 0
    
    def test_recommendations_overweight(self):
        """Test recommendations for overweight profile"""
        profile = {
            'weight_kg': 75,
            'height_cm': 170,
            'goal': 'lose_weight',
            'activity_level': 'lightly_active'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        # Should contain overweight-specific advice
        overweight_advice = [r for r in recommendations if 'colorful vegetables' in r.lower() or 'lean proteins' in r.lower() or 'whole grains' in r.lower()]
        assert len(overweight_advice) > 0
        
        # Should contain water advice
        water_advice = [r for r in recommendations if 'hydrated' in r.lower()]
        assert len(water_advice) > 0
    
    def test_recommendations_very_active(self):
        """Test recommendations for very active profile"""
        profile = {
            'weight_kg': 70,
            'height_cm': 175,
            'goal': 'maintain_weight',
            'activity_level': 'very_active'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should contain activity-specific advice
        activity_advice = [r for r in recommendations if 'protein' in r.lower()]
        assert len(activity_advice) > 0
        
        # Should contain water advice
        water_advice = [r for r in recommendations if 'hydrated' in r.lower()]
        assert len(water_advice) > 0
    
    def test_recommendations_sedentary(self):
        """Test recommendations for sedentary profile"""
        profile = {
            'weight_kg': 70,
            'height_cm': 175,
            'goal': 'maintain_weight',
            'activity_level': 'sedentary'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should contain water advice
        water_advice = [r for r in recommendations if 'hydrated' in r.lower()]
        assert len(water_advice) > 0
    
    def test_recommendations_contains_water(self):
        """Test recommendations contain water advice"""
        profile = {
            'weight_kg': 70,
            'height_cm': 175,
            'goal': 'maintain_weight',
            'activity_level': 'moderately_active'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should contain water advice
        water_advice = [r for r in recommendations if 'hydrated' in r.lower()]
        assert len(water_advice) > 0
    
    def test_recommendations_contains_motivation(self):
        """Test recommendations contain motivational messages"""
        profile = {
            'weight_kg': 70,
            'height_cm': 175,
            'goal': 'maintain_weight',
            'activity_level': 'moderately_active'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should contain at least one motivational message
        motivational_advice = [r for r in recommendations if 'transformations' in r.lower()]
        assert len(motivational_advice) > 0
    
    def test_recommendations_minimum_count(self):
        """Test that recommendations return minimum number of items"""
        profile = {
            'weight_kg': 70,
            'height_cm': 175,
            'goal': 'maintain_weight',
            'activity_level': 'moderately_active'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should return at least 4 recommendations
        assert len(recommendations) >= 4
    
    def test_recommendations_incomplete_profile(self):
        """Test recommendations with incomplete profile"""
        profile = {
            'weight_kg': 70,
            'goal': 'maintain_weight'
        }
        
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # Should still return some recommendations
        assert len(recommendations) >= 2
        
        # Should contain at least motivational message
        motivational_advice = [r for r in recommendations if 'transformations' in r.lower()]
        assert len(motivational_advice) > 0


class TestCalculationIntegration:
    """Integration tests for combined calculations"""
    
    def test_complete_profile_analysis(self):
        """Test complete profile analysis with all calculations"""
        profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 70,
            'height_cm': 175,
            'activity_level': 'moderately_active',
            'goal': 'maintain_weight'
        }
        
        # Test all calculations work together
        bmi = calculate_bmi(profile['weight_kg'], profile['height_cm'])
        ideal_weight = calculate_ideal_weight(profile['height_cm'], profile['gender'])
        water_needs = calculate_water_needs(profile['weight_kg'], profile['activity_level'])
        metabolic_age = calculate_metabolic_age(
            profile['age'], profile['gender'], profile['weight_kg'], 
            profile['height_cm'], profile['activity_level']
        )
        macros = calculate_macro_distribution(2200, profile['goal'])
        portions = calculate_meal_portions(2200)
        recommendations = get_nutrition_recommendations(profile, [], 'en')
        
        # All calculations should complete without errors
        assert bmi['bmi'] > 0
        assert ideal_weight['ideal_min'] > 0
        assert water_needs['liters'] > 0
        assert metabolic_age['metabolic_age'] > 0
        assert macros['protein']['grams'] > 0
        assert len(portions['meals']) > 0
        assert len(recommendations) > 0
    
    def test_edge_case_profile(self):
        """Test calculations with edge case profile"""
        profile = {
            'age': 18,
            'gender': 'female',
            'weight_kg': 45,
            'height_cm': 150,
            'activity_level': 'extremely_active',
            'goal': 'gain_weight'
        }
        
        # All calculations should handle edge cases gracefully
        bmi = calculate_bmi(profile['weight_kg'], profile['height_cm'])
        ideal_weight = calculate_ideal_weight(profile['height_cm'], profile['gender'])
        water_needs = calculate_water_needs(profile['weight_kg'], profile['activity_level'])
        metabolic_age = calculate_metabolic_age(
            profile['age'], profile['gender'], profile['weight_kg'], 
            profile['height_cm'], profile['activity_level']
        )
        
        assert bmi['category'] == 'normal'  # 45kg at 150cm = BMI 20, which is normal
        assert ideal_weight['ideal_min'] <= profile['weight_kg']  # Allow equal for edge case
        assert water_needs['liters'] >= 2.0  # Should be substantial for extremely active
        assert metabolic_age['metabolic_age'] >= 18


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 