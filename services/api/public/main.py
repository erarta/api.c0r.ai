import os
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger


ENV = os.getenv("ENV", "development").lower()
ENABLE_SWAGGER = (os.getenv("ENABLE_SWAGGER") or ("true" if ENV != "production" else "false")).lower() == "true"

docs_url = "/docs" if ENABLE_SWAGGER else None
openapi_url = "/openapi.json" if ENABLE_SWAGGER else None

app = FastAPI(docs_url=docs_url, openapi_url=openapi_url, redoc_url=None)


_default_origins = "*" if ENV != "production" else ""
_origins = os.getenv("CORS_ORIGINS", _default_origins)
origins = [o.strip() for o in _origins.split(",") if o.strip()]
if ENV == "production" and ("*" in origins or not origins):
    origins = []
    logger.warning("CORS is disabled by default in production. Set CORS_ORIGINS to an allowlist if needed.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
async def health_root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Routers
from routers.food_plan import router as food_plan_router  # noqa: E402

app.include_router(food_plan_router)


