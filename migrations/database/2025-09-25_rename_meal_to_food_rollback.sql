-- Rollback: Rename 'food' back to 'meal' in table names
-- Date: 2025-09-25
-- Description: Rollback migration that renamed meal_recommendations to food_recommendations

BEGIN;

-- =============================================
-- 1. RENAME food_recommendations BACK TO meal_recommendations
-- =============================================

-- Drop dependent objects first
DROP VIEW IF EXISTS public.recent_food_recommendations;

-- Rename the table back
ALTER TABLE public.food_recommendations RENAME TO meal_recommendations;

-- Update check constraint for food_type back to meal_type
ALTER TABLE public.meal_recommendations RENAME COLUMN food_type TO meal_type;

-- Update check constraint
ALTER TABLE public.meal_recommendations DROP CONSTRAINT IF EXISTS food_recommendations_food_type_check;
ALTER TABLE public.meal_recommendations ADD CONSTRAINT meal_recommendations_meal_type_check
    CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack'));

-- Rename indexes back
ALTER INDEX IF EXISTS food_recommendations_pkey RENAME TO meal_recommendations_pkey;
ALTER INDEX IF EXISTS idx_food_recommendations_user_id RENAME TO idx_meal_recommendations_user_id;
ALTER INDEX IF EXISTS idx_food_recommendations_nutrition_dna_id RENAME TO idx_meal_recommendations_nutrition_dna_id;
ALTER INDEX IF EXISTS idx_food_recommendations_food_type RENAME TO idx_meal_recommendations_meal_type;
ALTER INDEX IF EXISTS idx_food_recommendations_created_at RENAME TO idx_meal_recommendations_created_at;

-- Rename constraints back
ALTER TABLE public.meal_recommendations RENAME CONSTRAINT food_recommendations_user_id_fkey TO meal_recommendations_user_id_fkey;
ALTER TABLE public.meal_recommendations RENAME CONSTRAINT food_recommendations_nutrition_dna_id_fkey TO meal_recommendations_nutrition_dna_id_fkey;

-- =============================================
-- 2. RENAME food_plans BACK TO meal_plans
-- =============================================

-- Rename the table back
ALTER TABLE public.food_plans RENAME TO meal_plans;

-- Rename indexes back
ALTER INDEX IF EXISTS food_plans_pkey RENAME TO meal_plans_pkey;
ALTER INDEX IF EXISTS idx_food_plans_user_id RENAME TO idx_meal_plans_user_id;
ALTER INDEX IF EXISTS idx_food_plans_nutrition_dna_id RENAME TO idx_meal_plans_nutrition_dna_id;

-- Rename constraints back
ALTER TABLE public.meal_plans RENAME CONSTRAINT food_plans_user_id_fkey TO meal_plans_user_id_fkey;
ALTER TABLE public.meal_plans RENAME CONSTRAINT food_plans_nutrition_dna_id_fkey TO meal_plans_nutrition_dna_id_fkey;

-- =============================================
-- 3. ROLLBACK FOREIGN KEY REFERENCES
-- =============================================

-- Update foreign key reference back
DO $$
BEGIN
    -- Check if there's a food_plan reference to rename back
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_food_analysis_enhanced'
        AND column_name = 'food_plan_id'
    ) THEN
        -- Update food_plan references back to meal_plan
        ALTER TABLE public.user_food_analysis_enhanced RENAME COLUMN food_plan_id TO meal_plan_id;
    END IF;
END $$;

-- =============================================
-- 4. RECREATE ORIGINAL VIEWS
-- =============================================

-- Recreate the original view with meal names
CREATE OR REPLACE VIEW public.recent_meal_recommendations AS
SELECT
    mr.*,
    nd.archetype,
    nd.confidence_score
FROM public.meal_recommendations mr
LEFT JOIN public.nutrition_dna nd ON mr.nutrition_dna_id = nd.id
WHERE mr.created_at >= NOW() - INTERVAL '30 days'
ORDER BY mr.created_at DESC;

COMMIT;

-- =============================================
-- ROLLBACK COMPLETE
-- =============================================