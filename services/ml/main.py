import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from io import BytesIO
from collections import defaultdict, deque
import uuid
import time
import base64
import json
import httpx
import asyncio
from openai import OpenAI
from loguru import logger
from common.routes import Routes
from shared.health import create_health_response
from shared.auth import require_internal_auth
from .config import get_model_config, validate_model_for_task
from services.ml.core.providers.llm_factory import llm_factory
from services.ml.perplexity.client import analyze_food_with_perplexity
from common.db.profiles import get_user_profile
# OpenFoodFacts removed
from services.ml.chestnyznak_client import fetch_product_by_gtin, map_cz_to_basic
from services.ml.barcodelist_client import fetch_product_by_barcode as fetch_barcodelist, map_barcodelist_to_basic

# Optional imports for barcode detection
try:
    from PIL import Image, ImageOps, ImageEnhance
    from pyzbar.pyzbar import decode as zbar_decode
    _BARCODE_AVAILABLE = True
except Exception as _e:
    _BARCODE_AVAILABLE = False
    logger.warning(f"Barcode dependencies not available yet: {_e}")

_OCR_AVAILABLE = True

# Environment and app configuration
ENV = os.getenv("ENV", "development").lower()

# Swagger/Docs exposure: enabled in non-production by default; use ENABLE_SWAGGER to override
_enable_swagger_env = os.getenv("ENABLE_SWAGGER")
ENABLE_SWAGGER = (
    (_enable_swagger_env or ("true" if ENV != "production" else "false")).lower() == "true"
)

docs_url = "/docs" if ENABLE_SWAGGER else None
openapi_url = "/openapi.json" if ENABLE_SWAGGER else None

app = FastAPI(docs_url=docs_url, openapi_url=openapi_url, redoc_url=None)

# CORS for mobile/web clients (locked down in production)
_default_origins = "*" if ENV != "production" else ""
_origins = os.getenv("CORS_ORIGINS", _default_origins)
origins = [o.strip() for o in _origins.split(",") if o.strip()]
if ENV == "production" and ("*" in origins or not origins):
    # Disable CORS by default in production unless explicitly allowed
    origins = []
    logger.warning(
        "CORS is disabled by default in production. Set CORS_ORIGINS to an allowlist if needed."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic request ID middleware for observability
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Lightweight per-IP rate limiter (internal endpoints still benefit from abuse protection)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
_request_history: dict[str, deque[float]] = defaultdict(deque)
_barcode_cache: dict[str, tuple[float, dict]] = {}
BARCODE_CACHE_TTL_SEC = 600.0

def _rate_limit_ok(key: str) -> bool:
    now = time.time()
    window_seconds = 60.0
    dq = _request_history[key]
    while dq and (now - dq[0] > window_seconds):
        dq.popleft()
    if len(dq) >= RATE_LIMIT_PER_MINUTE:
        return False
    dq.append(now)
    return True

# Upload size guard
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "8"))
MAX_UPLOAD_BYTES = int(MAX_UPLOAD_MB * 1024 * 1024)

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize OpenAI client with proxy support
if OPENAI_API_KEY:
    # Check for proxy settings
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    
    if http_proxy or https_proxy:
        logger.info(f"Using proxy: HTTP={http_proxy}, HTTPS={https_proxy}")
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(
                proxies={
                    "http://": http_proxy,
                    "https://": https_proxy
                } if http_proxy or https_proxy else None
            )
        )
    else:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized without proxy")
else:
    openai_client = None
    logger.warning("OpenAI API key not provided")

class DetectedBarcode(BaseModel):
    type: str
    value: str

class OcrBlock(BaseModel):
    text: str
    confidence: Optional[float] = None

class LabelAnalyzeResponse(BaseModel):
    language: str
    barcodes: List[DetectedBarcode] = Field(default_factory=list)
    ocr_text: str = ""
    ocr_blocks: List[OcrBlock] = Field(default_factory=list)
    parsed_nutrition: Optional[dict] = None
    notes: Optional[str] = None


class PerplexityAnalyzeResponse(BaseModel):
    language: str
    analysis: dict

