-- Rollback: Restore test tables in production (if needed)
-- Created: 2025-10-03
-- Added by: Claude for production cleanup rollback

DO $$
BEGIN
    -- Note: This rollback would recreate the test tables if needed
    -- However, since these were test tables, this rollback mainly removes the cleanup log entry

    -- Remove cleanup migration log entry
    DELETE FROM public.migrations_log WHERE migration_name = '2025-10-03_cleanup_production_test_tables.sql';

    -- Restore original migration log entries (if they were deleted)
    INSERT INTO public.migrations_log (migration_name, applied_at) VALUES
    ('2025-10-01_create_test_analytics_table.sql', CURRENT_TIMESTAMP),
    ('2025-10-01_create_zer0_final_migration_testing_table.sql', CURRENT_TIMESTAMP),
    ('2025-10-01_create_zer0_final_migration_testing_v2_table.sql', CURRENT_TIMESTAMP)
    ON CONFLICT (migration_name) DO NOTHING;

    -- Log the rollback
    INSERT INTO public.migrations_log (migration_name, applied_at)
    VALUES ('2025-10-03_cleanup_production_test_tables_rollback.sql', CURRENT_TIMESTAMP);

    RAISE NOTICE 'Rollback completed: cleanup migration reverted';
    RAISE NOTICE 'Note: Test tables were not recreated - use original migration files to restore if needed';
END $$;