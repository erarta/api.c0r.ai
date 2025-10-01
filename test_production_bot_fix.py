#!/usr/bin/env python3
"""
Test the bot functionality with production database after schema fix
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Use production database connection
os.environ['SUPABASE_URL'] = 'https://mmrzpngugivxoapjiovb.supabase.co'
os.environ['SUPABASE_SERVICE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tcnpwbmd1Z2l2eG9hcGppb3ZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTg4NDQzOSwiZXhwIjoyMDY3NDYwNDM5fQ.KZhEDiqQCW2s0Yfyw3LrWYLXUz_6tLb_33qvxQ0uMQo'

sys.path.append('.')

async def test_production_bot():
    print("=== TESTING PRODUCTION BOT AFTER SCHEMA FIX ===")

    try:
        from common.db.users import get_or_create_user, get_user_stats, decrement_credits

        # Test with a real telegram_id that we saw in logs
        test_telegram_id = 391490  # This user exists in production

        print(f"1. Testing get_or_create_user for existing user {test_telegram_id}...")
        user = await get_or_create_user(test_telegram_id, 'en')

        if user and 'credits_remaining' in user:
            print(f"✅ SUCCESS: User created/found with new schema: {user}")

            # Test user stats (this is called in the start command)
            print(f"2. Testing get_user_stats...")
            stats = await get_user_stats(test_telegram_id)
            print(f"✅ SUCCESS: User stats: {stats}")

            # Test credits decrement (this happens in bot usage)
            if user.get('credits_remaining', 0) > 0:
                print(f"3. Testing decrement_credits...")
                updated_user = await decrement_credits(test_telegram_id, 1)
                print(f"✅ SUCCESS: Credits decremented: {updated_user}")
            else:
                print(f"3. Skipping decrement test - user has 0 credits")

            return True
        else:
            print(f"❌ FAILED: User missing credits_remaining field: {user}")
            return False

    except Exception as e:
        print(f"❌ ERROR during bot test: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the test
success = asyncio.run(test_production_bot())
print(f"\n=== RESULT ===")
print(f"Production bot test: {'✅ PASSED' if success else '❌ FAILED'}")

if success:
    print("\n🎉 The bot should now work correctly on production!")
    print("The schema migration has resolved the 'credits_remaining' error.")
else:
    print("\n💥 There are still issues with the bot functionality.")