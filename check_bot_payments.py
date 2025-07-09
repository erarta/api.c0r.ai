#!/usr/bin/env python3
"""
Check bot payment settings via Telegram API
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def check_bot_payments():
    """Check if bot has payment provider configured"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return
    
    # Check bot info
    print("🔍 Checking bot information...")
    
    async with httpx.AsyncClient() as client:
        # Get bot info
        response = await client.get(f"https://api.telegram.org/bot{token}/getMe")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot: @{bot_info.get('username')}")
                print(f"   Name: {bot_info.get('first_name')}")
                print(f"   Can join groups: {bot_info.get('can_join_groups')}")
                print(f"   Can read messages: {bot_info.get('can_read_all_group_messages')}")
                print(f"   Supports inline: {bot_info.get('supports_inline_queries')}")
            else:
                print(f"❌ Bot API error: {data.get('description')}")
                return
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return
    
    print("\n💡 To get Provider Token:")
    print("1. Go to @BotFather")
    print("2. Send /mybots")
    print("3. Select your bot: @c0rAiBot")
    print("4. Click 'Payments'")
    print("5. Click on YooKassa provider")
    print("6. Look for 'Provider Token' or 'Token' field")
    print("7. Copy the token (format: number:TEST:token)")
    
    print("\n📋 Expected format:")
    print("YOOKASSA_PROVIDER_TOKEN=1234567890:TEST:your_token_here")
    
    # Check if provider token is already set
    provider_token = os.getenv('YOOKASSA_PROVIDER_TOKEN')
    if provider_token:
        print(f"\n✅ Provider token found in .env: {provider_token[:20]}...")
    else:
        print("\n❌ YOOKASSA_PROVIDER_TOKEN not found in .env")

if __name__ == "__main__":
    asyncio.run(check_bot_payments()) 