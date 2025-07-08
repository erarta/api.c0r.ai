from fastapi import FastAPI, Request, HTTPException
import asyncio
from bot import start_bot
import os
import httpx
from common.supabase_client import (
    get_or_create_user, get_user_by_telegram_id, decrement_credits, add_credits, log_analysis, add_payment
)

app = FastAPI()

ML_URL = os.getenv("ML_URL", "http://ml:8001/api/v1/analyze")
PAY_URL = os.getenv("PAY_URL", "http://pay:8002/invoice")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

@app.get("/")
def root():
    return {"msg": "api.c0r.ai is alive"}

# Запуск aiogram-бота в фоне при старте FastAPI
@app.on_event("startup")
def launch_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())

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
    user_id = data.get("user_id")
    image_url = data.get("image_url")
    model_used = data.get("model_used", "openai")
    if not user_id or not image_url:
        raise HTTPException(status_code=400, detail="user_id and image_url required")
    user = await get_user_by_telegram_id(user_id)
    if not user or user["credits_remaining"] < 1:
        raise HTTPException(status_code=402, detail="Not enough credits")
    await decrement_credits(user_id)
    # Прокси-запрос к ml.c0r.ai
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            ML_URL,
            headers={"X-Internal-Token": INTERNAL_API_TOKEN},
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
            PAY_URL,
            headers={"X-Internal-Token": INTERNAL_API_TOKEN},
            json={"user_id": user_id, "amount": amount, "description": description}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.post("/credits/add")
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