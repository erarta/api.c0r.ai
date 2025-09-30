-- Enhanced Nutrition System Migration
-- Date: 2025-09-25
-- Description: Adds comprehensive nutrition personalization features including DNA profiling, questionnaire responses, and enhanced user profiles

-- Migration: 2025-09-25_enhanced_nutrition_system.sql
-- Rollback: 2025-09-25_enhanced_nutrition_system_rollback.sql

BEGIN;

-- =============================================
-- 1. EXTEND USER PROFILES WITH ENHANCED NUTRITION FIELDS
-- =============================================

-- Add nutrition onboarding and enhanced preference fields
ALTER TABLE public.user_profiles
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS onboarding_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS favorite_foods TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS disliked_foods TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS preferred_cuisines TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS meal_times JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS cooking_skill TEXT DEFAULT 'intermediate' CHECK (cooking_skill IN ('beginner', 'intermediate', 'advanced')),
ADD COLUMN IF NOT EXISTS cooking_time_available TEXT DEFAULT 'moderate' CHECK (cooking_time_available IN ('quick', 'moderate', 'extended')),
ADD COLUMN IF NOT EXISTS work_schedule TEXT DEFAULT 'office_9_5',
ADD COLUMN IF NOT EXISTS social_eating_frequency TEXT DEFAULT 'sometimes' CHECK (social_eating_frequency IN ('rarely', 'sometimes', 'often', 'very_often')),
ADD COLUMN IF NOT EXISTS health_conditions TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS water_intake_goal INTEGER DEFAULT 8 CHECK (water_intake_goal >= 4 AND water_intake_goal <= 20),
ADD COLUMN IF NOT EXISTS meal_prep_preference TEXT DEFAULT 'some_prep' CHECK (meal_prep_preference IN ('no_prep', 'some_prep', 'full_prep')),
ADD COLUMN IF NOT EXISTS snacking_preference TEXT DEFAULT 'healthy_snacks',
ADD COLUMN IF NOT EXISTS weekend_eating_style TEXT DEFAULT 'relaxed' CHECK (weekend_eating_style IN ('strict', 'relaxed', 'flexible')),
ADD COLUMN IF NOT EXISTS stress_eating_tendency INTEGER DEFAULT 3 CHECK (stress_eating_tendency >= 1 AND stress_eating_tendency <= 5),
ADD COLUMN IF NOT EXISTS primary_motivation TEXT DEFAULT 'health',
ADD COLUMN IF NOT EXISTS weight_goal NUMERIC,
ADD COLUMN IF NOT EXISTS timeline TEXT DEFAULT '3_months',
ADD COLUMN IF NOT EXISTS accountability_preference TEXT DEFAULT 'progress_tracking',
ADD COLUMN IF NOT EXISTS eating_frequency TEXT DEFAULT '3_meals' CHECK (eating_frequency IN ('2_meals', '3_meals', '4_meals', '5_6_small_meals')),
ADD COLUMN IF NOT EXISTS skip_meals TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS supplements TEXT[] DEFAULT '{}';

-- Add indexes for frequently queried fields
CREATE INDEX IF NOT EXISTS idx_user_profiles_onboarding_completed ON public.user_profiles(onboarding_completed);
CREATE INDEX IF NOT EXISTS idx_user_profiles_preferred_cuisines ON public.user_profiles USING GIN(preferred_cuisines);
CREATE INDEX IF NOT EXISTS idx_user_profiles_dietary_preferences ON public.user_profiles USING GIN(dietary_preferences);
CREATE INDEX IF NOT EXISTS idx_user_profiles_allergies ON public.user_profiles USING GIN(allergies);

-- =============================================
-- 2. NUTRITION QUESTIONNAIRE RESPONSES TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS public.nutrition_questionnaire_responses (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    question_id TEXT NOT NULL,
    response_value TEXT NOT NULL,
    response_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT nutrition_questionnaire_responses_pkey PRIMARY KEY (id),
    CONSTRAINT nutrition_questionnaire_responses_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    CONSTRAINT nutrition_questionnaire_responses_unique
        UNIQUE (user_id, question_id)
);

-- Add indexes for questionnaire responses
CREATE INDEX IF NOT EXISTS idx_nutrition_questionnaire_responses_user_id
    ON public.nutrition_questionnaire_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_questionnaire_responses_question_id
    ON public.nutrition_questionnaire_responses(question_id);

