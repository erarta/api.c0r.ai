-- ==========================================
-- DATABASE CONSTRAINTS MIGRATION v0.4.3
-- ==========================================
-- Date: 2025-01-21
-- Purpose: Add NOT NULL constraints and validation to prevent incomplete profiles
-- This ensures data integrity at the database level

-- ==========================================
-- 1. ADD NOT NULL CONSTRAINTS TO REQUIRED FIELDS
-- ==========================================

-- Add NOT NULL constraints to required profile fields
-- This will prevent any new incomplete profiles from being created

-- First, let's check if constraints already exist to avoid errors
DO $$
BEGIN
    -- Check if age column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'age' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN age SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to age column';
    ELSE
        RAISE NOTICE 'Age column already has NOT NULL constraint';
    END IF;
END $$;

DO $$
BEGIN
    -- Check if gender column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'gender' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN gender SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to gender column';
    ELSE
        RAISE NOTICE 'Gender column already has NOT NULL constraint';
    END IF;
END $$;

DO $$
BEGIN
    -- Check if height_cm column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'height_cm' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN height_cm SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to height_cm column';
    ELSE
        RAISE NOTICE 'Height_cm column already has NOT NULL constraint';
    END IF;
END $$;

DO $$
BEGIN
    -- Check if weight_kg column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'weight_kg' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN weight_kg SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to weight_kg column';
    ELSE
        RAISE NOTICE 'Weight_kg column already has NOT NULL constraint';
    END IF;
END $$;

DO $$
BEGIN
    -- Check if activity_level column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'activity_level' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN activity_level SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to activity_level column';
    ELSE
        RAISE NOTICE 'Activity_level column already has NOT NULL constraint';
    END IF;
END $$;

DO $$
BEGIN
    -- Check if goal column is already NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'goal' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN goal SET NOT NULL;
        RAISE NOTICE 'Added NOT NULL constraint to goal column';
    ELSE
        RAISE NOTICE 'Goal column already has NOT NULL constraint';
    END IF;
END $$;

-- ==========================================
-- 2. ADD VALIDATION CHECK CONSTRAINTS
-- ==========================================

-- Add check constraints to ensure data is within valid ranges
-- These will prevent invalid data from being inserted

-- Age range check (10-120 years)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_age_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_age_range CHECK (age >= 10 AND age <= 120);
        RAISE NOTICE 'Added age range check constraint';
    ELSE
        RAISE NOTICE 'Age range check constraint already exists';
    END IF;
END $$;

-- Height range check (100-250 cm)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_height_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_height_range CHECK (height_cm >= 100 AND height_cm <= 250);
        RAISE NOTICE 'Added height range check constraint';
    ELSE
        RAISE NOTICE 'Height range check constraint already exists';
    END IF;
END $$;

-- Weight range check (30-300 kg)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_weight_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_weight_range CHECK (weight_kg >= 30 AND weight_kg <= 300);
        RAISE NOTICE 'Added weight range check constraint';
    ELSE
        RAISE NOTICE 'Weight range check constraint already exists';
    END IF;
END $$;

-- Gender validation check
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_gender_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_gender_valid CHECK (gender IN ('male', 'female'));
        RAISE NOTICE 'Added gender validation check constraint';
    ELSE
        RAISE NOTICE 'Gender validation check constraint already exists';
    END IF;
END $$;

-- Activity level validation check
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_activity_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_activity_valid CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active'));
        RAISE NOTICE 'Added activity level validation check constraint';
    ELSE
        RAISE NOTICE 'Activity level validation check constraint already exists';
    END IF;
END $$;

-- Goal validation check
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_goal_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles ADD CONSTRAINT check_goal_valid CHECK (goal IN ('lose_weight', 'maintain_weight', 'gain_weight'));
        RAISE NOTICE 'Added goal validation check constraint';
    ELSE
        RAISE NOTICE 'Goal validation check constraint already exists';
    END IF;
END $$;

-- ==========================================
-- 3. CREATE AUTOMATIC CALORIE CALCULATION TRIGGER
-- ==========================================

-- Create function to automatically calculate daily calories when all fields are present
CREATE OR REPLACE FUNCTION calculate_profile_calories()
RETURNS TRIGGER AS $$
DECLARE
    bmr NUMERIC;
    tdee NUMERIC;
BEGIN
    -- Only calculate if all required fields are present
    IF NEW.age IS NOT NULL AND NEW.gender IS NOT NULL AND NEW.height_cm IS NOT NULL 
       AND NEW.weight_kg IS NOT NULL AND NEW.activity_level IS NOT NULL AND NEW.goal IS NOT NULL THEN
        
        -- Calculate BMR using Mifflin-St Jeor Equation
        IF NEW.gender = 'male' THEN
            bmr := 10 * NEW.weight_kg + 6.25 * NEW.height_cm - 5 * NEW.age + 5;
        ELSE
            bmr := 10 * NEW.weight_kg + 6.25 * NEW.height_cm - 5 * NEW.age - 161;
        END IF;
        
        -- Apply activity multiplier
        CASE NEW.activity_level
            WHEN 'sedentary' THEN tdee := bmr * 1.2;
            WHEN 'lightly_active' THEN tdee := bmr * 1.375;
            WHEN 'moderately_active' THEN tdee := bmr * 1.55;
            WHEN 'very_active' THEN tdee := bmr * 1.725;
            WHEN 'extremely_active' THEN tdee := bmr * 1.9;
        END CASE;
        
        -- Apply goal adjustment
        CASE NEW.goal
            WHEN 'lose_weight' THEN tdee := tdee * 0.85;
            WHEN 'gain_weight' THEN tdee := tdee * 1.15;
            WHEN 'maintain_weight' THEN tdee := tdee; -- No adjustment
        END CASE;
        
        NEW.daily_calories_target := ROUND(tdee);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically calculate calories
