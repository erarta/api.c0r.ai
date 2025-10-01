-- Migration: Create zer0_final_migration_testing_v2 table for GitHub Actions testing
-- Created: 2025-10-01
-- Added by: Claude for testing fixed GitHub Actions auto-migrations
-- Purpose: Verify that automatic migrations work correctly in CI/CD pipeline

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-01_create_zer0_final_migration_testing_v2_table.sql') THEN

        -- Create zer0_final_migration_testing_v2 table
        CREATE TABLE IF NOT EXISTS public.zer0_final_migration_testing_v2 (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            test_name VARCHAR(255) NOT NULL,
            test_version VARCHAR(10) NOT NULL DEFAULT 'v2',
            github_actions_test BOOLEAN NOT NULL DEFAULT true,
            deployment_method VARCHAR(50) NOT NULL DEFAULT 'github_actions',
            test_data JSONB DEFAULT '{}'::jsonb,
            environment VARCHAR(20) NOT NULL,
            deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            test_status VARCHAR(50) NOT NULL DEFAULT 'pending',

            -- Constraints
            CONSTRAINT zer0_v2_test_name_check CHECK (length(test_name) > 0),
            CONSTRAINT zer0_v2_status_check CHECK (test_status IN ('pending', 'running', 'passed', 'failed')),
            CONSTRAINT zer0_v2_env_check CHECK (environment IN ('development', 'production')),
            CONSTRAINT zer0_v2_method_check CHECK (deployment_method IN ('manual', 'github_actions', 'local_test'))
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_zer0_v2_test_name ON public.zer0_final_migration_testing_v2(test_name);
        CREATE INDEX IF NOT EXISTS idx_zer0_v2_version ON public.zer0_final_migration_testing_v2(test_version);
        CREATE INDEX IF NOT EXISTS idx_zer0_v2_deployment_method ON public.zer0_final_migration_testing_v2(deployment_method);
        CREATE INDEX IF NOT EXISTS idx_zer0_v2_environment ON public.zer0_final_migration_testing_v2(environment);
        CREATE INDEX IF NOT EXISTS idx_zer0_v2_deployed_at ON public.zer0_final_migration_testing_v2(deployed_at);

        -- Grant permissions
        GRANT ALL ON public.zer0_final_migration_testing_v2 TO postgres;
        GRANT ALL ON public.zer0_final_migration_testing_v2 TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.zer0_final_migration_testing_v2 TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.zer0_final_migration_testing_v2 TO authenticated;

        -- Insert test data to verify the table works
        INSERT INTO public.zer0_final_migration_testing_v2 (test_name, test_status, test_data, environment, deployment_method) VALUES
        ('github_actions_migration_test', 'passed', '{"ci": true, "automated": true, "version": "v2"}', 'development', 'github_actions'),
        ('ci_cd_pipeline_test', 'passed', '{"workflow": "deploy.yml", "fixed_env_vars": true}', 'development', 'github_actions'),
        ('auto_deployment_validation', 'passed', '{"timestamp": "2025-10-01", "status": "github_actions_fixed"}', 'development', 'github_actions');

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-01_create_zer0_final_migration_testing_v2_table.sql');

        RAISE NOTICE 'Migration 2025-10-01_create_zer0_final_migration_testing_v2_table.sql applied successfully';
        RAISE NOTICE 'Created zer0_final_migration_testing_v2 table with 3 test records';
        RAISE NOTICE 'GitHub Actions auto-migration test table ready!';
    ELSE
        RAISE NOTICE 'Migration 2025-10-01_create_zer0_final_migration_testing_v2_table.sql already applied, skipping';
    END IF;
END $$;