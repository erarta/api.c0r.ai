import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
from loguru import logger
from common.routes import Routes
from shared.health import create_health_response
from shared.auth import require_internal_auth, get_auth_headers
from yookassa_handlers.client import create_yookassa_invoice, verify_yookassa_payment, validate_yookassa_webhook
from yookassa_handlers.config import PLANS_YOOKASSA

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Get environment variables
API_SERVICE_URL = os.getenv("API_SERVICE_URL", "https://api.c0r.ai")

class InvoiceRequest(BaseModel):
    user_id: str
    amount: float
    description: str
    plan_id: str = "basic"  # Default plan

@app.get(Routes.PAY_HEALTH)
async def health():
    """Comprehensive health check for Payment service"""
    from shared.health import create_comprehensive_health_response
    
    # Note: We don't check API service health to avoid circular dependency
    # API service checks Pay service, but Pay service doesn't check API service
    
    return await create_comprehensive_health_response(
        service_name="pay",
        check_database=True,
        check_external_services={},  # No external service checks to avoid circular dependency
        additional_info={
            "api_service_configured": bool(API_SERVICE_URL),
            "yookassa_configured": bool(os.getenv("YOOKASSA_SHOP_ID") and os.getenv("YOOKASSA_SECRET_KEY")),
            "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
            "available_plans": list(PLANS_YOOKASSA.keys())
        }
    )

@app.get("/health")
async def health_alias():
    """Health check alias endpoint"""
    return await health()

@app.post(Routes.PAY_INVOICE)
@require_internal_auth
async def create_invoice(request_obj: Request, request: InvoiceRequest):
    """
    Create payment invoice for user
    """
    try:
        logger.info(f"Creating invoice for user {request.user_id}, plan {request.plan_id}")
        
        # Create YooKassa payment
        invoice_data = await create_yookassa_invoice(
            user_id=int(request.user_id),
            plan_id=request.plan_id
        )
        
        return invoice_data
        
    except ValueError as e:
        logger.error(f"Invalid request for user {request.user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create invoice for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment invoice")

@app.post(Routes.PAY_WEBHOOK_YOOKASSA)
async def yookassa_webhook(request: Request):
    """
    Handle YooKassa webhook notifications
    Process successful payments and update user credits
    """
    try:
        # Get request body and headers
        body = await request.body()
        headers = dict(request.headers)
        
        # Validate webhook (basic validation for now)
        if not validate_yookassa_webhook(body.decode(), headers):
            logger.warning("Invalid YooKassa webhook signature")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        # Parse webhook data
        data = await request.json()
        logger.info(f"YooKassa webhook received: {data}")
        
        # Check if this is a payment success notification
        if data.get("event") == "payment.succeeded":
            payment_object = data.get("object", {})
            payment_id = payment_object.get("id")
            status = payment_object.get("status")
            metadata = payment_object.get("metadata", {})
            
            if status == "succeeded" and payment_id:
                # Extract user info from metadata
                user_id = metadata.get("user_id")
                credits_count = int(metadata.get("credits_count", 0))
                plan_id = metadata.get("plan_id")
                amount = float(payment_object.get("amount", {}).get("value", 0))
                
                if user_id and credits_count > 0:
                    # Add credits to user account via API service
                    await add_credits_to_user(user_id, credits_count, payment_id, amount)
                    logger.info(f"Successfully processed payment {payment_id} for user {user_id}")
                else:
                    logger.warning(f"Missing user_id or credits_count in payment {payment_id}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing YooKassa webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def add_credits_to_user(user_id: str, credits_count: int, payment_id: str, amount: float):
    """
    Add credits to user account via API service
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{API_SERVICE_URL}/credits/add",
                headers=get_auth_headers(),
                json={
                    "user_id": user_id,
                    "count": credits_count,
                    "payment_id": payment_id,
                    "amount": amount,
                    "gateway": "yookassa",
                    "status": "succeeded"
                }
            )
            response.raise_for_status()
            logger.info(f"Added {credits_count} credits to user {user_id}")
            
    except Exception as e:
        logger.error(f"Failed to add credits to user {user_id}: {e}")
        raise

@app.get("/payment/success", response_class=HTMLResponse)
async def payment_success(request: Request, user_id: str, plan_id: str):
    """
    Handle successful payment redirect
    Show success page and redirect to Telegram
    """
    plan = PLANS_YOOKASSA.get(plan_id, {"name": "Unknown", "count": 0})
    
    return templates.TemplateResponse("payment_success.html", {
        "request": request,
        "user_id": user_id,
        "plan_name": plan["name"],
        "credits_count": plan["count"],
        "plan_id": plan_id
    })

# Stripe webhook is implemented in services/pay/stripe/webhooks.py
# This endpoint is removed to avoid duplication