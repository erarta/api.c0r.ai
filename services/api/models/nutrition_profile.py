"""
Enhanced nutrition profile models with psychological insights and temporal patterns.
"""
from __future__ import annotations

from datetime import datetime, time, date
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class EatingPersonality(str, Enum):
    """User eating personality archetypes"""
    EARLY_BIRD_PLANNER = "early_bird_planner"
    LATE_STARTER_IMPULSIVE = "late_starter_impulsive"
    STRUCTURED_BALANCED = "structured_balanced"
    STRESS_DRIVEN = "stress_driven"
    SOCIAL_EATER = "social_eater"
    INTUITIVE_GRAZER = "intuitive_grazer"
    BUSY_PROFESSIONAL = "busy_professional"
    WEEKEND_WARRIOR = "weekend_warrior"


class EnergyPattern(BaseModel):
    """User's energy and appetite patterns throughout the day"""
    morning_appetite: float = Field(ge=0, le=1, description="Morning appetite level 0-1")
    afternoon_hunger: float = Field(ge=0, le=1, description="Afternoon hunger level 0-1")
    evening_comfort_eating: float = Field(ge=0, le=1, description="Evening comfort eating tendency 0-1")
    peak_hunger_time: time = Field(description="Time of day with peak hunger")
    lowest_energy_time: time = Field(description="Time of day with lowest energy")


class SocialEatingPattern(BaseModel):
    """Social and contextual eating behaviors"""
    weekend_indulgence_score: float = Field(ge=0, le=1, description="Weekend vs weekday eating difference")
    work_stress_snacking: float = Field(ge=0, le=1, description="Stress-induced snacking frequency")
    restaurant_frequency: float = Field(ge=0, le=1, description="How often eats out vs home cooking")
    social_meal_impact: float = Field(ge=0, le=1, description="How much social situations affect eating")
    planning_score: float = Field(ge=0, le=1, description="How well user plans meals")


class TemporalPattern(BaseModel):
    """Time-based eating patterns and insights"""
    preferred_breakfast_time: time = Field(description="Usual breakfast time")
    preferred_lunch_time: time = Field(description="Usual lunch time")
    preferred_dinner_time: time = Field(description="Usual dinner time")
    meal_timing_consistency: float = Field(ge=0, le=1, description="How consistent meal times are")
    weekend_shift_hours: float = Field(description="How much meal times shift on weekends")
    late_night_eating_frequency: float = Field(ge=0, le=1, description="Frequency of eating after 21:00")


class NutritionTrigger(BaseModel):
    """Behavioral triggers that affect eating patterns"""
    trigger: str = Field(description="The trigger (stress, monday, weekend, etc)")
    food_response: str = Field(description="Typical food response")
    probability: float = Field(ge=0, le=1, description="How often this trigger leads to this response")
    time_of_day: Optional[time] = Field(None, description="When this typically happens")


class SuccessPattern(BaseModel):
    """Patterns that correlate with user's nutrition success"""
    pattern: str = Field(description="The successful pattern")
    outcome: str = Field(description="The positive outcome")
    correlation: float = Field(ge=0, le=1, description="Strength of correlation")


class OptimizationZone(BaseModel):
    """Areas for nutrition optimization"""
    area: str = Field(description="Area to optimize (fiber, sugar, timing, etc)")
    difficulty: Literal["easy_wins", "moderate_effort", "requires_strategy", "long_term_goal"]
    impact: Literal["low", "medium", "high"]
    current_score: float = Field(ge=0, le=1, description="Current performance in this area")
    target_score: float = Field(ge=0, le=1, description="Target performance")


