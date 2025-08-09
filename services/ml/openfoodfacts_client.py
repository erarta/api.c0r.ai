from typing import Optional, Dict, Any
import httpx
from loguru import logger


OPENFOODFACTS_BASE = "https://world.openfoodfacts.org/api/v2"


async def fetch_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """Fetch product info from OpenFoodFacts by barcode"""
    url = f"{OPENFOODFACTS_BASE}/product/{barcode}.json"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == 1 and data.get("product"):
                return data["product"]
            return None
    except Exception as e:
        logger.error(f"OpenFoodFacts fetch failed for {barcode}: {e}")
        return None


def map_off_to_nutrition(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map OFF product data to our nutrition structure"""
    nutriments = product.get("nutriments") or {}
    # kcal per 100g from energy-kcal_100g if available, else convert kJ
    kcal_100g = nutriments.get("energy-kcal_100g")
    if kcal_100g is None and "energy_100g" in nutriments:
        # energy_100g in kJ; convert to kcal
        try:
            kcal_100g = float(nutriments["energy_100g"]) / 4.184
        except Exception:
            kcal_100g = None
    try:
        proteins_100g = float(nutriments.get("proteins_100g", 0) or 0)
        fats_100g = float(nutriments.get("fat_100g", 0) or 0)
        carbs_100g = float(nutriments.get("carbohydrates_100g", 0) or 0)
        calories_100g = float(kcal_100g) if kcal_100g is not None else None
    except Exception:
        return None

    if calories_100g is None:
        return None

    # Serving computation fallback
    serving_qty_g = None
    serving_size = product.get("serving_size")  # e.g., "30g"
    if isinstance(serving_size, str) and serving_size.lower().endswith("g"):
        try:
            serving_qty_g = float(serving_size[:-1])
        except Exception:
            serving_qty_g = None

    # Default serving 100g if unknown
    if serving_qty_g is None or serving_qty_g <= 0:
        serving_qty_g = 100.0

    factor = serving_qty_g / 100.0
    calories_per_serving = calories_100g * factor
    proteins_per_serving = proteins_100g * factor
    fats_per_serving = fats_100g * factor
    carbs_per_serving = carbs_100g * factor

    analysis = {
        "analysis": {
            "food_items": [
                {
                    "name": product.get("product_name") or product.get("generic_name") or "Product",
                    "weight_grams": round(serving_qty_g, 1),
                    "calories": round(calories_per_serving, 1),
                    "emoji": "🍽️",
                    "health_benefits": ""
                }
            ],
            "total_nutrition": {
                "calories": round(calories_per_serving, 1),
                "proteins": round(proteins_per_serving, 1),
                "fats": round(fats_per_serving, 1),
                "carbohydrates": round(carbs_per_serving, 1)
            },
            "nutrition_analysis": {
                "health_score": 6
            },
            "provenance": {
                "source": "openfoodfacts",
                "barcode": product.get("code"),
                "serving_size": product.get("serving_size"),
                "per_100g": {
                    "calories": round(calories_100g, 1),
                    "proteins": round(proteins_100g, 1),
                    "fats": round(fats_100g, 1),
                    "carbohydrates": round(carbs_100g, 1)
                }
            }
        }
    }

    return analysis


