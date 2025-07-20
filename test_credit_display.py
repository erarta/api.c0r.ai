#!/usr/bin/env python3
"""
Test script to check credit display consistency
"""
import asyncio
import sys
import os

# Add paths for imports
sys.path.append('.')
sys.path.append('..')

from common.supabase_client import get_user_with_profile, get_or_create_user

async def test_credit_display():
    """Test credit display for user 7981950009"""
    telegram_user_id = 7981950009
    
    print(f"Testing credit display for user {telegram_user_id}")
    print("=" * 50)
    
    # Test 1: Direct user lookup
    print("1. Direct user lookup:")
    user = await get_or_create_user(telegram_user_id)
    print(f"   User data: {user}")
    print(f"   Credits remaining: {user.get('credits_remaining', 'NOT_FOUND')}")
    print(f"   Credits (wrong field): {user.get('credits', 'NOT_FOUND')}")
    print()
    
    # Test 2: User with profile lookup (used in recipe.py)
    print("2. User with profile lookup (used in recipe.py):")
    user_data = await get_user_with_profile(telegram_user_id)
    user_from_profile = user_data['user']
    print(f"   User data: {user_from_profile}")
    print(f"   Credits remaining: {user_from_profile.get('credits_remaining', 'NOT_FOUND')}")
    print(f"   Credits (wrong field): {user_from_profile.get('credits', 'NOT_FOUND')}")
    print()
    
    # Test 3: Simulate recipe.py credit display logic
    print("3. Simulating recipe.py credit display logic:")
    credits_display_line_137 = user_from_profile.get('credits_remaining', 0)
    credits_display_line_145 = user_from_profile.get('credits_remaining', 0)
    print(f"   Line 137 display: {credits_display_line_137}")
    print(f"   Line 145 display: {credits_display_line_145}")
    print()
    
    # Test 4: Check if there's any data type issue
    print("4. Data type analysis:")
    credits_value = user_from_profile.get('credits_remaining')
    print(f"   Credits value: {credits_value}")
    print(f"   Credits type: {type(credits_value)}")
    print(f"   Credits is None: {credits_value is None}")
    print()

if __name__ == "__main__":
    asyncio.run(test_credit_display())