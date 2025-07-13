#!/usr/bin/env python3
"""
YooKassa Integration Test Script
Tests all components of YooKassa integration for c0r.ai bot
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')
sys.path.append('./api.c0r.ai/app')
sys.path.append('./common')

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'YOOKASSA_SHOP_ID', 
        'YOOKASSA_SECRET_KEY',
        'YOOKASSA_PROVIDER_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_yookassa_sdk():
    """Test YooKassa SDK configuration"""
    print("\n🔍 Testing YooKassa SDK...")
    
    try:
        from yookassa import Configuration, Payment
        
        shop_id = os.getenv('YOOKASSA_SHOP_ID')
        secret_key = os.getenv('YOOKASSA_SECRET_KEY')
        
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        
        print("✅ YooKassa SDK configured successfully")
        return True
        
    except ImportError:
        print("❌ YooKassa SDK not installed. Run: pip install yookassa")
        return False
    except Exception as e:
        print(f"❌ YooKassa SDK configuration failed: {e}")
        return False

def test_telegram_bot_token():
    """Test Telegram bot token"""
    print("\n🔍 Testing Telegram bot token...")
    
    try:
        import httpx
        import asyncio
        
        async def check_bot():
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            url = f"https://api.telegram.org/bot{token}/getMe"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        print(f"✅ Bot token valid: @{bot_info.get('username', 'unknown')}")
                        return True
                    else:
                        print(f"❌ Bot API error: {data.get('description', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    return False
        
        return asyncio.run(check_bot())
        
    except Exception as e:
        print(f"❌ Telegram bot token test failed: {e}")
        return False

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from common.supabase_client import get_or_create_user
        
        # Test with a dummy user ID
        test_user_id = 123456789
        user = await get_or_create_user(test_user_id)
        
        if user:
            print(f"✅ Supabase connection successful")
            print(f"   User ID: {user.get('telegram_id')}")
            print(f"   Credits: {user.get('credits_remaining')}")
            return True
        else:
            print("❌ Supabase connection failed: No user returned")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_payment_plans():
    """Test payment plans configuration"""
    print("\n🔍 Testing payment plans...")
    
    try:
        from api.c0r.ai.app.handlers.payments import PAYMENT_PLANS
        
        print("Payment plans configured:")
        for plan_id, plan in PAYMENT_PLANS.items():
            print(f"  📦 {plan_id}: {plan['title']}")
            print(f"     💰 Price: {plan['price']/100:.2f} {plan['currency']}")
            print(f"     ⚡ Credits: {plan['credits']}")
            print()
        
        print("✅ Payment plans configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Payment plans test failed: {e}")
        return False

def test_provider_token_format():
    """Test provider token format"""
    print("\n🔍 Testing provider token format...")
    
    provider_token = os.getenv('YOOKASSA_PROVIDER_TOKEN')
    
    if not provider_token:
        print("❌ YOOKASSA_PROVIDER_TOKEN not set")
        return False
    
    # Provider token should be in format: number:TEST:token or number:LIVE:token
    if ':' in provider_token:
        parts = provider_token.split(':')
        if len(parts) >= 3:
            print(f"✅ Provider token format looks correct")
            print(f"   Environment: {parts[1]}")
            return True
    
    print("❌ Provider token format incorrect. Should be: number:TEST:token")
    return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting YooKassa Integration Tests for c0r.ai\n")
    
    tests = [
        ("Environment Variables", check_environment_variables),
        ("YooKassa SDK", test_yookassa_sdk),
        ("Telegram Bot Token", test_telegram_bot_token),
        ("Supabase Connection", test_supabase_connection),
        ("Payment Plans", test_payment_plans),
        ("Provider Token Format", test_provider_token_format)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! YooKassa integration is ready!")
        print("\nNext steps:")
        print("1. Deploy your bot to production")
        print("2. Test payment flow with real users")
        print("3. Monitor logs for any issues")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before deployment.")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 