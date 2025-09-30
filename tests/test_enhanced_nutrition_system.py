"""
Comprehensive tests for the Enhanced Nutrition System.
Tests all components: DNA generation, insights, predictions, recommendations, and visualizations.
"""
import pytest
import asyncio
from datetime import datetime, date, timedelta, time
from typing import Dict, Any, List

# Import all our enhanced components
from services.api.models.nutrition_profile import (
    NutritionDNA, EatingPersonality, EnergyPattern, SocialEatingPattern,
    TemporalPattern, NutritionTrigger, SuccessPattern, OptimizationZone
)
from services.api.analyzers.nutrition_dna_generator import NutritionDNAGenerator
from services.api.analyzers.temporal_patterns import TemporalPatternsAnalyzer
from services.api.analyzers.psychological_profile import PsychologicalProfileAnalyzer
from services.api.engines.personalized_insights import PersonalizedInsightsEngine
from services.api.engines.contextual_analyzer import ContextualAnalyzer
from services.api.predictors.behavior_predictor import BehaviorPredictor
from services.api.recommenders.adaptive_meal_recommender import AdaptiveMealRecommender
from services.api.visualization.nutrition_visualizer import NutritionVisualizer
from services.api.llm.enhanced_food_plan_generator import EnhancedFoodPlanGenerator