async def _detect_barcodes(image_bytes: bytes) -> List[DetectedBarcode]:
    """Detect barcodes using pyzbar with simple augmentations (rotate/contrast/resize).
    Adds detailed logs about attempts and successes to help diagnose failures in the field.
    """
    found_codes: dict[str, str] = {}
    results: List[DetectedBarcode] = []
    if not _BARCODE_AVAILABLE:
        return results
    try:
        t0 = time.monotonic()
        base = Image.open(BytesIO(image_bytes))
        # Ensure RGB for consistent ops
        if base.mode not in ("RGB", "L"):
            base = base.convert("RGB")

        # Prepare candidate variants
        candidates: List[Image.Image] = []
        # Original and grayscale
        candidates.append(base)
        candidates.append(ImageOps.grayscale(base))
        # Slight contrast boost can help
        try:
            candidates.append(ImageEnhance.Contrast(ImageOps.grayscale(base)).enhance(1.5))
        except Exception:
            pass
        # If image small, upscale (cap to 1600px on largest side)
        w, h = base.size
        max_side = max(w, h)
        if max_side < 900:
            scale = min(1600 / max_side, 2.5)
            new_size = (int(w * scale), int(h * scale))
            try:
                candidates.extend([
                    base.resize(new_size),
                    ImageOps.grayscale(base.resize(new_size))
                ])
            except Exception:
                pass

        logger.info(f"[BARCODE] Candidates prepared: {len(candidates)}; original size={w}x{h}")

        # Try rotations for each candidate
        total_decodes = 0
        for img in candidates:
            for angle in (0, 90, 180, 270):
                try:
                    test_img = img.rotate(angle, expand=True) if angle else img
                    decoded = zbar_decode(test_img)
                    logger.info(f"[BARCODE] Attempt angle={angle}: {len(decoded)} codes")
                    for d in decoded:
                        try:
                            value = d.data.decode("utf-8").strip()
                        except Exception:
                            value = d.data.decode(errors="ignore").strip()
                        if not value:
                            continue
                        # Deduplicate by value
                        if value not in found_codes:
                            found_codes[value] = d.type or "unknown"
                            total_decodes += 1
                except Exception:
                    continue

        logger.info(f"[BARCODE] Unique codes found={len(found_codes)} (raw decodes={total_decodes}) in {round((time.monotonic()-t0)*1000)}ms")
        for val, typ in found_codes.items():
            results.append(DetectedBarcode(type=typ, value=val))
    except Exception as e:
        logger.warning(f"Barcode decode failed: {e}")
    return results

def _normalize_text(s: str) -> str:
    return " ".join((s or "").replace("\n", " ").split())


async def _ocr_text(image_bytes: bytes, lang: str) -> tuple[str, List[OcrBlock]]:
    if not _OCR_AVAILABLE:
        return "", []
    try:
        import pytesseract
        from PIL import Image
        from io import BytesIO
        lang_code = "rus+eng" if lang.startswith("ru") else "eng+rus"
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img, lang=lang_code)
        # Split lines as blocks; pytesseract confidence requires image_to_data; we keep it simple for speed
        blocks = [OcrBlock(text=line.strip()) for line in text.splitlines() if line.strip()]
        return text, blocks
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return "", []


def _parse_nutrition_from_text(text: str) -> Optional[dict]:
    if not text:
        return None
    import re
    # Normalize common locale/spacing issues
    t = text.replace('\xa0', ' ')
    t = t.replace(',', '.')
    t = t.lower()
    # Common RU labels
    # energy (kcal)
    kcal = None
    m = re.search(r"(ккал|kcal)\D{0,15}([0-9]+(?:\.[0-9]+)?)", t)
    if m:
        try:
            kcal = float(m.group(2))
        except Exception:
            kcal = None
    # energy (kJ)
    kj = None
    m_kj = re.search(r"(кдж|kj)\D{0,15}([0-9]+(?:\.[0-9]+)?)", t)
    if m_kj:
        try:
            kj = float(m_kj.group(2))
        except Exception:
            kj = None
    # proteins
    prot = None
    m = re.search(r"(белк[аи]?|белок|protein[s]?)\D{0,15}([0-9]+(?:\.[0-9]+)?)\s*(g|гр|г)?\b", t)
    if m:
        try:
            prot = float(m.group(2))
        except Exception:
            prot = None
    # fats
    fat = None
    m = re.search(r"(жир[ыа]?|fat[s]?)\D{0,15}([0-9]+(?:\.[0-9]+)?)\s*(g|гр|г)?\b", t)
    if m:
        try:
            fat = float(m.group(2))
        except Exception:
            fat = None
    # carbs
    carb = None
    m = re.search(r"(углевод[ыа]?|carb[sh]?)\D{0,20}([0-9]+(?:\.[0-9]+)?)\s*(g|гр|г)?\b", t)
    if m:
        try:
            carb = float(m.group(2))
        except Exception:
            carb = None

    # serving size detection (e.g., 100 г / 100g)
    serving_g = 100.0
    m = re.search(r"(100)\s*(г|g)\b", t)
    if m:
        serving_g = 100.0

    if kcal is None and all(v is None for v in [prot, fat, carb]):
        return None

    # If kcal looks like kJ (too large), convert using kJ if available
    if kcal is not None and kcal > 1000:
        try:
            if kj is not None:
                kcal = float(kj) / 4.184
            else:
                kcal = float(kcal) / 4.184
        except Exception:
            pass
    # If kcal missing but macros present, estimate
    if kcal is None and any(v is not None for v in [prot, fat, carb]):
        try:
            kcal = 4.0 * (prot or 0) + 9.0 * (fat or 0) + 4.0 * (carb or 0)
        except Exception:
            kcal = None

    if kcal is None:
        return None

    analysis = {
        "analysis": {
            "food_items": [
                {
                    "name": "Product",
                    "weight_grams": round(serving_g, 1),
                    "calories": round(kcal, 1),
                    "emoji": "🍽️",
                    "health_benefits": "",
                }
            ],
            "total_nutrition": {
                "calories": round(kcal, 1),
                "proteins": round(prot or 0.0, 1),
                "fats": round(fat or 0.0, 1),
                "carbohydrates": round(carb or 0.0, 1),
            },
            "provenance": {
                "source": "ocr",
                "debug": {"kcal_raw": kcal, "kj_raw": kj, "prot": prot, "fat": fat, "carb": carb}
            },
        }
    }
    return analysis


