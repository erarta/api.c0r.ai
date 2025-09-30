"""
Minimal async Redis client facade used by food plan router for caching.

For local/dev environments without Redis, functions degrade gracefully.
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict

from loguru import logger

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class _DummyAsyncRedis:
    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        logger.debug(f"[DummyRedis] setex {key} ttl={ttl_seconds} len={len(value)}")

    async def get(self, key: str) -> None:
        logger.debug(f"[DummyRedis] get {key} -> None")
        return None


_client = None


async def get_async_redis():
    """Return an async Redis-like client. Uses dummy in dev if REDIS_URL is not configured."""
    global _client
    if _client is not None:
        return _client
    url = os.getenv("REDIS_URL")
    if url and redis is not None:
        try:
            _client = redis.from_url(url, encoding="utf-8", decode_responses=True)
            logger.info("Connected to Redis")
            return _client
        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed to connect to Redis at {url}: {e}")
    _client = _DummyAsyncRedis()
    logger.warning("Using Dummy Redis client")
    return _client


def make_cache_key(namespace: str, params: Dict[str, Any]) -> str:
    try:
        suffix = json.dumps(params, sort_keys=True, ensure_ascii=False)
    except Exception:
        suffix = str(params)
    return f"c0r:{namespace}:{suffix}"


async def cache_get_json(key: str):
    """Get JSON value by key from Redis, returns parsed object or None."""
    try:
        client = await get_async_redis()
        raw = await client.get(key)  # type: ignore[attr-defined]
        if not raw:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.debug(f"cache_get_json error for {key}: {e}")
        return None


async def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    """Set JSON value with TTL."""
    try:
        client = await get_async_redis()
        await client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))  # type: ignore[attr-defined]
    except Exception as e:
        logger.debug(f"cache_set_json error for {key}: {e}")


