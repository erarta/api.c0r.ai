-- Rename 'meal' to 'food' in table names
-- Date: 2025-09-25
-- Description: Renames meal_recommendations to food_recommendations and updates meal_plans references

-- Migration: 2025-09-25_rename_meal_to_food.sql
-- Rollback: 2025-09-25_rename_meal_to_food_rollback.sql

BEGIN;

-- =============================================
-- 1. RENAME meal_recommendations TO food_recommendations
-- =============================================

-- Drop dependent objects first
DROP VIEW IF EXISTS public.recent_meal_recommendations;

-- Rename the table
ALTER TABLE public.meal_recommendations RENAME TO food_recommendations;

-- Update check constraint for meal_type to food_type
ALTER TABLE public.food_recommendations RENAME COLUMN meal_type TO food_type;

-- Update check constraint
ALTER TABLE public.food_recommendations DROP CONSTRAINT IF EXISTS meal_recommendations_meal_type_check;
ALTER TABLE public.food_recommendations ADD CONSTRAINT food_recommendations_food_type_check
    CHECK (food_type IN ('breakfast', 'lunch', 'dinner', 'snack'));

-- Rename indexes
ALTER INDEX IF EXISTS meal_recommendations_pkey RENAME TO food_recommendations_pkey;
ALTER INDEX IF EXISTS idx_meal_recommendations_user_id RENAME TO idx_food_recommendations_user_id;
ALTER INDEX IF EXISTS idx_meal_recommendations_nutrition_dna_id RENAME TO idx_food_recommendations_nutrition_dna_id;
ALTER INDEX IF EXISTS idx_meal_recommendations_meal_type RENAME TO idx_food_recommendations_food_type;
ALTER INDEX IF EXISTS idx_meal_recommendations_created_at RENAME TO idx_food_recommendations_created_at;

-- Rename constraints
ALTER TABLE public.food_recommendations RENAME CONSTRAINT meal_recommendations_user_id_fkey TO food_recommendations_user_id_fkey;
ALTER TABLE public.food_recommendations RENAME CONSTRAINT meal_recommendations_nutrition_dna_id_fkey TO food_recommendations_nutrition_dna_id_fkey;

-- =============================================
-- 2. RENAME meal_plans TO food_plans
-- =============================================

-- Rename the table
ALTER TABLE public.meal_plans RENAME TO food_plans;

-- Rename indexes
ALTER INDEX IF EXISTS meal_plans_pkey RENAME TO food_plans_pkey;
ALTER INDEX IF EXISTS idx_meal_plans_user_id RENAME TO idx_food_plans_user_id;
ALTER INDEX IF EXISTS idx_meal_plans_nutrition_dna_id RENAME TO idx_food_plans_nutrition_dna_id;

-- Rename constraints
ALTER TABLE public.food_plans RENAME CONSTRAINT meal_plans_user_id_fkey TO food_plans_user_id_fkey;
ALTER TABLE public.food_plans RENAME CONSTRAINT meal_plans_nutrition_dna_id_fkey TO food_plans_nutrition_dna_id_fkey;

-- =============================================
-- 3. UPDATE FOREIGN KEY REFERENCES
-- =============================================

-- Update foreign key reference in user_food_analysis_enhanced if it exists
DO $$
BEGIN
    -- Check if there's a foreign key referencing meal_plans (now food_plans)
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'user_food_analysis_enhanced'
        AND kcu.column_name LIKE '%meal_plan%'
    ) THEN
        -- Update any meal_plan references to food_plan
        ALTER TABLE public.user_food_analysis_enhanced RENAME COLUMN meal_plan_id TO food_plan_id;
    END IF;
END $$;

-- =============================================
-- 4. RECREATE UPDATED VIEWS
-- =============================================

-- Recreate the view with new table names
CREATE OR REPLACE VIEW public.recent_food_recommendations AS
SELECT
    fr.*,
    nd.archetype,
    nd.confidence_score
FROM public.food_recommendations fr
LEFT JOIN public.nutrition_dna nd ON fr.nutrition_dna_id = nd.id
WHERE fr.created_at >= NOW() - INTERVAL '30 days'
ORDER BY fr.created_at DESC;

-- Update the complete_nutrition_profiles view to reference food_plans
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

COMMIT;

-- =============================================
-- MIGRATION COMPLETE
-- =============================================
-- This migration renames all 'meal' references to 'food':
-- 1. meal_recommendations → food_recommendations
-- 2. meal_plans → food_plans
-- 3. meal_type → food_type
-- 4. Updates all related indexes, constraints, and views
-- 5. Maintains referential integrity throughout