def _heuristic_nutrition_from_title(title: Optional[str]) -> Optional[dict]:
    """Very small RU dairy heuristic to avoid zeros when only product name is known.
    Returns analysis per 100 g using typical values. Provenance: heuristic.
    """
    if not title:
        return None
    t = title.lower()
    # (kcal, proteins, fats, carbs)
    heuristics: list[tuple[str, tuple[float, float, float, float]]] = [
        (r"сливочн.*сыр", (330.0, 25.0, 26.0, 3.0)),  # cream-style cheese
        (r"\bсыр\b", (350.0, 25.0, 27.0, 0.0)),      # generic hard cheese
        (r"творог", (170.0, 16.0, 9.0, 3.0)),         # cottage cheese
        (r"молок", (64.0, 3.3, 3.2, 4.7)),            # 3.2% milk
        (r"йогурт", (60.0, 4.0, 3.0, 5.0)),           # plain yogurt
        (r"кефир", (52.0, 3.0, 3.0, 4.0)),            # kefir
    ]
    import re
    for pattern, (kcal, prot, fat, carb) in heuristics:
        if re.search(pattern, t):
            serving_g = 100.0
            analysis = {
                "analysis": {
                    "food_items": [
                        {
                            "name": title,
                            "weight_grams": serving_g,
                            "calories": round(kcal, 1),
                            "emoji": "🍽️",
                            "health_benefits": "",
                        }
                    ],
                    "total_nutrition": {
                        "calories": round(kcal, 1),
                        "proteins": round(prot, 1),
                        "fats": round(fat, 1),
                        "carbohydrates": round(carb, 1),
                    },
                    "provenance": {
                        "source": "heuristic",
                        "basis": "typical per 100 g",
                        "matched": pattern,
                    },
                }
            }
            return analysis
    return None

@app.get(Routes.ML_HEALTH)
async def health():
    """Comprehensive health check for ML service"""
    from shared.health import create_comprehensive_health_response
    
    return await create_comprehensive_health_response(
        service_name="ml",
        check_database=True,
        check_openai=True,
        additional_info={
            "openai_configured": bool(OPENAI_API_KEY),
            "gemini_configured": bool(GEMINI_API_KEY),
            "current_llm_provider": llm_factory.get_current_provider(),
            "available_providers": llm_factory.list_available_providers()
        }
    )

@app.get("/health")
async def health_alias():
    """Health check alias endpoint"""
    return await health()

