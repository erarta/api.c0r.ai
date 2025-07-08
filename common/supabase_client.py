import os
from supabase import create_client, Client
import asyncio
from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# USERS
async def get_or_create_user(telegram_id: int, country: Optional[str] = None):
    # Поиск пользователя
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    if user:
        return user[0]
    # Создание пользователя с 3 кредитами
    data = {"telegram_id": telegram_id, "credits_remaining": 3}
    if country:
        data["country"] = country
    user = supabase.table("users").insert(data).execute().data[0]
    return user

async def get_user_by_telegram_id(telegram_id: int):
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute().data
    return user[0] if user else None

async def decrement_credits(telegram_id: int, count: int = 1):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        return None
    new_credits = max(0, user["credits_remaining"] - count)
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    return updated

async def add_credits(telegram_id: int, count: int = 20):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        return None
    new_credits = user["credits_remaining"] + count
    updated = supabase.table("users").update({"credits_remaining": new_credits}).eq("telegram_id", telegram_id).execute().data[0]
    return updated

# LOGS
async def log_analysis(user_id: str, photo_url: str, kbzhu: dict, model_used: str):
    log = {
        "user_id": user_id,
        "photo_url": photo_url,
        "kbzhu": kbzhu,
        "model_used": model_used
    }
    supabase.table("logs").insert(log).execute()
    return True

# PAYMENTS
async def add_payment(user_id: str, amount: float, gateway: str, status: str):
    payment = {
        "user_id": user_id,
        "amount": amount,
        "gateway": gateway,
        "status": status
    }
    supabase.table("payments").insert(payment).execute()
    return True 