DROP TRIGGER IF EXISTS trigger_calculate_calories ON user_profiles;
CREATE TRIGGER trigger_calculate_calories
    BEFORE INSERT OR UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION calculate_profile_calories();

-- ==========================================
-- 4. VERIFY COLUMN TYPES AND ADD DOCUMENTATION
-- ==========================================

-- Verify that daily_calories_target column exists and has correct type
DO $$
BEGIN
    -- Check if daily_calories_target column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'daily_calories_target'
    ) THEN
        -- Add the column if it doesn't exist
        ALTER TABLE user_profiles ADD COLUMN daily_calories_target INTEGER;
        RAISE NOTICE 'Added daily_calories_target column';
    ELSE
        -- Check if the column type is correct
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public'
            AND lower(table_name) = 'user_profiles' 
            AND column_name = 'daily_calories_target'
            AND data_type = 'integer'
        ) THEN
            -- Alter the column type if it's not INTEGER
            ALTER TABLE user_profiles ALTER COLUMN daily_calories_target TYPE INTEGER USING daily_calories_target::INTEGER;
            RAISE NOTICE 'Updated daily_calories_target column type to INTEGER';
        ELSE
            RAISE NOTICE 'daily_calories_target column already exists with correct type';
        END IF;
    END IF;
END $$;

-- Verify TEXT column types for gender, activity_level, and goal
DO $$
BEGIN
    -- Check gender column type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'gender'
        AND data_type NOT IN ('text', 'character varying')
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN gender TYPE TEXT;
        RAISE NOTICE 'Updated gender column type to TEXT';
    END IF;
    
    -- Check activity_level column type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'activity_level'
        AND data_type NOT IN ('text', 'character varying')
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN activity_level TYPE TEXT;
        RAISE NOTICE 'Updated activity_level column type to TEXT';
    END IF;
    
    -- Check goal column type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'goal'
        AND data_type NOT IN ('text', 'character varying')
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN goal TYPE TEXT;
        RAISE NOTICE 'Updated goal column type to TEXT';
    END IF;
END $$;

-- Add comment to document the constraints
COMMENT ON TABLE user_profiles IS 'User profiles with automatic calorie calculation and data validation constraints';

-- Add comments to important columns
COMMENT ON COLUMN user_profiles.age IS 'User age in years (10-120) - REQUIRED';
COMMENT ON COLUMN user_profiles.gender IS 'User gender (male/female) - REQUIRED';
COMMENT ON COLUMN user_profiles.height_cm IS 'User height in centimeters (100-250) - REQUIRED';
COMMENT ON COLUMN user_profiles.weight_kg IS 'User weight in kilograms (30-300) - REQUIRED';
COMMENT ON COLUMN user_profiles.activity_level IS 'Activity level (sedentary/lightly_active/moderately_active/very_active/extremely_active) - REQUIRED';
COMMENT ON COLUMN user_profiles.goal IS 'Weight goal (lose_weight/maintain_weight/gain_weight) - REQUIRED';
COMMENT ON COLUMN user_profiles.daily_calories_target IS 'Automatically calculated daily calorie target based on profile data';

-- ==========================================
-- 5. VERIFICATION QUERIES
-- ==========================================

-- This query will show the current state of NOT NULL constraints
SELECT 
    'NOT NULL Constraints:' as constraint_type,
    column_name,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public'
AND lower(table_name) = 'user_profiles' 
AND column_name IN ('age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal')
ORDER BY column_name;

-- This query will show all check constraints using pg_constraint
SELECT 
    'Check Constraints:' as constraint_type,
    conname as constraint_name,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'user_profiles'::regclass
AND contype = 'c'
ORDER BY conname;

-- This query will show column types for verification
SELECT 
    'Column Types:' as info_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public'
AND lower(table_name) = 'user_profiles' 
AND column_name IN ('age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal', 'daily_calories_target')
ORDER BY column_name;

-- This query will show if the trigger exists
SELECT 
    'Triggers:' as info_type,
    trigger_name,
    event_manipulation,
    action_statement
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
AND event_object_table = 'user_profiles'
AND trigger_name = 'trigger_calculate_calories';

-- ==========================================
-- MIGRATION COMPLETE
-- ==========================================
-- ✅ All NOT NULL constraints added to prevent incomplete profiles
-- ✅ All validation check constraints added for data integrity
-- ✅ Automatic calorie calculation trigger created
-- ✅ Database-level protection against incomplete profiles implemented
-- ✅ All constraints are idempotent (safe to run multiple times)
-- ✅ Used pg_constraint for reliable constraint checking
-- ✅ Simplified function structure (removed nested BEGIN)
-- ✅ Verified column types and added missing columns if needed
-- ✅ Added schema specification and case-insensitive table name handling
-- ✅ Verified TEXT column types for gender, activity_level, and goal