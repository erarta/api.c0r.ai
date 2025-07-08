import os
from fastapi import FastAPI, Request, HTTPException
import httpx
import stripe
from supabase import create_client, Client

app = FastAPI()

# Environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SERVICE_BOT_URL = os.getenv("SERVICE_BOT_URL")  # e.g., webhook endpoint for c0r_ai_Service_Bot

stripe.api_key = STRIPE_SECRET_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    # Handle successful payment
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        telegram_user_id = intent["metadata"].get("telegram_user_id")
        amount = intent["amount_received"] / 100  # Stripe uses cents
        # Determine credits to add (example: 10 for $2.99, 100 for $19.99)
        credits = 10 if amount < 10 else 100
        # Update user credits in Supabase
        user_res = supabase.table("users").select("id, credits_remaining").eq("telegram_id", telegram_user_id).execute()
        if not user_res.data:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_res.data[0]["id"]
        new_credits = user_res.data[0]["credits_remaining"] + credits
        supabase.table("users").update({"credits_remaining": new_credits}).eq("id", user_id).execute()
        # Insert payment record
        supabase.table("payments").insert({
            "user_id": user_id,
            "amount": amount,
            "gateway": "stripe",
            "status": "succeeded"
        }).execute()
        # Notify service bot (optional, via webhook or HTTP call)
        if SERVICE_BOT_URL:
            async with httpx.AsyncClient() as client:
                await client.post(SERVICE_BOT_URL, json={
                    "event": "payment",
                    "user_id": telegram_user_id,
                    "amount": amount,
                    "credits_added": credits
                })
    return {"status": "ok"} 