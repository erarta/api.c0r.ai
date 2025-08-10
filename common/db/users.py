"""
User management operations
Handles user creation, credits, language settings, and basic user data
"""
import asyncio
from typing import Optional
from loguru import logger
from .client import supabase


async def get_or_create_user(telegram_id: int, language: Optional[str] = None):
    """
    Get existing user or create new one with initial credits
    
    Args:
        telegram_id: Telegram user ID
        language: User's preferred language (optional)
        
    Returns:
        User data dictionary
    """
    logger.info(f"Getting or creating user for telegram_id: {telegram_id}")
    
    # Search for existing user
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    if user:
        logger.info(f"Found existing user {telegram_id}: {user[0]}")
        return user[0]
    
    # Create new user with 3 initial credits
    data = {"telegram_id": telegram_id, "credits_remaining": 3}
    if language:
        data["language"] = language
    
    logger.info(f"Creating new user {telegram_id} with data: {data}")
    user = supabase.table("users").insert(data).execute().data[0]
    logger.info(f"Created new user {telegram_id}: {user}")
    return user


async def get_user_by_telegram_id(telegram_id: int):
    """
    Get user by Telegram ID
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        User data dictionary or None if not found
    """
    logger.info(f"Getting user by telegram_id: {telegram_id}")
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    result = user[0] if user else None
    logger.info(f"User {telegram_id} query result: {result}")
    return result


async def decrement_credits(telegram_id: int, count: int = 1):
    """
    Decrement user's credits
    
    Args:
        telegram_id: Telegram user ID
        count: Number of credits to decrement (default: 1)
        
    Returns:
        Updated user data or None if user not found
    """
    logger.info(f"Decrementing {count} credits for user {telegram_id}")
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for credit decrement")
        return None
    
    old_credits = user["credits_remaining"]
    new_credits = max(0, old_credits - count)
    logger.info(f"User {telegram_id} credits: {old_credits} -> {new_credits}")
    
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Credits decremented for user {telegram_id}: {updated}")
    return updated


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


async def update_user_language(telegram_id: int, language: str):
    """
    Update user's preferred language
    
    Args:
        telegram_id: Telegram user ID
        language: Language code ('en' or 'ru')
        
    Returns:
        Updated user data or None if invalid language
    """
    logger.info(f"Updating language for user {telegram_id} to {language}")
    
    if language not in ['en', 'ru']:
        logger.error(f"Invalid language code: {language}")
        return None
    
    updated = supabase.table("users").update({"language": language}).eq("telegram_id", telegram_id).execute().data[0]
    logger.info(f"Language updated for user {telegram_id}: {updated}")
    return updated


async def update_user_country_and_phone(telegram_id: int, country: Optional[str] = None, phone_number: Optional[str] = None):
    """
    DEPRECATED: This function is no longer used. Use update_user_language instead.
    """
    logger.warning(f"update_user_country_and_phone is deprecated for user {telegram_id}")
    return None


async def get_user_stats(telegram_id: int):
    """
    Get user statistics (credits, total analyses, etc.)
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        Dictionary with user statistics
    """
    logger.info(f"Getting stats for user {telegram_id}")
    
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logger.error(f"User {telegram_id} not found for stats")
        return None
    
    # Get analysis count from logs
    analysis_count = supabase.table("logs").select("id", count="exact").eq("user_id", user['id']).eq("action_type", "photo_analysis").execute().count
    
    stats = {
        'telegram_id': telegram_id,
        'credits_remaining': user['credits_remaining'],
        'total_analyses': analysis_count or 0,
        'language': user.get('language', 'en'),
        'country': user.get('country'),
        'created_at': user.get('created_at')
    }
    
    logger.info(f"Stats for user {telegram_id}: {stats}")
    return stats