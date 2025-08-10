-- 2025-08-08 Rollback: favorites, corrections, meal plans, saved recipes, indexes
-- Drops objects created by 2025-08-08_features_favorites_plans_recipes.sql

BEGIN;

-- Drop indexes (safe if not exists)
DROP INDEX IF EXISTS public.favorites_food_user_created_idx;
DROP INDEX IF EXISTS public.favorites_food_user_name_idx;
DROP INDEX IF EXISTS public.analysis_corrections_user_idx;
DROP INDEX IF EXISTS public.meal_plans_user_period_uniq;
DROP INDEX IF EXISTS public.meal_plans_user_created_idx;
DROP INDEX IF EXISTS public.saved_recipes_user_created_idx;
DROP INDEX IF EXISTS public.saved_recipes_user_title_idx;
-- Note: users_language_idx may be pre-existing; drop only if created by forward
DROP INDEX IF EXISTS public.users_language_idx;

-- Drop tables
DROP TABLE IF EXISTS public.saved_recipes CASCADE;
DROP TABLE IF EXISTS public.meal_plans CASCADE;
DROP TABLE IF EXISTS public.analysis_corrections CASCADE;
DROP TABLE IF EXISTS public.favorites_food CASCADE;

COMMIT;
