"""
Minimal Chestny ZNAK (CRPT) lookup for GTIN (barcode) → product metadata.

Notes:
- Public API options are limited; production access requires CRPT org credentials.
- We implement a best-effort GET to the public catalog endpoint for basic metadata.
- Nutrition is typically unavailable; we return name/brand and provenance only.

Env:
- CHESTNYZNAK_ENABLED=true|false
- CHESTNYZNAK_BASE=https://ismp.crpt.ru (default uses public catalog gateway)
"""
from typing import Optional, Dict, Any
import os
import httpx
from loguru import logger


CHESTNYZNAK_ENABLED = os.getenv("CHESTNYZNAK_ENABLED", "false").lower() == "true"
CHESTNYZNAK_BASE = os.getenv("CHESTNYZNAK_BASE", "https://ismp.crpt.ru")


async def fetch_product_by_gtin(gtin: str) -> Optional[Dict[str, Any]]:
    if not CHESTNYZNAK_ENABLED:
        return None
    # Public endpoint for catalog search by GTIN (subject to change/limits)
    # Fallback to demo endpoint if base unavailable
    paths = [
        f"/api/v3/reestr/gtin/{gtin}",  # common style
        f"/reestr/gtin/{gtin}",         # alt style
        f"/v1/reestr/gtin/{gtin}",      # legacy style
    ]
    async with httpx.AsyncClient(timeout=10) as client:
        for p in paths:
            url = f"{CHESTNYZNAK_BASE.rstrip('/')}{p}"
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Normalize a simple shape
                    if isinstance(data, dict) and data:
                        return {
                            "gtin": gtin,
                            "product_name": data.get("product_name") or data.get("name") or data.get("goods_name"),
                            "brand": data.get("brand") or data.get("trademark"),
                            "owner": data.get("owner_name") or data.get("producer_name"),
                            "raw": data,
                        }
            except Exception as e:
                logger.warning(f"ChestnyZNAK fetch failed for {gtin} via {url}: {e}")
    return None


def map_cz_to_basic(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not product:
        return None
    name = product.get("product_name") or product.get("raw", {}).get("product_name") or "Product"
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
            "total_nutrition": {
                "calories": 0.0,
                "proteins": 0.0,
                "fats": 0.0,
                "carbohydrates": 0.0,
            },
            "provenance": {
                "source": "chestnyznak",
                "gtin": product.get("gtin"),
                "owner": product.get("owner"),
                "brand": product.get("brand"),
            },
        }
    }
    return analysis


