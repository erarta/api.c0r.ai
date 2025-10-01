-- Migration: Create user activity logs table for testing migration system
-- Created: 2025-10-01
-- Added by: Claude for end-to-end migration testing
-- Purpose: Test automated migration deployment from development to production

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = '2025-10-01_create_user_activity_logs_table.sql') THEN

        -- Create user activity logs table
        CREATE TABLE IF NOT EXISTS public.user_activity_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            activity_type VARCHAR(100) NOT NULL,
            activity_description TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            ip_address INET,
            user_agent TEXT,
            session_id VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            -- Constraints
            CONSTRAINT user_activity_logs_activity_type_check CHECK (length(activity_type) > 0),
            CONSTRAINT user_activity_logs_user_id_check CHECK (user_id IS NOT NULL)
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_user_activity_logs_user_id ON public.user_activity_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_activity_logs_activity_type ON public.user_activity_logs(activity_type);
        CREATE INDEX IF NOT EXISTS idx_user_activity_logs_created_at ON public.user_activity_logs(created_at);
        CREATE INDEX IF NOT EXISTS idx_user_activity_logs_session_id ON public.user_activity_logs(session_id) WHERE session_id IS NOT NULL;

        -- Grant permissions
        GRANT ALL ON public.user_activity_logs TO postgres;
        GRANT ALL ON public.user_activity_logs TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.user_activity_logs TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.user_activity_logs TO authenticated;

        -- Insert test data to verify the table works
        INSERT INTO public.user_activity_logs (user_id, activity_type, activity_description, metadata, session_id) VALUES
        (gen_random_uuid(), 'login', 'User logged in via Telegram bot', '{"source": "telegram", "version": "2.0"}', 'test-session-003'),
        (gen_random_uuid(), 'food_analysis', 'User analyzed food image', '{"image_type": "jpg", "analysis_duration": 2.5}', 'test-session-004'),
        (gen_random_uuid(), 'plan_generation', 'User generated meal plan', '{"days": 3, "preferences": ["vegetarian"]}', 'test-session-005');

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('2025-10-01_create_user_activity_logs_table.sql');

        RAISE NOTICE 'Migration 2025-10-01_create_user_activity_logs_table.sql applied successfully';
        RAISE NOTICE 'Created user_activity_logs table with 3 test records';
    ELSE
        RAISE NOTICE 'Migration 2025-10-01_create_user_activity_logs_table.sql already applied, skipping';
    END IF;
END $$;