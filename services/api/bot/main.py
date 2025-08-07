import sys; print("PYTHONPATH:", sys.path)
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
import asyncio
from services.api.bot.bot import start_bot
import os
import httpx
from common.routes import Routes
from common.supabase_client import (
    get_or_create_user, get_user_by_telegram_id, decrement_credits, add_credits, log_analysis, add_payment
)
from services.api.bot.utils.r2 import test_r2_connection, get_photo_stats, get_user_photos
from shared.auth import require_internal_auth, get_auth_headers
from loguru import logger

app = FastAPI()

# Mount static files directory for assets (logo, etc.)
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
    logger.info("Assets directory mounted successfully")
else:
    logger.warning("Assets directory not found, static files will not be served")

# All values must be set in .env file
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
PAY_SERVICE_URL = os.getenv("PAY_SERVICE_URL")

@app.get("/")
async def health():
    """Comprehensive health check for API Bot service"""
    from shared.health import create_comprehensive_health_response
    
    # Check external service dependencies
    external_services = {}
    if ML_SERVICE_URL:
        external_services["ml_service"] = f"{ML_SERVICE_URL}/"
    if PAY_SERVICE_URL:
        external_services["pay_service"] = f"{PAY_SERVICE_URL}/"
    
    return await create_comprehensive_health_response(
        service_name="api",
        check_database=True,
        check_external_services=external_services,
        additional_info={
            "ml_service_configured": bool(ML_SERVICE_URL),
            "pay_service_configured": bool(PAY_SERVICE_URL),
            "r2_enabled": os.getenv("R2_ENABLED", "false").lower() == "true"
        }
    )

@app.get("/health")
async def health_alias():
    """Health check alias endpoint"""
    return await health()

# Simple bot startup without complex lifecycle management
@app.on_event("startup")
async def launch_bot():
    logger.info("FastAPI startup - launching bot...")
    
    async def start_bot_with_error_handling():
        try:
            await start_bot()
        except Exception as e:
            logger.error(f"Bot startup failed: {e}")
            logger.exception("Bot startup exception details:")
            raise
    
    asyncio.create_task(start_bot_with_error_handling())

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    country = data.get("country")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="telegram_id required")
    user = await get_or_create_user(telegram_id, country)
    return user

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    # Extract data for logging
    user_id = data.get("user_id", "unknown")
    model_used = data.get("model_used", "openai")
    image_url = data.get("image_url")
    if not user_id or not image_url:
        raise HTTPException(status_code=400, detail="user_id and image_url required")
    user = await get_user_by_telegram_id(user_id)
    if not user or user["credits_remaining"] < 1:
        raise HTTPException(status_code=402, detail="Not enough credits")
    await decrement_credits(user_id)
    # Прокси-запрос к ml.c0r.ai
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ML_SERVICE_URL}{Routes.ML_ANALYZE}",
            headers=get_auth_headers(),
            json={"user_id": user_id, "image_url": image_url}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    result = resp.json()
    # Логирование анализа
    await log_analysis(user["id"], image_url, result, model_used)
    return result

@app.post("/credits/buy")
async def buy_credits(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    description = data.get("description", "Buy credits")
    if not user_id or not amount:
        raise HTTPException(status_code=400, detail="user_id and amount required")
    # Прокси-запрос к pay.c0r.ai
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAY_SERVICE_URL}{Routes.PAY_INVOICE}",
            headers=get_auth_headers(),
            json={"user_id": user_id, "amount": amount, "description": description}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.post("/credits/add")
@require_internal_auth
async def add_credits_api(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    count = data.get("count", 20)
    payment_id = data.get("payment_id")
    amount = data.get("amount")
    gateway = data.get("gateway", "yookassa")
    status = data.get("status", "succeeded")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    user = await add_credits(user_id, count)
    # Добавить запись о платеже, если есть данные
    if amount is not None and payment_id is not None:
        await add_payment(user["id"], amount, gateway, status)
    return user

@app.get("/debug/r2")
async def debug_r2():
    """Debug R2 configuration and status"""
    from services.api.bot.utils.r2 import R2_ENABLED, R2_ACCOUNT_ID, R2_BUCKET_NAME, test_r2_connection
    
    r2_config = {
        "r2_enabled": R2_ENABLED,
        "r2_account_id": R2_ACCOUNT_ID[:8] + "..." if R2_ACCOUNT_ID else None,
        "r2_bucket_name": R2_BUCKET_NAME,
        "r2_access_key_configured": bool(os.getenv("R2_ACCESS_KEY_ID")),
        "r2_secret_key_configured": bool(os.getenv("R2_SECRET_ACCESS_KEY")),
    }
    
    if R2_ENABLED:
        connection_test = await test_r2_connection()
        r2_config["connection_test"] = "SUCCESS" if connection_test else "FAILED"
    else:
        r2_config["connection_test"] = "SKIPPED (R2 not enabled)"
    
    return r2_config

@app.get("/debug/recent-logs")
async def debug_recent_logs():
    """Get recent photo analysis logs to check R2 URLs"""
    from common.supabase_client import supabase
    
    # Get last 10 photo analysis logs
    logs = supabase.table("logs").select("*").eq("action_type", "photo_analysis").order("timestamp", desc=True).limit(10).execute().data
    
    return {
        "recent_logs_count": len(logs),
        "logs": logs
    }

@app.get("/r2/test")
async def test_r2():
    """Test R2 connection and configuration"""
    connection_ok = await test_r2_connection()
    stats = get_photo_stats()
    
    return {
        "r2_connection": "ok" if connection_ok else "failed",
        "bucket_stats": stats,
        "status": "R2 storage is working" if connection_ok else "R2 storage has issues"
    }

@app.get("/r2/stats")
async def r2_stats():
    """Get R2 bucket statistics"""
    return get_photo_stats()

@app.get("/r2/user/{user_id}/photos")
async def get_user_photos_api(user_id: str, limit: int = 20):
    """Get photos for specific user"""
    photos = await get_user_photos(user_id, limit)
    return {
        "user_id": user_id,
        "photos_count": len(photos),
        "photos": photos
    }


@app.get("/test-region-detection/{language_code}")
async def test_region_detection(language_code: str):
    """Test endpoint for region detection by language code"""
    try:
        from shared.region_detector import region_detector
        
        region = region_detector.detect_region(language_code)
        payment_system = region_detector.get_payment_system(language_code)
        
        return {
            "success": True,
            "language_code": language_code,
            "region": region.value,
            "payment_system": payment_system.value,
            "is_cis_user": region_detector.is_cis_user(language_code)
        }
        
    except Exception as e:
        logger.error(f"Error in test_region_detection: {e}")
        return {"success": False, "error": str(e)} 