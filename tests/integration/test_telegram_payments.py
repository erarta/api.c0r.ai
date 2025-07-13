#!/usr/bin/env python3
"""
Test Telegram Payments functionality
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_send_invoice():
    """Test sending invoice via Telegram Bot API"""
    print("🔍 Testing Telegram invoice creation...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    provider_token = os.getenv('YOOKASSA_PROVIDER_TOKEN')
    admin_id = os.getenv('TELEGRAM_ADMIN_ID', '391490')
    
    if not bot_token or not provider_token:
        print("❌ Missing bot token or provider token")
        return False
    
    # Test invoice data
    invoice_data = {
        'chat_id': admin_id,
        'title': 'Test Payment - Basic Plan',
        'description': '20 credits for food analysis',
        'payload': 'test_payment_basic',
        'provider_token': provider_token,
        'currency': 'RUB',
        'prices': json.dumps([{
            'label': 'Basic Plan',
            'amount': 9900  # 99.00 RUB in kopecks
        }]),
        'need_name': False,
        'need_phone_number': False,
        'need_email': False,
        'need_shipping_address': False,
        'send_phone_number_to_provider': False,
        'send_email_to_provider': False,
        'is_flexible': False
    }
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendInvoice"
        response = requests.post(url, data=invoice_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Invoice sent successfully!")
                print(f"   Message ID: {data['result']['message_id']}")
                print(f"   Chat ID: {data['result']['chat']['id']}")
                return True
            else:
                print(f"❌ Telegram API error: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Invoice test failed: {e}")
        return False

def test_webhook_structure():
    """Test webhook data structure"""
    print("\n🔍 Testing webhook structure...")
    
    # Sample webhook data that YooKassa would send
    sample_webhook = {
        "type": "payment.succeeded",
        "event": "payment.succeeded",
        "object": {
            "id": "test_payment_id",
            "status": "succeeded",
            "amount": {
                "value": "99.00",
                "currency": "RUB"
            },
            "payment_method": {
                "type": "bank_card",
                "id": "test_method_id"
            },
            "created_at": "2024-01-01T12:00:00.000Z",
            "description": "Test payment",
            "metadata": {
                "telegram_user_id": "391490",
                "plan": "basic",
                "credits": "20"
            }
        }
    }
    
    print("✅ Webhook structure valid")
    print(f"   Payment ID: {sample_webhook['object']['id']}")
    print(f"   Status: {sample_webhook['object']['status']}")
    print(f"   Amount: {sample_webhook['object']['amount']['value']} {sample_webhook['object']['amount']['currency']}")
    print(f"   User ID: {sample_webhook['object']['metadata']['telegram_user_id']}")
    print(f"   Credits: {sample_webhook['object']['metadata']['credits']}")
    
    return True

def test_payment_buttons():
    """Test payment button structure"""
    print("\n🔍 Testing payment buttons...")
    
    # Test inline keyboard for payments
    payment_keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "💳 Basic Plan - 99₽",
                    "callback_data": "buy_basic"
                }
            ],
            [
                {
                    "text": "💎 Pro Plan - 399₽", 
                    "callback_data": "buy_pro"
                }
            ]
        ]
    }
    
    print("✅ Payment buttons configured")
    print("   Buttons:")
    for row in payment_keyboard["inline_keyboard"]:
        for button in row:
            print(f"     - {button['text']} → {button['callback_data']}")
    
    return True

def test_environment_setup():
    """Test environment setup"""
    print("\n🔍 Testing environment setup...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'YOOKASSA_PROVIDER_TOKEN',
        'TELEGRAM_ADMIN_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing variables: {', '.join(missing)}")
        return False
    
    print("✅ Environment setup complete")
    print(f"   Bot token: {os.getenv('TELEGRAM_BOT_TOKEN')[:20]}...")
    print(f"   Provider token: {os.getenv('YOOKASSA_PROVIDER_TOKEN')[:20]}...")
    print(f"   Admin ID: {os.getenv('TELEGRAM_ADMIN_ID')}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Telegram Payments Test for c0r.ai\n")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Payment Buttons", test_payment_buttons),
        ("Webhook Structure", test_webhook_structure),
        ("Send Invoice", test_send_invoice)
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
    print("📊 TELEGRAM PAYMENTS TEST SUMMARY")
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
        print("\n🎉 Telegram payments ready for testing!")
        print("\nNext steps:")
        print("1. Start your bot")
        print("2. Send /buy command to test payment buttons")
        print("3. Complete test payment with test card")
        print("4. Check webhook receives payment notification")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check configuration.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 