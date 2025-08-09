"""
Saved recipes database operations
"""
from typing import Optional, List, Dict, Any
from loguru import logger
from .client import supabase


def _apply_search(query, search: Optional[str]):
    if search:
        return query.ilike("title", f"%{search}%")
    return query


async def save_recipe(
    user_id: str,
    title: str,
    recipe_json: Dict[str, Any],
    language: str = "en",
    source: Optional[str] = None,
) -> Dict[str, Any]:
    logger.info(f"Saving recipe for user={user_id}, title={title}")
    record = {
        "user_id": user_id,
        "title": title,
        "language": language,
        "recipe_json": recipe_json,
    }
    if source:
        record["source"] = source

    try:
        res = supabase.table("saved_recipes").insert(record).execute()
        return res.data[0] if res.data else record
    except Exception as e:
        logger.error(f"Failed to save recipe: {e}")
        raise


async def list_recipes(
    user_id: str,
    limit: int = 50,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    logger.info(f"Listing recipes for user={user_id}, limit={limit}, search={search}")
    try:
        query = supabase.table("saved_recipes").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit)
        query = _apply_search(query, search)
        res = query.execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Failed to list recipes: {e}")
        return []


async def get_recipe_by_id(user_id: str, recipe_id: str) -> Optional[Dict[str, Any]]:
    try:
        res = supabase.table("saved_recipes").select("*").eq("user_id", user_id).eq("id", recipe_id).single().execute()
        return res.data
    except Exception as e:
        logger.error(f"Failed to get recipe {recipe_id} for user {user_id}: {e}")
        return None


async def delete_recipe(user_id: str, recipe_id: str) -> bool:
    try:
        res = supabase.table("saved_recipes").delete().eq("user_id", user_id).eq("id", recipe_id).execute()
        deleted = bool(res.data)
        logger.info(f"Deleted recipe {recipe_id} for user {user_id}: {deleted}")
        return deleted
    except Exception as e:
        logger.error(f"Failed to delete recipe {recipe_id} for user {user_id}: {e}")
        return False
