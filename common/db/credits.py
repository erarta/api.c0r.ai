"""
Credits management module for c0r.AI project
Handles credit operations for users
"""

from loguru import logger
from .client import supabase
from .users import get_user_by_telegram_id


async def add_credits(telegram_id: int, count: int = 20):
    """
    Add credits to user's account
    
    Args:
        telegram_id: Telegram user ID
        count: Number of credits to add (default: 20)
        
    Returns:
        Updated user data or None if user not found
    """
    logger.info(f"Adding {count} credits for user {telegram_id}")
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for credit addition")
        return None
    
    old_credits = user["credits_remaining"]
    new_credits = old_credits + count
    logger.info(f"User {telegram_id} credits: {old_credits} -> {new_credits}")
    
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Credits added for user {telegram_id}: {updated}")
    return updated


async def decrement_credits(telegram_id: int, count: int = 1):
    """
    Decrement credits from user's account
    
    Args:
        telegram_id: Telegram user ID
        count: Number of credits to decrement (default: 1)
        
    Returns:
        Updated user data or None if user not found or insufficient credits
    """
    logger.info(f"Decrementing {count} credits for user {telegram_id}")
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for credit decrement")
        return None
    
    old_credits = user["credits_remaining"]
    if old_credits < count:
        logger.error(f"Insufficient credits for user {telegram_id}: {old_credits} < {count}")
        return None
    
    new_credits = old_credits - count
    logger.info(f"User {telegram_id} credits: {old_credits} -> {new_credits}")
    
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Credits decremented for user {telegram_id}: {updated}")
    return updated 