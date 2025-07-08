from fastapi import FastAPI, Request, HTTPException
import os
from yookassa.client import create_yookassa_invoice
from stripe.client import create_stripe_invoice
import httpx
from yookassa.config import PLANS_YOOKASSA
from stripe.config import PLANS_STRIPE

INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")
API_URL = os.getenv("API_URL", "http://api:8000/credits/add")

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "pay.c0r.ai is alive"}

@app.post("/invoice")
async def create_invoice(request: Request):
    token = request.headers.get("X-Internal-Token")
    if token != INTERNAL_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await request.json()
    user_id = data.get("user_id")
    plan_id = data.get("plan_id", "basic")
    if not user_id or not plan_id:
        raise HTTPException(status_code=400, detail="user_id and plan_id required")
    # Determine provider by plan_id naming convention
    if plan_id.startswith("pro_stripe"):
        plan = PLANS_STRIPE.get(plan_id)
        if not plan:
            raise HTTPException(status_code=400, detail="Unknown plan_id for Stripe")
        result = await create_stripe_invoice(user_id, plan_id)
    else:
        plan = PLANS_YOOKASSA.get(plan_id)
        if not plan:
            raise HTTPException(status_code=400, detail="Unknown plan_id for YooKassa")
        result = await create_yookassa_invoice(user_id, plan_id)
    return result

@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()
    obj = data.get("object", {})
    status = obj.get("status")
    payment_id = obj.get("id")
    amount = obj.get("amount", {}).get("value")
    user_id = obj.get("metadata", {}).get("user_id")
    count = obj.get("metadata", {}).get("count", 20)
    plan_id = obj.get("metadata", {}).get("plan_id", "basic")
    recurring = obj.get("metadata", {}).get("recurring", False)
    interval = obj.get("metadata", {}).get("interval")
    # gateway is not needed here anymore
    if status == "succeeded" and user_id and amount:
        async with httpx.AsyncClient() as client:
            await client.post(
                API_URL,
                headers={"X-Internal-Token": INTERNAL_API_TOKEN},
                json={
                    "user_id": user_id,
                    "count": count,
                    "payment_id": payment_id,
                    "amount": amount,
                    "status": status,
                    "plan_id": plan_id,
                    "recurring": recurring,
                    "interval": interval
                }
            )
    return {"ok": True} 