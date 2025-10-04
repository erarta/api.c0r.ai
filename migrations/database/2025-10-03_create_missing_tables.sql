-- Migration: Create missing tables in production (analysis_corrections, favorites_food, saved_recipes)
-- Created: 2025-10-03
-- Added by: Claude for schema synchronization

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-03_create_missing_tables.sql') THEN

        -- Create analysis_corrections table
        CREATE TABLE IF NOT EXISTS public.analysis_corrections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            source_log_id UUID,
            original_items JSONB NOT NULL,
            corrected_items JSONB NOT NULL,
            reason TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS analysis_corrections_user_idx ON public.analysis_corrections(user_id, created_at DESC);

        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'analysis_corrections_user_id_fkey') THEN
                ALTER TABLE public.analysis_corrections
                ADD CONSTRAINT analysis_corrections_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
            END IF;
        END $$;

        -- Create favorites_food table
        CREATE TABLE IF NOT EXISTS public.favorites_food (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            name TEXT NOT NULL,
            items_json JSONB NOT NULL,
            composition_hash TEXT NOT NULL,
            default_portion NUMERIC,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS favorites_food_user_created_idx ON public.favorites_food(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS favorites_food_user_name_idx ON public.favorites_food(user_id, name);

        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'favorites_food_user_id_fkey') THEN
                ALTER TABLE public.favorites_food
                ADD CONSTRAINT favorites_food_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
            END IF;
        END $$;

        -- Create saved_recipes table
        CREATE TABLE IF NOT EXISTS public.saved_recipes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            title TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            recipe_json JSONB NOT NULL,
            source TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS saved_recipes_user_created_idx ON public.saved_recipes(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS saved_recipes_user_title_idx ON public.saved_recipes(user_id, title);

        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'saved_recipes_language_check') THEN
                ALTER TABLE public.saved_recipes
                ADD CONSTRAINT saved_recipes_language_check
                CHECK (language = ANY (ARRAY['en'::text, 'ru'::text]));
            END IF;
        END $$;

        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'saved_recipes_user_id_fkey') THEN
                ALTER TABLE public.saved_recipes
                ADD CONSTRAINT saved_recipes_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
            END IF;
        END $$;

        -- Grant permissions
        GRANT ALL ON public.analysis_corrections TO postgres;
        GRANT ALL ON public.analysis_corrections TO service_role;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.analysis_corrections TO anon;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.analysis_corrections TO authenticated;

        GRANT ALL ON public.favorites_food TO postgres;
        GRANT ALL ON public.favorites_food TO service_role;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.favorites_food TO anon;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.favorites_food TO authenticated;

        GRANT ALL ON public.saved_recipes TO postgres;
        GRANT ALL ON public.saved_recipes TO service_role;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.saved_recipes TO anon;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.saved_recipes TO authenticated;

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-03_create_missing_tables.sql');

        RAISE NOTICE 'Migration 2025-10-03_create_missing_tables.sql applied successfully';
        RAISE NOTICE 'Created tables: analysis_corrections, favorites_food, saved_recipes';
    ELSE
        RAISE NOTICE 'Migration 2025-10-03_create_missing_tables.sql already applied, skipping';
    END IF;
END $$;