"""
Supabase utility functions for NeuCor Telegram Bot
"""
import os
from loguru import logger
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Async function to get or create a user by telegram_id
def _user_to_dict(user_row):
    return {
        "id": user_row["id"],
        "telegram_id": user_row["telegram_id"],
        "credits_remaining": user_row["credits_remaining"],
        "total_paid": user_row.get("total_paid", 0),
        "created_at": user_row["created_at"],
    }

async def get_or_create_user(telegram_id: int):
    try:
        # Check if user exists
        res = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        if res.data:
            logger.info(f"User {telegram_id} found in Supabase.")
            return _user_to_dict(res.data[0]), False
        # Insert new user
        new_user = {
            "telegram_id": telegram_id,
            "credits_remaining": 3,
            "total_paid": 0,
        }
        insert_res = supabase.table("users").insert(new_user).execute()
        logger.info(f"User {telegram_id} created in Supabase.")
        return _user_to_dict(insert_res.data[0]), True
    except Exception as e:
        logger.error(f"Supabase error for user {telegram_id}: {e}")
        raise

async def decrement_credits(telegram_id: int):
    try:
        # Fetch current credits
        res = supabase.table("users").select("credits_remaining").eq("telegram_id", telegram_id).execute()
        if not res.data:
            raise ValueError(f"User {telegram_id} not found for credit decrement.")
        credits = res.data[0]["credits_remaining"]
        if credits <= 0:
            raise ValueError(f"User {telegram_id} has no credits to decrement.")
        # Decrement credits
        update_res = supabase.table("users").update({"credits_remaining": credits - 1}).eq("telegram_id", telegram_id).execute()
        logger.info(f"Decremented credits for user {telegram_id}: {credits} -> {credits - 1}")
        return _user_to_dict(update_res.data[0])
    except Exception as e:
        logger.error(f"Error decrementing credits for user {telegram_id}: {e}")
        raise

# Placeholder for Supabase user management functions 