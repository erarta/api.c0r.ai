#!/usr/bin/env python3
"""
Script to run the multilingual migration on Supabase database
"""

import os
import sys
from supabase import create_client, Client
from loguru import logger

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def run_migration():
    """Run the multilingual migration"""
    logger.info("Starting multilingual migration...")
    
    try:
        # Migration statements
        statements = [
            # Add language columns to users table
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ru'))",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS country TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number TEXT",
            
            # Create index for language
            "CREATE INDEX IF NOT EXISTS idx_users_language ON users(language)",
            
            # Add comments
            "COMMENT ON COLUMN users.language IS 'User preferred language: en (English) or ru (Russian)'",
            "COMMENT ON COLUMN users.country IS 'User country code for language detection'",
            "COMMENT ON COLUMN users.phone_number IS 'User phone number for language detection'",
            
            # Drop and recreate view
            "DROP VIEW IF EXISTS user_activity_summary",
            """
            CREATE VIEW user_activity_summary AS
            SELECT 
                u.telegram_id,
                u.credits_remaining,
                u.total_paid,
                u.language,
                u.country,
                u.created_at,
                COUNT(l.id) as total_actions,
                COUNT(CASE WHEN l.action_type = 'photo_analysis' THEN 1 END) as photo_analyses,
                COUNT(CASE WHEN l.action_type = 'start' THEN 1 END) as start_commands,
                COUNT(CASE WHEN l.action_type = 'help' THEN 1 END) as help_commands,
                COUNT(CASE WHEN l.action_type = 'status' THEN 1 END) as status_commands,
                COUNT(CASE WHEN l.action_type = 'buy' THEN 1 END) as buy_commands,
                COUNT(CASE WHEN l.action_type = 'language_change' THEN 1 END) as language_changes,
                MAX(l.timestamp) as last_activity
            FROM users u
            LEFT JOIN logs l ON u.id = l.user_id
            GROUP BY u.id, u.telegram_id, u.credits_remaining, u.total_paid, u.language, u.country, u.created_at
            """
        ]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                logger.info(f"Executing statement {i}/{len(statements)}")
                logger.debug(f"SQL: {statement[:100]}...")
                
                try:
                    # Execute the statement using raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    logger.info(f"Statement {i} executed successfully")
                except Exception as e:
                    logger.error(f"Failed to execute statement {i}: {e}")
                    logger.error(f"Statement: {statement}")
                    raise
        
        logger.success("Multilingual migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 