-- Migration: Create test analytics table for migration system testing
-- Created: 2025-10-01
-- Added by: Claude for migration system testing
-- Purpose: Test that auto-migrations work correctly from dev to production

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-01_create_test_analytics_table.sql') THEN

        -- Create test analytics table
        CREATE TABLE IF NOT EXISTS public.test_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_name VARCHAR(255) NOT NULL,
            event_data JSONB DEFAULT '{}'::jsonb,
            user_agent TEXT,
            ip_address INET,
            session_id VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP WITH TIME ZONE,

            -- Add some indexes for performance
            CONSTRAINT test_analytics_event_name_check CHECK (length(event_name) > 0)
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_test_analytics_event_name ON public.test_analytics(event_name);
        CREATE INDEX IF NOT EXISTS idx_test_analytics_created_at ON public.test_analytics(created_at);
        CREATE INDEX IF NOT EXISTS idx_test_analytics_session_id ON public.test_analytics(session_id) WHERE session_id IS NOT NULL;

        -- Grant permissions
        GRANT ALL ON public.test_analytics TO postgres;
        GRANT ALL ON public.test_analytics TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.test_analytics TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.test_analytics TO authenticated;

        -- Insert test data to verify the table works
        INSERT INTO public.test_analytics (event_name, event_data, session_id) VALUES
        ('migration_test', '{"test": true, "version": "1.0"}', 'test-session-001'),
        ('system_check', '{"component": "migrations", "status": "active"}', 'test-session-002');

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-01_create_test_analytics_table.sql');

        RAISE NOTICE 'Migration 2025-10-01_create_test_analytics_table.sql applied successfully';
        RAISE NOTICE 'Created test_analytics table with 2 test records';
    ELSE
        RAISE NOTICE 'Migration 2025-10-01_create_test_analytics_table.sql already applied, skipping';
    END IF;
END $$;