-- Migration: Cleanup test tables from production
-- Created: 2025-10-03
-- Added by: Claude for production cleanup

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-03_cleanup_production_test_tables.sql') THEN

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
        VALUES ('2025-10-03_cleanup_production_test_tables.sql');

        RAISE NOTICE 'Migration 2025-10-03_cleanup_production_test_tables.sql applied successfully';
        RAISE NOTICE 'Production environment cleaned up - all test tables removed';
    ELSE
        RAISE NOTICE 'Migration 2025-10-03_cleanup_production_test_tables.sql already applied, skipping';
    END IF;
END $$;