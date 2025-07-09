import os
from supabase import create_client, Client
import asyncio
from typing import Optional
from loguru import logger

# Must be set in .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# USERS
async def get_or_create_user(telegram_id: int, country: Optional[str] = None):
    logger.info(f"Getting or creating user for telegram_id: {telegram_id}")
    # Поиск пользователя
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    if user:
        logger.info(f"Found existing user {telegram_id}: {user[0]}")
        return user[0]
    # Создание пользователя с 3 кредитами
    data = {"telegram_id": telegram_id, "credits_remaining": 3}
    if country:
        data["country"] = country
    logger.info(f"Creating new user {telegram_id} with data: {data}")
    user = supabase.table("users").insert(data).execute().data[0]
    logger.info(f"Created new user {telegram_id}: {user}")
    return user

async def get_user_by_telegram_id(telegram_id: int):
    logger.info(f"Getting user by telegram_id: {telegram_id}")
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    result = user[0] if user else None
    logger.info(f"User {telegram_id} query result: {result}")
    return result

async def decrement_credits(telegram_id: int, count: int = 1):
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

# LOGS
async def log_analysis(user_id: str, photo_url: str, kbzhu: dict, model_used: str):
    logger.info(f"Logging analysis for user {user_id}")
    log = {
        "user_id": user_id,
        "photo_url": photo_url,
        "kbzhu": kbzhu,
        "model_used": model_used
    }
    supabase.table("logs").insert(log).execute()
    logger.info(f"Analysis logged for user {user_id}")
    return True

# PAYMENTS
async def add_payment(user_id: str, amount: float, gateway: str, status: str):
    logger.info(f"Adding payment record for user {user_id}: {amount} via {gateway}")
    payment = {
        "user_id": user_id,
        "amount": amount,
        "gateway": gateway,
        "status": status
    }
    supabase.table("payments").insert(payment).execute()
    logger.info(f"Payment recorded for user {user_id}")
    return True 