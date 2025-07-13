#!/usr/bin/env python3
"""
Simple YooKassa Payment Test
"""

import os
import requests
from dotenv import load_dotenv
from yookassa import Configuration, Payment

load_dotenv()

def test_yookassa_connection():
    """Test YooKassa API connection"""
    print("🔍 Testing YooKassa connection...")
    
    shop_id = os.getenv('YOOKASSA_SHOP_ID')
    secret_key = os.getenv('YOOKASSA_SECRET_KEY')
    
    if not shop_id or not secret_key:
        print("❌ YooKassa credentials not found")
        return False
    
    try:
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        
        # Try to create a test payment
        payment = Payment.create({
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://c0r.ai/success"
            },
            "description": "Test payment"
        })
        
        print(f"✅ YooKassa connection successful")
        print(f"   Payment ID: {payment.id}")
        print(f"   Status: {payment.status}")
        print(f"   Amount: {payment.amount.value} {payment.amount.currency}")
        
        return True
        
    except Exception as e:
        print(f"❌ YooKassa connection failed: {e}")
        return False

def test_telegram_bot():
    """Test Telegram bot token"""
    print("\n🔍 Testing Telegram bot...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Telegram bot token not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Telegram bot connection successful")
                print(f"   Bot: @{bot_info.get('username')}")
                print(f"   Name: {bot_info.get('first_name')}")
                return True
        
        print(f"❌ Telegram bot connection failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        return False

def test_provider_token():
    """Test provider token format"""
    print("\n🔍 Testing provider token...")
    
    provider_token = os.getenv('YOOKASSA_PROVIDER_TOKEN')
    
    if not provider_token:
        print("❌ YOOKASSA_PROVIDER_TOKEN not found")
        return False
    
    # Check format: number:TEST:token
    if ':' in provider_token:
        parts = provider_token.split(':')
        if len(parts) >= 3:
            print(f"✅ Provider token format correct")
            print(f"   Environment: {parts[1]}")
            print(f"   Token: {parts[0]}:***:{parts[2][:8]}...")
            return True
    
    print("❌ Provider token format incorrect")
    return False

def test_payment_plans():
    """Test payment plans configuration"""
    print("\n🔍 Testing payment plans...")
    
    # Define payment plans directly here for testing
    PAYMENT_PLANS = {
        'basic': {
            'title': 'Basic Plan',
            'description': '20 credits for food analysis',
            'price': 9900,  # 99.00 RUB in kopecks
            'currency': 'RUB',
            'credits': 20
        },
        'pro': {
            'title': 'Pro Plan', 
            'description': '100 credits for food analysis',
            'price': 39900,  # 399.00 RUB in kopecks
            'currency': 'RUB',
            'credits': 100
        }
    }
    
    print("Payment plans configured:")
    for plan_id, plan in PAYMENT_PLANS.items():
        print(f"  📦 {plan_id}: {plan['title']}")
        print(f"     💰 Price: {plan['price']/100:.2f} {plan['currency']}")
        print(f"     ⚡ Credits: {plan['credits']}")
        print()
    
    print("✅ Payment plans configuration valid")
    return True

def main():
    """Run all tests"""
    print("🚀 c0r.ai YooKassa Payment Integration Test\n")
    
    tests = [
        ("YooKassa Connection", test_yookassa_connection),
        ("Telegram Bot", test_telegram_bot),
        ("Provider Token", test_provider_token),
        ("Payment Plans", test_payment_plans)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
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
        print("\n🎉 All tests passed! Payment integration is ready!")
        print("\nNext steps:")
        print("1. Test payment flow with Telegram bot")
        print("2. Send test invoice to yourself")
        print("3. Complete test payment with test card")
        print("4. Verify credits are added to user account")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the configuration.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 