@app.post(Routes.ML_LABEL_ANALYZE, response_model=LabelAnalyzeResponse)
@require_internal_auth
async def label_analyze(
    request: Request,
    photo: UploadFile = File(...),
    user_language: str = Form(default="en"),
):
    """
    Analyze packaging/label image. Skeleton only: returns OCR/barcodes stubs.
    """
    try:
        # Rate limiting (by client IP)
        client_ip = request.client.host if request.client else "unknown"
        if not _rate_limit_ok(f"label_analyze:{client_ip}"):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Content length early check (if present)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        image_bytes = await photo.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        start_overall = time.monotonic()
        logger.info("[BARCODE] Starting detection")
        barcodes = await _detect_barcodes(image_bytes)
        if barcodes:
            logger.info(f"Detected barcodes: {[b.value for b in barcodes]}")
        else:
            logger.info("No barcodes detected")
        ocr_text, ocr_blocks = await _ocr_text(image_bytes, user_language)

        # If we have a barcode, try providers in order with time budget: ChestnyZNAK → BarcodeList (RU)
        parsed_nutrition = None
        overall_deadline = start_overall + 9.5  # hard cap ~10s total
        if barcodes:
            for b in barcodes:
                # Quick cache check
                cached = _barcode_cache.get(b.value)
                if cached and (time.monotonic() - cached[0] < BARCODE_CACHE_TTL_SEC):
                    logger.info(f"[LOOKUP] Cache hit for {b.value}")
                    parsed_nutrition = cached[1]
                    break
                # 1) OpenFoodFacts removed

                # 2/3) Try CZ and BarcodeList concurrently with small timeouts
                remaining = overall_deadline - time.monotonic()
                if remaining <= 0:
                    break
                per_call_timeout = max(2.0, min(4.0, remaining))
                logger.info(f"[LOOKUP] Parallel CZ & BarcodeList (timeout={per_call_timeout:.1f}s each)")
                try:
                    cz_task = asyncio.create_task(fetch_product_by_gtin(b.value))
                    bl_task = asyncio.create_task(fetch_barcodelist(b.value))
                    done, pending = await asyncio.wait(
                        {cz_task, bl_task}, timeout=per_call_timeout, return_when=asyncio.FIRST_COMPLETED
                    )
                    for t in done:
                        res = t.result()
                        if res and not parsed_nutrition:
                            if t is cz_task:
                                mapped2 = map_cz_to_basic(res)
                                if mapped2 and isinstance(mapped2, dict) and "analysis" in mapped2:
                                    parsed_nutrition = mapped2
                                    # OFF upgrade removed
                            elif t is bl_task:
                                mapped3 = map_barcodelist_to_basic(res)
                                if mapped3 and isinstance(mapped3, dict) and "analysis" in mapped3:
                                    parsed_nutrition = mapped3
                                    # OFF upgrade removed
                    # Cancel pending to save time
                    for p in pending:
                        p.cancel()
                except Exception:
                    pass

                # If still metadata only, apply RU dairy heuristic from BL title
                if parsed_nutrition and parsed_nutrition.get('analysis',{}).get('provenance',{}).get('source') == 'barcodelist':
                    bl_name = None
                    try:
                        bl_name = res.get("title") if 'res' in locals() and isinstance(res, dict) else None
                    except Exception:
                        bl_name = None
                    if bl_name and parsed_nutrition.get('analysis',{}).get('total_nutrition',{}).get('calories', 0) == 0:
                        heur = _heuristic_nutrition_from_title(bl_name)
                        if heur:
                            parsed_nutrition = heur
                            _barcode_cache[b.value] = (time.monotonic(), parsed_nutrition)
                            logger.info("[LOOKUP] Applied RU dairy heuristic from title")
                            break

        # If no provider matched, try OCR nutrition extraction as fallback
        if not parsed_nutrition:
            # Run OCR parse fast
            parsed_nutrition = _parse_nutrition_from_text(ocr_text)
            if parsed_nutrition:
                logger.info("[OCR] Nutrition extracted from label text")
            else:
                # Try to guess product name from OCR and search OFF by name under tight deadline
                try:
                    title_candidate = None
                    for blk in ocr_blocks:
                        line = blk.text.strip()
                        if 8 <= len(line) <= 80 and any(c.isalpha() for c in line):
                            upper_letters = sum(1 for c in line if c.isalpha() and c.upper() == c)
                            total_letters = sum(1 for c in line if c.isalpha())
                            upper_ratio = (upper_letters / total_letters) if total_letters else 0.0
                            if upper_ratio > 0.6 or line.istitle():
                                title_candidate = line
                                break
                    if title_candidate:
                        deadline = time.monotonic() + 3.0
                        logger.info(f"[OCR] OFF by OCR title (deadline): {title_candidate}")
                        off_by_title = await fetch_best_product_by_names([title_candidate], deadline_ts=deadline, page_size=5, timeout_sec=2.5)
                        if off_by_title:
                            mapped_from_title = map_off_to_nutrition(off_by_title)
                            if mapped_from_title and isinstance(mapped_from_title, dict) and "analysis" in mapped_from_title:
                                parsed_nutrition = mapped_from_title
                                logger.info("[LOOKUP] Upgrade success via OFF name from OCR title")
                except Exception:
                    pass

        # Assemble debug info for provenance
        provenance = None
        if parsed_nutrition and isinstance(parsed_nutrition, dict):
            provenance = parsed_nutrition.get('analysis', {}).get('provenance', {})
            if isinstance(provenance, dict):
                provenance.setdefault('debug', {})
                provenance['debug'].update({
                    'barcodes_detected': [b.value for b in barcodes] if barcodes else [],
                    'ocr_present': bool(ocr_text),
                    'time_ms': round((time.monotonic() - start_overall) * 1000),
                })
        resp = LabelAnalyzeResponse(
            language=user_language,
            barcodes=barcodes,
            ocr_text=ocr_text,
            ocr_blocks=ocr_blocks,
            parsed_nutrition=parsed_nutrition,
            notes=(
                "Matched ChestnyZNAK (basic metadata)" if parsed_nutrition and parsed_nutrition.get('analysis',{}).get('provenance',{}).get('source') == 'chestnyznak'
                else "Matched BarcodeList (basic metadata)" if parsed_nutrition and parsed_nutrition.get('analysis',{}).get('provenance',{}).get('source') == 'barcodelist'
                else "Parsed from label (OCR)" if parsed_nutrition and parsed_nutrition.get('analysis',{}).get('provenance',{}).get('source') == 'ocr'
                else "Heuristic estimate (RU dairy)" if parsed_nutrition and parsed_nutrition.get('analysis',{}).get('provenance',{}).get('source') == 'heuristic'
                else "No barcode match; OCR pending"
            ),
        )
        elapsed = round((time.monotonic() - start_overall) * 1000)
        logger.info(f"[TIMING] label_analyze elapsed={elapsed}ms")
        return resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Label analyze error [{getattr(request.state, 'request_id', '-') }]: {e}")
        raise HTTPException(status_code=500, detail="Label analysis failed")

@app.post(Routes.ML_LABEL_PERPLEXITY, response_model=PerplexityAnalyzeResponse)
@require_internal_auth
async def label_analyze_perplexity(
    request: Request,
    photo: UploadFile = File(...),
    user_language: str = Form(default="en"),
):
    try:
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        image_bytes = await photo.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file")
        # Detect barcode(s) up front
        try:
            barcodes = await _detect_barcodes(image_bytes)
        except Exception:
            barcodes = []
        # Delegate to Perplexity client for a rich product analysis
        # Try to fetch a minimal user context if telegram id header present
        user_context = None
        try:
            telegram_id = request.headers.get("X-Telegram-Id")
            if telegram_id:
                from common.db.users import get_user_by_telegram_id
                user = await get_user_by_telegram_id(int(telegram_id))
                if user:
                    profile = await get_user_profile(user['id'])
                    user_context = profile or {}
        except Exception:
            user_context = None
        analysis = await analyze_food_with_perplexity(
            image_bytes,
            user_language,
            use_premium_model=False,
            mode="label",
            user_context=user_context,
        )
        # Attach detected barcodes into provenance.debug for UI usage
        try:
            az = analysis.get("analysis") if isinstance(analysis, dict) else None
            if isinstance(az, dict):
                prov = az.setdefault("provenance", {}).setdefault("debug", {})
                if barcodes:
                    prov["barcodes_detected"] = [b.value for b in barcodes]
        except Exception:
            pass
        return PerplexityAnalyzeResponse(language=user_language, analysis=analysis.get("analysis", analysis))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Perplexity label analyze error: {e}")
        raise HTTPException(status_code=500, detail="Perplexity label analysis failed")