class NutritionDNA(BaseModel):
    """Complete nutritional behavioral profile - like genetic code for eating habits"""
    archetype: EatingPersonality
    confidence_score: float = Field(ge=0, le=1, description="How confident we are in this profile")

    # Behavioral patterns
    energy_patterns: EnergyPattern
    social_patterns: SocialEatingPattern
    temporal_patterns: TemporalPattern

    # Learning and prediction
    triggers: List[NutritionTrigger] = Field(default_factory=list)
    success_patterns: List[SuccessPattern] = Field(default_factory=list)
    optimization_zones: List[OptimizationZone] = Field(default_factory=list)

    # Metrics
    diversity_score: float = Field(ge=0, le=1, description="How diverse the diet is")
    consistency_score: float = Field(ge=0, le=1, description="How consistent eating habits are")
    goal_alignment_score: float = Field(ge=0, le=1, description="How well current eating aligns with goals")

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    data_quality_score: float = Field(ge=0, le=1, description="Quality of data used to generate this profile")


class WeeklyInsight(BaseModel):
    """Weekly nutrition insights and recommendations"""
    week_start: date

    # Day-specific insights
    day_insights: Dict[str, str] = Field(description="Insights for each day of week")

    # Patterns observed
    observed_patterns: List[str] = Field(description="Patterns noticed this week")

    # Micro-recommendations
    micro_goals: List[str] = Field(description="Small, achievable goals for next week")

    # Predictive insights
    risk_days: List[str] = Field(description="Days with higher risk of poor choices")
    opportunity_moments: List[str] = Field(description="Best moments for positive changes")


class PersonalizedFoodRecommendation(BaseModel):
    """AI-generated food recommendation based on user's DNA"""
    food_type: Literal["breakfast", "lunch", "dinner", "snack"]
    recommended_time: time

    # Personalization factors
    matches_energy_level: bool
    addresses_typical_craving: bool
    fits_schedule_pattern: bool
    supports_current_goal: bool

    # Recommendation details
    dish_name: str
    description: str
    reasoning: str = Field(description="Why this meal is recommended for this user")

    # Nutrition
    calories: int
    protein: int
    fats: int
    carbs: int
    fiber: Optional[int] = None

    # Context
    prep_time_minutes: int
    difficulty_level: Literal["easy", "medium", "hard"]
    ingredients: List[Dict[str, Any]]


class EnhancedUserProfile(BaseModel):
    """Extended user profile with psychological and temporal insights"""

    # Basic info (existing)
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    dietary_preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    daily_calories_target: Optional[int] = None
    language: str = "en"

    # Enhanced profile
    nutrition_dna: Optional[NutritionDNA] = None
    last_dna_update: Optional[datetime] = None

    # Analysis history summary
    total_analyses: int = 0
    active_days_14d: int = 0
    last_analysis_date: Optional[date] = None

    # Preferences learned from behavior
    preferred_cuisines: List[str] = Field(default_factory=list)
    disliked_foods: List[str] = Field(default_factory=list)
    typical_portion_sizes: Dict[str, str] = Field(default_factory=dict)  # small/medium/large for different meal types

    # Goals and tracking
    current_phase: Optional[str] = None  # weight_loss, muscle_gain, maintenance
    weekly_targets: Dict[str, float] = Field(default_factory=dict)
    progress_metrics: Dict[str, List[float]] = Field(default_factory=dict)


class FoodAnalysisEnhanced(BaseModel):
    """Enhanced food analysis with context and insights"""

    # Basic analysis (existing)
    timestamp: datetime
    calories: int
    protein: int
    fats: int
    carbs: int
    fiber: Optional[int] = None

    # Enhanced context
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None
    context: Optional[str] = None  # home, restaurant, work, travel
    mood_before: Optional[str] = None  # hungry, stressed, happy, bored
    mood_after: Optional[str] = None
    satisfaction_level: Optional[int] = Field(None, ge=1, le=5)

    # Behavioral insights
    aligned_with_goal: bool = False
    matched_typical_pattern: bool = False
    was_planned: bool = False
    social_context: bool = False  # eaten with others

    # Recommendations generated
    immediate_feedback: Optional[str] = None
    next_meal_suggestion: Optional[str] = None

    # Quality score
    nutrition_quality_score: float = Field(ge=0, le=1)
    timing_appropriateness: float = Field(ge=0, le=1)