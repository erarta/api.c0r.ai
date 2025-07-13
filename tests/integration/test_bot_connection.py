#!/usr/bin/env python3
"""
Quick Telegram Bot Connection Test
Tests if bot token is valid and bot is accessible
"""

import os
import asyncio
import httpx
from aiogram import Bot

async def test_bot_connection():
    """Test Telegram bot connection"""
    print("🤖 Testing Telegram Bot Connection...")
    
    # Check if token is set
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return False
    
    print(f"✅ Token found: {token[:10]}...{token[-10:]}")
    
    try:
        # Create bot instance
        bot = Bot(token=token)
        
        # Test 1: Get bot info
        print("\n1️⃣ Testing bot info...")
        me = await bot.get_me()
        print(f"✅ Bot info: @{me.username} ({me.first_name})")
        print(f"   Bot ID: {me.id}")
        print(f"   Can join groups: {me.can_join_groups}")
        print(f"   Can read messages: {me.can_read_all_group_messages}")
        
        # Test 2: Check webhook status
        print("\n2️⃣ Testing webhook status...")
        webhook_info = await bot.get_webhook_info()
        print(f"✅ Webhook URL: {webhook_info.url or 'Not set (polling mode)'}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        
        # Test 3: Test API endpoint directly
        print("\n3️⃣ Testing API endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            if response.status_code == 200:
                print("✅ Direct API access successful")
            else:
                print(f"❌ Direct API access failed: {response.status_code}")
        
        print("\n🎉 Bot connection test successful!")
        print(f"Your bot @{me.username} is ready to use!")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Bot connection test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "SUPABASE_URL", 
        "SUPABASE_KEY",
        "ML_SERVICE_URL"
    ]
    
    missing = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            missing.append(var)
            print(f"❌ {var} is missing")
    
    if missing:
        print(f"\n❌ Missing variables: {missing}")
        return False
    
    print("\n✅ All environment variables are set!")
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Bot Connection Tests...\n")
    
    # Test environment first
    if not test_environment():
        print("\n❌ Please set missing environment variables in .env file")
        return
    
    # Test bot connection
    if await test_bot_connection():
        print("\n✅ All tests passed! Bot is ready for production testing.")
        print("\n📱 Next steps:")
        print("1. Start monitoring: ./monitor_bot.sh errors")
        print("2. Start bot: docker-compose up -d")
        print("3. Test in Telegram: /start")
    else:
        print("\n❌ Bot connection tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 