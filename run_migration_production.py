#!/usr/bin/env python3
"""
Production Migration Runner for Enhanced Nutrition System
Runs migration on production with confirmation bypass
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def log(message):
    print(f"{GREEN}[INFO]{NC} {message}")

def error(message):
    print(f"{RED}[ERROR]{NC} {message}")

def warning(message):
    print(f"{YELLOW}[WARNING]{NC} {message}")

def run_migration(env_file):
    """Run migration using environment file"""

    if not Path(env_file).exists():
        error(f"Environment file not found: {env_file}")
        return False

    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        error("DATABASE_URL not found in environment file")
        return False

    log(f"Using database: {database_url.split('@')[1].split('/')[0]}...")

    # Check if psql is available
    try:
        subprocess.run(['psql', '--version'], capture_output=True, check=True)
        log("PostgreSQL client (psql) is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        error("psql command not found. Please install PostgreSQL client:")
        error("  macOS: brew install postgresql")
        error("  Ubuntu/Debian: sudo apt-get install postgresql-client")
        error("  Windows: Download from postgresql.org")
        return False

    # Path to migration file - support custom migration file
    if len(sys.argv) > 1:
        migration_filename = sys.argv[1]
    else:
        migration_filename = "2025-09-25_enhanced_nutrition_system.sql"

    migration_file = Path(__file__).parent / "migrations" / "database" / migration_filename

    if not migration_file.exists():
        error(f"Migration file not found: {migration_file}")
        return False

    log(f"Found migration file: {migration_file.name}")

    # Run migration
    log("Executing migration...")
    try:
        result = subprocess.run([
            'psql', database_url, '-f', str(migration_file)
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            log("✅ Migration executed successfully!")

            # Show any output
            if result.stdout.strip():
                log("Migration output:")
                print(result.stdout)

            return True
        else:
            error("❌ Migration failed!")
            if result.stderr:
                error("Error details:")
                print(result.stderr)
            if result.stdout:
                error("Output:")
                print(result.stdout)
            return False

    except subprocess.TimeoutExpired:
        error("❌ Migration timed out (5 minutes limit)")
        return False
    except Exception as e:
        error(f"❌ Migration execution failed: {e}")
        return False

def verify_migration(env_file):
    """Verify migration was successful"""

    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

    database_url = os.environ.get('DATABASE_URL')

    log("Verifying migration...")

    # Check if tables were created (updated for food naming)
    verify_sql = """
    SELECT
        CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'nutrition_dna') THEN '✅' ELSE '❌' END ||
        ' nutrition_dna' as table_check
    UNION ALL
    SELECT
        CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'nutrition_questionnaire_responses') THEN '✅' ELSE '❌' END ||
        ' nutrition_questionnaire_responses'
    UNION ALL
    SELECT
        CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'food_recommendations') THEN '✅' ELSE '❌' END ||
        ' food_recommendations'
    UNION ALL
    SELECT
        CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'food_plans') THEN '✅' ELSE '❌' END ||
        ' food_plans'
    UNION ALL
    SELECT
        CASE WHEN EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'onboarding_completed') THEN '✅' ELSE '❌' END ||
        ' user_profiles.onboarding_completed'
    ;
    """

    try:
        result = subprocess.run([
            'psql', database_url, '-c', verify_sql
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            log("Migration verification results:")
            print(result.stdout)

            # Check if all verifications passed
            if '❌' not in result.stdout:
                log("🎉 All migration components verified successfully!")
                return True
            else:
                warning("⚠️ Some migration components may have issues")
                return False
        else:
            error("Verification query failed")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        error(f"Verification failed: {e}")
        return False

def main():
    """Main entry point"""

    print("🧬 Enhanced Nutrition System - Production Migration Runner")
    print("=" * 60)

    env_file = ".env.production"

    log(f"Running migration for production environment")
    log(f"Using configuration file: {env_file}")
    log("⚠️ PRODUCTION DATABASE MIGRATION - PROCEEDING AUTOMATICALLY")
    print("")

    # Run migration
    success = run_migration(env_file)

    if success:
        print("")
        log("Migration completed successfully")

        # Verify migration
        if verify_migration(env_file):
            print("")
            log("🎉 Enhanced Nutrition System is ready on PRODUCTION!")
            log("Next steps:")
            log("1. Update your application with new environment variables")
            log("2. Restart your application services")
            log("3. Test the enhanced nutrition features")
            print("")
        else:
            warning("Migration completed but verification found issues")
            warning("Please check the database manually")
    else:
        print("")
        error("❌ Migration failed!")
        error("Please check the error messages above and:")
        error("1. Verify database connection")
        error("2. Check database permissions")
        error("3. Ensure migration file is present")
        error("4. Try running the SQL manually in Supabase dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()