-- Migration: Fix the actual users table that the application uses
-- File: 2025-09-30_fix_correct_users_table.sql
-- Purpose: Identify and modify the correct users table that PostgREST serves to the application

BEGIN;

-- Find and list all users tables in the database
DO $$
DECLARE
    table_record RECORD;
    schema_name TEXT;
    table_name TEXT;
    full_table_name TEXT;
BEGIN
    RAISE NOTICE '=== SEARCHING FOR USERS TABLES ===';

    FOR table_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE tablename LIKE '%user%'
        ORDER BY schemaname, tablename
    LOOP
        RAISE NOTICE 'Found table: %.%', table_record.schemaname, table_record.tablename;
    END LOOP;
END $$;

-- Check if public.users exists and what columns it has
DO $$
DECLARE
    col_record RECORD;
    table_exists BOOLEAN := FALSE;
BEGIN
    RAISE NOTICE '=== CHECKING PUBLIC.USERS TABLE ===';

    -- Check if public.users exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) INTO table_exists;

    IF table_exists THEN
        RAISE NOTICE 'public.users table exists';
        RAISE NOTICE 'Current columns in public.users:';

        FOR col_record IN
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users'
            ORDER BY ordinal_position
        LOOP
            RAISE NOTICE '  - % (% %)', col_record.column_name, col_record.data_type,
                CASE WHEN col_record.is_nullable = 'YES' THEN 'NULL' ELSE 'NOT NULL' END;
        END LOOP;
    ELSE
        RAISE NOTICE 'public.users table does NOT exist';
    END IF;
END $$;

-- Now apply the migration to public.users if it exists, otherwise create it
DO $$
DECLARE
    table_exists BOOLEAN := FALSE;
    has_telegram_id BOOLEAN := FALSE;
    has_credits BOOLEAN := FALSE;
    has_credits_remaining BOOLEAN := FALSE;
    has_language BOOLEAN := FALSE;
    has_language_code BOOLEAN := FALSE;
    has_total_spent BOOLEAN := FALSE;
    has_total_paid BOOLEAN := FALSE;
BEGIN
    RAISE NOTICE '=== APPLYING MIGRATION TO PUBLIC.USERS ===';

    -- Check if public.users exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) INTO table_exists;

    IF NOT table_exists THEN
        RAISE NOTICE 'Creating public.users table';
        CREATE TABLE public.users (
            id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
            telegram_id bigint UNIQUE NOT NULL,
            credits_remaining integer NOT NULL DEFAULT 3,
            language text DEFAULT 'en'::text CHECK (language = ANY (ARRAY['en'::text, 'ru'::text])),
            country text,
            phone_number text,
            total_paid numeric NOT NULL DEFAULT 0,
            created_at timestamp with time zone DEFAULT now()
        );

        -- Enable RLS
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

        RAISE NOTICE 'Created public.users table with correct schema';
    ELSE
        RAISE NOTICE 'public.users table exists, checking columns...';

        -- Check existing columns
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'telegram_id'
        ) INTO has_telegram_id;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'credits'
        ) INTO has_credits;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'credits_remaining'
        ) INTO has_credits_remaining;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'language'
        ) INTO has_language;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'language_code'
        ) INTO has_language_code;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'total_spent'
        ) INTO has_total_spent;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'total_paid'
        ) INTO has_total_paid;

        -- Ensure telegram_id exists
        IF NOT has_telegram_id THEN
            ALTER TABLE public.users ADD COLUMN telegram_id bigint UNIQUE NOT NULL DEFAULT 0;
            RAISE NOTICE 'Added telegram_id column';
        END IF;

        -- Handle credits -> credits_remaining migration
        IF has_credits AND NOT has_credits_remaining THEN
            ALTER TABLE public.users RENAME COLUMN credits TO credits_remaining;
            RAISE NOTICE 'Renamed credits to credits_remaining';
        ELSIF NOT has_credits AND NOT has_credits_remaining THEN
            ALTER TABLE public.users ADD COLUMN credits_remaining integer NOT NULL DEFAULT 3;
            RAISE NOTICE 'Added credits_remaining column';
        END IF;

        -- Handle language_code -> language migration
        IF has_language_code AND NOT has_language THEN
            ALTER TABLE public.users RENAME COLUMN language_code TO language;
            RAISE NOTICE 'Renamed language_code to language';
        ELSIF NOT has_language_code AND NOT has_language THEN
            ALTER TABLE public.users ADD COLUMN language text DEFAULT 'en'::text
                CHECK (language = ANY (ARRAY['en'::text, 'ru'::text]));
            RAISE NOTICE 'Added language column';
        END IF;

        -- Handle total_spent -> total_paid migration
        IF has_total_spent AND NOT has_total_paid THEN
            ALTER TABLE public.users RENAME COLUMN total_spent TO total_paid;
            RAISE NOTICE 'Renamed total_spent to total_paid';
        ELSIF NOT has_total_spent AND NOT has_total_paid THEN
            ALTER TABLE public.users ADD COLUMN total_paid numeric NOT NULL DEFAULT 0;
            RAISE NOTICE 'Added total_paid column';
        END IF;

        -- Add missing columns
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'country'
        ) THEN
            ALTER TABLE public.users ADD COLUMN country text;
            RAISE NOTICE 'Added country column';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'phone_number'
        ) THEN
            ALTER TABLE public.users ADD COLUMN phone_number text;
            RAISE NOTICE 'Added phone_number column';
        END IF;
    END IF;
END $$;

-- Grant necessary permissions
GRANT ALL ON public.users TO postgres;
GRANT ALL ON public.users TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO authenticated;

-- Force schema cache refresh for PostgREST
COMMENT ON TABLE public.users IS 'User accounts table - schema aligned 2025-09-30';
NOTIFY pgrst, 'reload schema';

-- Show final schema
RAISE NOTICE '=== FINAL SCHEMA VERIFICATION ===';
SELECT
    'public.users' as table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'users'
ORDER BY ordinal_position;

COMMIT;