-- =============================================
-- 3. NUTRITION DNA PROFILES TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS public.nutrition_dna (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    archetype TEXT NOT NULL CHECK (archetype IN (
        'EARLY_BIRD_PLANNER', 'STRESS_DRIVEN', 'SOCIAL_EATER',
        'BUSY_PROFESSIONAL', 'WEEKEND_WARRIOR', 'INTUITIVE_GRAZER',
        'LATE_STARTER_IMPULSIVE', 'STRUCTURED_BALANCED'
    )),
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),

    -- Energy patterns
    morning_appetite DECIMAL(3,2) DEFAULT 0.5,
    evening_energy DECIMAL(3,2) DEFAULT 0.5,

    -- Temporal patterns
    preferred_breakfast_time TIME DEFAULT '08:00',
    preferred_lunch_time TIME DEFAULT '13:00',
    preferred_dinner_time TIME DEFAULT '19:00',
    weekend_shift_hours INTEGER DEFAULT 0,
    meal_timing_flexibility DECIMAL(3,2) DEFAULT 0.5,

    -- Social patterns
    social_influence_score DECIMAL(3,2) DEFAULT 0.5,
    restaurant_frequency INTEGER DEFAULT 2,
    cooking_for_others_frequency DECIMAL(3,2) DEFAULT 0.3,

    -- Psychological patterns
    stress_eating_score DECIMAL(3,2) DEFAULT 0.5,
    emotional_eating_triggers TEXT[] DEFAULT '{}',
    reward_food_frequency DECIMAL(3,2) DEFAULT 0.3,
    mindful_eating_score DECIMAL(3,2) DEFAULT 0.5,

    -- Optimization zones (areas for improvement)
    optimization_zones JSONB DEFAULT '[]',

    -- Metadata
    generated_from JSONB DEFAULT '{}',
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT nutrition_dna_pkey PRIMARY KEY (id),
    CONSTRAINT nutrition_dna_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    CONSTRAINT nutrition_dna_user_unique UNIQUE (user_id)
);

-- Add indexes for nutrition DNA
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_user_id ON public.nutrition_dna(user_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_archetype ON public.nutrition_dna(archetype);
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_confidence_score ON public.nutrition_dna(confidence_score);

-- =============================================
-- 4. ENHANCED MEAL RECOMMENDATIONS TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS public.meal_recommendations (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    nutrition_dna_id UUID,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    recommended_time TIME NOT NULL,

    -- Personalization match scores
    matches_energy_level BOOLEAN DEFAULT FALSE,
    addresses_typical_craving BOOLEAN DEFAULT FALSE,
    fits_schedule_pattern BOOLEAN DEFAULT FALSE,
    supports_current_goal BOOLEAN DEFAULT FALSE,

    -- Meal details
    dish_name TEXT NOT NULL,
    description TEXT,
    reasoning TEXT,

    -- Nutrition info
    calories INTEGER NOT NULL CHECK (calories > 0),
    protein DECIMAL(5,2) DEFAULT 0,
    fats DECIMAL(5,2) DEFAULT 0,
    carbs DECIMAL(5,2) DEFAULT 0,
    fiber DECIMAL(5,2) DEFAULT 0,

    -- Practical info
    prep_time_minutes INTEGER NOT NULL CHECK (prep_time_minutes > 0),
    difficulty_level TEXT NOT NULL CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    ingredients JSONB DEFAULT '[]',

    -- Context and metadata
    context_data JSONB DEFAULT '{}',
    recommendation_score DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE,
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 5),
    feedback_notes TEXT,

    CONSTRAINT meal_recommendations_pkey PRIMARY KEY (id),
    CONSTRAINT meal_recommendations_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    CONSTRAINT meal_recommendations_nutrition_dna_id_fkey
        FOREIGN KEY (nutrition_dna_id) REFERENCES public.nutrition_dna(id) ON DELETE SET NULL
);

-- Add indexes for meal recommendations
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_user_id ON public.meal_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_nutrition_dna_id ON public.meal_recommendations(nutrition_dna_id);
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_meal_type ON public.meal_recommendations(meal_type);
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_created_at ON public.meal_recommendations(created_at);

-- =============================================
-- 5. USER FOOD ANALYSIS ENHANCED TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS public.user_food_analysis_enhanced (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    original_log_id UUID,

    -- Enhanced analysis data
    temporal_context JSONB DEFAULT '{}', -- time of day, day of week patterns
    psychological_context JSONB DEFAULT '{}', -- stress indicators, mood
    social_context JSONB DEFAULT '{}', -- eating alone/with others, location
    nutritional_analysis JSONB DEFAULT '{}', -- detailed macro/micro breakdown
    behavioral_insights JSONB DEFAULT '{}', -- patterns, triggers, preferences

    -- Analysis metadata
    analysis_version TEXT NOT NULL DEFAULT 'v1.0',
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    processing_time_ms INTEGER,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT user_food_analysis_enhanced_pkey PRIMARY KEY (id),
    CONSTRAINT user_food_analysis_enhanced_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    CONSTRAINT user_food_analysis_enhanced_original_log_id_fkey
        FOREIGN KEY (original_log_id) REFERENCES public.logs(id) ON DELETE SET NULL
);

