-- Migration: Simple production schema fix - only add missing columns
-- File: 2025-09-30_simple_production_fix.sql
-- Purpose: Add only the required columns without dropping existing ones

BEGIN;

-- Add credits_remaining column (rename from credits if exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'credits_remaining'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'credits'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN credits TO credits_remaining;
            RAISE NOTICE 'Renamed credits to credits_remaining';
        ELSE
            ALTER TABLE public.users ADD COLUMN credits_remaining integer NOT NULL DEFAULT 3;
            RAISE NOTICE 'Added credits_remaining column';
        END IF;
    ELSE
        RAISE NOTICE 'credits_remaining already exists';
    END IF;
END $$;

-- Add language column (rename from language_code if exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'language'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'language_code'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN language_code TO language;
            RAISE NOTICE 'Renamed language_code to language';
        ELSE
            ALTER TABLE public.users
            ADD COLUMN language text DEFAULT 'en'::text
            CHECK (language = ANY (ARRAY['en'::text, 'ru'::text]));
            RAISE NOTICE 'Added language column';
        END IF;
    ELSE
        RAISE NOTICE 'language already exists';
    END IF;
END $$;

-- Add country column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'country'
    ) THEN
        ALTER TABLE public.users ADD COLUMN country text;
        RAISE NOTICE 'Added country column';
    ELSE
        RAISE NOTICE 'country already exists';
    END IF;
END $$;

-- Add phone_number column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone_number'
    ) THEN
        ALTER TABLE public.users ADD COLUMN phone_number text;
        RAISE NOTICE 'Added phone_number column';
    ELSE
        RAISE NOTICE 'phone_number already exists';
    END IF;
END $$;

-- Add total_paid column (rename from total_spent if exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'total_paid'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'total_spent'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN total_spent TO total_paid;
            RAISE NOTICE 'Renamed total_spent to total_paid';
        ELSE
            ALTER TABLE public.users ADD COLUMN total_paid numeric NOT NULL DEFAULT 0;
            RAISE NOTICE 'Added total_paid column';
        END IF;
    ELSE
        RAISE NOTICE 'total_paid already exists';
    END IF;
END $$;

-- Force schema cache refresh
COMMENT ON TABLE users IS 'User accounts table - production schema updated';
NOTIFY pgrst, 'reload schema';

-- Show final schema
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY column_name;

COMMIT;