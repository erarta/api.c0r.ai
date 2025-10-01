#!/usr/bin/env python3
"""
Test production database connection and schema
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load production environment
env_file = Path(__file__).parent / ".env.production"
print(f"Loading production environment from: {env_file}")
load_dotenv(env_file)

print("=== PRODUCTION DATABASE TEST ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

try:
    # Import our modules
    sys.path.append('.')
    from common.db.client import supabase

    print("✅ Successfully imported supabase client")

    # Test connection and check schema
    result = supabase.table('users').select('*').limit(1).execute()
    print(f"✅ Query successful: {len(result.data)} rows returned")

    if result.data:
        print(f"Production schema: {list(result.data[0].keys())}")
        print(f"Sample user: {result.data[0]}")

        # Check if we have the required columns
        required_cols = ['id', 'telegram_id', 'credits_remaining', 'language']
        actual_cols = list(result.data[0].keys())

        missing = [col for col in required_cols if col not in actual_cols]
        if missing:
            print(f"❌ Missing required columns: {missing}")
        else:
            print("✅ All required columns present")
    else:
        print("Table is empty")

    # Test user creation (what the bot does on /start)
    print("\n=== TESTING BOT FUNCTIONS ===")
    import asyncio
    from common.db.users import get_or_create_user

    async def test_user_creation():
        test_user = await get_or_create_user(888888888, 'en')
        print(f"Test user creation: {test_user}")
        return test_user is not None

    success = asyncio.run(test_user_creation())
    print(f"Bot function test: {'✅ PASSED' if success else '❌ FAILED'}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()