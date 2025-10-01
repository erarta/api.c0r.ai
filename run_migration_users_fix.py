#!/usr/bin/env python3
"""
Apply users table migration to fix production bot issues
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get direct PostgreSQL connection"""
    # Try to construct connection string from Supabase URL
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        print("ERROR: SUPABASE_URL not found in environment")
        return None

    # Parse Supabase URL to get PostgreSQL connection details
    # Supabase URL format: https://xyz.supabase.co
    # PostgreSQL URL format: postgresql://postgres:[password]@db.xyz.supabase.co:5432/postgres

    if "supabase.co" in supabase_url:
        project_id = supabase_url.split("//")[1].split(".")[0]
        db_password = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("DB_PASSWORD")

        if not db_password:
            print("ERROR: Database password not found. Set SUPABASE_SERVICE_KEY or DB_PASSWORD")
            return None

        # Construct PostgreSQL connection string
        db_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
        print(f"Connecting to: postgresql://postgres:***@db.{project_id}.supabase.co:5432/postgres")

        try:
            conn = psycopg2.connect(db_url)
            return conn
        except Exception as e:
            print(f"Connection failed: {e}")
            return None
    else:
        print(f"Unrecognized Supabase URL format: {supabase_url}")
        return None

def run_migration():
    """Execute the migration script"""
    migration_file = Path(__file__).parent / "migrations" / "database" / "2025-09-30_fix_correct_users_table.sql"

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    print(f"Reading migration from: {migration_file}")
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Get database connection
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        print("Executing migration...")
        cursor.execute(migration_sql)

        # Fetch any notices or results
        while cursor.nextset():
            pass

        conn.commit()
        print("Migration completed successfully!")

        # Verify the schema
        print("\nVerifying users table schema:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()
        if columns:
            print("Columns in public.users:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        else:
            print("No columns found - table may not exist or may be in different schema")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    print("=== Running Users Table Migration ===")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("The bot should now work correctly on production.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)