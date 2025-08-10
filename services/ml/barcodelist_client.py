"""
barcode-list.ru lookup (RU)

Public web page with query param `?barcode=GTIN`.
We fetch and heuristically parse HTML to extract a product title if present.
Falls back to basic metadata if parsing fails.
"""
from typing import Optional, Dict, Any
import httpx
from loguru import logger
import urllib.parse
import re


BASE = "https://barcode-list.ru/barcode/RU/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm"


async def fetch_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    try:
        params = {"barcode": barcode}
        url = f"{BASE}?{urllib.parse.urlencode(params)}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning(f"barcodelist non-200 for {barcode}: {resp.status_code}")
                return None
            html = resp.text
            # Heuristic: try <title>...</title>
            m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = None
            if m:
                title = re.sub(r"\s+", " ", m.group(1)).strip()
                # Remove site suffixes
                title = re.sub(r"\s*\|.*$", "", title)
            # Also try a common pattern where product name appears in <h1>
            if not title:
                m2 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
                if m2:
                    title = re.sub(r"<[^>]+>", "", m2.group(1))
                    title = re.sub(r"\s+", " ", title).strip()
            if not title:
                return {"barcode": barcode, "title": None, "raw": None}
            return {"barcode": barcode, "title": title, "raw": None}
    except Exception as e:
        logger.warning(f"barcodelist fetch failed for {barcode}: {e}")
        return None


def map_barcodelist_to_basic(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    name = doc.get("title") or "Product"
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
            "provenance": {"source": "barcodelist", "barcode": doc.get("barcode")},
        }
    }
    return analysis


