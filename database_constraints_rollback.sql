-- ==========================================
-- DATABASE CONSTRAINTS ROLLBACK v0.4.3
-- ==========================================
-- Date: 2025-01-21
-- Purpose: Rollback script for database_constraints.sql migration
-- This safely undoes all constraints and changes if something goes wrong

-- ==========================================
-- 1. DROP TRIGGERS AND FUNCTIONS
-- ==========================================

-- Drop the automatic calorie calculation trigger
DROP TRIGGER IF EXISTS trigger_calculate_calories ON user_profiles;

-- Drop the calorie calculation function
DROP FUNCTION IF EXISTS calculate_profile_calories();

-- ==========================================
-- 2. DROP CHECK CONSTRAINTS
-- ==========================================

-- Drop all check constraints that were added
DO $$
BEGIN
    -- Drop age range check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_age_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_age_range;
        RAISE NOTICE 'Dropped check_age_range constraint';
    ELSE
        RAISE NOTICE 'check_age_range constraint does not exist';
    END IF;
END $$;

DO $$
BEGIN
    -- Drop height range check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_height_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_height_range;
        RAISE NOTICE 'Dropped check_height_range constraint';
    ELSE
        RAISE NOTICE 'check_height_range constraint does not exist';
    END IF;
END $$;

DO $$
BEGIN
    -- Drop weight range check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_weight_range' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_weight_range;
        RAISE NOTICE 'Dropped check_weight_range constraint';
    ELSE
        RAISE NOTICE 'check_weight_range constraint does not exist';
    END IF;
END $$;

DO $$
BEGIN
    -- Drop gender validation check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_gender_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_gender_valid;
        RAISE NOTICE 'Dropped check_gender_valid constraint';
    ELSE
        RAISE NOTICE 'check_gender_valid constraint does not exist';
    END IF;
END $$;

DO $$
BEGIN
    -- Drop activity level validation check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_activity_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_activity_valid;
        RAISE NOTICE 'Dropped check_activity_valid constraint';
    ELSE
        RAISE NOTICE 'check_activity_valid constraint does not exist';
    END IF;
END $$;

DO $$
BEGIN
    -- Drop goal validation check constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'check_goal_valid' 
        AND conrelid = 'user_profiles'::regclass
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT check_goal_valid;
        RAISE NOTICE 'Dropped check_goal_valid constraint';
    ELSE
        RAISE NOTICE 'check_goal_valid constraint does not exist';
    END IF;
END $$;

-- ==========================================
-- 3. REMOVE NOT NULL CONSTRAINTS
-- ==========================================

-- Remove NOT NULL constraints from all required fields
-- This allows NULL values again (rollback to original state)

DO $$
BEGIN
    -- Remove NOT NULL from age column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'age' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN age DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from age column';
    ELSE
        RAISE NOTICE 'Age column already allows NULL values';
    END IF;
END $$;

DO $$
BEGIN
    -- Remove NOT NULL from gender column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'gender' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN gender DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from gender column';
    ELSE
        RAISE NOTICE 'Gender column already allows NULL values';
    END IF;
END $$;

DO $$
BEGIN
    -- Remove NOT NULL from height_cm column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'height_cm' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN height_cm DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from height_cm column';
    ELSE
        RAISE NOTICE 'Height_cm column already allows NULL values';
    END IF;
END $$;

DO $$
BEGIN
    -- Remove NOT NULL from weight_kg column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'weight_kg' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN weight_kg DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from weight_kg column';
    ELSE
        RAISE NOTICE 'Weight_kg column already allows NULL values';
    END IF;
END $$;

DO $$
BEGIN
    -- Remove NOT NULL from activity_level column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'activity_level' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN activity_level DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from activity_level column';
    ELSE
        RAISE NOTICE 'Activity_level column already allows NULL values';
    END IF;
END $$;

DO $$
BEGIN
    -- Remove NOT NULL from goal column
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND lower(table_name) = 'user_profiles' 
        AND column_name = 'goal' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE user_profiles ALTER COLUMN goal DROP NOT NULL;
        RAISE NOTICE 'Removed NOT NULL constraint from goal column';
    ELSE
        RAISE NOTICE 'Goal column already allows NULL values';
    END IF;
END $$;

-- ==========================================
-- 4. REMOVE COLUMN COMMENTS
-- ==========================================

-- Remove comments that were added during migration
COMMENT ON COLUMN user_profiles.age IS NULL;
COMMENT ON COLUMN user_profiles.gender IS NULL;
COMMENT ON COLUMN user_profiles.height_cm IS NULL;
COMMENT ON COLUMN user_profiles.weight_kg IS NULL;
COMMENT ON COLUMN user_profiles.activity_level IS NULL;
COMMENT ON COLUMN user_profiles.goal IS NULL;
COMMENT ON COLUMN user_profiles.daily_calories_target IS NULL;

-- Remove table comment
COMMENT ON TABLE user_profiles IS NULL;

-- ==========================================
-- 5. VERIFICATION QUERIES
-- ==========================================

-- This query will show the current state of NOT NULL constraints after rollback
SELECT 
    'NOT NULL Constraints (After Rollback):' as constraint_type,
    column_name,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public'
AND lower(table_name) = 'user_profiles' 
AND column_name IN ('age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal')
ORDER BY column_name;

-- This query will show remaining check constraints (should be none)
SELECT 
    'Remaining Check Constraints:' as constraint_type,
    conname as constraint_name,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'user_profiles'::regclass
AND contype = 'c'
ORDER BY conname;

-- This query will show if any triggers remain
SELECT 
    'Remaining Triggers:' as info_type,
    trigger_name,
    event_manipulation,
    action_statement
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
AND event_object_table = 'user_profiles'
ORDER BY trigger_name;

-- This query will show column types after rollback
SELECT 
    'Column Types (After Rollback):' as info_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public'
AND lower(table_name) = 'user_profiles' 
AND column_name IN ('age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal', 'daily_calories_target')
ORDER BY column_name;

-- ==========================================
-- ROLLBACK COMPLETE
-- ==========================================
-- ✅ All NOT NULL constraints removed
-- ✅ All check constraints dropped
-- ✅ Automatic calorie calculation trigger and function removed
-- ✅ All column and table comments removed
-- ✅ Database returned to state before constraints migration
-- ✅ All operations are idempotent (safe to run multiple times)
-- 
-- ⚠️  WARNING: After rollback, incomplete profiles can be created again
-- ⚠️  WARNING: No automatic calorie calculation will occur
-- ⚠️  WARNING: Data validation will not be enforced at database level 