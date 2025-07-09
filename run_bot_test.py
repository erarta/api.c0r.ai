#!/usr/bin/env python3
"""
Run bot for testing payments
"""

import sys
import os
sys.path.append('./api.c0r.ai/app')

from dotenv import load_dotenv
load_dotenv()

# Import bot components
from bot import main

if __name__ == "__main__":
    print("🚀 Starting c0r.ai bot for payment testing...")
    print("📋 Available commands:")
    print("   /start - Start bot")
    print("   /help - Show help")
    print("   /status - Check credits")
    print("   /buy - Show payment options")
    print("   Send photo - Analyze food")
    print("\n💳 Payment testing:")
    print("   1. Send /buy command")
    print("   2. Choose payment plan")
    print("   3. Complete payment with test card")
    print("   4. Check credits added")
    print("\n🧪 Test cards:")
    print("   Card: 4111 1111 1111 1111")
    print("   Expiry: 12/25")
    print("   CVV: 123")
    print("\n🔄 Starting bot...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1) 