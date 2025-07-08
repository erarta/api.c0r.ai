from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import httpx
from loguru import logger
from common.routes import Routes

app = FastAPI()

# Get environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

@app.get(Routes.ML_HEALTH)
async def health():
    return {"status": "ok", "service": "ml.c0r.ai"}

@app.post(Routes.ML_ANALYZE)
async def analyze_file(
    photo: UploadFile = File(...),
    telegram_user_id: str = Form(...),
    provider: str = Form(...),
):
    # For now, return mock data since we need to implement file handling
    mock_kbzhu = {
        "calories": 250,
        "proteins": 15.5,
        "fats": 8.2,
        "carbohydrates": 32.1
    }
    return {"kbzhu": mock_kbzhu} 