#!/usr/bin/env python3
"""
Fix production database schema - apply the actual migration to production DB
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load the ACTUAL production environment (what the deployed app uses)
print("=== PRODUCTION DATABASE SCHEMA FIX ===")

# Use the production database connection string from logs
PRODUCTION_DB_URL = "postgresql://postgres.mmrzpngugivxoapjiovb:xuoO4|LSaaGX5@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

def apply_production_migration():
    """Apply the schema migration to production database"""

    # The migration SQL to transform old schema to new schema
    migration_sql = """
    BEGIN;

    -- Rename columns to match expected schema
    DO $$
    BEGIN
        -- Rename credits to credits_remaining if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'credits'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'credits_remaining'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN credits TO credits_remaining;
            RAISE NOTICE 'Renamed credits to credits_remaining';
        END IF;

        -- Rename language_code to language if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'language_code'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'language'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN language_code TO language;
            RAISE NOTICE 'Renamed language_code to language';
        END IF;

        -- Rename total_spent to total_paid if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'total_spent'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'total_paid'
        ) THEN
            ALTER TABLE public.users RENAME COLUMN total_spent TO total_paid;
            RAISE NOTICE 'Renamed total_spent to total_paid';
        END IF;

        -- Add missing columns if they don't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'country'
        ) THEN
            ALTER TABLE public.users ADD COLUMN country text;
            RAISE NOTICE 'Added country column';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'phone_number'
        ) THEN
            ALTER TABLE public.users ADD COLUMN phone_number text;
            RAISE NOTICE 'Added phone_number column';
        END IF;
    END $$;

    -- Force schema cache refresh
    COMMENT ON TABLE users IS 'Users table - production schema fixed 2025-10-01';
    NOTIFY pgrst, 'reload schema';

    -- Show final schema
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'users'
    ORDER BY ordinal_position;

    COMMIT;
    """

    try:
        print(f"Connecting to production database...")
        conn = psycopg2.connect(PRODUCTION_DB_URL)
        cursor = conn.cursor()

        print("Applying migration...")
        cursor.execute(migration_sql)

        conn.commit()
        print("\n✅ Migration applied successfully!")

        # Now check the final schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("Final schema:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = apply_production_migration()
    if success:
        print("\n🎉 Production database schema has been fixed!")
        print("The bot should now work correctly.")
    else:
        print("\n💥 Migration failed. Please check the error above.")
        sys.exit(1)