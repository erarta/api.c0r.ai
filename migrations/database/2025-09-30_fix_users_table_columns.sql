-- Migration: Fix missing users table columns and refresh schema cache
-- File: 2025-09-30_fix_users_table_columns.sql
-- Purpose: Resolve PostgREST schema cache issues causing bot /start failures

BEGIN;

-- Ensure credits_remaining column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'credits_remaining'
    ) THEN
        ALTER TABLE public.users
        ADD COLUMN credits_remaining integer NOT NULL DEFAULT 3;

        RAISE NOTICE 'Added credits_remaining column to users table';
    ELSE
        RAISE NOTICE 'credits_remaining column already exists';
    END IF;
END $$;

-- Ensure language column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'language'
    ) THEN
        ALTER TABLE public.users
        ADD COLUMN language text DEFAULT 'en'::text
        CHECK (language = ANY (ARRAY['en'::text, 'ru'::text]));

        RAISE NOTICE 'Added language column to users table';
    ELSE
        RAISE NOTICE 'language column already exists';
    END IF;
END $$;

-- Ensure country column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'country'
    ) THEN
        ALTER TABLE public.users
        ADD COLUMN country text;

        RAISE NOTICE 'Added country column to users table';
    ELSE
        RAISE NOTICE 'country column already exists';
    END IF;
END $$;

-- Ensure phone_number column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone_number'
    ) THEN
        ALTER TABLE public.users
        ADD COLUMN phone_number text;

        RAISE NOTICE 'Added phone_number column to users table';
    ELSE
        RAISE NOTICE 'phone_number column already exists';
    END IF;
END $$;

-- Force schema cache refresh
COMMENT ON TABLE users IS 'User accounts table - schema updated at 2025-09-30';
NOTIFY pgrst, 'reload schema';

-- Verify columns exist
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('credits_remaining', 'language', 'country', 'phone_number', 'telegram_id')
ORDER BY column_name;

COMMIT;