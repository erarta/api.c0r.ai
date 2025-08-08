-- 2025-08-08 Combined migration: favorites, corrections, flexible meal plans, saved recipes, indexes
-- NOTE: Verify in staging before production. Uses Postgres extensions/functions like gen_random_uuid().

BEGIN;

-- 1) Favorites: user-saved analyzed foods (quick add)
CREATE TABLE IF NOT EXISTS public.favorites_food (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name text NOT NULL,                               -- user-friendly name for search
  items_json jsonb NOT NULL,                        -- normalized detected items (LLM + control layer)
  composition_hash text NOT NULL,                   -- hash of items for duplicate detection
  default_portion numeric,                          -- optional default portion in grams
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS favorites_food_user_created_idx ON public.favorites_food (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS favorites_food_user_name_idx ON public.favorites_food (user_id, name);

-- 2) Analysis corrections: user adjustments to model output
CREATE TABLE IF NOT EXISTS public.analysis_corrections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  source_log_id uuid,                               -- optional link to public.logs.id
  original_items jsonb NOT NULL,                    -- original analysis result
  corrected_items jsonb NOT NULL,                   -- user-corrected result
  reason text,                                      -- optional user/system reason
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS analysis_corrections_user_idx ON public.analysis_corrections (user_id, created_at DESC);

-- 3) Meal plans: flexible duration (not only weeks)
CREATE TABLE IF NOT EXISTS public.meal_plans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  start_date date NOT NULL,
  end_date date NOT NULL,
  plan_json jsonb NOT NULL,                         -- days -> meals -> recipes/ingredients
  shopping_list_json jsonb NOT NULL,                -- aggregated ingredients list
  generated_from text,                              -- 'threshold_days' | 'threshold_analyses' | 'manual'
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT meal_plans_date_range CHECK (end_date >= start_date)
);

-- unique to prevent duplicates for same period per user
CREATE UNIQUE INDEX IF NOT EXISTS meal_plans_user_period_uniq ON public.meal_plans (user_id, start_date, end_date);
CREATE INDEX IF NOT EXISTS meal_plans_user_created_idx ON public.meal_plans (user_id, created_at DESC);

-- 4) Saved recipes: generated via "Create Recipe" button
CREATE TABLE IF NOT EXISTS public.saved_recipes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title text NOT NULL,                              -- auto-generated from recipe heading or user-provided
  language text DEFAULT 'en' CHECK (language = ANY (ARRAY['en','ru'])),
  recipe_json jsonb NOT NULL,                       -- full structured recipe (ingredients, steps, kbzhu)
  source text,                                      -- e.g., 'button_create_recipe' | 'analysis_followup'
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS saved_recipes_user_created_idx ON public.saved_recipes (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS saved_recipes_user_title_idx ON public.saved_recipes (user_id, title);

-- 5) Helpful index for routing/payments
CREATE INDEX IF NOT EXISTS users_language_idx ON public.users (language);

COMMIT;
