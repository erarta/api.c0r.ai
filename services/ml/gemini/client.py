import os
import httpx

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def analyze_image_gemini(image_url: str) -> dict:
    # Заглушка: здесь будет реальный вызов Gemini API
    # headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    # payload = {"image": image_url, ...}
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post("https://gemini.googleapis.com/v1/vision/analyze", headers=headers, json=payload)
    #     return resp.json()
    return {"provider": "gemini", "result": "stub: analysis done"} 