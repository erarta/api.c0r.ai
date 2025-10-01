-- Migration: Align production schema with development schema
-- File: 2025-09-30_align_production_schema.sql
-- Purpose: Add missing columns to production users table to match development

BEGIN;

-- Add credits_remaining column (rename from credits if exists)
DO $$
BEGIN
    -- Check if credits_remaining already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'credits_remaining'
    ) THEN
        -- Check if credits column exists (production schema)
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'credits'
        ) THEN
            -- Rename credits to credits_remaining
            ALTER TABLE public.users RENAME COLUMN credits TO credits_remaining;
            RAISE NOTICE 'Renamed credits column to credits_remaining';
        ELSE
            -- Add new credits_remaining column
            ALTER TABLE public.users
            ADD COLUMN credits_remaining integer NOT NULL DEFAULT 3;
            RAISE NOTICE 'Added credits_remaining column';
        END IF;
    ELSE
        RAISE NOTICE 'credits_remaining column already exists';
    END IF;
END $$;

-- Add language column (rename from language_code if exists)
DO $$
BEGIN
    -- Check if language already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'language'
    ) THEN
        -- Check if language_code column exists (production schema)
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'language_code'
        ) THEN
            -- Rename language_code to language
            ALTER TABLE public.users RENAME COLUMN language_code TO language;
            RAISE NOTICE 'Renamed language_code column to language';
        ELSE
            -- Add new language column
            ALTER TABLE public.users
            ADD COLUMN language text DEFAULT 'en'::text
            CHECK (language = ANY (ARRAY['en'::text, 'ru'::text]));
            RAISE NOTICE 'Added language column';
        END IF;
    ELSE
        RAISE NOTICE 'language column already exists';
    END IF;
END $$;

-- Add missing columns from development schema
DO $$
BEGIN
    -- Add country column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'country'
    ) THEN
        ALTER TABLE public.users ADD COLUMN country text;
        RAISE NOTICE 'Added country column';
    END IF;

    -- Add phone_number column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'phone_number'
    ) THEN
        ALTER TABLE public.users ADD COLUMN phone_number text;
        RAISE NOTICE 'Added phone_number column';
    END IF;

    -- Add total_paid column if missing (matches development schema)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'total_paid'
    ) THEN
        -- Check if total_spent exists (production schema)
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'total_spent'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN total_spent TO total_paid;
            RAISE NOTICE 'Renamed total_spent column to total_paid';
        ELSE
            ALTER TABLE public.users ADD COLUMN total_paid numeric NOT NULL DEFAULT 0;
            RAISE NOTICE 'Added total_paid column';
        END IF;
    END IF;
END $$;

-- Remove production-specific columns that don't exist in development
DO $$
BEGIN
    -- Remove username if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'username'
    ) THEN
        ALTER TABLE public.users DROP COLUMN username;
        RAISE NOTICE 'Dropped username column';
    END IF;

    -- Remove first_name if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'first_name'
    ) THEN
        ALTER TABLE public.users DROP COLUMN first_name;
        RAISE NOTICE 'Dropped first_name column';
    END IF;

    -- Remove last_name if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_name'
    ) THEN
        ALTER TABLE public.users DROP COLUMN last_name;
        RAISE NOTICE 'Dropped last_name column';
    END IF;

    -- Remove style_profile if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'style_profile'
    ) THEN
        ALTER TABLE public.users DROP COLUMN style_profile;
        RAISE NOTICE 'Dropped style_profile column';
    END IF;

    -- Remove body_measurements if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'body_measurements'
    ) THEN
        ALTER TABLE public.users DROP COLUMN body_measurements;
        RAISE NOTICE 'Dropped body_measurements column';
    END IF;

    -- Remove preferences if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'preferences'
    ) THEN
        ALTER TABLE public.users DROP COLUMN preferences;
        RAISE NOTICE 'Dropped preferences column';
    END IF;

    -- Remove size_preferences if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'size_preferences'
    ) THEN
        ALTER TABLE public.users DROP COLUMN size_preferences;
        RAISE NOTICE 'Dropped size_preferences column';
    END IF;

    -- Remove is_active if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE public.users DROP COLUMN is_active;
        RAISE NOTICE 'Dropped is_active column';
    END IF;

    -- Remove is_premium if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'is_premium'
    ) THEN
        ALTER TABLE public.users DROP COLUMN is_premium;
        RAISE NOTICE 'Dropped is_premium column';
    END IF;

    -- Remove last_activity if exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_activity'
    ) THEN
        ALTER TABLE public.users DROP COLUMN last_activity;
        RAISE NOTICE 'Dropped last_activity column';
    END IF;

    -- Remove updated_at if exists (development has no updated_at in users table)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'updated_at'
    ) THEN
        BEGIN
            ALTER TABLE public.users DROP COLUMN updated_at;
            RAISE NOTICE 'Dropped updated_at column';
        EXCEPTION
            WHEN undefined_column THEN
                RAISE NOTICE 'updated_at column does not exist, skipping';
        END;
    ELSE
        RAISE NOTICE 'updated_at column does not exist';
    END IF;
END $$;

-- Force schema cache refresh
COMMENT ON TABLE users IS 'User accounts table - aligned with development schema';
NOTIFY pgrst, 'reload schema';

-- Verify final schema matches development
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY column_name;

COMMIT;