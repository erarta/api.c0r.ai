# 🔄 Database Constraints Migration Rollback Guide

## Overview
This guide explains how to rollback the database constraints migration (`database_constraints.sql`) if something goes wrong.

## ⚠️ When to Rollback
- If the migration fails partway through
- If you encounter unexpected errors after migration
- If you need to temporarily disable constraints for maintenance
- If you want to revert to the previous database state

## 🔧 How to Rollback

### Step 1: Access Supabase Dashboard
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor**

### Step 2: Run Rollback Script
1. Copy the entire contents of `database_constraints_rollback.sql`
2. Paste it into the SQL Editor
3. Click **Run** (▶️)

### Step 3: Verify Rollback
The rollback script will show verification queries that confirm:
- ✅ All NOT NULL constraints have been removed
- ✅ All check constraints have been dropped
- ✅ Automatic calorie calculation trigger has been removed
- ✅ All comments have been cleared

## 📋 What the Rollback Does

### Removes All Constraints:
- **NOT NULL constraints** from all profile fields (age, gender, height_cm, weight_kg, activity_level, goal)
- **Check constraints** for data validation (age range, height range, weight range, gender validation, activity validation, goal validation)

### Removes Automation:
- **Automatic calorie calculation trigger** (`trigger_calculate_calories`)
- **Calorie calculation function** (`calculate_profile_calories()`)

### Cleans Up Documentation:
- **Column comments** for all profile fields
- **Table comment** for user_profiles

## ⚠️ Important Warnings

After rollback:
- ❌ **Incomplete profiles can be created again** (age: NULL, etc.)
- ❌ **No automatic calorie calculation** will occur
- ❌ **Data validation will not be enforced** at database level
- ❌ **The original error** (profile setup failure) may return

## 🔄 Re-applying Migration

If you want to re-apply the migration after rollback:
1. Fix any issues that caused the original problem
2. Run `database_constraints.sql` again
3. The migration is idempotent - safe to run multiple times

## 🆘 Emergency Rollback

If you need to rollback immediately due to production issues:

```sql
-- Quick emergency rollback (run in SQL Editor)
DROP TRIGGER IF EXISTS trigger_calculate_calories ON user_profiles;
DROP FUNCTION IF EXISTS calculate_profile_calories();
ALTER TABLE user_profiles ALTER COLUMN age DROP NOT NULL;
ALTER TABLE user_profiles ALTER COLUMN gender DROP NOT NULL;
ALTER TABLE user_profiles ALTER COLUMN height_cm DROP NOT NULL;
ALTER TABLE user_profiles ALTER COLUMN weight_kg DROP NOT NULL;
ALTER TABLE user_profiles ALTER COLUMN activity_level DROP NOT NULL;
ALTER TABLE user_profiles ALTER COLUMN goal DROP NOT NULL;
```

## 📞 Support

If you encounter issues with the rollback:
1. Check the error messages in Supabase SQL Editor
2. Verify that the `user_profiles` table exists
3. Ensure you have proper permissions to modify the table
4. Contact your database administrator if needed

## ✅ Success Indicators

After successful rollback, you should see:
- All columns allow NULL values again
- No check constraints remain
- No triggers on the user_profiles table
- Clean verification queries showing the original state

---

**Note**: This rollback script is designed to be safe and idempotent. You can run it multiple times without causing errors. 