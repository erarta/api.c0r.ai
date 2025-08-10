"""
UPCItemDB lookup

Env:
- UPCITEMDB_API_KEY (optional). If missing, provider is skipped.
- UPCITEMDB_BASE (optional) default https://api.upcitemdb.com/prod

Notes:
- UPCItemDB rarely provides nutrition; we map basic name/brand only.
"""
from typing import Optional, Dict, Any
import os
import httpx
from loguru import logger


UPCITEMDB_API_KEY = os.getenv("UPCITEMDB_API_KEY")
UPCITEMDB_BASE = os.getenv("UPCITEMDB_BASE", "https://api.upcitemdb.com/prod")


def is_enabled() -> bool:
    return bool(UPCITEMDB_API_KEY)


async def fetch_product_by_upc(upc: str) -> Optional[Dict[str, Any]]:
    if not is_enabled():
        return None
    url = f"{UPCITEMDB_BASE.rstrip('/')}/v1/lookup?upc={upc}"
    headers = {"user_key": UPCITEMDB_API_KEY}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"UPCItemDB non-200 for {upc}: {resp.status_code}")
                return None
            data = resp.json()
            items = data.get("items") or []
            if not items:
                return None
            return items[0]
    except Exception as e:
        logger.warning(f"UPCItemDB fetch failed for {upc}: {e}")
        return None


def map_upc_to_basic(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not item:
        return None
    name = item.get("title") or item.get("brand") or "Product"
    brand = item.get("brand")
    upc = item.get("upc")
    analysis = {
        "analysis": {
            "food_items": [
                {
                    "name": name,
                    "weight_grams": 100.0,
                    "calories": 0.0,
                    "emoji": "🍽️",
                    "health_benefits": "",
                }
            ],
            "total_nutrition": {"calories": 0.0, "proteins": 0.0, "fats": 0.0, "carbohydrates": 0.0},
            "provenance": {"source": "upcitemdb", "upc": upc, "brand": brand},
        }
    }
    return analysis


