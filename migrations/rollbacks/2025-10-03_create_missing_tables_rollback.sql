-- Rollback: Remove missing tables (analysis_corrections, favorites_food, saved_recipes)
-- Created: 2025-10-03
-- Added by: Claude for schema synchronization rollback

DO $$
BEGIN
    -- Drop tables if they exist
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'analysis_corrections') THEN
        DROP TABLE public.analysis_corrections CASCADE;
        RAISE NOTICE 'Dropped analysis_corrections table';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'favorites_food') THEN
        DROP TABLE public.favorites_food CASCADE;
        RAISE NOTICE 'Dropped favorites_food table';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'saved_recipes') THEN
        DROP TABLE public.saved_recipes CASCADE;
        RAISE NOTICE 'Dropped saved_recipes table';
    END IF;

    -- Remove migration log entry
    DELETE FROM public.migrations_log WHERE migration_name = '2025-10-03_create_missing_tables.sql';

    -- Log the rollback
    INSERT INTO public.migrations_log (migration_name, applied_at)
    VALUES ('2025-10-03_create_missing_tables_rollback.sql', CURRENT_TIMESTAMP);

    RAISE NOTICE 'Rollback completed: missing tables removed';
END $$;