-- Migration: Cleanup test tables after migration system validation
-- Created: 2025-10-01
-- Added by: Claude for test table cleanup
-- Purpose: Remove all test tables created during migration system development

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-01_zzz_cleanup_test_tables.sql') THEN

        -- Drop test_analytics table
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_analytics') THEN
            DROP TABLE public.test_analytics CASCADE;
            RAISE NOTICE 'Dropped test_analytics table';
        END IF;

        -- Drop zer0_final_migration_testing table
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'zer0_final_migration_testing') THEN
            DROP TABLE public.zer0_final_migration_testing CASCADE;
            RAISE NOTICE 'Dropped zer0_final_migration_testing table';
        END IF;

        -- Drop zer0_final_migration_testing_v2 table
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'zer0_final_migration_testing_v2') THEN
            DROP TABLE public.zer0_final_migration_testing_v2 CASCADE;
            RAISE NOTICE 'Dropped zer0_final_migration_testing_v2 table';
        END IF;

        -- Clean up migration log entries for test tables
        DELETE FROM public.migrations_log WHERE migration_name IN (
            '2025-10-01_create_test_analytics_table.sql',
            '2025-10-01_create_zer0_final_migration_testing_table.sql',
            '2025-10-01_create_zer0_final_migration_testing_v2_table.sql'
        );

        -- Log this cleanup migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-01_zzz_cleanup_test_tables.sql');

        RAISE NOTICE 'Migration 2025-10-01_zzz_cleanup_test_tables.sql applied successfully';
        RAISE NOTICE 'All test tables have been cleaned up';
        RAISE NOTICE 'Migration system validation completed - test environment restored';
    ELSE
        RAISE NOTICE 'Migration 2025-10-01_zzz_cleanup_test_tables.sql already applied, skipping';
    END IF;
END $$;