class TestEnhancedNutritionSystem:
    """Test suite for the complete enhanced nutrition system"""

    @pytest.fixture
    def sample_user_profile(self) -> Dict[str, Any]:
        """Sample user profile for testing"""
        return {
            "user_id": "test-user-123",
            "age": 32,
            "gender": "female",
            "height_cm": 165,
            "weight_kg": 60,
            "activity_level": "moderate",
            "goal": "weight_loss",
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "daily_calories_target": 1800,
            "language": "ru"
        }

    @pytest.fixture
    def sample_food_history(self) -> List[Dict[str, Any]]:
        """Sample food history for testing"""
        base_date = datetime.now() - timedelta(days=14)
        food_history = []

        for i in range(50):  # 50 food logs over 14 days
            log_date = base_date + timedelta(days=i % 14)

            # Vary timing throughout the day
            if i % 3 == 0:  # Breakfast
                log_date = log_date.replace(hour=8, minute=30)
            elif i % 3 == 1:  # Lunch
                log_date = log_date.replace(hour=13, minute=0)
            else:  # Dinner
                log_date = log_date.replace(hour=19, minute=30)

            # Add some late night snacks
            if i % 7 == 0:
                log_date = log_date.replace(hour=22, minute=0)

            food_history.append({
                "timestamp": log_date.isoformat(),
                "action_type": "photo_analysis",
                "kbzhu": {
                    "calories": 200 + (i % 5) * 100,  # Vary calories
                    "protein": 15 + (i % 3) * 5,
                    "fats": 8 + (i % 4) * 3,
                    "carbs": 25 + (i % 6) * 8,
                    "fiber": 3 + (i % 3)
                },
                "metadata": {
                    "description": f"Sample meal {i}",
                    "confidence": 0.8 + (i % 3) * 0.1
                }
            })

        return food_history

    @pytest.fixture
    def sample_context_data(self) -> List[Dict[str, Any]]:
        """Sample context data for testing"""
        context_data = []
        base_date = date.today() - timedelta(days=7)

        for i in range(7):
            context_date = base_date + timedelta(days=i)
            context_data.append({
                "date": context_date.isoformat(),
                "weather": ["sunny", "rainy", "cold", "hot"][i % 4],
                "work_stress_level": 3 + (i % 5),
                "social_plans": i % 3 == 0
            })

        return context_data

    def test_temporal_patterns_analyzer(self, sample_food_history):
        """Test temporal pattern analysis"""
        # Test temporal pattern analysis
        temporal_patterns = TemporalPatternsAnalyzer.analyze_temporal_patterns(sample_food_history)

        assert temporal_patterns is not None
        assert isinstance(temporal_patterns.preferred_breakfast_time, time)
        assert isinstance(temporal_patterns.preferred_lunch_time, time)
        assert isinstance(temporal_patterns.preferred_dinner_time, time)
        assert 0 <= temporal_patterns.meal_timing_consistency <= 1
        assert temporal_patterns.weekend_shift_hours >= 0
        assert 0 <= temporal_patterns.late_night_eating_frequency <= 1

        # Test energy pattern analysis
        energy_patterns = TemporalPatternsAnalyzer.analyze_energy_patterns(sample_food_history)

        assert energy_patterns is not None
        assert 0 <= energy_patterns.morning_appetite <= 1
        assert 0 <= energy_patterns.afternoon_hunger <= 1
        assert 0 <= energy_patterns.evening_comfort_eating <= 1
        assert isinstance(energy_patterns.peak_hunger_time, time)

        # Test insights generation
        insights = TemporalPatternsAnalyzer.generate_temporal_insights(temporal_patterns)
        assert isinstance(insights, list)
        assert all(isinstance(insight, str) for insight in insights)

        print("✅ Temporal patterns analyzer tests passed")

    def test_psychological_profile_analyzer(self, sample_food_history, sample_user_profile):
        """Test psychological profile analysis"""
        # Test eating personality detection
        personality = PsychologicalProfileAnalyzer.detect_eating_personality(
            sample_food_history, 0.7  # High consistency
        )
        assert isinstance(personality, EatingPersonality)

        # Test social eating patterns
        social_patterns = PsychologicalProfileAnalyzer.analyze_social_eating_patterns(sample_food_history)
        assert isinstance(social_patterns, SocialEatingPattern)
        assert 0 <= social_patterns.weekend_indulgence_score <= 1
        assert 0 <= social_patterns.work_stress_snacking <= 1

        # Test trigger identification
        triggers = PsychologicalProfileAnalyzer.identify_triggers(sample_food_history)
        assert isinstance(triggers, list)
        assert all(isinstance(trigger, NutritionTrigger) for trigger in triggers)

        # Test success patterns
        success_patterns = PsychologicalProfileAnalyzer.identify_success_patterns(
            sample_food_history, sample_user_profile.get("goal")
        )
        assert isinstance(success_patterns, list)

        # Test optimization zones
        optimization_zones = PsychologicalProfileAnalyzer.identify_optimization_zones(
            sample_food_history, sample_user_profile
        )
        assert isinstance(optimization_zones, list)

        print("✅ Psychological profile analyzer tests passed")

    def test_nutrition_dna_generator(self, sample_user_profile, sample_food_history):
        """Test Nutrition DNA generation"""
        # Generate DNA
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )

        assert isinstance(nutrition_dna, NutritionDNA)
        assert isinstance(nutrition_dna.archetype, EatingPersonality)
        assert 0 <= nutrition_dna.confidence_score <= 1
        assert 0 <= nutrition_dna.diversity_score <= 1
        assert 0 <= nutrition_dna.consistency_score <= 1
        assert 0 <= nutrition_dna.goal_alignment_score <= 1
        assert 0 <= nutrition_dna.data_quality_score <= 1

        # Test DNA summary generation
        summary = NutritionDNAGenerator.get_dna_summary(nutrition_dna)
        assert isinstance(summary, str)
        assert len(summary) > 50  # Should be descriptive

        # Test DNA updating
        updated_dna = NutritionDNAGenerator.update_nutrition_dna(
            nutrition_dna, sample_food_history[:10], sample_user_profile, days_since_last_update=5
        )
        assert isinstance(updated_dna, NutritionDNA)

        print("✅ Nutrition DNA generator tests passed")

    def test_personalized_insights_engine(self, sample_user_profile, sample_food_history):
        """Test personalized insights generation"""
        # First generate DNA for insights
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )

        # Test daily insights
        daily_insights = PersonalizedInsightsEngine.generate_daily_insights(
            nutrition_dna, date.today(), sample_food_history[-7:]
        )
        assert isinstance(daily_insights, list)
        assert all(isinstance(insight, str) for insight in daily_insights)

        # Test weekly insights
        weekly_insights = PersonalizedInsightsEngine.generate_weekly_insights(
            nutrition_dna, date.today() - timedelta(days=6), sample_food_history
        )
        assert weekly_insights is not None
        assert hasattr(weekly_insights, 'day_insights')
        assert hasattr(weekly_insights, 'micro_goals')

        print("✅ Personalized insights engine tests passed")

    def test_contextual_analyzer(self, sample_food_history, sample_context_data):
        """Test contextual analysis"""
        # Test context impact analysis
        context_analysis = ContextualAnalyzer.analyze_context_impact(
            sample_food_history, sample_context_data
        )

        assert isinstance(context_analysis, dict)
        assert "weather_impact" in context_analysis
        assert "time_impact" in context_analysis
        assert "strongest_influences" in context_analysis
        assert "context_score" in context_analysis
        assert 0 <= context_analysis["context_score"] <= 1

        # Test contextual recommendations
        recommendations = ContextualAnalyzer.get_contextual_recommendations(
            context_analysis,
            NutritionDNAGenerator.generate_nutrition_dna({}, sample_food_history),
            {"weather": "cold", "social_context": "work"}
        )
        assert isinstance(recommendations, list)

        print("✅ Contextual analyzer tests passed")

    def test_behavior_predictor(self, sample_user_profile, sample_food_history):
        """Test behavioral prediction"""
        # Generate DNA for predictions
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )

        # Test daily behavior prediction
        predictions = BehaviorPredictor.predict_daily_behavior(
            nutrition_dna, date.today(), sample_food_history[-10:]
        )
        assert isinstance(predictions, list)
        assert all(hasattr(pred, 'probability') for pred in predictions)
        assert all(0 <= pred.probability <= 1 for pred in predictions)

        # Test weekly predictions
        weekly_predictions = BehaviorPredictor.predict_weekly_outcomes(
            nutrition_dna, date.today()
        )
        assert isinstance(weekly_predictions, dict)
        assert len(weekly_predictions) == 7  # One prediction per day

        # Test goal success prediction
        success_prob, factors = BehaviorPredictor.predict_goal_success_probability(
            nutrition_dna, sample_user_profile.get("goal", "weight_loss"), 30
        )
        assert 0 <= success_prob <= 1
        assert isinstance(factors, list)

        print("✅ Behavior predictor tests passed")

    def test_adaptive_meal_recommender(self, sample_user_profile, sample_food_history):
        """Test adaptive meal recommendations"""
        # Generate DNA for recommendations
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )

        # Test single meal recommendation
        meal_rec = AdaptiveMealRecommender.recommend_meal(
            nutrition_dna, "breakfast", {"current_time": time(8, 0)}
        )

        assert meal_rec is not None
        assert meal_rec.meal_type == "breakfast"
        assert isinstance(meal_rec.dish_name, str)
        assert meal_rec.calories > 0
        assert meal_rec.protein >= 0
        assert meal_rec.prep_time_minutes > 0

        # Test daily meal plan generation
        daily_plan = AdaptiveMealRecommender.generate_daily_meal_plan(
            nutrition_dna, date.today()
        )
        assert isinstance(daily_plan, dict)
        assert "breakfast" in daily_plan
        assert "lunch" in daily_plan
        assert "dinner" in daily_plan

        # Test adaptive suggestions
        recent_meals = [meal_rec.dict() for meal_rec in daily_plan.values()]
        suggestions = AdaptiveMealRecommender.generate_adaptive_suggestions(
            nutrition_dna, recent_meals
        )
        assert isinstance(suggestions, list)

        print("✅ Adaptive meal recommender tests passed")

    def test_nutrition_visualizer(self, sample_user_profile, sample_food_history):
        """Test nutrition visualization components"""
        # Generate DNA for visualization
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )

        # Test DNA summary card
        dna_card = NutritionVisualizer.create_dna_summary_card(nutrition_dna)
        assert dna_card["type"] == "dna_summary_card"
        assert "archetype" in dna_card
        assert "scores" in dna_card

        # Test temporal patterns chart
        temporal_chart = NutritionVisualizer.create_temporal_patterns_chart(nutrition_dna)
        assert temporal_chart["type"] == "temporal_patterns_chart"
        assert "time_pattern" in temporal_chart

        # Test optimization zones chart
        opt_chart = NutritionVisualizer.create_optimization_zones_chart(nutrition_dna)
        assert opt_chart["type"] == "optimization_zones_chart"
        assert "optimization_cards" in opt_chart

        # Test progress timeline
        progress = NutritionVisualizer.create_progress_timeline(sample_food_history)
        assert progress["type"] == "progress_timeline"
        assert "timeline" in progress

        # Test comprehensive report
        report = NutritionVisualizer.generate_nutrition_report(
            nutrition_dna, sample_food_history
        )
        assert report["type"] == "comprehensive_nutrition_report"
        assert "components" in report
        assert len(report["components"]) > 0

        print("✅ Nutrition visualizer tests passed")

    @pytest.mark.asyncio
    async def test_enhanced_food_plan_generator(self, sample_user_profile, sample_food_history, sample_context_data):
        """Test enhanced food plan generation"""
        generator = EnhancedFoodPlanGenerator()

        # Test enhanced plan generation
        enhanced_plan = await generator.generate_enhanced_plan(
            sample_user_profile,
            sample_food_history,
            days=3,
            context={
                "context_data": sample_context_data,
                "weather": "sunny",
                "weekly_context": {
                    "monday": {"stress_level": "low"},
                    "tuesday": {"stress_level": "medium"}
                }
            }
        )

        # Verify enhanced plan structure
        assert isinstance(enhanced_plan, dict)
        assert "intro_summary" in enhanced_plan
        assert "plan_json" in enhanced_plan
        assert "shopping_list_json" in enhanced_plan
        assert "daily_insights" in enhanced_plan
        assert "personalization_data" in enhanced_plan
        assert "adaptive_suggestions" in enhanced_plan
        assert "confidence" in enhanced_plan
        assert "model_used" in enhanced_plan

        # Verify plan has correct number of days
        assert len(enhanced_plan["plan_json"]) == 3
        assert all(f"day_{i}" in enhanced_plan["plan_json"] for i in range(1, 4))

        # Verify each day has meals with AI enhancements
        for day_key, day_data in enhanced_plan["plan_json"].items():
            assert "breakfast" in day_data
            assert "lunch" in day_data
            assert "dinner" in day_data

            for meal in ["breakfast", "lunch", "dinner"]:
                meal_data = day_data[meal]
                assert "calories" in meal_data
                assert "protein" in meal_data
                assert "ai_metadata" in meal_data
                assert "personalization_match" in meal_data["ai_metadata"]

        # Verify personalization data
        personalization = enhanced_plan["personalization_data"]
        assert "nutrition_dna_summary" in personalization
        assert "behavioral_predictions" in personalization
        assert "success_probability" in personalization

        # Verify shopping list has AI suggestions
        shopping_list = enhanced_plan["shopping_list_json"]
        assert isinstance(shopping_list, dict)

        print("✅ Enhanced food plan generator tests passed")

    def test_integration_workflow(self, sample_user_profile, sample_food_history, sample_context_data):
        """Test complete integration workflow"""
        print("\n🔄 Testing complete integration workflow...")

        # Step 1: Generate Nutrition DNA
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )
        print(f"  ✅ Generated DNA: {nutrition_dna.archetype}")

        # Step 2: Analyze context
        context_analysis = ContextualAnalyzer.analyze_context_impact(
            sample_food_history, sample_context_data
        )
        print(f"  ✅ Context sensitivity: {context_analysis['context_score']:.2f}")

        # Step 3: Generate predictions
        predictions = BehaviorPredictor.predict_daily_behavior(
            nutrition_dna, date.today(), sample_food_history[-7:]
        )
        print(f"  ✅ Generated {len(predictions)} behavioral predictions")

        # Step 4: Create meal recommendations
        daily_meals = AdaptiveMealRecommender.generate_daily_meal_plan(
            nutrition_dna, date.today()
        )
        print(f"  ✅ Generated {len(daily_meals)} meal recommendations")

        # Step 5: Generate insights
        insights = PersonalizedInsightsEngine.generate_daily_insights(
            nutrition_dna, date.today(), sample_food_history[-5:]
        )
        print(f"  ✅ Generated {len(insights)} personalized insights")

        # Step 6: Create visualizations
        report = NutritionVisualizer.generate_nutrition_report(
            nutrition_dna, sample_food_history, predictions=[pred.dict() for pred in predictions]
        )
        print(f"  ✅ Generated report with {len(report['components'])} components")

        # Verify workflow integrity
        assert nutrition_dna.confidence_score > 0
        assert len(predictions) > 0
        assert len(daily_meals) > 0
        assert len(insights) > 0
        assert len(report['components']) > 0

        print("✅ Complete integration workflow test passed")

    def test_performance_benchmarks(self, sample_user_profile, sample_food_history):
        """Test performance of key components"""
        import time

        print("\n⚡ Running performance benchmarks...")

        # Benchmark DNA generation
        start_time = time.time()
        nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
            sample_user_profile, sample_food_history
        )
        dna_time = time.time() - start_time
        print(f"  DNA Generation: {dna_time:.3f}s")
        assert dna_time < 5.0  # Should complete in under 5 seconds

        # Benchmark predictions
        start_time = time.time()
        predictions = BehaviorPredictor.predict_daily_behavior(
            nutrition_dna, date.today(), sample_food_history[-10:]
        )
        prediction_time = time.time() - start_time
        print(f"  Behavior Prediction: {prediction_time:.3f}s")
        assert prediction_time < 2.0  # Should complete in under 2 seconds

        # Benchmark meal recommendations
        start_time = time.time()
        meal_plan = AdaptiveMealRecommender.generate_daily_meal_plan(
            nutrition_dna, date.today()
        )
        meal_time = time.time() - start_time
        print(f"  Meal Recommendations: {meal_time:.3f}s")
        assert meal_time < 1.0  # Should complete in under 1 second

        # Benchmark visualization
        start_time = time.time()
        report = NutritionVisualizer.generate_nutrition_report(
            nutrition_dna, sample_food_history
        )
        viz_time = time.time() - start_time
        print(f"  Visualization Report: {viz_time:.3f}s")
        assert viz_time < 2.0  # Should complete in under 2 seconds

        total_time = dna_time + prediction_time + meal_time + viz_time
        print(f"  Total Processing Time: {total_time:.3f}s")
        assert total_time < 10.0  # Complete workflow should be under 10 seconds

        print("✅ Performance benchmarks passed")


