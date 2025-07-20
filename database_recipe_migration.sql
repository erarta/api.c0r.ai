-- ==========================================
-- RECIPE GENERATION MIGRATION v0.5.0
-- ==========================================
-- Date: 2025-01-19
-- Purpose: Add dietary preferences and allergies fields for recipe generation

-- ==========================================
-- 1. ADD NEW PROFILE FIELDS
-- ==========================================

-- Add dietary preferences field (array of text values)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' AND column_name = 'dietary_preferences'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN dietary_preferences TEXT[] DEFAULT '{}';
        RAISE NOTICE 'Added dietary_preferences column';
    END IF;
END $$;

-- Add allergies field (array of text values)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' AND column_name = 'allergies'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN allergies TEXT[] DEFAULT '{}';
        RAISE NOTICE 'Added allergies column';
    END IF;
END $$;

-- ==========================================
-- 2. ADD CONSTRAINTS FOR NEW FIELDS
-- ==========================================

-- Add constraint for dietary preferences (valid options)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'check_dietary_preferences_valid'
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_dietary_preferences_valid 
        CHECK (
            dietary_preferences <@ ARRAY[
                'vegetarian', 'vegan', 'pescatarian', 'keto', 'paleo', 
                'mediterranean', 'low_carb', 'low_fat', 'gluten_free', 
                'dairy_free', 'halal', 'kosher', 'none'
            ]
        );
        RAISE NOTICE 'Added dietary preferences validation constraint';
    END IF;
END $$;

-- Add constraint for allergies (valid options)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'check_allergies_valid'
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_allergies_valid 
        CHECK (
            allergies <@ ARRAY[
                'nuts', 'peanuts', 'shellfish', 'fish', 'eggs', 'dairy', 
                'soy', 'wheat', 'gluten', 'sesame', 'sulfites', 'none'
            ]
        );
        RAISE NOTICE 'Added allergies validation constraint';
    END IF;
END $$;

-- ==========================================
-- 3. UPDATE LOGS TABLE FOR RECIPE ACTIONS
-- ==========================================

-- Update action_type comment to include recipe generation
COMMENT ON COLUMN logs.action_type IS 'Type of user action: photo_analysis, recipe_generation, start, help, status, buy, profile, daily';

-- ==========================================
-- 4. CREATE INDEXES FOR NEW FIELDS
-- ==========================================

-- Index for dietary preferences queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_dietary_preferences ON user_profiles USING GIN(dietary_preferences);

-- Index for allergies queries  
CREATE INDEX IF NOT EXISTS idx_user_profiles_allergies ON user_profiles USING GIN(allergies);

-- ==========================================
-- 5. ADD COMMENTS FOR DOCUMENTATION
-- ==========================================

COMMENT ON COLUMN user_profiles.dietary_preferences IS 'Array of dietary preferences for recipe generation';
COMMENT ON COLUMN user_profiles.allergies IS 'Array of food allergies to avoid in recipes';