class FoodPlanRequest(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)
    food_history: List[Dict[str, Any]] = Field(default_factory=list)
    days: int = Field(default=3, ge=1, le=7)


@app.post("/api/v1/food-plan/generate", response_model=Dict[str, Any])
@require_internal_auth
async def ml_generate_food_plan(payload: FoodPlanRequest):
    """Generate simple food plan. Placeholder for full LLM integration.
    Returns plan_json, shopping_list_json, confidence, model_used.
    """
    try:
        profile = payload.profile or {}
        days = int(payload.days)
        target = profile.get("daily_calories_target") or 2000
        try:
            target = int(target)
        except Exception:
            target = 2000
        per_meal = max(200, int(target // 4))
        plan: Dict[str, Any] = {}
        for d in range(1, days + 1):
            plan[f"day_{d}"] = {
                "breakfast": {"calories": per_meal, "protein": 20, "fats": 15, "carbs": 45, "text": "Oatmeal with berries"},
                "lunch": {"calories": per_meal, "protein": 25, "fats": 18, "carbs": 40, "text": "Chicken, rice, salad"},
                "dinner": {"calories": per_meal, "protein": 25, "fats": 18, "carbs": 40, "text": "Fish, quinoa, veggies"},
                "snack": {"calories": per_meal, "protein": 10, "fats": 10, "carbs": 25, "text": "Yogurt and nuts"},
                "summary": {},
            }
        shopping = {"items": ["oats", "berries", "chicken", "rice", "salad", "fish", "quinoa", "yogurt", "nuts"]}
        return {
            "plan_json": plan,
            "shopping_list_json": shopping,
            "confidence": 0.5,
            "model_used": llm_factory.get_current_provider(),
        }
    except Exception as e:
        logger.error(f"ML food plan generation error: {e}")
        raise HTTPException(status_code=500, detail="Food plan generation failed")

async def analyze_food_with_openai(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
    """
    Analyze food image using OpenAI Vision API
    Returns KBZHU data in expected format
    
    Args:
        image_bytes: Image data to analyze
        user_language: User language preference
        use_premium_model: Whether to use premium model settings
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Get model configuration for analysis task
        config = get_model_config("analysis", use_premium_model)
        model = config["model"]
        max_tokens = config["max_tokens"]
        temperature = config["temperature"]
        
        # Create prompt for food analysis based on user language
        if user_language == "ru":
            prompt = """
            Проанализируйте блюдо на фотографии и определите ВСЕ продукты питания максимально точно.
            
            ВАЖНЫЕ ПРАВИЛА РАСПОЗНАВАНИЯ:
            1. ВНИМАТЕЛЬНО изучите форму, цвет, текстуру каждого продукта
            2. Отличайте похожие продукты:
               - Вареные яйца: белые, овальные, со специфической текстурой белка
               - Моцарелла: более гладкая, кремовая текстура
               - Сыр фета: крупинчатая структура, белый цвет
            3. Оценивайте размеры порций РЕАЛИСТИЧНО:
               - Одно вареное яйцо = 50-60г
               - Порция сыра = 20-40г
               - Листья салата = 10-30г за пучок
            4. Указывайте ТОЧНЫЕ названия продуктов
            
                         ⚠️ КРИТИЧЕСКОЕ ВНИМАНИЕ К БЕЛЫМ ПРОДУКТАМ ⚠️
             
             НА ЭТОМ ФОТО ТОЧНО ЕСТЬ ЯЙЦА, НЕ МОЦАРЕЛЛА!
             
             АБСОЛЮТНЫЕ ПРАВИЛА:
             🥚 ЯЙЦА = Белые овальные кусочки с ВИДИМЫМ ЖЕЛТКОМ в центре, матовые, разрезанные пополам
             🧀 МОЦАРЕЛЛА = Идеально круглые шарики БЕЗ желтка, глянцевые, цельные
             
             ⛔ ЗАПРЕЩЕНО НАЗЫВАТЬ ЯЙЦА МОЦАРЕЛЛОЙ! ⛔
             
             ПОШАГОВАЯ ПРОВЕРКА:
             1. Вижу белые овальные объекты? → ПРОВЕРЬ ЕСТЬ ЛИ ЖЕЛТОК
             2. Есть желток в центре? → ЭТО ЯЙЦА 🥚
             3. Нет желтка, но круглые шарики? → ЭТО МОЦАРЕЛЛА 🧀
             4. Оранжевые куски? → ЛОСОСЬ 🐟
             5. Зеленые листья? → ШПИНАТ/РУККОЛА 🥬
             
             ВНИМАНИЕ: Разрезанные вареные яйца выглядят как белые овалы с желтой серединой!
            
            Верните JSON в формате:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "название кухни",
                        "dish_identification": "название блюда",
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "точное название продукта",
                            "weight_grams": реальный_вес,
                            "calories": калории,
                            "emoji": "🍽️",
                            "health_benefits": "польза для здоровья"
                        }
                    ],
                    "total_nutrition": {
                        "calories": 300,
                        "proteins": 20,
                        "fats": 10,
                        "carbohydrates": 30
                    },
                    "nutrition_analysis": {
                        "health_score": 8,
                        "positive_aspects": ["высокое содержание белка"],
                        "improvement_suggestions": ["добавить овощи"]
                    },
                    "motivation_message": "Отличный выбор для здорового питания!"
                }
            }
            """
        else:
            prompt = """
            Analyze the food in this image and identify ALL food items with MAXIMUM ACCURACY.
            
            CRITICAL RECOGNITION RULES:
            1. CAREFULLY examine shape, color, texture of each item
            2. Distinguish between similar foods:
               - Hard-boiled eggs: white, oval, specific egg white texture
               - Mozzarella: smoother, creamy texture
               - Feta cheese: crumbly structure, white color
            3. Estimate portion sizes REALISTICALLY:
               - One hard-boiled egg = 50-60g
               - Cheese portion = 20-40g
               - Salad leaves = 10-30g per handful
            4. Use PRECISE food names
            
                         ⚠️ CRITICAL ATTENTION TO WHITE FOOD ITEMS ⚠️
             
             THIS PHOTO DEFINITELY HAS EGGS, NOT MOZZARELLA!
             
             ABSOLUTE RULES:
             🥚 EGGS = White oval pieces with VISIBLE YOLK in center, matte surface, cut in half
             🧀 MOZZARELLA = Perfectly round balls WITHOUT yolk, glossy, whole pieces
             
             ⛔ FORBIDDEN TO CALL EGGS MOZZARELLA! ⛔
             
             STEP-BY-STEP CHECK:
             1. See white oval objects? → CHECK FOR YOLK
             2. Has yolk in center? → THESE ARE EGGS 🥚
             3. No yolk but round balls? → THIS IS MOZZARELLA 🧀
             4. Orange pieces? → SALMON 🐟
             5. Green leaves? → SPINACH/ARUGULA 🥬
             
             ATTENTION: Cut hard-boiled eggs look like white ovals with yellow center!
            
            Return JSON in format:
            {
                "analysis": {
                    "regional_analysis": {
                        "detected_cuisine_type": "cuisine name",
                        "dish_identification": "dish name", 
                        "regional_match_confidence": 0.8
                    },
                    "food_items": [
                        {
                            "name": "precise food name",
                            "weight_grams": realistic_weight,
                            "calories": calories,
                            "emoji": "🍽️",
                            "health_benefits": "health benefits"
                        }
                    ],
                    "total_nutrition": {
                        "calories": 300,
                        "proteins": 20,
                        "fats": 10,
                        "carbohydrates": 30
                    },
                    "nutrition_analysis": {
                        "health_score": 8,
                        "positive_aspects": ["high protein content"],
                        "improvement_suggestions": ["add vegetables"]
                    },
                    "motivation_message": "Great choice for healthy eating!"
                }
            }
            """
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert food recognition AI with advanced visual analysis capabilities. Your primary task is to accurately identify food items in images with precise attention to visual details like shape, color, texture, and size. Pay special attention to distinguishing between similar-looking foods (eggs vs cheese, different proteins, etc). Always prioritize accuracy over speed."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {content}")
        
        # Try to parse JSON from response with improved handling
        try:
            # Clean up the response content
            content = content.strip()
            
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            # Try to extract JSON from text if it's mixed with other content
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            response_data = json.loads(content)
            
            # Check if we have the new analysis format
            if "analysis" in response_data:
                # New format - return as is
                return response_data
            else:
                # Old format fallback - convert to new structure
                # Handle different possible old format keys
                kbzhu_data = None
                if "total_nutrition" in response_data:
                    kbzhu_data = response_data["total_nutrition"]
                elif "kbzhu" in response_data:
                    kbzhu_data = response_data["kbzhu"]
                else:
                    # Use the entire response as nutrition data
                    kbzhu_data = response_data
                
                # Validate required fields
                required_fields = ["calories", "proteins", "fats", "carbohydrates"]
                for field in required_fields:
                    if field not in kbzhu_data:
                        raise ValueError(f"Missing field: {field}")
                    # Ensure values are numbers
                    kbzhu_data[field] = float(kbzhu_data[field])
                
                # Convert old format to new format structure
                result = {
                    "analysis": {
                        "food_items": response_data.get("food_items", []),
                        "total_nutrition": kbzhu_data,
                        "motivation_message": "Keep tracking your nutrition!"
                    }
                }
                return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.error(f"Raw OpenAI response content: {content}")
            logger.info("Entering fallback logic due to JSON parsing failure")
            
            # Try to extract basic nutrition info from text if JSON parsing failed
            # This is a fallback to provide some detailed info even when JSON fails
            fallback_food_items = []
            
            # Simple text parsing for common food items (basic fallback)
            import re
            
            # Look for food names and calories in the text
            food_patterns = [
                r'(\w+(?:\s+\w+)*)\s*\(([^)]+)\)\s*-?\s*(\d+)\s*(?:cal|ккал)',
                r'(\w+(?:\s+\w+)*)\s*:\s*(\d+)\s*(?:cal|ккал)',
                r'•\s*(\w+(?:\s+\w+)*)\s*\(([^)]+)\)\s*-?\s*(\d+)'
            ]
            
            for pattern in food_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 3:
                        name, weight, calories = match
                        fallback_food_items.append({
                            "name": name.strip(),
                            "weight": weight.strip(),
                            "calories": int(calories)
                        })
                    elif len(match) == 2:
                        name, calories = match
                        fallback_food_items.append({
                            "name": name.strip(),
                            "weight": "estimated portion",
                            "calories": int(calories)
                        })
            
            # Return enhanced fallback with food items if found
            # Convert to new format structure
            fallback_nutrition = {
                "calories": 250,
                "proteins": 15.0,
                "fats": 8.0,
                "carbohydrates": 30.0
            }
            
            if fallback_food_items:
                # Recalculate total calories from food items
                total_calories = sum(item["calories"] for item in fallback_food_items)
                if total_calories > 0:
                    fallback_nutrition["calories"] = total_calories
            
            # Convert fallback food items to new format
            new_format_food_items = []
            for item in fallback_food_items:
                new_format_food_items.append({
                    "name": item["name"],
                    "weight_grams": 100,  # Default weight
                    "calories": item["calories"],
                    "emoji": "🍽️",
                    "health_benefits": f"Contains {item['calories']} calories"
                })
            
            result = {
                "analysis": {
                    "food_items": new_format_food_items,
                    "total_nutrition": fallback_nutrition,
                    "motivation_message": "Keep tracking your nutrition!"
                }
            }
            
            logger.info(f"Fallback result: {result}")
            return result
            
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")

async def generate_recipe_with_openai(image_url: str, user_context: dict) -> dict:
    """
    Generate recipe from food image using OpenAI GPT-4o
    Returns recipe data with ingredients, instructions, and nutrition
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
    try:
        # Get user language
        user_language = user_context.get('language', 'en')
        has_profile = user_context.get('has_profile', False)
        
        # Build personalized context
        context_parts = []
        
        if has_profile:
            # Add profile information to context
            if user_context.get('dietary_preferences'):
                dietary_prefs = [pref for pref in user_context['dietary_preferences'] if pref != 'none']
                if dietary_prefs:
                    context_parts.append(f"Dietary preferences: {', '.join(dietary_prefs)}")
            
            if user_context.get('allergies'):
                allergies = [allergy for allergy in user_context['allergies'] if allergy != 'none']
                if allergies:
                    context_parts.append(f"Food allergies to avoid: {', '.join(allergies)}")
            
            if user_context.get('goal'):
                goal_map = {
                    'lose_weight': 'weight loss',
                    'maintain_weight': 'weight maintenance',
                    'gain_weight': 'weight gain'
                }
                goal = goal_map.get(user_context['goal'], user_context['goal'])
                context_parts.append(f"Fitness goal: {goal}")
            
            if user_context.get('daily_calories_target'):
                context_parts.append(f"Daily calorie target: {user_context['daily_calories_target']} calories")
        
        # Create personalized context string
        personal_context = "\n".join(context_parts) if context_parts else "No specific dietary requirements"
        
        # Create prompt for recipe generation based on user language
        if user_language == "ru":
            prompt = f"""
            Проанализируйте это изображение еды/ингредиентов и создайте персонализированный рецепт.

            ПЕРСОНАЛЬНЫЙ КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:
            {personal_context}

            Пожалуйста, создайте рецепт, который:
            1. Использует ингредиенты, видимые на изображении
            2. Соответствует диетическим предпочтениям пользователя
            3. Избегает указанных аллергенов
            4. Подходит для цели пользователя по фитнесу
            5. Включает точную информацию о питании

            Верните ТОЛЬКО JSON объект со следующей структурой:
            {{
                "name": "название рецепта",
                "description": "краткое описание блюда",
                "prep_time": "время подготовки (например, 15 минут)",
                "cook_time": "время приготовления (например, 30 минут)",
                "servings": "количество порций (например, 4)",
                "ingredients": [
                    "ингредиент 1 с количеством",
                    "ингредиент 2 с количеством"
                ],
                "instructions": [
                    "шаг 1 инструкции",
                    "шаг 2 инструкции"
                ],
                "nutrition": {{
                    "calories": число_калорий_на_порцию,
                    "protein": число_белков_в_граммах,
                    "carbs": число_углеводов_в_граммах,
                    "fat": число_жиров_в_граммах
                }}
            }}

            Убедитесь, что рецепт безопасен и подходит для указанных диетических ограничений.
            Все числовые значения должны быть числами (не строками).
            """
        else:
            prompt = f"""
            Analyze this food/ingredient image and create a personalized recipe.

            USER'S PERSONAL CONTEXT:
            {personal_context}

            Please create a recipe that:
            1. Uses the ingredients visible in the image
            2. Matches the user's dietary preferences
            3. Avoids specified allergens
            4. Suits the user's fitness goal
            5. Includes accurate nutritional information

            Return ONLY a JSON object with the following structure:
            {{
                "name": "recipe name",
                "description": "brief description of the dish",
                "prep_time": "preparation time (e.g., 15 minutes)",
                "cook_time": "cooking time (e.g., 30 minutes)",
                "servings": "number of servings (e.g., 4)",
                "ingredients": [
                    "ingredient 1 with quantity",
                    "ingredient 2 with quantity"
                ],
                "instructions": [
                    "step 1 instruction",
                    "step 2 instruction"
                ],
                "nutrition": {{
                    "calories": calories_per_serving_number,
                    "protein": protein_grams_number,
                    "carbs": carbs_grams_number,
                    "fat": fat_grams_number
                }}
            }}

            Ensure the recipe is safe and suitable for the specified dietary restrictions.
            All numeric values should be numbers (not strings).
            """
        
        # Call OpenAI Vision API for recipe generation
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Use full GPT-4o for better recipe generation
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,  # More tokens for detailed recipes
            temperature=0.3  # Slightly more creative for recipe generation
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI recipe response: {content}")
        
        # Try to parse JSON from response
        try:
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            recipe_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["name", "ingredients", "instructions"]
            for field in required_fields:
                if field not in recipe_data:
                    raise ValueError(f"Missing field: {field}")
            
            # Validate nutrition data if present
            if "nutrition" in recipe_data:
                nutrition = recipe_data["nutrition"]
                for nutrient in ["calories", "protein", "carbs", "fat"]:
                    if nutrient in nutrition:
                        nutrition[nutrient] = float(nutrition[nutrient])
            
            return recipe_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI recipe response: {e}")
            # Return fallback recipe based on user language
            if user_language == "ru":
                return {
                    "name": "Вкусный рецепт",
                    "description": "Аппетитное блюдо из ингредиентов с вашего фото",
                    "prep_time": "15 минут",
                    "cook_time": "30 минут",
                    "servings": "4",
                    "ingredients": ["Ингредиенты с вашего фото"],
                    "instructions": ["Подготовьте ингредиенты как показано", "Готовьте согласно вашим предпочтениям"],
                    "nutrition": {
                        "calories": 300,
                        "protein": 20,
                        "carbs": 25,
                        "fat": 12
                    }
                }
            else:
                return {
                    "name": "Delicious Recipe",
                    "description": "A tasty dish made from the ingredients in your photo",
                    "prep_time": "15 minutes",
                    "cook_time": "30 minutes",
                    "servings": "4",
                    "ingredients": ["Ingredients from your photo"],
                    "instructions": ["Prepare ingredients as shown", "Cook according to your preference"],
                    "nutrition": {
                        "calories": 300,
                        "protein": 20,
                        "carbs": 25,
                        "fat": 12
                    }
                }
            
    except Exception as e:
        logger.error(f"OpenAI recipe generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recipe generation failed: {str(e)}")

