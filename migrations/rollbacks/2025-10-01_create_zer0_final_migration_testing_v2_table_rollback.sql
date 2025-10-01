-- Rollback: Remove zer0_final_migration_testing_v2 table
-- Created: 2025-10-01
-- Added by: Claude for GitHub Actions migration testing
-- Purpose: Rollback for 2025-10-01_create_zer0_final_migration_testing_v2_table.sql

-- Check if rollback should be applied
DO $$
BEGIN
    -- Check if the table exists before trying to drop it
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'zer0_final_migration_testing_v2') THEN

        -- Drop the table and all its dependencies
        DROP TABLE IF EXISTS public.zer0_final_migration_testing_v2 CASCADE;

        -- Remove migration log entry
        DELETE FROM public.migrations_log WHERE migration_name = '2025-10-01_create_zer0_final_migration_testing_v2_table.sql';

        -- Log the rollback
        INSERT INTO public.migrations_log (migration_name, applied_at)
        VALUES ('2025-10-01_create_zer0_final_migration_testing_v2_table_rollback.sql', CURRENT_TIMESTAMP);

        RAISE NOTICE 'Rollback completed: zer0_final_migration_testing_v2 table dropped';
        RAISE NOTICE 'Migration log entry removed';
        RAISE NOTICE 'GitHub Actions migration test rollback completed!';
    ELSE
        RAISE NOTICE 'zer0_final_migration_testing_v2 table does not exist, nothing to rollback';
    END IF;
END $$;