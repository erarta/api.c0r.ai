-- Rollback: Remove test analytics table
-- Created: 2025-10-01
-- Added by: Claude for migration system testing
-- Purpose: Rollback for 2025-10-01_create_test_analytics_table.sql

-- Check if rollback should be applied
DO $$
BEGIN
    -- Check if the table exists before trying to drop it
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_analytics') THEN

        -- Drop the table and all its dependencies
        DROP TABLE IF EXISTS public.test_analytics CASCADE;

        -- Remove migration log entry
        DELETE FROM public.migrations_log WHERE migration_name = '2025-10-01_create_test_analytics_table.sql';

        -- Log the rollback
        INSERT INTO public.migrations_log (migration_name, applied_at)
        VALUES ('2025-10-01_create_test_analytics_table_rollback.sql', CURRENT_TIMESTAMP);

        RAISE NOTICE 'Rollback completed: test_analytics table dropped';
        RAISE NOTICE 'Migration log entry removed';
    ELSE
        RAISE NOTICE 'test_analytics table does not exist, nothing to rollback';
    END IF;
END $$;