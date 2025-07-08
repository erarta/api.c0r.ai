import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def analyze_image_openai(image_url: str) -> dict:
    # Заглушка: здесь будет реальный вызов OpenAI Vision API
    # Пример запроса:
    # headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    # payload = {"image": image_url, ...}
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post("https://api.openai.com/v1/vision/analyze", headers=headers, json=payload)
    #     return resp.json()
    return {"provider": "openai", "result": "stub: analysis done"} 