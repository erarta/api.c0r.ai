-- Fix existing users onboarding status
-- Date: 2025-09-27
-- Description: Set onboarding_completed = true for existing users who have profiles

BEGIN;

-- Update existing users who have complete profiles to mark onboarding as completed
UPDATE public.user_profiles
SET
    onboarding_completed = true,
    onboarding_completed_at = COALESCE(updated_at, created_at)
WHERE
    onboarding_completed IS NULL OR onboarding_completed = false
    AND age IS NOT NULL
    AND gender IS NOT NULL
    AND goal IS NOT NULL
    AND daily_calories_target IS NOT NULL;

-- Log the update
SELECT
    COUNT(*) as updated_users,
    'Updated existing users onboarding status' as message
FROM public.user_profiles
WHERE onboarding_completed = true;

COMMIT;

-- Migration complete: existing users with complete profiles now have onboarding_completed = true