-- Add indexes for enhanced analysis
CREATE INDEX IF NOT EXISTS idx_user_food_analysis_enhanced_user_id
    ON public.user_food_analysis_enhanced(user_id);
CREATE INDEX IF NOT EXISTS idx_user_food_analysis_enhanced_original_log_id
    ON public.user_food_analysis_enhanced(original_log_id);
CREATE INDEX IF NOT EXISTS idx_user_food_analysis_enhanced_created_at
    ON public.user_food_analysis_enhanced(created_at);

-- =============================================
-- 6. EXTEND MEAL PLANS WITH NUTRITION DNA LINK
-- =============================================

-- Add nutrition DNA reference to existing meal_plans table
ALTER TABLE public.meal_plans
ADD COLUMN IF NOT EXISTS nutrition_dna_id UUID,
ADD COLUMN IF NOT EXISTS personalization_level TEXT DEFAULT 'basic' CHECK (personalization_level IN ('basic', 'enhanced', 'maximum')),
ADD COLUMN IF NOT EXISTS generation_metadata JSONB DEFAULT '{}';

-- Add foreign key constraint (drop if exists first)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'meal_plans_nutrition_dna_id_fkey'
        AND table_name = 'meal_plans'
    ) THEN
        ALTER TABLE public.meal_plans
        ADD CONSTRAINT meal_plans_nutrition_dna_id_fkey
            FOREIGN KEY (nutrition_dna_id) REFERENCES public.nutrition_dna(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Add index for nutrition DNA link
CREATE INDEX IF NOT EXISTS idx_meal_plans_nutrition_dna_id ON public.meal_plans(nutrition_dna_id);

-- =============================================
-- 7. UPDATE FUNCTIONS AND TRIGGERS
-- =============================================

-- Update timestamp trigger for user_profiles (function may already exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to enhanced tables (drop existing triggers first)
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nutrition_questionnaire_responses_updated_at ON public.nutrition_questionnaire_responses;
CREATE TRIGGER update_nutrition_questionnaire_responses_updated_at
    BEFORE UPDATE ON public.nutrition_questionnaire_responses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 8. CREATE HELPFUL VIEWS
-- =============================================

-- View for complete user nutrition profile
CREATE OR REPLACE VIEW public.complete_nutrition_profiles AS
SELECT
    u.id as user_id,
    u.telegram_id,
    up.age,
    up.gender,
    up.height_cm,
    up.weight_kg,
    up.activity_level,
    up.goal,
    up.daily_calories_target,
    up.onboarding_completed,
    up.dietary_preferences,
    up.allergies,
    up.favorite_foods,
    up.preferred_cuisines,
    up.cooking_skill,
    up.social_eating_frequency,
    nd.archetype,
    nd.confidence_score,
    nd.last_updated as dna_last_updated
FROM public.users u
LEFT JOIN public.user_profiles up ON u.id = up.user_id
LEFT JOIN public.nutrition_dna nd ON u.id = nd.user_id;

-- View for recent meal recommendations with feedback
CREATE OR REPLACE VIEW public.recent_meal_recommendations AS
SELECT
    mr.*,
    nd.archetype,
    nd.confidence_score
FROM public.meal_recommendations mr
LEFT JOIN public.nutrition_dna nd ON mr.nutrition_dna_id = nd.id
WHERE mr.created_at >= NOW() - INTERVAL '30 days'
ORDER BY mr.created_at DESC;

-- =============================================
-- 9. INSERT SAMPLE DATA FOR TESTING (OPTIONAL)
-- =============================================

-- Sample questionnaire questions metadata (for reference)
-- This would typically be handled by the application layer
INSERT INTO public.nutrition_questionnaire_responses (user_id, question_id, response_value, response_timestamp)
SELECT
    u.id,
    'sample_setup_complete',
    'true',
    NOW()
FROM public.users u
WHERE u.telegram_id = 0 -- Sample user, adjust as needed
ON CONFLICT (user_id, question_id) DO NOTHING;

COMMIT;

-- =============================================
-- MIGRATION COMPLETE
-- =============================================
-- This migration adds comprehensive nutrition personalization features:
-- 1. Enhanced user profiles with 25+ preference fields
-- 2. Questionnaire response tracking system
-- 3. Nutrition DNA profiling with 8 personality archetypes
-- 4. Personalized meal recommendation engine
-- 5. Enhanced food analysis with behavioral insights
-- 6. Meal plan integration with personalization levels
-- 7. Helpful views for complete user nutrition data
-- 8. Proper indexes for performance optimization
-- 9. Foreign key constraints for data integrity
-- 10. Timestamp triggers for audit trails