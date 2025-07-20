-- ==========================================
-- RECIPE GENERATION MIGRATION ROLLBACK v0.5.0
-- ==========================================
-- Date: 2025-01-19
-- Purpose: Rollback dietary preferences and allergies fields for recipe generation
-- Description: This rollback removes the dietary_preferences and allergies columns
--              and their associated constraints and indexes from user_profiles table

-- ==========================================
-- 1. DROP INDEXES FOR NEW FIELDS
-- ==========================================

-- Drop index for dietary preferences queries
DROP INDEX IF EXISTS idx_user_profiles_dietary_preferences;

-- Drop index for allergies queries  
DROP INDEX IF EXISTS idx_user_profiles_allergies;

-- ==========================================
-- 2. DROP CONSTRAINTS FOR NEW FIELDS
-- ==========================================

-- Drop constraint for dietary preferences
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'check_dietary_preferences_valid'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_dietary_preferences_valid;
        RAISE NOTICE 'Dropped dietary preferences validation constraint';
    END IF;
END $$;

-- Drop constraint for allergies
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'check_allergies_valid'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_allergies_valid;
        RAISE NOTICE 'Dropped allergies validation constraint';
    END IF;
END $$;

-- ==========================================
-- 3. DROP NEW PROFILE FIELDS
-- ==========================================

-- Drop dietary preferences field
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' AND column_name = 'dietary_preferences'
    ) THEN
        ALTER TABLE user_profiles DROP COLUMN dietary_preferences;
        RAISE NOTICE 'Dropped dietary_preferences column';
    END IF;
END $$;

-- Drop allergies field
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' AND column_name = 'allergies'
    ) THEN
        ALTER TABLE user_profiles DROP COLUMN allergies;
        RAISE NOTICE 'Dropped allergies column';
    END IF;
END $$;

-- ==========================================
-- 4. REVERT LOGS TABLE COMMENT
-- ==========================================

-- Revert action_type comment to original
COMMENT ON COLUMN logs.action_type IS 'Type of user action: photo_analysis, start, help, status, buy, profile, daily';

-- ==========================================
-- ROLLBACK COMPLETE
-- ==========================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Recipe generation migration rollback completed successfully';
END $$;