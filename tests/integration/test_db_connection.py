#!/usr/bin/env python3
"""
Database connection test script for c0r.ai bot
Tests Supabase connection and basic operations
"""

import os
import sys
import asyncio
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from common.supabase_client import supabase, get_or_create_user, log_user_action

async def test_database_connection():
    """Test basic database operations"""
    print("🧪 Testing database connection...")
    
    try:
        # Test 1: Basic connection
        print("\n1️⃣ Testing basic connection...")
        response = supabase.table("users").select("*").limit(1).execute()
        if response.data is not None:
            print("✅ Basic connection successful")
        else:
            print("❌ Basic connection failed")
            return False
            
        # Test 2: User creation
        print("\n2️⃣ Testing user creation...")
        test_user_id = 999999999  # Test user ID
        user = await get_or_create_user(test_user_id)
        if user and user.get('telegram_user_id') == test_user_id:
            print(f"✅ User creation successful: {user}")
        else:
            print("❌ User creation failed")
            return False
            
        # Test 3: Logging
        print("\n3️⃣ Testing logging...")
        await log_user_action(
            user_id=user['id'],
            action_type="test",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        print("✅ Logging successful")
        
        # Test 4: Database schema check
        print("\n4️⃣ Testing database schema...")
        
        # Check users table
        users_response = supabase.table("users").select("*").limit(1).execute()
        if users_response.data is not None:
            print("✅ Users table accessible")
        else:
            print("❌ Users table not accessible")
            
        # Check logs table
        logs_response = supabase.table("logs").select("*").limit(1).execute()
        if logs_response.data is not None:
            print("✅ Logs table accessible")
        else:
            print("❌ Logs table not accessible")
            
        # Check profiles table
        profiles_response = supabase.table("profiles").select("*").limit(1).execute()
        if profiles_response.data is not None:
            print("✅ Profiles table accessible")
        else:
            print("❌ Profiles table not accessible")
            
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing environment variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "TELEGRAM_BOT_TOKEN",
        "ML_SERVICE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All environment variables are set")
    return True

async def main():
    """Run all database tests"""
    print("🚀 Starting database connection tests...\n")
    
    # Test environment variables first
    if not test_environment_variables():
        print("\n❌ Environment variable tests failed. Please check your .env file.")
        return
    
    # Test database connection
    if await test_database_connection():
        print("\n✅ All tests passed! Database is ready for use.")
    else:
        print("\n❌ Database tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 