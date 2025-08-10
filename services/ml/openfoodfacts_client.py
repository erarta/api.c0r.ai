from typing import Optional, Dict, Any, List, Tuple
import re
import httpx
from loguru import logger
import time


OPENFOODFACTS_BASE = "https://world.openfoodfacts.org/api/v2"

_http_client: Optional[httpx.AsyncClient] = None

async def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(http2=True, timeout=10)
    return _http_client


async def fetch_product_by_barcode(barcode: str, timeout_sec: float = 5.0) -> Optional[Dict[str, Any]]:
    """Fetch product info from OpenFoodFacts by barcode"""
    url = f"{OPENFOODFACTS_BASE}/product/{barcode}.json"
    try:
        client = await _get_client()
        resp = await client.get(url, timeout=max(2.0, timeout_sec))
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == 1 and data.get("product"):
            return data["product"]
        return None
    except Exception as e:
        logger.error(f"OpenFoodFacts fetch failed for {barcode}: {e}")
        return None


def _clean_name_for_off(name: str) -> List[str]:
    s = re.sub(r"\s*-?\s*штрих[^\n\r]*$", "", name, flags=re.IGNORECASE).strip()
    s = re.sub(r"\d{8,}", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    alpha = re.sub(r"[0-9%]+", " ", s)
    alpha = re.sub(r"\b(гр|г|kg|кг|ml|мл|пр|pct|percent)\b", " ", alpha, flags=re.IGNORECASE)
    alpha = re.sub(r"\s+", " ", alpha).strip()
    words = alpha.split()
    short = " ".join(words[:4]) if words else alpha
    variants = []
    for v in [s, alpha, short]:
        if v and v not in variants:
            variants.append(v)
    return variants


async def fetch_product_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Search OpenFoodFacts by product name and return the best product with nutriments."""
    if not name:
        return None


async def fetch_best_product_by_names(
    names: List[str],
    timeout_sec: float = 6.0,
    page_size: int = 10,
    deadline_ts: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Try multiple names using OFF search endpoints; pick best product with nutriments.
    Uses both API v2 /search and legacy /cgi/search.pl to improve recall.
    """
    if not names:
        return None
    fields = "code,product_name,brands,nutriments,serving_size,categories,nova_group,nutriscore_grade,ingredients_text,allergens_tags,additives_tags"
    v2_url = f"{OPENFOODFACTS_BASE}/search"
    cgi_url = "https://world.openfoodfacts.org/cgi/search.pl"

    def tokenize(text: str) -> List[str]:
        t = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in t.split() if len(w) >= 2]

    def score_product(product: Dict[str, Any], query: str) -> Tuple[int, int, int]:
        # Higher is better: (nutriments_present, token_hits, name_len)
        nutr = product.get("nutriments") or {}
        nutr_present = int(any(k in nutr for k in (
            "energy-kcal_100g", "energy_100g", "proteins_100g", "fat_100g", "carbohydrates_100g"
        )))
        tokens = set(tokenize(query))
        in_name = tokenize(product.get("product_name") or "")
        in_brands = tokenize(product.get("brands") or "")
        token_hits = len(tokens.intersection(set(in_name + in_brands)))
        name_len = len(in_name)
        return nutr_present, token_hits, name_len

    try:
        client = await _get_client()
        best: Optional[Dict[str, Any]] = None
        best_score: Tuple[int, int, int] = (0, 0, 0)
        for raw in names:
            for q in _clean_name_for_off(raw):
                # Respect overall deadline if provided
                if deadline_ts is not None and time.monotonic() >= deadline_ts:
                    logger.info("[OFF] Deadline reached before search; returning best so far")
                    return best
                # 1) v2 search (prefer RU if Cyrillic present)
                langs = ("ru",) if re.search(r"[А-Яа-я]", q) else ("en", "ru")
                for lang in langs:
                    if deadline_ts is not None and time.monotonic() >= deadline_ts:
                        return best
                    params = {"search_terms": q, "page_size": page_size, "fields": fields, "search_simple": 1, "lang": lang}
                    logger.info(f"[OFF] v2 search q='{q}' lang={lang}")
                    try:
                        remaining = None
                        if deadline_ts is not None:
                            remaining = max(0.5, deadline_ts - time.monotonic())
                        r = await client.get(v2_url, params=params, timeout=min(max(2.0, timeout_sec), remaining) if remaining else max(2.0, timeout_sec))
                        r.raise_for_status()
                        products = (r.json().get("products") or [])
                        for p in products:
                            s = score_product(p, q)
                            if s > best_score:
                                best, best_score = p, s
                                if best_score[0] == 1 and best_score[1] >= 1:
                                    return best
                    except Exception as e:
                        logger.warning(f"[OFF] v2 search failed for '{q}' lang={lang}: {e}")
                # 2) legacy CGI search
                params2 = {
                    "search_terms": q,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1,
                    "page_size": page_size,
                    "fields": fields,
                }
                logger.info(f"[OFF] cgi search q='{q}'")
                try:
                    remaining = None
                    if deadline_ts is not None:
                        remaining = max(0.5, deadline_ts - time.monotonic())
                    r2 = await client.get(cgi_url, params=params2, timeout=min(max(2.0, timeout_sec), remaining) if remaining else max(2.0, timeout_sec))
                    r2.raise_for_status()
                    products2 = (r2.json().get("products") or [])
                    for p in products2:
                        s = score_product(p, q)
                        if s > best_score:
                            best, best_score = p, s
                            if best_score[0] == 1 and best_score[1] >= 1:
                                return best
                except Exception as e:
                    logger.warning(f"[OFF] cgi search failed for '{q}': {e}")
        return best
    except Exception as e:
        logger.error(f"OpenFoodFacts combined name search failed: {e}")
        return None
    url = f"{OPENFOODFACTS_BASE}/search"
    fields = "code,product_name,nutriments,serving_size"
    queries = _clean_name_for_off(name)
    try:
        client = await _get_client()
        for q in queries:
            for lang in ("ru", "en"):
                params = {
                    "search_terms": q,
                    "page_size": 5,
                    "fields": fields,
                    "search_simple": 1,
                    "lang": lang,
                }
                logger.info(f"[OFF] Name search: '{q}' lang={lang}")
                resp = await client.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                products = data.get("products") or []
                logger.info(f"[OFF] Results for '{q}' lang={lang}: {len(products)}")
                for p in products:
                    nutr = p.get("nutriments") or {}
                    if any(k in nutr for k in ("energy-kcal_100g", "energy_100g", "proteins_100g", "fat_100g", "carbohydrates_100g")):
                        logger.info(f"[OFF] Chosen product: {p.get('product_name')}")
                        return p
        # Legacy RU endpoint fallback
        legacy_url = "https://ru.openfoodfacts.org/cgi/search.pl"
        for q in queries:
            params = {
                "search_terms": q,
                "search_simple": 1,
                "json": 1,
                "page_size": 10,
                "fields": fields,
            }
            logger.info(f"[OFF-legacy] Name search: '{q}'")
            resp = await client.get(legacy_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            products = data.get("products") or []
            logger.info(f"[OFF-legacy] Results for '{q}': {len(products)}")
            for p in products:
                nutr = p.get("nutriments") or {}
                if any(k in nutr for k in ("energy-kcal_100g", "energy_100g", "proteins_100g", "fat_100g", "carbohydrates_100g")):
                    logger.info(f"[OFF-legacy] Chosen product: {p.get('product_name')}")
                    return p
    except Exception as e:
        logger.error(f"OpenFoodFacts name search failed for '{name}': {e}")
        return None


def _parse_serving_qty_grams(serving_size: Optional[str]) -> Optional[float]:
    if not isinstance(serving_size, str):
        return None
    s = serving_size.strip().lower()
    # Patterns like "30g", "30 g", "30gr", "30 ml"
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(g|gr|ml)", s)
    if not m:
        return None
    qty = float(m.group(1))
    unit = m.group(2)
    if unit in ("g", "gr"):
        return qty
    if unit == "ml":
        # Approximate 1 ml ~= 1 g when density unknown
        return qty
    return None


def _get_per100g(nutriments: Dict[str, Any], key: str, factor: Optional[float]) -> Optional[float]:
    # Try per 100g
    v = nutriments.get(f"{key}_100g")
    if v is not None:
        try:
            return float(v)
        except Exception:
            pass
    # Try per serving and back-calc
    if factor and factor > 0:
        v = nutriments.get(f"{key}_serving")
        if v is not None:
            try:
                return float(v) / factor
            except Exception:
                pass
    # Try plain key (some entries expose e.g. carbohydrates without suffix)
    v = nutriments.get(key)
    if v is not None:
        try:
            return float(v)
        except Exception:
            pass
    return None


def map_off_to_nutrition(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map OFF product data to our nutrition structure"""
    nutriments = product.get("nutriments") or {}

    # Serving quantity (grams). Used to compute per-serving values.
    serving_qty_g = _parse_serving_qty_grams(product.get("serving_size"))
    if not serving_qty_g or serving_qty_g <= 0:
        serving_qty_g = 100.0
    factor = serving_qty_g / 100.0

    # Calories/macros per 100g
    proteins_100g = _get_per100g(nutriments, "proteins", factor) or 0.0
    fats_100g = _get_per100g(nutriments, "fat", factor) or 0.0
    carbs_100g = _get_per100g(nutriments, "carbohydrates", factor) or 0.0
    kcal_100g = _get_per100g(nutriments, "energy-kcal", factor)
    if kcal_100g is None:
        # Fall back to kJ keys
        kj_100g = _get_per100g(nutriments, "energy", factor)
        if kj_100g is not None:
            try:
                kcal_100g = float(kj_100g) / 4.184
            except Exception:
                kcal_100g = None
    # If still unknown, estimate from macros if present
    if kcal_100g is None and any([proteins_100g, fats_100g, carbs_100g]):
        try:
            kcal_100g = 4.0 * float(proteins_100g) + 9.0 * float(fats_100g) + 4.0 * float(carbs_100g)
            logger.info("[OFF] Estimated kcal_100g from macros")
        except Exception:
            kcal_100g = None

    if kcal_100g is None:
        return None

    # Extra micronutrients
    satfat_100g = _get_per100g(nutriments, "saturated-fat", factor) or 0.0
    sugars_100g = _get_per100g(nutriments, "sugars", factor) or 0.0
    fiber_100g = _get_per100g(nutriments, "fiber", factor) or 0.0
    salt_100g = _get_per100g(nutriments, "salt", factor)
    if salt_100g is None:
        sodium_100g = _get_per100g(nutriments, "sodium", factor)
        salt_100g = float(sodium_100g) * 2.5 if sodium_100g is not None else 0.0

    calories_per_serving = float(kcal_100g) * factor
    proteins_per_serving = float(proteins_100g) * factor
    fats_per_serving = float(fats_100g) * factor
    carbs_per_serving = float(carbs_100g) * factor
    satfat_per_serving = float(satfat_100g) * factor
    sugars_per_serving = float(sugars_100g) * factor
    fiber_per_serving = float(fiber_100g) * factor
    salt_per_serving = float(salt_100g) * factor

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
                "carbohydrates": round(carbs_per_serving, 1),
                "saturated_fat": round(satfat_per_serving, 1),
                "sugars": round(sugars_per_serving, 1),
                "fiber": round(fiber_per_serving, 1),
                "salt": round(salt_per_serving, 2)
            },
            "nutrition_analysis": {
                "health_score": 6
            },
            "provenance": {
                "source": "openfoodfacts",
                "barcode": product.get("code"),
                "serving_size": product.get("serving_size"),
                "brand": product.get("brands"),
                "product_name": product.get("product_name"),
                "categories": product.get("categories"),
                "quantity": product.get("quantity"),
                "labels": product.get("labels"),
                "countries": product.get("countries"),
                "nova_group": product.get("nova_group"),
                "nutriscore_grade": product.get("nutriscore_grade"),
                "ingredients": product.get("ingredients_text"),
                "allergens": product.get("allergens_tags"),
                "additives": product.get("additives_tags"),
                 "per_100g": {
                    "calories": round(float(kcal_100g), 1),
                    "proteins": round(float(proteins_100g), 1),
                    "fats": round(float(fats_100g), 1),
                    "carbohydrates": round(float(carbs_100g), 1),
                    "saturated_fat": round(float(satfat_100g), 1),
                    "sugars": round(float(sugars_100g), 1),
                    "fiber": round(float(fiber_100g), 1),
                    "salt": round(float(salt_100g), 2)
                 }
            }
        }
    }

    return analysis


