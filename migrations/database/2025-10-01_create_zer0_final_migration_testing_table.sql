-- Migration: Create zer0_final_migration_testing table for final system testing
-- Created: 2025-10-01
-- Added by: Claude for final end-to-end migration testing
-- Purpose: Final validation that automated migration system works from dev to production

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-01_create_zer0_final_migration_testing_table.sql') THEN

        -- Create zer0_final_migration_testing table
        CREATE TABLE IF NOT EXISTS public.zer0_final_migration_testing (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            test_name VARCHAR(255) NOT NULL,
            test_status VARCHAR(50) NOT NULL DEFAULT 'pending',
            test_data JSONB DEFAULT '{}'::jsonb,
            environment VARCHAR(20) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            -- Constraints
            CONSTRAINT zer0_final_test_name_check CHECK (length(test_name) > 0),
            CONSTRAINT zer0_final_status_check CHECK (test_status IN ('pending', 'running', 'passed', 'failed')),
            CONSTRAINT zer0_final_env_check CHECK (environment IN ('development', 'production'))
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_zer0_final_test_name ON public.zer0_final_migration_testing(test_name);
        CREATE INDEX IF NOT EXISTS idx_zer0_final_status ON public.zer0_final_migration_testing(test_status);
        CREATE INDEX IF NOT EXISTS idx_zer0_final_environment ON public.zer0_final_migration_testing(environment);
        CREATE INDEX IF NOT EXISTS idx_zer0_final_created_at ON public.zer0_final_migration_testing(created_at);

        -- Grant permissions
        GRANT ALL ON public.zer0_final_migration_testing TO postgres;
        GRANT ALL ON public.zer0_final_migration_testing TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.zer0_final_migration_testing TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.zer0_final_migration_testing TO authenticated;

        -- Insert test data to verify the table works
        INSERT INTO public.zer0_final_migration_testing (test_name, test_status, test_data, environment) VALUES
        ('migration_system_test', 'passed', '{"version": "1.0", "automated": true}', 'development'),
        ('database_connection_test', 'passed', '{"connection_time": 0.5, "region": "auto-detected"}', 'development'),
        ('final_validation_test', 'passed', '{"timestamp": "2025-10-01", "status": "all_systems_go"}', 'development');

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-01_create_zer0_final_migration_testing_table.sql');

        RAISE NOTICE 'Migration 2025-10-01_create_zer0_final_migration_testing_table.sql applied successfully';
        RAISE NOTICE 'Created zer0_final_migration_testing table with 3 test records';
        RAISE NOTICE 'Final migration system test completed successfully!';
    ELSE
        RAISE NOTICE 'Migration 2025-10-01_create_zer0_final_migration_testing_table.sql already applied, skipping';
    END IF;
END $$;