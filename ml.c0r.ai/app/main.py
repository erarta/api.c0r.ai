from fastapi import FastAPI, Request, HTTPException, Query
import os
from openai_client import analyze_image_openai
from gemini_client import analyze_image_gemini

INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "ml.c0r.ai is alive"}

@app.post("/api/v1/analyze")
async def analyze(request: Request, provider: str = Query("openai", enum=["openai", "gemini"])):
    token = request.headers.get("X-Internal-Token")
    if token != INTERNAL_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await request.json()
    image_url = data.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="image_url required")
    if provider == "gemini":
        result = await analyze_image_gemini(image_url)
    else:
        result = await analyze_image_openai(image_url)
    return result 