@app.post(Routes.ML_ANALYZE)
@require_internal_auth
async def analyze_file(
    request: Request,
    photo: UploadFile = File(...),
    telegram_user_id: str = Form(...),
    provider: str = Form(default="openai"),
    user_language: str = Form(default="en")
):
    """
    Analyze food image and return KBZHU data
    """
    try:
        # Rate limiting (by client IP)
        client_ip = request.client.host if request.client else "unknown"
        if not _rate_limit_ok(f"analyze_file:{client_ip}"):
            raise HTTPException(status_code=429, detail="Too many requests")
        # Content length early check (if present)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")

        logger.info(f"🔥 ANALYZE_FILE CALLED: user={telegram_user_id}, provider={provider}")
        logger.info(f"🎯 Factory current provider: {llm_factory.get_current_provider()}")
        logger.info(f"Analyzing photo for user {telegram_user_id} with provider {provider}")
        
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await photo.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        if len(image_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image too large")
        
        # Use LLM factory for analysis (respects LLM_PROVIDER/ANALYSIS_PROVIDER env vars) and per-request override
        analysis_result = await llm_factory.analyze_food(
            image_bytes,
            user_language,
            use_premium_model=False,
            provider_override=provider,
        )
        
        logger.info(f"Analysis complete for user {telegram_user_id}: {analysis_result}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error [{getattr(request.state, 'request_id', '-') }]: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post(Routes.ML_GENERATE_RECIPE)
@require_internal_auth
async def generate_recipe(
    request: Request,
    image_url: str = Form(...),
    telegram_user_id: str = Form(...),
    user_context: str = Form(...)
):
    """
    Generate recipe from food image using OpenAI GPT-4o
    """
    try:
        logger.info(f"DEBUG: ML service received request:")
        logger.info(f"  - image_url: {image_url}")
        logger.info(f"  - telegram_user_id: {telegram_user_id}")
        logger.info(f"  - user_context: {user_context}")
        logger.info(f"Generating recipe for user {telegram_user_id}")
        
        # Parse user context JSON
        try:
            context_data = json.loads(user_context)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid user_context JSON")
        
        # Generate recipe with OpenAI
        recipe_result = await generate_recipe_with_openai(image_url, context_data)
        
        logger.info(f"Recipe generation complete for user {telegram_user_id}: {recipe_result['name']}")
        
        return recipe_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recipe generation error: {e}")
