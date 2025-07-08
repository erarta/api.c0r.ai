from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
from loguru import logger
from common.routes import Routes

app = FastAPI()

# Get environment variables
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

class InvoiceRequest(BaseModel):
    user_id: str
    amount: float
    description: str

@app.get(Routes.PAY_HEALTH)
async def health():
    return {"status": "ok", "service": "pay.c0r.ai"}

@app.post(Routes.PAY_INVOICE)
async def create_invoice(request: InvoiceRequest):
    # TODO: Implement actual invoice creation logic
    # For now, return placeholder response
    return {
        "status": "success",
        "invoice_url": "https://example.com/pay",
        "invoice_id": "inv_12345",
        "user_id": request.user_id,
        "amount": request.amount,
        "description": request.description
    }

@app.post(Routes.PAY_WEBHOOK_YOOKASSA)
async def yookassa_webhook(request: Request):
    # TODO: Implement YooKassa webhook logic
    data = await request.json()
    logger.info(f"YooKassa webhook received: {data}")
    return {"status": "ok"}

@app.post(Routes.PAY_WEBHOOK_STRIPE)
async def stripe_webhook(request: Request):
    # TODO: Implement Stripe webhook logic
    data = await request.json()
    logger.info(f"Stripe webhook received: {data}")
    return {"status": "ok"} 