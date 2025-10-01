-- Create meal_plans table (alias for food_plans)
CREATE TABLE IF NOT EXISTS public.meal_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    plan_json JSONB NOT NULL,
    shopping_list_json JSONB DEFAULT '{}'::jsonb,
    intro_summary TEXT,
    generated_from TEXT DEFAULT 'llm_generated',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_dates UNIQUE (user_id, start_date, end_date)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_id ON public.meal_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_dates ON public.meal_plans(start_date, end_date);

-- Grant permissions
GRANT ALL ON public.meal_plans TO postgres;
GRANT ALL ON public.meal_plans TO service_role;