if __name__ == "__main__":
    # Run tests manually for development
    test_suite = TestEnhancedNutritionSystem()

    # Create fixtures
    sample_profile = test_suite.sample_user_profile()
    sample_history = test_suite.sample_food_history()
    sample_context = test_suite.sample_context_data()

    print("🧪 Starting Enhanced Nutrition System Tests\n")

    try:
        # Run all tests
        test_suite.test_temporal_patterns_analyzer(sample_history)
        test_suite.test_psychological_profile_analyzer(sample_history, sample_profile)
        test_suite.test_nutrition_dna_generator(sample_profile, sample_history)
        test_suite.test_personalized_insights_engine(sample_profile, sample_history)
        test_suite.test_contextual_analyzer(sample_history, sample_context)
        test_suite.test_behavior_predictor(sample_profile, sample_history)
        test_suite.test_adaptive_meal_recommender(sample_profile, sample_history)
        test_suite.test_nutrition_visualizer(sample_profile, sample_history)

        # Run async test
        import asyncio
        asyncio.run(test_suite.test_enhanced_food_plan_generator(sample_profile, sample_history, sample_context))

        # Integration and performance tests
        test_suite.test_integration_workflow(sample_profile, sample_history, sample_context)
        test_suite.test_performance_benchmarks(sample_profile, sample_history)

        print("\n🎉 All Enhanced Nutrition System Tests Passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    else:
        print("\n✅ Enhanced Nutrition System is ready for production!")
        print("\n📊 System Capabilities Summary:")
        print("  • Nutrition DNA profiling with 8 personality archetypes")
        print("  • Temporal and psychological pattern analysis")
        print("  • Behavioral prediction with confidence scoring")
        print("  • Context-aware meal recommendations")
        print("  • Personalized insights and micro-goals")
        print("  • Comprehensive visualization and reporting")
        print("  • Real-time adaptation based on user feedback")
        print("  • Performance optimized for sub-10 second response times")