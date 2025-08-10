"""
Favorites database operations
"""
from typing import Optional, List, Dict, Any
from loguru import logger
from .client import supabase


def _apply_search(query, search: Optional[str]):
    if search:
        # Simple ILIKE search on name
        return query.ilike("name", f"%{search}%")
    return query


async def save_favorite_food(
    user_id: str,
    name: str,
    items_json: Dict[str, Any],
    composition_hash: str,
    default_portion: Optional[float] = None,
) -> Dict[str, Any]:
    logger.info(f"Saving favorite for user={user_id}, name={name}")
    record = {
        "user_id": user_id,
        "name": name,
        "items_json": items_json,
        "composition_hash": composition_hash,
    }
    if default_portion is not None:
        record["default_portion"] = default_portion

    try:
        res = supabase.table("favorites_food").insert(record).execute()
        return res.data[0] if res.data else record
    except Exception as e:
        logger.error(f"Failed to save favorite: {e}")
        raise


async def list_favorites(
    user_id: str,
    limit: int = 50,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    logger.info(f"Listing favorites for user={user_id}, limit={limit}, search={search}")
    try:
        query = supabase.table("favorites_food").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit)
        query = _apply_search(query, search)
        res = query.execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Failed to list favorites: {e}")
        return []


async def get_favorite_by_id(user_id: str, favorite_id: str) -> Optional[Dict[str, Any]]:
    try:
        res = supabase.table("favorites_food").select("*").eq("user_id", user_id).eq("id", favorite_id).single().execute()
        return res.data
    except Exception as e:
        logger.error(f"Failed to get favorite {favorite_id} for user {user_id}: {e}")
        return None


async def delete_favorite(user_id: str, favorite_id: str) -> bool:
    try:
        res = supabase.table("favorites_food").delete().eq("user_id", user_id).eq("id", favorite_id).execute()
        deleted = bool(res.data)
        logger.info(f"Deleted favorite {favorite_id} for user {user_id}: {deleted}")
        return deleted
    except Exception as e:
        logger.error(f"Failed to delete favorite {favorite_id} for user {user_id}: {e}")
        return False
