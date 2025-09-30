-- Enhanced Nutrition System Rollback
-- Date: 2025-09-25
-- Description: Rollback for Enhanced Nutrition System migration

-- Rollback: 2025-09-25_enhanced_nutrition_system_rollback.sql
-- Original: 2025-09-25_enhanced_nutrition_system.sql

BEGIN;

-- =============================================
-- ROLLBACK: DROP VIEWS
-- =============================================

DROP VIEW IF EXISTS public.recent_meal_recommendations;
DROP VIEW IF EXISTS public.complete_nutrition_profiles;

-- =============================================
-- ROLLBACK: DROP TRIGGERS
-- =============================================

DROP TRIGGER IF EXISTS update_nutrition_questionnaire_responses_updated_at ON public.nutrition_questionnaire_responses;
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- =============================================
-- ROLLBACK: REMOVE MEAL PLANS EXTENSIONS
-- =============================================

ALTER TABLE public.meal_plans
DROP CONSTRAINT IF EXISTS meal_plans_nutrition_dna_id_fkey,
DROP COLUMN IF EXISTS nutrition_dna_id,
DROP COLUMN IF EXISTS personalization_level,
DROP COLUMN IF EXISTS generation_metadata;

-- Drop meal plans indexes
DROP INDEX IF EXISTS idx_meal_plans_nutrition_dna_id;

-- =============================================
-- ROLLBACK: DROP ENHANCED TABLES
-- =============================================

-- Drop enhanced food analysis table
DROP TABLE IF EXISTS public.user_food_analysis_enhanced CASCADE;

-- Drop meal recommendations table
DROP TABLE IF EXISTS public.meal_recommendations CASCADE;

-- Drop nutrition DNA table
DROP TABLE IF EXISTS public.nutrition_dna CASCADE;

-- Drop questionnaire responses table
DROP TABLE IF EXISTS public.nutrition_questionnaire_responses CASCADE;

-- =============================================
-- ROLLBACK: REMOVE USER PROFILES EXTENSIONS
-- =============================================

-- Drop user profiles indexes
DROP INDEX IF EXISTS idx_user_profiles_allergies;
DROP INDEX IF EXISTS idx_user_profiles_dietary_preferences;
DROP INDEX IF EXISTS idx_user_profiles_preferred_cuisines;
DROP INDEX IF EXISTS idx_user_profiles_onboarding_completed;

-- Remove enhanced nutrition fields from user_profiles
ALTER TABLE public.user_profiles
DROP COLUMN IF EXISTS supplements,
DROP COLUMN IF EXISTS skip_meals,
DROP COLUMN IF EXISTS eating_frequency,
DROP COLUMN IF EXISTS accountability_preference,
DROP COLUMN IF EXISTS timeline,
DROP COLUMN IF EXISTS weight_goal,
DROP COLUMN IF EXISTS primary_motivation,
DROP COLUMN IF EXISTS stress_eating_tendency,
DROP COLUMN IF EXISTS weekend_eating_style,
DROP COLUMN IF EXISTS snacking_preference,
DROP COLUMN IF EXISTS meal_prep_preference,
DROP COLUMN IF EXISTS water_intake_goal,
DROP COLUMN IF EXISTS health_conditions,
DROP COLUMN IF EXISTS social_eating_frequency,
DROP COLUMN IF EXISTS work_schedule,
DROP COLUMN IF EXISTS cooking_time_available,
DROP COLUMN IF EXISTS cooking_skill,
DROP COLUMN IF EXISTS meal_times,
DROP COLUMN IF EXISTS preferred_cuisines,
DROP COLUMN IF EXISTS disliked_foods,
DROP COLUMN IF EXISTS favorite_foods,
DROP COLUMN IF EXISTS onboarding_completed_at,
DROP COLUMN IF EXISTS onboarding_completed;

COMMIT;

-- =============================================
-- ROLLBACK COMPLETE
-- =============================================
-- This rollback removes all Enhanced Nutrition System features:
-- 1. All new tables (nutrition_dna, meal_recommendations, etc.)
-- 2. Extended user_profiles columns
-- 3. All related indexes and constraints
-- 4. Helper views and triggers
-- 5. Foreign key relationships
--
-- After rollback, the system returns to basic nutrition functionality.